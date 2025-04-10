# app/src/cli.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import pandas as pd
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded connection string
CONN_STRING = "postgresql://finance_db_user:1234@transactions-db:5432/finance_db"

def get_engine():
    return create_engine(CONN_STRING)

def query_open_orders(session):
    query = text("""
        SELECT * from analytics.open_orders_agg
    """)
    df = pd.read_sql(query, session.bind)
    return df

def query_top_delivery_dates(session):
    query = text("""
                SELECT delivery_date,avg(total_open) from analytics.open_orders_agg group by 1 order by avg(total_open) limit 3

    """)
    df = pd.read_sql(query, session.bind)
    return df

def query_pending_items(session):
    query = text("""
        SELECT *
        FROM analytics.order_items_pending_agg
    """)
    df = pd.read_sql(query, session.bind)
    return df

def query_top_customers(session):
    query = text("""
      select * from analytics.customer_pending_orders_agg
    """)
    df = pd.read_sql(query, session.bind)
    return df

if __name__ == "__main__":
    engine = get_engine()
    with Session(engine) as session:
        try:
            parser = argparse.ArgumentParser(description="ACME Delivery Analytics CLI")
            parser.add_argument("--query", choices=['open_orders', 'top_dates', 'pending_items', 'top_customers'], required=True)
            parser.add_argument("--export", action="store_true", help="Export results to CSV")
            args = parser.parse_args()

            if args.query == 'open_orders':
                df = query_open_orders(session)
            elif args.query == 'top_dates':
                df = query_top_delivery_dates(session)
            elif args.query == 'pending_items':
                df = query_pending_items(session)
            elif args.query == 'top_customers':
                df = query_top_customers(session)

            logger.info(f"Query {args.query} executed successfully")
            print(df)
            if args.export:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{args.query}_result_{timestamp}.csv"
                df.to_csv(filename, index=False)
                logger.info(f"Exported to {filename}")
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            logger.info("Session closed")
# import psycopg2
# import pandas as pd
# import argparse
# from datetime import datetime
# import os 
# from sqlalchemy import create_engine

# def connect_db():
#     return psycopg2.connect("postgresql://finance_db_user:1234@transactions-db:5432/finance_db")


# def query_open_orders():
#     conn = connect_db()
#     query = """
#         SELECT delivery_date, status, order_count
#         FROM analytics.open_orders_agg
#         WHERE status = 'pending'
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

# def query_top_delivery_dates():
#     conn = connect_db()
#     query = """
#         SELECT delivery_date, SUM(order_count) as total_orders
#         FROM analytics.open_orders_agg
#         WHERE status = 'pending'
#         GROUP BY delivery_date
#         ORDER BY total_orders DESC
#         LIMIT 3
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

# def query_pending_items():
#     conn = connect_db()
#     query = """
#         SELECT product_id, pending_count
#         FROM analytics.order_items_pending_agg
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

# def query_top_customers():
#     conn = connect_db()
#     query = """
#         SELECT customer_id, pending_order_count
#         FROM analytics.customer_pending_orders_agg
#         ORDER BY pending_order_count DESC
#         LIMIT 3
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="ACME Delivery Analytics CLI")
#     parser.add_argument("--query", choices=['open_orders', 'top_dates', 'pending_items', 'top_customers'], required=True)
#     parser.add_argument("--export", action="store_true", help="Export results to CSV")
#     args = parser.parse_args()

#     if args.query == 'open_orders':
#         df = query_open_orders()
#     elif args.query == 'top_dates':
#         df = query_top_delivery_dates()
#     elif args.query == 'pending_items':
#         df = query_pending_items()
#     elif args.query == 'top_customers':
#         df = query_top_customers()

#     print(df)
#     if args.export:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"{args.query}_result_{timestamp}.csv"
#         df.to_csv(filename, index=False)
#         print(f"Exported to {filename}")