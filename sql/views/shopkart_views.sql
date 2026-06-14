-- ============================================================
-- ShopKart India - Reusable SQL Views
-- ============================================================

-- -------------------------------------------------------
-- View 1: Daily Sales Summary
-- -------------------------------------------------------
CREATE OR REPLACE VIEW vw_daily_sales AS
SELECT
    o.order_date,
    COUNT(DISTINCT o.order_id)      AS total_orders,
    COUNT(DISTINCT o.customer_id)   AS unique_customers,
    SUM(oi.quantity)                AS units_sold,
    ROUND(SUM(o.net_amount), 2)     AS revenue,
    ROUND(AVG(o.net_amount), 2)     AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY o.order_date;


-- -------------------------------------------------------
-- View 2: Product Performance Summary
-- -------------------------------------------------------
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.brand,
    p.selling_price,
    p.cost_price,
    ROUND(p.selling_price - p.cost_price, 2)        AS unit_margin,
    ROUND((p.selling_price - p.cost_price) * 100.0 /
           NULLIF(p.selling_price, 0), 2)            AS margin_pct,
    COALESCE(SUM(oi.quantity), 0)                    AS total_units_sold,
    COALESCE(ROUND(SUM(oi.line_total), 2), 0)        AS total_revenue,
    COALESCE(AVG(r.rating), 0)                       AS avg_rating,
    COUNT(DISTINCT ret.return_id)                    AS return_count
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status = 'Delivered'
LEFT JOIN reviews r ON p.product_id = r.product_id
LEFT JOIN returns ret ON p.product_id = ret.product_id AND ret.status = 'Approved'
GROUP BY p.product_id, p.product_name, p.category, p.sub_category,
         p.brand, p.selling_price, p.cost_price;


-- -------------------------------------------------------
-- View 3: Customer 360 View
-- -------------------------------------------------------
CREATE OR REPLACE VIEW vw_customer_360 AS
SELECT
    c.customer_id,
    c.full_name,
    c.city,
    c.state,
    c.gender,
    c.age,
    c.segment,
    c.registered_date,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    ROUND(SUM(o.net_amount), 2)         AS lifetime_value,
    ROUND(AVG(o.net_amount), 2)         AS avg_order_value,
    MIN(o.order_date)                   AS first_order_date,
    MAX(o.order_date)                   AS last_order_date,
    CURRENT_DATE - MAX(o.order_date)    AS days_since_last_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Delivered'
GROUP BY c.customer_id, c.full_name, c.city, c.state,
         c.gender, c.age, c.segment, c.registered_date;


-- -------------------------------------------------------
-- View 4: Category Monthly Revenue
-- -------------------------------------------------------
CREATE OR REPLACE VIEW vw_category_monthly_revenue AS
SELECT
    DATE_TRUNC('month', o.order_date)   AS month,
    p.category,
    COUNT(DISTINCT o.order_id)          AS orders,
    SUM(oi.quantity)                    AS units_sold,
    ROUND(SUM(oi.line_total), 2)        AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY 1, 2
ORDER BY 1, revenue DESC;
