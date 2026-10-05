-- One row per order: its most recent review. A few orders were reviewed more than once.
select
    order_id,
    review_id,
    review_score,
    review_created_date,
    review_answered_at
from {{ ref('stg_order_reviews') }}
qualify row_number() over (
    partition by order_id
    order by review_answered_at desc, review_id
) = 1
