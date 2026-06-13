from pathfinder import load_all_floors, build_graph, dijkstra

floors = load_all_floors()
graph, node_info = build_graph(floors)

start = "1F::24" # 24: Lift on 1st Floor
end = "GF::21" # 21: Window on Ground Floor

print(f"Testing route from {start} to {end}")
result = dijkstra(graph, start, end)

if result:
    dist, steps, path = result
    print(f"Path found! Distance: {dist}m, Steps: {steps}")
    print("Path nodes:", " -> ".join([node_info[k]['label'] for k in path]))
else:
    print("No path found!")
    # Check neighbors of start
    print(f"Neighbors of {start}:", graph.get(start, "None"))
    # Check if end exists in graph
    print(f"Does {end} exist in graph?", end in graph)
