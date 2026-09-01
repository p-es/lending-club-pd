LEAKY_COLUMNS = [
    "pymnt_plan", "out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv", "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries", "collection_recovery_fee", "last_pymnt_d", "last_pymnt_amnt", "next_pymnt_d", "last_credit_pull_d", "last_fico_range_high", "last_fico_range_low", "hardship_flag", "hardship_type", "hardship_reason", "hardship_status", "deferral_term", "hardship_amount", "hardship_start_date", "hardship_end_date", "payment_plan_start_date", "hardship_length", "hardship_dpd", "hardship_loan_status", "orig_projected_additional_accrued_interest", "hardship_payoff_balance_amount", "hardship_last_payment_amount", "debt_settlement_flag", "debt_settlement_flag_date", "settlement_status", "settlement_date", "settlement_amount", "settlement_percentage", "settlement_term", "loan_status", "default_flag",
]

# Model A: borrower raw attributes only, no leakage.
MODEL_A_FEATURES = [
    "loan_amnt", "annual_inc", "dti",
    "fico_mid", "revol_util", "revol_bal", "open_acc", "total_acc",
    "inq_last_6mths", "delinq_2yrs", "pub_rec", "pub_rec_bankruptcies",
    "mths_since_last_delinq",
    "emp_length_yrs", "emp_length_missing",
    "loan_to_income", "revol_bal_to_income",
    "credit_hist_yrs",
    "purpose", "home_ownership", "verification_status",
]
# Model B: adds the platform's own pricing.
MODEL_B_EXTRA = ["int_rate", "grade", "sub_grade"
]

#Week 3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "processed" / "lending.duckdb"

# Out-of-time split: train 2012Q1-2014Q4, test 2015Q1-2015Q3
# Random split model would see test perod regime, see 02_eda fig 1.

TRAIN_END = "2014-12-31"

CATEGORICAL_FEATURES = [
    "purpose", "home_ownership", "verification_status", "state_grp"
]

