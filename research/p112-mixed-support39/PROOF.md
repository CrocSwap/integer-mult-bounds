# Mixed-rank P112 shortening through common support 39

Use the fixed 112 nonframe E8 root lines and nine-bit labels of
`research/p112-root-simplex-exclusion/geometry.py`. Over any characteristic-zero
field K, let C be the evaluation code `c_h(t) = r_t dot h`, with `h in K^8`.
The binary support rank of a vector is the F2 rank of the labels at its nonzero
coordinates. Let pi_S delete one common coordinate set S.

**Theorem.** If `|S| <= 39` and three residual vectors q_1,q_2,q_3 have
binary support ranks at most 5,5,6, respectively, then

```
dim_K(pi_S(C) intersect span_K(q_1,q_2,q_3)) <= 1.
```

The vectors may be dependent and have arbitrary coefficients. Their rank
constraints apply only outside S. The theorem increases the sufficient cut
allowance in PR3267 from 38 to 39. It asserts no sharpness or actual caller.

## Pinned premises

The proof and receipt retained from pending PR3267 at
`008f042859a5183d1323228a68aa1038f8d7718a` provide these premises:

1. In an E6 normal A2 plane the live evaluation union has at least 78 sites.
   For a rank-five piece its total support M and its singleton sites J in
   that union satisfy `M+J <= 22`. For a rank-six piece, `M+J <= 32`.
   These bounds include arbitrary binary support spaces and coefficients.
2. A D6 normal plane is spanned by orthogonal root lines. Among all 3,780
   such planes, the live-union histogram is
   `82:448, 84:2688, 85:448, 86:168, 88:28`. Each of the 448 minimum planes
   has two large projective fibers of 29 live sites. Their rank-six support
   capacity is 18. Each of the other two fibers has at most 12 sites.

These are mathematical dependencies, not consequences of authenticating their
receipts. Their earlier A2 and 896 live-axis censuses are not rerun here.
The proof and receipt from pending PR3269 at
`ebe02d33157dc6c6d3b35df204e4a39242b7429e` give the global binary support
capacities 12 and 20 for ranks five and six on these exact labels. Its signed
quadratic-character proof replaces the older global census dependency. No
unpublished sibling result is used.

The standard real Weyl-chamber theorem remains a written dependency. The new
finite replay rechecks the parabolic threshold at 29 perpendicular live roots,
the actual orthogonal-plane union histogram, the four fiber sizes on every
minimum plane, and the new arithmetic. It does not formalize the chamber
theorem or independently prove the inherited capacity statements.

## Normalize a putative two-dimensional intersection

Suppose two independent restricted codewords belong to the piece span. Choose
lifts c_h,c_k and write their full live support union as U. Since outside S
their supports are contained in the three piece supports,

```
|U| <= |S| + 12 + 12 + 20 <= 83.
```

The lifts h,k are independent over K, since their restrictions are independent.
At least `112-83=29` live root lines are perpendicular to both. Their rational
span Z has rank at most six. This follows from characteristic-zero invariance
of the rank of a rational matrix. Every full E8 root in Z is also perpendicular
to h,k. Choose a generic real vector perpendicular to Z which avoids every
root hyperplane not containing that real subspace. Its perpendicular roots
are exactly the roots in Z. Move that vector into a closed Weyl chamber.

The resulting perpendicular root system is parabolic. All rank-at-most-five
parabolics have at most 20 root lines. Of the 28 six-node parabolics, only
D6 and E6 have at least 29, with 30 and 36 lines, respectively. The replay
checks these counts and their normal planes. Thus Z has rank six and h,k
span the scalar extension of a rational normal plane, of type D6 or E6.
Replacing h,k by a rational basis of this plane preserves the full union U.
This reasoning requires no ordering on K.

## The E6 branch still has a strict incidence gap

Let `N = |U minus S|`. Express the two restricted codewords by a fixed 2-by-3
coefficient matrix A applied to the q_i. A site of U outside S at which only
q_i is nonzero lies in the projective evaluation fiber of column i of A.
A zero column has no such site. This assertion holds for coefficients in K:
the evaluation pairs use a rational basis, so any nonempty such class is a
rational projective fiber.

Let M_i be each piece's total residual support and J_i count its singleton
sites in U outside S. A union site with multiple incidences has at least two.
Consequently the inherited joint bounds imply

```
78 = 2*(78-39) <= 2*N <= sum_i(M_i+J_i) <= 22+22+32 = 76.
```

This is impossible. Support outside U and cancellations cannot defeat the
inequality. They can only add to M_i without adding singleton sites.

## Count exclusive coordinates in the D6 branch

Here the inherited live-union histogram and `|U|<=83` force `|U|=82`.
Thus `N >= 82-39 = 43`, and the normal plane is one of the 448 minimum planes.

Let B_i be the support of q_i outside S. Define

```
E = (U minus S) minus (B_1 union B_2).
```

Every coordinate of E has q_3 nonzero and both other pieces zero, because the
chosen evaluation pair is nonzero there. Thus E consists of singleton sites
for q_3 in ONE projective fiber of its fixed coefficient column. If that
column is zero, E is empty. Otherwise a small fiber has at most 12 sites,
and a large live fiber meets a binary-rank-at-most-six support in at most 18
sites. Therefore `|E| <= 18`. Now use the set covering inequality

```
N <= |B_1| + |B_2| + |E| <= 12+12+18 = 42.
```

This contradicts `N>=43`. Unlike PR3267's equality argument at cut38, this
argument allows overlaps between all three supports, partial binary closures,
piece support outside U, and cancellations. It does not assert that the whole
rank-six piece lies in one fiber. Only its exclusive sites E do.

Both branches are impossible, proving the theorem over every K of
characteristic zero.

## Limits and the next boundary

At cut40 the two displayed contradictions become equalities, `76<=76` and
`42<=42`. The verifier retains this as a losing counting control. It is not
a P112 counterexample or a sharpness witness. An abstract disjoint set cover
of sizes 12,12,18 attains the latter number, but need not satisfy root labels,
binary ranks or the evaluation equations.

This is a sufficient shortening theorem, not a complete C5 reduction, decoder
floor, physical supplier, restoration program, consumer invoice, all-size
multiplication theorem or new kappa. The global capacity proof, A2 joint and
D6 fiber capacities and Weyl geometry have the explicit dependencies above.
There is no independent human or proof-kernel verification.

Credit Nick Petalas's PR3267/3260/3262/3269 and retained root-simplex geometry,
DreamingOfClouds/PR3154 for the TWOSIDE motivation, and the E8/P112 lineage
including joaqcoo. The new contribution is the exclusive-coordinate argument
and its cut39 consequence. Frozen predecessors and the selected result remain
unchanged.
