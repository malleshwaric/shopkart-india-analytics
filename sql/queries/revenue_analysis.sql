-- ============================================================
-- ShopKart India - Revenue Analysis Queries
-- ============================================================

-- -------------------------------------------------------
-- 1. Monthly Revenue Trend
-- -------------------------------------------------------
SELECT
    DATE_TRUNC('month', order_date)     AS month,
    COUNT(DISTINCT order_id)            AS total_orders,
    COUNT(DISTINCT customer_id)         AS unique_customers,
    ROUND(SUM(net_amount), 2)           AS total_revenue,
    ROUND(AVG(net_amount), 2)           AS avg_order_value
FROM orders
WHERE status = 'Delivered'
GROUP BY 1
ORDER BY 1;


-- -------------------------------------------------------
-- 2. Category-wise Revenue Breakdown
-- -------------------------------------------------------
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id)             AS orders_count,
    SUM(oi.quantity)                        AS units_sold,
    ROUND(SUM(oi.line_total), 2)            AS revenue,
    ROUND(SUM(oi.line_total) * 100.0 /
          SUM(SUM(oi.line_total)) OVER (), 2) AS revenue_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY revenue DESC;


-- -------------------------------------------------------
-- 3. Top 10 Products by Revenue
-- -------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity)            AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(AVG(p.selling_price - p.cost_price), 2) AS avg_margin
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY 1, 2, 3
ORDER BY total_revenue DESC
LIMIT 10;


-- -------------------------------------------------------
-- 4. City-wise Revenue Performance
-- -------------------------------------------------------
SELECT
    o.city,
    o.state,
    COUNT(DISTINCT o.order_id)      AS total_orders,
    COUNT(DISTINCT o.customer_id)   AS unique_customers,
    ROUND(SUM(o.net_amount), 2)     AS total_revenue,
    ROUND(AVG(o.net_amount), 2)     AS avg_order_value
FROM orders o
WHERE o.status = 'Delivered'
GROUP BY o.city, o.state
ORDER BY total_revenue DESC
LIMIT 15;


-- -------------------------------------------------------
-- 5. Customer Segment Analysis
-- -------------------------------------------------------
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id)       AS customer_count,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    ROUND(SUM(o.net_amount), 2)         AS total_revenue,
    ROUND(AVG(o.net_amount), 2)         AS avg_order_value,
    ROUND(SUM(o.net_amount) /
          COUNT(DISTINCT c.customer_id), 2) AS clv_estimate
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Delivered'
GROUP BY c.segment
ORDER BY total_revenue DESC;


-- -------------------------------------------------------
-- 6. Return Rate by Category
-- -------------------------------------------------------
WITH category_orders AS (
    SELECT
        p.category,
        COUNT(DISTINCT oi.order_id) AS total_orders
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category
),
category_returns AS (
    SELECT
        p.category,
        COUNT(DISTINCT r.order_id) AS returned_orders
    FROM returns r
    JOIN products p ON r.product_id = p.product_id
    WHERE r.status = 'Approved'
    GROUP BY p.category
)
SELECT
    co.category,
    co.total_orders,
    COALESCE(cr.returned_orders, 0)     AS returned_orders,
    ROUND(COALESCE(cr.returned_orders, 0) * 100.0 / co.total_orders, 2) AS return_rate_pct
FROM category_orders co
LEFT JOIN category_returns cr ON co.category = cr.category
ORDER BY return_rate_pct DESC;


-- -------------------------------------------------------
-- 7. Payment Method Distribution
-- -------------------------------------------------------
SELECT
    payment_method,
    COUNT(*)                        AS orders_count,
    ROUND(SUM(net_amount), 2)       AS total_revenue,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_orders
FROM orders
WHERE status = 'Delivered'
GROUP BY payment_method
ORDER BY orders_count DESC;


-- -------------------------------------------------------
-- 8. MoM Revenue Growth (Window Function)
-- -------------------------------------------------------
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        ROUND(SUM(net_amount), 2)       AS revenue
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY 1
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month)  AS prev_month_revenue,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 /
           NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) AS mom_growth_pct
FROM monthly_revenue
ORDER BY month;


-- -------------------------------------------------------
-- 9. Customer Cohort Retention (First Purchase Month)
-- -------------------------------------------------------
WITH first_order AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
),
customer_activity AS (
    SELECT
        o.customer_id,
        fo.cohort_month,
        DATE_TRUNC('month', o.order_date) AS activity_month,
        EXTRACT(MONTH FROM AGE(DATE_TRUNC('month', o.order_date), fo.cohort_month)) AS months_since_first
    FROM orders o
    JOIN first_order fo ON o.customer_id = fo.customer_id
    WHERE o.status = 'Delivered'
)
SELECT
    cohort_month,
    months_since_first,
    COUNT(DISTINCT customer_id) AS active_customers
FROM customer_activity
GROUP BY 1, 2
ORDER BY 1, 2;


-- -------------------------------------------------------
-- 10. Discount Impact on Margin
-- -------------------------------------------------------
SELECT
    CASE
        WHEN oi.discount_pct = 0        THEN 'No Discount'
        WHEN oi.discount_pct <= 10      THEN '1-10%'
        WHEN oi.discount_pct <= 20      THEN '11-20%'
        WHEN oi.discount_pct <= 30      THEN '21-30%'
        ELSE '30%+'
    END AS discount_bucket,
    COUNT(DISTINCT oi.order_id)             AS orders,
    ROUND(SUM(oi.line_total), 2)            AS revenue,
    ROUND(SUM(oi.line_total - p.cost_price * oi.quantity), 2) AS gross_profit,
    ROUND(SUM(oi.line_total - p.cost_price * oi.quantity) * 100.0 /
          NULLIF(SUM(oi.line_total), 0), 2) AS margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY 1
ORDER BY margin_pct DESC;
