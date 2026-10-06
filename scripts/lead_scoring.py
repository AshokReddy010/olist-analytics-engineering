"""Score marketing leads by how likely they are to sign as a seller.

Reads fct_lead_funnel from the DuckDB file, trains a logistic regression on the
earlier leads, and tests it on the most recent 25% (a time-based split, so the
model is always judged on leads that came after the ones it learned from).

Run from the project folder after `dbt build`:
    python scripts/lead_scoring.py
"""
from pathlib import Path

import duckdb
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

TEST_SHARE = 0.25
TOP_LANDING_PAGES = 20

con = duckdb.connect("olist.duckdb", read_only=True)
leads = con.execute(
    """
    select lead_id, first_contact_date, origin, landing_page_id, is_closed
    from fct_lead_funnel
    order by first_contact_date, lead_id
    """
).df()
con.close()

# Features known on the day of first contact. Nothing from after signing is used,
# so the model cannot peek at the outcome.
leads["first_contact_date"] = pd.to_datetime(leads["first_contact_date"])
leads["contact_weekday"] = leads["first_contact_date"].dt.day_name()
leads["target"] = leads["is_closed"].astype(int)

split = int(len(leads) * (1 - TEST_SHARE))
train, test = leads.iloc[:split].copy(), leads.iloc[split:].copy()

# Keep the busiest landing pages as their own category and group the rest,
# using the training period only to decide which pages count as busy.
top_pages = train["landing_page_id"].value_counts().head(TOP_LANDING_PAGES).index
for part in (train, test):
    part["landing_page_group"] = part["landing_page_id"].where(
        part["landing_page_id"].isin(top_pages), "other"
    )

features = ["origin", "landing_page_group", "contact_weekday"]
model = Pipeline(
    [
        ("encode", ColumnTransformer([("onehot", OneHotEncoder(handle_unknown="ignore"), features)])),
        ("classify", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ]
)
model.fit(train[features], train["target"])
test["score"] = model.predict_proba(test[features])[:, 1]

# Baseline: score each lead by its channel's close rate in the training period.
origin_rate = train.groupby("origin")["target"].mean()
test["baseline_score"] = test["origin"].map(origin_rate).fillna(train["target"].mean())


def top_decile_rate(frame, column):
    cutoff = max(1, len(frame) // 10)
    return frame.sort_values(column, ascending=False).head(cutoff)["target"].mean()


base_rate = test["target"].mean()
rows = []
for label, column in [("Channel close rate only (baseline)", "baseline_score"), ("Logistic regression", "score")]:
    top = top_decile_rate(test, column)
    rows.append(
        {
            "Model": label,
            "ROC AUC": round(roc_auc_score(test["target"], test[column]), 3),
            "Average precision": round(average_precision_score(test["target"], test[column]), 3),
            "Close rate in top 10% of scores": f"{top:.1%}",
            "Lift over average": f"{top / base_rate:.2f}x",
        }
    )
results = pd.DataFrame(rows)

summary = [
    "# Lead scoring results",
    "",
    f"- Leads: {len(leads):,} ({len(train):,} to train, {len(test):,} to test)",
    f"- Training period: {train['first_contact_date'].min():%d %b %Y} to {train['first_contact_date'].max():%d %b %Y}",
    f"- Test period: {test['first_contact_date'].min():%d %b %Y} to {test['first_contact_date'].max():%d %b %Y}",
    f"- Close rate in the test period: {base_rate:.1%}",
    "",
    results.to_markdown(index=False),
    "",
]
out = Path("analysis")
out.mkdir(exist_ok=True)
(out / "lead_scoring_results.md").write_text("\n".join(summary), encoding="utf-8")
test[["lead_id", "first_contact_date", "origin", "score", "target"]].sort_values("score", ascending=False).to_csv(
    out / "lead_scores_test_period.csv", index=False
)
print("\n".join(summary))
