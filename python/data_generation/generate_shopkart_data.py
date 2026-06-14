"""
ShopKart India - Synthetic Data Generator
Generates realistic e-commerce datasets with Indian locale
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta
import random
import os

fake = Faker('en_IN')
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = "../../data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Config ──────────────────────────────────────────────────────────────────
CITIES = {
    'Bangalore': 'Karnataka', 'Mumbai': 'Maharashtra', 'Delhi': 'Delhi',
    'Chennai': 'Tamil Nadu', 'Hyderabad': 'Telangana', 'Pune': 'Maharashtra',
    'Ahmedabad': 'Gujarat', 'Kolkata': 'West Bengal', 'Jaipur': 'Rajasthan',
    'Lucknow': 'Uttar Pradesh'
}

CATEGORIES = {
    'Electronics':    ['Mobile Phones', 'Laptops', 'Headphones', 'Tablets', 'Cameras'],
    'Fashion':        ['Men Clothing', 'Women Clothing', 'Footwear', 'Accessories'],
    'Home & Kitchen': ['Cookware', 'Furniture', 'Decor', 'Appliances'],
    'Books':          ['Fiction', 'Non-Fiction', 'Academic', 'Comics'],
    'Sports':         ['Fitness Equipment', 'Outdoor', 'Sportswear'],
    'Beauty':         ['Skincare', 'Haircare', 'Makeup', 'Fragrances'],
    'Groceries':      ['Staples', 'Snacks', 'Beverages', 'Organic'],
}

BRANDS = {
    'Electronics':    ['Samsung', 'Apple', 'OnePlus', 'Xiaomi', 'Boat', 'realme'],
    'Fashion':        ['H&M', 'Zara', 'FabIndia', 'Van Heusen', 'Bata', 'Puma'],
    'Home & Kitchen': ['Prestige', 'Pigeon', 'IKEA', 'Godrej', 'Philips'],
    'Books':          ['Penguin', 'Rupa', 'HarperCollins', 'Scholastic'],
    'Sports':         ['Nike', 'Adidas', 'Decathlon', 'Cosco', 'Nivia'],
    'Beauty':         ['Lakme', 'Maybelline', "L'Oreal", 'Biotique', 'WOW'],
    'Groceries':      ['Tata', 'Amul', 'Patanjali', 'ITC', 'HUL'],
}

PRICE_RANGE = {
    'Electronics':    (2000, 120000),
    'Fashion':        (299, 8000),
    'Home & Kitchen': (399, 35000),
    'Books':          (99, 1500),
    'Sports':         (299, 15000),
    'Beauty':         (149, 5000),
    'Groceries':      (49, 2000),
}

PAYMENT_METHODS = ['UPI', 'COD', 'Credit Card', 'Debit Card', 'Net Banking', 'Wallet']
PAYMENT_WEIGHTS  = [0.40, 0.25, 0.15, 0.10, 0.05, 0.05]

ORDER_STATUSES = ['Delivered', 'Returned', 'Cancelled', 'Pending']
ORDER_WEIGHTS  = [0.78, 0.10, 0.08, 0.04]

RETURN_REASONS = [
    'Defective product', 'Wrong item delivered', 'Size issue',
    'Better price elsewhere', 'Changed mind', 'Quality not as described'
]

# ─── Generators ──────────────────────────────────────────────────────────────

def gen_customers(n=1000):
    customers = []
    segments = ['New', 'Regular', 'Premium']
    seg_weights = [0.40, 0.45, 0.15]
    for i in range(1, n + 1):
        city, state = random.choice(list(CITIES.items()))
        customers.append({
            'customer_id':     f'CUST{i:05d}',
            'full_name':       fake.name(),
            'email':           fake.email(),
            'phone':           fake.phone_number()[:10],
            'city':            city,
            'state':           state,
            'pincode':         fake.postcode(),
            'gender':          random.choice(['Male', 'Female', 'Other']),
            'age':             random.randint(18, 65),
            'segment':         random.choices(segments, seg_weights)[0],
            'registered_date': fake.date_between(start_date='-3y', end_date='-6m'),
            'is_active':       random.choices([True, False], [0.90, 0.10])[0],
        })
    return pd.DataFrame(customers)


def gen_products(n=300):
    products = []
    for i in range(1, n + 1):
        cat = random.choice(list(CATEGORIES.keys()))
        sub = random.choice(CATEGORIES[cat])
        brand = random.choice(BRANDS[cat])
        lo, hi = PRICE_RANGE[cat]
        sell = round(random.uniform(lo, hi), -1)
        cost = round(sell * random.uniform(0.45, 0.72), 2)
        products.append({
            'product_id':    f'PROD{i:04d}',
            'product_name':  f'{brand} {sub} {fake.word().capitalize()} {random.randint(100,999)}',
            'category':      cat,
            'sub_category':  sub,
            'brand':         brand,
            'cost_price':    cost,
            'selling_price': sell,
            'discount_pct':  random.choice([0, 5, 10, 15, 20, 25, 30]),
            'stock_qty':     random.randint(0, 500),
            'rating':        round(random.uniform(3.0, 5.0), 1),
            'is_available':  random.choices([True, False], [0.92, 0.08])[0],
        })
    return pd.DataFrame(products)


def gen_orders(customers_df, products_df, n=5000):
    orders, order_items = [], []
    item_id = 1
    cust_ids = customers_df['customer_id'].tolist()
    prod_ids = products_df['product_id'].tolist()

    for i in range(1, n + 1):
        order_id = f'ORD{i:07d}'
        cust_id  = random.choice(cust_ids)
        order_dt = fake.date_between(start_date='-2y', end_date='today')
        status   = random.choices(ORDER_STATUSES, ORDER_WEIGHTS)[0]
        city, state = random.choice(list(CITIES.items()))

        n_items   = random.randint(1, 5)
        sel_prods = random.sample(prod_ids, min(n_items, len(prod_ids)))
        total = 0
        discount_total = 0

        for pid in sel_prods:
            prod = products_df[products_df['product_id'] == pid].iloc[0]
            qty  = random.randint(1, 4)
            disc = prod['discount_pct']
            unit = prod['selling_price']
            line = round(unit * qty * (1 - disc / 100), 2)
            disc_amt = round(unit * qty * disc / 100, 2)
            total += line
            discount_total += disc_amt
            order_items.append({
                'item_id':     item_id,
                'order_id':    order_id,
                'product_id':  pid,
                'quantity':    qty,
                'unit_price':  unit,
                'discount_pct': disc,
                'line_total':  line,
            })
            item_id += 1

        delivery_dt = order_dt + timedelta(days=random.randint(2, 10)) if status == 'Delivered' else None
        orders.append({
            'order_id':        order_id,
            'customer_id':     cust_id,
            'order_date':      order_dt,
            'delivery_date':   delivery_dt,
            'status':          status,
            'payment_method':  random.choices(PAYMENT_METHODS, PAYMENT_WEIGHTS)[0],
            'city':            city,
            'state':           state,
            'total_amount':    round(total + discount_total, 2),
            'discount_amount': round(discount_total, 2),
            'net_amount':      round(total, 2),
        })

    return pd.DataFrame(orders), pd.DataFrame(order_items)


def gen_returns(orders_df, order_items_df):
    returned = orders_df[orders_df['status'] == 'Returned']['order_id'].tolist()
    returns = []
    for oid in returned:
        items = order_items_df[order_items_df['order_id'] == oid]
        if items.empty:
            continue
        row = items.sample(1).iloc[0]
        ret_date = pd.to_datetime(
            orders_df[orders_df['order_id'] == oid]['order_date'].values[0]
        ) + timedelta(days=random.randint(1, 15))
        returns.append({
            'order_id':      oid,
            'product_id':    row['product_id'],
            'return_date':   ret_date.date(),
            'reason':        random.choice(RETURN_REASONS),
            'refund_amount': row['line_total'],
            'status':        random.choices(['Approved', 'Rejected', 'Pending'], [0.75, 0.15, 0.10])[0],
        })
    df = pd.DataFrame(returns)
    df.insert(0, 'return_id', range(1, len(df) + 1))
    return df


def gen_reviews(orders_df, order_items_df, customers_df):
    delivered = orders_df[orders_df['status'] == 'Delivered'].sample(frac=0.60)
    reviews = []
    for _, row in delivered.iterrows():
        items = order_items_df[order_items_df['order_id'] == row['order_id']]
        if items.empty:
            continue
        prod = items.sample(1).iloc[0]
        reviews.append({
            'product_id':   prod['product_id'],
            'customer_id':  row['customer_id'],
            'order_id':     row['order_id'],
            'rating':       random.choices([1, 2, 3, 4, 5], [0.03, 0.05, 0.12, 0.35, 0.45])[0],
            'review_text':  fake.sentence(nb_words=12),
            'review_date':  row['delivery_date'],
        })
    df = pd.DataFrame(reviews)
    df.insert(0, 'review_id', range(1, len(df) + 1))
    return df


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Generating ShopKart India datasets...")

    print("  → Customers...")
    customers_df = gen_customers(1000)
    customers_df.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)

    print("  → Products...")
    products_df = gen_products(300)
    products_df.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)

    print("  → Orders & Order Items...")
    orders_df, order_items_df = gen_orders(customers_df, products_df, 5000)
    orders_df.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)
    order_items_df.to_csv(f"{OUTPUT_DIR}/order_items.csv", index=False)

    print("  → Returns...")
    returns_df = gen_returns(orders_df, order_items_df)
    returns_df.to_csv(f"{OUTPUT_DIR}/returns.csv", index=False)

    print("  → Reviews...")
    reviews_df = gen_reviews(orders_df, order_items_df, customers_df)
    reviews_df.to_csv(f"{OUTPUT_DIR}/reviews.csv", index=False)

    print("\n✅ All datasets generated successfully!")
    print(f"   Customers : {len(customers_df):,}")
    print(f"   Products  : {len(products_df):,}")
    print(f"   Orders    : {len(orders_df):,}")
    print(f"   Items     : {len(order_items_df):,}")
    print(f"   Returns   : {len(returns_df):,}")
    print(f"   Reviews   : {len(reviews_df):,}")
    print(f"\n   Saved to: {OUTPUT_DIR}/")
