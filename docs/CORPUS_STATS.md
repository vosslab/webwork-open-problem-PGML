# Corpus statistics

This document is a self-contained snapshot of corpus-level statistics for:

- Full OPL (a local run against upstream OPL).
- This PGML corpus (this fork).

The `pg_analyze` output files used to generate these numbers are temporary and are not expected to be kept in-repo.

For the 2026-01-17 snapshot below, those outputs lived locally under `full_OPL_output/` and `PGML_corpus_output/`.

## Highlights

- The curated PGML corpus is about 13% of full OPL by `*.pg` file count (9,386 vs 72,734).
- Evaluator extraction is predominantly PGML-derived in this fork (most files are `widgets=some,eval=pgml_only`).
- The curated PGML corpus is much more math-heavy by DBsubject (77.8% vs 61.5%) and greatly reduces physics by DBsubject
  (0.6% vs 6.2%).

## How to regenerate

Run `pg_analyze` and point it at a directory you do not plan to commit:

```bash
python3 -m pg_analyze.main -r problems -o /tmp/pg_analyze_output
```

The most relevant reports for the tables below are:

- `summary/corpus_profile.tsv`
- `summary/counts_all.tsv`
- `summary/coverage_widgets_vs_evaluator_source.tsv`
- `summary/discipline_counts.tsv`
- `summary/discipline_coverage.tsv`

## Snapshot date

The numbers below were recorded on 2026-01-17.

## Corpus size

- Full OPL:
  - `*.pg` files: 72,734
  - DBsubject lines: 70,463
- PGML corpus (this fork):
  - `*.pg` files: 9,386
  - DBsubject lines: 9,017

## Interaction profile (macro census)

Counts below are "files that load this macro" (not total loads).

- Full OPL:
  - `PGML.pl`: 18,075
  - `MathObjects.pl`: 48,691
  - `parserPopUp.pl`: 7,964
  - `parserRadioButtons.pl`: 6,578
  - `parserAssignment.pl`: 1,616
- PGML corpus (this fork):
  - `PGML.pl`: 9,386
  - `MathObjects.pl`: 8,594
  - `parserPopUp.pl`: 2,508
  - `parserRadioButtons.pl`: 2,058
  - `parserAssignment.pl`: 528

### Top macro loads

These are the top 12 macro files by "number of `*.pg` files that load the macro" (not total loads).

Full OPL:

| macro | files |
| --- | ---: |
| PGstandard.pl | 59,503 |
| PGcourse.pl | 52,620 |
| MathObjects.pl | 48,691 |
| PGchoicemacros.pl | 31,314 |
| PGML.pl | 18,075 |
| PGgraphmacros.pl | 8,908 |
| AnswerFormatHelp.pl | 8,049 |
| parserPopUp.pl | 7,964 |
| parserMultiAnswer.pl | 6,962 |
| parserRadioButtons.pl | 6,578 |
| answerHints.pl | 6,529 |
| contextFraction.pl | 6,467 |

PGML corpus (this fork):

| macro | files |
| --- | ---: |
| PGML.pl | 9,386 |
| PGstandard.pl | 9,376 |
| MathObjects.pl | 8,594 |
| PGcourse.pl | 7,682 |
| AnswerFormatHelp.pl | 3,188 |
| parserPopUp.pl | 2,508 |
| parserRadioButtons.pl | 2,058 |
| contextFraction.pl | 1,937 |
| parserMultiAnswer.pl | 1,740 |
| PGgraphmacros.pl | 1,305 |
| PGchoicemacros.pl | 1,219 |
| PCCmacros.pl | 1,190 |

## Interaction profile (type counts)

Counts below are per-file, multi-label type counts (a file may contribute to multiple types).

- Full OPL:
  - `numeric_entry`: 44,575
  - `multiple_choice`: 37,516
  - `multipart`: (see `counts_all.tsv`)
  - `graph_like`: 8,908
  - `assignment_ordering`: 1,616
  - `matching`: 189
- PGML corpus (this fork):
  - `numeric_entry`: 9,332
  - `multiple_choice`: 3,144
  - `multipart`: 4,879
  - `graph_like`: 1,305
  - `assignment_ordering`: 528
  - `matching`: 0 (not observed in this snapshot)

### Matching note

Matching-style problems appear to be rare even in full OPL (189 / 72,734 files = 0.3%) and were not observed in the
curated PGML corpus (0 / 9,386 files = 0.0%).

## Cross-tabs (selected highlights)

Cross-tabs count files by co-occurrence (a file can contribute to multiple rows due to multi-label types and multiple
detected widget/evaluator kinds).

### Most common type x widget-kind pairs

Full OPL (top 12 pairs):

| type | widget_kind | files | pct of all `*.pg` files |
| --- | --- | ---: | ---: |
| numeric_entry | blank | 24,750 | 34.0% |
| multiple_choice | blank | 20,508 | 28.2% |
| multipart | blank | 17,564 | 24.1% |
| numeric_entry | pgml_blank | 15,119 | 20.8% |
| other | none | 8,376 | 11.5% |
| multipart | pgml_blank | 7,782 | 10.7% |
| multiple_choice | radio | 5,816 | 8.0% |
| multiple_choice | none | 5,159 | 7.1% |
| graph_like | blank | 4,946 | 6.8% |
| multiple_choice | pgml_blank | 4,788 | 6.6% |
| numeric_entry | none | 4,089 | 5.6% |
| multiple_choice | popup | 3,473 | 4.8% |

PGML corpus (this fork) (top 12 pairs):

| type | widget_kind | files | pct of all `*.pg` files |
| --- | --- | ---: | ---: |
| numeric_entry | pgml_blank | 9,326 | 99.4% |
| multipart | pgml_blank | 4,878 | 52.0% |
| multiple_choice | pgml_blank | 3,144 | 33.5% |
| graph_like | pgml_blank | 1,302 | 13.9% |
| assignment_ordering | pgml_blank | 528 | 5.6% |
| multiple_choice | popup | 503 | 5.4% |
| numeric_entry | popup | 501 | 5.3% |
| multipart | popup | 427 | 4.5% |
| multiple_choice | radio | 258 | 2.7% |
| numeric_entry | radio | 256 | 2.7% |
| multipart | radio | 221 | 2.4% |
| graph_like | popup | 185 | 2.0% |

### Evaluator source by type

Percentages below are "pct of files in this type that have at least one evaluator from this source".

Full OPL:

| type | files | ans_call | pgml_payload | pgml_star_spec | none |
| --- | ---: | ---: | ---: | ---: | ---: |
| numeric_entry | 44,575 | 30,794 (69.1%) | 13,478 (30.2%) | 78 (0.2%) | 637 (1.4%) |
| multiple_choice | 37,516 | 33,044 (88.1%) | 4,260 (11.4%) | 20 (0.1%) | 430 (1.1%) |
| multipart | 30,828 | 23,736 (77.0%) | 6,920 (22.4%) | 54 (0.2%) | 544 (1.8%) |
| graph_like | 8,908 | 6,805 (76.4%) | 1,992 (22.4%) | 12 (0.1%) | 148 (1.7%) |
| assignment_ordering | 1,616 | 761 (47.1%) | 738 (45.7%) | 0 (0.0%) | 154 (9.5%) |
| fib_word | 3,619 | 3,511 (97.0%) | 120 (3.3%) | 1 (0.0%) | 4 (0.1%) |

PGML corpus (this fork):

| type | files | ans_call | pgml_payload | pgml_star_spec | none |
| --- | ---: | ---: | ---: | ---: | ---: |
| numeric_entry | 9,332 | 234 (2.5%) | 9,296 (99.6%) | 46 (0.5%) | 3 (0.0%) |
| multiple_choice | 3,144 | 139 (4.4%) | 3,142 (99.9%) | 12 (0.4%) | 0 (0.0%) |
| multipart | 4,879 | 239 (4.9%) | 4,857 (99.5%) | 35 (0.7%) | 0 (0.0%) |
| graph_like | 1,305 | 13 (1.0%) | 1,303 (99.8%) | 6 (0.5%) | 0 (0.0%) |
| assignment_ordering | 528 | 20 (3.8%) | 528 (100.0%) | 0 (0.0%) | 0 (0.0%) |
| fib_word | 96 | 6 (6.2%) | 96 (100.0%) | 1 (1.0%) | 0 (0.0%) |

## Histograms (selected)

### Inputs per problem

These are file counts per detected input-count bucket.

Full OPL (`*.pg` files: 72,734):

| input_count bucket | files | pct |
| --- | ---: | ---: |
| 0 | 15,384 | 21.2% |
| 1 | 32,579 | 44.8% |
| 2 | 9,625 | 13.2% |
| 3 | 4,994 | 6.9% |
| 4 | 3,464 | 4.8% |
| 5-9 | 5,168 | 7.1% |
| 10-19 | 1,149 | 1.6% |
| 20+ | 371 | 0.5% |

PGML corpus (this fork) (`*.pg` files: 9,386):

| input_count bucket | files | pct |
| --- | ---: | ---: |
| 0 | 7 | 0.1% |
| 1 | 5,163 | 55.0% |
| 2 | 1,809 | 19.3% |
| 3 | 837 | 8.9% |
| 4 | 458 | 4.9% |
| 5-9 | 861 | 9.2% |
| 10-19 | 215 | 2.3% |
| 20+ | 36 | 0.4% |

### PGML blank-marker counts

This is a file-level histogram of PGML blank markers detected inside PGML blocks (it is intentionally near-zero for
non-PGML problems).

Full OPL (`*.pg` files: 72,734):

| pgml_blank_marker_count bucket | files | pct |
| --- | ---: | ---: |
| 0 | 57,426 | 79.0% |
| 1 | 9,068 | 12.5% |
| 2 | 2,788 | 3.8% |
| 3 | 1,359 | 1.9% |
| 4 | 771 | 1.1% |
| 5-9 | 1,059 | 1.5% |
| 10-19 | 225 | 0.3% |
| 20+ | 38 | 0.1% |

PGML corpus (this fork) (`*.pg` files: 9,386):

| pgml_blank_marker_count bucket | files | pct |
| --- | ---: | ---: |
| 0 | 7 | 0.1% |
| 1 | 5,373 | 57.2% |
| 2 | 1,799 | 19.2% |
| 3 | 875 | 9.3% |
| 4 | 477 | 5.1% |
| 5-9 | 692 | 7.4% |
| 10-19 | 141 | 1.5% |
| 20+ | 22 | 0.2% |

### ANS(...) calls per problem

This counts `ANS(...)` calls (outside strings/comments). PGML-heavy problems often grade answers without explicit
`ANS(...)` calls, so this is not a measure of whether the problem is graded.

Full OPL (`*.pg` files: 72,734):

| ans_count bucket | files | pct |
| --- | ---: | ---: |
| 0 | 22,129 | 30.4% |
| 1 | 30,337 | 41.7% |
| 2 | 8,077 | 11.1% |
| 3 | 4,276 | 5.9% |
| 4 | 2,985 | 4.1% |
| 5-9 | 3,767 | 5.2% |
| 10-19 | 847 | 1.2% |
| 20+ | 316 | 0.4% |

PGML corpus (this fork) (`*.pg` files: 9,386):

| ans_count bucket | files | pct |
| --- | ---: | ---: |
| 0 | 9,147 | 97.5% |
| 1 | 160 | 1.7% |
| 2 | 29 | 0.3% |
| 3 | 19 | 0.2% |
| 4 | 16 | 0.2% |
| 5-9 | 13 | 0.1% |
| 10-19 | 2 | 0.0% |


## Evaluator coverage buckets

Each file contributes to exactly one coverage bucket:

- Full OPL (`*.pg` files: 72,734):
  - `widgets=some,eval=ans_only`: 43,004
  - `widgets=some,eval=pgml_only`: 13,183
  - `widgets=some,eval=both`: 405
  - `widgets=some,eval=none`: 758
  - `widgets=none,eval=none`: 8,177
  - `widgets=none,eval=ans_only`: 7,196
  - `widgets=none,eval=pgml_only`: 11
- PGML corpus (this fork) (`*.pg` files: 9,386):
  - `widgets=some,eval=pgml_only`: 9,140
  - `widgets=some,eval=both`: 239
  - `widgets=none,eval=none`: 4
  - `widgets=none,eval=pgml_only`: 3

## Discipline breakdown (DBsubject lines)

Counts below are DBsubject-line counts (not file counts).

Full OPL (70,463 DBsubject lines):

- Math: 43,358 (61.5%)
- Physics: 4,384 (6.2%)
- Engineering: 5,911 (8.4%)
- Stats: 2,967 (4.2%)
- Finance: 854 (1.2%)
- CS: 54 (0.1%)
- Grade level: 356 (0.5%)
- Meta noise: 11,168 (15.8%)
- Meta missing: 911 (1.3%)
- Other: 500 (0.7%)
- Chemistry: 0
- Life sciences: 0

PGML corpus (this fork) (9,017 DBsubject lines):

- Math: 7,014 (77.8%)
- Engineering: 1,398 (15.5%)
- Stats: 100 (1.1%)
- Physics: 51 (0.6%)
- CS: 43 (0.5%)
- Finance: 15 (0.2%)
- Grade level: 10 (0.1%)
- Meta noise: 51 (0.6%)
- Meta missing: 312 (3.5%)
- Other: 23 (0.3%)
- Chemistry: 0
- Life sciences: 0

## Notes

- In OPL, "grade level" is overwhelmingly K-12 tagging (for example "Middle School"), not pedagogy.
- Chemistry and life sciences are structurally absent as DBsubject labels in both runs above.
