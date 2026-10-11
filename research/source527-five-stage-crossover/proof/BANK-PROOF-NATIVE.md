# Independent stage-private banks for the pinned source527 construction

The input is PR210 head 298f7c112889f799e8e2040099fbc325d0ccd0f6, `research/five-stage-source527-banks`. This note adds an independently generated, exactly checked allocation and a conservative selector bill. It preserves the public construction's conditional analytic/compiler interfaces and does not claim a new unconditional multiplication theorem.

## Actual occurrence inventory

A fresh preparation of the pinned word supplies 16,587 arbitrary dirty roles and 527 source-owned roles. Source-owned roles already contain correlated original input data and are excluded from the dirty-bank inventory. The independent bank occurrences are exactly 2,279: 2,200 entrance frames of dimension 20, 48 of dimension 13, 18 of dimension 12, and 13 of dimension 18. Thus their residual families have dimensions 4, 11, 12, and 6. The remaining 14,308 arbitrary dirty roles require dimension 24. Every role is taken from the actual prepared word, not inferred from a histogram.

## Literal allocation

There are 60 physical replicas and five separate stage-private bank collections. For each stage, the family packing is:

| Pattern in a 120-coordinate bank | Banks per stage |
|---|---:|
| eight rank-11 families and eight rank-4 families | 360 |
| thirty rank-4 families | 4,304 |
| twenty rank-6 families | 39 |
| ten rank-12 families | 108 |
| five rank-24 families | 171,696 |

These 176,507 banks per stage are genuine banks: every coordinate lies in exactly one assigned family. There are 882,535 banks across the five stages. The 422,400 data families, together with those banks, give literal physical stock 1,304,935. All 4,976,100 role/replica/stage assignments are enumerated by each native replay. The primary checker enumerates bank slots; the independent checker reconstructs the same allocation role by role and rejects overlap, duplication, and omission.

For a bank decomposition into mutually orthogonal idempotent projectors P_j with sum I, the weighted swap on a bank pair is D(P)=I_pair tensor (I-P)+J_pair tensor P. If P Q=Q P=0, direct multiplication gives D(P)D(Q)=D(P+Q). Consequently the family swaps compose to the full bank swap. This identity allows arbitrary initial bank values. Each stage uses a separate collection, so no across-stage synchronization assumption is needed.

## Actual charts and routing

The 231 distinct actual entrance frames are represented by rational charts computed from the actual frame annihilators. With G=9I-J, each residual row is constructed as 15a-sum(a) times the all-ones row. The checkers test its G-orthogonality to the actual entrance frame, both chart inverse identities, and the elementary factor program. The chart denominators and numerators are below 2^80. All 240 bank address columns are propagated through each of 25 explicit routing templates (one for each stage and packing pattern). Each template contains its 120-coordinate permutation and invertible scalar block. Outside-window scaled address columns distinguish roles sharing a bank; the inverse returns arbitrary correlated dirt.

## Full paid selector invoice

Our independent chart factorization has at most 310 elementary factors. This is more conservative than the public chart convention's 200. We charge the native factorization actually checked here:

    2 * 5 * 60 * ((1304935 - 1) + 16587 * 120 * (310 + 239))
      = 656433896400 < 2^40.

This counts both directions, all five stages, all 60 physical replicas, full-stock selection, all dirty-role chart factors, and all 239 routing factors. No unpaid common-bank or cross-stage lookup is used.

The recurrence uses five-stage normalization. Dividing literal stock 1,304,935 by five gives normalized stock 260,987; the public moment normalizer is 12. The number 12 is not the number of physical replicas. Stock normalization is an analytic recurrence convention and is never presented here as removal of physical storage.

## Reproduction and exact scope

`stage-private527-banks.cpp` regenerates `NATIVE-STAGE-PRIVATE527-BANKS.json` from the fresh actual prepared input. `check-stage-private527-banks.cpp` independently checks that witness and generates `INDEPENDENT-STAGE-PRIVATE527-BANKS.json`. Both compile with C++17 and the included exact rational/frame algebra; no floating-point comparisons are used. The independent replay contains three hostile controls: overlapping allocation, duplicated occurrence, and omitted occurrence. All are rejected.

This proves a sufficient literal bank allocation and its charged finite selector budget for the specified word. Global cover/compiler compatibility, common-ancestor chart interfaces, the analytic recurrence bridge, row recovery, and prime/routing assumptions remain the inherited public conditional interfaces. Scalar correctness and the physical five-stage word are checked separately by the source527 physical/scalar audits.