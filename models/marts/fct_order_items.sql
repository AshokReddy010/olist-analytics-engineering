-- One row per item sold, with its product category and the order's date and status.
select
    i.order_id,
    i.order_item_number,
    i.product_id,
    p.category_name,
    i.seller_id,
    o.customer_unique_id,
    o.purchase_date,
    o.purchase_month,
    o.order_status,
    o.is_cancelled,
    i.item_price,
    i.freight_value
from {{ ref('stg_order_items') }} as i
inner join {{ ref('int_orders_enriched') }} as o
    on i.order_id = o.order_id
left join {{ ref('int_products_translated') }} as p
    on i.product_id = p.product_id
