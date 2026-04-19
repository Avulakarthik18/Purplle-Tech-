import pandas as pd
import os

def load_pos_data():
    # Adjusted path to match project structure
    pos_path = os.path.join(os.path.dirname(__file__), "..", "data", "dataset", "pos_transactions.csv")
    if not os.path.exists(pos_path):
        # Fallback if run from a different CWD
        pos_path = "data/dataset/pos_transactions.csv"
        
    df = pd.read_csv(pos_path)

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df
