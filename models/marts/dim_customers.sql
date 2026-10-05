-- One row per person (customer_unique_id). Cancelled and unavailable orders are excluded from the counts and values.
select
    customer_unique_id,
    arg_max(customer_state, purchased_at) as customer_state,
    arg_max(customer_city, purchased_at) as customer_city,
    min(purchased_at) filter (where not is_cancelled) as first_order_at,
    max(purchased_at) filter (where not is_cancelled) as last_order_at,
    cast(date_trunc('month', min(purchased_at) filter (where not is_cancelled)) as date) as cohort_month,
    count(*) filter (where not is_cancelled) as order_count,
    count(*) filter (where is_cancelled) as cancelled_order_count,
    coalesce(sum(order_value) filter (where not is_cancelled), 0) as lifetime_value,
    avg(review_score) filter (where not is_cancelled) as avg_review_score,
    count(*) filter (where not is_cancelled) > 1 as is_repeat_customer
from {{ ref('int_orders_enriched') }}
group by customer_unique_id
