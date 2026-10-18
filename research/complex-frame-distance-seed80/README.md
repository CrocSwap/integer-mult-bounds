# Independent complex canonical-frame rank verification

The frozen PR1042 R480 word passes a separate check of all **1,004 canonical
frames, 2,896 directed child edges and 224 endpoint adapter ranks**. Its used
edges are nested, and their retained recursive ranks equal the dimension
differences. The checker reconstructs literal symplectic P/D/C actions and
compares them with an explicit Lagrangian/subspace-intersection calculation.
It imports no producer compiler or lowering routine.

The source-bound identity is

```
rank B(F_V F_U^-1) = dim(U) + dim(V) - 2 dim(U intersect V).
```

[PROOF.md](PROOF.md) derives the canonical preimage Lagrangians and proves the
identity for arbitrary subspaces in any finite dimension. The standard rank
formula is not claimed as new mathematics. The new evidence is the independent
check of the pinned implementation obligation, its actual source inventory and
the complete nonnested finite boundary census.

All 374 subspaces of F2^5 and all **139,876 ordered pairs** are checked. The
absolute dimension difference is insufficient for 128,712 of these pairs;
this is the expected nonnested boundary, not a defect in the selected nested
construction. The first example is `U=<1>, V=<2>`, with true rank 2 versus 0.

| Transition B-rank | Ordered pairs |
|---|---:|
| 0 | 374 |
| 1 | 4,154 |
| 2 | 19,840 |
| 3 | 44,950 |
| 4 | 49,724 |
| 5 | 20,834 |

## Source and exact coverage

Base: `ba82555c64e1879e4b7decce28186f208fcb8262`. PR1042 is the historical
checkpoint frozen at that base; main subsequently selected PR1094. This package
does not update either selection or claim its findings describe a new frontier.
The archive members are `slots/local/CANONICAL-WORD.json.gz`,
`slots/local/CLIFFORD-RECIPES.json` and `slots/local/CLIFFORD-REVIEW.json` in
`research/community-frontier1042-audit/selected-replay.tar.gz`. The mandatory
source inventory also pins the exact compiler convention, the rank obligation
in `phases_full.py`, and the SLOT-PINS receipt. The canonical word digest is
`4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`.

The edge inventory is reconstructed from the canonical word, including both
directions of every centre-to-zero transition, then compared exactly with the
recipe inventory. Each source and target port has exactly one endpoint adapter
record and its symplectic transition rank is independently checked to be zero.
Stored rank and histogram fields must agree. Missing or duplicate records fail.
All canonical frames are checked for symplecticity and for the exact preimage
Lagrangian, not just the dimension of that preimage.

The finite enumeration uses complete vector-set closure under adjoining every
ambient vector. It includes all dimensions, both transition directions and
nonnested pairs. The Gaussian-binomial dimension counts bind complete coverage.
Seed80 selects the independent-verification track; no random sample is used.

## Reproduce

```
python -I -O -B research/complex-frame-distance-seed80/verify.py
python -I -O -B research/complex-frame-distance-seed80/test_package.py
```

Expected first lines:

```
PASS_COMPLEX_FRAME_DISTANCE frames=1004 edges=2896 pairs=139876 controls=15 no_phase_claim
PASS_COMPLEX_FRAME_DISTANCE_PACKAGE relocation=1 corruptions=5
```

`verify.py --write` explicitly regenerates RESULT.json; the default replay is
read-only and requires typed canonical equality of the full result. Duplicate
JSON keys, nonfinite values, missing mandatory pins and source drift fail closed.
All checks remain active under `-O`. The implementation uses Python's standard
library only. A minimal relocated run and five packaging corruptions complement
the 15 mathematical rejection controls.

Those controls cover wrong child ranks, missing/duplicate edges, wrong histogram,
missing/wrong endpoint adapters, three nonnested dimension-shortcut failures,
three corrupted generator actions and three omitted diagonal-conjugation cases.
The omitted-diagonal cases remain symplectic but have the wrong preimage,
showing why a generic symplecticity check is insufficient. One additional
scope control changes a global phase while preserving the rank result.

## Scope, overlap and credit

This verifies a recursive-rank obligation only. A phase mutation is intentionally
invisible after forgetting phase, so neither the stored Clifford recipes nor
the complete operators are freshly verified here. There is no native compiler,
phase, provider, precision/tape, outer invoice or all-size multiplication proof.
No kappa, circuit, frame schedule, scalar word or cost profile changes.

The source Clifford convention and phase-aware compiler are icekylinx's
PR425/433 lineage, with earlier community construction credits retained.
LeaverSAT/LeaverSAT2 and icekylinx supply the R480 cells; PR1018 supplies the
seven-slot word and Jeremy Kothe's PR1042 is the frozen selected assembly.
PR702/712 check cold-wrapper phases and exact operator identities, a stronger
kind of equality on different objects. PR911 (ToikY) exhaustively verifies
binary residual/phase interfaces; its Gram and nonalternating conditions belong
to that different model. PR367 (amanforindia) accelerates historical rational
frame algebra. Earlier Lagrangian frame-layout bounds such as PR192/212 are
background, not newly discovered geometry. Round25's cell relabeling atlas and
round23's positive circuit minimum are separate finite questions.

Contributor @woklerx with substantial OpenAI Codex assistance. Apache-2.0;
see NOTICE.md. Algorithmic independence is not independent human review.
