# H6 canonical blocks and compensation spectrum

This scoped independent audit preserves the H6 proposal and PR606 predecessor sources. `audit.py` replays PR606's exact moment certificate, adds modular feature-rank witnesses and representative exact operator actions, and cross-checks its spectral trace square against the independent exhaustive pairing receipt in `../walsh/results.json`. Substantial AI assistance: Codex.

Run from the repository root, after the Walsh audit:

```sh
python3 -B research/h6-independent-audit/spectral/audit.py
```

## Correction to the frozen H6 block statement

The 28,800 canonical root × root ports are **120 antipodal a-lines × 240 signed b-roots**. The chosen a representative has its first nonzero coordinate positive, with the simultaneous antipodal sign absorbed into b. A common permutation of b columns gives the literal product order. For every a-line there are 63 orthogonal a-lines, 56 with absolute pairing 1, and one diagonal. Hence there are **120 × 119 = 14,280 ordered off-diagonal 240 × 240 blocks**, plus 120 diagonal blocks. There are 7,140 unordered off-diagonal block pairs.

The frozen output's `126 + 112 = 238` neighbour count belongs to 240 signed a-roots. Combining that count with 120 a-lines doubles the off-diagonal block count. In the actual canonical orientation the aggregate signed counts are s = -1: 2,240, s = 0: 7,560, s = +1: 4,480, and s = 2: 120. Counts of positive versus negative neighbours need not be constant per chosen a-line; only the absolute counts are invariant.

The polynomial identity remains correct. Write S_a for the 120 × 120 Gram matrix of canonical a representatives and S_b for the 240 × 240 Gram matrix of signed b-roots, all in ordinary E8 coordinates (the saved coordinates are doubled). Then, using entrywise powers,

```
48 K = S_a^3 ⊗ J + 3 S_a^2 ⊗ S_b
     + 3 S_a ⊗ S_b^2 + J ⊗ S_b^3
     - 4 S_a ⊗ J - 4 J ⊗ S_b.
```

The signed 240 × 240 Gram has Hadamard-power ranks 8, 36 and 120; exact monomial feature witnesses over F101 confirm the corresponding rational ranks because each has that many columns and a nonzero full-rank minor modulo 101. The formula also holds on the larger signed product, but that product has 57,600 rows and includes both simultaneous antipodal orientations; it must be restricted to the canonical product before using the 28,800-port invoice.

For I − K the off-diagonal block is **−f(s + S_b)** for s in {0, ±1}; the diagonal block is I_240 − f(2 + S_b), where f(t) = (t³ − 4t)/48 entrywise. Thus there are three off-diagonal block formulae and one diagonal formula. I − K is a sum of the identity Kronecker product and the six polynomial products. Calling it “not a Kronecker sum” is valid only in the conventional restricted sense A ⊗ I + I ⊗ B; it does not rule out this short sum of products or establish a cheap banked arithmetic schedule.

## Exact real compensation rank survives

The PR606 spectrum is retained:

| Eigenvalue of K | Multiplicity |
| --- | ---: |
| 39 | 224 |
| 45 | 560 |
| each root of λ² + 186λ − 6075 | 16 each |
| 0 | 30,144 |

The pure harmonic cubic dimensions are 2 × (120 − 8) = 224, the mixed linear/traceless quadratic dimensions are 2 × 8 × (36 − 1) = 560, and the radial linear sector has dimension 2 × 2 × 8 = 32. Exact full-rank F101 feature witnesses give pure cubics dimension 120 on the norm-four shell, root quadratics dimension 36 and root linears dimension 8. On root-pair ports, reversing b distinguishes the two mixed parities; their tensor feature ranks are 8 × 36 each. Single-block ports distinguish both pure sectors. These observations prove that all 816 cubic feature columns are independent over Q, hence also over R.

PR606's moment argument uses both full antipodal E8 shells. Its enumeration stores canonical representatives: the even moments are exactly half the full-shell sums, and odd total-degree feature products are not used. Coordinate permutations and even coordinate sign changes establish the degree ≤ 6 moment tensor from the six checked even patterns; canonical representatives need not themselves be literally closed under these signed actions. This is the precise symmetry premise for the sector calculation.

The radial action matrix is [[9, -240], [-18, -195]], with trace −186 and determinant −6075. Its characteristic polynomial is −5888 at 1. The two other nonzero eigenvalues are 39 and 45, so **1 is absent from K's spectrum**, and **rank_R(I − K) = 30,960**. The trace is 30,960. The trace square is 2,222,640, independently recovered from all 958,521,600 ordered pairings via Σ_t count(t)(t³−4t)²/48². Representative exact integer operator actions check both harmonic sectors and the radial matrix in both coordinate blocks. These diagnostic actions complement the moment proof; they are not an exhaustive dense eigendecomposition.

The binary support matrix B = (t mod 2) has rank 16 over F2. That statement concerns a different field and a different matrix from the real weighted compensation operator. Even a short Kronecker description or a rank-16 support description therefore does not contradict the full real rank. Full real rank forces at least 30,960 scalar rank-one rectangle terms in that representation model. It **does not** force 30,960 physical reusable helpers and supplies no universal lower bound on a reusable arithmetic DAG.

## Open next questions

Can the corrected 120 × 240 product support a cheaper banked schedule? First step: exhibit one concrete factor/block operation with actual visited frames, restored-wire semantics and copy incidence, then price it in the existing invoice. The short polynomial expression and rank statements alone do not resolve those physical obligations. This audit changes no selected frontier and makes no new κ claim.
