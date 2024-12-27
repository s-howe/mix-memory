from pathlib import Path


__all__ = ["Track", "Library"]


class Track:
    """A music track."""

    def __init__(self, artist: str, title: str) -> None:
        """Initialize the Track object."""
        self.artist = artist
        self.title = title

    def __repr__(self) -> str:
        return f"Track(artist={self.artist}, title={self.title})"

    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"


class Library:
    """A collection of music tracks. Tracks are stored in a dictionary with track IDs
    as keys."""

    def __init__(self, tracks: dict[int, Track]) -> None:
        """Initialize the Library object.

        Args:
            tracks: a dictionary with track IDs mapped to Track objects.
        """
        self.tracks = tracks

    @classmethod
    def from_track_list(cls, track_list: list[Track]) -> "Library":
        """Initialize the Library from a list of tracks. Track IDs are generated from
        the list position."""
        return cls(tracks=dict(enumerate(track_list)))

    @classmethod
    def from_m3u_file(cls, file_path: Path) -> "Library":
        """Load a Library from an Apple Music m3u file. Track properties are parsed from
        #EXTINF lines in the file. Track IDs are generated sequentially."""
        track_list = []

        with file_path.open("r") as f:
            lines = f.readlines()
            extinf_lines = [l for l in lines if l.startswith("#EXTINF")]
            for line in extinf_lines:
                title_artist = line.split(",")[1]
                title, artist = title_artist.split(" - ")
                track_list.append(Track(title, artist))

        return cls.from_track_list(track_list=track_list)

    def __repr__(self) -> str:
        return f"Library({len(self.tracks)} Tracks)"

    def __str__(self) -> str:
        return self.__repr__()

    def __getitem__(self, id) -> Track:
        return self.tracks[id]

    def __len__(self) -> int:
        return len(self.tracks)

    def add_track(self, track: Track, track_id: int | None = None) -> None:
        """Add a track to the library.

        Args:
            track: the track object to add to the library.
            track_id: the track ID to give the new track. If None, a new one will be
                incremented from the current max track ID.

        Raises:
            ValueError: if track ID already exists in library.
        """
        if track_id in self.tracks.keys():
            raise ValueError(f"Track ID already exists in library: {track_id}")

        if track_id is None:
            track_id = max(self.tracks.keys()) + 1

        self.tracks[track_id] = track

    def remove_track(self, track_id: int) -> None:
        """Remove a track from the library.

        Raises:
            KeyError: if track ID does not exist in the library.
        """
        if track_id not in self.tracks.keys():
            raise ValueError(f"Track ID not in library: {track_id}")

        del self.tracks[track_id]

    def get_track(self, track_id: int) -> Track:
        """Get a track from the library."""
        return self[track_id]

    def get_track_id_from_artist_title(self, artist: str, title: str) -> int:
        """Get the track ID from a track artist and title."""
        for track_id, track in self.tracks.items():
            if track.artist == artist and track.title == title:
                return track_id
        return None

    def get_track_id_from_track(self, track: Track) -> int:
        """Get the track ID from a track object."""
        return self.get_track_id_from_artist_title(
            artist=track.artist, title=track.title
        )
