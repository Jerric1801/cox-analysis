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
  """Converts total time in hours (float) to hours, minutes, and seconds.

  Args:
    total_hours: The total time in hours as a float.

  Returns:
    A string representing the time in HH:MM:SS format.
  """
  hours = int(total_hours)
  minutes = int((total_hours - hours) * 60)
  seconds = int(((total_hours - hours) * 60 - minutes) * 60)
  return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def normalize_DN_mean(DN_mean):
  """Normalizes DN_mean values to a 0-1 range.

  Args:
    DN_mean: The original DN_mean value.

  Returns:
    The normalized DN_mean value between 0 and 1.
  """
  min_value = 6.5
  max_value = 9
  normalized_value = (DN_mean - min_value) / (max_value - min_value)
  return normalized_value