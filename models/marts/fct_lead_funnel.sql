-- One row per marketing lead, followed through the funnel:
-- lead -> closed deal (signed as a seller) -> activated (made a first sale).
select
    l.lead_id,
    l.first_contact_date,
    cast(date_trunc('month', l.first_contact_date) as date) as contact_month,
    coalesce(l.origin, 'unknown') as origin,
    l.landing_page_id,
    d.lead_id is not null as is_closed,
    d.won_at,
    date_diff('day', l.first_contact_date, cast(d.won_at as date)) as days_to_close,
    d.seller_id,
    d.business_segment,
    d.lead_type,
    d.lead_behaviour_profile,
    d.business_type,
    d.declared_monthly_revenue,
    ss.seller_id is not null as is_activated,
    ss.first_sale_at,
    date_diff('day', cast(d.won_at as date), cast(ss.first_sale_at as date)) as days_to_first_sale,
    coalesce(ss.order_count, 0) as seller_order_count,
    coalesce(ss.revenue, 0) as seller_revenue
from {{ ref('stg_leads') }} as l
left join {{ ref('stg_closed_deals') }} as d
    on l.lead_id = d.lead_id
left join {{ ref('int_seller_sales') }} as ss
    on d.seller_id = ss.seller_id
