"""Train and evaluate PD models under out-of-time split. Learnt on the training window
(2012Q1-2014Q4) and applied unchanged to the test window (2015Q1-2015Q3)."""

import json

import duckdb
import joblib
import pandas as pd
from pyparsing import results
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from lending_pd.config import (CATEGORICAL_FEATURES, DB_PATH, MODEL_A_FEATURES, MODEL_B_EXTRA, ROOT, TRAIN_END)
from lending_pd.features import apply_caps, engineer_features, fit_caps

import lightgbm as lgb

from pandas.api.types import CategoricalDtype


MODELS_DIR = ROOT / "models"
METRICS_PATH = ROOT / "reports" / "metrics.json"


def load_engineered() -> pd.DataFrame:
    """Load the engineered features from the database."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("SELECT * FROM cohort").df()
    con.close()
    return engineer_features(df)

def temporal_split(df):
    """Split the dataframe into train and test sets based on the TRAIN_END date."""
    train = df[df["issue_date"] <= TRAIN_END].copy()
    test = df[df["issue_date"] > TRAIN_END].copy()
    return train, test

def add_state_grp(train, test, top_n=10):
    """Add a new categorical feature 'state_grp' to both train and test sets based on the top N states."""
    top = train["addr_state"].value_counts().nlargest(top_n).index
    for part in (train, test):
        part["state_grp"] = part["addr_state"].where(part["addr_state"].isin(top), "Other")
    return train, test

def build_logistic(numeric, categorical):
    """Build a logistic regression model with preprocessing for numeric and categorical features."""
    num = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])
    cat = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    pre = ColumnTransformer([("num", num, numeric), ("cat", cat, categorical)])
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000, random_state=42))])  

def evaluate(name, y_true, p, probabilistic=True):
    """Evaluate the model's performance using various metrics and save the results."""
    out = {
        "model": name,
        "roc_auc": round(float(roc_auc_score(y_true, p)), 4),
        "pr_auc": round(float(average_precision_score(y_true, p)), 4),
        "observed_default_rate": round(float(y_true.mean()), 4),
        "n_test": int(len(y_true)),
        }
    if probabilistic:
        out["brier"] = round(float(brier_score_loss(y_true, p)), 4)
        out["mean_predicted_pd"] = round(float(pd.Series(p).mean()), 4)
    return out

# Gradient boosting model (LightGBM) for comparison



VAL_START = "2014-07-01" # last two training quarters held for early stopping.

def to_categorical(train_X, other_X, categorical):
    """Convert specified columns to categorical dtype for LightGBM."""
    train_X, other_X = train_X.copy(), other_X.copy()
    for c in categorical:
        train_X[c] = train_X[c].astype("category")
        dtype = CategoricalDtype(categories=train_X[c].cat.categories)
        unseen = ~other_X[c].isin(dtype.categories) & other_X[c].notna()
        if unseen.any():
            print(f"Warning: {int(unseen.sum())} unseen categories in column '{c}' will be set to NaN."
                  f"categories: {sorted(other_X.loc[unseen, c].unique())}")
        other_X[c] = other_X[c].where(~unseen).astype(dtype)
    return train_X, other_X



def main():
    df = load_engineered()
    train, test = temporal_split(df)
    caps = fit_caps(train)
    train, test = apply_caps(train, caps), apply_caps(test, caps)
    train, test = add_state_grp(train, test)
    y_tr, y_te = train["default_flag"], test["default_flag"]

    results = []
    # Benchmark for Model A (the platform's own pricing as a ranking score)
    results.append(evaluate("benchmark_int_rate_alone", y_te, test["int_rate"], probabilistic=False))

    specs = {
        "logistic_A": (MODEL_A_FEATURES, CATEGORICAL_FEATURES),
        "logistic_B": (MODEL_A_FEATURES + MODEL_B_EXTRA, CATEGORICAL_FEATURES + ["sub_grade"]),
    }

    for name, (features, categorical) in specs.items():
        numeric = [f for f in features if f not in categorical]
        cols = numeric + categorical
        pipe = build_logistic(numeric, categorical)
        pipe.fit(train[cols], y_tr)
        p = pipe.predict_proba(test[cols])[:, 1]
        results.append(evaluate(name, y_te, p))
        joblib.dump(pipe, MODELS_DIR / f"{name}.joblib")

    fit_lgbm(train, test, y_tr, y_te, MODEL_A_FEATURES, CATEGORICAL_FEATURES, "lgbm_A", results)
    fit_lgbm(train, test, y_tr, y_te, MODEL_A_FEATURES + MODEL_B_EXTRA, CATEGORICAL_FEATURES + ["sub_grade"], "lgbm_B", results)

    METRICS_PATH.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

def fit_lgbm(train, test, y_tr, y_te, features, categorical, name, results):
    numeric = [f for f in features if f not in categorical]
    cols = numeric + categorical

    sub = train[train["issue_date"] < VAL_START]
    val = train[train["issue_date"] >= VAL_START]
    X_sub, X_val = to_categorical(sub[cols], val[cols], categorical)

    clf = lgb.LGBMClassifier(
        n_estimators=20000,
        learning_rate=0.05,
        num_leaves=31,
        min_child_samples=200,
        random_state=42,
    )
    clf.fit(X_sub, sub["default_flag"],
            eval_X=X_val, eval_y=val["default_flag"],
            eval_metric="auc",
            callbacks=[lgb.early_stopping(100, verbose=False)])

    X_tr_full, X_te = to_categorical(train[cols], test[cols], categorical)
    p = clf.predict_proba(X_te)[:, 1]
    results.append(evaluate(name, y_te, p))
    joblib.dump(clf, MODELS_DIR / f"{name}.joblib")
    return clf


if __name__ == "__main__":
    main()
    



