"""
RETAIL ANALYTICS PLATFORM - Phase 2-5: Complete Analytics Engine
Works with Pandas (no Spark installation needed!)

Simply run: python analytics_engine.py

Performs:
- Sales trend analysis
- Customer segmentation (RFM)
- Inventory analysis
- Product recommendations
- Customer lifetime value
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

print("\n" + "="*70)
print("RETAIL ANALYTICS ENGINE - COMPLETE ANALYSIS")
print("="*70 + "\n")

# Create output directory
os.makedirs('./output', exist_ok=True)

# ============================================================================
# LOAD ALL DATA
# ============================================================================
print("Loading data files...")

try:
    df_sales = pd.read_csv('./data/sales.csv')
    df_products = pd.read_csv('./data/products.csv')
    df_customers = pd.read_csv('./data/customers.csv')
    df_stores = pd.read_csv('./data/stores.csv')
    df_inventory = pd.read_csv('./data/inventory.csv')
    
    print(f"✓ Loaded {len(df_sales):,} sales records")
    print(f"✓ Loaded {len(df_products):,} products")
    print(f"✓ Loaded {len(df_customers):,} customers")
    print(f"✓ Loaded {len(df_stores)} stores")
    print(f"✓ Loaded {len(df_inventory):,} inventory records\n")
    
except FileNotFoundError as e:
    print(f"✗ Error: {e}")
    print("Please run data_generation.py first!\n")
    exit(1)

# ============================================================================
# STEP 1: DATA ENRICHMENT
# ============================================================================
print("Step 1: Enriching sales data...")

# Parse date
df_sales['date'] = pd.to_datetime(df_sales['date'])
df_sales['year'] = df_sales['date'].dt.year
df_sales['month'] = df_sales['date'].dt.month
df_sales['day'] = df_sales['date'].dt.day
df_sales['day_of_week'] = df_sales['date'].dt.dayofweek
df_sales['week'] = df_sales['date'].dt.isocalendar().week

# Merge with products to get cost
df_sales = df_sales.merge(df_products[['product_id', 'cost', 'category']], 
                           on='product_id', how='left')

# Calculate profit
df_sales['cost_total'] = df_sales['quantity'] * df_sales['cost']
df_sales['profit'] = df_sales['total_amount'] - df_sales['cost_total']
df_sales['profit_margin'] = np.round((df_sales['profit'] / df_sales['total_amount']) * 100, 2)

print("✓ Data enriched with dates, categories, profit margins\n")

# ============================================================================
# STEP 2: SALES TREND ANALYSIS
# ============================================================================
print("Step 2: Analyzing Sales Trends...")

# Daily sales
daily_sales = df_sales.groupby(df_sales['date'].dt.date).agg({
    'total_amount': 'sum',
    'quantity': 'sum',
    'transaction_id': 'count',
    'profit_margin': 'mean'
}).round(2)
daily_sales.columns = ['revenue', 'units_sold', 'transaction_count', 'avg_profit_margin']
daily_sales.to_csv('./output/daily_sales.csv')

# Monthly sales
monthly_sales = df_sales.groupby([df_sales['date'].dt.year, df_sales['date'].dt.month]).agg({
    'total_amount': 'sum',
    'quantity': 'sum',
    'transaction_id': 'count',
    'profit_margin': 'mean'
}).round(2)
monthly_sales.columns = ['revenue', 'units_sold', 'transaction_count', 'avg_profit_margin']
monthly_sales.to_csv('./output/monthly_sales.csv')

# Category performance
category_sales = df_sales.groupby('category').agg({
    'total_amount': 'sum',
    'transaction_id': 'count',
    'profit_margin': 'mean',
    'quantity': 'sum'
}).round(2).sort_values('total_amount', ascending=False)
category_sales.columns = ['revenue', 'transaction_count', 'avg_profit_margin', 'units_sold']
category_sales.to_csv('./output/category_sales.csv')

print(f"✓ Daily sales: {len(daily_sales)} days analyzed")
print(f"✓ Monthly sales: {len(monthly_sales)} months analyzed")
print(f"✓ Category sales: {len(category_sales)} categories\n")

# ============================================================================
# STEP 3: CUSTOMER SEGMENTATION (RFM)
# ============================================================================
print("Step 3: Customer Segmentation (RFM Analysis)...")

max_date = df_sales['date'].max()

# Calculate RFM
rfm = df_sales.groupby('customer_id').agg({
    'date': lambda x: (max_date - x.max()).days,  # Recency
    'transaction_id': 'count',  # Frequency
    'total_amount': 'sum'  # Monetary
}).round(0)

rfm.columns = ['recency', 'frequency', 'monetary']

# Scoring (1-5)
rfm['r_score'] = pd.cut(rfm['recency'], bins=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert to numeric
rfm['r_score'] = pd.to_numeric(rfm['r_score'])
rfm['f_score'] = pd.to_numeric(rfm['f_score'])
rfm['m_score'] = pd.to_numeric(rfm['m_score'])

# Segmentation
def segment(row):
    if row['r_score'] >= 4 and row['f_score'] >= 4 and row['m_score'] >= 4:
        return 'VIP'
    elif row['r_score'] >= 3 and row['f_score'] >= 3:
        return 'Loyal'
    elif row['r_score'] >= 3:
        return 'At Risk'
    else:
        return 'Inactive'

rfm['segment'] = rfm.apply(segment, axis=1)
rfm.to_csv('./output/customer_segments.csv')

# Segment summary
segment_summary = rfm['segment'].value_counts()
print(f"✓ Customer Segments:")
for seg, count in segment_summary.items():
    print(f"  - {seg}: {count:,} customers")
print()

# ============================================================================
# STEP 4: INVENTORY ANALYSIS
# ============================================================================
print("Step 4: Inventory Analysis...")

# Product velocity
product_velocity = df_sales.groupby('product_id').agg({
    'quantity': 'sum',
    'transaction_id': 'count'
}).round(0)
product_velocity.columns = ['units_sold', 'sale_frequency']

# Merge with inventory
inventory_analysis = df_inventory.merge(product_velocity, on='product_id', how='left').fillna(0)

# Calculate metrics
inventory_analysis['inventory_turnover'] = np.round(
    inventory_analysis['units_sold'] / (inventory_analysis['quantity_on_hand'] + 1), 2
)
inventory_analysis['stock_status'] = inventory_analysis.apply(
    lambda row: 'CRITICAL' if row['quantity_on_hand'] < row['reorder_point'] 
                else ('LOW' if row['quantity_on_hand'] < row['reorder_point'] * 2 else 'ADEQUATE'),
    axis=1
)

inventory_analysis.to_csv('./output/inventory_analysis.csv', index=False)

critical = len(inventory_analysis[inventory_analysis['stock_status'] == 'CRITICAL'])
low = len(inventory_analysis[inventory_analysis['stock_status'] == 'LOW'])

print(f"✓ Inventory Status:")
print(f"  - Critical: {critical} items")
print(f"  - Low: {low} items")
print(f"  - Adequate: {len(inventory_analysis) - critical - low} items\n")

# ============================================================================
# STEP 5: TOP PRODUCTS ANALYSIS
# ============================================================================
print("Step 5: Top Products Analysis...")

top_products = df_sales.groupby('product_id').agg({
    'quantity': 'sum',
    'total_amount': 'sum',
    'transaction_id': 'count'
}).round(2).sort_values('total_amount', ascending=False).head(100)

top_products.columns = ['units_sold', 'revenue', 'purchase_count']
top_products.to_csv('./output/top_products.csv')

print(f"✓ Top 100 products identified\n")

# ============================================================================
# STEP 6: CUSTOMER LIFETIME VALUE
# ============================================================================
print("Step 6: Customer Lifetime Value...")

clv = df_sales.groupby('customer_id').agg({
    'total_amount': 'sum',
    'transaction_id': 'count',
    'profit': 'sum',
    'date': ['min', 'max']
}).round(2)

clv.columns = ['lifetime_value', 'purchase_count', 'total_profit', 'first_purchase', 'last_purchase']
clv = clv.sort_values('lifetime_value', ascending=False)
clv.to_csv('./output/customer_lifetime_value.csv')

print(f"✓ CLV calculated for {len(clv):,} customers\n")

# ============================================================================
# STEP 7: SALES FORECAST (Simple Moving Average)
# ============================================================================
print("Step 7: Sales Forecasting...")

daily_revenue = df_sales.groupby(df_sales['date'].dt.date)['total_amount'].sum().sort_index()
daily_revenue.index = pd.to_datetime(daily_revenue.index)

# 7-day moving average
ma_7 = daily_revenue.rolling(window=7).mean()
ma_30 = daily_revenue.rolling(window=30).mean()

forecast_data = pd.DataFrame({
    'actual_revenue': daily_revenue,
    'ma_7_day': ma_7,
    'ma_30_day': ma_30
}).dropna()

forecast_data.to_csv('./output/sales_forecast.csv')

print(f"✓ Forecast with moving averages calculated\n")

# ============================================================================
# STEP 8: KEY METRICS SUMMARY
# ============================================================================
print("Step 8: Computing Key Metrics...\n")

# Summary statistics
total_revenue = df_sales['total_amount'].sum()
total_transactions = len(df_sales)
avg_transaction_value = total_revenue / total_transactions
total_profit = df_sales['profit'].sum()
avg_profit_margin = df_sales['profit_margin'].mean()
unique_customers = df_sales['customer_id'].nunique()
unique_products = df_sales['product_id'].nunique()

# Growth metrics
df_sales_sorted = df_sales.sort_values('date')
first_half = df_sales_sorted[df_sales_sorted['date'] < max_date - timedelta(days=365)]
second_half = df_sales_sorted[df_sales_sorted['date'] >= max_date - timedelta(days=365)]

revenue_1h = first_half['total_amount'].sum()
revenue_2h = second_half['total_amount'].sum()
growth_rate = ((revenue_2h - revenue_1h) / revenue_1h) * 100 if revenue_1h > 0 else 0

# Create summary
summary = {
    'total_revenue': round(total_revenue, 2),
    'total_transactions': int(total_transactions),
    'average_transaction_value': round(avg_transaction_value, 2),
    'total_profit': round(total_profit, 2),
    'average_profit_margin': round(avg_profit_margin, 2),
    'unique_customers': int(unique_customers),
    'unique_products': int(unique_products),
    'unique_stores': len(df_stores),
    'growth_rate_percent': round(growth_rate, 2),
    'date_range': f"{df_sales['date'].min().date()} to {df_sales['date'].max().date()}"
}

with open('./output/summary_metrics.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("="*70)
print("KEY BUSINESS METRICS")
print("="*70)
print(f"\nRevenue:              ${summary['total_revenue']:,.2f}")
print(f"Transactions:         {summary['total_transactions']:,}")
print(f"Avg Transaction:      ${summary['average_transaction_value']:.2f}")
print(f"Total Profit:         ${summary['total_profit']:,.2f}")
print(f"Avg Profit Margin:    {summary['average_profit_margin']:.2f}%")
print(f"\nCustomers:            {summary['unique_customers']:,}")
print(f"Products:             {summary['unique_products']:,}")
print(f"Stores:               {summary['unique_stores']}")
print(f"\nGrowth Rate:          {summary['growth_rate_percent']:.2f}%")
print(f"Date Range:           {summary['date_range']}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("✓ ANALYSIS COMPLETE!")
print("="*70)

print("\nGenerated analytics files in ./output/:")
print("  • daily_sales.csv              - Daily revenue trends")
print("  • monthly_sales.csv            - Monthly aggregations")
print("  • category_sales.csv           - Sales by category")
print("  • customer_segments.csv        - RFM segmentation")
print("  • inventory_analysis.csv       - Inventory metrics")
print("  • top_products.csv             - Top 100 products")
print("  • customer_lifetime_value.csv  - CLV analysis")
print("  • sales_forecast.csv           - Forecast data")
print("  • summary_metrics.json         - Key metrics summary")

print("\nNext step: Run dashboard.html to visualize this data!")
print("="*70 + "\n")
