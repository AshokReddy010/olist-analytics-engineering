-- One row per order, with the customer, the money, the review and delivery timing joined on.
select
    o.order_id,
    c.customer_unique_id,
    c.city as customer_city,
    c.state as customer_state,
    o.order_status,
    o.order_status = 'delivered' as is_delivered,
    o.order_status in ('canceled', 'unavailable') as is_cancelled,
    o.purchased_at,
    cast(o.purchased_at as date) as purchase_date,
    cast(date_trunc('month', o.purchased_at) as date) as purchase_month,
    o.approved_at,
    o.shipped_at,
    o.delivered_at,
    o.estimated_delivery_date,
    date_diff('day', o.purchased_at, o.delivered_at) as days_to_deliver,
    case
        when o.delivered_at is null then null
        else cast(o.delivered_at as date) > o.estimated_delivery_date
    end as is_late,
    coalesce(i.item_count, 0) as item_count,
    coalesce(i.seller_count, 0) as seller_count,
    coalesce(i.items_value, 0) as items_value,
    coalesce(i.freight_value, 0) as freight_value,
    coalesce(i.items_value, 0) + coalesce(i.freight_value, 0) as order_value,
    p.payment_total,
    p.main_payment_type,
    p.max_installments,
    r.review_score
from {{ ref('stg_orders') }} as o
left join {{ ref('stg_customers') }} as c
    on o.customer_id = c.customer_id
left join {{ ref('int_order_items_summed') }} as i
    on o.order_id = i.order_id
left join {{ ref('int_order_payments_summed') }} as p
    on o.order_id = p.order_id
left join {{ ref('int_order_reviews_latest') }} as r
    on o.order_id = r.order_id
