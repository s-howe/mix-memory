"""A module to convert Python network objects into d3-friendly network data."""

import json
from pathlib import Path

from pydantic import BaseModel

from mix_memory.track_network import TrackNetwork
from mix_memory.library import Library


class D3NetworkData:
    """Converts Python network objects into d3-friendly data in the form:
    { "nodes": [
        { "id": 1, "name": "A" },
        { "id": 2, "name": "B" }
    ],
      "links": [
        { "source": 1, "target": 2 }
    ]}
    """

    def __init__(self, network_dict: dict) -> None:
        """Initializes the D3NetworkData object.

        Raises:
            ValidationError: if the given network_dict is not in the form
                { "nodes": [
                    { "id": 1, "name": "A" },
                    { "id": 2, "name": "B" }
                ],
                "links": [
                    { "source": 1, "target": 2 }
                ]}
        """

        # Validate given dict
        class Node(BaseModel):
            id: int
            name: str

        class Link(BaseModel):
            source: int
            target: int

        class NetworkDictSchema(BaseModel):
            nodes: list[Node]
            links: list[Link]

        NetworkDictSchema(**network_dict)

        self.network_dict = network_dict

    @classmethod
    def from_track_network_and_library(
        cls, track_network: TrackNetwork, library: Library
    ):
        return cls(
            {
                "nodes": [
                    {"id": track_id, "name": str(library[track_id])}
                    for track_id in track_network.track_ids
                ],
                "links": [
                    {"source": source_track_id, "target": target_track_id}
                    for source_track_id, target_track_id in track_network.connections
                ],
            }
        )

    def to_json(self, file_path: Path) -> None:
        with file_path.open("w") as fp:
            json.dump(self.network_dict, fp, indent=4)
