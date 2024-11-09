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

# --- Helper Functions ---
def calculate_edge_time(row, speed, scenario):  # Add scenario argument
    """Calculates the time taken to traverse an edge considering disaster risk."""

    # --- Parameters ---
    Sij = speed 
    fmap = {"10yr": 0.95, "20yr": 0.86, "50yr": 0.63}[scenario] 
    frisk = normalize_DN_mean(row["DN_mean"]) if row["DN_mean"] > 0 else 0.1 

    # lrisk = row["l_risk"]  
    lrisk = 0.1
    alpha, beta, gamma = 0.7, 0.3, 0.2  

    # --- Adjusted Velocity Function ---
    # Vij = Sij * (1 - alpha * fmap) * (1 - beta * frisk) * (1 - gamma * lrisk) 
    Vij = Sij * (1 - alpha * fmap) * (1 - beta * frisk)

    # --- Time Calculation ---
    time_taken = row["length"] / Vij 

    return time_taken

def create_graph(rainfall, speed):
    """Creates a NetworkX graph with nodes and edges."""
    G = nx.Graph()
    for _, row in node_df.iterrows():
        G.add_node(row["nodeID"], pos=(row["xCoord"], row["yCoord"]))

    if 0 <= rainfall <= 160000:  
        scenario = "10yr"
    elif rainfall <= 180000:
        scenario = "20yr"
    else:
        scenario = "50yr"

    # Use the determined scenario to get the correct road data
    df = road_data[scenario] 

    for _, row in df.iterrows(): 
        if row["node1"] in G.nodes and row["node2"] in G.nodes:
            G.add_edge(
                row["node1"], 
                row["node2"],
                length=row["length"],
                time=calculate_edge_time(row, speed, scenario),  
                scenario=scenario
            )
        else:
            # Debug: Print missing nodes if any
            print(f"Edge between {row['node1']} and {row['node2']} skipped because nodes are missing.")
    return G

def add_route_to_map(m, G, path):
    """Adds the route to the given Folium map."""
    path_edges = list(zip(path, path[1:]))
    for edge in path_edges:
        start_coords = G.nodes[edge[0]]["pos"]
        end_coords = G.nodes[edge[1]]["pos"]
        folium.PolyLine([start_coords, end_coords], color="blue", weight=2.5, opacity=1).add_to(m)
    return m

def heuristic(a, b, G):  # Add G as argument
    a_x, a_y = G.nodes[a]['pos']
    b_x, b_y = G.nodes[b]['pos']
    return ((a_x - b_x) ** 2 + (a_y - b_y) ** 2) ** 0.5


# --- Flask Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    # --- Create the base map --- 
    m = folium.Map(location=[21.2096, 92.1480], zoom_start=14)
    m._name = "rohingya"
    m._id = "123"

    # # --- Add markers for all nodes ---
    # m.add_child(folium.ClickForMarker(popup="Selected Node"))

    if request.method == "POST":
        rainfall = float(request.form["rainfall"])
        origin = int(request.form["origin"])
        destination = int(request.form["destination"])
        speed = int(request.form["speed"])
        
        print(request.form)
        if "algorithm" in request.form:  # Check if checkbox is checked
            algorithm = "heuristic"  
        else:
            algorithm = "dijkstra"


        G = create_graph(rainfall, speed)

        try:
            start_time = time.time()
            if algorithm == "dijkstra":
                path = nx.shortest_path(G, source=origin, target=destination, weight="time")
            elif algorithm == "heuristic":
                path = nx.astar_path(G, source=origin, target=destination, heuristic=lambda a, b: heuristic(a, b, G), weight="time") 
            else:
                return "Invalid algorithm selected."
            
            end_time = time.time()  # Record end time
            execution_time = end_time - start_time 

            total_time = nx.shortest_path_length(G, source=origin, target=destination, weight="time")
            
            path_edges = list(zip(path, path[1:]))

            # --- Prepare data for display ---
            edges_data = []
            for edge in path_edges:
                edge_data = G.get_edge_data(*edge)
                edges_data.append({
                    "edge": edge,
                    "length": edge_data["length"],
                    "time": round(edge_data["time"], 3),
                    "scenario": edge_data["scenario"]
                })

            # --- Add markers for origin and destination ---
            origin_coords = node_df.loc[node_df["nodeID"] == origin, ["xCoord", "yCoord"]].values[0]
            destination_coords = node_df.loc[node_df["nodeID"] == destination, ["xCoord", "yCoord"]].values[0]
            folium.Marker(location=origin_coords, tooltip=origin).add_to(m)
            folium.Marker(location=destination_coords, tooltip=destination).add_to(m)

            # --- Add route to the existing map ---
            m = add_route_to_map(m, G, path)

            total_time = convert_time(total_time)

            return render_template(
                "map.html", 
                map=m._repr_html_(), 
                rainfall=rainfall, 
                origin=origin, 
                destination=destination, 
                path=path, 
                total_time=total_time,
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