from pathlib import Path
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from mix_memory.d3_network_data import D3NetworkData
from mix_memory.database import Database, LibraryData, ConnectionsData
from mix_memory.library import Track, merge_libraries
from mix_memory.track_network import TrackNetwork
from mix_memory.rekordbox import (
    load_rekordbox_histories_since,
    RekordboxHistoryPlaylist,
)


console = Console()


def load_track_network_from_db(db_name: str) -> TrackNetwork:
    """Load the track network from the database."""
    database = Database(db_name)
    library = LibraryData.from_sqlite(database).to_library()
    connections = ConnectionsData.from_sqlite(database).to_connections()
    track_network = TrackNetwork.from_library_and_connections(library, connections)
    return track_network


def save_track_network_to_db(track_network: TrackNetwork, db_name: str) -> None:
    """Save the track network to the database."""
    database = Database(db_name)
    LibraryData.from_library(track_network.library).to_sqlite(database)
    ConnectionsData.from_connections(track_network.connections).to_sqlite(database)


@click.group()
@click.option(
    "--db_name",
    default="mix-memory.db",
    envvar="DB_NAME",
    help="Path to the SQLite database.",
)
@click.pass_context
def cli(ctx: click.Context, db_name: str):
    # Initialize context dict
    ctx.ensure_object(dict)

    # Add context values for all commands in group
    ctx.obj["db_name"] = db_name


@cli.command()
@click.option(
    "--force", is_flag=True, help="Force recreation without asking for confirmation."
)
@click.pass_context
def init_db(ctx: click.Context, force: bool) -> None:
    """Drop existing database and recreate with empty tables."""
    db_name = ctx.obj["db_name"]

    if not force:
        if not Confirm.ask(
            f"[yellow]Are you sure you want to reset the database {db_name}?[/yellow]"
        ):
            raise click.Abort()

    Database(name=db_name).create_tables()
    console.print(f"Database [green]{db_name}[/green] has been recreated.")


@cli.command()
@click.argument("artist")
@click.argument("title")
@click.pass_context
def add_track(ctx: click.Context, artist: str, title: str) -> None:
    db_name = ctx.obj["db_name"]
    track_network = load_track_network_from_db(db_name)
    track = Track(artist, title)
    track_network.library.add_track(track)
    save_track_network_to_db(track_network, db_name)
    console.print(f"Track added to library: [green]{track}[/green]")


@cli.command()
@click.argument("source_track_artist")
@click.argument("source_track_title")
@click.argument("target_track_artist")
@click.argument("target_track_title")
@click.option(
    "--bidirectional",
    is_flag=True,
    default=False,
    help="A bidirectional connection should be added.",
)
@click.pass_context
def add_connection(
    ctx: click.Context,
    source_track_artist: str,
    source_track_title: str,
    target_track_artist: str,
    target_track_title: str,
    bidirectional: bool,
) -> None:
    """Add a connection from one track to another."""
    db_name = ctx.obj["db_name"]
    track_network = load_track_network_from_db(db_name)
    source_track_id = track_network.library.get_track_id_from_artist_title(
        artist=source_track_artist, title=source_track_title
    )
    target_track_id = track_network.library.get_track_id_from_artist_title(
        artist=target_track_artist, title=target_track_title
    )
    track_network.add_connection(
        source_track_id=source_track_id,
        target_track_id=target_track_id,
        bidirectional=bidirectional,
    )
    save_track_network_to_db(track_network, db_name)

    conn_str = " <-> " if bidirectional else " -> "
    console.print(
        f"Connection added: [green]{source_track_artist} - {source_track_title}[/green]{conn_str}"
        f"[green]{target_track_artist} - {target_track_title}[/green]"
    )


@cli.command()
@click.argument("track_artist")
@click.argument("track_title")
@click.pass_context
def next_track_options(ctx: click.Context, track_artist: str, track_title: str) -> None:
    """Recommend options for the next track from a given track based on saved
    transitions."""
    db_name = ctx.obj["db_name"]
    track_network = load_track_network_from_db(db_name)

    now_playing_track = Track(track_artist, track_title)
    now_playing_track_id = track_network.library.get_track_id_from_track(
        now_playing_track
    )

    # Get possible next tracks
    possible_next_track_ids = track_network.get_connected_track_ids(
        now_playing_track_id
    )
    possible_next_tracks = [
        track_network.library[track_id] for track_id in possible_next_track_ids
    ]

    if possible_next_tracks:
        table = Table(title=f"Recommendations for {now_playing_track}")
        table.add_column("Artist", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta", no_wrap=True)

        for track in possible_next_tracks:
            table.add_row(track.artist, track.title)

        console.print(table)
    else:
        console.print(f"[red]No recommendations found for {now_playing_track}.[/red]")


@cli.command()
@click.option(
    "--output-file",
    default="./web/track_network.json",
    show_default=True,
    help="Path to save the JSON file.",
)
@click.pass_context
def export_network_for_d3(ctx: click.Context, output_file: str) -> None:
    """Export the track network as a JSON file ready for visualizing using d3.js."""
    db_name = ctx.obj["db_name"]
    track_network = load_track_network_from_db(db_name)
    D3NetworkData.from_track_network(track_network).to_json(file_path=output_file)
    console.print(f"Track network exported to [green]{output_file}[/green]")


@cli.command()
@click.option(
    "--rekordbox-histories-dir",
    default="./rekordbox_histories",
    show_default=True,
    help="The directory from which Rekordbox history exported as .m3u8 files should be read.",
)
@click.option(
    "--min-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help=(
        "The minimum date to read Rekordbox history playlists from. Format YYYY-MM-DD. "
        "Optional."
    ),
)
@click.pass_context
def load_track_network_from_rekordbox_histories(
    ctx: click.Context, rekordbox_histories_dir: str, min_date: datetime.date
) -> None:
    """Loads the library from a directory of Rekordbox history playlist .m3u8 exports.
    A survey is then carried out for the user to mark good transitions. These
    transitions are then used to create a track network. The network can then be saved
    to the database."""
    db_name = ctx.obj["db_name"]
    playlists = load_rekordbox_histories_since(
        rekordbox_histories_dir=Path(rekordbox_histories_dir), min_date=min_date
    )

    library = merge_libraries(playlists)
    track_network = TrackNetwork.from_library(library)

    console.print(f"Loaded {len(playlists)} playlists into library.")

    _add_connections_from_playlists(track_network, playlists, db_name)


@cli.command()
@click.option(
    "--rekordbox-histories-dir",
    default="./rekordbox_histories",
    show_default=True,
    help="The directory from which Rekordbox history exported as .m3u8 files should be read.",
)
@click.option(
    "--min-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help=(
        "The minimum date to read Rekordbox history playlists from. Format YYYY-MM-DD. "
        "Optional."
    ),
)
@click.pass_context
def update_track_network_from_rekordbox_histories(
    ctx: click.Context, rekordbox_histories_dir: str, min_date: datetime.date
) -> None:
    """Updates an existing track network from a directory of Rekordbox history playlist
    .m3u8 exports. A survey is then carried out for the user to mark good transitions.
    The updated network can then be saved to the database."""
    db_name = ctx.obj["db_name"]

    track_network = load_track_network_from_db(db_name)

    playlists = load_rekordbox_histories_since(
        rekordbox_histories_dir=Path(rekordbox_histories_dir), min_date=min_date
    )

    library_playlists = merge_libraries(playlists)

    n_tracks_original = len(track_network.library)
    track_network.library = track_network.library.extend(library_playlists)
    n_tracks_new = len(track_network.library)
    console.print(f"Loaded {n_tracks_new - n_tracks_original} new tracks into library.")

    _add_connections_from_playlists(track_network, playlists, db_name)


def _add_connections_from_playlists(
    track_network: TrackNetwork, playlists: list[RekordboxHistoryPlaylist], db_name: str
) -> None:
    """Surveys the user about each transition in a list of Rekordbox history playlists.
    Good transitions are saved to the track network. The track network can then be saved
    to the database."""
    for playlist in playlists:
        console.print(
            f"\n[bold magenta]=== Transitions Survey: {playlist.name} ===[/bold magenta]\n"
            "Mark good transitions for each suggested pair.\n"
            "Type 'y' for Yes, 'n' for No, or 'Ctrl+C' to exit."
        )
        for start_track, end_track in playlist.transitions():
            if Confirm.ask(
                f"[yellow]{start_track}[/yellow] -> [yellow]{end_track}[/yellow]?"
            ):
                source_track_id = track_network.library.get_track_id_from_track(
                    start_track
                )
                target_track_id = track_network.library.get_track_id_from_track(
                    end_track
                )
                track_network.add_connection(source_track_id, target_track_id)

    if Confirm.ask(f"Save network to database [yellow]{db_name}[/yellow]?"):
        save_track_network_to_db(track_network, db_name)
