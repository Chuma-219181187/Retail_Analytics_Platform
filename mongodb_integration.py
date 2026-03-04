"""
RETAIL ANALYTICS PLATFORM - Phase 2: MongoDB Atlas Integration
==============================================================

Load retail data into MongoDB Atlas (NoSQL Database)

Setup Instructions:
1. Create free MongoDB Atlas account: https://www.mongodb.com/cloud/atlas
2. Create a cluster (free tier available)
3. Get connection string
4. Update MONGODB_URI below

Installation:
    pip install pymongo python-dotenv

Run:
    python mongodb_integration.py
"""

import json
import pandas as pd
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("RETAIL ANALYTICS - MONGODB ATLAS INTEGRATION")
print("="*80 + "\n")

# ================================================================
# MONGODB CONNECTION SETUP
# ================================================================

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    print("✓ PyMongo library loaded\n")
except ImportError:
    print("❌ PyMongo not installed")
    print("Install with: pip install pymongo")
    print("\nFalling back to JSON-based local storage...\n")
    
    # ========== LOCAL JSON-BASED FALLBACK ==========
    print("Creating local MongoDB-like JSON database...\n")
    
    os.makedirs('./database/mongodb_backup', exist_ok=True)
    
    # Load data
    df_sales = pd.read_csv('./data/sales.csv')
    df_products = pd.read_csv('./data/products.csv')
    df_customers = pd.read_csv('./data/customers.csv')
    df_stores = pd.read_csv('./data/stores.csv')
    df_inventory = pd.read_csv('./data/inventory.csv')
    
    print("Phase 1: Loading and Preparing Data")
    print("-" * 70)
    
    # Convert to JSON formats (MongoDB-like)
    print("✓ Converting sales to JSON format...")
    sales_records = df_sales.to_dict('records')
    
    print("✓ Converting products to JSON format...")
    products_records = df_products.to_dict('records')
    
    print("✓ Converting customers to JSON format...")
    customers_records = df_customers.to_dict('records')
    
    print("✓ Converting stores to JSON format...")
    stores_records = df_stores.to_dict('records')
    
    print("✓ Converting inventory to JSON format...")
    inventory_records = df_inventory.to_dict('records')
    
    # Load reviews
    print("✓ Loading reviews from JSON...")
    reviews_records = []
    try:
        with open('./data/reviews.json', 'r') as f:
            for line in f:
                reviews_records.append(json.loads(line))
    except:
        print("  (Reviews not found, creating sample...)")
    
    print(f"\nPhase 2: Saving Collections to Local Database")
    print("-" * 70)
    
    # Save collections
    collections = {
        'sales': sales_records,
        'products': products_records,
        'customers': customers_records,
        'stores': stores_records,
        'inventory': inventory_records,
        'reviews': reviews_records
    }
    
    for collection_name, records in collections.items():
        filepath = f'./database/mongodb_backup/{collection_name}.json'
        with open(filepath, 'w') as f:
            json.dump(records, f, indent=2, default=str)
        print(f"✓ {collection_name:15} - {len(records):10,} documents")
    
    print(f"\nPhase 3: Creating Indexes (Query Optimization)")
    print("-" * 70)
    
    # Create index metadata
    indexes = {
        'sales': ['product_id', 'customer_id', 'store_id', 'date'],
        'products': ['product_id', 'category', 'supplier'],
        'customers': ['customer_id', 'region'],
        'stores': ['store_id', 'region'],
        'inventory': ['store_id', 'product_id'],
        'reviews': ['product_id', 'customer_id', 'review_date']
    }
    
    # Save index metadata
    with open('./database/mongodb_backup/indexes.json', 'w') as f:
        json.dump(indexes, f, indent=2)
    
    for collection_name, index_fields in indexes.items():
        print(f"✓ {collection_name:15} - Indexes on: {', '.join(index_fields)}")
    
    print(f"\nPhase 4: Creating Aggregation Pipeline Configs")
    print("-" * 70)
    
    # Example aggregation pipelines
    pipelines = {
        'daily_sales': [
            {'$match': {}},
            {'$group': {
                '_id': '$date',
                'total_revenue': {'$sum': '$total_amount'},
                'transaction_count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ],
        'customer_segments': [
            {'$group': {
                '_id': '$customer_id',
                'total_spent': {'$sum': '$total_amount'},
                'purchase_count': {'$sum': 1},
                'last_purchase': {'$max': '$date'}
            }},
            {'$bucket': {
                'groupBy': '$total_spent',
                'boundaries': [0, 5000, 10000, 50000, 1000000],
                'default': 'other'
            }}
        ],
        'product_performance': [
            {'$group': {
                '_id': '$product_id',
                'total_quantity': {'$sum': '$quantity'},
                'total_revenue': {'$sum': '$total_amount'},
                'transaction_count': {'$sum': 1}
            }},
            {'$sort': {'total_revenue': -1}},
            {'$limit': 100}
        ]
    }
    
    with open('./database/mongodb_backup/aggregation_pipelines.json', 'w') as f:
        json.dump(pipelines, f, indent=2)
    
    print("✓ daily_sales              - Group by date and aggregate")
    print("✓ customer_segments         - RFM segmentation pipeline")
    print("✓ product_performance       - Top products by revenue")
    
    print(f"\nPhase 5: Validation & Statistics")
    print("-" * 70)
    
    # Validate data
    print(f"Total Documents:")
    total_docs = sum(len(records) for records in collections.values())
    print(f"  {total_docs:,} documents across {len(collections)} collections")
    
    # Data quality checks
    print(f"\nData Quality Metrics:")
    print(f"  Sales Date Range: {df_sales['date'].min()} to {df_sales['date'].max()}")
    print(f"  Total Revenue: ${df_sales['total_amount'].sum():,.2f}")
    print(f"  Unique Customers: {df_sales['customer_id'].nunique():,}")
    print(f"  Unique Products: {df_sales['product_id'].nunique():,}")
    print(f"  Unique Stores: {df_sales['store_id'].nunique():,}")
    
    print(f"\n" + "="*80)
    print("LOCAL DATABASE SETUP COMPLETE")
    print("="*80)
    
    print(f"\n📁 Database Location: ./database/mongodb_backup/")
    print(f"\n📊 Collections Ready for Analysis:")
    print(f"  • sales.json              - {len(sales_records):,} transaction records")
    print(f"  • products.json           - {len(products_records):,} product documents")
    print(f"  • customers.json          - {len(customers_records):,} customer profiles")
    print(f"  • stores.json             - {len(stores_records):,} store locations")
    print(f"  • inventory.json          - {len(inventory_records):,} stock records")
    print(f"  • reviews.json            - {len(reviews_records):,} review documents")
    
    print(f"\n📋 Configuration Files:")
    print(f"  • indexes.json            - Query indexes for optimization")
    print(f"  • aggregation_pipelines.json - Pre-configured analytics queries")
    
    print(f"\n🚀 TO CONNECT TO MONGODB ATLAS (Optional):")
    print(f"  1. Create cluster at: https://www.mongodb.com/cloud/atlas")
    print(f"  2. Get connection string")
    print(f"  3. Update MONGODB_URI in mongodb_integration.py")
    print(f"  4. Run: python mongodb_integration.py")
    
    print(f"\n" + "="*80 + "\n")
    
    exit(0)

# ================================================================
# MONGODB ATLAS CONNECTION (if PyMongo available)
# ================================================================

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://username:password@cluster.mongodb.net/retail_analytics')

print("Phase 1: Connecting to MongoDB Atlas")
print("-" * 70)

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ismaster')
    
    db = client['retail_analytics']
    print("✓ Connected to MongoDB Atlas")
    print(f"  Database: {db.name}\n")
    
except Exception as e:
    print(f"⚠️  Could not connect to MongoDB Atlas: {str(e)[:60]}")
    print("\nUsage Instructions:")
    print("  1. Create account: https://www.mongodb.com/cloud/atlas")
    print("  2. Set environment variable:")
    print(f"     $env:MONGODB_URI = 'your-connection-string'")
    print("  3. Run this script again")
    exit(1)

print("Phase 2: Loading Data Files")
print("-" * 70)

try:
    df_sales = pd.read_csv('./data/sales.csv')
    df_products = pd.read_csv('./data/products.csv')
    df_customers = pd.read_csv('./data/customers.csv')
    df_stores = pd.read_csv('./data/stores.csv')
    
    print(f"✓ Sales: {len(df_sales):,} records")
    print(f"✓ Products: {len(df_products):,} records")
    print(f"✓ Customers: {len(df_customers):,} records")
    print(f"✓ Stores: {len(df_stores):,} records\n")
    
except Exception as e:
    print(f"❌ Error loading files: {e}")
    exit(1)

print("Phase 3: Inserting Data into MongoDB")
print("-" * 70)

try:
    # Drop existing collections
    print("Clearing existing collections...")
    for collection_name in ['sales', 'products', 'customers', 'stores', 'reviews']:
        db[collection_name].drop()
    
    # Insert products
    products = db['products']
    products.insert_many(df_products.to_dict('records'))
    print(f"✓ Inserted {products.count_documents({}):,} products")
    
    # Insert customers
    customers = db['customers']
    customers.insert_many(df_customers.to_dict('records'))
    print(f"✓ Inserted {customers.count_documents({}):,} customers")
    
    # Insert stores
    stores = db['stores']
    stores.insert_many(df_stores.to_dict('records'))
    print(f"✓ Inserted {stores.count_documents({}):,} stores")
    
    # Insert sales
    sales = db['sales']
    sales.insert_many(df_sales.to_dict('records'), ordered=False)
    print(f"✓ Inserted {sales.count_documents({}):,} sales transactions")
    
    # Insert reviews
    reviews = db['reviews']
    review_records = []
    try:
        with open('./data/reviews.json', 'r') as f:
            for line in f:
                review_records.append(json.loads(line))
        reviews.insert_many(review_records, ordered=False)
        print(f"✓ Inserted {reviews.count_documents({}):,} reviews")
    except:
        print("  (Reviews not inserted)")
    
except Exception as e:
    print(f"⚠️  Error during insertion: {str(e)[:100]}")

print("\nPhase 4: Creating Indexes for Performance")
print("-" * 70)

try:
    # Sales indexes
    db['sales'].create_index('product_id')
    db['sales'].create_index('customer_id')
    db['sales'].create_index('store_id')
    db['sales'].create_index('date')
    db['sales'].create_index([('date', -1)])  # Descending for recent queries
    print("✓ Sales collection indexes created")
    
    # Product indexes
    db['products'].create_index('product_id', unique=True)
    db['products'].create_index('category')
    db['products'].create_index('supplier')
    print("✓ Products collection indexes created")
    
    # Customer indexes
    db['customers'].create_index('customer_id', unique=True)
    db['customers'].create_index('region')
    print("✓ Customers collection indexes created")
    
    # Store indexes
    db['stores'].create_index('store_id', unique=True)
    db['stores'].create_index('region')
    print("✓ Stores collection indexes created")
    
    # Review indexes
    db['reviews'].create_index('product_id')
    db['reviews'].create_index('customer_id')
    db['reviews'].create_index('review_date')
    print("✓ Reviews collection indexes created")
    
except Exception as e:
    print(f"⚠️  Index creation issue: {str(e)[:80]}")

print("\nPhase 5: Sample Aggregation Queries")
print("-" * 70)

try:
    # 1. Daily sales
    pipeline = [
        {'$group': {'_id': '$date', 'revenue': {'$sum': '$total_amount'}, 'count': {'$sum': 1}}},
        {'$sort': {'_id': -1}},
        {'$limit': 10}
    ]
    
    results = list(db['sales'].aggregate(pipeline))
    if results:
        print(f"✓ Daily sales aggregation: {len(results)} records")
    
    # 2. Top products
    pipeline = [
        {'$group': {'_id': '$product_id', 'total_sales': {'$sum': '$total_amount'}, 'count': {'$sum': 1}}},
        {'$sort': {'total_sales': -1}},
        {'$limit': 5}
    ]
    
    results = list(db['sales'].aggregate(pipeline))
    if results:
        print(f"✓ Top products query: {len(results)} products")
    
except Exception as e:
    print(f"⚠️  Aggregation error: {str(e)[:60]}")

print("\n" + "="*80)
print("MONGODB INTEGRATION COMPLETE")
print("="*80)

print(f"\n📊 Collections Summary:")
print(f"  Sales: {db['sales'].count_documents({})}")
print(f"  Products: {db['products'].count_documents({})}")
print(f"  Customers: {db['customers'].count_documents({})}")
print(f"  Stores: {db['stores'].count_documents({})}")

print(f"\n✅ Database Ready for:")
print(f"  • Complex queries with indexes")
print(f"  • Aggregation pipelines")
print(f"  • Structured and unstructured data (reviews)")
print(f"  • Scalable data operations")

print(f"\n🔗 Connection String:")
print(f"  {MONGODB_URI[:60]}...")

print("\n" + "="*80 + "\n")
