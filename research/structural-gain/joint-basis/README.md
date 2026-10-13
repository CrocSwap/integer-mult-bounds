# Joint kernel, donor and gauge bases

This pass found a new exact prefix presentation and tested several routes
toward a larger structural improvement. The admitted composition reaches
**κ = 0.001600682403612293**, a modest improvement. It does not deliver a
gain above one percent. The larger searches below are retained with
their precise boundaries rather than presented as universal obstructions.

The baseline is PR569, commit
`f1db606a1416359229f944946667338305208064`. Everything in
`research/larger-gain` was used read-only. New search scripts and the 57-gate
prefix presentation were prepared with OpenAI Codex assistance; Apache-2.0.
The exact gauge/kernel rewriter is inherited from the pinned PR564 package,
whose `gk_word.py` credits DreamingOfClouds and Claude Opus 5.5. The response,
frame-chain and forward-closure routines imported from PR569 retain their
original source notices and hashes.

## Positive literal construction

The experiment removes all 69 current static-kernel prefix gates and unlocks
their 44 pivot entrances together. The other 172 entrances remain exact
zero-response columns. It recomputes every dirty-response column on that
literal word, enumerates compatible frame classes, and chooses independent
donor bases and their dependent pivots jointly.

The selected presentation uses 57 prefix gates, 32 rank-two pivots and eight
rank-one pivots. On the PR569 width-seven word its profile and residual widths
are:

```
H = {1:2340, 2:576, 3:344, 4:192, 5:56, 6:56, 8:8}
widths = {9:292, 8:124, 7:32, 5:48, 4:8}
```

Relative to that supplier the change is `−12H1 −16H2 +16H3`, with four fewer
rank-one entrances. All selected response identities are checked over exact
rationals; all coefficients are dyadic; the whole paid frame chain is
recomputed after composition. The literal word and recipe are retained in
[`prefix-optimal-disjoint`](prefix-optimal-disjoint/CONSTRUCTION.json).

The independent integration combines this prefix with PR568's extra
multi-cut target-donor kernels. That adds `12H1 +4H2 −8H3` and restores the
exact PR569 width inventory. The resulting provider is:

```
H = {1:2352, 2:580, 3:336, 4:192, 5:56, 6:56, 8:8}
widths = {9:288, 8:128, 7:32, 5:48, 4:8}
```

Thus its improvement against the original width-seven provider is
`−12H2 +8H3`, at identical rank mass and width inventory. Native scalar,
wrapper, full phase, physical owner, invoice and exact recurrence admission
belong to the independent
[`frontier-composition`](../frontier-composition/combined-prefix-word/CONSTRUCTION.json)
work, with the final
[`ASSEMBLY.json`](../frontier-composition/global-replay/ASSEMBLY.json).
Search receipts in this directory do not replace those checks. The resulting
κ remains conditional on the inherited compiler/realization and analytic
assumptions.

## Executed structural screens

| Experiment | Exact finite scope and result |
| --- | --- |
| Fixed prefix bases | All 2,245 nonzero subspaces of actual first frames; 1,357 classes contain at least two eligible helpers. Exact rational dependencies give 112 rank-one and 80 rank-two components. There are no rank-three/four dependent components within these classes. |
| Raised prefix bases | All 2,893 nonzero subspaces of maximal legal future caps; 1,997 classes have at least two eligible helpers. Includes the 40 helpers whose first frame can rise from rank three to four. Exact forward closures give 130 rank-one and 100 rank-two components, and no rank-three/four component. The disjoint-component optimizer chooses the same 57-gate presentation. |
| Remaining untouched B helpers | All eight remaining partners after PR568+569, with every compatible donor epoch, including output targets. Eight rank-two span queries over 3,715 donor/time states find no relation. |
| Jointly unlocked suffixes | Remove all eight existing cold kernels by exact scalar subsequence alignment. Test all 560 eligible rank-two planes over 3,663 donor/time states. Find 16 literal exact circuits, two pivot orientations for each of eight pairs. |
| Shared suffix composition | Test all 256 choices of the retained rank-one versus new rank-two circuit for the eight original pivots. All entering scalar responses vanish in the 192 frame-compatible compositions. The other 64 violate the prescribed inserted-frame chains. At the stated capacity dual the best admitted chain keeps every rank-one circuit. |
| Shared entrance gauges | Intersect each cold helper's first-frame cap with all response-supported output caps and serving center frames. Every one of the 288 cold helpers has zero common cap; no one-class shared gauge is available. |
| Joint kernel/gauge bases | Unlock all 44 static pivots; solve response dependencies only on rows forbidden for the proposed gauge frame. Of 2,789 eligible helper subspaces, 2,763 admit no compatible output coordinate. The remaining 26 projected response matrices have no dependent eligible columns, so no joint kernel/gauge presentation is produced. |

The component selection MILP uses floating prices for discovery. Its chosen
word is checked exactly afterwards. Its optimality status applies only to
the enumerated **disjoint component choices** and the stated linear
objective. With raised frames, shared changes are repriced in the literal
word; independent component prices are not an exact global objective.

The 64 rejected suffix combinations could be reconsidered with larger
inserted-gate frames. The current experiment does not do that. Other exclusions
include alternate response bases within each matroid component, overlapping
or nested component classes, mixed gauge subsets, changed target/output
bases, changed center cuts and different packet architectures. In particular,
the absence of rank-three dependencies here is not a bound on every scalar
realization of the geometry.

## Reproduction

The combined words are retained by `frontier-composition`. Obtain the pinned
PR564 package and its freshly replayed PR558 promoted word, then run:

```sh
python3 -B research/structural-gain/joint-basis/reproduce.py \
  --source-package /path/to/complex-allcold \
  --promoted-word /path/to/pr564-replay/baseline558/reconstruction/promoted/FULL-WORD.json.gz \
  --optimizer-python /path/to/python-with-scipy \
  --work /tmp/new-joint-basis-replay
```

Only the two disjoint-component selection steps require NumPy/SciPy; the
remaining scripts use the Python standard library. This driver installs
nothing. It checks PR564's complete source inventory against manifest SHA256
`dd602912d0e60c9bb2befba446629ae531ea42a9d4fecda922f98aac40762c41`, the actual
promoted-word content against its immutable recipe, and every imported
research helper and input word against explicit SHA256 pins. It runs all ten
experiments afresh, compares every retained literal word by decompressed
content hash, and compares exact search counts and records.

`RESULT.json`, `RECEIPT.json` and per-stage logs bind commands, code hashes,
input hashes and outputs. The retained `REPLAY.json` records the completed
end-to-end research replay. Earlier exploratory receipts can contain the
hash of their then-current script revision; the end-to-end replay establishes
that the final scripts reproduce the same literal words and exact results.
Timing fields, paths and floating solver diagnostics are not mathematical
certificates.

Each script also has an explicit-path command-line interface. The principal
construction steps are `search_prefix_bases.py` followed by
`optimize_prefix_components.py`; adding `--raise-frames` to the first enables
full coupled future closures. `search_multicut.py` searches donor/time
coordinates, and `compose_multicut_choices.py` prices their shared chains.
`search_shared_gauges.py` and `search_joint_gauge_bases.py` implement the two
gauge tests described above.
