import os

from etl.bq import get_bq_client

def build_daily_features():
    client = get_bq_client()

    sql_path = os.path.join(os.path.dirname(__file__), "..", "sql", "build_features.sql")
    with open(sql_path, "r") as f:
        query = f.read()

    job = client.query(query)
    job.result()

    print("Daily ML features updated.")
