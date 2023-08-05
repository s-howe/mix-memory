import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt


def deduplicate_edges(edges):
    """Deduplicate edges."""
    deduplicated_edges = []
    for edge in edges:
        if edge not in deduplicated_edges and edge[::-1] not in deduplicated_edges:
            deduplicated_edges.append(edge)
    return deduplicated_edges


def visualize_network(graph: nx.DiGraph, save_path: str | Path = None) -> None:
    """Visualize the graph with weights."""
    plt.figure(figsize=(10, 10))
    pos = nx.circular_layout(graph, k=0.5)
    edge_labels = nx.get_edge_attributes(graph, 'strength')
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', 
            node_size=1500, edge_cmap=plt.cm.Blues)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    plt.show()
    if save_path:
        plt.savefig(save_path)


def visualize_connections(graph: nx.DiGraph, track_id: int, 
                          save_path: str | Path = None) -> None:
    """Visualize the connections of a track in the graph."""
    plt.figure(figsize=(10, 10))
    node = graph.nodes[track_id]
    neighbors = graph.neighbors(track_id)
    neighbors = [graph.nodes[n] for n in neighbors]
    neighbors.append(node)
    subgraph = graph.subgraph(neighbors)
    pos = nx.circular_layout(subgraph, k=0.5)
    edge_labels = nx.get_edge_attributes(subgraph, 'strength')
    nx.draw(subgraph, pos, with_labels=True, node_color='skyblue', 
            node_size=1500, edge_cmap=plt.cm.Blues)
    nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels)
    plt.show()
    if save_path:
        plt.savefig(save_path)

