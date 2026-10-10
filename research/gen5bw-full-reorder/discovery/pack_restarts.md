# Randomized packing restarts

`coll/pack_restarts.py` is `coll/pack.py` with an optional restart loop (`PACK_RESTARTS=N`, `PACK_SEED`, `PACK_NOISE`):
each restart orders the candidate families by their standalone φ gain perturbed multiplicatively by up to `PACK_NOISE`,
runs the same greedy acceptance with the same exact marginal (shared-donor chain) costs, and the order with the lowest
total φ is kept and written in `pack.py`'s formats. On the gen5b word after the descent and squares, 250 restarts
(seed 11, noise 0.3) lower the packing from φ −3,799.13 (1,720 entries, the plain greedy order) to φ −3,860.01
(1,734 entries). Not run by `verify.py`; the frozen `kernel-selection.json` is bound to the fresh word by
`build_selection.py` as before.
