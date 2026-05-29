"""
A* Algorithm Implementation
For Smart Path Suggestor - Campus Navigation
Source: Final1.ipynb (canonical reference)

This module implements A* pathfinding algorithm with haversine distance heuristic
to find optimal paths on the Gujarat University campus.
"""

import networkx as nx
import matplotlib.pyplot as plt
import heapq
import math
import time


# ─── Canonical Campus Data (from Final1.ipynb) ──────────────────────────────

NODES = {
    "ADMIN BUILDING (TOWER)": (23.0361584, 72.5471442),
    "ATAL KALAM": (23.0381546, 72.5421939),
    "B K SCHOOL OF BUSINESS MANAGEMENT": (23.0361038, 72.5479811),
    "CANTEEN": (23.0375237, 72.5468153),
    "DR BABA SAHEB AMBEDKAR GATE": (23.0355293, 72.5450273),
    "DEPARTMENT OF PSYCHOLOGY": (23.0369461, 72.5481299),
    "DEPARTMENT OF PHYSICS": (23.0371494, 72.5446793),
    "DEPARTMENT OF ZOOLOGY": (23.0381734, 72.5448975),
    "DEPARTMENT OF ANIMATION": (23.0388152, 72.5455111),
    "DEPARTMENT OF BOTANY": (23.0377720, 72.5431427),
    "DEPARTMENT OF MICROBIOLOGY": (23.0374364, 72.5440798),
    "DEPARTMENT OF CHEMISTRY": (23.0383820, 72.5429556),
    "DEPARTMENT OF BIOCHEMISTRY": (23.0387862, 72.5439940),
    "DEPARTMENT OF COMPUTER SCIENCE": (23.0360597, 72.5452603),
    "DEPARTMENT OF MATHEMATICS": (23.0380115, 72.5446934),
    "EXAMINATION CENTRE": (23.0369791, 72.5463513),
    "GATE NO 1": (23.0362870, 72.5484974),
    "GUJARAT UNIVERSITY POLICE STATION": (23.03511208, 72.5397883),
    "GUSEC": (23.0381071, 72.5431927),
    "INFORMATION CENTRE": (23.0378859, 72.5482825),
    "K S SCHOOL OF BUSINESS MANAGEMENT": (23.036287, 72.5478641),
    "LIBRARY": (23.0385101, 72.5477165),
    "MAHATMA GANDHI GATE": (23.0389503, 72.5467308),
    "NETAJI SUBHASH CHANDRA BOSE GATE": (23.0378091, 72.5484984),
    "PHYSICAL RESEARCH LABORATORY (PRL)": (23.0354034, 72.5440315),
    "SCHOOL OF LANGUAGES": (23.0377159, 72.5483931),
    "SCHOOL OF DESIGN": (23.0396751, 72.5434964),
    "SCHOOL OF INTERNATIONAL STUDIES AND DIASPORA": (23.0380331, 72.5458091),
    "TOWER CIRCLE": (23.0361911, 72.5475660),
    "UPASANA": (23.0362812, 72.5449763),
    "2": (23.0362297, 72.5479656),
    "3": (23.0370004, 72.5475348),
    "4": (23.0377113, 72.5474624),
    "5": (23.0378020, 72.5481718),
    "6": (23.0359853, 72.5461008),
    "7": (23.0356397, 72.5461062),
    "8": (23.0363620, 72.5460599),
    "9": (23.0356308, 72.5450749),
    "10": (23.0363287, 72.5452492),
    "11": (23.0368378, 72.5463540),
    "12": (23.0360464, 72.5451939),
    "13": (23.0367946, 72.5453840),
    "14": (23.0375379, 72.5456056),
    "15": (23.0384882, 72.5458430),
    "16": (23.0390494, 72.5459238),
    "17": (23.0392144, 72.5448801),
    "18": (23.0395887, 72.5440463),
    "19": (23.0380738, 72.5457468),
    "20": (23.0374897, 72.5448888),
    "21": (23.0370390, 72.5446813),
    "22": (23.0370556, 72.5442367),
    "23": (23.0374453, 72.5442065),
    "24": (23.0379081, 72.5441552),
    "25": (23.0383669, 72.5441177),
    "26": (23.0395717, 72.5440543),
    "27": (23.0383104, 72.5430656),
    "28": (23.0378692, 72.5431088),
    "29": (23.0378334, 72.5427494),
    "30": (23.0382774, 72.5427045),
    "31": (23.0401502, 72.5431367),
    "32": (23.0382083, 72.5416004),
    "33": (23.0352331, 72.5392408),
    "34": (23.0347703, 72.5397477),
    "35": (23.0352553, 72.5440952),
    "37": (23.0357221, 72.5485551),
    "39": (23.0376421, 72.5467714),
    "40": (23.0384752, 72.5455362),
    "41": (23.0384928, 72.5474188),
    "42": (23.0398957, 72.5435085),
    "43": (23.0379353, 72.5447141),
    "44": (23.0376476, 72.5449450),
    "45": (23.0387914, 72.5440801),
    "46": (23.0380929, 72.5430760),
    "47": (23.0382453, 72.5421962),
    "48": (23.0373087, 72.5436322),
    "51": (23.0388433, 72.5486660),
}

RAW_EDGES = [
    ("ADMIN BUILDING (TOWER)", "TOWER CIRCLE"),
    ("ADMIN BUILDING (TOWER)", "6"),
    ("B K SCHOOL OF BUSINESS MANAGEMENT", "2"),
    ("K S SCHOOL OF BUSINESS MANAGEMENT", "2"),
    ("DEPARTMENT OF PSYCHOLOGY", "3"),
    ("SCHOOL OF LANGUAGES", "5"),
    ("INFORMATION CENTRE", "5"),
    ("LIBRARY", "41"),
    ("DEPARTMENT OF COMPUTER SCIENCE", "12"),
    ("UPASANA", "10"),
    ("DEPARTMENT OF PHYSICS", "21"),
    ("DEPARTMENT OF ZOOLOGY", "20"),
    ("DEPARTMENT OF ANIMATION", "40"),
    ("DEPARTMENT OF BOTANY", "28"),
    ("DEPARTMENT OF MICROBIOLOGY", "23"),
    ("ATAL KALAM", "47"),
    ("DEPARTMENT OF CHEMISTRY", "27"),
    ("DEPARTMENT OF BIOCHEMISTRY", "45"),
    ("PHYSICAL RESEARCH LABORATORY (PRL)", "35"),
    ("GUJARAT UNIVERSITY POLICE STATION", "34"),
    ("SCHOOL OF DESIGN", "42"),
    ("DEPARTMENT OF MATHEMATICS", "43"),
    ("GUSEC", "46"),
    ("SCHOOL OF INTERNATIONAL STUDIES AND DIASPORA", "19"),
    ("EXAMINATION CENTRE", "11"),
    ("CANTEEN", "39"),
    ("TOWER CIRCLE", "3"),
    ("TOWER CIRCLE", "2"),
    ("GATE NO 1", "2"),
    ("GATE NO 1", "37"),
    ("GATE NO 1", "NETAJI SUBHASH CHANDRA BOSE GATE"),
    ("DR BABA SAHEB AMBEDKAR GATE", "37"),
    ("DR BABA SAHEB AMBEDKAR GATE", "35"),
    ("DR BABA SAHEB AMBEDKAR GATE", "9"),
    ("NETAJI SUBHASH CHANDRA BOSE GATE", "5"),
    ("NETAJI SUBHASH CHANDRA BOSE GATE", "51"),
    ("MAHATMA GANDHI GATE", "51"),
    ("MAHATMA GANDHI GATE", "16"),
    ("2", "TOWER CIRCLE"),
    ("2", "GATE NO 1"),
    ("2", "B K SCHOOL OF BUSINESS MANAGEMENT"),
    ("2", "K S SCHOOL OF BUSINESS MANAGEMENT"),
    ("3", "11"),
    ("3", "4"),
    ("3", "TOWER CIRCLE"),
    ("4", "39"),
    ("4", "5"),
    ("4", "3"),
    ("4", "41"),
    ("5", "NETAJI SUBHASH CHANDRA BOSE GATE"),
    ("5", "INFORMATION CENTRE"),
    ("5", "SCHOOL OF LANGUAGES"),
    ("5", "4"),
    ("6", "ADMIN BUILDING (TOWER)"),
    ("6", "7"),
    ("6", "8"),
    ("7", "6"),
    ("7", "8"),
    ("8", "6"),
    ("8", "10"),
    ("9", "DR BABA SAHEB AMBEDKAR GATE"),
    ("9", "7"),
    ("9", "12"),
    ("10", "UPASANA"),
    ("10", "12"),
    ("10", "8"),
    ("10", "13"),
    ("11", "3"),
    ("11", "13"),
    ("11", "EXAMINATION CENTRE"),
    ("12", "DEPARTMENT OF COMPUTER SCIENCE"),
    ("12", "9"),
    ("12", "10"),
    ("13", "10"),
    ("13", "11"),
    ("13", "14"),
    ("14", "13"),
    ("14", "39"),
    ("14", "19"),
    ("14", "20"),
    ("15", "16"),
    ("15", "19"),
    ("15", "40"),
    ("16", "15"),
    ("16", "MAHATMA GANDHI GATE"),
    ("16", "17"),
    ("17", "16"),
    ("17", "18"),
    ("17", "26"),
    ("18", "17"),
    ("18", "25"),
    ("19", "15"),
    ("19", "14"),
    ("20", "14"),
    ("20", "23"),
    ("21", "22"),
    ("22", "21"),
    ("22", "23"),
    ("23", "20"),
    ("23", "24"),
    ("24", "23"),
    ("24", "43"),
    ("24", "28"),
    ("24", "25"),
    ("25", "18"),
    ("25", "45"),
    ("25", "24"),
    ("25", "27"),
    ("26", "17"),
    ("26", "42"),
    ("26", "45"),
    ("27", "25"),
    ("27", "46"),
    ("27", "30"),
    ("28", "29"),
    ("28", "46"),
    ("28", "24"),
    ("29", "28"),
    ("29", "30"),
    ("30", "29"),
    ("30", "27"),
    ("30", "47"),
    ("31", "32"),
    ("31", "42"),
    ("32", "31"),
    ("32", "33"),
    ("32", "47"),
    ("33", "32"),
    ("33", "34"),
    ("34", "33"),
    ("34", "35"),
    ("35", "34"),
    ("39", "14"),
    ("39", "4"),
    ("40", "15"),
    ("41", "4"),
    ("42", "26"),
    ("42", "31"),
    ("43", "24"),
    ("45", "25"),
    ("45", "26"),
    ("46", "28"),
    ("46", "27"),
    ("47", "32"),
    ("47", "30"),
]


def haversine(coord1, coord2):
    """Calculate haversine distance in meters between two GPS coordinates."""
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class Graph:
    """Graph representation using adjacency matrix with A* pathfinding capability."""

    def __init__(self, size):
        self.adj_matrix = [[0] * size for _ in range(size)]
        self.size = size
        self.vertex_data = [''] * size
        self.edges = []
        self.node_positions = {}  # GPS (lat, lon) for heuristic
        self.display_labels = {}

    def add_vertex_data(self, vertex, data, position):
        """Add a vertex with label and GPS position."""
        if 0 <= vertex < self.size:
            cleaned_data = ' '.join(data.strip().split())
            self.vertex_data[vertex] = cleaned_data
            self.node_positions[vertex] = position
            self.display_labels[vertex] = data

    def add_edge(self, u, v, weight):
        """Add an edge between vertices u and v with given weight."""
        if 0 <= u < self.size and 0 <= v < self.size:
            stored_weight = max(weight, 0.0001)
            self.adj_matrix[u][v] = stored_weight
            self.adj_matrix[v][u] = stored_weight
            self.edges.append((u, v, weight))

    def heuristic(self, node1, node2):
        """Haversine distance heuristic (uses real GPS coordinates)."""
        return haversine(self.node_positions[node1], self.node_positions[node2])

    def a_star(self, start_vertex_data, end_vertex_data):
        """Find shortest path using A* algorithm."""
        try:
            start_vertex = self.vertex_data.index(start_vertex_data)
            end_vertex = self.vertex_data.index(end_vertex_data)
        except ValueError:
            return float('inf'), []

        open_set = [(0, start_vertex)]
        came_from = {}
        g_score = {i: float('inf') for i in range(self.size)}
        g_score[start_vertex] = 0

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == end_vertex:
                return g_score[current], self.get_path(came_from, start_vertex_data, end_vertex_data)

            for neighbor in range(self.size):
                if self.adj_matrix[current][neighbor] != 0:
                    tentative_g_score = g_score[current] + self.adj_matrix[current][neighbor]
                    if tentative_g_score < g_score[neighbor]:
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + self.heuristic(neighbor, end_vertex)
                        heapq.heappush(open_set, (f_score, neighbor))
                        came_from[neighbor] = current

        return float('inf'), []

    def get_path(self, came_from, start_vertex_data, end_vertex_data):
        """Reconstruct path from came_from dictionary."""
        path = []
        try:
            current = self.vertex_data.index(end_vertex_data)
        except ValueError:
            return []

        while current in came_from:
            path.insert(0, self.vertex_data[current])
            current = came_from[current]

        path.insert(0, start_vertex_data)
        return path

    def visualize(self, path=[]):
        """Visualize the graph and highlight the optimal path found by A*."""
        G = nx.Graph()
        for i, label in enumerate(self.vertex_data):
            if label:
                G.add_node(i, label=label)
        for u, v, weight in self.edges:
            G.add_edge(u, v, weight=round(weight, 1))

        pos = nx.spring_layout(G, seed=42)
        labels = nx.get_node_attributes(G, 'label')
        edge_labels = nx.get_edge_attributes(G, 'weight')

        plt.figure(figsize=(18, 20))
        nx.draw(G, pos, with_labels=False, node_size=800, node_color="lightblue")
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color="black")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=6)

        if path:
            H = nx.DiGraph()
            path_indices = [self.vertex_data.index(node) for node in path]
            for i in range(len(path_indices) - 1):
                u, v = path_indices[i], path_indices[i + 1]
                weight = self.adj_matrix[u][v]
                H.add_edge(u, v, weight=round(weight, 1))

            path_edge_labels = nx.get_edge_attributes(H, 'weight')
            nx.draw_networkx_edges(H, pos, edgelist=H.edges(),
                                   edge_color="green", width=3, arrows=True, arrowsize=25)
            nx.draw_networkx_nodes(G, pos, nodelist=path_indices, node_color="yellow")
            nx.draw_networkx_edge_labels(H, pos, edge_labels=path_edge_labels,
                                         font_color="green")

        plt.title("A* Pathfinding - Shortest Path Highlighted", fontsize=16)
        plt.show()


def initialize_campus_graph():
    """
    Initialize the campus graph using EXACT data from Final1.ipynb notebook.
    Uses real GPS coordinates and haversine-computed edge weights.
    """
    node_names = list(NODES.keys())
    n = len(node_names)
    g = Graph(n)

    # Map name -> index
    name_to_idx = {name: i for i, name in enumerate(node_names)}

    # Add all vertices with GPS positions
    for i, name in enumerate(node_names):
        g.add_vertex_data(i, name, NODES[name])

    # Add edges with haversine distances (matching notebook exactly)
    added_edges = set()
    for a, b in RAW_EDGES:
        if a in name_to_idx and b in name_to_idx:
            key = tuple(sorted([a, b]))
            if key not in added_edges:
                idx_a = name_to_idx[a]
                idx_b = name_to_idx[b]
                dist = haversine(NODES[a], NODES[b])
                g.add_edge(idx_a, idx_b, dist)
                added_edges.add(key)

    return g


def get_astar_paths(source_name, destination_name, k=3):
    """
    Find the top K shortest paths using NetworkX's simple paths algorithm.
    Returns a list of paths with their distances, steps, and segments.
    """
    # Standardize names
    src = ' '.join(source_name.strip().upper().split())
    dest = ' '.join(destination_name.strip().upper().split())

    if src not in NODES or dest not in NODES:
        return None, "One or both locations not found in campus map."

    # Build NetworkX graph
    G = nx.Graph()
    for node in NODES:
        G.add_node(node)
    for edge in RAW_EDGES:
        dist = haversine(NODES[edge[0]], NODES[edge[1]])
        G.add_edge(edge[0], edge[1], weight=dist)

    paths = []
    try:
        # Get up to k simple paths
        path_generator = nx.shortest_simple_paths(G, src, dest, weight='weight')
        for i in range(k):
            try:
                path = next(path_generator)
                total_dist = 0
                segments = []
                for j in range(len(path) - 1):
                    seg_dist = G[path[j]][path[j+1]]['weight']
                    total_dist += seg_dist
                    segments.append({
                        "from_label": path[j],
                        "to_label": path[j+1],
                        "distance_m": round(seg_dist, 2),
                        "steps": int(seg_dist * 1.3)
                    })
                paths.append({
                    "distance": round(total_dist, 2),
                    "steps": int(total_dist * 1.3),
                    "path": path,
                    "segments": segments,
                    "algorithm": "A*"
                })
            except StopIteration:
                break
    except nx.NetworkXNoPath:
        return None, f"No path exists between {src} and {dest}."

    if not paths:
        return None, f"No path exists between {src} and {dest}."

    return paths, None


def get_astar_path(source_name, destination_name):
    """Legacy wrapper for singular path returns."""
    paths, err = get_astar_paths(source_name, destination_name, k=1)
    if err:
        return None, err
    return paths[0], None


def main():
    """Main function to run A* pathfinding with performance metrics."""
    print("=" * 60)
    print("A* Algorithm - Campus Navigator")
    print("=" * 60)

    g = initialize_campus_graph()

    source = input("Enter the source location: ").strip().upper()
    destination = input("Enter the destination location: ").strip().upper()

    if source not in g.vertex_data:
        print(f"Error: Source '{source}' not found in campus map.")
        return

    if destination not in g.vertex_data:
        print(f"Error: Destination '{destination}' not found in campus map.")
        return

    start_time = time.perf_counter()
    distance, path = g.a_star(source, destination)
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    if distance == float('inf'):
        print(f"\nNo path exists between {source} and {destination}.")
    else:
        distance_km = distance / 1000
        print("\n" + "=" * 60)
        print("OPTIMAL PATH FOUND (A* Algorithm)")
        print("=" * 60)
        print(f"Path: {' -> '.join(path)}")
        print(f"Distance: {distance:.2f} meters ({distance_km:.2f} kilometers)")
        print(f"Execution Time: {execution_time * 1e9:.2f} nanoseconds ({execution_time * 1e6:.4f} microseconds)")
        print("=" * 60)

        visualize = input("\nVisualize the path? (y/n): ").strip().lower()
        if visualize == 'y':
            g.visualize(path)


if __name__ == "__main__":
    main()
