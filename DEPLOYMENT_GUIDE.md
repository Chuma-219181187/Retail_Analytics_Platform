# Deployment Guide - Retail Analytics Platform

## 📦 Production Deployment Options

This document covers deployment scenarios from local development to enterprise cloud platforms.

---

## Option 1: Local Development (Current Setup)

### Best For
- Learning and testing
- Development environment
- Small-scale analytics (<100K records)

### Prerequisites
```
- Python 3.8+
- 4GB RAM minimum
- 2GB free disk space
```

### Setup Steps
```bash
# 1. Clone repository (when in GitHub)
git clone https://github.com/yourusername/retail-analytics-platform.git
cd retail-analytics-platform

# 2. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
pip install scikit-learn statsmodels

# 4. Run pipeline
python data_generation.py
python analytics_engine.py
python spark_data_pipeline.py
python ml_models.py
python sentiment_analysis.py

# 5. Start dashboard
# Open dashboard.html in web browser
```

### Limitations
- Single machine processing
- No distributed computing
- Manual scheduling required
- Limited scalability beyond 1M records

---

## Option 2: Databricks (Recommended for Spark)

### Best For
- Medium to large datasets (10M - 1B records)
- Team collaboration
- Production ML pipelines
- Auto-scaling requirements

### Cost
- **Databricks Community Edition**: FREE
- **Databricks Standard**: $0.10 per DBU (compute unit)
- Typical cost: $100-500/month for medium workloads

### Setup Steps

#### Step 1: Create Databricks Account
1. Go to: https://www.databricks.com/product/community-edition
2. Sign up with email
3. Create a workspace
4. No credit card required for community edition

#### Step 2: Create Databricks Cluster
```
1. Click "Create Cluster"
2. Name: retail_analytics
3. Cluster Type: All-purpose
4. Databricks Runtime: 14.0+ (with Scala 2.12)
5. Worker Type: i3.xlarge (or smaller for testing)
6. Number of Workers: 2-4
7. Click "Create Cluster"
```

#### Step 3: Upload Data Files
```python
# In Databricks Notebook
%fs mkdirs dbfs:/data/retail_analytics/

# Upload CSV files
# Use Databricks UI or CLI
dbfs cp --recursive data/ dbfs:/data/retail_analytics/
```

#### Step 4: Run Spark Pipeline
Create a new notebook in Databricks:

```python
# Notebook: 01_data_processing

%run /Workspace/Shared/spark_data_pipeline

# Spark will automatically scale across workers
# 500K rows processed in <1 minute on 4-node cluster
```

#### Step 5: Schedule Jobs
```
1. Create Job: "retail_analytics_daily"
2. Type: Notebook
3. Notebook path: /Workspace/Shared/spark_data_pipeline
4. Schedule: Daily at 2:00 AM
5. Alerts: Email on failure
6. Timeout: 30 minutes
```

#### Step 6: Store Results
```python
# Save results to Delta Lake
df_daily_sales.write.mode("overwrite").delta("dbfs:/output/daily_sales")
df_customer_segments.write.mode("overwrite").delta("dbfs:/output/customer_segments")

# Or export to cloud storage
df_forecasts.write.option("header", "true").csv("s3://mybucket/output/forecasts/")
```

---

## Option 3: Azure Synapse (Enterprise)

### Best For
- Enterprise data warehouse
- Complex queries
- Integration with Azure ecosystem
- Data governance requirements

### Cost
- SQL On-Demand: $6 per TB queried
- Provisioned Pool: $2.55-3.06 per DWU per hour
- Typical cost: $2,000-10,000/month

### Setup Steps

#### Step 1: Create Azure Synapse Workspace
```bash
# Using Azure CLI
az group create --name retail-analytics --location eastus

az synapse workspace create \
  --resource-group retail-analytics \
  --name retail-analytics-ws \
  --storage-account mystorageaccount \
  --file-system dataLake \
  --sql-admin-login sqladmin \
  --sql-admin-login-password Password123!
```

#### Step 2: Create SQL Pool
```bash
az synapse sql pool create \
  --resource-group retail-analytics \
  --workspace-name retail-analytics-ws \
  --name analyticspool \
  --performance-level "DW1000c"
```

#### Step 3: Load Data
```sql
-- Copy data to SQL Pool
CREATE EXTERNAL TABLE sales
WITH (
    DATA_SOURCE = DataLakeSource,
    LOCATION = 'sales.csv',
    FILE_FORMAT = CSVFormat
)
AS SELECT * FROM OPENROWSET(
    BULK 'sales.csv',
    DATA_SOURCE = 'DataLakeSource',
    FORMAT = 'CSV',
    FIELDQUOTE = '"',
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n'
) AS rows;
```

#### Step 4: Create Views for BI
```sql
CREATE VIEW daily_sales_view AS
SELECT 
    CAST(date AS DATE) as sales_date,
    SUM(total_amount) as daily_revenue,
    COUNT(*) as transaction_count
FROM sales
GROUP BY CAST(date AS DATE)
ORDER BY sales_date DESC;
```

---

## Option 4: AWS EMR (Elastic MapReduce)

### Best For
- AWS-native deployments
- Hadoop/Spark jobs
- Cost-sensitive large-scale processing
- Batch processing workflows

### Cost
- Cluster: ~$0.30-1.50/hour per instance
- Typical cost: $100-300/month for medium cluster

### Setup Steps

```bash
# 1. Create EMR cluster using AWS CLI
aws emr create-cluster \
  --name "retail-analytics" \
  --release-label emr-6.14.0 \
  --applications Name=Spark Name=Hive \
  --instance-type m6i.xlarge \
  --instance-count 3 \
  --ec2-keyname my-key-pair \
  --log-uri s3://my-bucket/logs/

# 2. SSH into master node
ssh -i my-key-pair.pem hadoop@<master-public-dns>

# 3. Upload scripts
aws s3 cp spark_data_pipeline.py s3://my-bucket/scripts/

# 4. Run Spark job
spark-submit \
  --num-executors 4 \
  --executor-cores 2 \
  --executor-memory 4g \
  s3://my-bucket/scripts/spark_data_pipeline.py

# 5. Export results
hadoop fs -copyToLocal /output/results s3://my-bucket/output/
```

---

## Option 5: Google BigQuery (Serverless)

### Best For
- SQL-focused analytics
- Serverless architecture
- Pay-per-query model
- Real-time streaming

### Cost
- Analysis: $6.25 per TB queried
- Storage: $0.02 per GB/month
- Typical cost: $50-500/month

### Setup Steps

```python
# 1. Install BigQuery client
pip install google-cloud-bigquery

# 2. Authenticate
from google.cloud import bigquery
client = bigquery.Client(project='my-project')

# 3. Create dataset
dataset = client.create_dataset('retail_analytics')

# 4. Load CSV to BigQuery
job_config = bigquery.LoadJobConfig(
    skip_leading_rows=1,
    autodetect=True,
    source_format=bigquery.SourceFormat.CSV,
)

table_id = 'my-project.retail_analytics.sales'
job = client.load_table_from_uri(
    'gs://my-bucket/sales.csv',
    table_id,
    job_config=job_config
)

# 5. Run SQL analytics
query = """
    SELECT 
        DATE(date) as sales_date,
        SUM(total_amount) as daily_revenue
    FROM `my-project.retail_analytics.sales`
    GROUP BY sales_date
    ORDER BY sales_date DESC
"""

results = client.query(query).result()
```

---

## Option 6: Kubernetes (Container Deployment)

### Best For
- Microservices architecture
- High availability requirements
- Auto-scaling needs
- On-premises or hybrid cloud

### Prerequisites
- Docker installed
- Kubernetes cluster (AWS EKS, Azure AKS, GCP GKE, or on-prem)
- kubectl CLI

### Setup Steps

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install scikit-learn statsmodels

COPY . .

CMD ["python", "analytics_engine.py"]
```

#### Step 2: Build and Push Image
```bash
docker build -t retail-analytics:1.0 .
docker tag retail-analytics:1.0 myregistry.azurecr.io/retail-analytics:1.0
docker push myregistry.azurecr.io/retail-analytics:1.0
```

#### Step 3: Create Kubernetes Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retail-analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: retail-analytics
  template:
    metadata:
      labels:
        app: retail-analytics
    spec:
      containers:
      - name: analytics
        image: myregistry.azurecr.io/retail-analytics:1.0
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: uri
```

#### Step 4: Deploy to Kubernetes
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml  # Expose service
kubectl logs -f deployment/retail-analytics
```

---

## 🔄 CI/CD Pipeline Setup (GitHub Actions)

### Automated Workflow
```yaml
# .github/workflows/analytics-pipeline.yml

name: Retail Analytics Pipeline

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM
  workflow_dispatch:

jobs:
  analytics:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install scikit-learn statsmodels
    
    - name: Run data generation
      run: python data_generation.py
    
    - name: Run analytics
      run: python analytics_engine.py
    
    - name: Run ML models
      run: python ml_models.py
    
    - name: Upload results to S3
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        aws s3 sync output/ s3://my-bucket/output/
    
    - name: Notify on failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        status: ${{ job.status }}
```

---

## 📊 Monitoring & Alerting

### Application Monitoring
```python
# Real-time monitoring
from prometheus_client import Counter, Histogram

# Track metrics
pipeline_duration = Histogram('pipeline_duration_seconds', 'Pipeline execution time')
data_records_processed = Counter('records_processed', 'Number of records processed')

@pipeline_duration.time()
def run_pipeline():
    # Your code here
    pass
```

### Log Aggregation
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **DataDog**: $15/host/month
- **New Relic**: $0.50/GB/day
- **Azure Monitor**: Integrated with Azure services

### Alerts
```
- Daily forecast available: ✅
- ML model accuracy <85%: ⚠️ Alert
- Data freshness >24 hours: ⚠️ Alert
- Pipeline duration >1 hour: ⚠️ Alert
- Churn risk customers >5000: ℹ️ Notify
```

---

## 🔐 Security Checklist

- [ ] Encrypt data in transit (TLS 1.3)
- [ ] Encrypt data at rest (AES-256)
- [ ] Use environment variables for secrets
- [ ] Enable audit logging
- [ ] Implement role-based access control (RBAC)
- [ ] Regular security scans (OWASP Top 10)
- [ ] Backup and disaster recovery plan
- [ ] Comply with GDPR/CCPA if handling PII

---

## 📈 Scaling Guidelines

**Vertical Scaling** (increase machine size):
- Cost increase: 3-5x for 10x capacity
- Simplicity: High
- Best for: <100M records

**Horizontal Scaling** (add more machines):
- Cost: Linear
- Complexity: High
- Best for: >1B records

**Hybrid Approach**:
- Use larger machines for hot data
- Archive cold data to cheaper storage
- Implement caching layer
- Use columnar formats (Parquet, ORC)

---

## 💰 Cost Optimization

1. **Spot/Preemptible Instances**: 70% cost savings (AWS, GCP)
2. **Reserved Capacity**: 40% savings (Databricks, Azure)
3. **Data Compression**: gzip (50%), snappy (20-30%)
4. **Columnar Storage**: Parquet (10x smaller than CSV)
5. **Incremental Loads**: Only process new data
6. **Query Caching**: Reduce redundant computations

**Estimated Monthly Costs**:
- Local Development: $0
- Databricks: $100-500
- Azure Synapse: $2,000-10,000
- AWS EMR: $100-300
- Google BigQuery: $50-500

---

## 📞 Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| Slow data load | Use parquet/columnar format |
| Memory errors | Increase cluster size or stream data |
| Model training slow | Enable GPU support |
| Database connection issues | Check VPC/security groups |
| Cost overruns | Implement auto-shutdown, use spot instances |

---

**Last Updated**: March 2, 2026

