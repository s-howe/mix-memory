from datetime import datetime
from pathlib import Path
import re
from mix_memory.library import Library, Track, merge_libraries


class RekordboxHistoryM3UFile:
    """The exported .m3u8 file of a Rekordbox history playlist. Used for validating the
    filename and extracting the date and date file number of the file.

    Examples:
        - "HISTORY 2023-07-28.m3u8"
        - "HISTORY 2023-07-28 (4).m3u8"
    """

    filename_pattern = re.compile(r"^HISTORY (\d{4}-\d{2}-\d{2}) ?(\((\d+)\))?\.m3u8$")

    def __init__(self, file_path: Path) -> None:
        """Initialize the RekordboxHistoryM3UFile from the file path.

        Raises:
            ValueError: if the file name doesn't match the usual syntax of a Rekordbox
                history playlist file.
        """
        file_name = file_path.name
        match = self.filename_pattern.match(file_name)
        if not match:
            raise ValueError(
                f"File name doesn't match Rekordbox history pattern: {file_name}"
            )

        self.path = file_path
        self.name = file_name

        # Extract variables from regex groups
        date_str = match.group(1)
        self.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        self.date_file_number = match.group(3) if match.group(3) else 1


# TODO: update repr and str
class RekordboxHistoryPlaylist(Library):
    """A library specifically representing the tracks in a Rekordbox history
    playlist. Because a Rekordbox history playlist is ordered by the track play time,
    it serves as a good record of all the transitions a DJ made during a certain set."""

    def __init__(
        self,
        track_map: dict[int, Track],
        name: str,
        date: datetime.date,
        date_file_number: int,
    ) -> None:
        """Initialize the RekordboxHistoryPlaylist from a track map and metadata. For a
        RekordboxHistoryPlaylist, the track map must be ordered sequentially according
        to when the track was played."""
        super().__init__(track_map=track_map)
        self.name = name
        self.date = date
        self.date_file_number = date_file_number

    @classmethod
    def from_m3u_file(cls, file_path: str | Path) -> "RekordboxHistoryPlaylist":
        """Initialize the RekordboxHistoryPlaylist from the tracks and metadata in its
        .m3u8 file."""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        library = Library.from_m3u_file(file_path=file_path)

        # Load other metadata from the file e.g. the date
        file = RekordboxHistoryM3UFile(file_path=file_path)

        return cls(
            track_map=library.track_map,
            name=file.name,
            date=file.date,
            date_file_number=file.date_file_number,
        )

    def transitions(self) -> list[tuple[Track]]:
        """Because a Rekordbox history playlist is ordered by the track play time, it
        can be used as a record of all the transitions a DJ made during a set."""
        tracks = self.tracks()

        # Construct the list of transitions by pairing each track to the next
        transitions = [(tracks[i], tracks[i + 1]) for i, _ in enumerate(tracks[:-1])]
        return transitions


def load_rekordbox_histories_since(
    rekordbox_histories_dir: str | Path, min_date: datetime.date
) -> list[RekordboxHistoryPlaylist]:
    """Load multiple history playlists since a given date.

    Arguments:
        rekordbox_histories_dir: A directory containing exported .m3u8 files from
            Rekordbox history playlists.
        min_date: The minimum date from which history files should be read.
    """
    # Force path if str is given
    rekordbox_histories_dir = Path(rekordbox_histories_dir)

    rekordbox_history_files = [
        RekordboxHistoryM3UFile(f) for f in rekordbox_histories_dir.glob("*.m3u8")
    ]

    files_after_min_date = [f for f in rekordbox_history_files if f.date >= min_date]

    playlists = [
        RekordboxHistoryPlaylist.from_m3u_file(f.path) for f in files_after_min_date
    ]

    return playlists