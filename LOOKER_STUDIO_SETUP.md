# Google Looker Studio BI Setup Guide

A step-by-step guide to create professional dashboards with your Retail Analytics data.

---

## 📋 Table of Contents
1. Data Preparation
2. Looker Studio Setup
3. Dashboard Configuration
4. Advanced Features
5. Sharing & Collaboration

---

## Step 1: Data Preparation

### Google Cloud Storage Setup
```bash
# 1. Create Google Cloud account (free tier available)
# Go to: https://console.cloud.google.com/

# 2. Create a storage bucket
gsutil mb gs://retail-analytics-data

# 3. Upload CSV files
gsutil -m cp output/*.csv gs://retail-analytics-data/
gsutil -m cp output/summary_metrics.json gs://retail-analytics-data/

# 4. Make files publicly readable
gsutil iam ch serviceAccount:sa@project.iam.gserviceaccount.com:objectViewer gs://retail-analytics-data
```

### Alternative: Google Sheets Import
```
1. Go to: https://sheets.google.com
2. Create new spreadsheet
3. File > Import > Upload
4. Select daily_sales.csv, summary_metrics.json, etc.
5. Create separate sheets for each file
6. Share folder with Looker Studio
```

---

## Step 2: Create Looker Studio Dashboards

### Dashboard 1: Sales Overview Dashboard

#### Setup
```
1. Go to: https://looker.studio
2. Click "Create" > "Report"
3. Name: "Sales Overview Dashboard"
4. Click "Create"
```

#### Add Data Source
```
1. Click "Data" tab
2. Click "Add a data source"
3. Select "Google Sheets" or "Google Cloud Storage"
4. Select your daily_sales.csv file
5. Click "Create"
```

#### Add Charts

**Chart 1: Daily Revenue Trend**
- Type: Time series chart
- Dimension: Date (date_only)
- Metric: Sum of daily_revenue
- Date range: Last 2 years
- Title: "Daily Sales Trend"

**Chart 2: Revenue by Region**
- Type: Bar chart
- Dimension: Region
- Metric: Sum of revenue
- Sort: Descending
- Title: "Sales by Region"

**Chart 3: Product Category Performance**
- Type: Table
- Dimensions: Category, Product ID
- Metrics: Revenue, Units Sold, Profit Margin
- Sort: Revenue (descending)
- Show top 20 products
- Title: "Top Products by Category"

**Chart 4: Daily Transactions**
- Type: Scorecard
- Metric: Count of transactions
- Format: Number with commas
- Title: "Total Transactions"

**Chart 5: Average Transaction Value**
- Type: Scorecard
- Metric: Average of unit_price
- Format: Currency
- Title: "Avg Transaction Value"

---

### Dashboard 2: Customer Analytics Dashboard

#### Charts

**Chart 1: Customer Segments (Pie)**
- Data Source: customer_segments.csv
- Type: Pie chart
- Dimension: Segment (VIP, Loyal, At-Risk, Inactive)
- Metric: Count of customers
- Title: "Customer Segmentation"

**Chart 2: Revenue by Customer Segment**
- Type: Bar chart
- Dimension: Segment
- Metric: Sum of revenue
- Comparison: Transaction count
- Title: "Segment Performance"

**Chart 3: Customer Lifetime Value Distribution**
- Data Source: customer_lifetime_value.csv
- Type: Histogram
- Dimension: CLV_amount
- Title: "CLV Distribution"

**Chart 4: Churn Risk Analysis**
- Data Source: ml_high_risk_customers.csv
- Type: Table
- Columns: customer_id, churn_probability, recency, monetary
- Filter: churn_probability > 0.5
- Title: "High-Risk Customers"

---

### Dashboard 3: Inventory & Operations Dashboard

#### Charts

**Chart 1: Inventory Status**
- Data Source: inventory_analysis.csv
- Type: Gauge chart
- Metric: Inventory turnover rate
- Min: 0, Max: 100
- Title: "Inventory Health"

**Chart 2: Stock Levels by Category**
- Type: Stacked bar chart
- Dimension: Category
- Metrics: Critical, Low, Adequate
- Title: "Inventory Status by Category"

**Chart 3: Store Performance Comparison**
- Data Source: store_performance_analysis.csv
- Type: Table
- Columns: store_id, revenue, transactions, profit_margin
- Sort: Revenue (descending)
- Show top 30 stores
- Title: "Store Performance Ranking"

---

### Dashboard 4: Predictive Analytics Dashboard

#### Charts

**Chart 1: Sales Forecast (30-Day)**
- Data Source: ml_demand_forecast_30day.csv
- Type: Time series chart
- X-axis: Date
- Y-axis: predicted_revenue
- Add trendline
- Title: "30-Day Revenue Forecast"

**Chart 2: Forecast Accuracy**
- Type: Scorecard
- Metric: Average forecast error
- Format: Percentage
- Refresh: Daily
- Title: "Forecast Confidence"

**Chart 3: Demand by Product**
- Type: Table
- Data: Top products with forecasted demand
- Allow sorting/filtering by category
- Title: "Demand Forecast by Product"

**Chart 4: Price Elasticity Recommendations**
- Data Source: ml_price_elasticity.csv
- Type: Table
- Columns: product_id, elasticity_score, optimal_price_change
- Filter: elasticity > 0.5 (Price increase recommended)
- Title: "Price Optimization Opportunities"

---

### Dashboard 5: Sentiment & Reviews Dashboard

#### Charts

**Chart 1: Overall Sentiment Score**
- Data Source: reviews_with_sentiment.csv
- Type: Gauge
- Metric: Average vader_compound (or textblob_polarity)
- Min: -1, Max: 1
- Green: >0.3, Yellow: -0.3 to 0.3, Red: <-0.3
- Title: "Customer Sentiment Score"

**Chart 2: Sentiment Distribution**
- Type: Pie chart
- Dimension: vader_sentiment (Positive/Negative/Neutral)
- Metric: Count of reviews
- Title: "Review Distribution"

**Chart 3: Product Sentiment Heat Map**
- Data Source: product_sentiment_analysis.csv
- Type: Table
- Columns: product_id, avg_sentiment_score, positive_percentage, review_count
- Color code: Green (high sentiment), Red (low sentiment)
- Title: "Product Sentiment Analysis"

**Chart 4: Sentiment Trends Over Time**
- Data Source: monthly_sentiment_trends.csv
- Type: Time series chart
- X-axis: Month
- Y-axis: Average sentiment
- Title: "Customer Sentiment Trend"

---

## Step 3: Interactive Features

### Add Filters

**Date Range Filter**
```
Control: Date range picker
Applied to: All charts with date dimension
Default: Last 90 days
```

**Region Filter**
```
Control: List selector
Applied to: Regional charts
Allow multiple selections
```

**Product Category Filter**
```
Control: Dropdown
Options: Electronics, Clothing, Home & Garden, etc.
Applied to: Product-related charts
```

**Segment Filter**
```
Control: List selector
Options: VIP, Loyal, At-Risk, Inactive
Applied to: Customer analytics charts
```

### Add Interactivity

**Click-through Navigation**
- Click on region → drill down to store performance
- Click on product → show product details and sentiment
- Click on customer segment → list all customers in segment

**Custom Metrics**
```
Create Field:
- Profit Margin % = (profit / revenue) * 100
- Customer Lifetime Value = monetary / frequency
- Churn Risk Score = recency_days / avg_days_between_purchases
```

---

## Step 4: Advanced Dashboard Features

### Data Exploration

**Pivot Table**
```
Rows: Category, Product ID
Columns: Month
Values: Revenue, Units Sold
Allows: Drill-down, expand/collapse
```

**Scatter Plot: Price vs Quantity Sold**
```
X-axis: unit_price
Y-axis: quantity_sold
Bubble size: revenue
Color: category
Hover: Shows product details
```

### Real-Time Updates

**Schedule Data Refresh**
1. In Looker Studio: Report settings
2. Data source refresh:
   - Google Sheets: Automatic (5-30 minutes)
   - CSV: Set up Cloud Function for daily upload
   - MongoDB: Use MongoDB Atlas Charts integration

**Automated Alerts**
```
Create alert for:
- Revenue < $10M per day
- Churn risk customers > 5000
- Low inventory items > 500
- New forecast anomalies detected
```

---

## Step 5: Data Connectors Setup

### MongoDB Atlas Connection
```javascript
// Set up MongoDB Charts (within Atlas)

// 1. Create datasource in Charts
POST /api/public/v1.0/groups/{groupId}/charts

// 2. Configure aggregation pipeline
[
  {$match: {date: {$gte: new Date("2024-01-01")}}},
  {$group: {
    _id: "$date",
    revenue: {$sum: "$total_amount"},
    transactions: {$sum: 1}
  }},
  {$sort: {_id: -1}}
]

// 3. Embed in Looker Studio via iframe
<iframe src="https://charts.mongodb.com/charts/v1/..." />
```

### PostgreSQL Connection
```sql
-- Create views optimized for BI
CREATE VIEW bi_daily_sales AS
SELECT 
    DATE(date) as sales_date,
    SUM(total_amount) as daily_revenue,
    COUNT(*) as transactions,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales
GROUP BY DATE(date);

-- Use BigQuery Connector to connect to PostgreSQL
CREATE OR REPLACE EXTERNAL DATA CONNECTION 'postgres_connection'
OPTIONS (
  connector = 'postgres',
  host = 'your-postgres-host',
  database = 'retail_analytics',
  user = 'reader_user'
);
```

---

## Step 6: Sharing & Collaboration

### Share Dashboard

**Public Link**
1. Click "Share" button
2. Change to "Anyone with the link"
3. Copy shareable URL
4. Send to stakeholders

**Organization Sharing**
1. Share with specific users/groups
2. Set permissions: Viewer, Editor, Owner
3. Allow collaborators to add insights

**Embedded in Website**
```html
<iframe 
  width="100%" height="600"
  src="https://looker.studio/embed/reporting/YOUR_REPORT_ID/page/YOUR_PAGE_ID"
  allowFullScreen>
</iframe>
```

### Scheduled Reports
```
1. Click "Share" > "Schedule email"
2. Recipients: Enter email addresses
3. Frequency: Daily, Weekly, Monthly
4. Time: 8:00 AM
5. Recipients receive PDF snapshot
```

---

## Step 7: Looker Studio Best Practices

### Design Principles
- **Hierarchy**: Most important KPIs at top
- **Color**: Green=Good, Yellow=Warning, Red=Alert
- **Simplicity**: One insight per chart
- **Consistency**: Same colors across all dashboards
- **Mobile**: Test on mobile (70% of viewers use mobile)

### Performance Optimization
```
Slow Dashboard? 
1. Reduce date range
2. Limit table rows to 1000
3. Use filters instead of raw data
4. Aggregate data before visualization
5. Use Looker Studio data uploads instead of sheets
```

### Query Optimization for BigQuery
```sql
-- GOOD: Aggregated
SELECT DATE(date) as day, SUM(total_amount) as revenue
FROM sales
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
GROUP BY DATE(date)

-- AVOID: Full scan
SELECT * FROM sales WHERE year = 2024  -- Scans entire table!
```

---

## Example: Complete Morning Executive Dashboard

**Single Page Dashboard with 5 Key Charts**:
1. **KPI Card Row** (top): Total Revenue YTD, Growth%, Customer Count, Profit
2. **Main Chart** (middle-left): Sales Trend (interactive date slider)
3. **Forecast Chart** (middle-right): 30-Day Outlook
4. **Segment Donuts** (bottom-left): Customer segments
5. **Risk Table** (bottom-right): Top 10 churn-risk customers

**Load Time**: <3 seconds  
**Update**: Daily at 7 AM EST  
**Recipients**: 50 executives/analysts  

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard loads slow | Reduce data range, use aggregated data |
| Data not updating | Check data source refresh settings |
| Chart type not available | Use table with conditional formatting |
| Connector fails | Verify credentials, check firewall/VPN |
| Users can't see data | Share data source + report, check permissions |

---

## 🎓 Learning Resources

- Looker Studio Help: https://support.google.com/looker-studio
- Google Analytics Academy: https://analytics.google.com/analytics/academy/
- BigQuery Tutorials: https://cloud.google.com/bigquery/docs
- Dashboard Design Best Practices: https://www.interaction-design.org/

---

**Last Updated**: March 2, 2026  
**Estimated Setup Time**: 2-4 hours  
**Difficulty Level**: Intermediate

