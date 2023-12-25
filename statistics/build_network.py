import json
from dash import Dash, html, Input, Output, callback, dcc
import dash_cytoscape as cyto
import networkx as nx
import pandas as pd
import random

# For reproducibility
random.seed(31)

# Read data from csv file.
data = pd.read_csv('statistics\\ConceptData.csv', header=0)
# Initiate a Dash app.
app = Dash(__name__)
cyto.load_extra_layouts()

# Initiate the network graph.
G = nx.Graph()
# Iterate row in dataframe such that its column matches the node and edge in network graph.
for _, row in data.iterrows():
    concept1 = row['concept1']
    concept1_desc = row['concept1_desc']
    concept2 = row['concept2']
    concept2_desc = row['concept2_desc']
    relationship_desc = row['relationship_desc']
    # Add nodes with an additional attribute `concept1_desc` and `concept2_desc`.
    G.add_node(concept1, concept1_desc=concept1_desc)
    G.add_node(concept2, concept2_desc=concept2_desc)
    # Add edges with the 'relationship_desc' attribute.
    G.add_edge(concept1, concept2, relationship_desc=relationship_desc)

# List of key main concepts to highlight (yellow boxes).
key_main_concepts = ["Distribution", "Random variables", "Moments", "Other"]

# elements for cytoscape to read. note that the elements look like this:
# 'elements': {
# 'nodes': [{'data': {'concept1_desc': 'Not fixed number. Use data to learn the properties for a sample. A sophisticated "guess".', 'id': 'Estimate', 'value': 'Estimate', 'name': 'Estimate'}}, {'data': {'concept2_desc': 'A variable that takes values according to a certain probability distribution', 'id': 'Random variables', 'value': 'Random variables', 'name': 'Random variables'}}], 
# 'edges': [{'data': {'relationship_desc': nan, 'source': 'Univariate distribution', 'target': 'Distribution'}}, {'data': {'relationship_desc': 'A type of dist', 'source': 'Univariate distribution', 'target': 'CDF'}}]
# }
# Each node and edge in nodes and edges is a "data" which has redundant items like
# value, name, id. Just ignore them and focus on "id" and the newly created one "desc".
elements = nx.readwrite.json_graph.cytoscape_data(G)['elements']

# UPDATE: 12/21/2023: no need for this:
# Edges haven't had a direct way to add new attribute. Manually update edge data to include 'relationship_desc'
# for edge in elements['edges']:
#     source = edge['data']['source']
#     target = edge['data']['target']
#     edge_data = G.get_edge_data(source, target, default={})
#     edge['data']['relationship_desc'] = edge_data.get('relationship_desc', '')

# Style:
# Update node style to put the label inside the node and highlight key main concepts
elements['nodes'] = [
    {
        "data": {"id": node, "label": node},
        "classes": "key-main-concept" if node in key_main_concepts else "",
        "style": {
            "label": node,
            "text-halign": "center",
            "text-valign": "center",
            "background-color": "#bde0fe" if node not in key_main_concepts else "#FFD700",
            "shape": "roundrectangle",
            "width": "label"}
    }
    for node in G.nodes
]

# Interactive features:
# Select a node and display its description info.
@app.callback(
    Output("info-node", "children"),
    [Input("cytoscape", "selectedNodeData")]
)
def display_info(data):
    if data is None or len(data) == 0:
        return ""
    selected_node = data[0]["id"]
    if selected_node not in G.nodes():
        return ""
    # Check if concept1 node
    if "concept1_desc" in G.nodes[selected_node]:
        concept1_desc = G.nodes[selected_node]["concept1_desc"]
        return dcc.Markdown(concept1_desc, dangerously_allow_html=True)
    # Otherwise concept2 node
    elif "concept2_desc" in G.nodes[selected_node]:
        concept2_desc = G.nodes[selected_node]["concept2_desc"]
        return dcc.Markdown(concept2_desc, dangerously_allow_html=True)
    else:
        return ""

# Interactive features:
# Select an edge and display its description info.
@app.callback(
    Output("info-edge", "children"),
    [Input("cytoscape", "selectedEdgeData")]
)
def display_edge_info(data):
    if data is None or len(data) == 0:
        return ""
    edge_info = ""
    for edge_data in data:
        # Get the source concept and target concept of the selected edge.
        source = edge_data.get("source", "")
        target = edge_data.get("target", "")
        # Retrieve the edge description directly from the graph.
        edge_desc = G.get_edge_data(source, target, default={}).get("relationship_desc")
        # Convert to string (even empty description or "nan")
        edge_info += str(edge_desc)
    return edge_info

###
# Add a div to display selected node or edge information
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        layout={
             'name': 'klay',
             'avoidOverlap': True,    # Set to True to avoid node overlap
            'spacingFactor': 1.25,    # Adjust the spacing between nodes (increase or decrease as needed)

        },
        elements=elements,
        style={'width': '75%', 'height': '100vh', 'float': 'left'},
        stylesheet=[{'selector': 'node', 'style': {'font-size': '15px'}}]
    ),
    html.Div(id="info-node", style={"margin-right": "25px", "margin-left": "20px", "fontSize": "20px"}),
    html.Div(id="info-edge", style={"margin-right": "25px", "margin-left": "20px", "fontSize": "20px"})
])

if __name__ == '__main__':
    app.run_server(debug=True)
