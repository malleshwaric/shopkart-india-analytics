-- ============================================================
-- ShopKart India - Database Schema
-- ============================================================

-- Customers Table
CREATE TABLE customers (
    customer_id     VARCHAR(10) PRIMARY KEY,
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    phone           VARCHAR(15),
    city            VARCHAR(50),
    state           VARCHAR(50),
    pincode         VARCHAR(6),
    gender          VARCHAR(10),
    age             INT,
    segment         VARCHAR(20),  -- 'New', 'Regular', 'Premium'
    registered_date DATE,
    is_active       BOOLEAN DEFAULT TRUE
);

-- Products Table
CREATE TABLE products (
    product_id      VARCHAR(10) PRIMARY KEY,
    product_name    VARCHAR(200) NOT NULL,
    category        VARCHAR(50),
    sub_category    VARCHAR(50),
    brand           VARCHAR(100),
    cost_price      NUMERIC(10,2),
    selling_price   NUMERIC(10,2),
    discount_pct    NUMERIC(5,2) DEFAULT 0,
    stock_qty       INT,
    rating          NUMERIC(3,1),
    is_available    BOOLEAN DEFAULT TRUE
);

-- Orders Table
CREATE TABLE orders (
    order_id        VARCHAR(15) PRIMARY KEY,
    customer_id     VARCHAR(10) REFERENCES customers(customer_id),
    order_date      DATE NOT NULL,
    delivery_date   DATE,
    status          VARCHAR(20),  -- 'Delivered','Returned','Cancelled','Pending'
    payment_method  VARCHAR(20),  -- 'UPI','COD','Card','Netbanking'
    city            VARCHAR(50),
    state           VARCHAR(50),
    total_amount    NUMERIC(12,2),
    discount_amount NUMERIC(10,2),
    net_amount      NUMERIC(12,2)
);

-- Order Items Table
CREATE TABLE order_items (
    item_id         SERIAL PRIMARY KEY,
    order_id        VARCHAR(15) REFERENCES orders(order_id),
    product_id      VARCHAR(10) REFERENCES products(product_id),
    quantity        INT NOT NULL,
    unit_price      NUMERIC(10,2),
    discount_pct    NUMERIC(5,2),
    line_total      NUMERIC(12,2)
);

-- Returns Table
CREATE TABLE returns (
    return_id       SERIAL PRIMARY KEY,
    order_id        VARCHAR(15) REFERENCES orders(order_id),
    product_id      VARCHAR(10) REFERENCES products(product_id),
    return_date     DATE,
    reason          VARCHAR(100),
    refund_amount   NUMERIC(10,2),
    status          VARCHAR(20)  -- 'Approved','Rejected','Pending'
);

-- Reviews Table
CREATE TABLE reviews (
    review_id       SERIAL PRIMARY KEY,
    product_id      VARCHAR(10) REFERENCES products(product_id),
    customer_id     VARCHAR(10) REFERENCES customers(customer_id),
    order_id        VARCHAR(15) REFERENCES orders(order_id),
    rating          INT CHECK (rating BETWEEN 1 AND 5),
    review_text     TEXT,
    review_date     DATE
);

-- Indexes for performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_returns_order ON returns(order_id);
