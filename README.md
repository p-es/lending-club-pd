# Credit risk modelling on LendingClub loans

**Status: in progress (week 1 of 4) — data acquisition and audit.**

Probability-of-default modelling on ~2.26M US personal loans (LendingClub,
2007–2018), built with an explicit focus on the methodological traps this
popular dataset is known for: leakage from post-origination columns,
random cross-validation across drifting vintages, and mislabelling of
censored (still-active) loans. End goal is a properly validated,
calibrated PD model evaluated on out-of-time data, with a portfolio-level
profit comparison against LendingClub's own risk grades.

## Data

- **Source:** [All Lending Club loan data](https://www.kaggle.com/datasets/wordsforthewise/lending-club)
  (Kaggle, licence CC0), downloaded 18 Aug 2026.
- **Files:** `accepted_2007_to_2018Q4.csv.gz` (~2.26M rows, 151 columns) and
  `rejected_2007_to_2018Q4.csv.gz` (~27.6M rows). Data is not committed to
  this repository; place the files in `data/raw/` to reproduce.
- **Reference:** the LendingClub data dictionary (`LCDataDictionary.xlsx`)
  is used for the column-by-column leakage audit (week 2).

## Data quirks found so far

The raw accepted-loans CSV is a concatenation of separate export files, each
ending with a two-line summary footer ("Total amount funded in policy code
1/2: …"). Together with a few blank lines, this makes **33 non-data rows**
that break integer parsing of the `id` column. Rather than loading with
`ignore_errors` (which silently drops anything unparseable), I typed `id`
explicitly as VARCHAR, enabled full-file type scanning (`sample_size = -1`),
and excluded rows with `loan_amnt IS NULL` — so the exclusion is explicit,
counted, and documented. See `sql/01_load_raw.sql`.

## Structure

- `sql/` — all data loading, cohort construction, and audit queries (DuckDB)
- `src/lending_pd/` — reusable Python package (DB access, features, training)
- `notebooks/` — exploration and narrative
- `reports/` — figures and written artefacts (leakage audit, experiment log)

## Reproducing