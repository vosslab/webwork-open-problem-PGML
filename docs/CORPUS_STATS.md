# Corpus statistics

This document is a self-contained snapshot of corpus-level statistics for:

- **Full OPL**: a local run against upstream OPL.
- **PGML corpus (this fork)**: the curated PGML-forward subset.

The `pg_analyze` output files used to generate these numbers are temporary and are not expected to be kept in-repo.

For the 2026-01-17 snapshot below, those outputs lived locally under `full_OPL_output/` and `PGML_corpus_output/`.

## Highlights

- The curated PGML corpus is about 13% of full OPL by `*.pg` file count (9,386 vs 72,734).
- Evaluator extraction is predominantly PGML-derived in this fork (most files are `widgets=some,eval=pgml_only`).
- The curated PGML corpus is much more math-heavy by DBsubject (77.8% vs 61.5%) and greatly reduces physics by DBsubject (0.6% vs 6.2%).
- This fork is mostly `Contrib/` and `Pending/`, while full OPL has a large `OpenProblemLibrary/` component.

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

| Metric | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `*.pg` files | 72,734 | 9,386 |
| DBsubject lines | 70,463 | 9,017 |

## DB tagging coverage

Counts below refer to header comment lines only (for example, `## DBsubject(...)`).

| Tag | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `## DBsubject(...)` | 70,463 (96.9%) | 9,017 (96.1%) |
| `## DBchapter(...)` | 70,299 (96.7%) | 8,960 (95.4%) |
| `## DBsection(...)` | 69,711 (95.9%) | 8,787 (93.6%) |

Normalization snapshot for DBsubject values:

| Metric | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| distinct raw DBsubject strings | 128 | 55 |
| distinct normalized DBsubject strings | 119 | 54 |
| DBsubject lines changed by normalization | 306 | 2 |

## Interaction profile

### Macro census (selected)

Counts below are "files that load this macro" (not total loads).

| Macro | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `PGML.pl` | 18,075 | 9,386 |
| `MathObjects.pl` | 48,691 | 8,594 |
| `parserPopUp.pl` | 7,964 | 2,508 |
| `parserRadioButtons.pl` | 6,578 | 2,058 |
| `parserAssignment.pl` | 1,616 | 528 |

### Type counts

Counts below are per-file, multi-label type counts (a file may contribute to multiple types).

| Type | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `numeric_entry` | 44,575 | 9,332 |
| `multiple_choice` | 37,516 | 3,144 |
| `multipart` | 30,828 | 4,879 |
| `graph_like` | 8,908 | 1,305 |
| `assignment_ordering` | 1,616 | 528 |
| `matching` | 189 | 0 |

### Most common type x widget-kind pairs

"%" below is out of total `*.pg` files.

| Type | Widget kind | Full OPL | PGML corpus (this fork) |
|---|---|---:|---:|
| `numeric_entry` | `pgml_blank` | 10,446 (14.4%) | 9,326 (99.4%) |
| `multiple_choice` | `pgml_blank` | 3,876 (5.3%) | 3,144 (33.5%) |
| `multipart` | `pgml_blank` | 2,292 (3.2%) | 4,878 (52.0%) |
| `graph_like` | `pgml_blank` | (not in full top pairs) | 1,302 (13.9%) |
| `numeric_entry` | `blank` | 9,246 (12.7%) | 74 (0.8%) |
| `multiple_choice` | `blank` | 4,656 (6.4%) | (not in PGML top pairs) |
| `multipart` | `blank` | 4,685 (6.4%) | (not in PGML top pairs) |
| `multiple_choice` | `radio` | 2,521 (3.5%) | 258 (2.7%) |
| `numeric_entry` | `radio` | 2,489 (3.4%) | 256 (2.7%) |
| `multiple_choice` | `popup` | 846 (1.2%) | 503 (5.4%) |
| `numeric_entry` | `popup` | 822 (1.1%) | 501 (5.3%) |
| `multipart` | `radio` | 678 (0.9%) | 221 (2.4%) |
| `multipart` | `popup` | 607 (0.8%) | 427 (4.5%) |
| `multiple_choice` | `checkbox` | (not in full top pairs) | 69 (0.7%) |
| `numeric_entry` | `checkbox` | (not in full top pairs) | 69 (0.7%) |
| `matching` | `pgml_blank` | (not in full top pairs) | 0 |

### Widget kind coverage

Each file contributes to zero or more type buckets, but can contribute to multiple widget kinds.

| Widget kind | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `pgml_blank` | 15,163 (20.8%) | 9,379 (99.9%) |
| `blank` | 35,071 (48.2%) | 74 (0.8%) |
| `popup` | 1,721 (2.4%) | 503 (5.4%) |
| `radio` | 5,689 (7.8%) | 258 (2.7%) |
| `checkbox` | 2,037 (2.8%) | 69 (0.7%) |
| `none` | 15,169 (20.9%) | 4 (0.0%) |

## Evaluator coverage

### Evaluator coverage buckets

Each file contributes to exactly one coverage bucket.

| Coverage bucket | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `widgets=some,eval=ans_only` | 43,004 (59.1%) | 0 (0.0%) |
| `widgets=some,eval=pgml_only` | 13,183 (18.1%) | 9,140 (97.4%) |
| `widgets=some,eval=both` | 405 (0.6%) | 239 (2.5%) |
| `widgets=some,eval=none` | 758 (1.0%) | 0 (0.0%) |
| `widgets=none,eval=none` | 8,177 (11.2%) | 4 (0.0%) |
| `widgets=none,eval=ans_only` | 7,196 (9.9%) | 0 (0.0%) |
| `widgets=none,eval=pgml_only` | 11 (0.0%) | 3 (0.0%) |

### Evaluator source by type (exclusive)

For each type bucket, what fraction is `pgml_only` vs `ans_only` vs `both` vs `none`.

| Type | Files (full) | `ans_call` (full) | `pgml_payload` (full) | `pgml_star_spec` (full) | `none` (full) | Files (PGML) | `ans_call` (PGML) | `pgml_payload` (PGML) | `pgml_star_spec` (PGML) | `none` (PGML) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `numeric_entry` | 44,575 (100.0%) | 19,513 (43.8%) | 25,348 (56.8%) | 54 (0.1%) | 332 (0.7%) | 9,332 (100.0%) | 234 (2.5%) | 9,296 (99.6%) | 46 (0.5%) | 3 (0.0%) |
| `multiple_choice` | 37,516 (100.0%) | 8,520 (22.7%) | 29,200 (77.8%) | 12 (0.0%) | 70 (0.2%) | 3,144 (100.0%) | 139 (4.4%) | 3,142 (99.9%) | 12 (0.4%) | 0 (0.0%) |
| `multipart` | 30,828 (100.0%) | 5,463 (17.7%) | 25,576 (83.0%) | 42 (0.1%) | 84 (0.3%) | 4,879 (100.0%) | 239 (4.9%) | 4,857 (99.5%) | 35 (0.7%) | 0 (0.0%) |
| `graph_like` | 8,908 (100.0%) | 770 (8.6%) | 8,170 (91.7%) | 6 (0.1%) | 35 (0.4%) | 1,305 (100.0%) | 13 (1.0%) | 1,303 (99.8%) | 6 (0.5%) | 0 (0.0%) |
| `assignment_ordering` | 1,616 (100.0%) | 1,616 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 528 (100.0%) | 528 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `matching` | 189 (100.0%) | 188 (99.5%) | 1 (0.5%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

## Discipline breakdown (DBsubject lines)

Counts below are DBsubject-line counts (not file counts).

| Discipline | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| math | 43,358 (61.5%) | 7,014 (77.8%) |
| physics | 4,384 (6.2%) | 51 (0.6%) |
| engineering | 5,911 (8.4%) | 1,398 (15.5%) |
| stats | 2,967 (4.2%) | 100 (1.1%) |
| finance | 854 (1.2%) | 15 (0.2%) |
| cs | 54 (0.1%) | 43 (0.5%) |
| grade_level | 356 (0.5%) | 10 (0.1%) |
| meta_noise | 11,168 (15.8%) | 51 (0.6%) |
| meta_missing | 911 (1.3%) | 312 (3.5%) |
| other | 500 (0.7%) | 23 (0.3%) |
| chemistry | 0 (0.0%) | 0 (0.0%) |
| life_sciences | 0 (0.0%) | 0 (0.0%) |

## Path provenance

"Path provenance" is the top-level folder under `problems/`.

| Path top | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `OpenProblemLibrary` | 37,676 (51.8%) | 0 (0.0%) |
| `Contrib` | 31,533 (43.4%) | 7,088 (75.5%) |
| `Pending` | 3,525 (4.8%) | 2,298 (24.5%) |

## Complexity proxies

### Input-count percentiles

"Input count" counts the number of student-visible input blanks per problem.

| Percentile | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| p50 | 1 | 1 |
| p90 | 2 | 4 |
| p99 | 6 | 8 |

### Multipart-only input-count distribution

This distribution is restricted to files classified as `multipart`.

| Inputs per multipart file | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| 1 | 11,903 (38.6%) | 2,402 (49.2%) |
| 2 | 6,330 (20.5%) | 1,112 (22.8%) |
| 3 | 4,174 (13.5%) | 602 (12.3%) |
| 4 | 2,362 (7.7%) | 332 (6.8%) |
| 5 | 1,418 (4.6%) | 161 (3.3%) |
| 6+ | 4,641 (15.1%) | 270 (5.5%) |

## Randomization and duplicates

Randomization proxy is a cheap signal of randomization usage (for example, `random(...)`, `rand(...)`, `list_random(...)`).

| Metric | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| Randomization proxy coverage | 19,485 (26.8%) | 4,250 (45.3%) |
| Exact-duplicate files (SHA-256) | 2,824 (3.9%) | 113 (1.2%) |
| Exact-duplicate groups | 1,104 | 45 |
| Largest exact-duplicate group size | 17 | 13 |

## Macro risk surface

### Top non-baseline macros

Baseline excluded: `PGstandard.pl`, `PGcourse.pl`, `MathObjects.pl`, `PGML.pl`.

| Macro | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `AnswerFormatHelp.pl` | 8,049 | 0 |
| `parserPopUp.pl` | 7,964 | 2,508 |
| `parserRadioButtons.pl` | 6,578 | 2,058 |
| `contextFraction.pl` | 6,586 | 1,683 |
| `answerHints.pl` | 6,545 | 1,915 |
| `PGauxiliaryFunctions.pl` | 6,482 | 1,304 |
| `PGbasicmacros.pl` | 6,222 | 0 |
| `PGanswermacros.pl` | 5,991 | 1,303 |
| `PG_CAPAmacros.pl` | 4,861 | 0 |
| `BrockPhysicsMacros.pl` | 4,772 | 0 |

### Selected macro counts

A small curated list of macros that tend to imply higher implementation complexity.

| Macro | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| `parserNumberWithUnits.pl` | 1,172 | 119 |
| `parserMultiAnswer.pl` | 7,004 | 739 |
| `parserAssignment.pl` | 1,616 | 528 |
| `parserFormulaUpToConstant.pl` | 1,289 | 267 |
| `PGtikz.pl` | 734 | 277 |
| `PJmacros.pl` | 250 | 0 |
| `unionTables.pl` | 2,267 | 0 |
| `PeriodicRerandomization.pl` | 2,410 | 0 |

## Content hints

These are simple keyword hits intended to be interpreted as "weak evidence" only.

| Content hint | Full OPL | PGML corpus (this fork) |
|---|---:|---:|
| Chem-ish term hit coverage | 2,638 (3.6%) | 55 (0.6%) |
| Bio-ish term hit coverage | 238 (0.3%) | 10 (0.1%) |

### Top chem-ish terms

| Term | Full OPL (files) | PGML corpus (files) |
|---|---:|---:|
| acid | 1,253 | 12 |
| base | 592 | 8 |
| mole | 346 | 0 |
| mol | 273 | 0 |
| equilibrium | 218 | 0 |
| polymer | 170 | 1 |
| pH | 150 | 0 |
| stoichiometry | 84 | 0 |
| redox | 63 | 0 |
| titration | 23 | 0 |

### Top bio-ish terms

| Term | Full OPL (files) | PGML corpus (files) |
|---|---:|---:|
| cell | 120 | 3 |
| protein | 44 | 1 |
| DNA | 21 | 0 |
| gene | 19 | 0 |
| bacteria | 14 | 0 |
| RNA | 10 | 0 |
| enzyme | 8 | 0 |
| virus | 7 | 0 |
| lipid | 6 | 0 |
| antibody | 5 | 0 |

## Problematic DBsubject values

These are normalized DBsubject values that ended up in `meta_noise`, `meta_missing`, or `other` buckets.

| Normalized DBsubject value | Full OPL (lines) | PGML corpus (lines) |
|---|---:|---:|
| ZZZ-Inserted Text | 7,193 | 0 |
| WeBWorK | 2,383 | 10 |
| (empty) | 693 | 10 |
| History | 687 | 0 |
| NECAP | 252 | 0 |
| Middle School | 158 | 0 |
| Elementary School | 104 | 0 |
| Subject | 89 | 3 |
| TBA | 16 | 0 |
| Demos | 1 | 0 |
| algeba | 1 | 0 |

## Notes

- In OPL, `grade_level` is overwhelmingly K-12 tagging (for example "Middle School"), not pedagogy.
- Chemistry and life sciences are structurally absent as DBsubject labels in both runs above.
