# Mixed 5,6,6 shortening through one common cut of 32

Fix the 112 nonframe E8 root lines and leading-one nine-bit labels in the
source-pinned root-simplex geometry. For a characteristic-zero field K, let
`C = {(r_t dot h)_t : h in K^8}`. A vector's binary support rank is the F2
rank of the labels at its nonzero coordinates. Write pi_S for deletion of
ONE common coordinate set S.

**Theorem, conditional on the inherited premises below.** If `|S| <= 32`
and three arbitrary residual vectors q_1,q_2,q_3 have binary support ranks
at most 5,6,6, respectively, then

```
dim_K(pi_S(C) intersect span_K(q_1,q_2,q_3)) <= 1.
```

The pieces may be dependent and have arbitrary coefficients. Their rank
constraints apply only outside S. This improves the available uniform
rank-six cut29 contract for this mixed profile. It claims neither sharpness
nor a new literal caller exclusion.

## Inherited premises

PR3295 at `4cff8128f0f9ea1e61515b95ddbb884366e9362c` supplies the following
mathematical inputs. Its verbatim proof and two finite receipts are retained
in vendor/ and bound by PREDECESSORS.json. Authentication of those bytes does
not prove the inputs; their censuses and transport checks are not rerun here.

1. Global P112 support capacities for binary ranks five and six are 12 and
   20. PR3295 credits the PR3278/3267/3260/3262/3269 chain for its premises.
2. For an E6-normal A2 plane the live evaluation union has at least 78
   sites. A rank-five piece's total support M plus its singleton sites J in
   any one projective fiber is at most 22. For rank six it is at most 32.
3. Among the D6 normal planes spanned by orthogonal roots, the live-union
   sizes are 82,84,85,86,88. At sizes 82 and 84 the four live projective
   fiber sizes are respectively 29,29,12,12 and 31,31,11,11. The two large
   fibers are the two coordinate axes of the orthogonal-root basis.
4. In a full E8 D6 axis fiber, ten labels of a rank-at-most-five support
   force its entire full-root support closure into that same axis. Eighteen
   labels do the same for rank at most six. Each small full D6 fiber has
   rank-five capacity eight and at most twelve roots in total.
5. The checked parabolic counts and normal-root facts, together with the
   standard real Weyl-chamber theorem, give the normalization below.

The concentration thresholds are PR3295's new finite contribution. They
apply to arbitrary ambient binary spaces, including support subsets rather
than full closures. Its reflection/label transport covers every orthogonal
root pair. The present theorem composes these inputs with a new common-cut
and two-axis covering argument. It does not independently validate them.

## Normalize a hypothetical two-dimensional intersection

Choose two independent restricted codewords in the piece span and lift
them to c_h,c_k in C. Extend each q_i by zero on S and let U be the full
live support union of c_h,c_k. The support capacities give

```
|U| <= |S| + 12 + 20 + 20 <= 84.
```

The lifts are independent. At least 28 live root lines are perpendicular
to both. Their rational span Z has rank at most six, since the rank of a
rational matrix is unchanged by a characteristic-zero field extension.
Every full E8 root in Z is also perpendicular to h,k. A generic real vector
perpendicular to Z avoids all root hyperplanes that do not contain Z's
orthogonal complement. Its perpendicular roots are precisely the roots in Z.
Move that real vector into a closed Weyl chamber.

The resulting root subsystem is parabolic. The inherited counts rule out
rank at most five, whose parabolics have at most 20 root lines. Among the
rank-six parabolics, only D6 and E6 have at least 28 lines. Thus Z has rank
six and h,k span the scalar extension of a rational normal plane of one of
these two types. Replace h,k by a rational basis without changing U.
This argument uses no ordering on K.

Let R = U minus S and N = |R|. A fixed 2-by-3 matrix A expresses the two
restricted codewords as combinations of the pieces. At a site in R where
only q_i is nonzero, the nonzero evaluation pair is proportional to column
i of A. Such singleton sites belong to ONE projective fiber. A zero column
has no singleton sites. A nonempty fiber is rational because the evaluation
pair uses the rational normal-plane basis, even when A has coefficients in K.

## The E6 incidence gap

Let M_i count the whole residual support of q_i, including sites outside U,
and J_i its singleton sites in R. Counting each nonsingleton site at least
twice gives

```
2N <= sum_i(M_i+J_i) <= 22+32+32 = 86.
2N >= 2*(78-32) = 92.
```

This contradiction permits arbitrary overlaps and cancellations.

## D6 near equality forces concentration

Only the D6 live-union sizes 82 and 84 are at most 84. Set
`c=(12,20,20)` and `D=52-N`. At each t in R let k_t count the nonzero pieces.
Every k_t is at least one. The exact identity

```
D = sum_i(c_i-M_i)
    + (piece incidences outside R)
    + sum_{t in R}(k_t-1)
```

has nonnegative terms. Each piece is zero on S, so the outside-R incidences
are outside U. For a fixed i, its nonsingleton incidences in R number at
most `sum(k_t-1)`. Consequently

```
c_i-J_i = (c_i-M_i) + its outside-R incidences
          + its nonsingleton incidences in R
        <= D.
```

If |U|=82, N>=50 and D<=2. If |U|=84, N>=52 and D<=0.
In either case

```
J_1 >= 10,  J_2 >= 18,  J_3 >= 18.
```

The rank-five piece cannot use a small fiber, whose rank-five capacity is
eight. Neither rank-six piece can use a small fiber with at most twelve
roots. Their singleton fibers are therefore large axes. The inherited
concentration lemma forces each entire piece support into its assigned axis.
This conclusion concerns the full support closure, so discarding coordinates
and allowing cancellations introduces no exception.

## Two axes cannot cover enough retained sites

There are three pieces and two disjoint axes. One axis receives at most one
piece. Its covered sites number at most 20, the largest piece capacity.
The other axis contributes at most its live size L. This also bounds
assignments with an empty axis. Thus

```
|U|=82: N <= 29+20 = 49 < 50 <= N.
|U|=84: N <= 31+20 = 51 < 52 <= N.
```

These contradictions prove the theorem. The argument never assumes
independence of the pieces, disjoint supports before concentration, a common
coefficient, or a small-piece realization of S.

## Scope and the next boundary

The new direct replay checks the common-cut incidence arithmetic, all eight
axis assignments per D6 type, and a separate enumeration of 91,728 integer
occupancy relaxations. These are checks of the proof's new finite inequalities.
They do not re-prove the inherited capacities, concentration, transport or
Weyl theorem. At cut33 the same uniform concentration step is no longer
forced in the union82 branch. The losing control is not a counterexample
and does not establish sharpness.

PR3295 already proves the six-piece 4,5,5,5,6,6 theorem and excludes the
historical 4,5^3,6^6 caller. That result gets full credit. Its premise is
different from this universal arbitrary common-cut statement. No new caller
count, full C5, global decoder floor, native program, physical execution,
restoration, consumer bill, supplier admission, multiplication theorem or
kappa follows here. Human and proof-kernel review are unrun.

Credit Nick Petalas/PR3295 and the PR3278/3267/3260/3262/3269 source chain,
DreamingOfClouds/PR3154 for the reduction motivation, and the retained E8/P112
lineage including joaqcoo. Frozen predecessors and selected science are unchanged.
