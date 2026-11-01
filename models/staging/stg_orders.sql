
SELECT
    order_id,
    TRY_CAST(order_date AS DATE) AS order_date,
    customer_id,
   CASE UPPER(TRIM(country))
    WHEN 'FRANCE' THEN 'France'
    WHEN 'GERMANY' THEN 'Germany'
    WHEN 'ITALY' THEN 'Italy'
    WHEN 'MOROCCO' THEN 'Morocco'
    WHEN 'TUNISIA' THEN 'Tunisia'
    ELSE TRIM(country)
END AS country,
    product,
    TRY_CAST(quantity AS INTEGER) AS quantity,
    TRY_CAST(unit_price AS DOUBLE) AS unit_price,
    _row_number,
    _source_file,
    _loaded_at
FROM {{ source('raw', 'orders') }}
