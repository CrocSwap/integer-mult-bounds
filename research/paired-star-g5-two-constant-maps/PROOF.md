# Two constant thin maps miss one g=5 paired-star word at q=1

**Evidence class: proof, under the hypotheses below.** Selected κ stays
363005817/100000000000. Nothing here edits that record. This is not an
exhaustive census of paired-star words, and it is not a search failure
promoted to nonexistence. Each negative statement is either a polynomial
identity, a complete enumeration of a 24-element set, or an inconsistent
linear system at an explicit point.

## Hypotheses

The field has characteristic 2. There is q=1 coupled port, so every block
has size d=2, and there are g=5 leaves. The fixed legal pair is

```text
A = [[1, 0], [0, 0]],    B = [[0, 1], [0, 0]],    A' = I + A.
```

Then A^2 = A, A' = I+A, rank A = 1, and AB+BA = B. On stage j the calls are
the usual embedded blocks

```text
P  = [[A+B, B], [B, A+B]],    R  = [[A, A], [A, A]],
```

and the same formulae with A replaced by A'. The two halves are
complementary projectors, P R = R, and R+R' = T_j. The same pair is used
on every stage. The projectors of stage 0 and stage 1 do not commute.

A full call is (I+(D_j+1) P)(I+e R) in F[e, D_0, ..., D_4]/(e^2). Because
P R = R, its e coefficient is D_j R and its pure factor is I+(D_j+1) P.
A thin call is I+e Z with Z constant. The endpoint is

```text
(I+e) prod_j (I+(D_j+1) E_j).
```

List order is chronological: the first call is the rightmost factor. Gap k,
for k = 0, ..., 10, is the position after the first k full calls.

## Theorem 1. A foreign full call cannot separate this pair

**Statement.** Suppose two stages both use the pair above. The pure product
of their four full calls equals (I+x_0 E_0)(I+x_1 E_1) if and only if each
stage's two halves occupy adjacent positions. Consequently, at every g≥2,
no placement of constant thin maps meets the endpoint on a word that puts a
full call of one stage between the halves of another stage, when every
stage uses this same pair.

**Adjacent orders.** In the 12-dimensional space of g=5,

```text
(I+x P')(I+x P) = (I+x P)(I+x P') = I+x E
```

as polynomials in one variable x. The factors I+x_j E_j commute with each
other, because each E_j is diagonal in the region basis. Any word whose
full calls form five adjacent stage blocks therefore has the endpoint's
pure factor, for either internal order of each block and any order of the
blocks. Thin maps contribute I to the pure product, so they do not change
this conclusion.

**The other sixteen orders.** There are 4! = 24 orders of four labeled
calls, and exactly 8 of them are adjacent. Each of the other 16 misses the
pure endpoint at (D_0, D_1) = (2, 3) in GF(256). A polynomial identity would
survive that substitution. The registered census checks that the orders
which pass the point are exactly the 8 adjacent orders.

**Lift.** Suppose a full call of stage s sits between the halves of stage
j in a longer word, and every stage uses this pair. Set D_k = 1 for every
stage other than j and s. Then x_k = 0, so each of those gates is the
identity. The pure product specializes to the induced order of stages j
and s, and the endpoint specializes to (I+x_j E_j)(I+x_s E_s). The induced
order separates stage j, so it is one of the 16 failures. The checker
locks the gate fact (a factor I+(D+1) P is I when D=1) and multiplies one
explicit witness: the g=5 order (0a, 1a, 0b, 1b) followed by adjacent
blocks for stages 2, 3, and 4. Its pure polynomial is not the endpoint, and
the further substitution (2, 3, 1, 1, 1) misses as well.

This is an exhaustive census of a 24-element set, plus the specialization
that copies a bad induced order into every longer word. It is not a search
over g.

## Theorem 2. The identity block order admits no two constant thin maps

**Statement.** Let Λ be the full-call order that completes stages 0, 1, 2,
3, 4 in that order, half A before half A' inside each stage, with the pair
above on every stage. No placement of exactly two constant thin maps in
two distinct gaps meets the endpoint.

By Theorem 1 the pure product of Λ equals the endpoint's pure factor Q.
Two maps in one gap add to a single matrix. That one-map case is not
re-proved here. The 55 placements into distinct gaps are decided below.

**The sum of the two maps.** Set every D_j = 1. Each full call collapses
to I+e R, the two halves of stage j sum to T_j, and the endpoint collapses
to I+e. Therefore any successful pair of constant maps satisfies

```text
Z_1 + Z_2 = I + sum_j T_j = K.
```

With the core first and g odd, the blocks of K are 0 on every diagonal
region and I in both directions between the core and each leaf. The
three-map word in the next section sums to this same K.

**The gap equation.** At a point where every D_j is nonzero, each pure gate
is invertible: its eigenvalues are 1 and D_j. Write L_k and R_k for the
pure products of the full calls after and before gap k. The endpoint holds
if and only if

```text
L_1 Z_1 R_1 + L_2 Z_2 R_2 = Q + (sum of the full-call e contributions).
```

Substituting Z_2 = K+Z_1 gives one linear equation for the 144 entries of
Z_1. Both of the points

```text
(2, 3, 5, 6, 7) and (6, 7, 11, 13, 14)
```

lie in GF(256)^5, with the AES polynomial x^8+x^4+x^3+x+1, and every
coordinate is nonzero. For every one of the C(11, 2) = 55 gap pairs the
stacked system is inconsistent. An inconsistent linear system over GF(256)
stays inconsistent over any extension. A constant solution whose entries
lie in a characteristic-2 field would specialize into that extension,
because the gate entries at these points lie in GF(256) and the pair itself
lies in F_2. Therefore no constant pair meets Λ.

Forty of the 55 pairs put at least one map between the halves of a stage.
Those gaps are 1, 3, 5, 7, and 9: gap 1 lies between stage 0's halves, gap
3 between stage 1's halves, and so on. The named first-step placement is
gaps 1 and 3. The adjacent-halves count in PR #7010 does not cover these
forty placements, because a thin map between the halves means the two full
calls are not adjacent in the word. The same linear system rules them out.
The other fifteen pairs leave every stage block intact; they are included
in the 55 and are not given a separate argument.

The formula is the one used for the three-leaf census. A probe matrix in
gap 1, carried through the polynomial word and through L Z R, agrees at
(2, 3, 5, 6, 7). That lock is what ties the eliminator to the polynomial.

## The three-map word on Λ still meets the endpoint

Use the maps from `research/coupled31-chronology/COMMUTING.md`, with this
nonzero B rather than B=0. After both halves of each even stage
s in {0, 2, 4}, insert the thin map that carries I in both directions
between the core and leaves s and s+1, or only leaf s when s=4. The gaps
are 2, 6, and 10. Each map has rank 4. The product equals the endpoint as
a polynomial over F_2. Deleting the last map keeps the pure factor and
misses the e coefficient.

The same identity at g=3, q=1, with this pair, is the positive control for
the eliminator. The two sharp maps sit in gaps 2 and 6, they sum to K, and
the gap formula returns a zero residual. The g=5 calculation uses that
same elimination. It accepts this known solution and rejects every gap
pair on Λ.

## One mixed order that separates a stage and keeps the pure factor

Theorem 1 uses one pair on every stage. The following word does not. Stage
0 uses the diagonal pair (A, B=0). Stages 1, 2, 3, and 4 use the nonzero
pair above. The full-call order is

```text
(0a, 1a, 1b, 0b, 2a, 2b, 3a, 3b, 4a, 4b).
```

Stage 0's halves are separated by the adjacent block of stage 1. The pure
product equals the endpoint as a polynomial, so the word is outside both
the adjacent-halves hypothesis and the commuting hypothesis: the stage-0
projector and the stage-1 projector do not commute. The same two-point
system is inconsistent for all 55 gap pairs.

The swapped assignment, with the nonzero pair on stage 0 and the diagonal
pair on the other stages, in this same order, misses the pure endpoint.
No thin maps repair that swap. This is one order, not a classification of
mixed assignments.

## What this does not say

- It does not change κ. It does not price a caller, a tape, or a native lift.
- It does not treat the other 5! · 2^5 − 1 adjacent-block orders of this
  pair. Only Λ is solved among those orders.
- It does not treat the other eleven F_2 resolutions, or a pair whose
  entries leave F_2, or any q>1.
- It does not classify mixed assignments. One pure-correct mixed order is
  solved, and one swapped order misses the pure product.
- It does not re-prove the one-map theorem of PR #7090, and it says nothing
  about five thin maps at g=13 or g=31.
- A thin matrix that depends on the D_j is outside the constant-map
  contract. The specialization step uses that Z is constant.
