# A five-line counterexample to the independent-deletion relaxation

## Statement

Use the retained P112 configuration. The 120 E8 root lines have doubled integer representatives of squared norm eight. Delete the eight frame lines

```text
2e_0 +/- 2e_1, 2e_2 +/- 2e_3,
2e_4 +/- 2e_5, 2e_6 +/- 2e_7.
```

Choose the sign with first nonzero coordinate positive and sort the remaining 112 representatives lexicographically. Write these representatives as `r_t`. Their binary labels `ell(t)` are their eight integral simple-root coordinates modulo two, with a leading one in bit zero. The exact simple system is in the pinned geometry input and independently transcribed in `reference.py`.

For `V <= F2^9`, let `Lambda(V)={t: ell(t) in V}`. For a nonzero characteristic-zero vector h, let `Off(h)={t: <r_t,h> != 0}`.

For a fixed seven-space V, consider the directions h such that there exists a set `P_h` of at most p live lines with

```text
rank_F2 ell(Off(h) \ (Lambda(V) union P_h)) <= 7.
```

The retained OS-CHARGE2 Lemma N says that at p=4 there are at most two projective directions, even with different `P_h` for different h. This is a predecessor claim checked there; its global upper bound is not replayed here.

At p=5 there can be at least three linearly independent directions. Consequently four cannot be increased to five in that independently deleted statement.

## Literal certificate

A positive integer below 512 denotes a binary functional, applied to a label by the parity of the bitwise intersection. A pair of independent functionals defines a seven-space as their common kernel.

Take V with annihilator rows `(2,65)` and the following directions and second seven-spaces:

| i | h_i | Annihilator of G_i | P_i |
|---|---|---|---|
| 0 | `(0,0,0,0,0,2,-2,0)` | `(3,129)` | `0,1,2,4,7` |
| 1 | `(0,0,0,0,0,2,0,-2)` | `(3,384)` | `0,1,3,5,6` |
| 2 | `(0,0,0,0,0,2,0,2)` | `(3,385)` | `0,2,3,5,6` |

All indices are zero-based live-line indices, not full-root indices. The only indices used in the cuts have these labels:

| t | r_t | ell(t) |
|---|---|---:|
| 0 | `(0,0,0,0,0,2,-2,0)` | 257 |
| 1 | `(0,0,0,0,0,2,0,-2)` | 425 |
| 2 | `(0,0,0,0,0,2,0,2)` | 421 |
| 3 | `(0,0,0,0,0,2,2,0)` | 269 |
| 4 | `(0,0,0,0,2,0,-2,0)` | 385 |
| 5 | `(0,0,0,0,2,0,0,-2)` | 297 |
| 6 | `(0,0,0,0,2,0,0,2)` | 293 |
| 7 | `(0,0,0,0,2,0,2,0)` | 397 |

The checkers reconstruct every live line and verify, for each i,

```text
Off(h_i) \ (Lambda(V) union Lambda(G_i)) = P_i,
|Off(h_i)| = 53,
rank_F2 ell(Off(h_i) \ (Lambda(V) union P_i)) = 7.
```

Thus every displayed h_i qualifies at five deletions. Their columns 5,6,7 form the rational matrix

```text
[2 -2  0]
[2  0 -2]
[2  0  2]
```

whose determinant is 16. They are linearly independent over every characteristic-zero field. Equivalently, their Gram matrix has determinant 256. The support and label identities use only integers and binary arithmetic, so no numerical or finite-characteristic inference supplies this independence.

## Each of the three directions really needs five

For each fixed `V,h_i`, the primary checker tests every binary seven-space G, enumerated by its two-dimensional annihilator. There are

```text
(511*510)/(3*2) = 43,435
```

such annihilators. Exactly one G leaves at most five uncovered live lines, namely the displayed G_i; it leaves exactly five. Lower-dimensional residual spaces are covered as well, since each extends to a seven-space.

A separate implementation does not enumerate G. It reconstructs E8 from the doubled lattice conditions, solves the simple-coordinate system by rational elimination and computes the 37 labels in `Off(h_i) \ Lambda(V)`. It checks every four-element deletion subset. There are `binomial(37,4)=66,045` subsets per direction, and each leaves rank at least eight. Any successful deletion of fewer than four lines could be enlarged to four without increasing rank, so this also excludes every smaller deletion set. The displayed five deletions leave rank seven.

These independent local checks establish exact deletion distance five for all three directions. They are not a new global five-deletion classification.

## Why this is not a common-five-line counterexample

For the displayed completions,

```text
P_0 union P_1 union P_2 = {0,1,2,3,4,5,6,7}.
```

The union has size eight and binary rank four. If a common set P of at most five lines worked for the same triple, each residual support would lie in some seven-space G. The unique-completion check forces that G to be G_i and forces P to contain P_i. It would therefore have to contain all eight lines, contradiction.

This distinguishes separate five-line deletions from one common five-line deletion, and from an actual rank-four small piece. No assertion is made that these directions and covers are the normalized circuit relations of independent physical pieces. In particular this witness does not invalidate FINITE alpha's rank-four cover result or prove any decoder-floor or multiplication claim.
