"""
RETAIL ANALYTICS PLATFORM - Phase 8: Sentiment Analysis & NLP
==============================================================

Sentiment analysis on customer reviews using:
- VADER sentiment analysis (rule-based)
- TextBlob (simplified NLP)
- Optional: Transformers for advanced NLP

Installation:
    pip install nltk textblob vaderSentiment

Run:
    python sentiment_analysis.py
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("RETAIL ANALYTICS - SENTIMENT ANALYSIS & NLP")
print("="*80 + "\n")

# ================================================================
# SETUP
# ================================================================

print("Setting up NLP tools...")

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    import nltk
    
    # Download required NLTK data
    try:
        nltk.data.find('vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    
    vader = SentimentIntensityAnalyzer()
    print("✓ VADER sentiment analyzer loaded")
except:
    print("⚠️  VADER not available, will use TextBlob")
    vader = None

try:
    from textblob import TextBlob
    print("✓ TextBlob loaded")
except ImportError:
    print("⚠️  Installing textblob: pip install textblob")
    TextBlob = None

# ================================================================
# LOAD REVIEW DATA
# ================================================================

print("\nLoading review data...")

reviews = []
try:
    with open('./data/reviews.json', 'r') as f:
        for line in f:
            reviews.append(json.loads(line))
    
    df_reviews = pd.DataFrame(reviews)
    print(f"✓ Loaded {len(df_reviews):,} customer reviews")
except Exception as e:
    print(f"✗ Could not load reviews.json: {e}")
    print("Creating sample review data...")
    
    # Create synthetic reviews for demo
    sample_reviews = [
        "Excellent product, highly recommend!",
        "Great quality and fast delivery",
        "Amazing value for money",
        "Very satisfied with this purchase",
        "Perfect! Exactly as described",
        "Best purchase ever!",
        "Exceeded my expectations",
        "Poor quality, not as advertised",
        "Arrived damaged",
        "Terrible customer service",
        "Waste of money",
        "Stopped working after a week",
        "Not worth the price",
        "It's okay, nothing special",
        "Average product, average price",
        "Does what it's supposed to do",
        "Decent but could be better"
    ]
    
    df_reviews = pd.DataFrame({
        'review_id': [f'REV_{i:07d}' for i in range(len(sample_reviews) * 100)],
        'product_id': np.random.choice(['PROD_000001', 'PROD_000002', 'PROD_000003'], len(sample_reviews) * 100),
        'customer_id': [f'CUST_{i%50000:06d}' for i in range(len(sample_reviews) * 100)],
        'rating': np.random.choice([1, 2, 3, 4, 5], len(sample_reviews) * 100),
        'review_text': np.random.choice(sample_reviews, len(sample_reviews) * 100),
        'review_date': pd.date_range(start='2024-01-01', periods=len(sample_reviews) * 100, freq='D').astype(str),
        'helpful_count': np.random.randint(0, 100, len(sample_reviews) * 100)
    })

print(f"Total reviews: {len(df_reviews):,}\n")

# ================================================================
# SENTIMENT ANALYSIS
# ================================================================

print("Phase 1: Performing Sentiment Analysis")
print("-" * 70)

sentiments = []

for idx, row in df_reviews.iterrows():
    review_text = str(row['review_text'])
    
    sentiment_data = {
        'review_id': row['review_id'],
        'product_id': row['product_id'],
        'customer_id': row['customer_id'],
        'rating': row['rating'],
        'review_text': review_text,
        'review_date': row['review_date'],
        'helpful_count': row['helpful_count']
    }
    
    # Method 1: VADER Sentiment Analysis
    if vader:
        try:
            scores = vader.polarity_scores(review_text)
            sentiment_data['vader_positive'] = round(scores['pos'], 4)
            sentiment_data['vader_negative'] = round(scores['neg'], 4)
            sentiment_data['vader_neutral'] = round(scores['neu'], 4)
            sentiment_data['vader_compound'] = round(scores['compound'], 4)
            
            # Classify
            if scores['compound'] >= 0.05:
                sentiment_data['vader_sentiment'] = 'Positive'
            elif scores['compound'] <= -0.05:
                sentiment_data['vader_sentiment'] = 'Negative'
            else:
                sentiment_data['vader_sentiment'] = 'Neutral'
        except:
            sentiment_data['vader_compound'] = 0
            sentiment_data['vader_sentiment'] = 'Unknown'
    
    # Method 2: TextBlob Sentiment
    if TextBlob:
        try:
            blob = TextBlob(review_text)
            sentiment_data['textblob_polarity'] = round(blob.sentiment.polarity, 4)
            sentiment_data['textblob_subjectivity'] = round(blob.sentiment.subjectivity, 4)
            
            if blob.sentiment.polarity > 0.1:
                sentiment_data['textblob_sentiment'] = 'Positive'
            elif blob.sentiment.polarity < -0.1:
                sentiment_data['textblob_sentiment'] = 'Negative'
            else:
                sentiment_data['textblob_sentiment'] = 'Neutral'
        except:
            sentiment_data['textblob_polarity'] = 0
            sentiment_data['textblob_sentiment'] = 'Unknown'
    
    sentiments.append(sentiment_data)
    
    if (idx + 1) % 5000 == 0:
        print(f"  Processed {idx + 1:,} reviews...")

df_sentiments = pd.DataFrame(sentiments)
df_sentiments.to_csv('./output/reviews_with_sentiment.csv', index=False)

print(f"✓ Sentiment analysis complete")
print(f"  Saved to: reviews_with_sentiment.csv\n")

# ================================================================
# SENTIMENT DISTRIBUTION
# ================================================================

print("Phase 2: Sentiment Distribution Analysis")
print("-" * 70)

if 'vader_sentiment' in df_sentiments.columns:
    sentiment_dist = df_sentiments['vader_sentiment'].value_counts()
    print("\nVADER Sentiment Distribution:")
    for sentiment, count in sentiment_dist.items():
        percentage = (count / len(df_sentiments) * 100)
        print(f"  {sentiment:10} : {count:6,} ({percentage:5.2f}%)")
    
    # Sentiment by rating
    print("\nSentiment vs Star Rating:")
    sentiment_by_rating = pd.crosstab(df_sentiments['rating'], df_sentiments['vader_sentiment'])
    print(sentiment_by_rating)
    sentiment_by_rating.to_csv('./output/sentiment_by_rating.csv')

# ================================================================
# PRODUCT SENTIMENT ANALYSIS
# ================================================================

print("\n\nPhase 3: Product-Level Sentiment Analysis")
print("-" * 70)

product_sentiment = df_sentiments.groupby('product_id').agg({
    'review_id': 'count',
    'rating': 'mean',
    'helpful_count': 'sum'
}).round(2)
product_sentiment.columns = ['review_count', 'avg_rating', 'total_helpful']

if 'vader_compound' in df_sentiments.columns:
    product_sentiment['avg_sentiment_score'] = df_sentiments.groupby('product_id')['vader_compound'].mean().round(4)

if 'vader_sentiment' in df_sentiments.columns:
    # Count positive reviews
    positive_count = df_sentiments[df_sentiments['vader_sentiment'] == 'Positive'].groupby('product_id').size()
    product_sentiment['positive_reviews'] = positive_count
    product_sentiment['positive_reviews'] = product_sentiment['positive_reviews'].fillna(0).astype(int)
    product_sentiment['positive_percentage'] = (product_sentiment['positive_reviews'] / product_sentiment['review_count'] * 100).round(2)

product_sentiment = product_sentiment.sort_values('review_count', ascending=False).head(100)
product_sentiment.to_csv('./output/product_sentiment_analysis.csv')

print(f"✓ Analyzed sentiment for {len(product_sentiment):,} products")
print(f"  Saved to: product_sentiment_analysis.csv")

# Show top and bottom products
print("\nTop 5 products by sentiment:")
if 'avg_sentiment_score' in product_sentiment.columns:
    top_products = product_sentiment.sort_values('avg_sentiment_score', ascending=False).head(5)
    for product_id, row in top_products.iterrows():
        print(f"  {product_id}: {row['avg_sentiment_score']:.4f} ({int(row['review_count'])} reviews)")

# ================================================================
# CUSTOMER SENTIMENT ANALYSIS
# ================================================================

print("\n\nPhase 4: Customer Sentiment Analysis")
print("-" * 70)

customer_sentiment = df_sentiments.groupby('customer_id').agg({
    'review_id': 'count',
    'rating': 'mean',
    'helpful_count': 'sum'
}).round(2)
customer_sentiment.columns = ['review_count', 'avg_rating', 'helpful_received']

if 'vader_compound' in df_sentiments.columns:
    customer_sentiment['avg_sentiment'] = df_sentiments.groupby('customer_id')['vader_compound'].mean().round(4)

if 'vader_sentiment' in df_sentiments.columns:
    negative_count = df_sentiments[df_sentiments['vader_sentiment'] == 'Negative'].groupby('customer_id').size()
    customer_sentiment['negative_review_count'] = negative_count.fillna(0).astype(int)
    customer_sentiment['negative_percentage'] = (customer_sentiment['negative_review_count'] / customer_sentiment['review_count'] * 100).round(2)

# Identify critics (always negative)
customer_sentiment = customer_sentiment.sort_values('review_count', ascending=False)

# Only create critic_customers if we have the negative_percentage column
if 'negative_percentage' in customer_sentiment.columns:
    critic_customers = customer_sentiment[customer_sentiment['negative_percentage'] > 50].head(50)
    
    if len(critic_customers) > 0:
        critic_customers.to_csv('./output/critic_customers.csv')
        print(f"✓ Identified {len(critic_customers):,} critic customers (>50% negative reviews)")
        print(f"  Top critics exported to: critic_customers.csv")
else:
    print("✓ Customer sentiment analysis completed")
    print(f"  Saved to: reviews_with_sentiment.csv")

# ================================================================
# TREND ANALYSIS
# ================================================================

print("\n\nPhase 5: Sentiment Trend Analysis")
print("-" * 70)

df_sentiments['review_date'] = pd.to_datetime(df_sentiments['review_date'])
df_sentiments['year_month'] = df_sentiments['review_date'].dt.to_period('M')

if 'vader_compound' in df_sentiments.columns:
    monthly_sentiment = df_sentiments.groupby('year_month').agg({
        'vader_compound': 'mean',
        'review_id': 'count',
        'rating': 'mean'
    }).round(4)
    monthly_sentiment.columns = ['avg_sentiment', 'review_count', 'avg_rating']
    monthly_sentiment.to_csv('./output/monthly_sentiment_trends.csv')
    
    print("✓ Monthly sentiment trends computed")
    print(f"  Saved to: monthly_sentiment_trends.csv")
    
    print("\nRecent sentiment trend (last 6 months):")
    recent_trend = monthly_sentiment.tail(6)
    for period, row in recent_trend.iterrows():
        print(f"  {period}: Sentiment {row['avg_sentiment']:+.4f}, Rating {row['avg_rating']:.2f}/5 ({int(row['review_count'])} reviews)")

# ================================================================
# KEY INSIGHTS
# ================================================================

print("\n\nKEY SENTIMENT INSIGHTS")
print("="*70)

if 'vader_sentiment' in df_sentiments.columns:
    pos_ratio = (df_sentiments['vader_sentiment'] == 'Positive').sum() / len(df_sentiments) * 100
    neg_ratio = (df_sentiments['vader_sentiment'] == 'Negative').sum() / len(df_sentiments) * 100
    
    print(f"\n📊 Overall Sentiment Score:")
    print(f"  Positive Reviews: {pos_ratio:.1f}%")
    print(f"  Negative Reviews: {neg_ratio:.1f}%")
    print(f"  Neutral Reviews:  {100-pos_ratio-neg_ratio:.1f}%")

print(f"\n📈 Customer Engagement:")
print(f"  Total Reviews: {len(df_sentiments):,}")
print(f"  Unique Customers: {df_sentiments['customer_id'].nunique():,}")
print(f"  Unique Products: {df_sentiments['product_id'].nunique():,}")
print(f"  Avg Reviews per Customer: {len(df_sentiments) / df_sentiments['customer_id'].nunique():.2f}")

print(f"\n🎯 Business Recommendations:")
if 'negative_percentage' in customer_sentiment.columns:
    print(f"  1. Address {len(critic_customers)} critic customers with targeted outreach")
else:
    print(f"  1. Monitor customer sentiment trends closely")
print(f"  2. Promote top-sentiment products in marketing")
print(f"  3. Implement quality improvements for negative-sentiment products")
print(f"  4. Engage power reviewers (high helpful count) for testimonials")

print("\n" + "="*80 + "\n")
