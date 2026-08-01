"""Quarter-hourly orders ingestion DAG."""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.orders_ingestion import fetch_orders_raw, normalize_orders, write_orders_to_bq


def _normalize_orders(**context: object) -> list[dict[str, object]]:
    """Normalize the raw orders batch stored in XCom."""
    return normalize_orders(context["ti"].xcom_pull(task_ids="fetch_orders_raw"))


def _write_orders(**context: object) -> None:
    """Write the normalized order batch from XCom."""
    write_orders_to_bq(context["ti"].xcom_pull(task_ids="normalize_orders"))


with DAG(
    dag_id="orders_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *",
    catchup=False,
    tags=["marketing", "ingestion"],
) as dag:
    fetch_task = PythonOperator(task_id="fetch_orders_raw", python_callable=fetch_orders_raw)
    normalize_task = PythonOperator(task_id="normalize_orders", python_callable=_normalize_orders)
    write_task = PythonOperator(task_id="write_orders_to_bq", python_callable=_write_orders)
    freshness_task = PythonOperator(
        task_id="update_orders_freshness", python_callable=lambda: None
    )
    fetch_task >> normalize_task >> write_task >> freshness_task
