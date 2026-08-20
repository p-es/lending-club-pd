import duckdb
import pytest
from lending_pd.config import (LEAKY_COLUMNS, MODEL_A_FEATURES, MODEL_B_EXTRA)


DB = "data/processed/lending.duckdb"

def test_model_features_disjoint_from_leaky():
    """Check that the features used in the models do not include any leaky columns."""
    feats = set(MODEL_A_FEATURES) | set(MODEL_B_EXTRA)
    assert feats.isdisjoint(LEAKY_COLUMNS), "Model features include leaky columns!"

def test_cohort_contains_only_terminal_statuses():
    """Check that the cohort used for modeling contains only loans with terminal statuses."""
    con = duckdb.connect(DB, read_only=True)
    statuses = {r[0] for r in
                con.execute("SELECT DISTINCT loan_status FROM cohort").fetchall()}
    assert statuses == {"Fully Paid", "Charged Off"}

def test_cohort_is_36_month_matured_window():
    """Check that the cohort used for modeling contains only 36-month matured loans."""
    con = duckdb.connect(DB, read_only=True)
    lo, hi = con.execute(
        "SELECT min(issue_date), max(issue_date) FROM cohort").fetchone()
    assert str(lo) >= "2012-01-01" and str(hi) <= "2015-09-30"