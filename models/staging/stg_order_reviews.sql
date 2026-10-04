select
    review_id,
    order_id,
    cast(review_score as integer) as review_score,
    review_comment_title as comment_title,
    review_comment_message as comment_message,
    cast(review_creation_date as date) as review_created_date,
    cast(review_answer_timestamp as timestamp) as review_answered_at
from {{ source('raw', 'olist_order_reviews_dataset') }}
