# 🛒 ShopKart India — Retail & E-Commerce Analytics

## 🚀 Live Interactive Dashboard

**[View Dashboard →](https://malleshwaric.github.io/shopkart-india-analytics/dashboard.html)**

Fully interactive — charts, tabs, KPI cards. No login required, opens in any browser.

---


> E-commerce analytics for a multi-category Indian retail platform — revenue trends, category margins, customer segmentation, and return rate analysis.

---

## 📌 Project Overview

ShopKart India is a fictional e-commerce platform operating across 10+ Indian cities. This project covers the full analytics pipeline — from raw data generation to dashboard-ready insights.

**Business Questions Answered:**
- Which product categories drive the most revenue?
- What is the month-over-month sales trend?
- Which cities and customer segments are most valuable?
- What is the return rate by category?
- How do discounts impact profit margins?

---

## 🗂️ Project Structure

```
shopkart-india-analytics/
│
├── data/
│   ├── raw/                  # Generated raw CSV datasets
│   └── processed/            # Cleaned, analysis-ready data
│
├── sql/
│   ├── schema/               # Table creation scripts
│   ├── queries/              # Business insight queries
│   └── views/                # Reusable SQL views
│
├── python/
│   ├── data_generation/      # Synthetic dataset scripts
│   ├── cleaning/             # Data cleaning pipelines
│   └── analysis/             # EDA and summary stats
│
├── powerbi/                  # Power BI layout notes & DAX measures
├── docs/                     # Project documentation
└── README.md
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python (pandas, numpy, Faker) | Data generation & cleaning |
| PostgreSQL / MySQL | Data storage & querying |
| SQL (CTEs, Window Functions) | Business analysis |
| Power BI | Dashboard & visualisation |
| GitHub | Version control |

---

## 📊 Key KPIs Tracked

- **Total Revenue** — Monthly/Quarterly/Annual
- **Average Order Value (AOV)**
- **Customer Lifetime Value (CLV)**
- **Return Rate %**
- **Gross Margin %**
- **City-wise Revenue Share**
- **Category Performance Index**

---

## 🚀 How to Run

### 1. Generate Data
```bash
cd python/data_generation
pip install pandas numpy faker
python generate_shopkart_data.py
```

### 2. Load into Database
```bash
# Run schema first
psql -U your_user -d your_db -f sql/schema/create_tables.sql

# Load CSVs using your preferred method (pgAdmin, DBeaver, etc.)
```

### 3. Run Queries
```bash
psql -U your_user -d your_db -f sql/queries/revenue_analysis.sql
```

---

## About

Built by Malleshwari C · [GitHub](https://github.com/malleshwaric)

---

## 📁 Dataset Note

Sample data generated with Python using realistic Indian market distributions.
