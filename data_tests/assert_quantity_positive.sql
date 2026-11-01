SELECT *
FROM {{ ref('orders_clean') }}
WHERE quantity <= 0