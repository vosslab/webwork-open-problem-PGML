# Standard Library
import heapq


#============================================


def confidence_bin(confidence: float) -> str:
	if confidence < 0.0:
		confidence = 0.0
	if confidence > 1.0:
		confidence = 1.0
	i = int(confidence * 10.0)
	if i >= 10:
		i = 9
	lo = i / 10.0
	hi = (i + 1) / 10.0
	return f"{lo:.1f}-{hi:.1f}"


#============================================


def count_bucket(count: int) -> str:
	if count <= 0:
		return "0"
	if count == 1:
		return "1"
	if count == 2:
		return "2"
	if count == 3:
		return "3"
	if count == 4:
		return "4"
	if count <= 9:
		return "5-9"
	if count <= 19:
		return "10-19"
	return "20+"


#============================================


def reasons_to_text(reasons: list[dict]) -> str:
	parts: list[str] = []
	for r in reasons:
		if not isinstance(r, dict):
			continue
		kind = r.get("kind")
		value = r.get("value")
		if not isinstance(kind, str) or not isinstance(value, str):
			continue
		parts.append(f"{kind}:{value}")
	return "; ".join(parts)


#============================================


def _inc(counter: dict[str, int], key: str, amount: int = 1) -> None:
	counter[key] = counter.get(key, 0) + amount


#============================================


def _render_counts_tsv(rows: list[tuple[str, int]], *, key_name: str) -> str:
	lines: list[str] = [f"{key_name}\tcount"]
	for key, count in sorted(rows, key=lambda x: (-x[1], x[0])):
		lines.append(f"{key}\t{count}")
	return "\n".join(lines) + "\n"


#============================================


class Aggregator:
	def __init__(self, *, needs_review_limit: int = 200):
		self.type_counts: dict[str, int] = {}
		self.confidence_bins: dict[str, int] = {}
		self.macro_counts: dict[str, int] = {}
		self.widget_counts: dict[str, int] = {}
		self.evaluator_counts: dict[str, int] = {}
		self.input_hist: dict[str, int] = {}
		self.ans_hist: dict[str, int] = {}

		self._needs_review_limit = needs_review_limit
		self._needs_review_heap: list[tuple[float, str, float, str, str]] = []

	def add_record(self, record: dict) -> None:
		types = record.get("types", [])
		confidence = record.get("confidence", 0.0)
		load_macros = record.get("loadMacros", [])
		widget_kinds = record.get("widget_kinds", [])
		evaluator_kinds = record.get("evaluator_kinds", [])
		input_count = record.get("input_count", 0)
		ans_count = record.get("ans_count", 0)
		needs_review = record.get("needs_review", False)

		if isinstance(types, list):
			for t in types:
				if isinstance(t, str):
					_inc(self.type_counts, t)

		if isinstance(confidence, float) or isinstance(confidence, int):
			_inc(self.confidence_bins, confidence_bin(float(confidence)))

		if isinstance(load_macros, list):
			for macro in load_macros:
				if isinstance(macro, str):
					_inc(self.macro_counts, macro)

		if isinstance(widget_kinds, list):
			for kind in widget_kinds:
				if isinstance(kind, str):
					_inc(self.widget_counts, kind)

		if isinstance(evaluator_kinds, list):
			for kind in evaluator_kinds:
				if isinstance(kind, str):
					_inc(self.evaluator_counts, kind)

		if isinstance(input_count, int):
			_inc(self.input_hist, count_bucket(input_count))

		if isinstance(ans_count, int):
			_inc(self.ans_hist, count_bucket(ans_count))

		if needs_review:
			self._add_needs_review(record)

	def _add_needs_review(self, record: dict) -> None:
		file_path = record.get("file", "")
		confidence = float(record.get("confidence", 0.0))
		types = record.get("types", [])
		reasons = record.get("reasons", [])

		if not isinstance(file_path, str):
			return

		types_text = ",".join(t for t in types if isinstance(t, str))
		reasons_text = reasons_to_text(reasons if isinstance(reasons, list) else [])

		heapq.heappush(self._needs_review_heap, (-confidence, file_path, confidence, types_text, reasons_text))
		if len(self._needs_review_heap) > self._needs_review_limit:
			heapq.heappop(self._needs_review_heap)

	def render_reports(self) -> dict[str, str]:
		out: dict[str, str] = {}
		out["counts_by_type.tsv"] = _render_counts_tsv(list(self.type_counts.items()), key_name="type")
		out["confidence_bins.tsv"] = _render_counts_tsv(list(self.confidence_bins.items()), key_name="bin")
		out["macro_counts.tsv"] = _render_counts_tsv(list(self.macro_counts.items()), key_name="macro")
		out["widget_counts.tsv"] = _render_counts_tsv(list(self.widget_counts.items()), key_name="widget_kind")
		out["evaluator_counts.tsv"] = _render_counts_tsv(list(self.evaluator_counts.items()), key_name="evaluator_kind")
		out["input_count_hist.tsv"] = _render_counts_tsv(list(self.input_hist.items()), key_name="bucket")
		out["ans_count_hist.tsv"] = _render_counts_tsv(list(self.ans_hist.items()), key_name="bucket")
		out["needs_review.tsv"] = self._render_needs_review_tsv()
		return out

	def _render_needs_review_tsv(self) -> str:
		items = [(-neg_conf, file_path, types_text, reasons_text) for neg_conf, file_path, _, types_text, reasons_text in self._needs_review_heap]
		items_sorted = sorted(items, key=lambda x: (x[0], x[1]))
		lines: list[str] = ["file\tconfidence\ttypes\treasons"]
		for conf, file_path, types_text, reasons_text in items_sorted:
			lines.append(f"{file_path}\t{conf:.2f}\t{types_text}\t{reasons_text}")
		return "\n".join(lines) + "\n"

