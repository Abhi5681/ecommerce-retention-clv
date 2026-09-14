-- Monthly Cohort Retention Matrix (PostgreSQL Compatible)
WITH customer_orders AS (
    SELECT
        customer_id,
        invoice_id,
        CAST(invoice_date AS TIMESTAMP) AS order_timestamp,
        DATE_TRUNC('month', CAST(invoice_date AS TIMESTAMP))::DATE AS order_month,
        quantity * unit_price AS order_amount
    FROM ecommerce_transactions
    WHERE quantity > 0
),

cohort_assignments AS (
    SELECT
        customer_id,
        MIN(order_month) AS cohort_month
    FROM customer_orders
    GROUP BY customer_id
),

cohort_monthly_activity AS (
    SELECT
        co.customer_id,
        ca.cohort_month,
        co.order_month,
        -- Calculate index representing months elapsed since first purchase
        (EXTRACT(YEAR FROM co.order_month) - EXTRACT(YEAR FROM ca.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM co.order_month) - EXTRACT(MONTH FROM ca.cohort_month)) AS cohort_index
    FROM customer_orders co
    JOIN cohort_assignments ca
        ON co.customer_id = ca.customer_id
    GROUP BY 
        co.customer_id, 
        ca.cohort_month, 
        co.order_month,
        cohort_index
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_customers
    FROM cohort_assignments
    GROUP BY cohort_month
),

cohort_retention_counts AS (
    SELECT
        cma.cohort_month,
        cma.cohort_index,
        COUNT(DISTINCT cma.customer_id) AS active_customers
    FROM cohort_monthly_activity cma
    GROUP BY cma.cohort_month, cma.cohort_index
)

SELECT
    cs.cohort_month,
    cs.total_customers AS cohort_base_size,
    crc.cohort_index AS month_number,
    crc.active_customers,
    ROUND((crc.active_customers::DECIMAL / cs.total_customers) * 100.0, 2) AS retention_rate_pct
FROM cohort_retention_counts crc
JOIN cohort_sizes cs 
    ON crc.cohort_month = cs.cohort_month
ORDER BY 
    cs.cohort_month ASC, 
    crc.cohort_index ASC;
