"""Ten-minute clickstream compaction DAG."""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.events_compaction import compact_events_raw, normalize_events, write_events_to_bq


def _normalize_events(**context: object) -> list[dict[str, object]]:
    """Normalize the compacted event batch stored in XCom."""
    return normalize_events(context["ti"].xcom_pull(task_ids="compact_events_raw"))


def _write_events(**context: object) -> None:
    """Write the normalized event batch from XCom."""
    write_events_to_bq(context["ti"].xcom_pull(task_ids="normalize_events"))


with DAG(
    dag_id="events_compaction",
    start_date=datetime(2024, 1, 1),
    schedule="*/10 * * * *",
    catchup=False,
    tags=["marketing", "events"],
) as dag:
    compact_task = PythonOperator(task_id="compact_events_raw", python_callable=compact_events_raw)
    normalize_task = PythonOperator(task_id="normalize_events", python_callable=_normalize_events)
    write_task = PythonOperator(task_id="write_events_to_bq", python_callable=_write_events)
    freshness_task = PythonOperator(
        task_id="update_events_freshness", python_callable=lambda: None
    )
    compact_task >> normalize_task >> write_task >> freshness_task
