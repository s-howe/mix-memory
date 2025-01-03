import networkx as nx
from pydantic import BaseModel, ValidationError
from typing import NamedTuple

from mix_memory.library import Library


__all__ = ["TrackIdConnections", "TrackNetwork"]


class TrackIdConnection(NamedTuple):
    """A connection representing a directional transition between two tracks. Stored as
    a tuple of two track IDs (integers)."""

    source: int
    target: int


class TrackNetwork:
    """A class to represent a network of tracks as a directed graph. Each track is a
    node, and each connection is an edge on the network graph. These are stored in a
    NetworkX DiGraph."""

    def __init__(self, graph: nx.DiGraph, library: Library) -> None:
        self._graph = graph
        self.library = library

    def __repr__(self) -> str:
        return f"TrackNetwork({self.n_tracks} tracks, {self.n_connections} connections)"

    def __str__(self) -> str:
        return (
            "TrackNetwork of "
            f"{self.n_tracks} tracks with "
            f"{self.n_connections} connections."
        )

    @classmethod
    def from_library_and_connections(
        cls, library: Library, connections: list[TrackIdConnection] | None = None
    ) -> "TrackNetwork":
        """
        Initialize a TrackNetwork instance from a Library and dictionary of track ID
        connections.

        Parameters:
            library: The library instance.
            connections: A list of tuples representing the connections between tracks.
                If None, then the network will be initiated with no connections.
        """
        graph = nx.DiGraph()

        # Add nodes to the graph
        for track_id in library.track_map.keys():
            graph.add_node(track_id)

        # Add edges to graph
        if connections is not None:
            for track_id, neighbor_id in connections:
                graph.add_edge(track_id, neighbor_id)

        return cls(graph=graph, library=library)

    @classmethod
    def from_library(cls, library: Library) -> "TrackNetwork":
        """Initialize a blank TrackNetwork instance with no connections from a library."""
        return cls.from_library_and_connections(library=library, connections=None)

    @property
    def track_ids(self) -> list[int]:
        return list(self._graph.nodes())

    @property
    def connections(self) -> list[TrackIdConnection]:
        return [TrackIdConnection(*e) for e in self._graph.edges()]

    @property
    def n_tracks(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def n_connections(self) -> int:
        return self._graph.number_of_edges()

    def add_connection(
        self, source_track_id: int, target_track_id: int, bidirectional: bool = False
    ) -> None:
        """Add a connection between two tracks.

        Raises:
            ValueError: if either track doesn't exist in the network.
        """
        connection = TrackIdConnection(source=source_track_id, target=target_track_id)
        for track_id in connection:
            if not track_id in self._graph.nodes:
                raise ValueError(f"Track ID does not exist in network: {track_id}")

        self._graph.add_edge(connection.source, connection.target)

        if bidirectional:
            # Add another edge in the opposite direction.
            self._graph.add_edge(connection.target, connection.source)

    def remove_connection(self, source_track_id: int, target_track_id: int) -> None:
        """Remove a connection between two tracks.

        Raises:
            ValueError: if either track doesn't exist in the network.
        """
        connection = TrackIdConnection(source=source_track_id, target=target_track_id)
        for track_id in connection:
            if not track_id in self._graph.nodes:
                raise ValueError(f"Track ID does not exist: {track_id}")

        self._graph.remove_edge(connection.source, connection.target)

    def get_connected_track_ids(self, source_track_id: int) -> list[int]:
        """Return the list of connected tracks from a source track ID."""
        neighbours = self._graph.adj[source_track_id]
        return list(neighbours)
