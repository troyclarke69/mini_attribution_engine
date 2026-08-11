import joblib
import pandas as pd

def inspect_feature_importance():
    model = joblib.load("ml/model_roas.pkl")

    # Load the same training dataframe to get feature names
    from ml.data_loader import get_training_dataframe
    df = get_training_dataframe()

    feature_names = df.drop(columns=["target_next_day_roas"]).columns

    importances = model.feature_importances_

    fi = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    print("\n=== FEATURE IMPORTANCE ===")
    print(fi)
