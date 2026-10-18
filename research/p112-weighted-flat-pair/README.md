# P112 `4,5^2,6^8` excluded by a weighted flat-pair bound

Nick Petalas. Apache-2.0.

Eleven independent P112 pieces with code-intersection dimension at least seven
cannot have weight bounds `4,5^2,6^8`, over any characteristic-zero field.
This removes one actual TWOSIDE `(7,4)` profile from DreamingOfClouds's
[PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154), answering
the adjacent-profile handoff in [PR3176](https://github.com/CrocSwap/integer-mult-bounds/pull/3176).
[PROOF.md](PROOF.md) states the hypotheses and complete implication.

```
Eight weight-six endpoints allow 160 support incidences.
Mixed root/D7 edges require at least 162.
Ordinary root-A7 branch requires at least 168.
Exceptional root-A7 branch:
  arbitrary deletions give only 158, a losing control;
  retain two actual five-flats and the orthogonal frame;
  weighted flat-pair bound gives at least 162.
Contradiction margin at least two.
```

The new finite lemma covers all 2,025 orthogonal frames and all 3,309,747 binary
five-flats. Seven frame orbits and 3,248 high-cost flat masks suffice for the
weighted pair check. A separate generator reconstructs those same masks from
5,124 root-generated spaces and checks every frame without orbit reduction.
The mixed check covers all 9,737 six-cliques, including 2,016 independent cases.
The two programs share the retained geometry and the primary census's proved
full120 five-flat capacity twelve. They are not independent human or proof-kernel
review. [RESULT.json](RESULT.json) records exact counts, witnesses and hashes.

This is one scoped mathematical exclusion. The full `(7,4)` cell, C5,
`C(P112)>=64`, supplier admission and an improved kappa remain open. The selected
conditional kappa is unchanged at `0.001672660197076918`. The standard
Weyl-chamber theorem and original decoder reduction are explicit dependencies.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-weighted-flat-pair-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" python3.12 -B scripts/research_package.py \
  --package research/p112-weighted-flat-pair
```

The three registered commands run sequentially with 120-second limits.
Expected final lines include `PASS_WEIGHTED_FLAT_PAIR`,
`PASS_INDEPENDENT_WEIGHTED_PAIR` and `Ran 16 tests ... OK`.
The behavioral controls run with optimization enabled, so mathematical guards
must not rely on assertions. [CHECKS.json](CHECKS.json) records actual local
checks and limits.

`verify.py --output NEW_ABSOLUTE_PATH` writes a fresh external receipt and
refuses overwrite. Without that argument it compares fresh evidence with the
committed receipt. It never regenerates evidence in the checkout. Git-free
direct replay requires this package and the sole declared input
`research/one-sided-six-multisets/data/data.txt` at the same relative paths.
Generic metadata checking additionally requires the pinned Git provenance.

## Sources and scope

Base main is `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
The concrete handoff was taken before the generic task picker.
[TASK.json](TASK.json) records the changed scope from proof-assistant work to
an exact characteristic-zero lemma. No Lean, Docker or full supplier replay
was run. Physical ownership, restoration, precision and a consumer are outside
this nonexistence proof, not declared free.

DreamingOfClouds's PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`
supplies TWOSIDE, original filters and the C5 handoff. Nick Petalas's PR3176
at `1111a074414c4d2be8b4e230133d873432780814` supplies the retained
support-72 alphabet, mixed graph, root-star and geometry routines, following
PR3164/3175 and the retained E8/P112 decoder lineage including DreamingOfClouds
and joaqcoo's model. The new contributions are the six-clique application,
exceptional A7 weighted-flat-pair lemma, separate flat enumeration and this
explicit eleven-piece exclusion.

[SOURCES.json](SOURCES.json) binds exact heads, original paths, Git blobs and
SHA256 hashes for eight byte-identical retained files. Predecessor notices and
licenses remain in `vendor/`; no frozen predecessor or selected input changed.
Development and local checks used substantial automated assistance.
[ENGINEERING.md](ENGINEERING.md) records implementation bounds and diagnostics.

## Open next questions

Does another actual remaining TWOSIDE profile meet the precise quotient,
support and edge-alphabet hypotheses of this weighted lemma? First pin the
original profile and derive its full budget. This result alone is not a reason
to extend a deletion census or launch a supplier search. The blocker is the
next profile's applicability, not another seed. Structured relevance and the
first step are in [TASK.json](TASK.json).
