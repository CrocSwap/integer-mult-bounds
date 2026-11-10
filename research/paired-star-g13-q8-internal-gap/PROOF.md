# One internal gap misses the g=13, q=8 paired star

This is a proof for one schedule. It is not a census of interleavings, and it
is not a claim that every word with a call between two stage halves fails.

No new kappa is claimed. The selected frontier stays
`781451/250000000 = 0.003125804`.

## 1. Contract

Use the paired-star contract in `research/coupled31-chronology/PROOF.md` at
base `17469fff78c22941280f04d39dc5a1faee09c840`. The field has characteristic
2. The core and each of the g leaves have dimension d = 2q. Stage j has two
orthogonal projectors. In core/leaf blocks they have the legal shape

```text
P  = [[A+B, B], [B, A+B]],    R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]],  R' = [[A', A'], [A', A']],
```

with A' = I+A, A^2 = A, and AB+BA = B. The same relation holds for A',
because A'B+BA' = AB+BA. A full call is (I+x P)(I+e R) with x = D+1 and
e^2 = 0. Thin calls are I+e Z with Z constant. The variables D_j are
independent and invertible. The target is (I+e I) times the product of
(I+x_j E_j), where E_j is the identity on the core and on leaf j.

The normalized coefficient S is the left factor in (I+e S) times the pure
product. A full call replaces S by (I+x P) S (I+x P)^{-1} + R. A thin call
adds Z. The endpoint requires S = I. The inverse is I+(x/D) P, since
(I+x P)(I+(x/D) P) = I.

## 2. The pattern

Number the leaves 0 through g-1. The word does one of the following, and
nothing else.

- Apply one half of stage 0, then every thin map, then the other half of
  stage 0. Either half may come first.
- Then apply both halves of stage 1, both of stage 2, and so on through
  stage g-1. Those pairs are adjacent. No thin map sits in any later gap.

Call this the **first-stage internal gap**. Stages 1 through g-1 are the
consecutive tail. The pattern separates the halves of stage 0 and of no
other stage.

## 3. Local factor of an adjacent pair

On a stage's own core and leaf,

```text
P+P' = [[I, 0], [0, I]],    P'P = 0,    PP' = 0.
```

The off-diagonal blocks of P'P are A'B+BA and BA+A'B. Substituting
A'B = B+AB gives A'B+BA = B+(AB+BA) = B+B = 0. The diagonal blocks reduce
to the same expression because A'A = 0. Thus

```text
(I+x P')(I+x P) = I+x E
```

on that core and leaf, and the identity on every other leaf. The same
holds with the halves exchanged. In particular B cancels, so a completed
pair conjugates by the scalar operator U that multiplies the core and that
leaf by D and fixes every other leaf.

The same cancellation gives P'R = RP' = 0 and PR' = R'P = 0. Conjugation
by either half therefore fixes the other half's query, and an adjacent
pair adds T = R+R' = [[I, I], [I, I]] on its core and leaf after the
scalar conjugation. Leaf-to-leaf blocks of T are zero.

## 4. Setting every D_j = 1 forces one sum

At D_j = 1 every x_j is 0, so every conjugation is the identity. Each
stage contributes T_j regardless of order, and

```text
S = sum_j T_j + sum Z.
```

The sum of the queries has I on the core diagonal exactly g times, I on
each leaf diagonal, and I on each core/leaf off-diagonal pair. For odd g
the core diagonal is I. The endpoint S = I therefore forces the thin sum
Z to be the matrix K which is I on every core/leaf off-diagonal pair and
zero on every diagonal and every leaf/leaf block. Every block is fixed.
There is no other constant solution of the D_j = 1 equation in this
pattern, at any rank.

## 5. The second half moves K onto a leaf/leaf block

Write y = x/D = 1+D^{-1} and let L = I+x Q, where Q is whichever half is
applied after the thin maps. Both P and P' have off-diagonal block B, so

```text
L = [[I+x(A_Q+B), x B], [x B, I+x(A_Q+B)]]
```

on the core and leaf 0, and L acts as the identity on every other leaf.
Here A_Q is A or A'. The same formula with y gives L^{-1}.

Split K = J_0 + sum_{t=1}^{g-1} J_t, where J_t is I on the two blocks
between the core and leaf t. The matrix J_0 commutes with Q: both products
equal [[B, A_Q+B], [A_Q+B, B]]. Thus L J_0 L^{-1} = J_0, which has no
leaf/leaf block.

For t ≥ 1, apply L J_t L^{-1} to a vector supported on leaf t. L^{-1}
fixes that leaf, J_t sends the vector to the core, and L sends a core
vector c to (x B) c on leaf 0. The block of L J_t L^{-1} from leaf t to
leaf 0 is therefore x B. The symmetric computation, starting from leaf 0,
gives the block from leaf 0 to leaf t equal to y B.

T_0 does not meet those blocks, and neither does J_0. After stage 0,

```text
S_{leaf 0, leaf t} = (D_0+1) B,
S_{leaf t, leaf 0} = (D_0+1) D_0^{-1} B.
```

## 6. The consecutive tail scales the block and does not cancel it

Each later stage k replaces S by U_k S U_k^{-1} + T_k. The operator U_k
multiplies the block from leaf t to leaf 0 by D_t^{-1} when k = t, and by
1 otherwise: leaf 0 is outside every later support, and leaf t is inside
only stage t. No query T_k has a leaf/leaf block, and U_k does not mix
distinct leaves. The final normalized block is

```text
S_{leaf 0, leaf t} = (D_0+1) D_t^{-1} B,
S_{leaf t, leaf 0} = D_t (D_0+1) D_0^{-1} B.
```

## 7. Theorem

Let g be odd and at least 2, and let B be nonzero. In the first-stage
internal gap, no constant thin maps meet the endpoint. Both half orders
are included.

Indeed K is the only sum allowed by section 4, and section 6 then gives a
leaf-to-leaf block equal to a nonzero scalar times B at every
specialization with D_0 ≠ 1 and D_t ≠ 0. The normalized coefficient is
not I.

In particular this holds at g = 13 and q = 8. Five rank-8 maps can sum to
K, so the obstruction is not that the D_j = 1 equation is impossible at
rank q. Index the d = 16 coordinates by 0, ..., 15. Let K_a copy
coordinate a from the core onto every leaf and sum that coordinate from
every leaf back into the core. Its image is spanned by the core basis
vector e_a and the vector that equals e_a on every leaf, so its rank is 2.
The five bundles

```text
(0,1,2,3), (0,1,4,5), (0,1,6,7), (8,9,10,11), (12,13,14,15)
```

each contain four coordinates. Coordinates 0 and 1 lie in three bundles
and every other coordinate lies in one, so the sum of the five bundle
maps is K. Distinct coordinates use distinct slots, and each bundle has
rank 8. Their total rank is 40.

The chronological floor in `research/coupled31-chronology/PROOF.md` is
4q + 2 ceil((g-2)/3). At these parameters it equals 40. These five maps
meet that number and still fail. This note does not re-prove the floor.
The adjacent-halves count in the open consecutive-halves argument is a
different schedule: it does not apply once a thin map stands between the
halves, and it is not used here.

The pure product is still the target. Thin maps contribute the identity
to the pure word, and each completed stage contributes I+x E_j. Those
factors commute. The failure is only the coefficient of e.

## 8. What the checker establishes

`verify.py` evaluates the normalized coefficient over GF(16), with the
degree-4 polynomial x^4+x+1. It raises unless all of the following hold.

- The exhibited (A, B) is legal. B is nonzero, with ones at positions
  (0, q) and, for q > 2, (q+1, 2). The two stage projectors on that B do
  not commute. The same checks pass for B = 0, where the projectors are
  not asked to be noncommuting.
- The five bundles have rank 8, odd coordinate coverage, and sum K. The
  sum has rank 32.
- On a g = 2, q = 1 word, the fast updater agrees with the dual-number
  product and with deriv · pure^{-1}. A completed pair scales the
  leaf-0←leaf-1 entry by D_1^{-1}. One half alone does not.
- For g = 1, the full swap between the two halves meets the endpoint at
  three values, including D = 1. There is no second leaf, so section 6
  has nothing to obstruct. This map has rank 4q, not rank q.
- At g = 13, q = 8, both half orders, the five maps give S = I when every
  D_j = 1. At

```text
(2,3,4,5,6,7,8,9,10,11,12,13,14)
(6,10,3,5,7,9,11,13,14,2,4,8,12)
```

the pure product is the target, S is not I, and both leaf-0/leaf-t blocks
for t = 1 and t = 12 equal the scalars in section 6. Those scalars are
nonzero because D_0 ≠ 1.

- The same five maps placed after both halves of stage 0 produce the zero
  block in leaf 0←leaf 1. The internal half is what creates the block.
- With B = 0 the same internal word produces the zero block, in agreement
  with the factor B. The commuting-projector theorem already excludes five
  maps of unrestricted rank for every order when B = 0. That theorem is
  not re-proved here.

The two field points are a consistency check of the updater against the
block identity. The identity itself is sections 3 through 7. One nonzero
specialization is enough to show that the block polynomial is not the
zero matrix; the checker records two, in both half orders.

## 9. What this does not prove

- A thin map may still occupy a later gap as well as the internal gap.
  Section 4 used that every thin map sees the same conjugation.
- The open stage may fail to be the first stage. An earlier adjacent pair
  would scale the state before the half conjugation.
- Another stage's full call may stand between the halves. The pure
  product in section 7 uses that the only pure factors between the halves
  are identities.
- Nested or crossed stage intervals are outside the pattern.
- The same schedule shape is not certified at g = 31, q = 26. The internal
  gap left open by the consecutive rank argument at that profile is a
  different question, and this package does not enter it.
- No exhaustive or sampled search of patterns, projectors, or field
  elements was run. Absence of such a search is not nonexistence of every
  interleaved word.
- The g = 3 finite censuses do not lift, and they are not inputs.
- Native transport, frames, and the selected frontier are untouched.

When B = 0 the leaf/leaf block of section 6 is zero, so this certificate
does not fire. That hypothesis is the commuting case already settled for
every call order.

## 10. Credit

The paired-star contract, the chronological rank floor, and the commuting
map-count are from PR #5747 (Ali Romman), with the predecessor statements
in PR #5673, PR #5631, and PR #5617. The adjacent-halves count that leaves
an internal gap open is the open PR #7010 argument. The consecutive rank
bound that leaves the g = 31 internal gap open is the open PR #7005
argument. Neither schedule hypothesis is the pattern proved here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
