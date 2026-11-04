from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Базовые настройки DAG
default_args = {
    'owner': 'amin',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    'speed_metrics_pipeline',
    default_args=default_args,
    description='ETL pipeline for Core Web Vitals',
    schedule_interval='0 18 * * *',  
    start_date=datetime(2026, 11, 5),
    catchup=False,
    tags=['ozon_project'],
) as dag:

    
    extract_data = BashOperator(
        task_id='extract_from_google_api',
        bash_command='cd /opt/airflow/project && python3 extract_speed_data.py',
    )

    
    transform_data = BashOperator(
        task_id='run_dbt_models',
        bash_command='cd /opt/airflow/project/dbt && dbt run --profiles-dir .',
    )

   
    load_to_clickhouse = BashOperator(
        task_id='load_to_clickhouse',
        bash_command='cd /opt/airflow/project && python3 load_to_clickhouse_v2.py',
    )

    
    check_data_quality = BashOperator(
        task_id='check_data_quality_pandas',
        bash_command='cd /opt/airflow/project && python3 check_quality.py',
    )

    # Выстраиваем цепочку: Extract -> Transform -> Load -> Check
    extract_data >> transform_data >> load_to_clickhouse >> check_data_quality