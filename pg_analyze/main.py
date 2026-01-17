#!/usr/bin/env python3

# Standard Library
import argparse
import json
import os

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
	args = parse_args()

	roots = _default_roots(args.roots)
	pg_files = scan_pg_files(roots)

	os.makedirs(args.out_dir, exist_ok=True)
	aggregator = pg_analyze.aggregate.Aggregator(needs_review_limit=200)

	per_file_handle = None
	if args.per_file_tsv:
		out_dir = os.path.dirname(args.per_file_tsv)
		if out_dir:
			os.makedirs(out_dir, exist_ok=True)
		per_file_handle = open(args.per_file_tsv, "w", encoding="utf-8")
		per_file_handle.write("\t".join(_per_file_header()) + "\n")

	jsonl_handle = None
	if args.jsonl_out:
		out_dir = os.path.dirname(args.jsonl_out)
		if out_dir:
			os.makedirs(out_dir, exist_ok=True)
		jsonl_handle = open(args.jsonl_out, "w", encoding="utf-8")

	try:
		for file_path in pg_files:
			record = analyze_file(file_path)
			aggregator.add_record(record)

			if per_file_handle is not None:
				per_file_handle.write("\t".join(_per_file_row(record)) + "\n")

			if jsonl_handle is not None:
				jsonl_handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")
	finally:
		if per_file_handle is not None:
			per_file_handle.close()
		if jsonl_handle is not None:
			jsonl_handle.close()

	write_reports(args.out_dir, aggregator)


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
	parser.add_argument(
		"--per-file-tsv",
		dest="per_file_tsv",
		default="",
		help="Optional path to write the full per-file TSV (off by default).",
	)
	parser.add_argument(
		"--jsonl-out",
		dest="jsonl_out",
		default="",
		help="Optional path to write JSONL per-file records (off by default).",
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
	stripped = pg_analyze.tokenize.strip_comments(text)
	newlines = pg_analyze.tokenize.build_newline_index(stripped)

	macros = pg_analyze.extract_evaluators.extract_macros(stripped, newlines=newlines)
	widgets, _pgml_info = pg_analyze.extract_widgets.extract(stripped, newlines=newlines)
	answers = pg_analyze.extract_answers.extract(stripped, newlines=newlines)
	evaluators = pg_analyze.extract_evaluators.extract(stripped, newlines=newlines)
	wiring = pg_analyze.wire_inputs.wire(widgets=widgets, evaluators=evaluators)

	report = {
		"file": file_path,
		"macros": macros,
		"widgets": widgets,
		"evaluators": evaluators,
		"answers": answers,
		"wiring": wiring,
		"pgml": _pgml_info,
	}

	labels, _ = pg_analyze.classify.classify(report)

	widget_kinds = sorted({w.get("kind") for w in widgets if isinstance(w.get("kind"), str)})
	evaluator_kinds = sorted({e.get("kind") for e in evaluators if isinstance(e.get("kind"), str)})
	input_count = sum(1 for w in widgets if w.get("kind") in {"blank", "popup", "radio", "checkbox", "matching", "ordering"})
	ans_count = len(evaluators)
	wiring_empty = len(wiring) == 0
	confidence = float(labels.get("confidence", 0.0))
	types = labels.get("types", [])
	reasons = labels.get("reasons", [])

	needs_review = (confidence < 0.55) or ((ans_count >= 2) and wiring_empty)

	return {
		"file": file_path,
		"types": types,
		"confidence": confidence,
		"needs_review": needs_review,
		"input_count": input_count,
		"ans_count": ans_count,
		"widget_kinds": widget_kinds,
		"evaluator_kinds": evaluator_kinds,
		"loadMacros": macros.get("loadMacros", []),
		"reasons": reasons,
		"wiring_empty": wiring_empty,
	}


#============================================


def _read_text_latin1(path: str) -> str:
	with open(path, "r", encoding="latin-1") as f:
		return f.read()


#============================================


def _per_file_header() -> list[str]:
	return [
		"file",
		"needs_review",
		"confidence",
		"types",
		"input_count",
		"ans_count",
		"widget_kinds",
		"evaluator_kinds",
		"loadMacros",
	]


#============================================


def _per_file_row(record: dict) -> list[str]:
	return [
		str(record.get("file", "")),
		str(bool(record.get("needs_review", False))).lower(),
		f"{float(record.get('confidence', 0.0)):.2f}",
		",".join(record.get("types", [])),
		str(int(record.get("input_count", 0))),
		str(int(record.get("ans_count", 0))),
		",".join(record.get("widget_kinds", [])),
		",".join(record.get("evaluator_kinds", [])),
		",".join(record.get("loadMacros", [])),
	]


#============================================


def write_reports(out_dir: str, aggregator: pg_analyze.aggregate.Aggregator) -> None:
	reports = aggregator.render_reports()
	for filename, content in reports.items():
		path = os.path.join(out_dir, filename)
		with open(path, "w", encoding="utf-8") as f:
			f.write(content)


#============================================


if __name__ == "__main__":
	main()
