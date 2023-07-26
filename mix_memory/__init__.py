import json
from pathlib import Path
from mix_memory.plotting import visualize_connections, visualize_network


class Track:
    def __init__(self, track_id: int, title: str, artist: str = None) -> None:
        self.track_id = track_id
        self.title = title
        if artist is None:
            self.artist, self.title = self.infer_artist()
        self.connections = []

    def __repr__(self) -> str:
        return f'Track({self.track_id}, {self.title}, {self.artist})'
    
    def __str__(self) -> str:
        return f'{self.track_id} - {self.artist} - {self.title}'

    def infer_artist(self) -> str:
        """Infer artist from track title."""
        if ' - ' in self.title:
            return self.title.split(' - ')
        return 'Unknown', self.title

class TrackNetwork:
    def __init__(self) -> None:
        """Initialize the network. 
        
        The network is represented as a dictionary of tracks, where the key is
        the track id and the value is a Track object.
        
        The Track object has the following attributes:
        - track_id: the track id
        - title: the title of the track
        - artist: the artist of the track
        - connections: a list of tuples, where each tuple contains the track id
          of a connected track and the strength of the connection
        """
        self.tracks = {}

    def add_track(self, track_id: int, title: str, artist: str = None):
        """Add a track to the network."""
        if track_id not in self.tracks:
            self.tracks[track_id] = Track(track_id, title, artist)
        return self.tracks[track_id]

    def add_connection(self, 
                       track_id1: int, 
                       track_id2: int, 
                       direction: str = 'both',
                       strength: int = 3) -> None:
        """Add a connection between two tracks.

        The direction of the connection can be 'both' or 'forward'.
        
        The strength of the connection is a number between 1 and 3, where 1 is
        a weak connection and 3 is a strong connection."""
        if track_id1 in self.tracks and track_id2 in self.tracks:
            self.tracks[track_id1].connections.append((track_id2, strength))
            if direction == 'both':
                self.tracks[track_id2].connections.append((track_id1, strength))

    def add_connection_from_string(self, 
                                   connection: str, 
                                   strength: int = 3) -> None:
        """Add a connection from a string."""

        # Split the connection string into two track titles.
        direction_mapping = {' <-> ': 'both', ' -> ': 'forward'}
        for delimiter in direction_mapping:
            if delimiter in connection:
                direction = direction_mapping[delimiter]
                title1, title2 = connection.split(delimiter)
                break
        else:
            raise ValueError('Invalid connection string.')
        
        # Find the track ids of the two tracks.
        track_id1 = self.get_id_from_title(title1)
        track_id2 = self.get_id_from_title(title2)
        if track_id1 is None:
            track1 = self.add_track(len(self.tracks), title1)
            track_id1 = track1.track_id
        if track_id2 is None:
            track2 = self.add_track(len(self.tracks), title2)
            track_id2 = track2.track_id
        
        # Add the connection.
        self.add_connection(track_id1, track_id2, direction, strength)

    def get_id_from_title(self, title: str) -> int:
        """Get the track id from a track title."""
        for track_id, track in self.tracks.items():
            if track.title in (title, title.split(' - ')[-1]):
                return track_id
        return None

    def get_connected_songs(self, track_id: int) -> list[int]:
        """Get all songs connected to a given song."""
        if track_id in self.tracks:
            return self.tracks[track_id].connections
        return []
    
    def visualize_network(self, depth: int = 1) -> None:
        """Visualize the network."""
        visualize_network(self, depth)

    def visualize_connections(self, track_id: int, depth: int = 1) -> None:
        """Visualize the connections of a given song."""
        if track_id in self.tracks:
            visualize_connections(self, track_id, depth)

    def print_network(self, depth: int = 1) -> None:
        """Print the network."""
        for track_id in self.tracks:
            print(self.tracks[track_id])
            for connected_track_id, strength in self.get_connected_songs(track_id):
                print(f'  {self.tracks[connected_track_id]} ({strength})')
                if depth > 1:
                    for connected_track_id2, strength2 in self.get_connected_songs(connected_track_id):
                        print(f'    {self.tracks[connected_track_id2]} ({strength2})')

    def to_json(self, file_name: str | Path) -> str:
        """Convert the network to a JSON string."""
        with open(file_name, 'w') as json_file:
            json.dump(self.tracks, json_file, indent=4)
