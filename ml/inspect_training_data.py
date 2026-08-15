import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from etl.bq_extract_training_data import load_training_data

def main():
    df = load_training_data()

    print("\n=== HEAD ===")
    print(df.head())

    print("\n=== SUMMARY ===")
    print(df.describe())

    print("\n=== COLUMNS ===")
    print(df.columns)

if __name__ == "__main__":
    main()
