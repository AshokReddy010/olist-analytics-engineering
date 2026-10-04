select
    mql_id as lead_id,
    cast(first_contact_date as date) as first_contact_date,
    landing_page_id,
    nullif(origin, '') as origin
from {{ source('raw', 'olist_marketing_qualified_leads_dataset') }}
