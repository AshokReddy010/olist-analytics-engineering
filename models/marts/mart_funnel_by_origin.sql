-- Funnel conversion by lead origin: how many leads each channel brought, and how far they got.
select
    origin,
    count(*) as leads,
    count(*) filter (where is_closed) as closed_deals,
    count(*) filter (where is_activated) as activated_sellers,
    round(count(*) filter (where is_closed) * 1.0 / count(*), 4) as lead_to_close_rate,
    round(
        count(*) filter (where is_activated) * 1.0
        / nullif(count(*) filter (where is_closed), 0),
        4
    ) as close_to_activation_rate,
    round(median(days_to_close) filter (where is_closed), 1) as median_days_to_close,
    coalesce(sum(seller_revenue), 0) as revenue_from_channel
from {{ ref('fct_lead_funnel') }}
group by origin
