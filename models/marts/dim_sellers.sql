-- One row per seller, with their sales totals and whether they came through the marketing funnel.
select
    s.seller_id,
    s.city as seller_city,
    s.state as seller_state,
    d.lead_id is not null as came_from_funnel,
    d.business_segment,
    d.lead_type,
    ss.first_sale_at,
    ss.last_sale_at,
    coalesce(ss.order_count, 0) as order_count,
    coalesce(ss.revenue, 0) as revenue
from {{ ref('stg_sellers') }} as s
left join {{ ref('stg_closed_deals') }} as d
    on s.seller_id = d.seller_id
left join {{ ref('int_seller_sales') }} as ss
    on s.seller_id = ss.seller_id
