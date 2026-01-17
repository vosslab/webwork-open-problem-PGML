# Standard Library
import pytest

# Local modules
import pg_analyze.main


@pytest.mark.parametrize(
	"label,text,check",
	[
		(
			"hash_in_strings",
			"$x = '# not a comment'; # comment\n"
			"$y = \"# not a comment\"; # comment\n"
			"ANS(num_cmp(1));\n",
			lambda r: (r["ans_count"] == 1),
		),
		(
			"heredoc_body_parentheses",
			"PGML::Format(<<END_PGML);\n"
			"(( not code ))) # keep\n"
			"END_PGML\n"
			"ANS(num_cmp(1));\n",
			lambda r: (r["ans_count"] == 1),
		),
		(
			"heredoc_body_parens_in_call_args",
			"loadMacros(\n"
			"  <<END_HERE,\n"
			") ) ) # not code\n"
			"END_HERE\n"
			"  \"PGstandard.pl\",\n"
			");\n",
			lambda r: ("PGstandard.pl" in r["loadMacros"]),
		),
		(
			"loadmacros_mixed_quotes_whitespace",
			"loadMacros(  \"PGstandard.pl\" ,\n"
			"  'MathObjects.pl' ,  \"parserRadioButtons.pl\"  );\n"
			"ANS(num_cmp(1));\n",
			lambda r: (r["loadMacros"] == ["PGstandard.pl", "MathObjects.pl", "parserRadioButtons.pl"]),
		),
		(
			"ans_multiline",
			"ANS(\n"
			"  num_cmp(\n"
			"    3\n"
			"  )\n"
			");\n",
			lambda r: (r["ans_count"] == 1 and r["evaluator_kinds"] == ["num_cmp"]),
		),
		(
			"multianswer_ctor_single_ans",
			"$ma = MultiAnswer(Real(1), Real(2));\n"
			"ANS($ma->cmp());\n",
			lambda r: ("multipart" in r["types"]),
		),
		(
			"named_ans_rule_evaluator_ref",
			"NAMED_ANS_RULE('ans1');\n"
			"ANS(named_ans_rule('ans1'));\n",
			lambda r: ("ans1" in r.get("named_rule_refs", [])),
		),
		(
			"pgml_blanks_only",
			"BEGIN_PGML\n"
			"[_] [__]\n"
			"END_PGML\n",
			lambda r: (r["input_count"] == 2 and "pgml_blank" in r["widget_kinds"]),
		),
		(
			"include_pgproblem_wrapper",
			"includePGproblem('foo/bar.pg');\n",
			lambda r: (r["ans_count"] == 0),
		),
		(
			"named_ans_rule_order_wiring",
			"NAMED_ANS_RULE('ans1');\n"
			"ANS(num_cmp(1));\n",
			lambda r: (r["wiring_empty"] is False),
		),
		(
			"two_ans_no_wiring_needs_review",
			"ANS(num_cmp(1));\n"
			"ANS(num_cmp(2));\n",
			lambda r: (r["ans_count"] == 2 and r["needs_review"] is True),
		),
		(
			"radio_buttons_widget",
			"$rb = RadioButtons([\"A\",\"B\"],\"A\");\n"
			"ANS($rb->cmp());\n",
			lambda r: ("multiple_choice" in r["types"] and "radio" in r["widget_kinds"]),
		),
		(
			"ordering_widget",
			"$s = Sort([1,2,3]);\n"
			"ANS($s->cmp());\n",
			lambda r: ("ordering" in r["types"] and "ordering" in r["widget_kinds"]),
		),
		(
			"string_cmp",
			"ANS(str_cmp('hi'));\n",
			lambda r: ("fib_word" in r["types"] and "str_cmp" in r["evaluator_kinds"]),
		),
	],
)
def test_pg_analyze_regressions(label: str, text: str, check) -> None:
	record = pg_analyze.main.analyze_text(text=text, file_path=f"{label}.pg")
	assert check(record)
