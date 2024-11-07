import os
from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
import folium
from utils import Vij, calculate_optimal_route

app = Flask(__name__)

# Sample network data (replace with your actual data)
network_data = pd.DataFrame({
    'origin_node': ['A', 'A', 'B', 'C'],
    'destination_node': ['B', 'C', 'D', 'D'],
    'distance': [5, 10, 8, 6]
})

# Create NetworkX graph
graph = nx.Graph()
for index, row in network_data.iterrows():
    graph.add_edge(row['origin_node'], row['destination_node'], weight=row['distance'])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        origin = request.form["origin"]
        destination = request.form["destination"]

        # Example scenario parameters (replace with your actual parameters)
        fmap = 0.2  
        frisk = 0.1
        lrisk = 0.05

        # Calculate optimal route
        route, total_time = calculate_optimal_route(
            graph, origin, destination, fmap, frisk, lrisk
        )

        # Create Folium map
        m = folium.Map(location=[21.3143, 92.1818], zoom_start=12)  

        # Add markers for origin and destination (example)
        folium.Marker([21.31, 92.18], tooltip=origin).add_to(m)  
        folium.Marker([21.32, 92.19], tooltip=destination).add_to(m)  

        # ... (Add route lines to the map)

        return render_template("map.html", map=m._repr_html_())

    return render_template("map.html")


if __name__ == "__main__":
    os.environ["FLASK_APP"] = "app.py" 
    app.run(debug=True)