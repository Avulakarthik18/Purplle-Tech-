import pandas as pd

df = pd.read_csv("data/dataset/pos_transactions.csv")

print("Columns:", df.columns)
print(df.head())
