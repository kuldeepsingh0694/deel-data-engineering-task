# app/src/etl_pipeline.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded connection string
CONN_STRING = "postgresql://finance_db_user:1234@transactions-db:5432/finance_db"

def get_engine():
    return create_engine(CONN_STRING)

def main():
    engine = get_engine()
    with Session(engine) as session:
        try:
            # Extract from staging
            query_open_orders = text("""
                                WITH ranked_orders AS (
    SELECT 
        * , -- Specify only needed columns
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) as rn
    FROM staging.orders
)
SELECT 
   delivery_date, status, COUNT(*) as order_count,sum(count(*)) over(partition by delivery_date) as total_open
FROM ranked_orders
WHERE rn = 1 and  status <> 'COMPLETED'
                GROUP BY delivery_date, status
                
            """)
            df_open_orders = pd.read_sql(query_open_orders, session.bind)

            query_items = text("""
                with ranked_orders AS ( select order_id,status from (
    SELECT 
        * , -- Specify only needed columns
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) as rn
    FROM operations.orders
)a
where rn=1 and status='PENDING')

, ranked_order_items AS (
    SELECT 
        a.* , -- Specify only needed columns
        ROW_NUMBER() OVER (PARTITION BY a.order_item_id ORDER BY a.updated_at DESC) as rn
    FROM staging.order_items a
	inner join ranked_orders b
	on a.order_id=b.order_id
	
) 
SELECT 
   product_id,count(*)
FROM ranked_order_items
WHERE rn = 1 
	 
 
			   GROUP BY 1
            """)
            df_items = pd.read_sql(query_items, session.bind)

            query_customers = text("""
                WITH ranked_orders AS (
    SELECT 
        * , -- Specify only needed columns
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) as rn
    FROM staging.orders
)
SELECT 
   a.customer_id,b.customer_name,count(a.*)
FROM ranked_orders a
left join staging.customers b
on a.customer_id=b.customer_id
WHERE rn = 1 and  status ='PENDING'
                GROUP BY 1,2
            """)
            df_customers = pd.read_sql(query_customers, session.bind)

            # Load into analytics schema
            df_open_orders.to_sql('open_orders_agg', session.bind, schema='analytics', if_exists='replace', index=False)
            df_items.to_sql('order_items_pending_agg', session.bind, schema='analytics', if_exists='replace', index=False)
            df_customers.to_sql('customer_pending_orders_agg', session.bind, schema='analytics', if_exists='replace', index=False)
            logger.info("ETL process completed successfully")
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            logger.info("Session closed")

if __name__ == "__main__":
    main()

# import psycopg2
# import pandas as pd
# from datetime import datetime
# import os
# from sqlalchemy import create_engine

# conn = psycopg2.connect("postgresql://finance_db_user:1234@transactions-db:5432/finance_db")

# # Extract from staging
# query_orders = """
#     SELECT delivery_date, status, COUNT(*) as order_count
#     FROM staging.orders
#     WHERE status = 'pending'
#     GROUP BY delivery_date, status
# """
# df_orders = pd.read_sql(query_orders, conn)

# query_items = """
#     SELECT oi.product_id, COUNT(*) as pending_count
#     FROM staging.order_items oi
#     JOIN staging.orders o ON oi.order_id = o.order_id
#     WHERE o.status = 'pending'
#     GROUP BY oi.product_id
# """
# df_items = pd.read_sql(query_items, conn)

# query_customers = """
#     SELECT o.customer_id, COUNT(*) as pending_order_count
#     FROM staging.orders o
#     WHERE o.status = 'pending'
#     GROUP BY o.customer_id
# """
# df_customers = pd.read_sql(query_customers, conn)

# # Load into analytics schema
# df_orders.to_sql('open_orders_agg', conn, schema='analytics', if_exists='replace', index=False)
# df_items.to_sql('order_items_pending_agg', conn, schema='analytics', if_exists='replace', index=False)
# df_customers.to_sql('customer_pending_orders_agg', conn, schema='analytics', if_exists='replace', index=False)

# conn.close()