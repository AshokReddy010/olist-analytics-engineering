-- One row per order: how many items it had and what they cost.
select
    order_id,
    count(*) as item_count,
    count(distinct product_id) as distinct_product_count,
    count(distinct seller_id) as seller_count,
    sum(item_price) as items_value,
    sum(freight_value) as freight_value
from {{ ref('stg_order_items') }}
group by order_id
