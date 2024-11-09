import pandas as pd
from pyproj import Transformer

# Create the transformer object
transformer = Transformer.from_crs("EPSG:32646", "EPSG:4326")

# Read the CSV file
merged_df = pd.read_csv("./nodes_raw.csv")

# Rename the 'combined id' column to 'nodeID'
merged_df = merged_df.rename(columns={'combined_id': 'nodeID'})

# Reproject xCoord and yCoord
xCoord_proj, yCoord_proj = transformer.transform(
    merged_df["xCoord"].values, 
    merged_df["yCoord"].values
)

# Update the DataFrame with the reprojected coordinates
merged_df["xCoord"] = xCoord_proj.round(6)
merged_df["yCoord"] = yCoord_proj.round(6)

# --- Add new columns ---
merged_df["isHealthcare"] = False  # Initialize as False for all nodes
merged_df["old_id"] = merged_df["nodeID"]  # Store original IDs

# --- Identify and update healthcare node IDs ---
def update_node_id(row):
    try:
        # Attempt to convert to integer
        int(row["nodeID"])
        return row
    except ValueError:
        # If not an integer, it's a healthcare node
        row["isHealthcare"] = True
        row["old_id"] = row["nodeID"]  # Store the original ID
        row["nodeID"] = len(merged_df) + 1  # Assign a new integer ID
        return row

merged_df = merged_df.apply(update_node_id, axis=1)

# Select only the desired columns
cleaned_df = merged_df[["nodeID", "xCoord", "yCoord", "isHealthcare", "old_id"]]

cleaned_df.to_csv("./nodes.csv", index=False)