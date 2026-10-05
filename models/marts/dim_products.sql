-- One row per product with an English category name.
select * from {{ ref('int_products_translated') }}
