# Joint retiming search with a movable owned-C wire (evidence only)

`cwire_joint.py` extends the earlier joint frame-retiming model: every scalar contact that touches C becomes a variable, and each centre block's C wire gets its own chain. Pricing is the same as in `PROOF.md`. L roles may only climb, and C moves along nested frames in either direction. A move is accepted only if the paid moment falls in both orientations at both t = 0.997 and t = 0.9999. The script reproduces #4470's local paid profile `{1:2237,2:388,3:494,4:147,5:36,8:8}` in both orientations before it searches.

Units are maximal groups of variable contacts that share a frame consecutively along an L role. Two unit models were run, each for 45 minutes on one process.

| Unit model | Units | Level 1 | Level 2 (adjacent pairs) | Level 3 (connected triples) | Annealing steps | Model improvements |
|---|---:|---:|---:|---:|---:|---:|
| C contacts glued into units | 1,012 | 1,012 | 2,871 | 91,223 | ≈1.6 M | 0 |
| every C contact its own unit (`--c-single`) | 1,210 | 1,210 | 3,320 | 103,315 | ≈1.9 M | 0 |

The best annealing state never improved on the baseline (best gain +0.0000). With no model improvement, no exact literal replay was needed. The search is not exhaustive beyond triples, and it does not move helper entrances or exits.
