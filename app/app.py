import os
import time
from flask import Flask, render_template, request, jsonify
import pandas as pd
import networkx as nx
import folium
from utils import Vij, calculate_optimal_route, convert_time, normalize_DN_mean # Assuming utils.py contains your existing functions

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


# --- Graph Creation ---
def calculate_edge_time(row, speed, scenario, weights=None):
    """Calculates edge traversal time considering disaster risk (deterministic/stochastic)."""

    Sij = speed
    frisk = normalize_DN_mean(row["DN_mean"]) if row["DN_mean"] > 0 else 1
    lrisk = 1 
    alpha, beta, gamma = 0.3, 0.4, 0.3

    if weights:  # Stochastic calculation
        Vij = Sij * (
            weights["10yr"]
            * (1 - alpha * {"10yr": 0.63, "20yr": 0.86, "50yr": 0.95}["10yr"])
            * (1 - beta * frisk)
            * (1 - gamma * lrisk)
            + weights["20yr"]
            * (1 - alpha * {"10yr": 0.63, "20yr": 0.86, "50yr": 0.95}["20yr"])
            * (1 - beta * frisk)
            * (1 - gamma * lrisk)
            + weights["50yr"]
            * (1 - alpha * {"10yr": 0.63, "20yr": 0.86, "50yr": 0.95}["50yr"])
            * (1 - beta * frisk)
            * (1 - gamma * lrisk)
        )
    else:  # Deterministic calculation
        fmap = {"10yr": 0.63, "20yr": 0.86, "50yr": 0.95}[scenario]
        Vij = Sij * (1 - alpha * fmap) * (1 - beta * frisk) * (1 - gamma * lrisk)

    length_km = row["length"]/1000

    return length_km / Vij


def create_graph(rainfall, speed, method_type):
    """Creates a NetworkX graph with nodes and edges based on the chosen method."""

    G = nx.Graph()
    for _, row in node_df.iterrows():
        G.add_node(row["nodeID"], pos=(row["xCoord"], row["yCoord"]))

    if method_type == "deterministic":
        scenario = determine_scenario(rainfall)  
        df = road_data[scenario]
        add_edges_to_graph(G, df, speed, scenario)
    elif method_type == "stochastic":
        weights = {"10yr": 10/17, "20yr": 5/17, "50yr": 2/17}
        for scenario, df in road_data.items():
            add_edges_to_graph(G, df, speed, scenario, weights)

    return G


def determine_scenario(rainfall):
    """Determines the flood scenario based on rainfall."""
    if 0 <= rainfall <= 160000:
        return "10yr"
    elif rainfall <= 180000:
        return "20yr"
    else:
        return "50yr"


def add_edges_to_graph(G, df, speed, scenario, weights=None):
    """Adds edges to the graph with calculated times."""
    for _, row in df.iterrows():
        if row["node1"] in G.nodes and row["node2"] in G.nodes:
            time_taken = calculate_edge_time(row, speed, scenario, weights)
            if G.has_edge(row["node1"], row["node2"]):
                if time_taken < G[row["node1"]][row["node2"]]["time"]:
                    G[row["node1"]][row["node2"]]["time"] = time_taken
                    G[row["node1"]][row["node2"]]["scenario"] = scenario
            else:
                G.add_edge(
                    row["node1"],
                    row["node2"],
                    length=row["length"],
                    time=time_taken,
                    scenario=scenario,
                )
        else:
            print(
                f"Edge between {row['node1']} and {row['node2']} skipped because nodes are missing."
            )


# --- Route Calculation and Map Visualization ---
def heuristic(a, b, G):
    """Heuristic function for A* algorithm."""
    a_x, a_y = G.nodes[a]["pos"]
    b_x, b_y = G.nodes[b]["pos"]
    return ((a_x - b_x) ** 2 + (a_y - b_y) ** 2) ** 0.5


def add_route_to_map(m, G, path):
    """Adds the calculated route to the Folium map."""
    path_edges = list(zip(path, path[1:]))
    for edge in path_edges:
        start_coords = G.nodes[edge[0]]["pos"]
        end_coords = G.nodes[edge[1]]["pos"]
        folium.PolyLine(
            [start_coords, end_coords], color="blue", weight=2.5, opacity=1
        ).add_to(m)
    return m


def calculate_route(G, origin, destination, algorithm):
    """Calculates the shortest path based on the selected algorithm."""
    start_time = time.time()
    if algorithm == "dijkstra":
        path = nx.shortest_path(G, source=origin, target=destination, weight="time")
    elif algorithm == "heuristic":
        path = nx.astar_path(
            G,
            source=origin,
            target=destination,
            heuristic=lambda a, b: heuristic(a, b, G),
            weight="time",
        )
    else:
        raise ValueError("Invalid algorithm selected.")
    end_time = time.time()
    return path, end_time - start_time


def prepare_route_data(G, path):
    """Prepares data for display on the map."""
    path_edges = list(zip(path, path[1:]))
    edges_data = []
    for edge in path_edges:
        edge_data = G.get_edge_data(*edge)
        edges_data.append(
            {
                "edge": edge,
                "length": edge_data["length"],
                "time": round(edge_data["time"], 3),
                "scenario": edge_data["scenario"],
            }
        )
    return edges_data

# --- Flask Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    # --- Create the base map --- 
    m = folium.Map(location=[21.2096, 92.1480], zoom_start=14)
    m._name = "rohingya"
    m._id = "123"

    print("app started")

    if request.method == "POST":
        rainfall = float(request.form["rainfall"])
        origin = int(request.form["origin"])
        destination = int(request.form["destination"])
        speed = int(request.form["speed"])
        algorithm = request.form.get("algorithm", "dijkstra")
        method_type = request.form.get("method_type", "deterministic")

        G = create_graph(rainfall, speed, method_type)

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
                total_time=round(total_time,3),
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
        return render_template("map.html", map=m._repr_html_(), nodes=node_df.to_dict('records'), error=None)

if __name__ == "__main__":
    os.environ["FLASK_APP"] = "app.py"
    app.run(debug=True)