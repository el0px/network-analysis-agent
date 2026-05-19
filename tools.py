import pandas as pd
import numpy as np
import networkx as nx
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # stops matplotlib from opening any windows at all

def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    print(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns")
    return df

def compute_correlations(df: pd.DataFrame, threshold: float = 0.7) -> pd.DataFrame:
    corr_matrix = df.corr()

    pairs = []

    # loop through every pair of columns in corr_matrix
    # if the correlation value is above threshold AND the two columns aren't the same column
    # append a dict to pairs: {"node_a": col1, "node_b": col2, "correlation": value}

    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) >= threshold:
                pairs.append({"node_a": col1, "node_b": col2, "correlation": corr_value})
    return pd.DataFrame(pairs)


def build_network(corr_df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    for _, row in corr_df.iterrows():
        G.add_edge(row['node_a'], row['node_b'], weight=row['correlation'])
    return G

def find_hub_nodes(G: nx.Graph, top_n: int = 5) -> list:
    # G.degree() gives you (node, degree) pairs
    # sort them by degree, highest first
    # return just the top_n node names as a list

    degree_dict = dict(G.degree())
    sorted_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
    hubs = [node for node, degree in sorted_nodes[:top_n]]
    return hubs

def run_clustering(G: nx.Graph) -> dict:
    import networkx.algorithms.community as nx_comm

    if len(G.nodes()) == 0:
        return {}

    clusters = {}
    for node in G.nodes():
        clusters[node] = -1

    # Build weighted adjacency matrix
    nodes = list(G.nodes())
    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}
    
    # Distance matrix — strong correlation = small distance
    dist_matrix = np.ones((n, n))
    for u, v, data in G.edges(data=True):
        weight = abs(data.get('weight', 1.0))
        distance = 1 - weight  # 0.97 correlation → 0.03 distance
        i, j = node_idx[u], node_idx[v]
        dist_matrix[i][j] = distance
        dist_matrix[j][i] = distance

    np.fill_diagonal(dist_matrix, 0)

    # DBSCAN on distance matrix
    db = DBSCAN(eps=0.3, min_samples=2, metric='precomputed')
    labels = db.fit_predict(dist_matrix)

    for node, label in zip(nodes, labels):
        clusters[node] = int(label)

    return clusters

def summarize_results(G: nx.Graph, hubs: list, clusters: dict) -> str:
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    unique_clusters = set(clusters.values()) - {-1}
    singletons = sum(1 for v in clusters.values() if v == -1)

    summary = (
        f"Network has {num_nodes} nodes and {num_edges} edges.\n"
        f"Found {len(unique_clusters)} clusters and {singletons} singleton nodes.\n"
        f"Top hub nodes (most connected): {', '.join(str(h) for h in hubs)}\n\n"
    )

    # Add cluster details with strongest edges
    for cid in sorted(unique_clusters):
        members = [n for n, c in clusters.items() if c == cid]
        summary += f"Cluster {cid}: {', '.join(members)}\n"

        # Find strongest internal edges
        internal_edges = [
            (u, v, d['weight'])
            for u, v, d in G.edges(data=True)
            if clusters.get(u) == cid and clusters.get(v) == cid
        ]
        if internal_edges:
            strongest = sorted(internal_edges, key=lambda x: abs(x[2]), reverse=True)[:3]
            for u, v, w in strongest:
                summary += f"  Strongest: {u}-{v} (correlation: {w:.3f})\n"

    return summary


def visualize_network_3d(G: nx.Graph, clusters: dict):
    import plotly.graph_objects as go
    import numpy as np

    hubs = set(find_hub_nodes(G))

    # Generate 3D positions
    pos = nx.spring_layout(G, dim=3, seed=42, k=2)

    # --- Build edge traces ---
    edge_x, edge_y, edge_z = [], [], []
    for u, v in G.edges():
        x0, y0, z0 = pos[u]
        x1, y1, z1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='rgba(150,150,150,0.4)', width=2),
        hoverinfo='none',
        name='Connections'
    )

    # --- Build node traces per cluster so you can click/toggle them ---
    unique_clusters = set(clusters.values())
    node_traces = []

    colors = [
        '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
        '#9b59b6', '#1abc9c', '#e67e22', '#34495e'
    ]

    for cluster_id in sorted(unique_clusters):
        cluster_nodes = [n for n, c in clusters.items() if c == cluster_id]
        if not cluster_nodes:
            continue

        nx_, ny_, nz_, hover_, color_, size_ = [], [], [], [], [], []

        for node in cluster_nodes:
            x, y, z = pos[node]
            nx_.append(x)
            ny_.append(y)
            nz_.append(z)

            degree = G.degree(node)
            corr_partners = [v if u == node else u for u, v in G.edges(node)]
            hover_.append(
                f"<b>{node}</b><br>"
                f"Cluster: {'Singleton' if cluster_id == -1 else cluster_id}<br>"
                f"Connections: {degree}<br>"
                f"Connected to: {', '.join(str(p) for p in corr_partners)}<br>"
                f"{'⭐ HUB NODE' if node in hubs else ''}"
            )

            if node in hubs:
                color_.append('#ff0000')
                size_.append(20)
            elif cluster_id == -1:
                color_.append('#95a5a6')
                size_.append(8)
            else:
                idx = cluster_id % len(colors)
                color_.append(colors[idx])
                size_.append(12)

        label = 'Singletons' if cluster_id == -1 else f'Cluster {cluster_id}'
        node_traces.append(go.Scatter3d(
            x=nx_, y=ny_, z=nz_,
            mode='markers+text',
            marker=dict(size=size_, color=color_, opacity=0.9,
                       line=dict(color='white', width=1)),
            text=[str(n) for n in cluster_nodes],
            textposition='top center',
            textfont=dict(size=9),
            hovertext=hover_,
            hoverinfo='text',
            name=label
        ))

    # --- Layout ---
    fig = go.Figure(
        data=[edge_trace] + node_traces,
        layout=go.Layout(
            title=dict(text='<b>Network Analysis — 3D Interactive</b><br>'
                           '<sup>Red=Hub  |  Click legend to toggle clusters  |  Scroll to zoom  |  Drag to rotate</sup>',
                      font=dict(size=16)),
            showlegend=True,
            legend=dict(title='Clusters (click to toggle)'),
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                bgcolor='rgb(10,10,20)'
            ),
            paper_bgcolor='rgb(10,10,20)',
            font=dict(color='white'),
            margin=dict(l=0, r=0, t=80, b=0),
            hovermode='closest'
        )
    )

    fig.show()
