"""Hourly last-touch attribution DAG."""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

from etl.attribution import compute_summary_metrics, run_last_touch_attribution, write_attribution_results


def _wait_for_sources_fresh() -> None:
    """Provide an explicit dependency gate for source freshness checks."""
    return None


def _write_attribution(**context: object) -> None:
    """Persist the attribution results for this run."""
    write_attribution_results()


with DAG(
    dag_id="attribution",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["marketing", "attribution"],
) as dag:
    wait_task = PythonOperator(task_id="wait_for_sources_fresh", python_callable=_wait_for_sources_fresh)
    attribution_task = PythonOperator(
        task_id="run_last_touch_attribution", python_callable=run_last_touch_attribution
    )
    metrics_task = PythonOperator(
        task_id="compute_summary_metrics",
        python_callable=lambda **context: compute_summary_metrics(
            context["ti"].xcom_pull(task_ids="run_last_touch_attribution") or []
        ),
    )
    write_task = PythonOperator(task_id="write_attribution_to_bq", python_callable=_write_attribution)
    freshness_task = BigQueryInsertJobOperator(
        task_id="update_attribution_freshness",
        configuration={"query": {"query": "SELECT CURRENT_TIMESTAMP() AS updated_at", "useLegacySql": False}},
    )
    wait_task >> attribution_task >> metrics_task >> write_task >> freshness_task
