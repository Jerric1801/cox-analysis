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

def convert_time(total_hours):
  """Converts total time in hours (float) to total minutes (integer).

  Args:
    total_hours: The total time in hours as a float.

  Returns:
    An integer representing the total time in minutes.
  """
  total_minutes = total_hours * 60  # Convert hours to minutes
  return total_minutes


def normalize_DN_mean(DN_mean):
  """Normalizes DN_mean values to a 0-1 range. Values between 6 & 9

  Args:
    DN_mean: The original DN_mean value.

  Returns:
    The normalized DN_mean value between 0 and 1.
  """
  min_value = 5.999
  max_value = 9.001
  normalized_value = (DN_mean - min_value) / (max_value - min_value)
  return normalized_value