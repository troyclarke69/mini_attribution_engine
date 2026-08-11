import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# NEW: import BigQuery training extractor
from etl.bq_extract_training_data import load_training_data

# ---------------------------------------------------------
# 1. Load real training data from BigQuery
# ---------------------------------------------------------

def get_training_dataframe():
    """
    Loads historical marketing metrics from BigQuery.
    Returns a Pandas DataFrame with features + target.
    """
    print("Loading training data from BigQuery...")
    df = load_training_data()

    # Rename target column to match model expectations
    df = df.rename(columns={"next_day_roas": "target_next_day_roas"})

    return df


# ---------------------------------------------------------
# 2. Split into features (X) and target (y)
# ---------------------------------------------------------

def split_features_target(df):
    """
    Splits the dataset into features (X) and target (y),
    then performs a train/test split.
    """
    X = df.drop(columns=["target_next_day_roas"])
    y = df["target_next_day_roas"]

    return train_test_split(X, y, test_size=0.2, random_state=42)


# ---------------------------------------------------------
# 3. Train the ROAS prediction model
# ---------------------------------------------------------

def train_roas_model(X_train, y_train):
    """
    Trains a RandomForestRegressor model for ROAS prediction.
    """
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model


# ---------------------------------------------------------
# 4. Evaluate the model
# ---------------------------------------------------------

def evaluate_model(model, X_test, y_test):
    """
    Evaluates the model using MSE and R2 metrics.
    """
    preds = model.predict(X_test)

    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print("\n=== MODEL EVALUATION ===")
    print(f"MSE: {mse:.4f}")
    print(f"R2:  {r2:.4f}")


# ---------------------------------------------------------
# 5. Save the model artifact
# ---------------------------------------------------------

def save_model(model, path="ml/model_roas.pkl"):
    """
    Saves the trained model to disk so FastAPI can load it.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"\nModel saved to {path}")


# ---------------------------------------------------------
# 6. Main entrypoint
# ---------------------------------------------------------

def main():
    print("Fetching training data...")
    df = get_training_dataframe()

    print("Splitting into train/test...")
    X_train, X_test, y_train, y_test = split_features_target(df)

    print("Training ROAS model...")
    model = train_roas_model(X_train, y_train)

    print("Evaluating model...")
    evaluate_model(model, X_test, y_test)

    print("Saving model artifact...")
    save_model(model)


if __name__ == "__main__":
    main()
