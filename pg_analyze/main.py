#!/usr/bin/env python3

# Standard Library
import argparse
import os
import re
import sys
import time

# Local modules
import pg_analyze.aggregate
import pg_analyze.classify
import pg_analyze.extract_answers
import pg_analyze.extract_evaluators
import pg_analyze.extract_widgets
import pg_analyze.tokenize
import pg_analyze.wire_inputs


#============================================

def main() -> None:
	start = time.perf_counter()
	args = parse_args()

	roots = _default_roots(args.roots)
	_log(f"pg_analyze: scanning roots: {', '.join(roots)}")
	scan_start = time.perf_counter()
	pg_files = scan_pg_files(roots)
	_log(f"pg_analyze: found {len(pg_files)} .pg files in {time.perf_counter() - scan_start:.2f}s")

	os.makedirs(args.out_dir, exist_ok=True)
	out_dir_abs = os.path.abspath(args.out_dir)
	aggregator = pg_analyze.aggregate.Aggregator(needs_review_limit=200, out_dir=args.out_dir)

	try:
		_log("pg_analyze: analyzing files...")
		last_progress = time.perf_counter()
		for i, file_path in enumerate(pg_files, start=1):
			text = _read_text_latin1(file_path)
			record = analyze_text(text=text, file_path=file_path)
			aggregator.add_record(record)
			aggregator.add_pgml_blocks(record=record, text=text)
			last_progress = _maybe_log_progress(last_progress, done=i, total=len(pg_files))
		_log("pg_analyze: writing outputs...")
		write_reports(args.out_dir, aggregator)
	finally:
		aggregator.close()

	elapsed = time.perf_counter() - start
	_log(f"pg_analyze: done in {elapsed:.2f}s; output is located at {out_dir_abs}")


#============================================


def _log(msg: str) -> None:
	print(msg, file=sys.stderr, flush=True)


def _maybe_log_progress(last_progress: float, *, done: int, total: int) -> float:
	now = time.perf_counter()
	if now - last_progress < 2.0:
		return last_progress
	_log(f"pg_analyze: processed {done}/{total} files...")
	return now


#============================================


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(prog="pg_analyze")

	parser.add_argument(
		"-r",
		"--roots",
		dest="roots",
		nargs="*",
		default=[],
		help="Roots to scan for .pg files (default: OpenProblemLibrary Contrib Pending, if present).",
	)
	parser.add_argument(
		"-o",
		"--out-dir",
		dest="out_dir",
		required=True,
		help="Directory to write aggregate TSV reports.",
	)

	return parser.parse_args()


#============================================


def _default_roots(roots: list[str]) -> list[str]:
	if roots:
		return roots
	candidates = ["OpenProblemLibrary", "Contrib", "Pending"]
	existing = [c for c in candidates if os.path.exists(c)]
	return existing if existing else ["."]


#============================================

def scan_pg_files(roots: list[str]) -> list[str]:
	"""
	Return a sorted list of .pg file paths under the given roots.

	Returned paths are workspace-relative (using os.sep).
	"""
	found: list[str] = []
	for root in roots:
		if not os.path.exists(root):
			continue
		if os.path.isfile(root):
			if root.endswith(".pg"):
				found.append(root)
			continue
		for dirpath, dirnames, filenames in os.walk(root):
			dirnames[:] = [d for d in dirnames if d != ".git"]
			for filename in filenames:
				if not filename.endswith(".pg"):
					continue
				found.append(os.path.join(dirpath, filename))
	return sorted(set(found))


#============================================


def analyze_file(file_path: str) -> dict:
	text = _read_text_latin1(file_path)
	return analyze_text(text=text, file_path=file_path)

def analyze_text(*, text: str, file_path: str) -> dict:
	comment_stripped = pg_analyze.tokenize.strip_comments(text)
	clean = pg_analyze.tokenize.strip_heredocs(comment_stripped)
	newlines = pg_analyze.tokenize.build_newline_index(clean)
	raw_newlines = pg_analyze.tokenize.build_newline_index(text)

	macros = pg_analyze.extract_evaluators.extract_macros(clean, newlines=newlines)
	widgets, _pgml_info = pg_analyze.extract_widgets.extract(clean, newlines=newlines)
	answers = pg_analyze.extract_answers.extract(clean, newlines=newlines)
	ans_evaluators = pg_analyze.extract_evaluators.extract(clean, newlines=newlines)
	pgml_payload_evaluators = pg_analyze.extract_evaluators.extract_pgml_payload_evaluators(text, newlines=raw_newlines)
	evaluators = ans_evaluators + pgml_payload_evaluators
	wiring = pg_analyze.wire_inputs.wire(widgets=widgets, evaluators=evaluators)
	has_multianswer = bool(_MULTIANSWER_RX.search(clean))
	named_rule_refs = _extract_named_rule_refs(evaluators)

	report = {
		"file": file_path,
		"macros": macros,
		"widgets": widgets,
		"evaluators": evaluators,
		"answers": answers,
		"wiring": wiring,
		"pgml": _pgml_info,
		"has_multianswer": has_multianswer,
	}

	labels, _ = pg_analyze.classify.classify(report)

	widget_kinds = [w.get("kind") for w in widgets if isinstance(w.get("kind"), str)]
	evaluator_kinds = [e.get("kind") for e in evaluators if isinstance(e.get("kind"), str)]
	evaluator_sources = [e.get("source") for e in evaluators if isinstance(e.get("source"), str)]
	input_count = sum(1 for w in widgets if w.get("kind") in {"blank", "popup", "radio", "checkbox", "matching", "ordering"})
	ans_count = len(ans_evaluators)
	wiring_empty = len(wiring) == 0
	confidence = float(labels.get("confidence", 0.0))
	types = labels.get("types", [])
	reasons = labels.get("reasons", [])

	ans_token_count = len(_ANS_TOKEN_RX.findall(clean))
	has_ans_token = 1 if ans_token_count > 0 else 0
	has_cmp_token = 1 if bool(_CMP_TOKEN_RX.search(clean)) else 0
	has_num_cmp_token = 1 if bool(_NUM_CMP_TOKEN_RX.search(clean)) else 0
	has_str_cmp_token = 1 if bool(_STR_CMP_TOKEN_RX.search(clean)) else 0
	has_named_ans_rule_token = 1 if bool(_NAMED_ANS_RULE_TOKEN_RX.search(clean)) else 0
	has_named_ans_token = 1 if bool(_NAMED_ANS_TOKEN_RX.search(clean)) else 0
	has_ans_num_to_name = 1 if bool(_ANS_NUM_TO_NAME_RX.search(clean)) else 0
	has_install_problem_grader = 1 if bool(_INSTALL_PROBLEM_GRADER_RX.search(clean)) else 0

	pgml_blank_count = int(_pgml_info.get("blank_count", 0) or 0)
	pgml_block_count = int(_pgml_info.get("block_count", 0) or 0)
	if pgml_blank_count > 0:
		widget_kinds.extend(["pgml_blank"] * pgml_blank_count)
		input_count += pgml_blank_count

	has_answer_ctor = 1 if (len(answers) > 0 or bool(_CTOR_TOKEN_RX.search(clean))) else 0

	ans_call_evaluator_count = len(ans_evaluators)
	pgml_payload_evaluator_count = len(pgml_payload_evaluators)
	ans_call_evaluator_kinds = [e.get("kind") for e in ans_evaluators if isinstance(e.get("kind"), str)]
	pgml_payload_evaluator_kinds = [e.get("kind") for e in pgml_payload_evaluators if isinstance(e.get("kind"), str)]

	record = {
		"file": file_path,
		"types": types,
		"confidence": confidence,
		"input_count": input_count,
		"ans_count": ans_count,
		"widget_kinds": widget_kinds,
		"evaluator_kinds": evaluator_kinds,
		"evaluator_sources": evaluator_sources,
		"ans_call_evaluator_count": ans_call_evaluator_count,
		"pgml_payload_evaluator_count": pgml_payload_evaluator_count,
		"ans_call_evaluator_kinds": ans_call_evaluator_kinds,
		"pgml_payload_evaluator_kinds": pgml_payload_evaluator_kinds,
		"loadMacros": macros.get("loadMacros", []),
		"reasons": reasons,
		"wiring_empty": wiring_empty,
		"has_multianswer": has_multianswer,
		"named_rule_refs": named_rule_refs,
		"pgml_block_count": pgml_block_count,
		"pgml_blank_marker_count": pgml_blank_count,
		"ans_token_count": ans_token_count,
		"has_ans_token": has_ans_token,
		"has_cmp_token": has_cmp_token,
		"has_num_cmp_token": has_num_cmp_token,
		"has_str_cmp_token": has_str_cmp_token,
		"has_answer_ctor": has_answer_ctor,
		"has_named_ans_rule_token": has_named_ans_rule_token,
		"has_named_ans_token": has_named_ans_token,
		"has_ans_num_to_name": has_ans_num_to_name,
		"has_install_problem_grader": has_install_problem_grader,
	}

	bucket = pg_analyze.aggregate.needs_review_bucket(record)
	needs_review = (confidence < 0.55) or ((ans_count >= 2) and wiring_empty) or bool(bucket)
	if needs_review and (not bucket):
		bucket = "low_confidence_misc"
	record["needs_review"] = needs_review
	record["needs_review_bucket"] = bucket
	return record


#============================================


def _read_text_latin1(path: str) -> str:
	with open(path, "r", encoding="latin-1") as f:
		return f.read()

#============================================


def write_reports(out_dir: str, aggregator: pg_analyze.aggregate.Aggregator) -> None:
	reports = aggregator.render_reports()
	for filename, content in reports.items():
		rel_path = pg_analyze.aggregate.REPORT_PATHS.get(filename, os.path.join("summary", filename))
		path = os.path.join(out_dir, rel_path)
		parent = os.path.dirname(path)
		if parent:
			os.makedirs(parent, exist_ok=True)
		with open(path, "w", encoding="utf-8") as f:
			f.write(content)

	_write_index(out_dir)


def _write_index(out_dir: str) -> None:
	lines = [
		"pg_analyze output index",
		"",
		"Start here:",
		"- summary/coverage.tsv",
		"- summary/counts_by_type.tsv",
		"- needs_review/needs_review_bucket_counts.tsv",
		"",
		"Then:",
		"- summary/evaluator_source_counts.tsv",
		"- counts/pgml_payload_evaluator_counts.tsv",
		"",
		"Then:",
		"- cross_tabs/widget_by_evaluator.tsv",
		"- cross_tabs/type_by_evaluator_source.tsv",
		"",
		"For tuning:",
		"- macros/macro_counts_unknown_pgml_blank.tsv",
		"- needs_review/evaluator_coverage_reasons.tsv",
		"",
		"For examples:",
		"- diagnostics/pgml_blocks_sample.txt",
		"- samples/*.tsv",
		"",
	]

	path = os.path.join(out_dir, "INDEX.txt")
	with open(path, "w", encoding="utf-8") as f:
		f.write("\n".join(lines))


#============================================


_MULTIANSWER_RX = re.compile(r"\bMultiAnswer\s*\(")

_NAMED_RULE_REF_RX = re.compile(r"\bnamed_ans_rule\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")

_ANS_TOKEN_RX = re.compile(r"\bANS\s*\(")
_CMP_TOKEN_RX = re.compile(r"->\s*cmp\s*\(")
_NUM_CMP_TOKEN_RX = re.compile(r"\bnum_cmp\s*\(")
_STR_CMP_TOKEN_RX = re.compile(r"\b(str_cmp|string_cmp)\s*\(")
_NAMED_ANS_RULE_TOKEN_RX = re.compile(r"\b(NAMED_ANS_RULE|named_ans_rule)\s*\(")
_NAMED_ANS_TOKEN_RX = re.compile(r"\bNAMED_ANS\s*\(")
_ANS_NUM_TO_NAME_RX = re.compile(r"\bANS_NUM_TO_NAME\s*\(")
_INSTALL_PROBLEM_GRADER_RX = re.compile(r"\binstall_problem_grader\b")
_CTOR_TOKEN_RX = re.compile(r"\b(Real|Formula|Compute|String|List|Vector|Point)\s*\(")


def _extract_named_rule_refs(evaluators: list[dict]) -> list[str]:
	names: list[str] = []
	for ev in evaluators:
		expr = ev.get("expr", "")
		if not isinstance(expr, str):
			continue
		for m in _NAMED_RULE_REF_RX.finditer(expr):
			name = m.group(1)
			if name not in names:
				names.append(name)
	return names


#============================================


if __name__ == "__main__":
	main()
