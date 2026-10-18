# Exclude the final two P112 beta shapes by root-simplex incidence

Nine independent P112 pieces with code intersection dimension at least five
cannot have weights bounded by either `3,4^2,6^6` or `2,5^3,6^5`.
The proof holds over every characteristic-zero field. It excludes the two
remaining `(b,t)=(5,4)` TWOSIDE beta shapes reported by [PR3162](https://github.com/CrocSwap/integer-mult-bounds/pull/3162).

Choose three small pieces. The six others yield an affine root A5 simplex
after quotient normalization. Each of its fifteen edges has at least 53
nonzero coordinates; each live coordinate meets at most nine edges.
Counting outside the small supports gives impossible inequalities
`615 <= 600` and `561 <= 560`. The latter has margin one.

[PROOF.md](PROOF.md) gives the argument and all hypotheses.
[RESULT.json](RESULT.json) records exact checks of all 4,097,782 five/six-flat
kernels, all 7,140 root planes, the chamber facts and a sharp simplex fixture.
The universal incidence bound is proved in prose; the fixture alone would
not establish it. Seventeen behavioral groups include source mutations,
threshold failures and a one-extra-line control that loses the narrow margin.

This new proof stands on its explicit nine-piece hypotheses. Combining it
with PR3162's thirteen earlier exclusions removes the pinned fifteen-shape
residue, inheriting that package's author-checked finite theorem and the
original TWOSIDE filters. It does not settle full C5, other cells,
`C(P112)>=64`, supplier admission or kappa. The selected conditional kappa
remains `0.001672660197076918`.

## Reproduce

Requires Python 3.12 or later and its standard library. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-simplex-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN"
TMPDIR="$RUN" uv run --python 3.12 --no-project python -W error -B \
  research/p112-root-simplex-exclusion/verify.py
TMPDIR="$RUN" uv run --python 3.12 --no-project python -O -W error -B \
  research/p112-root-simplex-exclusion/test_verify.py
TMPDIR="$RUN" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/p112-root-simplex-exclusion
```

An existing `python3.12` executable can replace the `uv run` prefix. The direct
replay needs only this package and its declared data file, with no Git or network.
It compares the reconstructed receipt to the committed one. `--output NEW_PATH`
writes a new external receipt and refuses overwriting. The registered launcher
also validates Git provenance and runs both commands with 120-second bounds.
[SOURCES.json](SOURCES.json) distinguishes the sole live input from historical
provenance. [CHECKS.json](CHECKS.json) records execution and review limits.
[ENGINEERING.md](ENGINEERING.md) records loop bounds and runtime deviations.

## Open next questions

Which remaining beta cell has the same six-piece, one-dimensional quotient?
First pin an actual cell, choose its small pieces and check every edge's
support is below 70. That hypothesis check is required before expanding this
argument; the present result is no universal decoder lower bound.

Can the nine-edge lemma and quotient normalization be kernel-verified?
Start with the integer root inner products. This package includes no Lean
environment or proof-assistant build. Structured questions are in
[TASK.json](TASK.json).

## Credit

Nick Petalas contributed the root-simplex incidence argument, the two new
exclusions and their exact replay. DreamingOfClouds's [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154) supplies TWOSIDE's
reduction and the current handoff. PR3161 and PR3162 supply the preceding
exclusions and root/label reconstruction convention. The retained E8/P112
and decoder contributors keep their credit. Exact heads, paths, Git blobs
and hashes are in SOURCES.json. Predecessor sources are unchanged.

New work is Apache-2.0. Development and internal read-only review used
substantial automated assistance. No independent human or proof-kernel
review is claimed.
