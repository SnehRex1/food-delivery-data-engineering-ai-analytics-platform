# Food Delivery Data Engineering & AI Analytics Platform

> An end-to-end **Data Engineering + AI Analytics platform** for a food
> delivery business, built with **Amazon S3, Snowflake, dbt, Apache
> Airflow, Python, Google Gemini, RAG, and Streamlit**.

The platform ingests food-delivery CSV data into Amazon S3, loads it
into Snowflake, transforms it through a dbt-based analytical pipeline,
enriches customer reviews using Gemini, and exposes the data through
RAG-based review analysis and natural-language Text-to-SQL analytics.

------------------------------------------------------------------------

## Architecture

![Food Delivery Data Engineering & AI Analytics
Platform](docs/architecture.png)

### High-Level Architecture

``` text
CSV Data
   |
   v
Amazon S3
   |
   | COPY INTO
   v
Snowflake RAW
   |
   | dbt
   v
dbt STAGING
   |
   | dbt
   v
dbt MARTS
   |
   +----------------------+----------------------+
   |                      |                      |
   v                      v                      v
Business Analytics   Review AI Enrichment    AI Applications
                            |                      |
                         Gemini              +-----+-----+
                            |                |           |
                            v                v           v
                    AI.REVIEW_ENRICHED     RAG       Text-to-SQL
                            |                |           |
                           dbt              Gemini      Gemini
                            |                |           |
                            v                v           v
                    MART_REVIEW_INSIGHTS  Semantic   SQL + Safety
                                           Search       Check
                                                \         /
                                                 v       v
                                                   Snowflake
                                                      |
                                                      v
                                                  Streamlit
```

------------------------------------------------------------------------

# Project Overview

This project simulates a production-style data platform for a food
delivery business.

It handles both **structured business data** and **unstructured customer
reviews**.

### Structured Data

The platform supports analytics around:

-   Orders
-   Order items
-   Restaurants
-   Customers
-   Food
-   Cities
-   Payment methods
-   Revenue
-   Delivery performance
-   Cancellation rates

### Unstructured Data

Customer reviews are processed using **Google Gemini** to extract:

-   Sentiment label
-   Sentiment score
-   Review topic
-   Key issue

The enriched review data is then used for downstream analytics and
conversational review analysis.

------------------------------------------------------------------------

# Key Features

## Data Engineering

-   CSV-based food delivery datasets
-   Amazon S3 as the data lake
-   Snowflake as the cloud data warehouse
-   Snowflake external stage and `COPY INTO`
-   RAW -\> STAGING -\> MART architecture
-   dbt-based SQL transformations
-   Dimensional and fact modeling
-   Analytical marts
-   dbt data tests
-   dbt lineage and documentation

## Orchestration

-   Apache Airflow DAG
-   Automated RAW ingestion
-   dbt core build
-   Gemini review enrichment
-   AI-specific dbt build
-   Sequential task dependencies

## Generative AI

-   Google Gemini for review classification
-   Gemini embeddings for semantic search
-   RAG-based conversational review analysis
-   Gemini-powered Text-to-SQL
-   SQL safety validation
-   Natural-language access to Snowflake analytics

## Applications

-   Streamlit RAG review application
-   Streamlit Text-to-SQL analytics application
-   Generated SQL visibility
-   Query result tables
-   Analytical result presentation

------------------------------------------------------------------------

# Technology Stack

  Category           Technology
  ------------------ ------------------------
  Data Lake          Amazon S3
  Data Warehouse     Snowflake
  Transformation     dbt
  Orchestration      Apache Airflow
  Programming        Python
  AI / LLM           Google Gemini
  Embeddings         Gemini Embedding Model
  Vector Storage     Parquet
  Data Processing    Pandas, NumPy
  Applications       Streamlit
  Containerization   Docker
  SQL                Snowflake SQL
  Version Control    Git

------------------------------------------------------------------------

# Data Sources

The project contains seven source datasets:

``` text
data/
├── restaurants/
├── users/
├── food/
├── menu/
├── orders/
├── order_items/
└── reviews/
```

These CSV datasets are uploaded to Amazon S3 and organized into
corresponding folders.

------------------------------------------------------------------------

# End-to-End Data Flow

## 1. Data Ingestion

``` text
CSV Files
   |
   v
Amazon S3
   |
   v
Snowflake External Stage
   |
   v
COPY INTO
   |
   v
RAW Tables
```

The Snowflake RAW layer contains:

``` text
RAW.RESTAURANTS
RAW.USERS
RAW.FOOD
RAW.MENU
RAW.ORDERS
RAW.ORDER_ITEMS
RAW.REVIEWS
```

Example:

``` sql
COPY INTO RAW.RESTAURANTS
FROM @FD_RAW_STAGE/restaurant/
ON_ERROR = 'CONTINUE';
```

------------------------------------------------------------------------

# 2. Snowflake RAW Layer

The raw data is loaded into the `FOOD_DELIVERY.RAW` schema.

``` text
FOOD_DELIVERY
└── RAW
    ├── FOOD
    ├── MENU
    ├── ORDERS
    ├── ORDER_ITEMS
    ├── RESTAURANTS
    ├── REVIEWS
    └── USERS
```

The RAW layer preserves the ingested source data before dbt
transformations.

------------------------------------------------------------------------

# 3. dbt STAGING Layer

dbt transforms the RAW tables into cleaned and standardized staging
models.

``` text
RAW
 |
 v
STAGING
```

Models:

``` text
STG_FOOD
STG_MENU
STG_ORDERS
STG_ORDER_ITEMS
STG_RESTAURANTS
STG_REVIEWS
STG_USERS
```

The staging layer handles:

-   Column standardization
-   Type casting
-   Cleaning
-   Source normalization
-   Preparing data for analytical modeling

------------------------------------------------------------------------

# 4. dbt MARTS Layer

The cleaned staging data is transformed into analytical models.

## Dimensions

``` text
DIM_CUSTOMER
DIM_DATE
DIM_FOOD
DIM_RESTAURANTS
```

## Facts

``` text
FCT_ORDERS
FACT_ORDER_ITEMS
```

## Business Marts

``` text
MART_DAILY_CITY_REVENUE
MART_DELIVERY_SLA
MART_RESTAURANT_PERFORMANCE
```

These models provide business-ready datasets for analytical queries.

------------------------------------------------------------------------

# 5. AI Review Enrichment

Customer reviews are processed using Python and Gemini.

``` text
STG_REVIEWS
      |
      v
enrich_reviews.py
      |
      v
Google Gemini
      |
      +-- Sentiment Label
      +-- Sentiment Score
      +-- Topic
      +-- Key Issue
      |
      v
AI.REVIEW_ENRICHED
```

Example:

``` text
Review:
"Gravy spilled all over the bag."

Gemini:
sentiment_label = negative
sentiment_score = -0.8
topic           = packaging
key_issue       = gravy spilled in the bag
```

The enriched results are written to:

``` text
FOOD_DELIVERY.AI.REVIEW_ENRICHED
```

This keeps AI-enriched data separate from the core analytical schemas.

------------------------------------------------------------------------

# 6. AI dbt Model

The enriched review data is combined with review information through
dbt.

``` text
AI.REVIEW_ENRICHED
        |
        +------+
               |
STG_REVIEWS ---+
        |
        v
MART_REVIEW_INSIGHTS
```

`MART_REVIEW_INSIGHTS` provides:

-   City
-   Review topic
-   Sentiment
-   Number of reviews
-   Average sentiment score
-   Average star rating
-   Number of flagged issues

The model is tagged:

``` yaml
tags:
  - ai
```

Therefore it can be built independently:

``` bash
dbt build --select tag:ai
```

------------------------------------------------------------------------

# 7. RAG Chat Application

The RAG application provides conversational access to customer reviews.

``` text
Customer Reviews
       |
       v
Gemini Embeddings
       |
       v
review_embeddings.parquet
       |
       v
Cosine Similarity
       |
       v
Top-K Relevant Reviews
       |
       v
Gemini
       |
       v
Grounded Natural-Language Answer
```

For a question such as:

> What are the common complaints about delivery?

the application:

1.  Generates an embedding for the question.
2.  Compares it with review embeddings.
3.  Selects the most relevant reviews.
4.  Uses those reviews as context.
5.  Generates a grounded answer with Gemini.

------------------------------------------------------------------------

# 8. Text-to-SQL Application

The second AI application allows users to query Snowflake marts using
natural language.

``` text
User Question
      |
      v
Streamlit
      |
      v
Gemini
      |
      v
SQL Generation
      |
      v
Safety Validation
      |
      v
Snowflake MARTS
      |
      v
Pandas DataFrame
      |
      v
Streamlit Results
```

Example:

``` text
User:
Top 10 cities by GMV
```

Example generated SQL:

``` sql
SELECT
    city,
    SUM(gmv) AS total_gmv
FROM MART_DAILY_CITY_REVENUE
GROUP BY city
ORDER BY total_gmv DESC
LIMIT 10;
```

The generated SQL is displayed before execution.

------------------------------------------------------------------------

# SQL Safety

The Text-to-SQL application validates generated SQL before execution.

Read-oriented queries such as:

``` text
SELECT
WITH
```

are permitted.

Potentially destructive operations are rejected, including:

``` text
DROP
DELETE
TRUNCATE
ALTER
UPDATE
INSERT
CREATE
REPLACE
GRANT
REVOKE
```

This provides an additional guardrail between LLM-generated SQL and
Snowflake.

------------------------------------------------------------------------

# Orchestration with Airflow

The complete pipeline is orchestrated with Apache Airflow.

### DAG

``` text
food_delivery_batch
```

### Task Flow

``` text
reload_raw
     |
     v
dbt_build_core
     |
     v
enrich_reviews
     |
     v
dbt_build_ai
```

The DAG dependency is:

``` python
reload_raw >> dbt_build_core >> enrich_reviews >> dbt_build_ai
```

### Task Responsibilities

**`reload_raw`**

Loads the latest source data from S3 into Snowflake RAW.

**`dbt_build_core`**

Builds the core dbt staging and analytical models.

**`enrich_reviews`**

Runs `ai_layer/enrich_reviews.py` and sends reviews to Gemini for AI
enrichment.

**`dbt_build_ai`**

Builds AI-specific dbt models using:

``` bash
dbt build --select tag:ai
```

------------------------------------------------------------------------

# Snowflake Data Model

``` text
FOOD_DELIVERY
│
├── RAW
│   ├── FOOD
│   ├── MENU
│   ├── ORDERS
│   ├── ORDER_ITEMS
│   ├── RESTAURANTS
│   ├── REVIEWS
│   └── USERS
│
├── STAGING
│   ├── STG_FOOD
│   ├── STG_MENU
│   ├── STG_ORDERS
│   ├── STG_ORDER_ITEMS
│   ├── STG_RESTAURANTS
│   ├── STG_REVIEWS
│   └── STG_USERS
│
├── MARTS
│   ├── DIM_CUSTOMER
│   ├── DIM_DATE
│   ├── DIM_FOOD
│   ├── DIM_RESTAURANTS
│   ├── FACT_ORDER_ITEMS
│   ├── FCT_ORDERS
│   ├── MART_DAILY_CITY_REVENUE
│   ├── MART_DELIVERY_SLA
│   ├── MART_RESTAURANT_PERFORMANCE
│   └── MART_REVIEW_INSIGHTS
│
└── AI
    └── REVIEW_ENRICHED
```

------------------------------------------------------------------------

# dbt Lineage

``` text
RAW
 |
 +-- RAW.RESTAURANTS --> STG_RESTAURANTS --> DIM_RESTAURANTS
 |
 +-- RAW.USERS --------> STG_USERS --------> DIM_CUSTOMER
 |
 +-- RAW.FOOD ---------> STG_FOOD ---------> DIM_FOOD
 |
 +-- RAW.MENU ---------> STG_MENU
 |
 +-- RAW.ORDERS -------> STG_ORDERS -------> FCT_ORDERS
 |
 +-- RAW.ORDER_ITEMS --> STG_ORDER_ITEMS --> FACT_ORDER_ITEMS
 |
 +-- RAW.REVIEWS ------> STG_REVIEWS
                              |
                              v
                       Gemini Enrichment
                              |
                              v
                     AI.REVIEW_ENRICHED
                              |
                              v
                     MART_REVIEW_INSIGHTS
```

Business marts are derived from the core analytical models:

``` text
FCT_ORDERS
    |
    +--> MART_DAILY_CITY_REVENUE
    |
    +--> MART_RESTAURANT_PERFORMANCE
    |
    +--> MART_DELIVERY_SLA
```

------------------------------------------------------------------------

# Project Structure

``` text
food-delivery-data-engineering-ai-analytics-platform/
│
├── ai_layer/
│   ├── enrich_reviews.py
│   ├── rag_chat.py
│   ├── text_to_sql.py
│   └── review_embeddings.parquet
│
├── airflow/
│   ├── dags/
│   │   └── food_delivery_batch.py
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   └── .env
│
├── data/
│   ├── restaurants/
│   ├── users/
│   ├── food/
│   ├── menu/
│   ├── orders/
│   ├── order_items/
│   └── reviews/
│
├── food_delivery_dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── _sources.yml
│   │   │   ├── _staging.yml
│   │   │   ├── _ai_sources.yml
│   │   │   ├── stg_food.sql
│   │   │   ├── stg_menu.sql
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_restaurants.sql
│   │   │   ├── stg_reviews.sql
│   │   │   └── stg_users.sql
│   │   │
│   │   └── marts/
│   │       ├── _marts.yml
│   │       ├── dim_customer.sql
│   │       ├── dim_date.sql
│   │       ├── dim_food.sql
│   │       ├── dim_restaurants.sql
│   │       ├── fact_order_items.sql
│   │       ├── fct_orders.sql
│   │       ├── mart_daily_city_revenue.sql
│   │       ├── mart_delivery_sla.sql
│   │       ├── mart_restaurant_performance.sql
│   │       └── mart_review_insights.sql
│   │
│   ├── macros/
│   ├── seeds/
│   ├── snapshots/
│   ├── tests/
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── snowflake/
│   ├── 01_setup.sql
│   ├── 02_storage_integration.sql
│   ├── 03_stage_and_formats.sql
│   ├── 04_raw_tables.sql
│   └── 05_copy_into.sql
│
├── docs/
│   └── architecture.png
│
├── README.md
└── .gitignore
```

------------------------------------------------------------------------

# Running the Project

## 1. Start Airflow

From the `airflow` directory:

``` bash
docker compose up -d
```

Check the containers:

``` bash
docker compose ps
```

Expected services include:

``` text
postgres
airflow-init
scheduler
dag-processor
apiserver
```

------------------------------------------------------------------------

## 2. Open Airflow

Open:

``` text
http://localhost:8080
```

The main DAG is:

``` text
food_delivery_batch
```

Trigger the DAG from the Airflow UI.

------------------------------------------------------------------------

# Running dbt

Inside the Airflow scheduler container:

``` bash
docker compose exec scheduler /opt/airflow/dbt_venv/bin/dbt build --project-dir /opt/airflow/dbt/food_delivery_dbt --profiles-dir /opt/airflow/dbt/food_delivery_dbt
```

Check AI models:

``` bash
docker compose exec scheduler /opt/airflow/dbt_venv/bin/dbt ls --select tag:ai --project-dir /opt/airflow/dbt/food_delivery_dbt --profiles-dir /opt/airflow/dbt/food_delivery_dbt
```

Build only AI models:

``` bash
docker compose exec scheduler /opt/airflow/dbt_venv/bin/dbt build --select tag:ai --project-dir /opt/airflow/dbt/food_delivery_dbt --profiles-dir /opt/airflow/dbt/food_delivery_dbt
```

Expected AI model:

``` text
food_delivery_dbt.marts.mart_review_insights
```

------------------------------------------------------------------------

# Running AI Review Enrichment

Inside the scheduler container:

``` bash
docker compose exec scheduler python /opt/airflow/ai_layer/enrich_reviews.py
```

The script sends review text to Gemini and writes structured enrichment
results into:

``` text
FOOD_DELIVERY.AI.REVIEW_ENRICHED
```

------------------------------------------------------------------------

# Running the RAG Application

From the `ai_layer` directory:

``` bash
streamlit run rag_chat.py
```

Example question:

``` text
What are the most common complaints from customers?
```

The application retrieves semantically relevant reviews and uses Gemini
to generate a grounded answer.

------------------------------------------------------------------------

# Running the Text-to-SQL Application

From the `ai_layer` directory:

``` bash
streamlit run text_to_sql.py
```

Example questions:

``` text
Top 10 cities by GMV

Which cuisine has the most orders?

Average delivery time by city, worst first

What is the cancel rate by payment method?

Top 10 restaurants by revenue

Which food items generate the most revenue?
```

------------------------------------------------------------------------

# Example Analytics

### Revenue

``` text
Top 10 cities by GMV
```

### Restaurant Performance

``` text
Top 10 restaurants by revenue
```

### Delivery

``` text
Average delivery time by city, worst first
```

### Payments

``` text
What is the cancel rate by payment method?
```

### Food

``` text
Which food items generate the most revenue?
```

### Reviews

``` text
What are the most common complaints from customers?
```

------------------------------------------------------------------------

# AI Design

The project separates the three AI capabilities:

``` text
                    AI LAYER
                       |
       +---------------+----------------+
       |               |                |
       v               v                v
Review Enrichment   RAG Chat        Text-to-SQL
       |               |                |
       v               v                v
 Gemini LLM       Embeddings        Gemini LLM
       |               |                |
       v               v                v
Structured AI     Semantic Search   SQL Generation
Data              + Grounding       + Safety Guard
```

### Review Enrichment

Transforms unstructured reviews into structured analytical attributes.

### RAG

Uses semantic retrieval to provide relevant review context before
generating an answer.

### Text-to-SQL

Allows business users to query structured Snowflake marts using natural
language.

------------------------------------------------------------------------

# Data Quality & Governance

The project includes:

-   dbt models for standardized transformations
-   dbt data tests
-   Dedicated RAW, STAGING, MARTS and AI schemas
-   SQL safety validation for Text-to-SQL
-   `ON_ERROR = 'CONTINUE'` during raw ingestion
-   Separate AI enrichment layer
-   Airflow dependency management
-   Environment variables for credentials and API keys
-   Dockerized Airflow environment

------------------------------------------------------------------------

# Key Engineering Concepts Demonstrated

## Data Engineering

-   ETL / ELT
-   Data lake architecture
-   Cloud data warehousing
-   Snowflake
-   SQL
-   Dimensional modeling
-   Fact and dimension tables
-   Analytical marts
-   Data transformation

## dbt

-   Sources
-   Models
-   `ref()`
-   `source()`
-   Model tags
-   Data tests
-   Lineage
-   Documentation
-   Layered transformation architecture

## Airflow

-   DAGs
-   Task dependencies
-   BashOperator
-   SQLExecuteQueryOperator
-   Scheduled pipelines
-   Docker-based execution

## Generative AI

-   LLM-based classification
-   Structured JSON generation
-   Embeddings
-   Semantic search
-   Retrieval-Augmented Generation
-   Natural-language SQL generation
-   LLM safety guardrails

## Cloud / Data Platform

-   Amazon S3
-   Snowflake stages
-   `COPY INTO`
-   Snowflake schemas
-   Warehouse-based processing

------------------------------------------------------------------------

# Pipeline Execution

``` text
                    DAILY AIRFLOW DAG
                           |
                           v
                    +-------------+
                    | reload_raw  |
                    +------+------+
                           |
                           v
                  +-----------------+
                  | dbt_build_core  |
                  +--------+--------+
                           |
                           v
                  +-----------------+
                  | enrich_reviews  |
                  |     + Gemini    |
                  +--------+--------+
                           |
                           v
                    +-------------+
                    | dbt_build_ai|
                    +------+------+
                           |
                           v
                   AI + Analytics
```

The validated pipeline execution completed successfully:

``` text
reload_raw       ✓ SUCCESS
dbt_build_core   ✓ SUCCESS
enrich_reviews   ✓ SUCCESS
dbt_build_ai     ✓ SUCCESS
```

------------------------------------------------------------------------

# Project Outcomes

The platform provides:

-   A cloud-based data lake and warehouse pipeline
-   Automated data ingestion
-   dbt-powered transformation and modeling
-   Reusable analytical marts
-   Automated AI review enrichment
-   AI-powered review analytics
-   Semantic search over customer reviews
-   Natural-language SQL analytics
-   SQL execution safeguards
-   Airflow orchestration
-   Streamlit business-facing applications

------------------------------------------------------------------------

# Future Improvements

Potential production enhancements include:

-   Incremental dbt models
-   Snowflake Dynamic Tables
-   Snowflake-native vector search
-   Batch embedding pipelines
-   Embedding refresh and version management
-   More robust SQL AST-based validation
-   Role-based Snowflake access for Streamlit applications
-   CI/CD for dbt
-   Automated dbt tests in CI
-   Airflow failure notifications
-   Data quality monitoring
-   Observability and pipeline metrics
-   Containerized Streamlit deployment
-   Cloud deployment of the complete platform

------------------------------------------------------------------------

# Project Highlights

### End-to-End Data Pipeline

``` text
S3 → Snowflake → dbt → Marts
```

### AI Pipeline

``` text
Reviews → Gemini → AI.REVIEW_ENRICHED → dbt → MART_REVIEW_INSIGHTS
```

### RAG Pipeline

``` text
Reviews → Gemini Embeddings → Vector Store → Similarity Search → Gemini
```

### Text-to-SQL Pipeline

``` text
Natural Language → Gemini → SQL → Safety Check → Snowflake → Results
```

### Orchestration

``` text
Airflow
   ↓
RAW Ingestion
   ↓
dbt Core
   ↓
Gemini Enrichment
   ↓
dbt AI
```

------------------------------------------------------------------------

# Repository

**Repository name:**

``` text
food-delivery-data-engineering-ai-analytics-platform
```

**Project title:**

## Food Delivery Data Engineering & AI Analytics Platform

------------------------------------------------------------------------

# What This Project Demonstrates

> **A complete modern data platform where traditional Data Engineering
> forms the foundation for Generative AI and self-service analytics.**

``` text
             DATA ENGINEERING FOUNDATION
                         |
       +-----------------+-----------------+
       v                 v                 v
     S3              Snowflake            dbt
       |                 |                 |
       +-----------------+-----------------+
                         |
                         v
                  Analytical Marts
                         |
                         v
                    AI Layer
                         |
          +--------------+--------------+
          v              v              v
      Enrichment        RAG        Text-to-SQL
          |              |              |
          +--------------+--------------+
                         |
                         v
                    Streamlit
                         |
                         v
                   Business Users
```

This project combines a production-style **Data Engineering foundation**
with three integrated AI capabilities: **review enrichment,
conversational RAG, and natural-language Text-to-SQL analytics**.
