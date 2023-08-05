import json
from pathlib import Path
from mix_memory.plotting import visualize_connections, visualize_network
from typing import List, Union, Optional, Dict
import networkx as nx


class Track:
    def __init__(self, track_id: int, title: str, artist: str = None) -> None:
        self.track_id = track_id
        self.title = title
        if artist is None:
            self.artist, self.title = self.infer_artist()
        self.connections = []

    @classmethod
    def from_file(cls, file_name: str | Path) -> list['Track']:
        """Initialize the Track instance from a file."""
        # TODO
        pass

    def __repr__(self) -> str:
        return f'Track({self.track_id}, {self.title}, {self.artist})'
    
    def __str__(self) -> str:
        return f'{self.track_id} - {self.artist} - {self.title}'

    def infer_artist(self) -> str:
        """Infer artist from track title."""
        if ' - ' in self.title:
            return self.title.split(' - ')
        return 'Unknown', self.title
    

class TrackCollection:
    def __init__(self, tracks) -> None:
        self.tracks = tracks

    @classmethod
    def from_json_file(cls, file_name: str | Path) -> 'TrackCollection':
        """Initialize the TrackCollection instance from a JSON file."""
        with open(file_name, 'r') as f:
            tracks = json.load(f)
        return cls(tracks)
    
    @classmethod
    def from_m3u_file(cls, file_path: str | Path) -> 'TrackCollection':
        """Load a TrackCollection from an m3u file."""
        tracks = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            track_id = 1
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # For simplicity, assume that the file path contains the title and artist info
                    # in the format: "Artist - Title.mp3"
                    file_path = Path(line)
                    title, ext = file_path.stem.rsplit(' - ', 1)
                    artist = None  # You can extract artist info if available in the file path
                    track = Track(track_id, title, artist)
                    tracks.append(track)
                    track_id += 1

        return cls(tracks)
    
    def to_json(self, file_name: str | Path = None) -> None:
        """Save the track collection to a JSON file or string."""
        json_serialize(self.tracks, file_name)

    def __repr__(self) -> str:
        return f'TrackCollection({self.tracks})'
    
    def __str__(self) -> str:
        if len(self.tracks) > 3:
            return f'TrackCollection({self.tracks[:3]}...)'
        return f'TrackCollection({self.tracks})'
    
    def __iter__(self):
        return iter(self.tracks)
    
    def __getitem__(self, id):
        return self.get_track(id)
    
    def __len__(self):
        return len(self.tracks)
    
    def add_track(self, track: Track) -> None:
        """Add a track to the track collection."""
        self.tracks.append(track)
    
    def remove_track(self, track_id: int) -> None:
        """Remove a track from the track collection."""
        self.tracks = [track for track in self.tracks if track.track_id != track_id]

    def get_track(self, track_id: int) -> Track:
        """Get a track from the track collection."""
        return [track for track in self.tracks if track.track_id == track_id][0]    
    
    def get_track_from_title(self, title: str) -> Track:
        """Get the track from a track title."""
        for track in self.tracks:
            if track.title == title:
                return track
        return None
    
    def get_track_from_artist_title(self, artist: str, title: str) -> Track:
        """Get the track from a track artist and title."""
        for track in self.tracks:
            if track.artist == artist and track.title == title:
                return track
        return None
    

class TrackNetwork:
    def __init__(self, track_collection: TrackCollection, 
                       connections: Optional[Dict[int, List[int]]] = None) -> None:
        self.track_collection = track_collection
        self.graph = self.create_networkx_graph(connections)

    @classmethod
    def from_json_file(cls, file_name: str | Path) -> 'TrackNetwork':
        """Initialize the TrackNetwork instance from a JSON file."""
        with open(file_name, 'r') as f:
            graph_json = json.load(f)
        graph = nx.node_link_graph(graph_json)
        track_collection = cls.create_track_collection(graph)
        return cls(track_collection, graph)
    
    @classmethod
    def create_track_collection(cls, graph: nx.DiGraph) -> TrackCollection:
        """Create a TrackCollection instance from a NetworkX directional graph."""
        tracks = []
        for node, data in graph.nodes(data=True):
            track_id = node
            title = data['title']
            artist = data['artist']
            track = Track(track_id, title, artist)
            tracks.append(track)
        return TrackCollection(tracks)

    def create_networkx_graph(self, 
                              connections: Optional[Dict[int, List[int]]] = None) -> nx.DiGraph:
        """
        Create a NetworkX directional graph from the TrackCollection instance.

        Parameters:
            connections (Optional[Dict[int, List[int]]]): A dictionary representing the connections
                                                          between tracks. If not provided, the
                                                          connections will be inferred from the
                                                          TrackCollection instance.

        Returns:
            nx.DiGraph: A directional graph representing the tracks.
        """
        graph = nx.DiGraph()
        
        # Add nodes to the graph
        for track in self.track_collection.tracks:
            graph.add_node(track.track_id)

        # Add edges to the graph
        if connections is None:
            connections = {track.track_id: track.connections 
                           for track in self.track_collection.tracks}
        
        for track_id, track_connections in connections.items():
            for neighbor_id, strength in track_connections:
                graph.add_edge(track_id, neighbor_id, strength=strength)

        return graph
    
    def add_connection(self, source_track_id: int, target_track_id: int, 
                       strength: int = 1) -> None:
        """Add a connection between two tracks."""
        if source_track_id in self.graph.nodes and target_track_id in self.graph.nodes:
            self.graph.add_edge(source_track_id, target_track_id, strength=strength)
        else:
            raise ValueError(f'Invalid track ID: {source_track_id} or {target_track_id}')
        
    def remove_connection(self, source_track_id: int, target_track_id: int) -> None:
        """Remove a connection between two tracks."""
        if source_track_id in self.graph.nodes and target_track_id in self.graph.nodes:
            self.graph.remove_edge(source_track_id, target_track_id)
        else:
            raise ValueError(f'Invalid track ID: {source_track_id} or {target_track_id}')
        
    def save_connections(self, file_name: str | Path) -> None:
        """Save the connections to a JSON file."""
        connections = {}
        for track_id in self.graph.nodes:
            connections[track_id] = self.graph[track_id]
        json_serialize(connections, file_name)

    def get_shortest_path(self, source_track: int, target_track: int) -> List[int]:
        """
        Get the shortest path between two tracks.

        Parameters:
            source_track (int): The ID of the source track.
            target_track (int): The ID of the target track.

        Returns:
            List[int]: A list of track IDs representing the shortest path from source to target.
                       If no path is found, an empty list will be returned.
        """
        if nx.has_path(self.graph, source_track, target_track):
            return nx.shortest_path(self.graph, source_track, target_track)
        else:
            return []
        
    def visualize_network(self, save_path: str | Path = None) -> None:
        """Visualize the network."""
        visualize_network(self.graph, save_path)

    def visualize_connections(self, track_id: int, 
                              save_path: str | Path = None) -> None:
        """Visualize the connections of a given song."""
        if track_id in self.tracks:
            visualize_connections(self.graph, track_id, save_path)

    def to_json(self, file_name: str | Path = None) -> None:
        """Save the network to a JSON file or string."""
        graph_json = nx.node_link_data(self.graph)
        json_serialize(graph_json, file_name)


def json_serialize(obj, file_name: str | Path = None):
    """Serialize an object to JSON."""
    if file_name is None:
        return json.dumps(obj)
    else:
        with open(file_name, 'w') as f:
            json.dump(obj, f)
