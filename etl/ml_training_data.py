from google.cloud import bigquery
from google.oauth2 import service_account
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def extract_roas_training_data():
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    client = bigquery.Client(project=PROJECT_ID, credentials=credentials)

    sql_path = os.path.join(os.path.dirname(__file__), "..", "sql", "extract_roas_training_data.sql")
    with open(sql_path, "r") as f:
        query = f.read()

    df = client.query(query).to_dataframe()
    print(f"Extracted {len(df)} training rows for ROAS prediction.")
    return df
