SELECT
    country,
    ROUND(SUM(quantity * unit_price), 2) AS revenue
FROM {{ ref('orders_clean') }}
GROUP BY country
ORDER BY country