-- One row per order: total paid, and the payment type that covered the largest amount.
select
    order_id,
    count(*) as payment_count,
    sum(payment_value) as payment_total,
    max(installments) as max_installments,
    arg_max(payment_type, payment_value) as main_payment_type
from {{ ref('stg_order_payments') }}
group by order_id
