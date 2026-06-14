"""
ShopKart India - Data Cleaning Pipeline
Cleans raw CSVs and outputs analysis-ready data
"""

import pandas as pd
import numpy as np
import os

RAW_DIR = "../../data/raw"
PROCESSED_DIR = "../../data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning customers...")
    df = df.drop_duplicates(subset='customer_id')
    df = df.dropna(subset=['customer_id', 'email'])
    df['email'] = df['email'].str.lower().str.strip()
    df['full_name'] = df['full_name'].str.strip().str.title()
    df['phone'] = df['phone'].astype(str).str.replace(r'\D', '', regex=True).str[:10]
    df['age'] = df['age'].clip(lower=18, upper=80)
    df['registered_date'] = pd.to_datetime(df['registered_date'])
    df['is_active'] = df['is_active'].astype(bool)
    print(f"  → {len(df):,} rows after cleaning")
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning products...")
    df = df.drop_duplicates(subset='product_id')
    df = df.dropna(subset=['product_id', 'selling_price', 'cost_price'])
    df['selling_price'] = df['selling_price'].clip(lower=0)
    df['cost_price'] = df['cost_price'].clip(lower=0)
    # Flag products with negative margin
    df['has_negative_margin'] = df['selling_price'] < df['cost_price']
    df['discount_pct'] = df['discount_pct'].fillna(0).clip(0, 70)
    df['rating'] = df['rating'].clip(1.0, 5.0)
    df['stock_qty'] = df['stock_qty'].clip(lower=0).fillna(0).astype(int)
    print(f"  → {len(df):,} rows after cleaning | Negative margin: {df['has_negative_margin'].sum()}")
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning orders...")
    df = df.drop_duplicates(subset='order_id')
    df = df.dropna(subset=['order_id', 'customer_id', 'order_date'])
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['delivery_date'] = pd.to_datetime(df['delivery_date'])
    df['net_amount'] = df['net_amount'].clip(lower=0)
    df['discount_amount'] = df['discount_amount'].clip(lower=0)
    # Derived columns
    df['delivery_days'] = (df['delivery_date'] - df['order_date']).dt.days
    df['order_month'] = df['order_date'].dt.to_period('M').astype(str)
    df['order_quarter'] = df['order_date'].dt.to_period('Q').astype(str)
    df['order_year'] = df['order_date'].dt.year
    # Outlier flag for very large orders
    q99 = df['net_amount'].quantile(0.99)
    df['is_outlier_order'] = df['net_amount'] > q99
    print(f"  → {len(df):,} rows | Outliers: {df['is_outlier_order'].sum()}")
    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning order items...")
    df = df.drop_duplicates(subset='item_id')
    df = df.dropna(subset=['order_id', 'product_id'])
    df['quantity'] = df['quantity'].clip(lower=1)
    df['unit_price'] = df['unit_price'].clip(lower=0)
    df['line_total'] = df['line_total'].clip(lower=0)
    print(f"  → {len(df):,} rows after cleaning")
    return df


def clean_returns(df: pd.DataFrame) -> pd.DataFrame:
    print("Cleaning returns...")
    df = df.drop_duplicates(subset='return_id')
    df = df.dropna(subset=['order_id', 'product_id'])
    df['return_date'] = pd.to_datetime(df['return_date'])
    df['refund_amount'] = df['refund_amount'].clip(lower=0)
    print(f"  → {len(df):,} rows after cleaning")
    return df


def generate_summary(orders_df, order_items_df, customers_df):
    print("\nGenerating summary report...")
    delivered = orders_df[orders_df['status'] == 'Delivered']
    summary = {
        'total_orders': len(orders_df),
        'delivered_orders': len(delivered),
        'total_revenue': delivered['net_amount'].sum().round(2),
        'avg_order_value': delivered['net_amount'].mean().round(2),
        'total_customers': len(customers_df),
        'active_customers': customers_df['is_active'].sum(),
        'total_items_sold': order_items_df[
            order_items_df['order_id'].isin(delivered['order_id'])
        ]['quantity'].sum(),
    }
    return pd.DataFrame([summary])


if __name__ == '__main__':
    print("=" * 50)
    print("ShopKart India — Data Cleaning Pipeline")
    print("=" * 50)

    customers = clean_customers(pd.read_csv(f"{RAW_DIR}/customers.csv"))
    products  = clean_products(pd.read_csv(f"{RAW_DIR}/products.csv"))
    orders    = clean_orders(pd.read_csv(f"{RAW_DIR}/orders.csv"))
    items     = clean_order_items(pd.read_csv(f"{RAW_DIR}/order_items.csv"))
    returns   = clean_returns(pd.read_csv(f"{RAW_DIR}/returns.csv"))

    customers.to_csv(f"{PROCESSED_DIR}/customers_clean.csv", index=False)
    products.to_csv(f"{PROCESSED_DIR}/products_clean.csv", index=False)
    orders.to_csv(f"{PROCESSED_DIR}/orders_clean.csv", index=False)
    items.to_csv(f"{PROCESSED_DIR}/order_items_clean.csv", index=False)
    returns.to_csv(f"{PROCESSED_DIR}/returns_clean.csv", index=False)

    summary = generate_summary(orders, items, customers)
    summary.to_csv(f"{PROCESSED_DIR}/summary_stats.csv", index=False)

    print("\n✅ Cleaning complete! Files saved to data/processed/")
    print(summary.T.to_string(header=False))
