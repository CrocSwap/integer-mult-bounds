# One unsplit call per stage still needs thin rank 8

No new kappa. At block size 2 and three leaves, over F_2, place one unsplit
full call E_j on each stage and exactly two constant thin maps. Every such
word misses the paired-star endpoint when the thin ranks sum to 6 or 7.
The minimum that does meet the endpoint is 8, and it is attained. The
selected frontier stays 781451/250000000.

This is not the two-call census. Each stage contributes the single factor
I + x_j E_j, which the determinant count of
`research/paired-star-three-full-calls/PROOF.md` allows. It is not a
non-T-commuting factor, and it does not change the selected frontier.

## 1. Hypotheses

Keep the paired-star target from `research/coupled31-chronology/PROOF.md`.
The space is a core plus g=3 leaves, each of dimension d=2, over F_2.
Coordinates are ordered core, leaf 0, leaf 1, leaf 2, with two lanes in
each block. On the core and leaf j,

```text
E_j = diag(I, I),    T_j = [[I, I], [I, I]],    x_j = D_j + 1.
```

The unsplit full call is the single factor

```text
(I + x_j E_j)(I + e T_j) = I + x_j E_j + e D_j T_j
```

in F_2[D_0, D_1, D_2, e] / (e^2). There is one such call for each stage, and
no other full call. A thin call is I + e Z with Z constant and entries in
F_2. The target is

```text
(I + e) * product_j (I + x_j E_j).
```

Call order is any permutation of the three stages. The first call is the
rightmost factor. The four gaps are the positions before all calls, between
the calls, and after all calls. Two thin maps may occupy one gap or two
different gaps.

T_j is supported on the core and leaf j, and it preserves lanes: it sends
each core basis vector to the sum of that vector and the same lane of leaf
j, and likewise from the leaf. E_j is the diagonal projector onto those
four coordinates. Off that block both operators are zero. Consequently
I + x_j E_j is diagonal. On the core and on leaf j its diagonal entry is
D_j; elsewhere it is 1. The three pure factors commute, and for every order
their product is the diagonal operator

```text
diag(D_0 D_1 D_2, D_0 D_1 D_2, D_0, D_0, D_1, D_1, D_2, D_2).
```

That is the pure part of the target. The pure endpoint is therefore met by
every order, before any thin map is chosen. The obstruction is in the
coefficient of e.

## 2. The two-gap equation

Write each full call as Q_j + e S_j with Q_j = I + x_j E_j and
S_j = D_j T_j. In a product of terms P + e S, the coefficient of e is the
sum of one S conjugated by the pure factors on its left and right. A thin
map I + e Z in the gap after the first k calls contributes L Z R, where R
is the pure product of those k calls and L is the pure product of the later
calls. Both L and R are diagonal. For a matrix entry this contribution is
the monomial L_ii R_jj times the constant bit Z_ij.

Distinct monomials in D_0, D_1, D_2 are linearly independent, and every
monomial that appears is square-free: each S_j contributes one D_j, and the
pure factors around it belong to the other stages. Thus each matrix entry,
for thin maps in two distinct gaps, is an equation in two bits:

```text
m_g Z_ij + m_h W_ij = defect_ij
```

in F_2[D_0, D_1, D_2]. The two monomials are known from the gap, and the
defect is the target's e coefficient plus the full-call sum. The entry is
impossible, forced, or has a one-bit affine freedom. Entries do not
interact. Two thin maps in the same gap multiply to one thin map, because
(I + e Z)(I + e W) = I + e (Z + W). That case is the one-map equation.

The verifier compares this conjugation with the expanded polynomial word
for every order, with no thin maps and with a probe matrix in every pair of
gaps. The two calculations agree, so the entry equations are the endpoint.

## 3. Which gap pairs survive

There are 6 orders and C(4, 2) = 6 pairs of distinct gaps, 36 systems.
Each system is 64 independent equations. The count is:

| Gap pair, counted from the right | Systems | Result |
|---|---:|---|
| (0, 1), (0, 3), (2, 3) | 18 | no constant solution |
| (0, 2) and (1, 3) | 12 | family A below |
| (1, 2) | 6 | family B below |

A single gap is the same kind of equation with one monomial. All 6 orders
and all 4 gaps fail. Same-gap pairs fail with them.

One obstruction is enough to show the shape. For order (0, 1, 2) and the
outer gaps 0 and 3, the core-to-leaf-1 entry in lane 0 has defect D_1 D_2.
Gap 0 multiplies that row by D_0 D_1 D_2, and gap 3 multiplies that column
by D_1. Neither monomial, nor their sum, is D_1 D_2. The verifier checks
this entry and every other failing entry; the table is not a sample.

## 4. Family A

After a permutation of the three leaves, each of the 12 systems is one of
the following block forms. The diagonal blocks A, B, C, D are arbitrary and
shared by the two maps. Every other block is constant. Here I is the 2-by-2
identity.

Singleton leaf on the first map, and the other two leaves on the second:

```text
Z = [[A, I, 0, 0], [I, B, 0, 0], [0, 0, C, 0], [0, 0, 0, D]]
W = [[A, 0, I, I], [0, B, 0, 0], [I, 0, C, 0], [I, 0, 0, D]]
```

The exchanged form puts the pair of identity blocks on Z and the singleton
on W. A leaf permutation is a simultaneous reordering of block rows and
block columns. It preserves rank, and it preserves these shapes because the
identity block does not depend on the leaf. The verifier checks that every
surviving (0, 2) or (1, 3) system matches one of these shapes exactly.

**Proposition.** In either form, rank(Z) + rank(W) >= 8. Both zero-parameter
matrices have ranks 4 and 4, so 8 is attained.

Proof of the singleton-on-Z form. The images of the leaf 1 and leaf 2
columns of Z lie in those leaves, and the core-plus-leaf-0 columns stay in
that four-dimensional sum. Therefore

```text
rank(Z) = rank([[A, I], [I, B]]) + rank(C) + rank(D).
```

The two leaf 0 columns of the 4-by-4 block are independent because their
core component is I. A core input v is already in that span exactly when
(I + BA) v = 0, so the 4-by-4 block has rank
2 + rank(I + BA). Hence

```text
rank(Z) = 2 + rank(I + BA) + rank(C) + rank(D).
```

For W, the leaf 0 output is B w and no other input meets that leaf, while
the remaining outputs do not depend on w. Thus
rank(W) = rank(B) + rank(R) with

```text
R(v, p, q) = (A v + p + q, v + C p, v + D q).
```

Set v' = v + C p and clear v' from the other outputs by row operations.
The remaining map on (p, q) is

```text
S(p, q) = ((I + AC) p + q, C p + D q).
```

The first component can absorb q, after which the second component covers
im(D) + im(C + D + DAC). So rank(S) = 2 + dim(im D + im M) for that M, and

```text
rank(R) = 4 + dim(im D + im M) >= 4.
```

Adding the two ranks,

```text
rank(Z) + rank(W) = 6 + rank(B) + rank(I + BA) + rank(C) + rank(D) + dim(im D + im M).
```

The last three terms are nonnegative. The 2-by-2 lemma

```text
rank(B) + rank(I + BA) >= 2
```

holds for every pair of 2-by-2 matrices over F_2: B = 0 forces I + BA = I,
and BA = I forces B to be invertible. The sum is therefore at least 8.
Equality holds at A = B = C = D = 0.

The exchanged form is the same calculation with the roles reversed. Leaf 2
splits off W with rank(B) + rank(C) + 2 + rank(I + DA), and the identity
block in the leaf 1 output of the reduced Z map contributes rank at least
2. The same 2-by-2 lemma, applied to D and A, supplies the remaining 2.
The verifier evaluates the lemma on all 256 pairs and evaluates both
16^4-parameter forms directly. Both minima are 8.

The zero-parameter word, order (0, 1, 2), with the first map before every
call and the second map after the second call, multiplies to the target in
the polynomial ring. Adding the same core identity to both maps still
matches. Adding it to only one map, or deleting either map, misses the
target.

## 5. Family B

The six systems with thin maps in the two internal gaps match, after a leaf
permutation, the block form

```text
Z = [[A, I, P,   0], [I, B, 0, H], [Q,   0, C, 0], [0, K, 0, D]]
W = [[A, 0, P+I, I], [0, B, 0, H], [Q+I, 0, C, 0], [I, K, 0, D]]
```

A, B, C, D, H, K, P, Q are arbitrary 2-by-2 matrices. Diagonal blocks and
the leaf-0/leaf-2 blocks are shared. The core/leaf-1 blocks differ by I.
The identity blocks of leaf 0 lie on Z, and those of leaf 2 lie on W.
Every one of the 2^32 choices is a solution of the endpoint equation, and
every solution of these six systems arises from one choice by a leaf
permutation. Rank is unchanged by that permutation.

**Proposition.** Every matrix in this family has rank(Z) + rank(W) >= 8.
The zero parameters have ranks 4 and 4.

This is an exhaustive census of a finite set, not a sample and not a hand
inequality. `search.c` visits every 8-tuple. It skips a branch only when
the six leaf rows already have rank sum at least 8. Those rows do not
contain A or P: the verifier compares them at A = P = 0 and at A = P = 15.
Adding the two core rows cannot lower the rank, so a skipped branch is at
least 8. The visit counter is exactly 2^32. The minimum returned is 8.

Python recomputes the rank sum on two slices of 2^16 parameters each, the
diagonal parameters with the other four zero and the reverse, and checks
the hashes against the C program. Both slices use the same matrix layout.
The zero word, with the maps in the two internal gaps of order (0, 1, 2),
equals the target in the polynomial ring.

## 6. What was not proved

The two statements above are the whole constant F_2, two-map, one-unsplit-
call-per-stage contract at g=3, d=2. They do not say:

- Three or more thin maps are impossible. The two-call witness of total
  rank 6 uses a different full-call shape.
- A thin map whose entries depend on the stage variables is impossible.
- Entries outside F_2, a non-T-commuting stage factor, or a second full
  call inside a stage are impossible. The three-or-more T-commuting
  projector obstruction is the predecessor, and it is not re-proved here.
- The bound lifts to g=13, q=8 or g=31, q=26.
- This is a native caller, a compiler bill, or a change of kappa.
  781451/250000000 stays the selected frontier.

No Lean proof, Docker replay, `make frontier6030-verify`, or
selected-frontier replay was run.

## Credit

The contract, the local form, and the rank floor are from PR #5747 (Ali
Romman), including PR #5673, PR #5631, and PR #5617. The determinant count
that leaves one unsplit call per stage open is PR #6956. The two-call
rank-8 census is PR #6940, and the one-map census is PR #6922. Prepared by
unpaidmoon with substantial Cursor Grok assistance. Independent human
review and a proof-assistant proof are unclaimed. Apache-2.0.
