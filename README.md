# Data Engineering Take-Home Task

This repository contains the solution for the ACME Delivery Services Analytical Platform, a data engineering task designed to extract, transform, and analyze transactional and dimensional data using Dockerized PostgreSQL and Python scripts.

## Prerequisites
- Docker and Docker Compose installed.

## Setup and Running
To run the solution, use the following command to start the Docker stack with a fresh build and recreation of services:
```bash 
docker-compose up --build --force-recreate --always-recreate-deps -d
```
This command ensures the stack runs in detached mode (-d) with a rebuilt environment, forcing recreation of all services and their dependencies.

## Setup and Running

##Current Approach
Data Extraction
Incremental Extraction from Transaction Tables: Data is extracted incrementally from transactional tables based on the updated_at field. Instead of deleting or merging data (which could increase processing time), we retain all records and rely on the primary key (PK) and last updated time to determine the current state. This approach avoids writing analytical queries directly on the transactional database, which experiences heavy writes. In a production environment, it is recommended to use a read replica database for querying.

## Pipieline

Extract_to_staging.py >>>>>  ETL_Pipeline.py >>>>>> Cli.py

Full Load for Dimension Tables: Dimension tables (e.g., products, customers) are truncated and reloaded due to their smaller size, ensuring a clean dataset. All extracted data is staged in the staging environment (Bronze Tier).



Replication Attempt
PostgreSQL Logical Replication: An attempt was made to use PostgreSQL's built-in logical replication with a publisher and subscriber model. However, due to long-running replication issues (cause unknown), the approach was abandoned in favor of direct SQL queries.

## ETL Pipeline Script Explanation
The `app/src/etl_pipeline.py` script is responsible for transforming data from the `staging` schema (Bronze Tier) into the `analytics` schema (Silver Tier) by aggregating and enriching the data for analytical purposes. Below is an overview of its functionality:

- **Purpose**: The script processes staged data (e.g., `products`, `customers`, `orders`, `order_items`) to create aggregated fact tables in the `analytics` schema, such as `open_orders_agg`, `order_items_pending_agg`, and `customer_pending_orders_agg`.
- **Implementation**:
  - Uses SQLAlchemy for database connections and pandas for data manipulation.
  - Connects to the PostgreSQL database using a hardcoded connection string (`postgresql://finance_db_user:1234@trans-db:5432/finance_db`), which should be replaced with environment variables in production.
  - Executes SQL queries to join and aggregate data from the `staging` tables.
- **Key Transformations**:
  - **Open Orders Aggregation**: Groups `orders` data by `delivery_date` and `status` to count pending orders.
  - **Pending Items Aggregation**: Calculates the number of pending items per `product_id` by joining `order_items` with `orders` where `status` is 'pending'.
  - **Top Customers Aggregation**: Identifies the top customers by counting pending orders per `customer_id`.
- **Execution**: The script truncates existing tables in the `analytics` schema and loads the transformed data, ensuring a full refresh for each run. This aligns with the incremental extraction from transactional tables and full load from dimension tables.
- **Limitations**: The script assumes data consistency (e.g., matching `order_id` between `orders` and `order_items`). Data gaps (e.g., missing `order_id` entries) may result in null values, as noted in the Data Gaps section.
- **File Location**: Located at `app/src/etl_pipeline.py`, it is executed via the `etl-service` in `docker-compose.yml`.

To run the ETL process manually, use:
``` docker-compose run etl-service ```

Building the Enriched Layer
Approach 1: Python Scripts: Python scripts read data from the staging environment to build fact tables. Note: is_active flags were excluded from queries due to a lack of context in the task description.
Approach 2: Materialized Views: An alternative approach involves creating materialized views for frequently updated data. Two views are recommended:
Historic View: Contains data up to the previous date (excluding the current date).

Current Date View: Contains data for the current date.
A union view can be created on top of these to fetch both latest and historic data with improved performance.

## Data Gaps and Potential Issues
Order ID Mismatch: Not all order_id values from the operations.orders table are present in the operations.order_items table, likely due to randomness in the sample data. This causes the pending_items output to be null in most cases. To investigate:
```bash
SELECT DISTINCT a.order_id, b.order_id
FROM operations.order_items a
RIGHT JOIN operations.orders b ON a.order_id = b.order_id;
```

## Export Query - 
```bash

sample - docker-compose run cli-app --query top_customers --export ,
docker-compose run cli-app --query pending_items --export ,
docker-compose run cli-app --query top_dates --export,
docker-compose run cli-app --query open_orders --export
```

Export Queries
Sample commands to export query results to CSV files:

Export Top Customers:
```bash


docker-compose run cli-app --query top_customers --export
Output file: top_customers_result_<timestamp>.csv.

```
Export Pending Items:
```bash

docker-compose run cli-app --query pending_items --export
Output file: pending_items_result_<timestamp>.csv.
Export Top Dates:
```
```bash


docker-compose run cli-app --query top_dates --export
Output file: top_dates_result_<timestamp>.csv.
Export Open Orders:
```
```bash

docker-compose run cli-app --query open_orders --export
Output file: open_orders_result_<timestamp>.csv.
```

## To-Do Items
Asncio : Use Async while extraction this enable parllel writing | Trade off hard to debug and sacrifice code readibility 
Logging: Implement comprehensive logging to track execution and errors.
Secrets Management: Handle sensitive data (e.g., database credentials) using environment variables with the os module instead of hardcoding.
Consolidate CSV Extraction: Create a single command to run all export queries and consider adding email delivery of the CSV files.
Performance Optimization - Instead of Pandas use fireduck & in place sqlAlemchy us pycopg2 based on time reduction 

## Other Ideas
Handling Large Volumes (>100M records in 10 minutes):
Kafka with PySpark and Debezium: Implement Change Data Capture (CDC) on the database using Debezium, process records with PySpark, and store them in a Delta Lake storage system, which provides ACID transactions on the file system.
Alternative Storage: Use columnar storage databases like Amazon Redshift or Snowflake with query acceleration for better performance on large querying datasets.
![image](https://github.com/user-attachments/assets/0b67141f-8990-480d-b50b-0f9d388df391)










