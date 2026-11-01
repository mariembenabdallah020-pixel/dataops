WITH base AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY _row_number
        ) AS duplicate_rank
    FROM {{ ref('stg_orders') }}
),

checked AS (
    SELECT
        *,
        CASE
            WHEN customer_id IS NULL OR TRIM(customer_id) = ''
                THEN 'missing_customer_id'

            WHEN order_date IS NULL
                THEN 'invalid_date'

            WHEN quantity IS NULL OR quantity <= 0
                THEN 'invalid_quantity'

            WHEN unit_price IS NULL
                 OR unit_price < 0.01
                 OR unit_price > 1000
                THEN 'invalid_unit_price'

            WHEN duplicate_rank > 1
                THEN 'duplicate_order_id'

            WHEN country NOT IN (
                'France', 'Germany', 'Italy', 'Morocco', 'Tunisia'
            )
                THEN 'unknown_country'

            ELSE NULL
        END AS reject_reason
    FROM base
)

SELECT *
FROM checked