import os
import json
import pandas as pd

DATA_PATH = "data/dataset"

def inspect_dataset():
    print("\n[DIR] Checking dataset structure...\n")

    for root, dirs, files in os.walk(DATA_PATH):
        level = root.replace(DATA_PATH, "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}[DIR] {os.path.basename(root)}")
        subindent = " " * 2 * (level + 1)
        for f in files:
            print(f"{subindent}[FILE] {f}")

    print("\n[CHECK] Checking important files...\n")

    # Check JSON
    layout_path = os.path.join(DATA_PATH, "store_layout.json")
    if os.path.exists(layout_path):
        with open(layout_path) as f:
            data = json.load(f)
            print("[OK] store_layout.json loaded")
            print("Sample:", list(data.keys())[:3])
    else:
        print("[MISSING] store_layout.json missing")

    # Check CSV
    pos_path = os.path.join(DATA_PATH, "pos_transactions.csv")
    if os.path.exists(pos_path):
        df = pd.read_csv(pos_path)
        print("[OK] pos_transactions.csv loaded")
        print(df.head())
    else:
        print("[MISSING] pos_transactions.csv missing")

if __name__ == "__main__":
    inspect_dataset()
