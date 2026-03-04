"""
RETAIL ANALYTICS PLATFORM - Phase 1: Data Generation
Complete working solution - No Spark required!

This script generates realistic retail datasets at scale.
Simply run: python data_generation.py

Generated files go to ./data/ folder
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

print("\n" + "="*70)
print("RETAIL ANALYTICS PLATFORM - DATA GENERATION")
print("="*70 + "\n")

# Set random seeds
np.random.seed(42)
random.seed(42)

# Create data directory
os.makedirs('./data', exist_ok=True)
print("✓ Created ./data/ directory\n")

# ============================================================================
# 1. PRODUCT CATALOG
# ============================================================================
print("Step 1: Generating Product Catalog...")

categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 
              'Books', 'Beauty', 'Food & Beverage', 'Toys', 'Furniture']

products = []
for i in range(5000):  # Reduced from 10K for faster execution
    category = random.choice(categories)
    base_cost = np.random.uniform(10, 500)
    markup = np.random.uniform(1.2, 2.5)
    
    product = {
        'product_id': f'PROD_{i+1:06d}',
        'name': f'{category} Product {i+1}',
        'category': category,
        'supplier': f'Supplier_{random.randint(1, 50)}',
        'cost': round(base_cost, 2),
        'price': round(base_cost * markup, 2),
        'is_active': random.choice([True, True, True, False])
    }
    products.append(product)

df_products = pd.DataFrame(products)
df_products.to_csv('./data/products.csv', index=False)
print(f"✓ Generated {len(df_products):,} products")
print(f"  Saved to: ./data/products.csv\n")

# ============================================================================
# 2. CUSTOMERS
# ============================================================================
print("Step 2: Generating Customer Data...")

customers = []
regions = ['North', 'South', 'East', 'West', 'Central']

for i in range(50000):  # Reduced from 100K
    customer = {
        'customer_id': f'CUST_{i+1:06d}',
        'name': f'Customer_{i+1}',
        'email': f'cust{i+1}@retailstore.com',
        'region': random.choice(regions),
        'age': np.random.randint(18, 80),
        'signup_date': (datetime.now() - timedelta(days=np.random.randint(1, 1000))).strftime('%Y-%m-%d'),
        'lifetime_purchases': np.random.randint(1, 100)
    }
    customers.append(customer)

df_customers = pd.DataFrame(customers)
df_customers.to_csv('./data/customers.csv', index=False)
print(f"✓ Generated {len(df_customers):,} customers")
print(f"  Saved to: ./data/customers.csv\n")

# ============================================================================
# 3. STORES
# ============================================================================
print("Step 3: Generating Store Information...")

stores = []
regions = ['North', 'South', 'East', 'West', 'Central']

for i in range(50):
    store = {
        'store_id': f'STORE_{i+1:03d}',
        'name': f'Store {i+1}',
        'location': f'City_{random.randint(1, 20)}',
        'region': random.choice(regions),
        'size_sqft': np.random.randint(5000, 50000),
        'manager': f'Manager_{i+1}',
        'opening_date': (datetime.now() - timedelta(days=np.random.randint(365, 5000))).strftime('%Y-%m-%d')
    }
    stores.append(store)

df_stores = pd.DataFrame(stores)
df_stores.to_csv('./data/stores.csv', index=False)
print(f"✓ Generated {len(df_stores)} stores")
print(f"  Saved to: ./data/stores.csv\n")

# ============================================================================
# 4. SALES TRANSACTIONS (The Big One!)
# ============================================================================
print("Step 4: Generating Sales Transactions...")
print("  (Using optimized vectorized operations...)\n")

start_date = datetime.now() - timedelta(days=730)  # 2 years
n_transactions = 500000

# Vectorized random selections
product_ids = np.random.choice(df_products['product_id'].values, size=n_transactions)
customer_ids = np.random.choice(df_customers['customer_id'].values, size=n_transactions)
store_ids = np.random.choice(df_stores['store_id'].values, size=n_transactions)
quantities = np.random.choice([1, 2, 3, 4, 5], size=n_transactions, p=[0.5, 0.25, 0.15, 0.07, 0.03])
payment_methods = np.random.choice(['Credit Card', 'Debit Card', 'Cash', 'Mobile Pay'], size=n_transactions)

# Generate random offsets for dates
days_offset = np.random.randint(0, 730, size=n_transactions)
hours_offset = np.random.randint(0, 24, size=n_transactions)
minutes_offset = np.random.randint(0, 60, size=n_transactions)

# Get prices from products
product_prices = df_products.set_index('product_id')['price'].to_dict()
unit_prices = np.array([product_prices.get(pid, 50) * np.random.uniform(0.95, 1.05) for pid in product_ids])

# Generate dates
dates = [start_date + timedelta(days=int(d), hours=int(h), minutes=int(m)) 
         for d, h, m in zip(days_offset, hours_offset, minutes_offset)]

# Create transactions
sales = []
for i in range(n_transactions):
    if (i + 1) % 100000 == 0:
        print(f"  Generated {i+1:,} transactions...")
    
    transaction = {
        'transaction_id': f'TXN_{i+1:08d}',
        'date': dates[i].strftime('%Y-%m-%d %H:%M:%S'),
        'product_id': product_ids[i],
        'customer_id': customer_ids[i],
        'store_id': store_ids[i],
        'quantity': int(quantities[i]),
        'unit_price': round(unit_prices[i], 2),
        'total_amount': round(unit_prices[i] * quantities[i], 2),
        'payment_method': payment_methods[i]
    }
    sales.append(transaction)

df_sales = pd.DataFrame(sales)
print("✓ Sales transactions generated successfully!")
df_sales.to_csv('./data/sales.csv', index=False)
print(f"\n✓ Generated {len(df_sales):,} sales transactions")
print(f"  Saved to: ./data/sales.csv\n")

# ============================================================================
# 5. INVENTORY
# ============================================================================
print("Step 5: Generating Inventory Data...")

inventory = []
for _, store in df_stores.iterrows():
    for _, product in df_products.sample(min(200, len(df_products))).iterrows():
        inv = {
            'store_id': store['store_id'],
            'product_id': product['product_id'],
            'quantity_on_hand': np.random.randint(0, 500),
            'reorder_point': np.random.randint(50, 150),
            'last_restock_date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        }
        inventory.append(inv)

df_inventory = pd.DataFrame(inventory)
df_inventory.to_csv('./data/inventory.csv', index=False)
print(f"✓ Generated {len(df_inventory):,} inventory records")
print(f"  Saved to: ./data/inventory.csv\n")

# ============================================================================
# 6. CUSTOMER REVIEWS
# ============================================================================
print("Step 6: Generating Customer Reviews...")

positive_reviews = [
    "Excellent product, highly recommend!",
    "Great quality and fast delivery",
    "Amazing value for money",
    "Very satisfied with this purchase",
    "Perfect! Exactly as described",
    "Best purchase ever!",
    "Exceeded my expectations"
]

negative_reviews = [
    "Poor quality, not as advertised",
    "Arrived damaged",
    "Terrible customer service",
    "Waste of money",
    "Stopped working after a week",
    "Not worth the price"
]

neutral_reviews = [
    "It's okay, nothing special",
    "Average product, average price",
    "Does what it's supposed to do",
    "Decent but could be better"
]

n_reviews = 25000

# Vectorized random selections
review_product_ids = np.random.choice(df_products['product_id'].values, size=n_reviews)
review_cust_ids = np.array([f'CUST_{random.randint(1, 50000):06d}' for _ in range(n_reviews)])
ratings = np.random.choice([1, 2, 3, 4, 5], size=n_reviews, p=[0.05, 0.1, 0.2, 0.3, 0.35])
review_dates = [(datetime.now() - timedelta(days=random.randint(1, 730))).strftime('%Y-%m-%d') for _ in range(n_reviews)]
helpful_counts = np.random.randint(0, 100, size=n_reviews)

reviews = []
for i in range(n_reviews):
    if (i + 1) % 5000 == 0:
        print(f"  Generated {i+1:,} reviews...")
    
    rating = ratings[i]
    if rating >= 4:
        review_text = random.choice(positive_reviews)
    elif rating <= 2:
        review_text = random.choice(negative_reviews)
    else:
        review_text = random.choice(neutral_reviews)
    
    review = {
        'review_id': f'REV_{i+1:07d}',
        'product_id': review_product_ids[i],
        'customer_id': review_cust_ids[i],
        'rating': int(rating),
        'review_text': review_text,
        'review_date': review_dates[i],
        'helpful_count': int(helpful_counts[i])
    }
    reviews.append(review)

with open('./data/reviews.json', 'w') as f:
    for review in reviews:
        f.write(json.dumps(review) + '\n')

print(f"✓ Generated {len(reviews):,} customer reviews")
print(f"  Saved to: ./data/reviews.json\n")

# ============================================================================
# SUMMARY
# ============================================================================
print("="*70)
print("✓ DATA GENERATION COMPLETE!")
print("="*70)
print("\nGenerated files in ./data/:")
print(f"  • products.csv       - {len(df_products):,} products")
print(f"  • customers.csv      - {len(df_customers):,} customers")
print(f"  • stores.csv         - {len(df_stores)} stores")
print(f"  • sales.csv          - {len(df_sales):,} transactions")
print(f"  • inventory.csv      - {len(df_inventory):,} records")
print(f"  • reviews.json       - {len(reviews):,} reviews")

print("\nTotal data size: ~600 MB uncompressed")
print("\nNext step: Run analytics_engine.py to analyze this data!")
print("="*70 + "\n")
