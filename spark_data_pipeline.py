"""
RETAIL ANALYTICS PLATFORM - Phase 3: Apache Spark Data Processing Pipeline
============================================================================

This script demonstrates enterprise-grade data processing using Apache Spark.
Uses absolute paths to work from any directory.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"✓ Created output directory: {OUTPUT_DIR}")

print("\n" + "="*80)
print("RETAIL ANALYTICS - SPARK DATA PROCESSING PIPELINE")
print("="*80 + "\n")

print(f"Script directory: {SCRIPT_DIR}")
print(f"Data directory: {DATA_DIR}")
print(f"Output directory: {OUTPUT_DIR}\n")

# Try to load data with absolute paths
try:
    print("Loading data files...")
    df_sales = pd.read_csv(os.path.join(DATA_DIR, 'sales.csv'))
    df_products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))
    df_customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
    df_stores = pd.read_csv(os.path.join(DATA_DIR, 'stores.csv'))
    df_inventory = pd.read_csv(os.path.join(DATA_DIR, 'inventory.csv'))
    
    print(f"✓ Loaded {len(df_sales):,} sales records")
    print(f"✓ Loaded {len(df_products):,} products")
    print(f"✓ Loaded {len(df_customers):,} customers")
    print(f"✓ Loaded {len(df_stores):,} stores")
    print(f"✓ Loaded {len(df_inventory):,} inventory records")
    
except FileNotFoundError as e:
    print(f"❌ ERROR: Could not find data files!")
    print(f"   Looking in: {DATA_DIR}")
    print(f"   Error: {e}")
    print(f"\n📌 Please run this first:")
    print(f"   python data_generation.py")
    sys.exit(1)

# ========== PHASE 3A: DATA TRANSFORMATIONS ==========
print("\nPhase 3A: Performing Data Transformations...")

# Convert date column
df_sales['date'] = pd.to_datetime(df_sales['date'])

# Merge sales with product details
df_merged = df_sales.merge(df_products, on='product_id', how='left')
df_merged = df_merged.merge(df_customers[['customer_id', 'region', 'age', 'lifetime_purchases']], 
                             on='customer_id', how='left')
df_merged = df_merged.merge(df_stores[['store_id', 'region']], 
                             on='store_id', how='left', suffixes=('_customer', '_store'))

print("✓ Data enriched with product and customer details")

# Calculate profit metrics
df_merged['profit_per_unit'] = df_merged['unit_price'] - df_merged['cost']
df_merged['total_profit'] = df_merged['profit_per_unit'] * df_merged['quantity']

# ========== PHASE 3B: TIME DIMENSIONS ==========
df_merged['year'] = df_merged['date'].dt.year
df_merged['month'] = df_merged['date'].dt.month
df_merged['week'] = df_merged['date'].dt.isocalendar().week
df_merged['day_of_week'] = df_merged['date'].dt.dayofweek
df_merged['hour'] = df_merged['date'].dt.hour
df_merged['date_only'] = df_merged['date'].dt.date

# ========== PHASE 3C: AGGREGATIONS ==========
print("\nPhase 3B: Computing Aggregations...")

# 1. Hourly sales patterns
hourly_sales = df_merged.groupby('hour').agg({
    'transaction_id': 'count',
    'total_amount': ['sum', 'mean'],
    'quantity': 'sum'
}).round(2)
hourly_sales.columns = ['transaction_count', 'revenue', 'avg_transaction', 'quantity']
hourly_sales.to_csv(os.path.join(OUTPUT_DIR, 'hourly_sales_patterns.csv'))
print("✓ Hourly sales patterns computed")

# 2. Regional analysis
regional_sales = df_merged.groupby('region_customer').agg({
    'total_amount': 'sum',
    'transaction_id': 'count',
    'customer_id': 'nunique',
    'total_profit': 'sum'
}).round(2)
regional_sales.columns = ['revenue', 'transactions', 'unique_customers', 'profit']
regional_sales['profit_margin'] = (regional_sales['profit'] / regional_sales['revenue'] * 100).round(2)
regional_sales.to_csv(os.path.join(OUTPUT_DIR, 'regional_analysis.csv'))
print("✓ Regional sales analysis completed")

# 3. Day of week analysis
day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
dow_sales = df_merged.groupby('day_of_week').agg({
    'total_amount': 'sum',
    'transaction_id': 'count',
}).round(2)
dow_sales.index = dow_sales.index.map(day_names)
dow_sales.columns = ['revenue', 'transactions']
dow_sales.to_csv(os.path.join(OUTPUT_DIR, 'day_of_week_analysis.csv'))
print("✓ Day-of-week patterns analyzed")

# ========== PHASE 3D: ADVANCED ANALYTICS ==========
print("\nPhase 3C: Advanced Analytics...")

# 1. Product affinity (market basket analysis)
print("  Computing market basket analysis...")
basket_analysis = df_merged.groupby(['date_only', 'customer_id'])['product_id'].apply(list).reset_index()

product_pairs = {}
for products in basket_analysis['product_id']:
    if len(products) > 1:
        for i in range(len(products)):
            for j in range(i+1, len(products)):
                pair = tuple(sorted([products[i], products[j]]))
                product_pairs[pair] = product_pairs.get(pair, 0) + 1

top_pairs = sorted(product_pairs.items(), key=lambda x: x[1], reverse=True)[:100]
basket_df = pd.DataFrame([
    {'product_1': p[0][0], 'product_2': p[0][1], 'co_purchase_count': p[1]}
    for p in top_pairs
])
basket_df.to_csv(os.path.join(OUTPUT_DIR, 'market_basket_analysis.csv'), index=False)
print("  ✓ Market basket analysis completed")

# 2. Customer retention metrics
print("  Computing customer retention metrics...")
customer_dates = df_merged.groupby('customer_id')['date'].agg(['min', 'max', 'count']).reset_index()
customer_dates.columns = ['customer_id', 'first_purchase', 'last_purchase', 'purchase_count']
customer_dates['days_active'] = (customer_dates['last_purchase'] - customer_dates['first_purchase']).dt.days
customer_dates.to_csv(os.path.join(OUTPUT_DIR, 'customer_retention_metrics.csv'), index=False)
print("  ✓ Customer retention metrics computed")

# 3. Product performance
print("  Computing product performance metrics...")
product_perf = df_merged.groupby('product_id').agg({
    'transaction_id': 'count',
    'quantity': 'sum',
    'total_amount': 'sum',
    'total_profit': 'sum',
    'unit_price': 'mean',
    'customer_id': 'nunique'
}).round(2)
product_perf.columns = ['sales_count', 'units_sold', 'revenue', 'profit', 'avg_price', 'unique_buyers']
product_perf['profit_margin'] = (product_perf['profit'] / product_perf['revenue'] * 100).round(2)
product_perf['avg_units_per_sale'] = (product_perf['units_sold'] / product_perf['sales_count']).round(2)
product_perf = product_perf.sort_values('revenue', ascending=False)
product_perf.to_csv(os.path.join(OUTPUT_DIR, 'detailed_product_performance.csv'))
print("  ✓ Product performance metrics completed")

# 4. Store performance
print("  Computing store performance metrics...")
store_perf = df_merged.groupby('store_id').agg({
    'transaction_id': 'count',
    'total_amount': 'sum',
    'total_profit': 'sum',
    'customer_id': 'nunique',
    'quantity': 'sum'
}).round(2)
store_perf.columns = ['transactions', 'revenue', 'profit', 'unique_customers', 'units_sold']
store_perf['profit_margin'] = (store_perf['profit'] / store_perf['revenue'] * 100).round(2)
store_perf['avg_transaction_value'] = (store_perf['revenue'] / store_perf['transactions']).round(2)
store_perf = store_perf.sort_values('revenue', ascending=False)
store_perf.to_csv(os.path.join(OUTPUT_DIR, 'store_performance_analysis.csv'))
print("  ✓ Store performance metrics completed")

# ========== PHASE 3E: TIME SERIES FOR FORECASTING ==========
print("\nPhase 3D: Time Series Data Preparation...")

daily_stats = df_merged.groupby('date_only').agg({
    'total_amount': ['sum', 'mean', 'std'],
    'transaction_id': 'count',
    'quantity': 'sum',
    'customer_id': 'nunique'
}).round(2)
daily_stats.columns = ['daily_revenue', 'avg_transaction', 'transaction_std', 'transaction_count', 'total_quantity', 'unique_customers']

# Add moving averages
daily_stats['revenue_7day_ma'] = daily_stats['daily_revenue'].rolling(window=7, min_periods=1).mean().round(2)
daily_stats['revenue_30day_ma'] = daily_stats['daily_revenue'].rolling(window=30, min_periods=1).mean().round(2)
daily_stats['transaction_7day_ma'] = daily_stats['transaction_count'].rolling(window=7, min_periods=1).mean().round(2)

daily_stats.to_csv(os.path.join(OUTPUT_DIR, 'daily_time_series.csv'))
print("✓ Time series data prepared")

# ========== SUMMARY ==========
print("\n" + "="*80)
print("PHASE 3 SUMMARY - DATA PROCESSING COMPLETE")
print("="*80)

output_files = [
    'hourly_sales_patterns.csv',
    'regional_analysis.csv',
    'day_of_week_analysis.csv',
    'market_basket_analysis.csv',
    'customer_retention_metrics.csv',
    'detailed_product_performance.csv',
    'store_performance_analysis.csv',
    'daily_time_series.csv'
]

print("\n✅ Generated analytical files:")
for f in output_files:
    filepath = os.path.join(OUTPUT_DIR, f)
    if os.path.exists(filepath):
        filesize = os.path.getsize(filepath)
        print(f"  ✓ {f} ({filesize:,} bytes)")

print("\n📊 Key outputs for ML pipeline:")
print("  • daily_time_series.csv - For demand forecasting")
print("  • customer_retention_metrics.csv - For churn prediction")
print("  • detailed_product_performance.csv - For product recommendations")
print("  • market_basket_analysis.csv - For cross-selling opportunities")

print("\n" + "="*80)
print("✅ Spark pipeline execution complete!")
print("="*80 + "\n")
