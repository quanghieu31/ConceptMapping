import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import networkx as nx
import pandas as pd
import dash_cytoscape as cyto

# Read the DataFrame
df = pd.read_csv('statistics\\ConceptData.csv')  

# Create a directed graph from the DataFrame
G = nx.from_pandas_edgelist(df, 'concept1', 'concept2', create_using=nx.DiGraph())

# Create a Dash web application
app = dash.Dash(__name__)

# Create a Cytoscape component
cyto_compo = cyto.Cytoscape(
    id='cytoscape',
    elements=nx.readwrite.json_graph.cytoscape_data(G)['elements'],
    layout={'name': 'circle'},
    style={'width': '100%', 'height': '500px'},
)

# Define the Dash layout
app.layout = html.Div([
    dcc.Input(id='filter-input', type='text', placeholder='Filter by concept name'),
    cyto_compo
])

# Define callback to update graph based on input
@app.callback(
    Output('cytoscape', 'elements'),
    [Input('filter-input', 'value')]
)
def update_graph(keyword):
    filtered_nodes = [node for node in G.nodes() if keyword.lower() in str(node).lower()]
    filtered_edges = [edge for edge in G.edges() if keyword.lower() in str(edge).lower()]
    filtered_graph = G.subgraph(filtered_nodes + filtered_edges)
    return nx.readwrite.json_graph.cytoscape_data(filtered_graph)['elements']

if __name__ == '__main__':
    app.run_server(debug=True)
