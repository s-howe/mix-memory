from pathlib import Path
import sqlite3

from mix_memory.library import Library, Track
from mix_memory.track_network import TrackIdConnections


__all__ = ["Database", "LibraryData", "ConnectionsData"]


class Database:
    def __init__(self, name: str | Path) -> None:
        if not name.endswith(".db"):
            name += ".db"

        self.name = name

    def create_tables(self):
        cur = sqlite3.connect(self.name).cursor()
        cur.execute("DROP TABLE IF EXISTS library")
        cur.execute("CREATE TABLE library(id, artist, title)")

        cur.execute("DROP TABLE IF EXISTS connections")
        cur.execute("CREATE TABLE connections(source_track_id, target_track_id)")
        cur.close()
        cur.connection.close()


class DBData:
    table_name: str | None = None

    def __init__(self, rows: list):
        self.rows = rows

    @classmethod
    def from_sqlite(cls, database: Database) -> "DBData":
        cur = sqlite3.connect(database.name).cursor()
        query = cur.execute(f"SELECT * FROM {cls.table_name}")
        colname = [d[0] for d in query.description]
        result_list = [dict(zip(colname, r)) for r in query.fetchall()]
        cur.close()
        cur.connection.close()

        return cls(rows=result_list)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nrows={len(self.rows)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.rows)} rows."


class LibraryData(DBData):
    table_name = "library"

    @classmethod
    def from_library(cls, library: Library) -> "LibraryData":
        rows = [
            {"id": track_id, "artist": track.artist, "title": track.title}
            for track_id, track in library.track_map.items()
        ]
        return cls(rows=rows)

    def to_library(self) -> Library:
        return Library(
            track_map={
                row["id"]: Track(artist=row["artist"], title=row["title"])
                for row in self.rows
            }
        )

    def to_sqlite(self, database) -> None:
        cur = sqlite3.connect(database.name).cursor()
        for row in self.rows:
            cur.execute(
                "INSERT INTO library (id, artist, title) VALUES (:id, :artist, :title)",
                row,
            )
        cur.connection.commit()
        cur.close()
        cur.connection.close()


class ConnectionsData(DBData):
    table_name = "connections"

    @classmethod
    def from_connections(cls, connections: TrackIdConnections) -> "ConnectionsData":
        rows = [
            {
                "source_track_id": source_track_id,
                "target_track_id": target_track_id,
            }
            for source_track_id, target_track_id in connections
        ]
        return cls(rows=rows)

    def to_connections(self) -> TrackIdConnections:
        return TrackIdConnections(
            [(row["source_track_id"], row["target_track_id"]) for row in self.rows]
        )

    def to_sqlite(self, database) -> None:
        cur = sqlite3.connect(database.name).cursor()
        for row in self.rows:
            cur.execute(
                "INSERT INTO connections (source_track_id, target_track_id) "
                "VALUES (:source_track_id, :target_track_id)",
                row,
            )
        cur.connection.commit()
        cur.close()
        cur.connection.close()
