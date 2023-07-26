import networkx as nx
import matplotlib.pyplot as plt

# TODO 
# - Refactor

def visualize_connections(network, track_id, depth=1):
    """Visualize the connections of a given song."""
    graph = nx.DiGraph()

    node = track_id
    track = network.tracks[track_id]
    node_connections = track.connections
    graph.add_node(node, track=track, color='red')
    for target, strength in node_connections:
        # Check if the edge is bidirectional (i.e., both nodes are connected to each other)
        graph.add_node(target, track=network.tracks[target], color='skyblue')
        target_connections = [conn[0] for conn in network.tracks[target].connections]
        if node in target_connections:
            # Add a bidirectional edge with the average strength of the two edges
            target_connection = [conn for conn in network.tracks[target].connections if conn[0] == node][0]
            reverse_strength = target_connection[1]
            bidirectional_strength = (strength + reverse_strength) / 2
            graph.add_edge(node, target, weight=bidirectional_strength, bidirectional=True)
        else:
            graph.add_edge(node, target, weight=strength, bidirectional=False)

    # Set up the positions for the nodes (optional)
    pos = nx.circular_layout(graph)

    node_labels = {node: f"{data['track'].artist}\n{data['track'].title}"
                   for node, data in graph.nodes(data=True)}

    # Draw the graph with custom settings
    plt.figure(figsize=(8, 6))
    bidirectional_edges = [(u, v) for u, v, d in graph.edges(data=True) if d['bidirectional']]
    bidirectional_edges = deduplicate_edges(bidirectional_edges)
    unidirectional_edges = [(u, v) for u, v, d in graph.edges(data=True) if not d['bidirectional']]
    nx.draw_networkx_nodes(graph, pos, node_size=500, node_color=[n[1]['color'] for n in graph.nodes(data=True)])
    nx.draw_networkx_edges(graph, pos, edgelist=unidirectional_edges, width=[d['weight'] / 3 for u, v, d in graph.edges(data=True) if not d['bidirectional']],
                        connectionstyle='arc3,rad=0.1', edge_color='gray', arrowsize=10, arrowstyle='->')
    nx.draw_networkx_edges(graph, pos, edgelist=bidirectional_edges, width=[d['weight'] / 3 for u, v, d in graph.edges(data=True) if d['bidirectional']],
                        connectionstyle='arc3,rad=-0.1', edge_color='gray', arrowsize=10, arrowstyle='<->')
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=7, font_color='black')

    # Show the plot
    plt.axis('off')
    plt.show()


def visualize_network(network, depth=1):
    # Create an empty graph
    graph = nx.DiGraph()

    # Add nodes and edges to the graph
    for track_id, track in network.tracks.items():
        node = track_id
        node_connections = track.connections
        graph.add_node(node, track=track)
        for target, strength in node_connections:
            # Check if the edge is bidirectional (i.e., both nodes are connected to each other)
            target_connections = [conn[0] for conn in network.tracks[target].connections]
            if node in target_connections:
                # Add a bidirectional edge with the average strength of the two edges
                target_connection = [conn for conn in network.tracks[target].connections if conn[0] == node][0]
                reverse_strength = target_connection[1]
                bidirectional_strength = (strength + reverse_strength) / 2
                graph.add_edge(node, target, weight=bidirectional_strength, bidirectional=True)
            else:
                graph.add_edge(node, target, weight=strength, bidirectional=False)

    # Set up the positions for the nodes (optional)
    pos = nx.circular_layout(graph)

    node_labels = {node: f"{data['track'].artist}\n{data['track'].title}"
                   for node, data in graph.nodes(data=True)}

    # Draw the graph with custom settings
    plt.figure(figsize=(8, 6))
    bidirectional_edges = [(u, v) for u, v, d in graph.edges(data=True) if d['bidirectional']]
    bidirectional_edges = deduplicate_edges(bidirectional_edges)
    unidirectional_edges = [(u, v) for u, v, d in graph.edges(data=True) if not d['bidirectional']]
    nx.draw_networkx_nodes(graph, pos, node_size=500, node_color='skyblue')
    nx.draw_networkx_edges(graph, pos, edgelist=unidirectional_edges, width=[d['weight'] / 3 for u, v, d in graph.edges(data=True) if not d['bidirectional']],
                        connectionstyle='arc3,rad=0.1', edge_color='gray', arrowsize=10, arrowstyle='->')
    nx.draw_networkx_edges(graph, pos, edgelist=bidirectional_edges, width=[d['weight'] / 3 for u, v, d in graph.edges(data=True) if d['bidirectional']],
                        connectionstyle='arc3,rad=-0.1', edge_color='gray', arrowsize=10, arrowstyle='<->')
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=7, font_color='black')

    # Show the plot
    plt.axis('off')
    plt.show()


def deduplicate_edges(edges):
    """Deduplicate edges."""
    deduplicated_edges = []
    for edge in edges:
        if edge not in deduplicated_edges and edge[::-1] not in deduplicated_edges:
            deduplicated_edges.append(edge)
    return deduplicated_edges
