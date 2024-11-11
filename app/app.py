import os
import time
from flask import Flask, render_template, request, jsonify
import pandas as pd
import networkx as nx
import folium
from utils import convert_time
from routes import create_graph, calculate_route, prepare_route_data, add_route_to_map 
import random
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

# --- Data Loading ---
NODE_DATA_PATH = "./data/network/filtered_nodes.csv"
ROAD_DATA_PATHS = {
    "10yr": "./data/flood/edges_i_j_10yr_joined.csv",
    "20yr": "./data/flood/edges_i_j_20yr_joined.csv",
    "50yr": "./data/flood/edges_i_j_50yr_joined.csv"
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

            if execution_time < 1:
                execution_time_ms = execution_time * 1000  # Convert to milliseconds
                execution_time_str = f"{execution_time_ms:.2f} milliseconds"
            else:
                execution_time_str = f"{execution_time:.2f} seconds"


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
                execution_time=execution_time_str 
            )

        except nx.NetworkXNoPath:
            return render_template(
                "map.html",
                map=m._repr_html_(), 
                error="No path found between origin and destination." 
            ) 

    else: 
        return render_template("map.html", map=m._repr_html_(), nodes=node_df.to_dict('records'), error=None)
    

@app.route("/simulation", methods=["GET", "POST"])
def simulation():
    if request.method == "POST":
        # Get parameters from the form
        num_simulations = int(request.form.get("num_simulations", 1000))
        rainfall = int(request.form.get("rainfall", 500))
        speed = int(request.form.get("speed", 60))
        algorithm = request.form.get("algorithm", "heuristic")
        method_type = request.form.get("method_type", "deterministic")

        G = create_graph(rainfall, speed, method_type, node_df, road_data)

        results = []
        no_path_count = 0

        for _ in range(num_simulations):
            origin = random.choice(node_df['nodeID'].tolist())
            destination = random.choice(node_df['nodeID'].tolist())
            while origin == destination:  # Ensure origin and destination are different
                destination = random.choice(node_df['nodeID'].tolist())

            try:
                path, execution_time = calculate_route(G, origin, destination, algorithm)
                total_time = nx.shortest_path_length(G, source=origin, target=destination, weight="time")
                results.append({
                    "origin": origin,
                    "destination": destination,
                    "total_time": total_time,
                    "execution_time": execution_time
                })
            except nx.NetworkXNoPath:
                no_path_count += 1
        

        analysis = {
            "overall_avg_time": convert_time(sum(result['total_time'] for result in results) / len(results)),
            "overall_avg_exec_time": f"{((sum(result['execution_time'] for result in results) / len(results)) * 1000):.2f} ms",
            "drop_out_rate": (no_path_count / num_simulations) * 100 
        }


        drop_out_rate = (no_path_count / num_simulations) * 100
        print(drop_out_rate)    

        return render_template(
            "simulation_results.html", 
            results=results, 
            analysis=analysis,
            # plot_url=plot_url,
            rainfall=rainfall, 
            speed=speed,
            algorithm=algorithm,
            method_type=method_type
        )
    else:  # GET request
        # Render the template with the form and default values
        return render_template(
            "simulation_results.html", 
            results=[] , # No results to display initially
            analysis=[]
        )

if __name__ == "__main__":
    os.environ["FLASK_APP"] = "app.py"
    app.run(debug=True)