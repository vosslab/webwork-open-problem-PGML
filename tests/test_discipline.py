# Local modules
import pg_analyze.discipline


def test_extract_dbsubjects_requires_double_hash_prefix() -> None:
	text = (
		"# DBsubject('physics')\n"
		"## DBsubject('calculus')\n"
		"   ##DBsubject(\"Linear Algebra\")\n"
		"##  DBsubject(  '  '  )\n"
		"## DBsubject('Probability, Statistics')\n"
		"#BEGIN_TEXT\n"
	)
	subjects = pg_analyze.discipline.extract_dbsubjects(text)
	assert subjects == [
		"calculus",
		"linear algebra",
		"",
		"probability, statistics",
	]

	assert pg_analyze.discipline.bucket_subject("TBA") == "meta_missing"
	assert pg_analyze.discipline.bucket_subject("WeBWorK") == "meta_noise"
	assert pg_analyze.discipline.bucket_subject("thermodyanmics") == "engineering"


def test_bucket_subject_mapping_and_primary() -> None:
	subjects = [
		"",
		"physical chemistry",
		"heat transfer",
		"quantum mechanics",
		"bayesian inference",
		"linear algebra",
		"computer science",
		"financial accounting",
		"middle school",
		"tba",
		"zzzz-inserted text",
	]
	buckets = [pg_analyze.discipline.bucket_subject(s) for s in subjects]
	assert buckets == [
		"meta_missing",
		"chemistry",
		"engineering",
		"physics",
		"stats",
		"math",
		"cs",
		"finance",
		"grade_level",
		"meta_missing",
		"meta_noise",
	]

	assert pg_analyze.discipline.primary_discipline(["", "  ", "Linear Algebra"]) == "math"
	assert pg_analyze.discipline.primary_discipline([]) == "other"
	assert pg_analyze.discipline.primary_subject(["", "  ", "Linear Algebra"]) == "linear algebra"
