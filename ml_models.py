"""
RETAIL ANALYTICS PLATFORM - Phase 5: Machine Learning Models
============================================================

Advanced ML models for:
- Demand forecasting
- Customer churn prediction
- Product recommendations
- Price optimization

Installation:
    pip install scikit-learn statsmodels lightgbm xgboost

Run after spark_data_pipeline.py:
    python ml_models.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("RETAIL ANALYTICS - MACHINE LEARNING MODELS")
print("="*80 + "\n")

# Load preprocessed data
try:
    df_sales = pd.read_csv('./data/sales.csv')
    df_products = pd.read_csv('./data/products.csv')
    df_customers = pd.read_csv('./data/customers.csv')
    df_stores = pd.read_csv('./data/stores.csv')
    
    # Load time series data if available
    try:
        df_daily = pd.read_csv('./output/daily_time_series.csv', index_col=0)
        df_daily.index = pd.to_datetime(df_daily.index)
    except:
        df_daily = None
    
    print("✓ Data loaded successfully\n")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit(1)

# ================================================================
# MODEL 1: DEMAND FORECASTING (Time Series Analysis)
# ================================================================

print("MODEL 1: Demand Forecasting (ARIMA/Exponential Smoothing)")
print("-" * 70)

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    import json
    
    df_sales['date'] = pd.to_datetime(df_sales['date'])
    daily_revenue = df_sales.groupby(df_sales['date'].dt.date)['total_amount'].sum().reset_index()
    daily_revenue.columns = ['date', 'revenue']
    daily_revenue['date'] = pd.to_datetime(daily_revenue['date'])
    daily_revenue = daily_revenue.set_index('date').sort_index()
    
    print("✓ Historical daily revenue data prepared")
    
    # Split data: 80% train, 20% test
    train_size = int(len(daily_revenue) * 0.8)
    train_data = daily_revenue[:train_size]
    test_data = daily_revenue[train_size:]
    
    print(f"  Training set: {len(train_data)} days")
    print(f"  Test set: {len(test_data)} days")
    
    # Method 1: ARIMA(1,1,1) - Simpler, faster
    print("\n  Training ARIMA(1,1,1) model...")
    try:
        arima_model = ARIMA(train_data['revenue'], order=(1, 1, 1))
        arima_fit = arima_model.fit()
        arima_pred = arima_fit.forecast(steps=len(test_data))
        
        # Calculate MAE
        arima_mae = np.mean(np.abs(arima_pred.values - test_data['revenue'].values))
        print(f"  ✓ ARIMA MAE: ${arima_mae:,.2f}")
    except Exception as e:
        print(f"  ⚠️  ARIMA failed: {str(e)[:50]}")
        arima_pred = None
        arima_mae = None
    
    # Method 2: Exponential Smoothing
    print("  Training Exponential Smoothing model...")
    try:
        exp_model = ExponentialSmoothing(train_data['revenue'], trend='add', seasonal=None)
        exp_fit = exp_model.fit()
        exp_pred = exp_fit.forecast(steps=len(test_data))
        
        exp_mae = np.mean(np.abs(exp_pred.values - test_data['revenue'].values))
        print(f"  ✓ Exp Smoothing MAE: ${exp_mae:,.2f}")
    except Exception as e:
        print(f"  ⚠️  Exponential Smoothing failed: {str(e)[:50]}")
        exp_pred = None
        exp_mae = None
    
    # Create forecast for next 30 days
    if arima_fit:
        future_forecast = arima_fit.forecast(steps=30)
    else:
        future_forecast = daily_revenue['revenue'].tail(30).values
    
    forecast_df = pd.DataFrame({
        'date': pd.date_range(daily_revenue.index[-1] + timedelta(days=1), periods=30),
        'predicted_revenue': future_forecast.values if hasattr(future_forecast, 'values') else future_forecast
    })
    forecast_df['predicted_revenue'] = forecast_df['predicted_revenue'].round(2)
    forecast_df.to_csv('./output/ml_demand_forecast_30day.csv', index=False)
    
    print("✓ Demand forecast generated for next 30 days")
    print("  Saved to: ml_demand_forecast_30day.csv\n")
    
except ImportError:
    print("⚠️  Installing required packages: pip install statsmodels")
    print("  Skipping ARIMA analysis\n")

# ================================================================
# MODEL 2: CUSTOMER CHURN PREDICTION
# ================================================================

print("MODEL 2: Customer Churn Prediction")
print("-" * 70)

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score, classification_report
    from sklearn.preprocessing import StandardScaler
    
    # Feature engineering
    df_sales['date'] = pd.to_datetime(df_sales['date'])
    
    # Customer lifetime analysis
    customer_stats = df_sales.groupby('customer_id').agg({
        'date': ['min', 'max', 'count'],
        'total_amount': ['sum', 'mean'],
        'quantity': 'mean'
    }).reset_index()
    
    customer_stats.columns = ['customer_id', 'first_purchase', 'last_purchase', 
                              'purchase_count', 'total_spent', 'avg_transaction', 'avg_quantity']
    
    # Calculate days since last purchase
    latest_date = df_sales['date'].max()
    customer_stats['days_since_purchase'] = (latest_date - pd.to_datetime(customer_stats['last_purchase'])).dt.days
    
    # RFM features
    customer_stats['recency'] = customer_stats['days_since_purchase']
    customer_stats['frequency'] = customer_stats['purchase_count']
    customer_stats['monetary'] = customer_stats['total_spent']
    
    # Customer lifetime in days
    customer_stats['customer_lifetime_days'] = (pd.to_datetime(customer_stats['last_purchase']) - pd.to_datetime(customer_stats['first_purchase'])).dt.days
    
    # Create churn label (no purchase in last 90 days = churned)
    customer_stats['is_churned'] = (customer_stats['days_since_purchase'] > 90).astype(int)
    
    print(f"Churn Rate: {customer_stats['is_churned'].mean()*100:.2f}%")
    print(f"Active Customers: {(customer_stats['is_churned']==0).sum():,}")
    print(f"Churned Customers: {(customer_stats['is_churned']==1).sum():,}\n")
    
    # Prepare features
    features = ['recency', 'frequency', 'monetary', 'avg_transaction', 'customer_lifetime_days']
    X = customer_stats[features].fillna(0)
    y = customer_stats['is_churned']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    print("Training Random Forest classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = rf_model.predict(X_test_scaled)
    y_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]
    
    # Evaluation
    auc_score = roc_auc_score(y_test, y_pred_proba)
    print(f"✓ Model AUC Score: {auc_score:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    for idx, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Get churn probabilities for all customers
    X_all_scaled = scaler.transform(X)
    customer_stats['churn_probability'] = rf_model.predict_proba(X_all_scaled)[:, 1]
    
    # High-risk customers (churn probability > 60%)
    high_risk = customer_stats[customer_stats['churn_probability'] > 0.6].sort_values('churn_probability', ascending=False)
    high_risk_output = high_risk[['customer_id', 'recency', 'frequency', 'monetary', 'churn_probability']].head(100)
    high_risk_output.to_csv('./output/ml_high_risk_customers.csv', index=False)
    
    print(f"\n✓ Identified {len(high_risk):,} high-risk customers (>60% churn probability)")
    print(f"  Top 100 exported to: ml_high_risk_customers.csv")
    
    # Feature importance
    feature_importance.to_csv('./output/ml_churn_feature_importance.csv', index=False)
    print(f"  Feature importance exported to: ml_churn_feature_importance.csv\n")
    
except Exception as e:
    print(f"Error in churn prediction: {str(e)[:100]}")
    print()

# ================================================================
# MODEL 3: PRODUCT RECOMMENDATION ENGINE
# ================================================================

print("MODEL 3: Product Recommendation Engine")
print("-" * 70)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Product features
    product_features = df_products.copy()
    
    # Vectorize product categories
    tfidf = TfidfVectorizer()
    category_vectors = tfidf.fit_transform(product_features['category'].fillna('Unknown'))
    
    # Compute similarity matrix
    similarity_matrix = cosine_similarity(category_vectors)
    
    # Get similar products for top 20 products
    top_products = df_sales['product_id'].value_counts().head(20).index.tolist()
    
    recommendations = []
    for product_id in top_products:
        try:
            prod_idx = product_features[product_features['product_id'] == product_id].index[0]
            similar_idx = np.argsort(similarity_matrix[prod_idx])[-6:-1][::-1]  # Top 5 similar
            
            for similar_product_idx in similar_idx:
                recommendations.append({
                    'source_product': product_id,
                    'recommended_product': product_features.iloc[similar_product_idx]['product_id'],
                    'similarity_score': similarity_matrix[prod_idx][similar_product_idx],
                    'category': product_features.iloc[similar_product_idx]['category']
                })
        except:
            pass
    
    if recommendations:
        rec_df = pd.DataFrame(recommendations).sort_values('similarity_score', ascending=False)
        rec_df['similarity_score'] = rec_df['similarity_score'].round(4)
        rec_df.to_csv('./output/ml_product_recommendations.csv', index=False)
        print(f"✓ Generated {len(rec_df):,} product recommendations")
        print(f"  Saved to: ml_product_recommendations.csv\n")
    else:
        print("⚠️  Could not generate recommendations\n")

except Exception as e:
    print(f"Error in recommendation engine: {str(e)[:100]}\n")

# ================================================================
# MODEL 4: PRICE OPTIMIZATION
# ================================================================

print("MODEL 4: Price Optimization Analysis")
print("-" * 70)

try:
    from scipy.stats import linregress
    
    # Analyze price elasticity
    product_analysis = df_sales.merge(df_products[['product_id', 'price', 'cost']], on='product_id')
    
    # Group by product and calculate statistics
    price_elasticity = []
    
    for product_id in df_products['product_id'].unique()[:500]:  # Sample for performance
        prod_data = product_analysis[product_analysis['product_id'] == product_id]
        
        if len(prod_data) > 10:
            # Simple elasticity: quantity vs price
            prices = prod_data['unit_price'].values
            quantities = prod_data['quantity'].values
            
            if len(np.unique(prices)) > 1:
                slope, intercept, r_value, p_value, std_err = linregress(prices, quantities)
                
                avg_price = prices.mean()
                avg_quantity = quantities.mean()
                
                # Elasticity = (% change in quantity) / (% change in price)
                if avg_price > 0 and avg_quantity > 0:
                    elasticity = (slope * avg_price) / avg_quantity
                    
                    price_elasticity.append({
                        'product_id': product_id,
                        'avg_price': avg_price,
                        'avg_quantity': avg_quantity,
                        'elasticity': elasticity,
                        'r_squared': r_value ** 2,
                        'sales_count': len(prod_data),
                        'optimal_price_change': 'Increase' if elasticity > -1 else 'Decrease'
                    })
    
    if price_elasticity:
        price_df = pd.DataFrame(price_elasticity).sort_values('r_squared', ascending=False).head(100)
        price_df.to_csv('./output/ml_price_elasticity.csv', index=False)
        print(f"✓ Analyzed price elasticity for {len(price_df):,} products")
        print(f"  Saved to: ml_price_elasticity.csv\n")

except Exception as e:
    print(f"Note: Price elasticity analysis requires additional data\n")

# ================================================================
# SUMMARY REPORT
# ================================================================

print("="*80)
print("MACHINE LEARNING MODELS - SUMMARY")
print("="*80 + "\n")

ml_files = [
    ('ml_demand_forecast_30day.csv', 'Sales forecast - next 30 days'),
    ('ml_high_risk_customers.csv', 'Churn risk analysis - top 100 at-risk customers'),
    ('ml_churn_feature_importance.csv', 'Feature importance for churn prediction'),
    ('ml_product_recommendations.csv', 'Cross-sell and upsell recommendations'),
    ('ml_price_elasticity.csv', 'Price optimization insights')
]

print("Generated ML model outputs:")
for filename, description in ml_files:
    try:
        if pd.read_csv(f'./output/{filename}', nrows=1).shape[0] > 0:
            print(f"  ✓ {filename}")
            print(f"    └─ {description}")
    except:
        pass

print("\n📊 Business Impact:")
print("  • Forecast next 30 days of revenue with ML models")
print("  • Identify 1000s of customers at churn risk")
print("  • Recommend products to increase AOV (Average Order Value)")
print("  • Optimize prices based on demand elasticity")

print("\n🎯 Next Steps:")
print("  1. Integrate predictions in dashboard")
print("  2. Set up automated model retraining (weekly)")
print("  3. Create business alerts for high-risk customers")
print("  4. A/B test price recommendations")

print("\n" + "="*80 + "\n")
