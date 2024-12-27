import networkx as nx
from pydantic import BaseModel, ValidationError

from mix_memory.library import Library


class TrackIdConnections(list):
    """A class to represent connections between pairs of tracks. These connections are
    stored as a list of tuples, each holding two track IDs (integers), the first being
    the source of the connection, the second the target."""

    def __init__(self, l):
        """Initialize the TrackIDConnections object.

        Raises:
            ValidationError: if passed object is not an iterable of 2-element tuples
                with both elements being integers.
        """

        # Validate given list
        class TrackConnectionModel(BaseModel):
            connection: tuple[int, int]

        for i in l:
            TrackConnectionModel(connection=i)

        super().__init__(l)


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
        cls, library: Library, connections: TrackIdConnections | None = None
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
        for track_id in library.tracks.keys():
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
    def connections(self) -> TrackIdConnections:
        return TrackIdConnections(list(self._graph.edges()))

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
        for track_id in [source_track_id, target_track_id]:
            if not track_id in self._graph.nodes:
                raise ValueError(f"Track ID does not exist: {track_id}")

        self._graph.add_edge(source_track_id, target_track_id)

        if bidirectional:
            # Add another edge in the opposite direction.
            self._graph.add_edge(target_track_id, source_track_id)

    def remove_connection(self, source_track_id: int, target_track_id: int) -> None:
        """Remove a connection between two tracks.

        Raises:
            ValueError: if either track doesn't exist in the network.
        """
        for track_id in [source_track_id, target_track_id]:
            if not track_id in self._graph.nodes:
                raise ValueError(f"Track ID does not exist: {track_id}")

        self._graph.remove_edge(source_track_id, target_track_id)
