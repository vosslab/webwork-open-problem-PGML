# Standard Library
from pathlib import Path

# Local modules
import pg_analyze.aggregate


def test_bucket_lists_write_paths_once_per_bucket(tmp_path: Path) -> None:
	writers = pg_analyze.aggregate.BucketWriters(str(tmp_path))
	try:
		writers.write_record({
			"file": "a.pg",
			"types": ["numeric_entry"],
			"subtype_tags": ["matrix_entry"],
			"widget_kinds": ["blank", "blank"],
			"evaluator_kinds": ["cmp"],
		})
		writers.write_record({
			"file": "b.pg",
			"types": ["other", "multipart"],
			"widget_kinds": [],
			"evaluator_kinds": [],
		})
	finally:
		writers.close()

	assert (tmp_path / "lists" / "type" / "numeric_entry_files.txt").read_text(encoding="utf-8") == "a.pg\n"
	assert (tmp_path / "lists" / "type" / "other_files.txt").read_text(encoding="utf-8") == "b.pg\n"
	assert (tmp_path / "lists" / "type" / "multipart_files.txt").read_text(encoding="utf-8") == "b.pg\n"
	assert (tmp_path / "lists" / "subtype" / "matrix_entry_files.txt").read_text(encoding="utf-8") == "a.pg\n"

	assert (tmp_path / "lists" / "widget" / "blank_files.txt").read_text(encoding="utf-8") == "a.pg\n"
	assert (tmp_path / "lists" / "widget" / "none_files.txt").read_text(encoding="utf-8") == "b.pg\n"

	assert (tmp_path / "lists" / "evaluator" / "cmp_files.txt").read_text(encoding="utf-8") == "a.pg\n"
	assert (tmp_path / "lists" / "evaluator" / "none_files.txt").read_text(encoding="utf-8") == "b.pg\n"
