-- Customer retention by cohort. A cohort is everyone whose first order fell in the same month.
-- One row per cohort and month offset: how many of that cohort ordered again N months later.
with customers as (

    select customer_unique_id, cohort_month
    from {{ ref('dim_customers') }}
    where cohort_month is not null

),

activity as (

    select distinct
        o.customer_unique_id,
        c.cohort_month,
        date_diff('month', c.cohort_month, o.purchase_month) as months_since_first_order
    from {{ ref('fct_orders') }} as o
    inner join customers as c
        on o.customer_unique_id = c.customer_unique_id
    where not o.is_cancelled

),

cohort_sizes as (

    select cohort_month, count(*) as cohort_size
    from customers
    group by cohort_month

)

select
    a.cohort_month,
    a.months_since_first_order,
    s.cohort_size,
    count(*) as active_customers,
    round(count(*) * 1.0 / s.cohort_size, 4) as retention_rate
from activity as a
inner join cohort_sizes as s
    on a.cohort_month = s.cohort_month
group by a.cohort_month, a.months_since_first_order, s.cohort_size
