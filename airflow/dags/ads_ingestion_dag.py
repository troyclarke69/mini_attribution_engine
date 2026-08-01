"""Hourly advertising spend ingestion DAG."""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.ads_ingestion import fetch_ads_raw, normalize_ads, write_ads_to_bq


def _normalize_ads(**context: object) -> list[dict[str, object]]:
    """Normalize the raw ads batch stored in XCom."""
    raw = context["ti"].xcom_pull(task_ids="fetch_ads_raw")
    return normalize_ads(raw)


def _update_ads_freshness(**context: object) -> None:
    """Complete the freshness task after the BigQuery write."""
    context["ti"].xcom_pull(task_ids="write_ads_to_bq")


with DAG(
    dag_id="ads_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["marketing", "ingestion"],
) as dag:
    fetch_task = PythonOperator(task_id="fetch_ads_raw", python_callable=fetch_ads_raw)
    normalize_task = PythonOperator(task_id="normalize_ads", python_callable=_normalize_ads)
    write_task = PythonOperator(
        task_id="write_ads_to_bq",
        python_callable=lambda **context: write_ads_to_bq(
            context["ti"].xcom_pull(task_ids="normalize_ads")
        ),
    )
    freshness_task = PythonOperator(
        task_id="update_ads_freshness", python_callable=_update_ads_freshness
    )
    fetch_task >> normalize_task >> write_task >> freshness_task
