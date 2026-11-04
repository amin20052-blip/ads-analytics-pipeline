import psycopg2
import pandas as pd

PG_CONFIG = {
    "dbname": "project_ads_db", "user": "postgres", "password": "admin2005",
    "host": "localhost", "port": "5432"
}

def check_data():
    conn = psycopg2.connect(**PG_CONFIG)
    df = pd.read_sql("SELECT * FROM speed_metrics_daily", conn)
    conn.close()

    print(f"Проверяем {len(df)} строк...")
    
    # Проверка 1: Данные вообще есть?
    if len(df) == 0:
        raise ValueError("Таблица пустая! Пайплайн сломался.")
    
    # Проверка 2: Нет ли LCP = 0 или отрицательного значения?
    if (df['avg_lcp_sec'] <= 0).any():
        raise ValueError("Найдено аномальное значение LCP (<= 0). Проверьте API.")
    
    print("Проверки пройдены успешно! Данные качественные.")

if __name__ == "__main__":
    check_data()