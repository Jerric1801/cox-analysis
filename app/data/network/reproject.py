import pandas as pd
from pyproj import Transformer

# Create the transformer object
transformer = Transformer.from_crs("EPSG:4326","EPSG:32646")

# Read the CSV file
merged_df = pd.read_csv("./filtered_nodes.csv")

# Reproject xCoord and yCoord
xCoord_proj, yCoord_proj = transformer.transform(
    merged_df["xCoord"].values, 
    merged_df["yCoord"].values
)

# Add the projected coordinates to the DataFrame
merged_df["xCoord_proj"] = xCoord_proj
merged_df["yCoord_proj"] = yCoord_proj

# Export the updated DataFrame to a new CSV file
merged_df.to_csv("./filtered_nodes_projected.csv", index=False)