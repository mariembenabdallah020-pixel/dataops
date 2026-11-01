SELECT *
FROM {{ ref('int_orders_checked') }}
WHERE reject_reason IS NOT NULL