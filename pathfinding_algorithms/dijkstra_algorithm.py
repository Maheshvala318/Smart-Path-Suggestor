"""
Dijkstra's Algorithm Implementation
For Smart Path Suggestor - Campus Navigation
Source: presentation.ipynb

This module implements Dijkstra's algorithm to find the shortest path
between two locations on the Gujarat University campus.
"""

import networkx as nx
import matplotlib.pyplot as plt


class Graph:
    """Graph representation using adjacency matrix for campus pathfinding."""

    def __init__(self, size):
        """
        Initialize graph with given number of vertices.

        Args:
            size: Number of vertices (nodes) in the graph
        """
        self.adj_matrix = [[0] * size for _ in range(size)]
        self.size = size
        self.vertex_data = [''] * size
        self.edges = []
        self.node_positions = {}
        self.display_labels = {}

    def add_vertex_data(self, vertex, data, position):
        """Add a vertex with label and position for visualization."""
        if 0 <= vertex < self.size:
            cleaned_data = ' '.join(data.strip().split())
            self.vertex_data[vertex] = cleaned_data
            self.node_positions[vertex] = position
            self.display_labels[vertex] = data

    def add_edge(self, u, v, weight):
        """Add an edge between vertices u and v with given weight."""
        if 0 <= u < self.size and 0 <= v < self.size:
            self.adj_matrix[u][v] = weight
            self.adj_matrix[v][u] = weight
            self.edges.append((u, v, weight))

    def dijkstra(self, start_vertex_data, end_vertex_data):
        """
        Find shortest path using Dijkstra's algorithm.

        Args:
            start_vertex_data: Name of start location
            end_vertex_data: Name of end location

        Returns:
            Tuple: (distance, path) where path is list of location names
        """
        try:
            start_vertex = self.vertex_data.index(start_vertex_data)
            end_vertex = self.vertex_data.index(end_vertex_data)
        except ValueError:
            return float('inf'), []

        distances = [float('inf')] * self.size
        predecessors = [None] * self.size
        distances[start_vertex] = 0
        visited = [False] * self.size

        for _ in range(self.size):
            min_distance = float('inf')
            u = None
            for i in range(self.size):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    u = i

            if u is None or u == end_vertex:
                break

            visited[u] = True

            for v in range(self.size):
                if self.adj_matrix[u][v] != 0 and not visited[v]:
                    alt = distances[u] + self.adj_matrix[u][v]
                    if alt < distances[v]:
                        distances[v] = alt
                        predecessors[v] = u

        return distances[end_vertex], self.get_path(predecessors, start_vertex_data, end_vertex_data)

    def get_path(self, predecessors, start_vertex_data, end_vertex_data):
        """Reconstruct path from predecessors array."""
        path = []
        try:
            current = self.vertex_data.index(end_vertex_data)
        except ValueError:
            return []

        while current is not None:
            path.insert(0, self.vertex_data[current])
            current = predecessors[current]
            if current == self.vertex_data.index(start_vertex_data):
                path.insert(0, start_vertex_data)
                break
        return path

    def visualize(self, path=[]):
        """Visualize the graph and highlight the shortest path."""
        G = nx.Graph()
        for i, label in enumerate(self.vertex_data):
            G.add_node(i, label=self.display_labels.get(i, label))
        for u, v, weight in self.edges:
            G.add_edge(u, v, weight=weight)

        scaled_positions = {i: (x * 1.5, y * 1.5) for i, (x, y) in self.node_positions.items()}
        labels = nx.get_node_attributes(G, 'label')
        edge_labels = nx.get_edge_attributes(G, 'weight')

        plt.figure(figsize=(18, 20))
        nx.draw(G, scaled_positions, with_labels=False, node_size=800, node_color="lightblue")
        nx.draw_networkx_labels(G, scaled_positions, labels, font_size=12, font_color="black")
        nx.draw_networkx_edge_labels(G, scaled_positions, edge_labels=edge_labels, font_color="red")

        if path:
            H = nx.DiGraph()
            path_indices = [self.vertex_data.index(node) for node in path]
            for i in range(len(path_indices) - 1):
                u, v = path_indices[i], path_indices[i + 1]
                weight = self.adj_matrix[u][v]
                H.add_edge(u, v, weight=weight)

            path_edge_labels = nx.get_edge_attributes(H, 'weight')
            nx.draw_networkx_edges(H, scaled_positions, edgelist=H.edges(),
                                 edge_color="green", width=3, arrows=True, arrowsize=25)
            nx.draw_networkx_nodes(G, scaled_positions, nodelist=path_indices, node_color="yellow")
            nx.draw_networkx_edge_labels(H, scaled_positions, edge_labels=path_edge_labels,
                                        font_color="green")

        plt.title("Graph Visualization with Shortest Path Highlighted", fontsize=16)
        plt.show()


def initialize_campus_graph():
    """Initialize the campus graph with all 76 nodes and their edges."""
    g = Graph(76)
    SCALING_FACTOR = 50

    # Adding vertices with fixed positions
    g.add_vertex_data(0, 'ADMIN \n BUILDING \n (TOWER)', (0 * SCALING_FACTOR, 0 * SCALING_FACTOR))
    g.add_vertex_data(1, 'B K SCHOOL \n OF \n BUSINESS', (-1 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(2, 'K S SCHOOL \n OF \n BUSINESS', (1 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(3, 'DEPARTMENT \n OF \n PSYCHOLOGY', (3 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(4, 'SCHOOL\nOF\nLANGUAGES', (4 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(5, 'INFORMATION \n CENTRE', (6 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(6, 'LIBRARY', (9 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(7, '\n DEPARTMENT OF \n COMPUTER \n SCIENCE', (0 * SCALING_FACTOR, 2 * SCALING_FACTOR))
    g.add_vertex_data(8, 'UPASANA', (1 * SCALING_FACTOR, 4 * SCALING_FACTOR))
    g.add_vertex_data(9, 'DEPARTMENT \n OF \n PHYSICS', (4 * SCALING_FACTOR, 7 * SCALING_FACTOR))
    g.add_vertex_data(10, 'DEPARTMENT \n OF \n ZOOLOGY', (7 * SCALING_FACTOR, 5 * SCALING_FACTOR))
    g.add_vertex_data(11, 'DEPARTMENT \n OF \n ANIMATION', (9 * SCALING_FACTOR, 4 * SCALING_FACTOR))
    g.add_vertex_data(12, 'DEPARTMENT \n OF \n BOTANY', (5 * SCALING_FACTOR, 12 * SCALING_FACTOR))
    g.add_vertex_data(13, 'DEPARTMENT \n OF \n MICROBIOLOGY', (5 * SCALING_FACTOR, 9 * SCALING_FACTOR))
    g.add_vertex_data(14, '  ATAL \n KALAM', (7 * SCALING_FACTOR, 14 * SCALING_FACTOR))
    g.add_vertex_data(15, 'DEPARTMENT \n OF \n CHEMISTRY', (9 * SCALING_FACTOR, 12 * SCALING_FACTOR))
    g.add_vertex_data(16, 'DEPARTMENT \n OF \n BIOCHEMISTRY', (9 * SCALING_FACTOR, 9 * SCALING_FACTOR))
    g.add_vertex_data(17, '      PHYSICAL \n       RESEARCH \n       LABORATORY', (-1 * SCALING_FACTOR, 6 * SCALING_FACTOR))
    g.add_vertex_data(18, '\n \n GU \n POLICE \n STATION', (-1 * SCALING_FACTOR, 12 * SCALING_FACTOR))
    g.add_vertex_data(19, 'SCHOOL\nOF\nDESIGN', (10 * SCALING_FACTOR, 11 * SCALING_FACTOR))
    g.add_vertex_data(20, 'DEPARTMENT \n OF \n MATHEMATICS', (7 * SCALING_FACTOR, 7 * SCALING_FACTOR))
    g.add_vertex_data(21, 'GUSEC', (7 * SCALING_FACTOR, 11 * SCALING_FACTOR))
    g.add_vertex_data(75, 'SCHOOL OF \n INTERNATIONAL STUDIES \n AND DIASPORA', (7 * SCALING_FACTOR, 2 * SCALING_FACTOR))
    g.add_vertex_data(22, 'EXAMINATION \n CENTRE', (4 * SCALING_FACTOR, 2 * SCALING_FACTOR))
    g.add_vertex_data(23, 'CANTEEN', (4 * SCALING_FACTOR, 0 * SCALING_FACTOR))
    g.add_vertex_data(24, 'TOWER \n CIRCLE', (0 * SCALING_FACTOR, -1 * SCALING_FACTOR))
    g.add_vertex_data(25, '2', (0 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(26, '3', (3 * SCALING_FACTOR, -1 * SCALING_FACTOR))
    g.add_vertex_data(27, '4', (5 * SCALING_FACTOR, -1 * SCALING_FACTOR))
    g.add_vertex_data(28, '5', (5 * SCALING_FACTOR, -2 * SCALING_FACTOR))
    g.add_vertex_data(29, '6', (0 * SCALING_FACTOR, 1 * SCALING_FACTOR))
    g.add_vertex_data(30, '7', (-1 * SCALING_FACTOR, 1 * SCALING_FACTOR))
    g.add_vertex_data(31, '8', (1 * SCALING_FACTOR, 1 * SCALING_FACTOR))
    g.add_vertex_data(32, '9', (-1 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(33, '10', (1 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(34, '11', (3 * SCALING_FACTOR, 2 * SCALING_FACTOR))
    g.add_vertex_data(35, '12', (0 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(36, '13', (3 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(37, '14', (5 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(38, '15', (8 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(39, '16', (11 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(40, '17', (11 * SCALING_FACTOR, 6 * SCALING_FACTOR))
    g.add_vertex_data(41, '18', (8 * SCALING_FACTOR, 6 * SCALING_FACTOR))
    g.add_vertex_data(42, '19', (7 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(43, '20', (5 * SCALING_FACTOR, 6 * SCALING_FACTOR))
    g.add_vertex_data(44, '21', (3 * SCALING_FACTOR, 7 * SCALING_FACTOR))
    g.add_vertex_data(45, '22', (3 * SCALING_FACTOR, 8 * SCALING_FACTOR))
    g.add_vertex_data(46, '23', (5 * SCALING_FACTOR, 8 * SCALING_FACTOR))
    g.add_vertex_data(47, '24', (6 * SCALING_FACTOR, 8 * SCALING_FACTOR))
    g.add_vertex_data(48, '25', (8 * SCALING_FACTOR, 8 * SCALING_FACTOR))
    g.add_vertex_data(49, '26', (11 * SCALING_FACTOR, 8 * SCALING_FACTOR))
    g.add_vertex_data(50, '27', (8 * SCALING_FACTOR, 12 * SCALING_FACTOR))
    g.add_vertex_data(51, '28', (6 * SCALING_FACTOR, 12 * SCALING_FACTOR))
    g.add_vertex_data(52, '29', (6 * SCALING_FACTOR, 13 * SCALING_FACTOR))
    g.add_vertex_data(53, '30', (8 * SCALING_FACTOR, 13 * SCALING_FACTOR))
    g.add_vertex_data(54, '31', (11 * SCALING_FACTOR, 15 * SCALING_FACTOR))
    g.add_vertex_data(55, '32', (8 * SCALING_FACTOR, 15 * SCALING_FACTOR))
    g.add_vertex_data(56, '33', (-2 * SCALING_FACTOR, 15 * SCALING_FACTOR))
    g.add_vertex_data(57, '34', (-2 * SCALING_FACTOR, 12 * SCALING_FACTOR))
    g.add_vertex_data(58, '35', (-2 * SCALING_FACTOR, 6 * SCALING_FACTOR))
    g.add_vertex_data(59, '\n \n DR \n BABA SAHEB \n AMBEDKAR GATE', (-2 * SCALING_FACTOR, 3 * SCALING_FACTOR))
    g.add_vertex_data(60, '37', (-2 * SCALING_FACTOR, -3 * SCALING_FACTOR))
    g.add_vertex_data(61, 'GATE \n NO \n 1', (0 * SCALING_FACTOR, -3 * SCALING_FACTOR))
    g.add_vertex_data(62, '39', (5 * SCALING_FACTOR, 0 * SCALING_FACTOR))
    g.add_vertex_data(63, '40', (8 * SCALING_FACTOR, 4 * SCALING_FACTOR))
    g.add_vertex_data(64, '41', (9 * SCALING_FACTOR, -1 * SCALING_FACTOR))
    g.add_vertex_data(65, '42', (11 * SCALING_FACTOR, 11 * SCALING_FACTOR))
    g.add_vertex_data(66, '43', (6 * SCALING_FACTOR, 7 * SCALING_FACTOR))
    g.add_vertex_data(67, '44', (7 * SCALING_FACTOR, 6 * SCALING_FACTOR))
    g.add_vertex_data(68, '45', (9 * SCALING_FACTOR, 8 * SCALING_FACTOR))
    g.add_vertex_data(69, '46', (7 * SCALING_FACTOR, 12 * SCALING_FACTOR))
    g.add_vertex_data(70, '47', (8 * SCALING_FACTOR, 14 * SCALING_FACTOR))
    g.add_vertex_data(71, '48', (6 * SCALING_FACTOR, 9 * SCALING_FACTOR))
    g.add_vertex_data(72, '\n NETAJI \n SUBHASH CHANDRA \n BOSE GATE', (5 * SCALING_FACTOR, -3 * SCALING_FACTOR))
    g.add_vertex_data(73, 'MAHATMA \n GANDHI \n GATE', (11 * SCALING_FACTOR, 0 * SCALING_FACTOR))
    g.add_vertex_data(74, '51', (11 * SCALING_FACTOR, -3 * SCALING_FACTOR))

    # Adding edges with distances in meters
    g.add_edge(0, 24, 0)
    g.add_edge(0, 29, 43)
    g.add_edge(1, 25, 1)
    g.add_edge(2, 25, 1)
    g.add_edge(3, 26, 42)
    g.add_edge(4, 28, 1)
    g.add_edge(5, 28, 1)
    g.add_edge(6, 64, 38)
    g.add_edge(7, 35, 1)
    g.add_edge(8, 33, 20)
    g.add_edge(9, 44, 1)
    g.add_edge(10, 67, 1)
    g.add_edge(11, 63, 1)
    g.add_edge(12, 51, 1)
    g.add_edge(13, 71, 1)
    g.add_edge(14, 70, 1)
    g.add_edge(15, 50, 1)
    g.add_edge(16, 68, 1)
    g.add_edge(17, 58, 32)
    g.add_edge(18, 57, 32)
    g.add_edge(19, 65, 1)
    g.add_edge(20, 66, 1)
    g.add_edge(21, 69, 1)
    g.add_edge(22, 34, 47)
    g.add_edge(23, 62, 47)
    g.add_edge(24, 0, 0)
    g.add_edge(24, 25, 37)
    g.add_edge(24, 26, 85)
    g.add_edge(25, 24, 37)
    g.add_edge(25, 1, 1)
    g.add_edge(25, 2, 1)
    g.add_edge(25, 61, 68)
    g.add_edge(26, 3, 42)
    g.add_edge(26, 24, 85)
    g.add_edge(26, 27, 81)
    g.add_edge(26, 34, 126)
    g.add_edge(27, 26, 81)
    g.add_edge(27, 28, 81)
    g.add_edge(27, 62, 39)
    g.add_edge(27, 64, 90)
    g.add_edge(28, 27, 81)
    g.add_edge(28, 4, 1)
    g.add_edge(28, 5, 1)
    g.add_edge(28, 72, 26)
    g.add_edge(29, 0, 43)
    g.add_edge(29, 30, 32)
    g.add_edge(29, 31, 41)
    g.add_edge(30, 29, 32)
    g.add_edge(30, 32, 104)
    g.add_edge(31, 29, 41)
    g.add_edge(31, 33, 79)
    g.add_edge(32, 30, 104)
    g.add_edge(32, 35, 39)
    g.add_edge(32, 59, 12)
    g.add_edge(33, 35, 49)
    g.add_edge(33, 36, 52)
    g.add_edge(33, 31, 79)
    g.add_edge(34, 22, 1)
    g.add_edge(34, 36, 96)
    g.add_edge(34, 26, 126)
    g.add_edge(35, 33, 49)
    g.add_edge(35, 32, 39)
    g.add_edge(36, 34, 96)
    g.add_edge(36, 33, 52)
    g.add_edge(36, 37, 84)
    g.add_edge(37, 36, 84)
    g.add_edge(37, 42, 64)
    g.add_edge(37, 62, 130)
    g.add_edge(37, 43, 73)
    g.add_edge(38, 42, 45)
    g.add_edge(38, 39, 62)
    g.add_edge(38, 63, 28)
    g.add_edge(39, 38, 62)
    g.add_edge(39, 40, 112)
    g.add_edge(39, 73, 90)
    g.add_edge(40, 39, 112)
    g.add_edge(40, 41, 87)
    g.add_edge(40, 49, 93)
    g.add_edge(41, 40, 87)
    g.add_edge(41, 63, 74)
    g.add_edge(41, 67, 28)
    g.add_edge(41, 48, 75)
    g.add_edge(43, 37, 73)
    g.add_edge(43, 46, 72)
    g.add_edge(43, 67, 77)
    g.add_edge(44, 9, 1)
    g.add_edge(44, 45, 51)
    g.add_edge(45, 44, 51)
    g.add_edge(45, 46, 42)
    g.add_edge(46, 45, 42)
    g.add_edge(46, 47, 52)
    g.add_edge(46, 43, 72)
    g.add_edge(47, 46, 52)
    g.add_edge(47, 71, 24)
    g.add_edge(47, 48, 51)
    g.add_edge(47, 66, 57)
    g.add_edge(48, 47, 51)
    g.add_edge(48, 68, 55)
    g.add_edge(48, 50, 108)
    g.add_edge(48, 41, 75)
    g.add_edge(49, 68, 45)
    g.add_edge(49, 40, 93)
    g.add_edge(49, 65, 57)
    g.add_edge(50, 15, 1)
    g.add_edge(50, 69, 20)
    g.add_edge(50, 48, 108)
    g.add_edge(50, 53, 37)
    g.add_edge(51, 12, 1)
    g.add_edge(51, 52, 37)
    g.add_edge(51, 69, 30)
    g.add_edge(51, 71, 82)
    g.add_edge(52, 51, 37)
    g.add_edge(52, 53, 49)
    g.add_edge(53, 52, 49)
    g.add_edge(53, 50, 37)
    g.add_edge(53, 70, 48)
    g.add_edge(54, 65, 49)
    g.add_edge(54, 55, 266)
    g.add_edge(55, 54, 266)
    g.add_edge(55, 56, 420)
    g.add_edge(55, 70, 62)
    g.add_edge(56, 55, 420)
    g.add_edge(56, 57, 70)
    g.add_edge(57, 56, 70)
    g.add_edge(57, 18, 32)
    g.add_edge(57, 58, 489)
    g.add_edge(58, 57, 489)
    g.add_edge(58, 17, 32)
    g.add_edge(58, 59, 76)
    g.add_edge(59, 58, 76)
    g.add_edge(59, 32, 12)
    g.add_edge(59, 60, 378)
    g.add_edge(60, 59, 378)
    g.add_edge(60, 61, 60)
    g.add_edge(61, 60, 60)
    g.add_edge(61, 72, 177)
    g.add_edge(61, 25, 68)
    g.add_edge(62, 23, 1)
    g.add_edge(62, 37, 130)
    g.add_edge(62, 27, 58)
    g.add_edge(63, 11, 1)
    g.add_edge(63, 38, 28)
    g.add_edge(63, 41, 74)
    g.add_edge(64, 6, 38)
    g.add_edge(64, 27, 90)
    g.add_edge(65, 19, 1)
    g.add_edge(65, 54, 49)
    g.add_edge(65, 49, 57)
    g.add_edge(66, 20, 1)
    g.add_edge(66, 47, 57)
    g.add_edge(67, 10, 1)
    g.add_edge(67, 41, 28)
    g.add_edge(68, 16, 1)
    g.add_edge(68, 48, 55)
    g.add_edge(68, 49, 85)
    g.add_edge(69, 21, 1)
    g.add_edge(69, 50, 20)
    g.add_edge(69, 51, 30)
    g.add_edge(70, 14, 1)
    g.add_edge(70, 53, 48)
    g.add_edge(70, 55, 62)
    g.add_edge(71, 13, 1)
    g.add_edge(71, 47, 24)
    g.add_edge(71, 51, 82)
    g.add_edge(72, 28, 26)
    g.add_edge(72, 61, 177)
    g.add_edge(72, 74, 102)
    g.add_edge(73, 39, 90)
    g.add_edge(73, 74, 196)
    g.add_edge(74, 72, 102)
    g.add_edge(74, 73, 196)
    g.add_edge(42, 75, 1)

    return g

def get_dijkstra_path(source_name, destination_name):
    """
    Modular function to get the shortest path between two locations.
    Standardizes input and handles graph initialization.
    """
    g = initialize_campus_graph()

    # Standardize names
    src = ' '.join(source_name.strip().upper().split())
    dest = ' '.join(destination_name.strip().upper().split())

    if src not in g.vertex_data or dest not in g.vertex_data:
        return None, "One or both locations not found in campus map."

    distance, path = g.dijkstra(src, dest)

    if distance == float('inf'):
        return None, f"No path exists between {src} and {dest}."

    return {
        "distance": distance,
        "path": path,
        "algorithm": "Dijkstra"
    }, None



def main():
    """Main function to run Dijkstra pathfinding."""
    print("=" * 50)
    print("Dijkstra's Algorithm - Campus Navigator")
    print("=" * 50)

    g = initialize_campus_graph()

    source = input("Enter the source location: ").strip().upper()
    destination = input("Enter the destination location: ").strip().upper()

    if source not in g.vertex_data:
        print(f"Error: Source '{source}' not found in campus map.")
        return

    if destination not in g.vertex_data:
        print(f"Error: Destination '{destination}' not found in campus map.")
        return

    distance, path = g.dijkstra(source, destination)

    if distance == float('inf'):
        print(f"\nNo path exists between {source} and {destination}.")
    else:
        distance_km = distance / 1000
        print("\n" + "=" * 50)
        print("SHORTEST PATH FOUND")
        print("=" * 50)
        print(f"Path: {' -> '.join(path)}")
        print(f"Distance: {distance} meters ({distance_km:.2f} kilometers)")
        print("=" * 50)

        visualize = input("\nVisualize the path? (y/n): ").strip().lower()
        if visualize == 'y':
            g.visualize(path)


if __name__ == "__main__":
    main()
