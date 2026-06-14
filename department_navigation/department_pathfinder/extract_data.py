import json

with open('d:/Project/Smart Path Suggestor/notebooks/Final1.ipynb', 'r') as f:
    notebook = json.load(f)

# Find the cell with NODES and RAW_EDGES
nodes_text = ""
edges_text = ""

for cell in notebook['cells']:
    if 'source' in cell:
        source = "".join(cell['source'])
        if 'NODES =' in source:
            nodes_text = source
        if 'RAW_EDGES =' in source:
            edges_text = source

print("--- NODES ---")
print(nodes_text)
print("--- EDGES ---")
print(edges_text)
