from google.cloud import bigquery
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = "marketing_demo"

def build_daily_features():
    client = bigquery.Client(project=PROJECT_ID)

    sql_path = os.path.join(os.path.dirname(__file__), "..", "sql", "build_features.sql")
    with open(sql_path, "r") as f:
        query = f.read()

    job = client.query(query)
    job.result()

    print("Daily ML features updated.")
