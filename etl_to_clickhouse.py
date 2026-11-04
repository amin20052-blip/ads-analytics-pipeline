import psycopg2
import pandas as pd 
import clickhouse_connect
from datetime import datetime, timedelta

PG_CONFIG = { 
    "dbname": "project_ads_db",
    "user": "postgres",
    "password": "admin2005",
    "host": "localhost",
    "port": "5432"
}


def extract_from_postgres():
    """Извлекает данные из PostgreSQL"""
    conn = psycopg2.connect(**PG_CONFIG)
    query = "SELECT * FROM raw_ad_events;"
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"Достали {len(df)} строк из постгреса.")
    return df


def transform_data(df):
    """Преобразуем данные"""
    df['event_time'] = pd.to_datetime(df['event_time'])
    df['hour']= df['event_time'].dt.floor('h')
    agg_df = df.groupby(['hour', 'device_type', 'placement']).agg(
        total_impressions=('event_id', 'count'),
        total_clicks=('is_click', 'sum'),
        avg_page_load_ms=('page_load_time_ms', 'mean'),
        avg_bid_price=('bid_price', 'mean')
    ).reset_index()
    agg_df['ctr_percentage'] = (agg_df['total_clicks'] / agg_df['total_impressions']) * 100
    agg_df['avg_page_load_ms'] = agg_df['avg_page_load_ms'].round(0).astype(int)
    agg_df['avg_bid_price'] = agg_df['avg_bid_price'].round(2)
    print(f"Преобразовали данные, получено {len(agg_df)} строк") 
    return agg_df

def load_to_clickhouse(df):
    """Загружаем данные в Clickhouse"""
    print("Подключение к Clickhouse... ")
    
    
    client = clickhouse_connect.get_client(
        host='localhost', 
        port=8123, 
        username='default', 
        password='my_secret_password' 
    )
    
    
    client.command("""
        CREATE TABLE IF NOT EXISTS ads_analytics_hourly(
            hour DateTime,
            device_type String,
            placement String,
            total_impressions UInt32,
            total_clicks UInt32,
            avg_page_load_ms UInt32,
            avg_bid_price Float32,
            ctr_percentage Float32
        ) ENGINE = MergeTree()
        ORDER BY (hour, device_type, placement)
    """)

    
    client.insert_df('ads_analytics_hourly', df)
    print("Данные успешно загружены в ClickHouse!")

if __name__ == "__main__":
    raw_data = extract_from_postgres()
    clean_data = transform_data(raw_data)
    load_to_clickhouse(clean_data)
    print("ETL-процесс завершен!")