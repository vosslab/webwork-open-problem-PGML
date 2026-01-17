# Standard Library
import re

# Local modules
import pg_analyze.tokenize


EVALUATOR_CALL_NAMES = {
	"ANS",
}

MACRO_CALL_NAMES = {
	"loadMacros",
	"includePGproblem",
}

VAR_RX = re.compile(r"\$([A-Za-z_]\w*)")
FILENAME_RX = re.compile(r"""['"]([^'"]+\.(?:pl|pg))['"]""")


#============================================


def extract_macros(stripped_text: str, *, newlines: list[int]) -> dict:
	"""
	Extract macro usage from stripped (comment-free) text.
	"""
	calls = pg_analyze.tokenize.iter_calls(stripped_text, MACRO_CALL_NAMES, newlines=newlines)

	load_macros: list[str] = []
	include_pgproblem: list[str] = []

	for call in calls:
		matches = [m.group(1) for m in FILENAME_RX.finditer(call.arg_text)]
		if call.name == "loadMacros":
			for filename in matches:
				if filename not in load_macros:
					load_macros.append(filename)
		elif call.name == "includePGproblem":
			for filename in matches:
				if filename not in include_pgproblem:
					include_pgproblem.append(filename)

	return {
		"loadMacros": load_macros,
		"includePGproblem": include_pgproblem,
	}


#============================================


def extract(stripped_text: str, *, newlines: list[int]) -> list[dict]:
	evaluators: list[dict] = []
	calls = pg_analyze.tokenize.iter_calls(stripped_text, EVALUATOR_CALL_NAMES, newlines=newlines)
	for call in calls:
		expr = _normalize_ws(call.arg_text)
		evaluators.append(
			{
				"kind": _classify(expr),
				"expr": expr,
				"vars": _extract_vars(expr),
				"line": call.line,
				"source": "ans_call",
			}
		)
	return evaluators


#============================================

PGML_BLANK_RX = re.compile(r"\[[ \t]*_+[ \t]*\]")
PGML_BLANK_WITH_PAYLOAD_RX = re.compile(r"\[[ \t]*_+[ \t]*\][ \t]*\{")


def extract_pgml_payload_evaluators(text: str, *, newlines: list[int]) -> list[dict]:
	"""
	Extract evaluator-like payloads embedded in PGML blanks.

	These often look like:
	  [_]{Real(3)->cmp()}
	  [____]{str_cmp("foo")}
	  [__]{ans_rule(20)}

	This intentionally avoids full Perl parsing: it scans known PGML regions and
	uses a balanced brace walker to capture {...} payloads.
	"""
	evaluators: list[dict] = []

	for start, end in _pgml_regions(text):
		block = text[start:end]
		for payload, payload_abs_pos in _iter_pgml_blank_payloads(block, start_offset=start):
			expr = _normalize_ws(payload)
			evaluators.append(
				{
					"kind": _classify(expr),
					"expr": expr,
					"vars": _extract_vars(expr),
					"line": pg_analyze.tokenize.pos_to_line(newlines, payload_abs_pos),
					"source": "pgml_payload",
				}
			)

	return evaluators


def _pgml_regions(text: str) -> list[tuple[int, int]]:
	regions: list[tuple[int, int]] = []
	regions.extend(_extract_begin_end_pgml_regions(text))
	regions.extend(_extract_pgml_heredoc_regions(text))
	return regions


def _extract_begin_end_pgml_regions(text: str) -> list[tuple[int, int]]:
	regions: list[tuple[int, int]] = []
	stack: list[tuple[str, int]] = []

	for m in re.finditer(r"(?m)^[ \t]*(BEGIN|END)_PGML(?:_(SOLUTION|HINT))?\b", text):
		kind = m.group(1)
		suffix = m.group(2) or ""
		tag = f"PGML_{suffix}" if suffix else "PGML"

		if kind == "BEGIN":
			stack.append((tag, m.end()))
			continue

		if kind == "END":
			if not stack:
				continue
			open_tag, open_pos = stack.pop()
			if open_pos < m.start():
				regions.append((open_pos, m.start()))

	return regions


def _extract_pgml_heredoc_regions(text: str) -> list[tuple[int, int]]:
	regions: list[tuple[int, int]] = []
	heredoc_end: str | None = None
	body_start: int | None = None

	pos = 0
	for line in text.splitlines(keepends=True):
		if heredoc_end is None:
			terminator = _scan_heredoc_terminator(line)
			if (terminator is not None) and ("PGML" in terminator):
				heredoc_end = terminator
				body_start = pos + len(line)
			pos += len(line)
			continue

		# in heredoc body
		if line.strip() == heredoc_end:
			if body_start is not None and body_start < pos:
				regions.append((body_start, pos))
			heredoc_end = None
			body_start = None
		pos += len(line)

	return regions


def _scan_heredoc_terminator(line: str) -> str | None:
	"""
	Detect a heredoc introducer outside of strings and return its terminator token.
	"""
	in_sq = False
	in_dq = False
	escape = False

	i = 0
	while i < len(line) - 1:
		ch = line[i]
		if escape:
			escape = False
			i += 1
			continue
		if ch == "\\":
			escape = True
			i += 1
			continue
		if (not in_dq) and (ch == "'") and (not in_sq):
			in_sq = True
			i += 1
			continue
		if in_sq and ch == "'":
			in_sq = False
			i += 1
			continue
		if (not in_sq) and (ch == '"') and (not in_dq):
			in_dq = True
			i += 1
			continue
		if in_dq and ch == '"':
			in_dq = False
			i += 1
			continue

		if (not in_sq) and (not in_dq) and (ch == "<") and (line[i + 1] == "<"):
			j = i + 2
			if j < len(line) and line[j] == "-":
				j += 1
			while j < len(line) and line[j].isspace():
				j += 1
			if j >= len(line):
				return None

			if line[j] in ("'", '"'):
				quote = line[j]
				j += 1
				start = j
				while j < len(line) and line[j] != quote:
					j += 1
				if j >= len(line):
					return None
				return line[start:j]

			start = j
			if not (line[j].isalpha() or line[j] == "_"):
				return None
			j += 1
			while j < len(line) and (line[j].isalnum() or line[j] == "_"):
				j += 1
			return line[start:j]

		i += 1

	return None


def _iter_pgml_blank_payloads(block_text: str, *, start_offset: int) -> list[tuple[str, int]]:
	out: list[tuple[str, int]] = []
	i = 0
	while True:
		m = PGML_BLANK_WITH_PAYLOAD_RX.search(block_text, i)
		if not m:
			break
		brace_open = block_text.find("{", m.end() - 1)
		if brace_open == -1:
			i = m.end()
			continue
		brace_close = _find_matching_brace(block_text, brace_open)
		if brace_close == brace_open:
			i = m.end()
			continue
		payload = block_text[brace_open + 1 : brace_close]
		out.append((payload, start_offset + brace_open + 1))
		i = brace_close + 1
	return out


def _find_matching_brace(text: str, open_brace_index: int) -> int:
	in_sq = False
	in_dq = False
	escape = False
	depth = 0
	i = open_brace_index
	while i < len(text):
		ch = text[i]
		if escape:
			escape = False
			i += 1
			continue
		if ch == "\\":
			escape = True
			i += 1
			continue
		if (not in_dq) and (ch == "'") and (not in_sq):
			in_sq = True
			i += 1
			continue
		if in_sq and ch == "'":
			in_sq = False
			i += 1
			continue
		if (not in_sq) and (ch == '"') and (not in_dq):
			in_dq = True
			i += 1
			continue
		if in_dq and ch == '"':
			in_dq = False
			i += 1
			continue

		if (not in_sq) and (not in_dq):
			if ch == "{":
				depth += 1
			elif ch == "}":
				depth -= 1
				if depth == 0:
					return i
		i += 1

	return open_brace_index


#============================================

def extract_pgml_blocks(text: str, *, newlines: list[int]) -> list[dict]:
	"""
	Extract raw PGML blocks for diagnostics.

	Returns a list of dicts with:
	- kind: BEGIN_PGML, BEGIN_PGML_HINT, BEGIN_PGML_SOLUTION, HEREDOC_PGML
	- start_line: 1-based line
	- blank_marker_count: number of [_] / [____] markers in the block
	- has_payload: whether any blank appears with a {...} payload
	- text: the raw block text
	"""
	out: list[dict] = []
	out.extend(_extract_begin_end_pgml_blocks(text, newlines=newlines))
	out.extend(_extract_pgml_heredoc_blocks(text, newlines=newlines))
	return out


def _extract_begin_end_pgml_blocks(text: str, *, newlines: list[int]) -> list[dict]:
	blocks: list[dict] = []
	stack: list[tuple[str, int, int]] = []

	for m in re.finditer(r"(?m)^[ \t]*(BEGIN|END)_PGML(?:_(SOLUTION|HINT))?\b", text):
		kind = m.group(1)
		suffix = m.group(2) or ""
		tag = f"PGML_{suffix}" if suffix else "PGML"

		if kind == "BEGIN":
			line_start = text.rfind("\n", 0, m.start()) + 1
			start = line_start if line_start >= 0 else m.start()
			stack.append((tag, start, m.start()))
			continue

		if kind == "END":
			if not stack:
				continue
			open_tag, start, _ = stack.pop()
			if open_tag != tag:
				continue
			end = _line_end_pos(text, m.end())
			block_text = text[start:end]
			blocks.append(_pgml_block_info(block_text, start=start, kind=_kind_label(tag), newlines=newlines))

	return blocks


def _extract_pgml_heredoc_blocks(text: str, *, newlines: list[int]) -> list[dict]:
	blocks: list[dict] = []
	heredoc_end: str | None = None
	body_start: int | None = None
	start_line: int | None = None

	pos = 0
	for line in text.splitlines(keepends=True):
		if heredoc_end is None:
			terminator = _scan_heredoc_terminator(line)
			if (terminator is not None) and ("PGML" in terminator):
				heredoc_end = terminator
				body_start = pos + len(line)
				start_line = pg_analyze.tokenize.pos_to_line(newlines, body_start)
			pos += len(line)
			continue

		if line.strip() == heredoc_end:
			if body_start is not None and body_start < pos:
				block_text = text[body_start:pos]
				blocks.append(_pgml_block_info(block_text, start=body_start, kind="HEREDOC_PGML", newlines=newlines, start_line=start_line))
			heredoc_end = None
			body_start = None
			start_line = None
		pos += len(line)

	return blocks


def _pgml_block_info(block_text: str, *, start: int, kind: str, newlines: list[int], start_line: int | None = None) -> dict:
	blank_marker_count = len(PGML_BLANK_RX.findall(block_text))
	has_payload = 1 if bool(PGML_BLANK_WITH_PAYLOAD_RX.search(block_text)) else 0
	if start_line is None:
		start_line = pg_analyze.tokenize.pos_to_line(newlines, start)
	return {
		"kind": kind,
		"start_line": start_line,
		"blank_marker_count": blank_marker_count,
		"has_payload": has_payload,
		"text": block_text,
	}


def _kind_label(tag: str) -> str:
	if tag == "PGML":
		return "BEGIN_PGML"
	if tag == "PGML_HINT":
		return "BEGIN_PGML_HINT"
	if tag == "PGML_SOLUTION":
		return "BEGIN_PGML_SOLUTION"
	return "BEGIN_PGML"


def _line_end_pos(text: str, pos: int) -> int:
	nl = text.find("\n", pos)
	return len(text) if nl == -1 else (nl + 1)


#============================================


def _normalize_ws(text: str) -> str:
	return " ".join(text.split())


#============================================


def _extract_vars(expr: str) -> list[str]:
	vars_found: list[str] = []
	for m in VAR_RX.finditer(expr):
		v = m.group(1)
		if v not in vars_found:
			vars_found.append(v)
	return vars_found


#============================================


def _classify(expr: str) -> str:
	if "->cmp(" in expr or expr.endswith("->cmp()") or "->cmp()" in expr:
		return "cmp"
	if re.search(r"\bnamed_ans_rule\s*\(", expr):
		return "named_rule"
	if re.search(r"\bradio_cmp\s*\(", expr):
		return "radio_cmp"
	if re.search(r"\bcheckbox_cmp\s*\(", expr):
		return "checkbox_cmp"
	if re.search(r"\bpopup_cmp\s*\(", expr):
		return "popup_cmp"
	if re.search(r"\bnum_cmp\s*\(", expr):
		return "num_cmp"
	if re.search(r"\bfun_cmp\s*\(", expr):
		return "fun_cmp"
	if re.search(r"\bformula_cmp\s*\(", expr):
		return "formula_cmp"
	if re.search(r"\b(str_cmp|string_cmp)\s*\(", expr):
		return "str_cmp"
	if re.search(r"\bchecker\s*=>\s*sub\s*\{", expr):
		return "custom"
	return "other"
