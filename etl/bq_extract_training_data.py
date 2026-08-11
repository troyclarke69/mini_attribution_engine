import pandas as pd
from google.cloud import bigquery
from etl.bq import DATASET_ID, PROJECT_ID, get_bq_client

# ---------------------------------------------------------
# Load training data from BigQuery
# ---------------------------------------------------------

def load_training_data():
    """
    Extract historical marketing metrics from BigQuery
    and return a Pandas DataFrame suitable for ML training.
    """

    client = get_bq_client()
    if client is None:
        raise RuntimeError("BigQuery client is not initialized. Check credentials.")

    query = f"""
        SELECT
            metric_date,
            spend,
            attributed_revenue,
            conversions,
            cac,
            roas,
            rolling_7d_roas,
            rolling_7d_spend,
            rolling_7d_conversions,
            rolling_7d_volatility,
            next_day_roas
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_campaign_metrics_features`
    """

    # Fill in project + dataset from environment variables
    # project_id = PROJECT_ID
    # dataset = DATASET_ID
    # final_query = query.format(project=project_id, dataset=dataset)

    df = client.query(query).to_dataframe()

    if df.empty:
        raise RuntimeError("BigQuery returned no training data.")

    return df
