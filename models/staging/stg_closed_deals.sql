select
    mql_id as lead_id,
    seller_id,
    sdr_id as sales_dev_rep_id,
    sr_id as sales_rep_id,
    cast(won_date as timestamp) as won_at,
    business_segment,
    lead_type,
    lead_behaviour_profile as lead_behaviour_profile,
    cast(has_company as boolean) as has_company,
    cast(has_gtin as boolean) as has_gtin,
    cast(average_stock as varchar) as average_stock,
    business_type,
    cast(declared_product_catalog_size as integer) as declared_catalog_size,
    cast(declared_monthly_revenue as decimal(14, 2)) as declared_monthly_revenue
from {{ source('raw', 'olist_closed_deals_dataset') }}
