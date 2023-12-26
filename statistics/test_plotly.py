import networkx as nx
import pandas as pd
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# For reproducibility
random.seed(31)

# Read data from csv file.
data = pd.read_csv('statistics\\ConceptData.csv', header=0)

# Initiate the network graph.
G = nx.Graph()
# Iterate over rows in the dataframe to match the node and edge in the network graph.
for _, row in data.iterrows():
    concept1 = row['concept1']
    concept1_desc = row['concept1_desc']
    concept2 = row['concept2']
    concept2_desc = row['concept2_desc']
    relationship_desc = row['relationship_desc']
    # Add nodes with additional attributes `concept1_desc` and `concept2_desc`.
    G.add_node(concept1, concept1_desc=concept1_desc)
    G.add_node(concept2, concept2_desc=concept2_desc)
    # Add edges with the 'relationship_desc' attribute.
    G.add_edge(concept1, concept2, relationship_desc=relationship_desc)

# List of key main concepts to highlight (yellow boxes).
key_main_concepts = ["Distribution", "Random variables", "Moments", "Other"]

# Style:
node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        )
    )
)

edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5, color='#888'),
    hoverinfo='text',
    mode='lines'
)

for node, adjacencies in enumerate(G.adjacency()):
    node_trace['x'] += tuple([node])
    node_trace['y'] += tuple([len(adjacencies[1])])
    node_info = f"{adjacencies[0]}<br># of connections: {len(adjacencies[1])}"
    node_trace['text'] += tuple([node_info])

for edge in G.edges():
    x0, y0 = edge[0], len(G[edge[0]])
    x1, y1 = edge[1], len(G[edge[1]])
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

# Create subplot
fig = make_subplots(rows=1, cols=1)

# Add nodes and edges to subplot
fig.add_trace(node_trace)
fig.add_trace(edge_trace)

# Update layout
fig.update_layout(
    showlegend=False,
    hovermode='closest',
    title_text='Network Graph made with Plotly',
    template='plotly_dark'
)

# Show plot
fig.show()
