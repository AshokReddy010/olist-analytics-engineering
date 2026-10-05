-- One row per order. Built incrementally: each run only reprocesses recent orders.
-- The 3-day lookback picks up orders whose status or delivery date changed after they were first loaded.
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='fail'
    )
}}

with sequenced as (

    select
        *,
        row_number() over (
            partition by customer_unique_id
            order by purchased_at, order_id
        ) as customer_order_number
    from {{ ref('int_orders_enriched') }}

)

select
    *,
    customer_order_number = 1 as is_first_order
from sequenced

{% if is_incremental() %}
where purchased_at >= (select max(purchased_at) - interval 3 day from {{ this }})
{% endif %}
