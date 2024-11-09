import os
from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
import folium
from utils import Vij, calculate_optimal_route  # Assuming utils.py contains your existing functions

app = Flask(__name__)

# --- Load node data ---
node_df = pd.read_csv("./data/network/nodes.csv")

# --- Load road data for different scenarios ---
road_data = {
    "10yr": pd.read_csv("./data/flood/edges_i_j_10yr.csv"),
    "20yr": pd.read_csv("./data/flood/edges_i_j_20yr.csv"),
    "50yr": pd.read_csv("./data/flood/edges_i_j_50yr.csv")
}

# --- Function to calculate time taken for a single edge ---
def calculate_edge_time(row, rainfall):
    # 1. Determine scenario based on rainfall
    if rainfall <= 100:  # Example threshold, adjust as needed
        scenario = "10yr"
    elif rainfall <= 200:
        scenario = "20yr"
    else:
        scenario = "50yr"

    # 2. Get relevant road data
    road_data_scenario = road_data[scenario]

    # 3. ... (Rest of your formula to calculate time_taken using row and road_data_scenario)
    #    This will involve accessing f_risk, l_risk, etc. from road_data_scenario
    #    and performing calculations based on your formula.
    #    Make sure to replace the following with your actual calculation
    adjusted_velocity = 10  # Example calculation
    time_taken = row["length"] / adjusted_velocity

    return time_taken


# --- Flask routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        rainfall = float(request.form["rainfall"])
        origin = int(request.form["origin"])
        destination = int(request.form["destination"])

        print(rainfall)
        print(origin, destination)

        # --- Create NetworkX graph ---
        G = nx.Graph()
        for _, row in node_df.iterrows():
            G.add_node(row["nodeID"], pos=(row["xCoord"], row["yCoord"]))

        for scenario, df in road_data.items():
            for _, row in df.iterrows():
                if row["node1"] in G.nodes and row["node2"] in G.nodes:
                    G.add_edge(row["node1"], row["node2"],
                            length=row["length"],
                            time=calculate_edge_time(row, rainfall),
                            scenario=scenario,
                            # Add other edge attributes if present
                            # f_risk=row["f_risk"],
                            # l_risk=row["l_risk"],
                            # etc.
                    )
                else:
                    # Debug: Print missing nodes if any
                    print(f"Edge between {row['node1']} and {row['node2']} skipped because nodes are missing.")

        print(G)

        # --- Find shortest path based on time ---
        try:
            path = nx.shortest_path(G, source=origin, target=destination, weight="length")
            total_time = nx.shortest_path_length(G, source=origin, target=destination, weight="length")
            # path = nx.shortest_path(G, source=origin, target=destination)
            # total_time = nx.shortest_path_length(G, source=origin, target=destination)
            path_edges = list(zip(path, path[1:]))
            
            print(path)

            # --- Prepare data for display ---
            edges_data = []
            for edge in path_edges:
                edge_data = G.get_edge_data(*edge)
                edges_data.append({
                    "edge": edge,
                    "length": edge_data["length"],
                    "time": edge_data["time"],
                    "scenario": edge_data["scenario"]
                })

            print(len(edge_data))

            # --- Create Folium map ---
            m = folium.Map(location=[21.3143, 92.1818], zoom_start=12)

            print(m)

            # --- Add markers for origin and destination ---
            origin_coords = node_df.loc[node_df["nodeID"] == origin, ["xCoord", "yCoord"]].values[0]
            destination_coords = node_df.loc[node_df["nodeID"] == destination, ["xCoord", "yCoord"]].values[0]
            folium.Marker(location=origin_coords, tooltip=origin).add_to(m)
            folium.Marker(location=destination_coords, tooltip=destination).add_to(m)

            # --- Add route lines to the map ---
            for edge in path_edges:
                start_coords = G.nodes[edge[0]]["pos"]
                end_coords = G.nodes[edge[1]]["pos"]
                folium.PolyLine([start_coords, end_coords], color="blue", weight=2.5, opacity=1).add_to(m)

            return render_template("map.html", map=m._repr_html_(), 
                                   rainfall=rainfall, 
                                   origin=origin, 
                                   destination=destination, 
                                   path=path, 
                                   total_time=total_time,
                                   edges_data=edges_data)

        except nx.NetworkXNoPath:
            return "No path found between origin and destination."

    return render_template("map.html")

if __name__ == "__main__":
    os.environ["FLASK_APP"] = "app.py"
    app.run(debug=True)