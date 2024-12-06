from datetime import datetime
import os

import polars as pl
from dotenv import load_dotenv

from snowflake_queries import *
from snowflake_connector import SnowflakeConnector
from warsimulator import WarSimulator, ORC_UNITS, CHAOS_MARINES_UNITS

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    snowflake_connector = SnowflakeConnector()
    war_simulator = WarSimulator(OPENAI_API_KEY)

    # Define data
    race_df = {
        'RACE_NAME': ['Orc', 'CHAOS MARINES'],
        'WIN_COUNT': [0, 0],
    }
    class_df = {
        'RACE_ID': [0, 1],
    }

    orc_warrior_df = war_simulator.generate_faction_data('Orc')
    # add RACE_ID to the dataframe with the value 0
    orc_warrior_df = orc_warrior_df.with_column(pl.col("RACE_ID").fill_null(0))

    chaos_marines_warrior_df = war_simulator.generate_faction_data('CHAOS MARINES')
    chaos_marines_warrior_df = chaos_marines_warrior_df.with_column(pl.col("RACE_ID").fill_null(1))


    # Convert to Polars DataFrame
    racepl_df = pl.DataFrame(race_df)
    classpl_df = pl.DataFrame(class_df)
    # SQL query template
    race_query = """
    INSERT INTO CORE_RACE (RACE_ID,RACE_NAME, WIN_COUNT)
    VALUES (%d, '%s', %d)
    """
    class_query = """
    INSERT INTO CORE_CLASS (CLASS_ID, CLASS_NAME, CREATION_DATE, RACE_ID)
    VALUES (%s, %s, %s, %s)
    """
    warrior_query = """
    INSERT INTO CORE_FIGHTERS (FIGHTER_ID, FIGHTER_NAME, ORIGIN_HISTORY, STATUS, CLASS_ID, RACE_ID)
    -- status is True upon creation 
    VALUES (%s, %s, %s, True, %s, %s)
    """
    # Insert each row into the database
    for i in range(racepl_df.height):
        row = racepl_df.row(i)
        snowflake_connector.execute_query_insert(race_query % (i,row[0], row[1]))

    # time complexity is O(n^2) but n is small so it is acceptable, could be optimized with batch insert
    for i in range(classpl_df.height):
        row = classpl_df.row(i)
        if row[0] == 0:
            for j in range(len(ORC_UNITS)):
                snowflake_connector.execute_query_insert(class_query % (j, ORC_UNITS[j], datetime.now(), row[0]))
                for k in range(orc_warrior_df.height):
                    warrior = orc_warrior_df.row(k)
                    if warrior[1] == ORC_UNITS[j]:
                        snowflake_connector.execute_query_insert(warrior_query % (k, warrior[0], warrior[2], j, row[0]))              
        else:
            for j in range(len(CHAOS_MARINES_UNITS)):
                snowflake_connector.execute_query_insert(class_query % (j, CHAOS_MARINES_UNITS[j], datetime.now(), row[0]))
                for k in range(chaos_marines_warrior_df.height):
                    warrior = chaos_marines_warrior_df.row(k)
                    if warrior[1] == CHAOS_MARINES_UNITS[j]:
                        snowflake_connector.execute_query_insert(warrior_query % (k, warrior[0], warrior[2], j, row[0]))


    
