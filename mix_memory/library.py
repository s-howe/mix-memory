from collections.abc import MutableMapping
import hashlib
from pathlib import Path
from typing import NamedTuple


__all__ = ["Track", "Library"]


class Track(NamedTuple):
    """A music track."""

    artist: str
    title: str

    @property
    def hash8(self):
        """A simple 8-digit hash to use as a track ID."""
        key = (self.artist, self.title)
        hash_input = str(key).encode("utf-8")
        self.hash8 = int(hashlib.md5(hash_input).hexdigest()[:8], 16)

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"


class MissingTrackError(Exception):
    pass


class DuplicateTrackError(Exception):
    pass


class Library:
    """A collection of music tracks. Tracks are stored in a dictionary with track IDs
    as keys."""

    def __init__(self, track_map: dict[int, Track] | None) -> None:
        """Initialize the Library object.

        Args:
            track_map: a dictionary with track IDs mapped to Track objects. If None,
                the library will be empty.
        """
        if track_map is None:
            track_map = {}

        self.track_map = track_map

    @classmethod
    def from_track_list(cls, track_list: list[Track]) -> "Library":
        """Initialize the Library from a list of tracks. Track IDs are generated from
        the list position."""
        track_map = {track.hash8: track for track in track_list}
        return cls(track_map=track_map)

    @classmethod
    def from_m3u_file(cls, file_path: Path) -> "Library":
        """Load a Library from an Apple Music m3u file. Track properties are parsed from
        #EXTINF lines in the file. Track IDs are generated sequentially."""
        track_list = []

        with file_path.open("r") as f:
            lines = f.readlines()
            extinf_lines = [l.strip() for l in lines if l.startswith("#EXTINF")]
            for line in extinf_lines:
                title_artist = line.split(",", 1)[1]
                title, artist = title_artist.split(" - ", 1)
                track_list.append(Track(title, artist))

        return cls.from_track_list(track_list=track_list)

    def __repr__(self) -> str:
        return f"Library({len(self.track_map)} Tracks)"

    def __str__(self) -> str:
        return self.__repr__()

    def __getitem__(self, id) -> Track:
        return self.track_map[id]

    def __len__(self) -> int:
        return len(self.track_map)

    def tracks(self) -> list[Track]:
        return list(self.track_map.values())

    def track_ids(self) -> list[int]:
        return list(self.track_map.keys())

    def add_track(self, track: Track) -> None:
        """Add a track to the library.

        Args:
            track: the track object to add to the library.

        Raises:
            DuplicateTrackError: if track already exists in library.
        """
        if track in self.track_map.values():
            raise DuplicateTrackError(f"Track already exists in library: {track}")

        track_id = track.hash8
        self.track_map[track_id] = track

    def remove_track_by_id(self, track_id: int) -> None:
        """Remove a track from the library by its ID.

        Raises:
            MissingTrackError: if track ID does not exist in the library.
        """
        if track_id not in self.track_map.keys():
            raise MissingTrackError(f"Track ID not in library: {track_id}")

        del self.track_map[track_id]

    def remove_track(self, track: Track) -> None:
        """Remove a track from the library.

        Raises:
            MissingTrackError: if track does not exist in the library.
        """
        track_id = self.get_track_id_from_track(track)
        self.remove_track_by_id(track_id=track_id)

    def get_track(self, track_id: int) -> Track:
        """Get a track from the library."""
        return self[track_id]

    def get_track_id_from_artist_title(self, artist: str, title: str) -> int:
        """Get the track ID from a track artist and title.

        Raises:
            MissingTrackError: if track artist and title doe not exist in library.
        """
        for track_id, track in self.track_map.items():
            if track.artist == artist and track.title == title:
                return track_id
        else:
            t = Track(artist, title)
            raise MissingTrackError(f"Track does not exist in library: {t}")

    def get_track_id_from_track(self, track: Track) -> int:
        """Get the track ID from a track object."""
        return self.get_track_id_from_artist_title(
            artist=track.artist, title=track.title
        )

    def extend(self, other: "Library") -> "Library":
        """Merges one library with another library."""
        merged_track_map = self.track_map.copy()
        merged_track_map.update(other.track_map)
        return Library(track_map=merged_track_map)


def merge_libraries(libraries: list[Library]) -> Library:
    """Merge many libraries into one."""
    libraries = libraries.copy()
    library = libraries.pop()

    for other in libraries:
        library = library.extend(other)

    return library
