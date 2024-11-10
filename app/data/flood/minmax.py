import pandas as pd

# --- Configuration ---
CSV_FILES = [
    "edges_i_j_10yr.csv",
    "edges_i_j_20yr.csv",
    "edges_i_j_50yr.csv",
]
COLUMN_NAME = "DN_mean"  # Replace with the actual column name

# --- Find Min and Max ---
min_values = []
max_values = []

for file in CSV_FILES:
    df = pd.read_csv(file)
    min_values.append(df[COLUMN_NAME].min())
    max_values.append(df[COLUMN_NAME].max())

# --- Output ---
print("Minimum Values:", min_values)
print("Maximum Values:", max_values)