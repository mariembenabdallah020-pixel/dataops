WITH counts AS (
    SELECT
        (SELECT COUNT(*) FROM {{ ref('orders_clean') }}) AS clean_count,
        (SELECT COUNT(*) FROM {{ ref('orders_rejected') }}) AS rejected_count
)

SELECT *
FROM counts
WHERE
    rejected_count * 1.0
    / NULLIF(clean_count + rejected_count, 0) >= 0.20