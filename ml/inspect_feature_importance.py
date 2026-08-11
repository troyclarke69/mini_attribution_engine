import joblib
import pandas as pd
from ml.data_loader import get_training_dataframe

def main():
    model = joblib.load("ml/model_roas.pkl")

    df = get_training_dataframe()

    # Drop non-feature columns
    feature_names = df.drop(columns=["metric_date", "target_next_day_roas"]).columns.tolist()

    importances = model.feature_importances_

    if len(importances) != len(feature_names):
        print("\nERROR: Feature count mismatch")
        print(f"Model importances: {len(importances)}")
        print(f"Feature names:     {len(feature_names)}")
        return

    fi = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    print("\n=== FEATURE IMPORTANCE ===")
    print(fi.to_string(index=False))

if __name__ == "__main__":
    main()
