import pandas as pd

# --- Load the node data ---
node_df = pd.read_csv("./network/nodes.csv")

# --- Function to process each road CSV ---
def process_road_csv(road_csv_path, output_filename): 
    road_df = pd.read_csv(road_csv_path)

    # Rename columns
    road_df = road_df.rename(columns={
        "fid": "roadID",
        "combined_id_min": "node1",
        "combined_id_max": "node2",
        # "time_needed (min)": "time"
    })

    # Round length to 3 decimal places
    road_df["length"] = road_df["length"].round(3)

    # --- Merge with node data using 'old_id' ---
    road_df = pd.merge(road_df, node_df, left_on="node1", right_on="old_id", how="left")
    road_df = road_df.rename(columns={
        "xCoord": "node1_Xcoord",
        "yCoord": "node1_Ycoord",
        "isHealthcare": "isHealthcare1"
    })
    road_df = road_df.drop(columns=["old_id"])  # Drop the 'old_id' column

    road_df = pd.merge(road_df, node_df, left_on="node2", right_on="old_id", how="left")
    road_df = road_df.rename(columns={
        "xCoord": "node2_Xcoord",
        "yCoord": "node2_Ycoord",
        "isHealthcare": "isHealthcare2"
    })
    road_df = road_df.drop(columns=["old_id"])  # Drop the 'old_id' column

    # Select only the desired columns and rename nodeID to node1 and node2
    road_df = road_df[[
        "roadID", "nodeID_x", "nodeID_y", "node1_Xcoord", "node1_Ycoord", 
        "node2_Xcoord", "node2_Ycoord", "DN_mean", "length", 
        "isHealthcare1", "isHealthcare2"  # Include healthcare columns
    ]]
    road_df = road_df.rename(columns={
        "nodeID_x": "node1",
        "nodeID_y": "node2"
    })

    road_df = road_df.dropna(subset=["node1", "node2"])

    # Save the cleaned DataFrame
    road_df.to_csv(output_filename, index=False) 

# --- Process each of the 3 CSV files ---
csv_files = [
    "./flood/raw/edges_i_j_10yr_raw.csv", 
    "./flood/raw/edges_i_j_20yr_raw.csv", 
    "./flood/raw/edges_i_j_50yr_raw.csv"  
]

output_filenames = [
    "./flood/edges_i_j_10yr.csv", 
    "./flood/edges_i_j_20yr.csv", 
    "./flood/edges_i_j_50yr.csv"  
]

for csv_file, output_filename in zip(csv_files, output_filenames):
    process_road_csv(csv_file, output_filename)