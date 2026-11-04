import psycopg2
from psycopg2.extras import execute_values
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker


fake = Faker()

#подключаю бд
DB_CONFIG = {
    "dbname": "project_ads_db",
    "user": "postgres",
    "password": "admin2005",
    "host": "localhost",
    "port": "5432"
}

# списки для генерации
PLACEMENTS = ['search', 'catalog', 'recommendations']
DEVICES = ['mobile', 'desktop', 'tablet']

def get_db_connection():
    """Создает подключение к PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def create_table_if_not_exists(conn):
    """Создает таблицу для сырых логов, если ее нет"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_ad_events (
                event_id UUID PRIMARY KEY,
                event_time TIMESTAMP,
                user_id UUID,
                product_id UUID,
                placement VARCHAR(50),
                device_type VARCHAR(20),
                is_click BOOLEAN,
                bid_price NUMERIC(10, 2),
                -- Метрики скорости сайта (Core Web Vitals)
                page_load_time_ms INT,
                ttfb_ms INT
            );
        """)
    conn.commit()

def generate_batch(num_events=1000):
    """Генерирует пачку событий (показы и клики)"""
    events = []
    
    # Базовое время: генерируем события за последний час
    base_time = datetime.now()
    
    for _ in range(num_events):
        event_id = fake.uuid4()
        
        # Случайное время в пределах последнего часа
        event_time = base_time - timedelta(seconds=random.randint(0, 3600))
        
        user_id = fake.uuid4()
        product_id = fake.uuid4()
        placement = random.choice(PLACEMENTS)
        device_type = random.choice(DEVICES)
        
        # Ставка (цена за клик) от 5 до 150 рублей
        bid_price = round(random.uniform(5.0, 150.0), 2)
        
        # симулирую CTR за базу 3% с мобилки больше из рекомендаций меньше
        ctr_base = 0.03
        if device_type == 'mobile': ctr_base += 0.01
        if placement == 'recommendations': ctr_base -= 0.01
        
        # лик на основе вероятности
        is_click = random.random() < ctr_base
        
        # --- МЕТРИКИ СКОРОСТИ (СВЯЗЬ С КЛИКОМ) ---
        # Если страница грузится долго, вероятность клика падает
        # Генерируем время загрузки (LCP)
        page_load_time = int(np.random.normal(loc=2500, scale=800)) # среднее 2.5 сек
        if page_load_time < 500: page_load_time = 500 # защита от слишком быстрых
        
        # Если страница грузилась дольше 4 секунд, шанс клика резко падает
        if page_load_time > 4000:
            is_click = random.random() < (ctr_base * 0.3) # CTR падает на 70%
            
        # Время до первого байта (TTFB)
        ttfb = int(page_load_time * random.uniform(0.1, 0.3))
        
        events.append((
            event_id, event_time, user_id, product_id, 
            placement, device_type, is_click, bid_price,
            page_load_time, ttfb
        ))
        
    return events

def insert_events(conn, events):
    """Вставляет сгенерированные события в PostgreSQL"""
    query = """
        INSERT INTO raw_ad_events (
            event_id, event_time, user_id, product_id, placement, 
            device_type, is_click, bid_price, page_load_time_ms, ttfb_ms
        ) VALUES %s
    """
    with conn.cursor() as cur:
        execute_values(cur, query, events)
    conn.commit()
    print(f"Успешно вставлено {len(events)} событий.")

if __name__ == "__main__":
    print("Подключение к БД...")
    conn = get_db_connection()
    create_table_if_not_exists(conn)
    
    print("Генерация данных...")
    # Генерируем 5000 событий за раз
    batch = generate_batch(num_events=5000)
    
    print("Загрузка в PostgreSQL...")
    insert_events(conn, batch)
    
    conn.close()
    print("Готово!")