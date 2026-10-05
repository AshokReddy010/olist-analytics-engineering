-- Products with an English category name.
-- Two categories have no translation and some products have no category at all,
-- so the name falls back to the Portuguese value, then to 'unknown'. No rows are dropped.
select
    p.product_id,
    coalesce(c.category_name, p.category_name_pt, 'unknown') as category_name,
    p.category_name_pt,
    c.category_name is null and p.category_name_pt is not null as is_category_untranslated,
    p.photo_count,
    p.weight_g,
    p.length_cm,
    p.height_cm,
    p.width_cm
from {{ ref('stg_products') }} as p
left join {{ ref('stg_product_categories') }} as c
    on p.category_name_pt = c.category_name_pt
