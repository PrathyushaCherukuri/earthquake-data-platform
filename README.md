# 🌍 Earthquake Analytics Platform on AWS

An end-to-end data engineering platform that ingests, processes, and analyzes earthquake data using both **streaming** and **batch** pipelines on AWS.

The platform supports **near real-time monitoring**, **historical analytics**, **alerts for significant earthquakes**, and **production-ready reliability patterns**.

---

## 🚀 Project Overview

Earthquake data from the USGS API is ingested in near real time and stored for long-term historical analysis.  
The solution combines **event-driven streaming** with **batch analytics**, enabling both live insights and trend analysis.

Key goals:
- Real-time earthquake monitoring
- Historical trend analysis
- Scalable, serverless AWS architecture
- Reliable ingestion with error handling and replay

---

## 📊 Data Source

- **USGS Earthquake API**
- Provides near real-time earthquake event data
- Limited historical retention → one-time backfill performed
- Ongoing streaming ingestion preserves full history in Amazon S3

---

## 🏗️ Architecture Overview

The platform follows a **streaming-first architecture** with batch analytics layered on top.

### Streaming Pipeline
- EventBridge schedules ingestion
- AWS Lambda polls USGS API
- Amazon Kinesis acts as event backbone
- Consumer Lambda processes events:
  - Writes latest state to DynamoDB
  - Stores raw and serving data in S3
  - Sends alerts via SNS
  - Routes noisy data to SQS DLQ

### Batch Pipeline
- AWS Glue processes historical data from S3
- Cleansing, deduplication, and enrichment applied
- Curated datasets optimized for analytics
- Data queried using Amazon Athena

---

## 🧱 Technology Stack

**Compute & Ingestion**
- AWS Lambda
- Amazon Kinesis
- Amazon EventBridge

**Storage & Analytics**
- Amazon S3
- AWS Glue
- Amazon Athena
- Amazon DynamoDB

**Visualization**
- Amazon QuickSight

**Monitoring & Reliability**
- Amazon CloudWatch
- Amazon SNS
- Amazon SQS (DLQ)

**Infrastructure & CI/CD**
- AWS CloudFormation
- AWS CodePipeline
- AWS CodeBuild

---

## 📈 Dashboards & Insights

- Earthquakes over time (event-based analysis)
- Magnitude distribution and severity trends
- Near real-time monitoring using ingestion timestamps
- Historical trend analysis using batch-processed data

---

## 🔔 Alerts & Error Handling

- SNS alerts triggered for high-magnitude earthquakes (≥ 4.5)
- Low-quality or noisy events routed to SQS Dead Letter Queue
- Replay mechanism supports safe reprocessing without data loss

---

## ⚙️ Infrastructure as Code & CI/CD

- All AWS resources provisioned using CloudFormation
- CI/CD pipeline implemented with CodePipeline and CodeBuild
- Git-driven deployments ensure reproducibility and consistency

---

## 🧠 Key Design Decisions

- Streaming-first ingestion with one-time historical backfill
- DynamoDB used only for latest-state access
- S3 acts as immutable system of record
- Clear separation between ingestion, processing, and serving layers

---

## 🚧 Challenges & Learnings

- Managing event time vs ingestion time for real-time dashboards
- Designing incremental processing without duplicates
- Balancing streaming and batch workloads
- Implementing reliable monitoring and replay mechanisms

---

## 🔮 Future Enhancements

- Geospatial visualizations for regional analysis
- Streaming data quality validation
- Dynamic alert thresholds based on regional activity
- Machine learning for seismic risk scoring and anomaly detection

---

## 📌 Conclusion

This project demonstrates a **production-oriented AWS data engineering solution** that combines real-time ingestion, batch analytics, monitoring, and automation using serverless services.

---

## 📬 Author

**Prathyusha Cherukuri**  
Data Engineer | AWS | Big Data | Streaming & Analytics
