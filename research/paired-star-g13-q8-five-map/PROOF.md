# Consecutive stage halves still need ceil(g/2) thin maps

This is a proof under a stated schedule hypothesis. It is not an exhaustive
census of every word, and it is not a claim that the g=13, q=8 profile is
impossible once a call is allowed to sit between the two halves of a stage.

Selected κ stays 781451/250000000. Nothing here changes that record.

## Contract

Use the paired-star contract recorded in
`research/coupled31-chronology/PROOF.md` and `COMMUTING.md` at base commit
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The field has characteristic 2.
There are g leaves and q coupled ports. Each stage has exactly two full calls.
In the block basis of the core and one leaf, a legal pair has the shape

```text
P  = [[A+B, B], [B, A+B]],    R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]],  R' = [[A', A'], [A', A']],
```

with A and A' rank-q idempotents, A+A' = I, B' = B, and AB+BA = B. Then
P and P' are complementary projectors resolving E = diag(I, I), R+R' = T,
and T is the matrix of all four identity blocks. The same shape is used on
every stage, with the leaf block placed on that stage's leaf. Projectors
from different stages are not assumed to commute, so B may be nonzero.

A full call at stage j is (I+(D_j+1)P)(I+e R) with e^2 = 0. A thin call is
I+e Z with Z a constant matrix of any rank. The endpoint asks for the pure
product (I+e I) times prod_j (I+x_j E_j), x_j = D_j+1. Equivalently, the
normalized coefficient S in the state (I+e S) Pure finishes at I.

A word has **consecutive halves** when the two full calls of each stage
occupy adjacent positions. Thin maps, and the calls of other stages, sit
only in the gaps before, between, or after those g pairs. The order of the
pairs is arbitrary. A thin map placed between the two halves of a stage is
outside this hypothesis.

## Lemma 1. An adjacent pair emits T and multiplies by U = I+xE

Let the two halves be applied with nothing between them, P first and P'
second. The scalar is x = D+1 and the inverse of I+xP' is I+(x/D)P',
because P'^2 = P' and D ≠ 0.

Since A' = I+A,

```text
P' R = [[A' A, A' A], [A' A, A' A]] = 0,
R P' = [[A A', A A'], [A A', A A']] = 0,
```

in characteristic 2. The B blocks cancel in these products, and A'A = 0
because A is idempotent. Therefore Ad_(I+xP')(R) = R. The pair adds R+R' = T
to the normalized coefficient, and the pure factor is

```text
(I+xP')(I+xP) = I + x(P+P') = I+xE,
```

because P P' = 0. The opposite order of the two halves gives the same pure
factor and the same emission. The calculation uses only the legal local
shape. It does not use B = 0, and it does not use commutation between
stages.

## Lemma 2. Later stages scale each region block by one monomial

Once a stage has been completed as an adjacent pair, its pure factor is
U_k = I+x_k E_k. These operators commute with each other, because every
E_k is diagonal in the same region basis. A thin map in a gap is afterwards
conjugated only by the U_k of stages that are still to come.

U_k acts on a block from region α to region β by the scalar

```text
D_k     if α is in the support of E_k and β is not,
D_k^{-1} if β is in the support and α is not,
1       otherwise.
```

The support of E_k is the core together with leaf k. On the core→leaf j
block, a later stage k therefore contributes D_k when k ≠ j and contributes
1 when k = j. On the leaf j→core block the same stage contributes the
inverse scalar. Each block of a constant thin map is multiplied by a single
Laurent monomial, not by a sum of monomials.

## Lemma 3. One gap meets the monomial of at most two leaves

Fix a completion order π_1, …, π_g of the stages, and consider a thin map
placed after t completed stages. Write R for the set of stages still to
come. The map's core→leaf j monomial is the product of D_k over k in
R \ {j}.

Stage j inserts T_j at the moment it completes. The core→leaf j block of
that T_j is I, and only the stages after j conjugate it, so its monomial
is the product of D_k over stages after j.

Those two index sets agree in exactly one of these cases:

- j is the next stage. Then R \ {j} is the set of stages after j.
- j is the stage that just completed. Then j is not in R, and R itself is
  the set of stages after j.

Every other leaf has a different index set. The same dichotomy holds for
the leaf→core block, with every exponent negated. A gap therefore has the
correct monomial for at most two leaves: the stage just finished, if any,
and the next stage, if any.

The Laurent monomials in independent stage variables are linearly
independent. On an uncovered leaf the coefficient of the needed monomial is
exactly the identity contributed by T_j. A thin map in any other gap adds
its block to a different monomial. It does not change that coefficient.
Several maps in the same gap add their blocks to the same monomial; they
still do not reach a leaf for which the gap has the wrong monomial.

Cancelling leaf j therefore requires at least one thin map in a gap
adjacent to j in the completion order, with the sum of those maps' blocks
equal to I in both off-diagonal directions. One map occupies one gap, so it
can serve at most the two leaves adjacent to that gap. This count does not
depend on the rank of the map, on q, or on whether B is zero.

## Theorem

In every characteristic-2 field, for every port count q and every leaf
count g, a paired-star word whose stage halves are consecutive needs at
least ceil(g/2) thin maps. The full projectors need not commute.

The g gaps in a fixed completion order form a path of g edges. Each thin
map sits at one vertex of that path and covers at most the two incident
edges. Covering every edge takes at least ceil(g/2) vertices. For g = 1
the single query T_1 is not I, so that word needs its one map as well.

In particular, no word with consecutive halves realizes the profile of
g = 13 leaves, q = 8 ports, and five thin maps. Five maps cover at most
ten leaves, whichever gaps they occupy and whatever their ranks are. The
same arithmetic says that five consecutive-halves maps also leave at least
twenty-one of thirty-one leaves uncovered. That is only the adjacent-halves
subcase of the thirty-one-leaf profile. This package does not investigate
a word that separates the halves of a thirty-one-leaf stage.

## The rank floor does not already give this obstruction

`research/coupled31-chronology/PROOF.md` records the paired rank floor
R ≥ 4q + 2 ceil((g-2)/3). At g = 13 and q = 8 that floor is 40. Five maps
of rank q meet it with equality. The floor is a necessary condition, not a
construction, and this package does not re-prove it. The map-count above
is independent of it: consecutive halves fail at five maps even if each
map is allowed to have arbitrary rank.

## The count is sharp for consecutive halves

The word in `COMMUTING.md` already meets ceil(g/2) with consecutive halves:
both halves of stage 1, both of stage 2, and so on; after each odd stage j,
one thin map carrying the identity in both directions between the core and
leaves j and j+1, or only leaf j when j = g. When g is even, that first
thin map also carries the core identity.

Lemma 1 shows that this word emits each T_j and multiplies by each U_j for
every legal B, not only for B = 0. Later conjugation is the monomial
scaling of Lemma 2, which does not read B. Each leaf is adjacent to the
gap where its identity map sits, so every off-diagonal coefficient is
I+I = 0. Diagonal blocks of T_j are fixed by later U_k. Their sum is I on
every leaf diagonal, and it is I on the core diagonal when g is odd. When
g is even the core sum is 0 and the first thin map supplies the missing
identity; later stages scale that core block by 1. No leaf-to-other-leaf
block is ever filled. The normalized coefficient finishes at I, and the
pure product is the required diagonal product.

Thus nonzero B, including B for which projectors of different stages do
not commute, does not reduce the consecutive-halves count below
ceil(g/2), and the same word shows that the count is achieved.

The commuting theorem in `COMMUTING.md` is the special case in which
commutation has already forced B = 0. The argument here keeps the legal
local shape and drops that commutation hypothesis, in exchange for the
adjacent-halves hypothesis. The two statements agree on the number.

## What the checker establishes

`verify.py` is an independent reading of the same state machine: pure and
derivative matrices over GF(16), with the normalized coefficient recovered
both as deriv · pure^{-1} and by the conjugation update. It raises unless
all of the following hold.

- All 24 legal F_2 pairs at q = 1, and an explicit legal pair at q = 8
  with nonzero B, satisfy Lemma 1. The q = 8 pair used for two stages has
  projectors that do not commute.
- The sharp word meets the full endpoint on the grid {2,4,8}^g for
  g = 1, 2, 4, 5 at q = 1, with a nonzero B whose stage projectors do not
  commute. Each stage variable has degree at most 2, so three distinct
  values separate the polynomial identity for those words. Deleting one
  of the sharp maps misses the endpoint. The same grid check passes for
  the q = 8, g = 2 word and fails if its thin map is removed.
- For every completion order at g ≤ 7, and for forty deterministic random
  orders at g = 13, the exponent-set rule and the adjacent-stage rule name
  the same leaves, and every gap names at most two.
- In label order, every placement of five gaps among the fourteen possible
  gaps covers at most ten of the thirteen leaves.
- At g = 13, q = 1, with the same noncommuting B, the seven-map sharp word
  meets the endpoint at two GF(16) points. The five-map word that keeps
  only the maps after stages 1, 3, 5, 7 and 9 misses both points. Its
  normalized core↔leaf blocks equal the monomial prediction, and leaves
  11, 12 and 13 remain nonzero. Those two points are a consistency check
  of the interpreter against the Laurent formula. The identity for general
  g and q is the argument above, not an interpolation on thirteen
  variables.

## The three-leaf results do not lift

Open PR #6922 records that one F_2 thin map misses the three-leaf, block
size 2 endpoint, including noncommuting projectors and every order of the
six full calls. Open PR #6940 records that every two-map word on that same
finite contract has total thin rank at least 8. Both state that this does
not decide g = 13, q = 8 or g = 31, q = 26.

Those censuses fix three leaves, block size 2, and entries in F_2. A
finite statement at that size does not by itself constrain thirteen leaves
or eight ports. The extra rank above 4q in the g = 13 floor is eight in
total, not eight per port, so the profiles are not a port-wise product of
the three-leaf census. This package does not repeat either census and does
not treat either one as a proof at g = 13.

## The interleaved schedule stays open

If a call stands between the two halves of a stage, Lemma 1 still describes
the emission of that stage's own query, but the conjugation of older
material is conjugation by a single half-projector. For nonzero B, I+xP
is not diagonal in the region basis, so one half can send a block to a sum
of two monomials. The pigeonhole above does not apply to that word.

No interleaved word with five rank-q thin maps is supplied here, and none
is ruled out. A search that fails to find one would be a search failure,
not a proof that no such word exists. Native transport, the physical bill,
and κ are out of scope even if such a word is later found.
