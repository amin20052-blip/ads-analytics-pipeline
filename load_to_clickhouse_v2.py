

import os
import psycopg2
import pandas as pd
import clickhouse_connect
from dotenv import load_dotenv


load_dotenv()

PG_CONFIG = {
    "dbname": os.getenv("PG_DBNAME"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT")
}
def load_dbt_mart_to_clickhouse():
    print("Читаем витрину из PostgreSQL...")
    conn = psycopg2.connect(**PG_CONFIG)
    
    df = pd.read_sql("SELECT * FROM speed_metrics_daily", conn)
    conn.close()
    print(f"Загружено {len(df)} строк из dbt-витрины.")

    print("Подключаемся к ClickHouse...")
    client = clickhouse_connect.get_client(
        host=os.getenv("CH_HOST"), 
        port=int(os.getenv("CH_PORT")), 
        username=os.getenv("CH_USER"), 
        password=os.getenv("CH_PASSWORD")
    )
    
    client.command("""
        CREATE TABLE IF NOT EXISTS speed_metrics_daily_ch (
            metric_date Date,
            url String,
            avg_lcp_sec Float32,
            avg_cls Float32,
            avg_tbt_sec Float32,
            measurements_count UInt32
        ) ENGINE = MergeTree()
        ORDER BY (metric_date, url)
    """)

    
    client.insert_df('speed_metrics_daily_ch', df)
    print("Данные успешно загружены в ClickHouse!")

if __name__ == "__main__":
    load_dbt_mart_to_clickhouse()