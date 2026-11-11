# An after-stage-0 gap and the g=13 leaf block

This note answers one placement left open by the first-stage internal gap:
a constant matrix removed from that internal sum and put back after both
halves of stage 0. It is a proof under the hypotheses below. It is not a
census of rank-8 maps, and a failure on this placement is not unrestricted
nonexistence of an interleaved word.

No new kappa is claimed. The selected frontier stays
`781451/250000000 = 0.003125804`.

## 1. Contract and schedule

Use the paired-star contract in `research/coupled31-chronology/PROOF.md` at
base `17469fff78c22941280f04d39dc5a1faee09c840`. The field has characteristic
2. The core and each of the g leaves have dimension d = 2q. Stage j has two
orthogonal projectors. On its core and leaf they have the shape

```text
P  = [[A+B, B], [B, A+B]],    R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]],  R' = [[A', A'], [A', A']],
```

with A' = I+A, A^2 = A, and AB+BA = B. The same relation holds for A'. A
full call is (I+x P_half)(I+e R_half) with x = D+1 and e^2 = 0. Thin calls
are I+e Z with Z constant. The variables D_j are independent and invertible.
The target is (I+e I) times the product of (I+x_j E_j), where E_j is the
identity on the core and on leaf j.

The normalized coefficient S starts at 0. A full call replaces S by
(I+x Q) S (I+x Q)^{-1} + R_Q. A thin call adds Z. The endpoint requires
S = I. The inverse of I+x Q is I+(x/D) Q.

The schedule, called the **after-stage-0 split**, is:

- one half of stage 0;
- a constant internal sum Z_int;
- the other half of stage 0;
- a constant sum Z_after;
- both halves of each stage 1, ..., g-1, with no further thin map.

Throughout, Z_int + Z_after = K. The matrix K is zero on every diagonal
block and every leaf/leaf block, and it is I on each of the two blocks
between the core and a leaf. For odd g this is the unique constant solution
of the all-D_j = 1 equation: every conjugation is then the identity, each
stage contributes T = R+R' = [[I, I], [I, I]] on its core and leaf, the core
diagonal receives g copies of I, and S = I forces the thin sum to be K.
Both gaps of this schedule see that identity conjugation, so keeping the
total sum equal to K is exactly the condition that every D_j = 1
specialization stays the same swap.

The profile is g = 13 and q = 8, so d = 16 and g is odd. The exhibited
legal pair is

```text
A = diag(I_8, 0),    B = E_{0,8} + E_{9,2},    A' = I+A.
```

B is nonzero. The two stage projectors on this B do not commute. Indices
on a leaf block run over 0, ..., 15.

## 2. A completed later stage scales blocks and does not mix leaves

On one stage support, P+P' = I and P'P = PP' = 0, so

```text
(I+x P')(I+x P) = I+x I = D I.
```

The same identity holds with the halves exchanged. On every other leaf the
product is I. Conjugation by a completed pair is therefore the scalar
operator U that multiplies the core and that leaf by D and fixes every
other leaf. The cross relations P'R = RP' = 0 and PR' = R'P = 0 make either
half fix the other half's query, so the pair adds T and no other term.

U is diagonal across the core/leaf decomposition. It multiplies an existing
block and does not move a block from one pair of summands to another. In
particular it never creates a leaf/leaf block from a core/leaf block, and
T has no leaf/leaf block. After the after-stage-0 gap, stage t multiplies
the block from leaf t into leaf 0 by D_t^{-1} and the block from leaf 0
into leaf t by D_t. Every other later stage fixes both of those blocks.

## 3. The second half acts on the internal sum

Let Q be the half applied after Z_int, with diagonal factor A_Q, and write
x = D_0+1 and L = I+x Q. The half relations of section 2 give
L R_first L^{-1} = R_first, and R_first+R_second = T_0. After both halves
and the after-gap,

```text
S = L Z_int L^{-1} + T_0 + Z_after.
```

T_0 has no leaf/leaf block. Split Z_int = K+M and Z_after = M, which is
the balanced insertion in characteristic 2.

The core/leaf swap J_0 between the core and leaf 0 commutes with Q, so
L J_0 L^{-1} = J_0. For t ≥ 1, J_t sends a vector on leaf t to the same
vector on the core and fixes that leaf under L^{-1}. The leaf-0 component
of L on a core vector c is x B c. Thus the block of L K L^{-1} from leaf t
into leaf 0 is x B, and the block from leaf 0 into leaf t is (x/D_0) B.

## 4. Theorem: support on the two leaf-0/leaf-1 blocks

Let M be an arbitrary constant matrix whose only nonzero blocks are the
two between leaf 0 and leaf 1. Write C for the block from leaf 1 into
leaf 0, and write E for the opposite block. Place M after stage 0 and
K+M in the internal gap. Then, for either half order and every invertible
specialization,

```text
S_{leaf 0 <- leaf 1} = D_1^{-1} (D_0+1) (B + (A_Q+B) C).
```

E does not appear. The same identity with C = 0 gives the uncorrected
block D_1^{-1}(D_0+1) B from leaf 1, and D_t^{-1}(D_0+1) B from every
other leaf t. A matrix supported on one pair does not change those other
blocks.

Proof. L^{-1} fixes leaf 1. M sends that vector to C u on leaf 0 and reads
nothing else from it. The leaf-0 component of L on a vector supported on
leaf 0 is (I+x(A_Q+B)) C u. Adding the after-gap copy of M contributes
another C. In characteristic 2 the two copies of C cancel, and section 3
contributes x B, so the block is x(B+(A_Q+B)C) before the tail. Section 2
multiplies it by D_1^{-1}. A vector on leaf t ≠ 1 is fixed by L^{-1} and
is invisible to M, so only the K term of section 3 remains on that block.

For this exhibited B, the block is nonzero whenever D_0 ≠ 1. Equivalently,
neither (A+B)C = B nor (A'+B)C = B has a solution, so the choice of which
half stands second does not matter.

The columns of A+B are e_0, e_1, e_2+e_9, e_3, ..., e_7, e_0, and then
zeros. A vector in that column space has coordinate 2 equal to coordinate
9. The functional φ(v) = v_2+v_9 vanishes on every column. Column 2 of B
is e_9, and φ(e_9) = 1, so e_9 is not in the column space.

The columns of A'+B span the vectors whose coordinates 1, ..., 7 are zero
and whose coordinates 0 and 8 agree. The functional ψ(v) = v_0+v_8
vanishes on that space. Column 8 of B is e_0, and ψ(e_0) = 1.

Both statements hold over every field of characteristic 2, because they
use only these 0-1 columns. In particular they hold for every rank,
including every rank-8 matrix on this support. Such matrices exist: the
block C = diag(I_8, 0), with E = 0, has rank 8 and still fails.

## 5. Theorem: each of the five named bundles

Index coordinates by 0, ..., 15 and let Z_S copy each coordinate in S from
the core onto every leaf and back. The five bundles

```text
(0,1,2,3), (0,1,4,5), (0,1,6,7), (8,9,10,11), (12,13,14,15)
```

each have rank 8, and their sum is K. Move one bundle Z_S into the
after-stage-0 gap and leave K+Z_S internal. For either half order,

```text
S_{leaf 0 <- leaf t} = D_t^{-1} (D_0+1) B π_{S^c},
S_{leaf t <- leaf 0} = D_t (D_0+1) D_0^{-1} π_{S^c} B,
```

where π_{S^c} is the coordinate projection off S. Whenever D_0 ≠ 1, the
first block is nonzero for every one of these five sets.

Proof. Z_S has no leaf/leaf block, and neither does K. On a vector u
supported on leaf t ≥ 1, L^{-1} fixes the leaf and Z_S writes π_S u on the
core. Section 3 sends that core vector to x B π_S u on leaf 0. The K term
contributes x B, so the sum is x B π_{S^c}. The after-gap copy of Z_S adds
nothing to a leaf/leaf block, and section 2 only scales the result.
Starting from leaf 0, L^{-1} writes (x/D_0) B u on the core, Z_S copies
the S-coordinates of that core vector onto leaf t, and the same arithmetic
produces the opposite block.

B has nonzero columns exactly at 2 and 8. Each of the five sets misses at
least one of those columns, so B π_{S^c} ≠ 0. The scalar D_t^{-1}(D_0+1)
is nonzero when D_0 ≠ 1. This is a proof for these five maps, both half
orders, and every invertible specialization with D_0 ≠ 1. It is not a
classification of other rank-8 maps.

## 6. Witness: one other rank-8 coordinate map clears the leaf block

Let S = {0, 2, 8, 9}. Then Z_S has rank 8. The same formulas as section 5
give the zero matrix in every leaf/leaf block: columns 2 and 8 of B both
lie in S, and rows 0 and 9 of B both lie in S. Place Z_S after stage 0 and
K+Z_S internally. The total thin sum is still K, so every D_j = 1
specialization is still the swap. Every leaf-to-leaf block of the
normalized coefficient, including leaf 0 ← leaf 1, is the zero matrix, for
both half orders and every invertible D.

This is a witness for that block, not an endpoint. It is not one of the
five bundles in section 5, and it is not a matrix supported only on the
two leaf-0/leaf-1 blocks. At both specializations

```text
(2,3,4,5,6,7,8,9,10,11,12,13,14)
(6,10,3,5,7,9,11,13,14,2,4,8,12)
```

and in both half orders, the normalized coefficient is not I. Its
disagreement with I has rank 32. Those four evaluations are exact
eliminations over GF(16). They are not a sample, and they are not a claim
that the defect has rank 32 at every other point.

A further constant matrix N of rank at most 8, subtracted from the
internal sum and added after stage 0, cannot repair this witness at those
points. The second half and the later scalar operators are invertible, and
the queries do not depend on N, so N changes the final coefficient by the
conjugate of L N L^{-1}+N. That change has rank at most 2 rank(N) ≤ 16.
A rank-32 defect is not a rank-16 matrix. This does not forbid a partner
of rank 16, whose change can have rank up to 32, and it does not forbid a
matrix placed in a different gap.

## 7. What the checker establishes

`verify.py` uses GF(16) with x^4+x+1. It raises unless all of the
following hold.

- The exhibited pair is legal, B has the two stated corners, and the stage
  projectors do not commute. The half products and the query cross terms
  of section 2 are zero, and J_0 commutes with both halves.
- φ vanishes on the columns of A+B and separates column 2 of B. ψ vanishes
  on the columns of A'+B and separates column 8 of B.
- On a g = 3, q = 4 split word, the fast updater agrees with dense
  conjugation and with the section 4 formula, in both half orders.
- The exhibited rank-8 leaf block C = diag(I_8, 0) reproduces section 4 at
  both g = 13 points and both half orders, including the unchanged blocks
  from leaf 2 and leaf 12. Changing E does not change those blocks. The
  pure product is the target. Every D_j = 1 gives S = I. The empty
  after-gap recovers D_1^{-1}(D_0+1) B. With B = 0 the empty after-gap has
  block 0, and the same C follows the formula with that zero corner.
- Each of the five bundles has rank 8, the five sum to K, and both block
  directions match section 5 at both points, both orders, for leaves 1 and
  12. The predicted blocks are nonzero. Every D_j = 1 gives S = I.
- The witness of section 6 has rank 8, clears every leaf/leaf block, keeps
  the pure product and the D_j = 1 swap, and has defect rank 32 at the
  four evaluations. One explicit balanced rank-8 partner, the leaf block
  C above, changes that state by a matrix of rank at most 16 and does not
  meet the endpoint.

The two field points check the updater against the identities. The
identities themselves are sections 2 through 6. One nonzero specialization
is enough, together with the functionals, to know the leaf-supported block
is not the zero matrix; the checker records two, in both half orders.

## 8. What this does not prove

- It does not say that every rank-8 matrix fails. Section 6 is a rank-8
  map in this same gap for which the leaf block is zero.
- It does not classify matrices that meet the core, or more than one pair
  of leaves, except for the five named bundles and the one witness.
- It does not move stage 0 off the first position. An earlier adjacent
  pair would scale the state before the half conjugation.
- It does not put a full call between the halves, and it does not treat
  nested or crossed stage intervals.
- It does not enter g = 31, q = 26.
- The rank-32 defect is computed at two specializations. That rules out a
  constant rank-at-most-8 partner for this witness, because any such
  partner would have to work at those points. It does not by itself name
  the defect at every other point.
- No search over legal off-diagonal blocks B was run. The functionals use
  the two corners exhibited here.
- Native transport, frames, and the selected frontier are untouched.

## 9. Credit

The paired-star contract and the chronological rank floor are from PR
#5747 (Ali Romman), with the predecessor statements in PR #5673, PR
#5631, and PR #5617. The adjacent-halves count that leaves an internal
gap open is open PR #7010. The first-stage internal gap at g = 13, q = 8,
whose open question 1 is the placement proved here, is open PR #7026.
The consecutive rank bound at g = 31, q = 26 is open PR #7005. None of
those schedules is the split in section 1.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
