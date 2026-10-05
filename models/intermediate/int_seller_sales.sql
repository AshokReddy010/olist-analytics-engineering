-- One row per seller that has made at least one valid sale: when they started and how much they sold.
select
    i.seller_id,
    min(o.purchased_at) as first_sale_at,
    max(o.purchased_at) as last_sale_at,
    count(distinct o.order_id) as order_count,
    sum(i.item_price) as revenue
from {{ ref('stg_order_items') }} as i
inner join {{ ref('stg_orders') }} as o
    on i.order_id = o.order_id
where o.order_status not in ('canceled', 'unavailable')
group by i.seller_id
