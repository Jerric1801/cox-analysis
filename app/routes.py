import time
import networkx as nx
import folium
from utils import normalize_DN_mean,convert_time


# --- Graph Creation ---
def calculate_edge_time(row, speed, scenario, weights=None):
    """Calculates edge traversal time considering disaster risk (deterministic/stochastic)."""

    Sij = speed
    frisk = normalize_DN_mean(row["DN_mean"]) if row["DN_mean"] > 0 else 1
    lrisk = 1  - row["Susceptibi_mean"]
    alpha, beta, gamma = 0.3, 0.4, 0.3
    lrisk = 1 if lrisk is None or lrisk != lrisk else lrisk  

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

    assert frisk >= 0, f"Unexpected frisk value: {frisk}"
    assert speed > 0, f"Speed must be positive: {speed}"
    assert Vij > 0, f"Vij should be positive: {Vij}" 


    return length_km / Vij


def create_graph(rainfall, speed, method_type, node_df, road_data):
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
    if 0 <= rainfall <= 26:
        return "10yr"
    elif rainfall <= 32:
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
                    int(row["node1"]),
                    int(row["node2"]),
                    length=row["length"],
                    time=time_taken,
                    scenario=scenario,
                )
        else:
            print(
                f"Edge between {row['node1']} and {row['node2']} skipped because nodes are missing."
            )


# --- Route Calculation and Map Visualization ---
# def heuristic(a, b, G):
#     """Heuristic function for A* algorithm."""
#     a_x, a_y = G.nodes[a]["pos"]
#     b_x, b_y = G.nodes[b]["pos"]
#     return ((a_x - b_x) ** 2 + (a_y - b_y) ** 2) ** 0.5

def heuristic(a, b, G):
  """Manhattan distance heuristic for A* algorithm."""
  a_x, a_y = G.nodes[a]["pos"]
  b_x, b_y = G.nodes[b]["pos"]
  return abs(a_x - b_x) + abs(a_y - b_y)

# import random

# def heuristic(a, b, G):
#   """
#   A non-admissible heuristic that randomly overestimates 
#   the distance to the goal, leading to unpredictable and 
#   potentially suboptimal paths.
#   """
#   a_x, a_y = G.nodes[a]["pos"]
#   b_x, b_y = G.nodes[b]["pos"]
#   distance = ((a_x - b_x) ** 2 + (a_y - b_y) ** 2) ** 0.5
#   return distance * (1 + random.uniform(0, 1)) 

# def heuristic(a, b, G):
#   """
#   A greedy heuristic that heavily favors nodes closer to the goal 
#   in terms of Euclidean distance, potentially leading to suboptimal paths.
#   """
#   a_x, a_y = G.nodes[a]["pos"]
#   b_x, b_y = G.nodes[b]["pos"]
#   distance = ((a_x - b_x) ** 2 + (a_y - b_y) ** 2) ** 0.5
#   return distance * 0.1


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
    execution_time_seconds = end_time - start_time

    # Format the time for better presentation
    return path, execution_time_seconds





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
                "time": convert_time(edge_data["time"]),
                "scenario": edge_data["scenario"],
            }
        )
    return edges_data
