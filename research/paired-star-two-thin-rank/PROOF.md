# Two F_2 thin maps on the three-leaf paired star have total rank at least 8

No new kappa. At block size 2 and three leaves, every paired-star word with
two thin maps has total thin rank at least 8. The commuting construction
meets the endpoint with ranks 4 and 4, so 8 is sharp for this contract.
One thin map is impossible as well. This does not build a caller and it
does not touch the selected frontier.

## 1. Contract

Keep the paired-star contract of
`research/coupled31-chronology/PROOF.md`. The space is a core plus g=3
leaves, each of dimension d=2, over a field of characteristic two. Stage
j acts on the core and leaf j. A full call is `(I + x_j P)(I + e R)` in
`F[e, D_0, D_1, D_2] / (e^2)`, where `x_j = D_j + 1`, `R = P T_j`, and the
two projectors of a stage are an orthogonal resolution of `E_j` and commute
with `T_j`. A thin call is `I + e Z` for a constant matrix Z with entries
in F_2. The target is

```text
(I + e) * product_j (I + x_j E_j).
```

The local form is the same as in that proof:

```text
P = [[A + B, B], [B, A + B]],    R = [[A, A], [A, A]].
```

A and I+A are rank-1 idempotents over F_2. There are 12 unordered
resolutions. Three of them have B=0. Of the 12*12 ordered pairs of
resolutions, 96 have noncommuting A factors, so the census is not the
commuting subcase. Each stage chooses one resolution. The six full calls
may stand in any of 720 orders. That is 12^3 * 720 = 1,244,160 words.
List order is chronological: the first call is the rightmost factor.

The predecessor rank bound gives

```text
sum of thin ranks >= 2d + 2 ceil((g - 2) / L) = 6
```

with L=3. Two maps may therefore have ranks adding to 6 or 7 without
breaking that bound. `COMMUTING.md` needs at least two thin maps only when
every full projector commutes, and its sharp construction at g=3 uses
ranks 4 and 4.

## 2. Statement

**Theorem.** In this contract, no word has exactly one thin map. Every
word with exactly two thin maps has rank sum at least 8. Both bounds are
realized in the sense that the commuting construction of `COMMUTING.md`,
specialized to g=3 and q=1, meets the endpoint with two maps of ranks 4
and 4, and deleting either map or moving the first map into the other odd
gap misses the endpoint.

Three or more thin maps, entries outside F_2, and stages with three or
more full calls are outside the theorem.

## 3. One map, and two maps in one gap

In characteristic two, `(I + x P)(I + e R) = I + x P + e D R` whenever
`P R = R`. A thin map contributes its matrix and does not change the pure
product. For a pure product Q equal to the target's pure part, the gap
after the first k calls has a unique candidate

```text
Z = L_k^{-1} (Q + full-call sum) R_k^{-1},
```

where `R_k` is the pure product of the earlier calls and `L_k` is the pure
product of the later calls. Every specialization below uses nonzero stage
values, so every prefix `I + (D+1) P` is invertible.

Any legal Z has entries in F_2, so it is unchanged by specialization. The
census evaluates the candidate at

```text
(D_0, D_1, D_2) = (2, 3, 5) and (6, 7, 11)
```

in GF(256) with the AES polynomial `x^8 + x^4 + x^3 + x + 1`. If the two
values are not the same 0-1 matrix, that gap has no legal Z. Across all
1,244,160 words, no gap agrees. A genuine one-map solution would have
agreed, so none exists.

Two thin maps in the same gap add, in characteristic two, to one thin map.
That case is the one-map theorem.

## 4. Two maps in different gaps

Let the thin maps sit in gaps `g < h`, with matrices Z_g and Z_h. The pure
product must still equal the target's pure part. The e coefficient is

```text
L_g Z_g R_g + L_h Z_h R_h + full-call sum = Q.
```

Hence

```text
Z_g = A Z_h B + C,    A = L_g^{-1} L_h,    B = R_h R_g^{-1},
```

with C the conjugated full-call defect. A, B and C depend on the stage
values. Z_g and Z_h are constant 0-1 matrices, so at a sample point every
entry of `A Z_h B + C` lies in F_2. Each of the 64 entries contributes
seven F_2 equations, one per high bit of GF(256). The solution set for
Z_h is an affine subspace of `M_8(F_2)`, and Z_g is an F_2-affine function
of Z_h because each summand `A_ia B_bj` is included or not according to a
bit of Z_h, and the low bit of a field sum is the sum of the low bits.

Every polynomial solution lies in the affine space cut out by both sample
points. The census solves that system for every word whose pure product
matches the target at both points, and for all 21 gap pairs. There are
159,984 pure hits at the first point. All 159,984 also match at the second
point. Of the 159,984 * 21 gap pairs, 568,752 systems are consistent.

On every consistent system the free variables split into independent
components of size at most 7: two variables are joined when they occur
together in a row of Z_h or of Z_g, and the program aborts if a row's
variables fall into two components or a component has more than seven
variables. Each row is therefore fixed by exactly one component. The
search assigns components one at a time and prunes a branch when the rows
already fixed have rank sum at least 8. A subset of rows cannot have
larger rank than the whole matrix, so any completion of rank sum at most 7
survives every prune. The search reports no such completion. The minimum
over a space that contains every legal pair is therefore at least 8, and
no legal pair has rank sum 6 or 7.

The same search, restricted to the first diagonal resolution on all three
stages, was compared with an unpruned enumeration of every affine space of
dimension at most 16. The two procedures agree, including the control gaps,
whose unpruned minimum is exactly 8.

## 5. The rank-8 control

Use the same diagonal resolution on every stage, run the two halves of
each stage together, and insert the `COMMUTING.md` thin maps after stage 0
and after stage 2. The first map is the identity between the core and
leaves 0 and 1. The second is the identity between the core and leaf 2.
Each has rank 4. The product in `F_2[D_0, D_1, D_2, e] / (e^2)` equals the
target. Replacing the first thin map by the identity misses the target.
Exchanging the two thin maps also misses the target. This is an exact
polynomial identity, not a specialization.

## 6. What was not run

No native caller, Lean proof, Docker replay, `make frontier6030-verify`,
or selected-frontier replay was run. The GF(256) screen is exhaustive for
this finite contract; it is not a proof assistant certificate. Profiles
with three or more thin maps, with block entries outside F_2, or with
three or more full calls in a stage were not searched. The g=13, q=8 and
g=31, q=26 profiles are untouched.

## Credit

The contract, the rank floor, and the commuting construction are from
PR #5747 (Ali Romman), including the predecessor statements in PR #5673,
PR #5631, and PR #5617. The one-map question closed in the open census
PR #6922 is re-checked here at the two sample points. Prepared by
unpaidmoon with substantial Cursor Grok assistance. Independent human
review and a proof-assistant proof are unclaimed. Apache-2.0.
