# Sharp COPY cost 71 on the remaining A8 simplex P112 frame orbit

The fixed nine-normal A8 simplex decoder has minimum separate COPY cost **71**
on each of the **1,080 one-pair frame punctures**, for arbitrary complex row
shifts. An exact witness with all nine terms active attains the bound. Thus
this family cannot beat the standard P112 COPY cost 64.

This resolves the other-frame question in
[commdata2338's PR1304](https://github.com/CrocSwap/integer-mult-bounds/pull/1304).
That predecessor covers 945 matching frames. A complete census here partitions
all 2,025 orthogonal E8 eight-frames into precisely those 945 frames and the
1,080 frames treated here. The latter consist of one pair root and a Fano
plane on the other seven coordinates. No theorem from a pending PR is assumed
to establish the new orbit's bound.

This is a scoped proof with exhaustive finite lemmas, **not a new supplier or
κ result**. It leaves the selected record and frozen sources unchanged.

## Exact scope and evidence

In the sum-zero subspace of Q^9, use roots `e_a-e_b` and
`1_S-(1/3)1`, for three-element sets S, in lexicographic order within those
two groups. Fix `T_ik=r_ik`; require `D T^t=2G` on all live pairs, with ordinary
transpose. Every permitted D has `D_ik=2r_ik+t_i`, with arbitrary `t_i` in C.
Term costs are binary label-pairing ranks on the actual nonzero supports.

The representative puncture is `[0,85,94,99,105,108,112,113]`. The proof in
[PROOF.md](PROOF.md) reduces all complex shifts to finite binary deficiency
compatibility. The two coordinate-anchor classes give:

| Anchors | Planes per anchor | Partner-space tuples per anchor | Compatible choices per anchor | Maximum deficiency sum |
|---|---:|---:|---:|---:|
| 0, 1 | 43,435 | 2,131 | 52,829 | 10 |
| 2 through 8 | 43,435 | 2,251 | 39,482 | 9 |

The primary replay checks all nine anchors: 390,915 planes, 20,019 distinct
ordered partner-space tuples across anchors, and 382,032 compatible choices.
The resulting cost is at least `81-10=71`. Witness costs are
`(0,8,9,9,9,9,9,9,9)` and, with all terms active,
`(1,8,8,9,9,9,9,9,9)`. Both all-pairs identities are checked exactly.

The second implementation derives labels from the rational Gram matrix,
uses nullspaces and Cartesian products instead of the primary bitmask search,
and checks two anchors with explicit puncture-preserving permutations covering
all nine. It also re-enumerates all frames and constructs the new orbit from
36 pairs and 30 Fano planes, separately from the primary coordinate-orbit BFS.

Both implementations are adapted from PR1304, with exact original file pins
in [SOURCES.json](SOURCES.json) and attribution in their headers. Every finite
premise for the changed puncture is recomputed. This is reuse of credited
methods; no independent peer review is claimed.

## Reproduce

From the repository root, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/a8-one-pair-frame-floor
```

The registered replay runs the primary checker, second checker and package
failure tests. Individual checks also work with Python 3.12 or later:

```sh
python3 -I -B research/a8-one-pair-frame-floor/verify.py
python3 -I -B research/a8-one-pair-frame-floor/independent.py
python3 -I -B research/a8-one-pair-frame-floor/test_package.py
```

Expected mathematical markers:

```text
PASS_A8_ONE_PAIR_FRAME_FLOOR frames=1080 anchors=9 planes=390915 configurations=20019 compatible_leaves=382032 cost=71 controls=10
PASS_A8_ONE_PAIR_SECOND_CHECK anchors=2 transported=9 planes=86870 compatible_leaves=92311 cost=71
```

Default replay is read-only and compares the entire deterministic certificate.
`verify.py --write` explicitly regenerates it. Ten semantic controls cover
identity, support costs, labels, puncture legality, compatibility, complex
shifts and omitted/misidentified frame coverage. Package tests exercise altered,
missing and malformed receipts and optimized relocated replay.

## Limits and credit

Only this fixed nine-normal, all-pairs, separately charged family is covered.
Other normals, arbitrary two-factor or masked decoders, other live-set sizes
and shared-copy pricing are outside the result. The COPY power comparison in
the proof fixes the width, normalization and multiplicity; it is not a complete
supplier invoice. Physical gathering, frame legality, restoration, hosting,
precision/tape, all-size/compiler, common-label/mutable-source, analytic and
bit H1–H5 obligations are not checked. No selected cold replay, Lean proof,
hosted-CI success, human review or maintainer acceptance is claimed.

Predecessor credit:

- commdata2338, PR1304: matching-frame floor, both adapted implementations,
  and the explicit other-frame question.
- Philipp / mightyOil, PR1248: the deficiency-space method on P120.
- joaqcoo, PR1224: the one-sided nine-term normal form and A8 family.
- DreamingOfClouds, PR717/595/446: decoder and separate-copy label model;
  Joel Pulikkan / GamingPuzzled, PR620: the coordinate COPY64 construction;
  themilkman216, PR968, and woklerx, PR1077: surrounding all-pairs bounds.

Base main: `ebedc0895eb4c06725af020bc1af165722b0a3ce`. The task, selector nonce,
exact predecessor heads and overlap boundaries are in [TASK.json](TASK.json).
The claim is in [discussion 1241](https://github.com/CrocSwap/integer-mult-bounds/discussions/1241#discussioncomment-18914233).

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in
the mathematics, both adaptations, verification and writing. Apache-2.0.

## Open next questions

- **A different specified nine-normal family.** Can an A7+A1 or A2+E6 family
  from PR1224 achieve COPY cost below 64 on a named P112 puncture? First derive
  its exact kernel-shift classes and column-label ranks, then a favorable
  finite compatibility bound. The fixed simplex normals are essential here;
  neither the deficiency table nor the frame symmetry automatically transfers.
- **Shared-copy accounting.** Can a concrete physical implementation share
  copied information across these nine terms at a net saving? First write its
  entry/exit contract and full recursive bill. This theorem assumes separate
  term charges; a support overlap alone is not a paid implementation.
