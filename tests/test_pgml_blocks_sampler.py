# Standard Library
from pathlib import Path

# Local modules
import pg_analyze.aggregate


def test_pgml_blocks_sample_written_and_capped(tmp_path: Path) -> None:
	agg = pg_analyze.aggregate.Aggregator(needs_review_limit=200, out_dir=str(tmp_path))
	try:
		text = (
			"BEGIN_PGML\n"
			"Answer: [_]{Real(3)->cmp()}\n"
			"END_PGML\n"
		)
		record = {
			"file": "a.pg",
			"types": ["unknown_pgml_blank"],
			"evaluator_kinds": [],
			"confidence": 0.25,
		}
		agg.add_pgml_blocks(record=record, text=text)
	finally:
		agg.close()

	out = (tmp_path / "pgml_blocks_sample.txt").read_text(encoding="utf-8")
	assert "=== file=a.pg kind=BEGIN_PGML" in out
	assert "Answer: [_]{Real(3)->cmp()}" in out
	assert "=== END ===" in out
