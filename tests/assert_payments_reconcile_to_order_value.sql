-- Reconciliation check between two independent sources of the same number:
-- what customers paid (payments file) against items plus freight (order items file).
-- Returns the orders where the two differ by more than 1.00.
-- Set to warn: differences are expected for a small share of orders
-- (for example vouchers and instalment interest) and should be reviewed, not block a build.
{{ config(severity='warn') }}

select
    order_id,
    order_value,
    payment_total,
    payment_total - order_value as difference
from {{ ref('int_orders_enriched') }}
where item_count > 0
  and payment_total is not null
  and abs(payment_total - order_value) > 1.00
