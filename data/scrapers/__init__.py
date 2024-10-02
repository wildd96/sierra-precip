import ao_scraper
import enso_scraper
import pdo_scraper
import utils.utils as utils
from google.cloud.sql.connector import Connector
import sqlalchemy
import pymysql
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class ClimateDatabase:
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS climate_indices (
        DATE DATE,
        NINO12 FLOAT,
        ANOM FLOAT,
        NINO3 FLOAT,
        ANOM1 FLOAT,
        NINO4 FLOAT,
        ANOM2 FLOAT,
        NINO34 FLOAT,
        ANOM3 FLOAT,
        pdo_value FLOAT,
        ao_value FLOAT,
        PRIMARY KEY (DATE)
    );    
    """

    def __init__(self, project_id, region, instance_name, db_user, db_pass, db_name):
        self.connector = Connector()
        self.connection_params = {
            "project_id": project_id,
            "region": region,
            "instance_name": instance_name,
            "user": db_user,
            "password": db_pass,
            "db": db_name
        }

    def get_connection(self):
        return self.connector.connect(
            f"{self.connection_params['project_id']}:{self.connection_params['region']}:{self.connection_params['instance_name']}",
            "pymysql",
            user=self.connection_params['user'],
            password=self.connection_params['password'],
            db=self.connection_params['db']
        )

    def create_table(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(self.CREATE_TABLE_SQL)
                conn.commit()
            print("Table created successfully")
        except Exception as e:
            print(f"Error creating table: {e}")
        
        conn.close()

    def insert_data(self, df):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for _, row in df.iterrows():
                    cursor.execute("""
                        INSERT INTO climate_indices (DATE, NINO12, ANOM, NINO3, ANOM1, NINO4, ANOM2, NINO34, ANOM3, pdo_value, ao_value)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, 
                    (row['DATE'], row['NINO1+2'], row['ANOM'], row['NINO3'], row['ANOM.1'], row['NINO4'], row['ANOM.2'], row['NINO3.4'], row['ANOM.3'], row['pdo_value'], row['ao_value'])
                    )
                conn.commit()
            print("Data inserted successfully")
        except pymysql.err.InterfaceError as e:
            print(f"An error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        conn.close()

def main():
    return None
    
if __name__ == "__main__":
    main()