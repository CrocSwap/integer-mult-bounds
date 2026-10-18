# A weighted A6 cover excludes P112 `3,4,6^8`

Nick Petalas. Apache-2.0.

Ten independent P112 pieces with code-intersection dimension at least six
cannot have weight bounds `3,4,6^8`, over any characteristic-zero field.
This excludes one actual TWOSIDE `(6,4)` profile in DreamingOfClouds's
[PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154).
[PROOF.md](PROOF.md) gives the full statement and implication.

```
Seven weight-six endpoints allow 140 support incidences.
Mixed root/D7 edges require at least 142.
Root-only A6 edges:
  forty arbitrary deletions give only 137, a losing control;
  retaining the frame and six-flat alone still gives only 139;
  retaining the actual four-flat as well gives at least 141.
Contradiction margin at least one.
```

The new weighted lemma retains a binary six-flat and four-flat, with the
rank-three support relaxed to four arbitrary coordinates. The replay covers
all 788,035 six-flats, all 2,025 orthogonal frames, and all relevant four-flats.
Only 63 high-cost six-flat masks and 135 four-flat masks survive the exact
threshold reductions. A separate program enumerates all 3,309,747 four-flats
instead of using that reduction and reconstructs frames by Weyl orbit rather
than orthogonality cliques. The mixed check covers 7,350 five-cliques, including
3,360 rank-six cases. [RESULT.json](RESULT.json) records complete counts,
witnesses and canonical hashes.

This is an author-checked finite mathematical result, not independent human
or proof-kernel review. The programs share root reconstruction and the written
Weyl-chamber dependency. It does not close the whole cell, C5, `C(P112)>=64`,
supplier admission or a new kappa. The selected conditional kappa remains
`0.001672660197076918`.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-a6-weighted-cover-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" python3.12 -B scripts/research_package.py \
  --package research/p112-a6-weighted-cover
```

Four registered commands run sequentially with 120-second limits. Expected
markers are `PASS_A6_WEIGHTED_COVER`, `PASS_INDEPENDENT_A6_MIXED`,
`PASS_INDEPENDENT_A6_WEIGHTED` and `Ran 16 tests ... OK`.
The tests run under optimization, so mathematical guards must remain active
without assertions. [CHECKS.json](CHECKS.json) records local checks and limits.

`verify.py --output NEW_ABSOLUTE_PATH` writes a fresh external receipt and
refuses overwrite. Without that option it compares fresh evidence with the
committed receipt. It does not regenerate files in the checkout. Direct
Git-free replay needs this package and its sole declared input
`research/one-sided-six-multisets/data/data.txt`, at the same relative paths.
Generic provenance validation additionally requires the pinned Git objects.

## Sources and overlap

Base main is `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
The concrete C5 handoff was taken before consulting the generic task card.
[TASK.json](TASK.json) records the changed scope from proof-assistant work
to an exact characteristic-zero lemma and the bounded candidate correction.

DreamingOfClouds/PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`
supplies TWOSIDE and the original filters. Nick Petalas/PR3176 at
`1111a074414c4d2be8b4e230133d873432780814` supplies the byte-identical
support-72 alphabet, rational graph and geometry routines. The retained
lineage includes PR3164/3175, DreamingOfClouds, joaqcoo's model and the
credited E8/P112 decoder sources. Frame traversal is adapted from PR3180;
the weighted A6 lemma and this five-clique application are new.
[SOURCES.json](SOURCES.json) binds exact heads, blobs and SHA256 hashes;
licenses and predecessor notices remain in `vendor/`.

The initial candidate `2,4,6^8` was discarded because PR3162 already excludes
it. For the present `3,4,6^8` profile, the unique weight-certified quotient
basis `3,4,6,6` needs twelve cuts in the two-six-flat cover and leaves no
rank-four nonbasis anchor. The pinned ten-cut and twelve-cut-anchor theorems
do not close it by that route. Live overlap is advisory, not a novelty proof.

No frozen input, shared implementation, research priority or selected result
changed. No Lean, Docker, physical caller or complete supplier replay was run.
[ENGINEERING.md](ENGINEERING.md) records implementation bounds and diagnostics.

## Open next questions

Does another actual remaining profile need this A6 cover lemma or a different
support contract? First pin that profile and prove its quotient dimension,
small-support and edge-alphabet hypotheses. The blocker is applicability,
not another seed. Do not infer a full C5 result or expand the census without
that decision. Structured relevance and a first step are in [TASK.json](TASK.json).
