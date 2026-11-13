# Independent Gaussian ring-matching review

The proposed construction passes an independent mathematical and executable
review. It gives an exact-sum bijection of Gaussian pairs with `F^2=swap`,
Euclidean pair error at most 1 from the ideal C pair, and bilateral radial
slack exactly `sqrt(19)-sqrt(13)`. Its inverse is `swap F`; inverse by
componentwise conjugation cannot be retained with exact sum and this square
identity.

The sharp lower bound is certified here for the class of global
quarter-turn-equivariant unit-neighbor half-grid matchings. The reduction
from arbitrary Gaussian rounding maps is outside this review and is being
reviewed independently elsewhere. The implementation is independent of the
parent and worker-B checkers: neither was read or imported.

Run from any working directory:

```sh
python -B /workspace/scratch/92c9920affc2/worker-a/research/gaussian-ring-matching-review/check.py
python -O -B /workspace/scratch/92c9920affc2/worker-a/research/gaussian-ring-matching-review/check.py
```

The checker uses only the Python standard library and explicit exceptions.
`--write` refreshes the JSON receipt; ordinary runs only print it. The
construction and all-size proof are in `matching.py` and `REVIEW.md`.
`RESULT.json` records the exact finite counts and source hashes.
Before importing the project model, the checker selects a fresh, initially
absent bytecode-cache prefix and disables bytecode writes. It therefore
replays the current source rather than accepting a pre-existing local cache.

This is an isolated AI mathematical review of the formula provided by the
parent research task on 2026-11-13. It has no physical-machine, caller,
recursive-cost, selected application, or kappa consequence by itself. It
claims no priority over earlier rounding literature/packages. No remote
publication or repository mutation was performed by this reviewer.
