# Standard Library
# Local modules
import pg_analyze.aggregate
import pg_analyze.main


def _parse_counts_tsv(tsv_text: str) -> dict[str, int]:
	lines = [l for l in tsv_text.splitlines() if l.strip()]
	assert lines
	assert "\t" in lines[0]
	out: dict[str, int] = {}
	for line in lines[1:]:
		key, count_text = line.split("\t", 1)
		out[key] = int(count_text)
	return out


def test_aggregate_reports_from_synthetic_pg_like_strings() -> None:
	aggregator = pg_analyze.aggregate.Aggregator(needs_review_limit=200)

	numeric_text = (
		'loadMacros("PGstandard.pl", "MathObjects.pl");\n'
		"Context('Numeric');\n"
		"$a = Real(3);\n"
		"ans_rule(20);\n"
		"ANS($a->cmp());\n"
	)
	mc_text = (
		'loadMacros("PGstandard.pl", "parserRadioButtons.pl");\n'
		"$rb = RadioButtons([\"A\", \"B\"], \"A\");\n"
		"ANS($rb->cmp());\n"
	)
	multipart_text = (
		'loadMacros("PGstandard.pl", "MathObjects.pl");\n'
		"$a = Real(1);\n"
		"$b = Real(2);\n"
		"ans_rule(20);\n"
		"ans_rule(20);\n"
		"ANS($a->cmp());\n"
		"ANS($b->cmp());\n"
	)

	records = [
		pg_analyze.main.analyze_text(text=numeric_text, file_path="a.pg"),
		pg_analyze.main.analyze_text(text=mc_text, file_path="b.pg"),
		pg_analyze.main.analyze_text(text=multipart_text, file_path="c.pg"),
	]

	for r in records:
		aggregator.add_record(r)

	reports = aggregator.render_reports()

	type_counts = _parse_counts_tsv(reports["counts_by_type.tsv"])
	assert type_counts["numeric_entry"] == 2
	assert type_counts["multiple_choice"] == 1
	assert type_counts["multipart"] == 1

	conf_bins = _parse_counts_tsv(reports["confidence_bins.tsv"])
	assert conf_bins["0.5-0.6"] == 2
	assert conf_bins["0.7-0.8"] == 1

	macro_counts = _parse_counts_tsv(reports["macro_counts.tsv"])
	assert macro_counts["PGstandard.pl"] == 3
	assert macro_counts["MathObjects.pl"] == 2
	assert macro_counts["parserRadioButtons.pl"] == 1

	widget_counts = _parse_counts_tsv(reports["widget_counts.tsv"])
	assert widget_counts["blank"] == 3
	assert widget_counts["radio"] == 1

	eval_counts = _parse_counts_tsv(reports["evaluator_counts.tsv"])
	assert eval_counts["cmp"] == 4

	input_hist = _parse_counts_tsv(reports["input_count_hist.tsv"])
	assert input_hist["1"] == 2
	assert input_hist["2"] == 1

	ans_hist = _parse_counts_tsv(reports["ans_count_hist.tsv"])
	assert ans_hist["1"] == 2
	assert ans_hist["2"] == 1

	needs_review_lines = [l for l in reports["needs_review.tsv"].splitlines() if l.strip()]
	assert needs_review_lines[0] == "file\tconfidence\ttypes\treasons"
	assert len(needs_review_lines) == 2
	assert needs_review_lines[1].startswith("a.pg\t0.50\t")
