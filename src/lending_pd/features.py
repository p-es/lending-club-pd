"""Feature engineering for the LendingClub PD model.

All functions are stateless transforms except the winsorisation caps,
which must be *fitted on training data only* (see fit_caps/apply_caps).
"""

import numpy as np
import pandas as pd

EMP_LENGTH_MAP = {
    "< 1 year": 0, "1 year": 1, "2 years": 2, "3 years": 3, "4 years": 4, "5 years": 5,
    "6 years": 6, "7 years": 7, "8 years": 8, "9 years": 9, "10+ years": 10,
}

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
# Employment length: map to years, create missing indicator.
    out["emp_length_yrs"] = out["emp_length"].map(EMP_LENGTH_MAP)
    out["emp_length_missing"] = out["emp_length_yrs"].isna().astype(int)

# FICO: midpoint of band.
    out["fico_mid"] = (out["fico_range_low"] + out["fico_range_high"]) / 2

# Derived ratios: loan-to-income, installment burden, revolving balance to income.
    inc = out["annual_inc"].replace(0, np.nan)
    out["loan_to_income"] = out["loan_amnt"] / inc
    out["installment_burden"] = out["installment"] * 12 / inc
    out["revol_bal_to_income"] = out["revol_bal"] / inc

# Credit history length in years.
    ecl = pd.to_datetime(out["earliest_cr_line"], format="%b-%Y", errors="coerce")
    out["credit_hist_yrs"] = (out["issue_date"] - ecl).dt.days / 365.25

    return out

def apply_caps(df: pd.DataFrame, caps: dict) -> pd.DataFrame:
    """Apply winsorisation caps to a dataframe."""
    out = df.copy()
    for col, (lower, upper) in caps.items():
        out[col] = out[col].clip(lower=lower, upper=upper)
    return out


def fit_caps(train_df: pd.DataFrame) -> dict:
    """Winsorisation caps, fitted on TRAINING data only to avoid using
    test-period information."""
    return {
        "annual_inc": (train_df["annual_inc"].quantile(0.995),
                       train_df["annual_inc"].quantile(0.005)),
        "revol_util": (0.0, 120.0)
    }