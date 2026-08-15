import os
import pandas as pd

# IMPORTANT: use the unified BigQuery client
from etl.bq import get_bq_client


def load_training_data():
    """
    Fetches historical marketing metrics from BigQuery.
    Returns a raw Pandas DataFrame.
    """

    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")

    if not project_id or not dataset:
        raise ValueError(
            f"Missing GCP_PROJECT_ID or BQ_DATASET. "
            f"Got project_id={project_id}, dataset={dataset}"
        )

    # FIXED: use authenticated client
    client = get_bq_client()

    table = f"{project_id}.{dataset}.fact_campaign_metrics_features"

    query = f"""
        SELECT
            metric_date,
            IFNULL(spend, 0) AS spend,
            IFNULL(conversions, 0) AS conversions,
            IFNULL(roas, 0) AS roas,
            IFNULL(rolling_7d_spend, 0) AS rolling_7d_spend,
            IFNULL(rolling_7d_roas, 0) AS rolling_7d_roas,
            IFNULL(rolling_7d_conversions, 0) AS rolling_7d_conversions,
            IFNULL(rolling_7d_volatility, 0) AS rolling_7d_volatility,
            IFNULL(cac, 0) AS cac,
            IFNULL(attributed_revenue, 0) AS attributed_revenue,
            IFNULL(next_day_roas, 0) AS next_day_roas
        FROM `{table}`
        WHERE next_day_roas IS NOT NULL
        ORDER BY metric_date ASC
    """

    df = client.query(query).to_dataframe()

    print("Loaded rows:", len(df))
    print("Columns:", df.columns.tolist())

    return df


def get_training_dataframe():
    """
    Loads historical marketing metrics from BigQuery.
    Cleans NaNs, renames target column, and returns a training-ready DataFrame.
    """
    print("Loading training data from BigQuery...")
    df = load_training_data()

    # Drop rows where the target is NaN
    df = df.dropna(subset=["next_day_roas"])

    # Rename target column FIRST (keeps consistency)
    df = df.rename(columns={"next_day_roas": "target_next_day_roas"})

    return df


def get_latest_feature_row():
    """
    Fetches the most recent row of features for prediction.
    Used by FastAPI /predict_next_day_roas endpoint.
    """

    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")

    if not project_id or not dataset:
        raise ValueError(
            f"Missing GCP_PROJECT_ID or BQ_DATASET. "
            f"Got project_id={project_id}, dataset={dataset}"
        )

    # FIXED: use authenticated client
    client = get_bq_client()

    table = f"{project_id}.{dataset}.fact_campaign_metrics_features"

    query = f"""
        SELECT
            metric_date,
            IFNULL(spend, 0) AS spend,
            IFNULL(conversions, 0) AS conversions,
            IFNULL(roas, 0) AS roas,
            IFNULL(rolling_7d_spend, 0) AS rolling_7d_spend,
            IFNULL(rolling_7d_roas, 0) AS rolling_7d_roas,
            IFNULL(rolling_7d_conversions, 0) AS rolling_7d_conversions,
            IFNULL(rolling_7d_volatility, 0) AS rolling_7d_volatility,
            IFNULL(cac, 0) AS cac,
            IFNULL(attributed_revenue, 0) AS attributed_revenue,
            IFNULL(next_day_roas, 0) AS next_day_roas
        FROM `{table}`
        WHERE next_day_roas IS NOT NULL
        ORDER BY metric_date DESC
        LIMIT 1
    """

    df = client.query(query).to_dataframe()

    df = df.rename(columns={"next_day_roas": "target_next_day_roas"})

    print("Loaded rows:", len(df))
    print("Columns:", df.columns.tolist())

    return df


def get_latest_feature_row_for_prediction():
    """
    Fetches the single most recent feature row for live prediction.

    Unlike get_latest_feature_row() above, this does NOT filter on
    next_day_roas being known. That column is tomorrow's target, so the
    truly-latest row can never have it populated - filtering on it meant
    live serving was silently falling back to an older row every time,
    regardless of how fresh the pipeline actually was.
    """

    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")

    if not project_id or not dataset:
        raise ValueError(
            f"Missing GCP_PROJECT_ID or BQ_DATASET. "
            f"Got project_id={project_id}, dataset={dataset}"
        )

    client = get_bq_client()

    table = f"{project_id}.{dataset}.fact_campaign_metrics_features"

    query = f"""
        SELECT
            metric_date,
            IFNULL(spend, 0) AS spend,
            IFNULL(conversions, 0) AS conversions,
            IFNULL(roas, 0) AS roas,
            IFNULL(rolling_7d_spend, 0) AS rolling_7d_spend,
            IFNULL(rolling_7d_roas, 0) AS rolling_7d_roas,
            IFNULL(rolling_7d_conversions, 0) AS rolling_7d_conversions,
            IFNULL(rolling_7d_volatility, 0) AS rolling_7d_volatility,
            IFNULL(cac, 0) AS cac,
            IFNULL(attributed_revenue, 0) AS attributed_revenue
        FROM `{table}`
        ORDER BY metric_date DESC
        LIMIT 1
    """

    df = client.query(query).to_dataframe()

    print("Loaded prediction feature row for:", df["metric_date"].iloc[0] if len(df) else "N/A")

    return df
