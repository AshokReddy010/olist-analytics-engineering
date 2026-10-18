"""Export the marts as one compact JSON file for the web dashboard (site/data/olist.json).

Run from the project folder after `dbt build`:
    python scripts/export_web.py
"""
import json
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "data" / "olist.json"
FIRST, LAST = "2017-01-01", "2018-08-01"     # complete months; the data thins out before and after


def rows(con, sql):
    rel = con.execute(sql)
    cols = [d[0] for d in rel.description]
    def clean(v):
        if v is not None and type(v).__name__ == "Decimal":
            v = float(v)
        return round(v, 6) if isinstance(v, float) else v  # rounded so parallel sums export identically

    return [dict(zip(cols, (clean(v) for v in r), strict=True)) for r in rel.fetchall()]


def main():
    con = duckdb.connect(str(ROOT / "olist.duckdb"), read_only=True)
    kpi = rows(con, f"""
        select count(*) orders, count(distinct customer_unique_id) customers,
               sum(order_value) filter (where not is_cancelled) revenue,
               avg(review_score) avg_review,
               avg(case when is_late then 1.0 else 0.0 end) filter (where is_delivered) late_share,
               median(days_to_deliver) filter (where is_delivered) median_days_to_deliver
        from fct_orders where purchase_month between '{FIRST}' and '{LAST}'""")[0]
    kpi["sellers"] = con.execute("select count(*) from dim_sellers").fetchone()[0]
    kpi["period"] = [FIRST[:7], LAST[:7]]

    monthly = rows(con, f"""
        select strftime(purchase_month, '%Y-%m') as month, count(*) orders,
               sum(order_value) filter (where not is_cancelled) revenue,
               avg(review_score) avg_review,
               avg(case when is_late then 1.0 else 0.0 end) filter (where is_delivered) late_share
        from fct_orders where purchase_month between '{FIRST}' and '{LAST}' group by 1 order by 1""")

    lateness = rows(con, """
        with o as (
            select review_score, date_diff('day', estimated_delivery_date, cast(delivered_at as date)) as late_days
            from fct_orders where is_delivered and delivered_at is not null and review_score is not null)
        select case when late_days <= -15 then '15+ days early' when late_days <= -8 then '8-14 days early'
                    when late_days <= -1 then '1-7 days early' when late_days = 0 then 'on the day'
                    when late_days <= 3 then '1-3 days late' when late_days <= 7 then '4-7 days late'
                    when late_days <= 14 then '8-14 days late' else '15+ days late' end bucket,
               min(late_days) sort_key, count(*) orders, avg(review_score) avg_review,
               avg(case when review_score = 1 then 1.0 else 0.0 end) one_star,
               avg(case when review_score = 5 then 1.0 else 0.0 end) five_star
        from o group by 1 order by 2""")

    states = rows(con, f"""
        select customer_state state, count(*) orders, sum(order_value) filter (where not is_cancelled) revenue,
               median(days_to_deliver) filter (where is_delivered) median_days,
               avg(case when is_late then 1.0 else 0.0 end) filter (where is_delivered) late_share,
               avg(review_score) avg_review
        from fct_orders where purchase_month between '{FIRST}' and '{LAST}' group by 1 order by orders desc""")

    categories = rows(con, f"""
        with i as (
            select i.*, o.review_score, o.is_late, o.is_delivered
            from fct_order_items i join fct_orders o using (order_id)
            where i.purchase_month between '{FIRST}' and '{LAST}' and not i.is_cancelled)
        select coalesce(category_name, 'unknown') category, count(distinct order_id) orders, sum(item_price) revenue,
               median(item_price) median_price, avg(freight_value / nullif(item_price, 0)) freight_share,
               avg(review_score) avg_review,
               avg(case when is_late then 1.0 else 0.0 end) filter (where is_delivered) late_share
        from i group by 1 order by revenue desc limit 20""")

    funnel = rows(con, "select * from mart_funnel_by_origin order by leads desc")
    cohorts = rows(con, """
        select strftime(cohort_month, '%Y-%m') cohort, months_since_first_order m, cohort_size, active_customers,
               retention_rate from mart_cohort_retention order by cohort, m""")
    pay = rows(con, f"""
        select main_payment_type as type, count(*) orders, avg(max_installments) avg_installments,
               sum(payment_total) paid from fct_orders
        where purchase_month between '{FIRST}' and '{LAST}' and main_payment_type is not null group by 1 order by 2 desc""")
    con.close()

    scores = pd.read_csv(ROOT / "analysis" / "lead_scores_test_period.csv")
    scores["decile"] = pd.qcut(scores["score"].rank(method="first", ascending=False), 10, labels=range(1, 11)).astype(int)
    deciles = scores.groupby("decile").agg(leads=("target", "size"), closed=("target", "sum")).reset_index()
    deciles["close_rate"] = (deciles["closed"] / deciles["leads"]).round(6)
    lead = {"base_rate": float(scores["target"].mean()), "deciles": deciles.to_dict("records")}

    doc = {"kpi": kpi, "monthly": monthly, "lateness": lateness, "states": states, "categories": categories,
           "funnel": funnel, "cohorts": cohorts, "payments": pay, "lead_scoring": lead}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, default=str, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
