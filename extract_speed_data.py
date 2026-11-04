
import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("GOOGLE_API_KEY")

SITES = ["https://www.ozon.ru", "https://www.ozon.travel"]

PG_CONFIG = {
    "dbname": os.getenv("PG_DBNAME"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT")
}

def get_speed_metrics(url):
    """Делает запрос к PageSpeed API и возвращает набор метрик"""
    endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={API_KEY}"
    response = requests.get(endpoint)
    
    if response.status_code != 200:
        print(f"Ошибка при запросе к {url}: {response.text}")
        return None
    
    data = response.json()
    audits = data.get('lighthouseResult', {}).get('audits', {})
    
    try:
        # Достаем значения из JSON. Если метрики нет, ставим None
        lcp = audits.get('largest-contentful-paint', {}).get('numericValue')
        cls = audits.get('cumulative-layout-shift', {}).get('numericValue')
        tbt = audits.get('total-blocking-time', {}).get('numericValue')
        fcp = audits.get('first-contentful-paint', {}).get('numericValue')
        
        return {
            "url": url, 
            "lcp_ms": lcp,  # Теперь сохраняем в миллисекундах
            "cls": round(cls, 3) if cls else None,
            "tbt_ms": tbt,
            "fcp_ms": fcp
        }
    except Exception as e:
        print(f"Ошибка парсинга для {url}: {e}")
        return None

def save_to_postgres(metrics):
    """Сохраняет метрики скорости в PostgreSQL"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_speed_metrics (
            id SERIAL PRIMARY KEY,
            url TEXT,
            lcp_ms NUMERIC,
            cls NUMERIC,
            tbt_ms NUMERIC,
            fcp_ms NUMERIC,
            parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    for m in metrics:
        if m: 
            
            cur.execute(
                """
                INSERT INTO raw_speed_metrics (url, lcp_ms, cls, tbt_ms, fcp_ms) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (m['url'], m['lcp_ms'], m['cls'], m['tbt_ms'], m['fcp_ms'])
            )
    
   
    conn.commit()
    
    cur.close()
    conn.close()
    
    print(f"Успешно сохранено {len(metrics)} записей в PostgreSQL.")
if __name__ == "__main__":
    print("Запрос метрик из PageSpeed API...")
    results = []
    for site in SITES:
        print(f"Проверяем {site}...")
        metrics = get_speed_metrics(site)
        if metrics:
            results.append(metrics)
    
    if results:
        save_to_postgres(results)
    else:
        print("Не удалось получить данные.")