# Mix Memory

## Intro

`mix-memory` is a proof-of-concept feature suggestion for AlphaTheta's Rekordbox software, 
developed in Python and visualized using d3.js.

The idea is to provide DJs with a tool to store and recall successful track transitions, 
helping them build a personal library of tried-and-tested track pairs or "set pieces."

The industry standard DJing software is AlphaTheta's Rekordbox. At the moment, Rekordbox
does not offer a way to save good transitions. Ideally, a DJ would be able
to use Rekordbox during a performance to save pairs of tracks that worked well together. 
In future, when they are playing a track and unsure which track to play next, they 
could recall their previously saved transitions from this track to others, providing a 
list of tried-and-tested options for the next track.

This collection of track pairs is represented by a graph network. Each track in a DJ's
library is a node, and each pairing is saved as an edge. These edges could be 
unidirectional (Track A transitions well into Track B, but not vice versa) or 
bidirectional (mixing in both directions works well).

## Installation

To install the Python package and CLI, run

``` sh
pip install .
```

## Command Line Interface

All functions of mix-memory are exposed via a command-line interface. See the various
commands by running

``` console
$ mix-memory --help
```

Example output for displaying the next track options from a now-playing
track:

``` console
$ mix-memory next-track-options OCH Whalesong

     Recommendations for OCH - Whalesong      
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Artist    ┃ Title                          ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Leftfield │ Not forgotten (Hard Hands Mix) │
│ Pizarro   │ Five Tones                     │
│ Pizarro   │ Release Me                     │
└───────────┴────────────────────────────────┘                        
```

### Loading from Rekordbox histories

A track network can be loaded from Rekordbox history playlists.

1. Export all relevant history playlists from Rekordbox in `.m3u8` format. Save or copy
these to a directory in this project e.g. `./rekordbox_histories`.
2. If there is no existing library or track network in the database, or if you wish to 
overwrite an existing track network, run the `load-track-network-from-rekordbox-histories`
command. Optionally supply a minimum date to read from in the format YYYY-MM-DD.

```console
$ mix-memory load-track-network-from-rekordbox-histories --min-date {min_date}
```

`mix-memory` will survey you on each transition in the history playlists, giving you the
option to save good transitions for future reference.

3. If there is an existing library or track network in the database, and you wish to
update this with new track transitions, run the `update-track-network-from-rekordbox-histories` 
command. Use the minimum date argument to only transitions from new playlists into the
track network.

``` console
$ mix-memory update-track-network-from-rekordbox-histories --min-date {min_date}
```

Both of these commands will prompt a survey with which you can save good transitions
from each history playlist, like so:

```
=== Transitions Survey: HISTORY 2024-10-26.m3u8 ===
Mark good transitions for each suggested pair.
Type 'y' for Yes, 'n' for No, or 'Ctrl+C' to exit.

Len Lewis - Morpheus -> Corporation & DJ Scattie - Heat & Fire? [y/N]: 
```

## Examples

There is an example script at `examples/example.py` which showcases:
1. Creating a track library
1. Creating a track network and adding connections
1. Saving and loading these objects to/from a database
1. Recommending next tracks from a currently-playing track
1. Visualizing the network using d3.js

### Example visualization

TODO: add directionality to d3 visualization

![track network](./examples/track_network.png)

## Ideas for future development

### Weights

The network edges could have weights, representing the quality of the transition. In
practice, a DJ could then not only save a transition, but also rate it out of 5 based on
how smooth or energising it was.

### Suggested next tracks

A recommendation engine could be built to suggest transitions based on track features
e.g. shared key, rhythms etc.

### Shortest path

A DJ may aim to get from one track to another in the quickest way possible. This would
of course only be possible with a very well-populated network, but it is basically
the shortest path between two network nodes.

### Best path

A DJ may aim to get from one track to another via the best possible transitions. This 
would of course only be possible with a very well-populated network, but it could be
derived from the path with the highest average weight per network edge.
