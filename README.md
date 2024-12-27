# Mix Memory

## Intro

A Proof-of-Concept of a feature suggestion for AlphaTheta's Rekordbox software written
in Python and d3.js.

Often when DJing, DJs will make a mental note of transitions between tracks that worked
particularly well. A DJ might build a database of these "track pairs" or "set pieces"
in their head, ready to recall and replay during future performances.

The industry standard DJing software is AlphaTheta's Rekordbox. At the moment, there is
no feature with which a DJ can mark a particularly good transition. Ideally, after
noting such a transition during a performance, a DJ would be able to use Rekordbox
software to save away this pair of tracks. In future, if they are playing a track and
unsure which track to play next, they could recall their previously saved transitions
from this track to others, providing a list of tried-and-tested options for the next
track.

This collection of track pairs is perfectly described by a network. Each track in a DJ's
library is a node, and each pairing is saved as an edge. These edges could be 
unidirectional (Track A transitions well into Track B, but not vice versa) or 
bidirectional (Track A transitions well into Track B and vice versa).

## Ideas for future development

### Weights

The network edges could have weights, representing the quality of the transition. A DJ
could not only save a transition, but also rate it out of 5 based on how smooth or 
energising it was.

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
