import requests
import os
from dotenv import load_dotenv
import csv
import time
import snowflake.connector
from datetime import datetime
load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

LIMIT = 1000
DS = '2024-10-14'

def run_stock_job():
    DS = datetime.now().strftime('%Y-%m-%d')
    url = f'https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker&apiKey={POLYGON_API_KEY}'
    response = requests.get(url)
    tickers = []

    data = response.json()
    print(data['next_url'])
    for ticker in data['results']:
        ticker['ds'] = DS
        tickers.append(ticker)

    time._pass_count = 1

    while 'next_url' in data:
        next_url = data['next_url']
        print(f'Requesting next page {next_url}')
        response = requests.get(data['next_url'] + f'&apiKey={POLYGON_API_KEY}')
        data = response.json()
        print(data)
        for ticker in data['results']:
            ticker['ds'] = DS
            tickers.append(ticker)

        # Pause every 4 passes
        time._pass_count += 1
        if time._pass_count % 5 == 0:
            print("Pausing for 1 minute...")
            time.sleep(70)

    example_ticker = {'ticker': 'HUIZ', 
    'name': 'Huize Holding Limited American Depositary Shares', 
    'market': 'stocks', 
    'locale': 'us', 
    'primary_exchange': 'XNAS', 
    'type': 'ADRC', 
    'active': True, 
    'currency_name': 'usd', 
    'cik': '0001778982', 
    'composite_figi': 'BBG00Q5M64J3', 
    'share_class_figi': 'BBG00Q5M6582', 
    'last_updated_utc': '2025-09-13T06:11:08.183300129Z',
    'ds': '2025-10-14'}
    
    columns = list(example_ticker.keys())

    # Write tickers to CSV with the same schema as example_ticker
    load_to_snowflake(tickers, columns)

def load_to_snowflake(tickers, columns):
    # Write tickers to Snowflake table with the same schema as example_ticker
    snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
    snowflake_user = os.getenv("SNOWFLAKE_USER")
    snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
    snowflake_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
    snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA")
    snowflake_role = os.getenv("SNOWFLAKE_ROLE")

    conn = snowflake.connector.connect(
        user=snowflake_user,
        password=snowflake_password,
        account=snowflake_account,
        warehouse=snowflake_warehouse,
        database=snowflake_database,
        schema=snowflake_schema,
        role=snowflake_role,
        session_parameters={
            'CLIENT_TELEMETRY_ENABLED': False,
            }
    )

    try:
        cur = conn.cursor()
        try:
            table_name = os.getenv("SNOWFLAKE_TABLE", "stock_tickers")

            # Define typed schema based on example_ticker
            type_overrides = {
                'ticker': 'VARCHAR', 
                'name': 'VARCHAR', 
                'market': 'VARCHAR', 
                'locale': 'VARCHAR', 
                'primary_exchange': 'VARCHAR', 
                'type': 'VARCHAR', 
                'active': 'BOOLEAN', 
                'currency_name': 'VARCHAR', 
                'cik': 'VARCHAR', 
                'composite_figi': 'VARCHAR', 
                'share_class_figi': 'VARCHAR', 
                'last_updated_utc': 'TIMESTAMP_NTZ',
                'ds': 'VARCHAR'
            }
            columns_sql_parts = []
            for col in columns:
                col_type = type_overrides.get(col, 'VARCHAR')
                columns_sql_parts.append(f'"{col.upper()}" {col_type}')

            # Create table if not exists
            create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} ( ' + ', '.join(columns_sql_parts) + ' )'
            cur.execute(create_table_sql)

            # Insert all tickers in a single batch
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
            rows = [[ticker.get(col, "") for col in columns] for ticker in tickers]
            cur.executemany(insert_sql, rows)

            print(f"Total tickers fetched: {len(tickers)}")
        finally:
            cur.close()
    finally:
        conn.close()

if __name__ == "__main__":
    run_stock_job()
        