# ShopKart India — Power BI Dashboard Guide

## Data Model (Star Schema)

```
               [dim_customers]
                      |
[dim_products] — [fact_order_items] — [fact_orders] — [dim_date]
                      |
               [fact_returns]
```

---

## DAX Measures

### Revenue & Orders
```dax
Total Revenue =
CALCULATE(
    SUMX(fact_orders, fact_orders[net_amount]),
    fact_orders[status] = "Delivered"
)

Total Orders =
CALCULATE(
    COUNTROWS(fact_orders),
    fact_orders[status] = "Delivered"
)

Avg Order Value =
DIVIDE([Total Revenue], [Total Orders], 0)

Cancelled Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(fact_orders), fact_orders[status] = "Cancelled"),
    COUNTROWS(fact_orders),
    0
) * 100
```

### Customer Metrics
```dax
Unique Customers =
CALCULATE(
    DISTINCTCOUNT(fact_orders[customer_id]),
    fact_orders[status] = "Delivered"
)

Avg Customer LTV =
DIVIDE([Total Revenue], [Unique Customers], 0)

New vs Returning =
VAR _customers = VALUES(fact_orders[customer_id])
VAR _first_orders = CALCULATETABLE(
    ADDCOLUMNS(_customers, "FirstOrder", CALCULATE(MIN(fact_orders[order_date]))),
    ALL(dim_date)
)
RETURN COUNTROWS(FILTER(_first_orders, [FirstOrder] >= MIN(dim_date[Date])))
```

### Product Metrics
```dax
Gross Margin % =
DIVIDE(
    SUMX(fact_order_items,
        fact_order_items[line_total] -
        RELATED(dim_products[cost_price]) * fact_order_items[quantity]
    ),
    SUM(fact_order_items[line_total]),
    0
) * 100

Units Sold =
SUM(fact_order_items[quantity])

Return Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(fact_returns), fact_returns[status] = "Approved"),
    [Total Orders],
    0
) * 100
```

### Time Intelligence
```dax
Revenue MoM Growth % =
VAR _current = [Total Revenue]
VAR _prev = CALCULATE([Total Revenue], PREVIOUSMONTH(dim_date[Date]))
RETURN DIVIDE(_current - _prev, _prev, 0) * 100

Revenue YTD =
CALCULATE([Total Revenue], DATESYTD(dim_date[Date]))

Revenue LY =
CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[Date]))
```

---

## Dashboard Pages

### Page 1 — Executive Summary
- KPI cards: Total Revenue, Orders, AOV, Return Rate %
- Line chart: Monthly Revenue Trend (with MoM growth %)
- Bar chart: Revenue by Category
- Map: City-wise Revenue (filled map with India states)
- Slicer: Date range, Category, City

### Page 2 — Product Analytics
- Table: Top 20 products by revenue (with margin %, return rate)
- Treemap: Category → Sub-category → Product by revenue
- Scatter: Selling price vs Units sold (bubble = margin)
- Bar: Return Rate by Category
- Slicer: Brand, Category

### Page 3 — Customer Analytics
- KPI: Unique Customers, New Customers, Avg LTV
- Bar: Customer Segment breakdown (New/Regular/Premium)
- Line: Customer cohort retention
- Donut: Payment method split
- Table: Top customers by LTV

### Page 4 — Operations
- Bar: Orders by Status (Delivered/Returned/Cancelled/Pending)
- Line: Daily Orders trend
- Gauge: Delivery SLA (avg delivery days)
- Bar: City delivery performance
- Matrix: Category × Month revenue heatmap

---

## Power Query Steps (ETL)

1. Load `orders_clean.csv`, `order_items_clean.csv`, `products_clean.csv`,
   `customers_clean.csv`, `returns_clean.csv`
2. Create `dim_date` table:
   ```powerquery
   = List.Dates(#date(2022,1,1), 730, #duration(1,0,0,0))
   ```
3. Add columns: Year, Month, Quarter, Week, Day Name
4. Establish relationships (star schema per diagram above)
5. Mark `dim_date` as Date Table

---

## Recommended Colour Theme

| Element | Colour |
|---------|--------|
| Primary | #2563EB (Blue) |
| Positive | #16A34A (Green) |
| Negative | #DC2626 (Red) |
| Neutral  | #6B7280 (Gray) |
| Background | #F8FAFC |
