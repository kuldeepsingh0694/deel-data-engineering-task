# app/src/extract_to_staging.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded connection string
CONN_STRING = "postgresql://finance_db_user:1234@transactions-db:5432/finance_db"

def get_engine():
    return create_engine(CONN_STRING)

def get_last_extract_timestamp(session, table_name):
    query = text(f"SELECT  MAX(updated_at) FROM staging.{table_name}")
    result = session.execute(query).scalar()
    return result if result else datetime(1970, 1, 1)

def extract_to_staging(session, table_name, query):
    if table_name in ["products", "customers"]:
        # Full refresh for products and customers
        logger.debug(f"Executing full refresh query for {table_name}: {query}")
        df = pd.read_sql(query, session.bind)
        if_exists_mode = 'replace'
        logger_info_msg = f"Extracted and loaded {len(df)} records into staging.{table_name} with full refresh"
    else:
        # Incremental update for orders and order_items
        last_extract = get_last_extract_timestamp(session, table_name)
        last_extract = last_extract - timedelta(minutes=5) if last_extract else datetime(1970, 1, 1)
        full_query = text(f"{query} WHERE updated_at > :last_extract OR created_at > :last_extract")
        logger.debug(f"Executing incremental query for {table_name}: {full_query}")
        df = pd.read_sql(full_query, session.bind, params={"last_extract": last_extract})
        if_exists_mode = 'append'
        logger_info_msg = f"Extracted and loaded {len(df)} records into staging.{table_name} with incremental update"

    if not df.empty:
        df['extract_timestamp'] = datetime.now()
        df.to_sql(table_name, session.bind, schema='staging', if_exists=if_exists_mode, index=False)
        logger.info(logger_info_msg)
    else:
        logger.warning(f"No records found for staging.{table_name}")

def main():
    engine = get_engine()
    with Session(engine) as session:
        try:
            queries = {
                "products": "SELECT * FROM operations.products",
                "customers": "SELECT * FROM operations.customers",
                "orders": "SELECT * FROM operations.orders",
                "order_items": "SELECT * FROM operations.order_items"
            }
            for table, query in queries.items():
                extract_to_staging(session, table, query)
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            logger.info("Session closed")

if __name__ == "__main__":
    main()

# # app/src/extract_to_staging.py
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import Session
# import pandas as pd
# from datetime import datetime, timedelta
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Hardcoded connection string
# CONN_STRING = "postgresql://finance_db_user:1234@transactions-db:5432/finance_db"

# def get_engine():
#     return create_engine(CONN_STRING)

# def get_last_extract_timestamp(session, table_name):
#     query = text(f"SELECT  MAX(updated_at) FROM staging.{table_name}")
#     result = session.execute(query).scalar()
#     return result if result else datetime(1970, 1, 1)

# def extract_to_staging(session, table_name, query):
#     last_extract = get_last_extract_timestamp(session, table_name)
#     last_extract = last_extract - timedelta(minutes=5) if last_extract else datetime(1970, 1, 1)
    
#     full_query = text(f"{query} WHERE updated_at > :last_extract OR created_at > :last_extract")
#     df = pd.read_sql(full_query, session.bind, params={"last_extract": last_extract})
    
    
#     if not df.empty:
#         df['extract_timestamp'] = datetime.now()
#         df.to_sql(table_name, session.bind, schema='staging', if_exists='append', index=False)
#         logger.info(f"Extracted and loaded {len(df)} records into staging.{table_name}")

# def main():
#     engine = get_engine()
#     with Session(engine) as session:
#         try:
#             queries = {
#                 "products": "SELECT * FROM operations.products",
#                 "customers": "SELECT * FROM operations.customers",
#                 "orders": "SELECT * FROM operations.orders", ## Appending the delta in the table
#                 "order_items": "SELECT * FROM operations.order_items" ## Appending the delta in the table
#             }
#             for table, query in queries.items():
#                 extract_to_staging(session, table, query)
#         except Exception as e:
#             logger.error(f"Database error: {e}")
#         finally:
#             logger.info("Session closed")

# if __name__ == "__main__":
#     main()

# import psycopg2
# import pandas as pd
# import os
# from datetime import datetime, timedelta
# from sqlalchemy import create_engine

# # DB_CONFIG = {
# #     "dbname": os.getenv("POSTGRES_DB", "finance_db"),
# #     "user": os.getenv("POSTGRES_USER", "finance_db_user"),
# #     "password": os.getenv("POSTGRES_PASSWORD", "1234"),
# #     "host": os.getenv("POSTGRES_HOST", "localhost"),
# #     "port": os.getenv("POSTGRES_PORT", "5432")
# # }
# CONN_STRING = "postgresql://finance_db_user:1234@transactions-db:5432/finance_db"

# def get_last_extract_timestamp(conn, table_name):
#     query = f"SELECT COALESCE(MAX(extract_timestamp),now()-interval '1 Hour') FROM staging.{table_name}"
#     df = pd.read_sql(query, conn)
#     print(df)
#     return df.iloc[0, 0] if pd.notna(df.iloc[0, 0]) else datetime(1970, 1, 1)

# def extract_to_staging(conn, table_name, query):
#     last_extract = get_last_extract_timestamp(conn, table_name)
#     last_extract = last_extract - timedelta(minutes=5) if last_extract else datetime(1970, 1, 1)
    
#     full_query = f"{query} WHERE updated_at > %s OR created_at > %s"
#     df = pd.read_sql(full_query, conn, params=(last_extract, last_extract))
    
#     if not df.empty:
#         df['extract_timestamp'] = datetime.now()
#         df.to_sql(table_name, conn, schema='staging', if_exists='append', index=False)
#         print(f"Extracted and loaded {len(df)} records into staging.{table_name}")

# def main():
#     conn = CONN_STRING
    
#     queries = {
#         "products": "SELECT * FROM operations.products",
#         "customers": "SELECT * FROM operations.customers",
#         "orders": "SELECT * FROM operations.orders",
#         "order_items": "SELECT * FROM operations.order_items"
#     }

#     for table, query in queries.items():
#         extract_to_staging(conn, table, query)

#     conn.close()

# if __name__ == "__main__":
#     main()