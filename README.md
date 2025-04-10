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
Full Load for Dimension Tables: Dimension tables (e.g., products, customers) are truncated and reloaded due to their smaller size, ensuring a clean dataset. All extracted data is staged in the staging environment (Bronze Tier).

Replication Attempt
PostgreSQL Logical Replication: An attempt was made to use PostgreSQL's built-in logical replication with a publisher and subscriber model. However, due to long-running replication issues (cause unknown), the approach was abandoned in favor of direct SQL queries.

Building the Enriched Layer
Approach 1: Python Scripts: Python scripts read data from the staging environment to build fact tables. Note: is_active flags were excluded from queries due to a lack of context in the task description.
Approach 2: Materialized Views: An alternative approach involves creating materialized views for frequently updated data. Two views are recommended:
Historic View: Contains data up to the previous date (excluding the current date).

Current Date View: Contains data for the current date.
A union view can be created on top of these to fetch both latest and historic data with improved performance.

Data Gaps and Potential Issues
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
Logging: Implement comprehensive logging to track execution and errors.
Secrets Management: Handle sensitive data (e.g., database credentials) using environment variables with the os module instead of hardcoding.
Consolidate CSV Extraction: Create a single command to run all export queries and consider adding email delivery of the CSV files.
Other Ideas
Handling Large Volumes (>100M records in 10 minutes):
Kafka with PySpark and Debezium: Implement Change Data Capture (CDC) on the database using Debezium, process records with PySpark, and store them in a Delta Lake storage system, which provides ACID transactions on the file system.
Alternative Storage: Use columnar storage databases like Amazon Redshift or Snowflake with query acceleration for better performance on large querying datasets.









