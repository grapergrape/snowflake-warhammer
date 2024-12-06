import os

import snowflake.connector
from dotenv import load_dotenv
import polars as pl

from snowflake_queries import get_all_orcs, get_race_id



load_dotenv()
# Establish a connection to Snowflake
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)
# Create a cursor object

class SnowflakeConnector:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user= os.getenv("SNOWFLAKE_USER"),
            password= os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"))
    
    def execute_query_fetch(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        # construct a DataFrame from the query results
        return(pl.DataFrame(cur))

    def execute_query_insert(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        cur.close()
        self.conn.commit()
        return cur.rowcount




