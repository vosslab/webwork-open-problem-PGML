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


def test_dbchapter_dbsection_and_raw_pairs() -> None:
	text = (
		"## DBchapter('Linear Algebra')\n"
		"## DBsection(\"Matrix Operations\")\n"
		"## DBsubject('Probability, Statistics')\n"
		"## DBsubject(Probability, Statistics)\n"
	)

	subject_pairs = pg_analyze.discipline.extract_dbsubjects_pairs(text)
	assert subject_pairs[0] == ("Probability, Statistics", "probability, statistics")
	assert subject_pairs[1] == ("Probability", "probability")

	chap_pairs = pg_analyze.discipline.extract_dbchapters_pairs(text)
	assert chap_pairs == [("Linear Algebra", "linear algebra")]

	sec_pairs = pg_analyze.discipline.extract_dbsections_pairs(text)
	assert sec_pairs == [("Matrix Operations", "matrix operations")]
