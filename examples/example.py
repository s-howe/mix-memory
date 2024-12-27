from mix_memory.library import Track, Library
from mix_memory.track_network import TrackNetwork
from mix_memory.database import Database, LibraryData, ConnectionsData
from mix_memory.d3_network_data import D3NetworkData

CONNECTIONS = [
    "DJ Ed - Ocean of Tears -> MJ Nebreda - Bubalu",
    "DHS & Meat Beat Manifesto - International Soundsystem -> Überzone - Busy Child",
    "Disk - Night <-> K-Hand - Untitled A2",
    "K-Hand - Untitled A2 -> Da Boom Boys - Medusa",
    "Da Boom Boys - Medusa -> Vince Watson - Depth Soul",
    "Vince Watson - Depth Soul -> Callisto - Can't Wait",
    "Callisto - Can't Wait -> Circulation - Uncovered",
    "Leftfield - Not forgotten (Hard Hands Mix) <-> OCH - Whalesong",
    "Leftfield - Not forgotten (Hard Hands Mix) <-> Pizarro - Five Tones",
    "OCH - Whalesong <-> Pizarro - Five Tones",
    "Dee Vaz - Sputnik -> Mike Ash - Clone Cheek",
    "Mike Ash - Clone Cheek -> The He-Men - Flamingo",
    "The He-Men - Flamingo -> I Believe - Outside Time",
    "I Believe - Outside Time -> Pizarro - Release Me",
    "Pizarro - Release Me <-> OCH - Whalesong",
    "Wil Do - Sunrise Scene <-> Luke's Anger - Blind Test",
]


def library_from_connection_strs(connection_strs: list[str]) -> Library:
    """Converts a list of string representations of track connections into a library
    of music tracks."""
    artist_title_strs = set()
    for connection_str in connection_strs:
        split_str = " <-> " if " <-> " in connection_str else " -> "
        artist_title_strs = artist_title_strs.union(
            set(connection_str.split(split_str))
        )

    artists_titles = [s.split(" - ") for s in artist_title_strs]
    track_list = [Track(artist=artist, title=title) for artist, title in artists_titles]
    return Library.from_track_list(track_list)


def add_connections_to_track_network(
    track_network: TrackNetwork, connection_strs: list[str]
) -> TrackNetwork:
    """Converts a list of string representations of track connections into a list of
    track ID connections. A library is used to get the track ID of each track."""
    for connection_str in connection_strs:
        if " <-> " in connection_str:
            split_str = " <-> "
            bidirectional = True
        else:
            split_str = " -> "
            bidirectional = False

        artist_titles = [s.split(" - ") for s in connection_str.split(split_str)]
        source_track_id, target_track_id = (
            track_network.library.get_track_id_from_artist_title(
                artist=artist, title=title
            )
            for artist, title in artist_titles
        )

        track_network.add_connection(
            source_track_id=source_track_id,
            target_track_id=target_track_id,
            bidirectional=bidirectional,
        )

    return track_network


if __name__ == "__main__":
    # Construct a library
    library = library_from_connection_strs(CONNECTIONS)

    # Construct a blank track network, with no connections yet
    track_network = TrackNetwork.from_library(library)

    # Add the connections to the track network
    track_network = add_connections_to_track_network(track_network, CONNECTIONS)

    # Save the library and connections to a sqlite database
    database = Database("mix-memory.db")
    database.create_tables()
    library_data = LibraryData.from_library(library)
    connections_data = ConnectionsData.from_connections(track_network.connections)
    library_data.to_sqlite(database)
    connections_data.to_sqlite(database)

    # Reload the objects from the database
    del library
    del track_network
    del library_data
    del connections_data

    library = LibraryData.from_sqlite(database).to_library()
    connections = ConnectionsData.from_sqlite(database).to_connections()
    track_network = TrackNetwork.from_library_and_connections(library, connections)

    # Recommend some tracks to play after a given track
    now_playing_track = Track("OCH", "Whalesong")
    now_playing_track_id = library.get_track_id_from_track(now_playing_track)

    possible_next_track_ids = track_network.get_connected_track_ids(
        now_playing_track_id
    )
    possible_next_tracks = [library[track_id] for track_id in possible_next_track_ids]
    print(
        f"After playing {now_playing_track}, consider playing {', '.join(str(t) for t in possible_next_tracks)}"
    )

    # Export the network to d3-friendly JSON ready for visualization
    d3_network_data = D3NetworkData.from_track_network(track_network)
    d3_network_data.to_json("./web/track_network.json")

    # Visualize the network in d3 by running a web server e.g.
    # `python -m http.server --directory web 8000` and loading http://localhost:8000
