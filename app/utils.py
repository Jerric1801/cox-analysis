import networkx as nx

def Vij(Sij, fmap, frisk, lrisk):
    # Example implementation (replace with your actual formula)
    speed_reduction_factor = 1 - (0.5 * fmap + 0.3 * frisk + 0.2 * lrisk)
    return Sij * speed_reduction_factor

def calculate_optimal_route(graph, origin, destination, fmap, frisk, lrisk):
    # Example using Dijkstra's algorithm (replace with your algorithm)
    
    # Update edge weights based on scenario
    for u, v, data in graph.edges(data=True):
        data['weight'] = Vij(data['weight'], fmap, frisk, lrisk)

    path = nx.dijkstra_path(graph, origin, destination, weight='weight')
    total_time = nx.dijkstra_path_length(graph, origin, destination, weight='weight')
    return path, total_time