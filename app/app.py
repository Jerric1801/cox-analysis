import os
import time
from flask import Flask, render_template, request, jsonify
import pandas as pd
import networkx as nx
import folium
from utils import convert_time
from routes import create_graph, calculate_route, prepare_route_data, add_route_to_map 

app = Flask(__name__)

# --- Data Loading ---
NODE_DATA_PATH = "./data/network/nodes.csv"
ROAD_DATA_PATHS = {
    "10yr": "./data/flood/edges_i_j_10yr.csv",
    "20yr": "./data/flood/edges_i_j_20yr.csv",
    "50yr": "./data/flood/edges_i_j_50yr.csv"
}

node_df = pd.read_csv(NODE_DATA_PATH)
road_data = {scenario: pd.read_csv(path) for scenario, path in ROAD_DATA_PATHS.items()}


# --- Flask Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    # --- Create the base map --- 
    m = folium.Map(location=[21.2096, 92.1480], zoom_start=14)
    m._name = "rohingya"
    m._id = "123"

    if request.method == "POST":
        rainfall = float(request.form["rainfall"])
        origin = int(request.form["origin"])
        destination = int(request.form["destination"])
        speed = int(request.form["speed"])
        algorithm = request.form.get("algorithm", "dijkstra")
        method_type = request.form.get("method_type", "deterministic")

        G = create_graph(rainfall, speed, method_type, node_df, road_data)

        try:
            path, execution_time = calculate_route(G, origin, destination, algorithm)

            total_time = nx.shortest_path_length(
                G, source=origin, target=destination, weight="time"
            )
            total_time = convert_time(total_time)

            edges_data = prepare_route_data(G, path)

            # --- Add markers for origin and destination ---
            origin_coords = node_df.loc[node_df["nodeID"] == origin, ["xCoord", "yCoord"]].values[0]
            destination_coords = node_df.loc[node_df["nodeID"] == destination, ["xCoord", "yCoord"]].values[0]
            folium.Marker(location=origin_coords, tooltip=origin).add_to(m)
            folium.Marker(location=destination_coords, tooltip=destination).add_to(m)

            # --- Add route to the existing map ---
            m = add_route_to_map(m, G, path)

            # total_time = convert_time(total_time)

            return render_template(
                "map.html", 
                map=m._repr_html_(), 
                rainfall=rainfall, 
                origin=origin, 
                speed= speed,
                algorithm= algorithm,
                method_type = method_type,
                destination=destination, 
                path=path, 
                total_time= total_time,
                edges_data=edges_data,
                execution_time=round(execution_time,3)
            )

        except nx.NetworkXNoPath:
            return render_template(
                "map.html",
                map=m._repr_html_(), 
                error="No path found between origin and destination." 
            ) 

    else: 

        healthcare_centers = node_df[node_df["isHealthcare"] == True]
        for _, row in healthcare_centers.iterrows():
            folium.Marker(
                location=[row["xCoord"], row["yCoord"]],
                tooltip=f"Healthcare Center (ID: {row['nodeID']})",  # Show node ID
                icon=folium.Icon(color="red", icon="plus"),  # Use a different icon
            ).add_to(m)

        return render_template("map.html", map=m._repr_html_(), nodes=node_df.to_dict('records'), error=None)

if __name__ == "__main__":
    os.environ["FLASK_APP"] = "app.py"
    app.run(debug=True)