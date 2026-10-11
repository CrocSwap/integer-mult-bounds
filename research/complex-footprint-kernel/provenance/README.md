Development scripts that found the frozen selections (`../data/selections/*.json`). They are NOT run by
`verify.py`; the selections are verified by the package, not by the search. They need numpy (and scipy for `hostmodel.py`) and
`CXG_BASE` = the output directory of `python -B research/idle-axis-hosting/verify.py $CXG_BASE`, `CXG_REPO` = this repository.
- `kern*.py`: shared-donor kernel classes (rank-1 entrances; simulated annealing over the helper → class partition).
- `gauge*.py`: entrance gauges (per-target nesting, per-centre chains, greedy with refill).
- `iso1.py`: with entrances restricted to the bit-style criterion (orthonormal basis, 1 ∉ E) the kernel potential and the number of
  gauge-eligible helpers are 0.
- `hostmodel.py`, `kcap.py`: the fast hosted-b model used to rank candidates (the package's certified numbers come from `assemble_gk.py`; the model's bank tiling predates the banked spectators and reads about 0.05 % high).
