# Five-term asymmetric C5 decoders still cost at least 20

Every strict scalar fit on each of the 23 physical C5 masks needs at least
five rank-one terms. If it uses exactly five terms, **each term costs at least
four**, even with unequal source and target supports and arbitrary rational,
real or complex coefficients. Cost 20 is attained. A decoder costing at most
19 must therefore use at least six terms.

This answers the minimum-term part of the asymmetric question left by
[PR3232](https://github.com/CrocSwap/integer-mult-bounds/pull/3232), exact head
`9d75ed2b5bc9bb8cb19f205724f978b02be732cb`. Its arbitrary-term Gram theorem
already proves cost 20 when the factors agree. The new result permits unequal
factors but requires the minimum term count. It does not settle arbitrary
asymmetric decompositions with six or more terms, or improve kappa.

The scalar minimum of five is already PR2484's C5 lemma. It is re-proved
below to expose its equality structure. The new claim is the individual
complete-plane tariff bound for every five-term asymmetric factorization.

## Exact contract

Index five complete binary planes cyclically by `i in Z/5`. Each plane `E_i`
is nondegenerate of dimension two. Adjacent planes are orthogonal; all other
distinct plane pairs are nonorthogonal. Each plane has two scalar ports.
Over `F = Q, R or C`, let `K` be a `10 x 10` matrix with

```text
K_ii = I_2,
K_ij = 0_2 for nonadjacent distinct i,j,
K_ij arbitrary for adjacent i,j.
```

The free blocks need not be symmetric. Consider an exact factorization
`K = A B^T` with `A,B` of size `10 x m`. A nonzero coefficient of a rank-one
term can be absorbed into its column of `B`. Zero terms can be discarded.
All transposes are ordinary transposes, including over the complex numbers.

For term `t`, let `S_t` and `T_t` be the plane indices on which column `t` of
`A` and `B`, respectively, is nonzero. Charge

```text
rho_t = rank_F2 pairing(sum_{i in S_t} E_i, sum_{j in T_t} E_j).
```

Touching one scalar port charges its whole plane. Rank is the rank of the
binary bilinear form on these complete spans, not a scalar matrix rank or
the number of scalar entries. The theorem says `m >= 5`, and `m = 5` implies
`rho_t >= 4` for every term.

## Proof

Write `A_i,B_i` for the two-row blocks. In the scalar coefficient space
`F^m`, put `U_i = row(A_i)` and `W_i = row(B_i)`, using its nondegenerate
coordinate bilinear form. The identity block `A_i B_i^T = I_2` makes both
spaces two-dimensional and makes their mutual pairing perfect. The zero
blocks imply `U_i` is orthogonal to `W_j` for nonadjacent `i,j`.

**1. Nonadjacent source spaces are disjoint.** If
`x in U_i intersect U_j` for nonadjacent `i,j`, then `x` annihilates `W_i`
because it lies in `U_j`. Perfect pairing on `U_i x W_i` forces `x = 0`.

**2. At least five terms are necessary.** The adjacent spaces `U_i,U_(i+1)`
both annihilate `W_(i+3)`, so their sum has dimension at most `m-2`. Thus

```text
dim(U_i intersect U_(i+1)) >= 6-m.
```

Inside `U_i`, its intersections with its two neighbors are disjoint, since
those neighbors are nonadjacent. Their dimensions therefore sum to at most
two. The displayed lower bound gives `2 >= 2(6-m)`, hence `m >= 5`.
This is a scalar dimension argument and makes no binary-tariff inference.

**3. At five terms, the source spaces are sums of five edge lines.** Now set
`m = 5` and `H_i = U_i intersect U_(i+1)`. Each `H_i` has dimension at least
one by step 2. The two neighboring intersections are disjoint inside a
two-dimensional space, so both have dimension exactly one and

```text
U_i = H_(i-1) direct-sum H_i.
```

The line `H_i` annihilates `W_j` unless `j = i` or `j = i+1`: for any other
`j`, at least one of `i,i+1` is nonadjacent to `j`.

Choose a nonzero row `h_i` in every `H_i`. These five rows are independent.
Indeed, in a relation `sum_i c_i h_i = 0`, pairing with all of `W_j` sees only
`c_(j-1) h_(j-1) + c_j h_j`, which lies in `U_j`. Perfect pairing forces this
sum to vanish. Its two summands belong to distinct lines, so both coefficients
vanish. This holds for every `j`.

Consequently the `h_i` form a basis of `F^5`. Let `g_i` be its dual row basis,
so `h_i g_j^T = delta_ij`. Since `W_j` annihilates every `h_i` except its two
incident edge lines and has dimension two, it is exactly

```text
W_j = span(g_(j-1), g_j).
```

Each two-row block `A_j` is an invertible change of basis on
`(h_(j-1),h_j)`; each `B_j` is an invertible change of basis on
`(g_(j-1),g_j)`. Hence column `t` of `A_j` vanishes precisely when both
`h_(j-1)[t]` and `h_j[t]` vanish, and the analogous statement holds for `B_j`
and the `g` rows.

**4. Every term contains one full orthogonal pair on both sides.** The two
basis matrices `H,G`, with rows `h_i,g_i`, satisfy `H G^T = I_5`. They are
square and invertible, so `H^T G = I_5` too. Its `t`-th diagonal entry gives

```text
sum_i h_i[t] g_i[t] = 1.
```

At least one product in this sum is nonzero. For that `i`, both source planes
`i,i+1` occur in term `t`, because both incident `A` blocks contain the
nonzero coordinate of `h_i`. Both target planes also occur, by the same
argument with `g_i`. No sign, positivity or conjugation argument is used.

The orthogonal, nondegenerate planes `E_i,E_(i+1)` have a nondegenerate
four-dimensional direct sum. Both complete term spans contain this sum, so
their restricted pairing has a nonsingular `4 x 4` submatrix. Therefore
`rho_t >= 4`. Summing over five terms proves cost at least 20.

**Attainment.** Assign each plane's two scalar ports to its two incident
cycle edges. For each edge take one vector with coefficient one on its two
assigned ports, and use its outer square. These five vectors partition the
ten scalar ports. Their sum fits the strict mask and each term costs four.
The verifier supplies this witness on every physical cycle.

## Why the term-count hypothesis matters

Split one attaining term `v v^T`, where `v = e_a+e_b` and the two ports belong
to adjacent planes, into

```text
e_a v^T + e_b v^T.
```

This gives a valid six-term asymmetric fit of the same matrix and total cost
20. Each new term costs two and contains no common adjacent plane pair on
both sides. Thus the proof's individual-term conclusion is false at six
terms. This is a boundary control, not a counterexample to a possible
arbitrary-term cost-20 theorem. No search over six-term decompositions was run.

## Evidence and reproduction

The proof above is a written characteristic-zero argument. Its universal
coverage comes from the dimension and dual-basis steps, not finite sampling.
The exact executable evidence checks the literal 56-plane matching, all 23
induced cycles, attaining fits, rational unequal-support changes of basis and
the six-term boundary. An independent test method enumerates chordless walks
and uses dense binary elimination rather than the verifier's bit pivots.

```sh
python3.12 -B scripts/research_package.py --package research/c5-rank-tight-asymmetric
```

The registered replay is read-only and uses the standard library. See
[RESULT.json](RESULT.json), [SOURCES.json](SOURCES.json), [TASK.json](TASK.json)
and [VERIFY.json](VERIFY.json) for exact fixtures, base/source identities,
scope and bounded commands. Scientific base is canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[The canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19003021)
records the claim and current evidence status.

The registered CPython 3.12.15 replay passes on macOS arm64, with 11 control
groups including all 23,552 rectangular tariff comparisons. A separate worker
reviewed the equality classification and dual-basis implication and independently
passed both direct scripts read-only on CPython 3.12.15. No blocking finding
was reported. Ruff checks `E,F,B,I,UP,C4,SIM`, formatting and metadata/source
pins pass. This review is internal, not independent human or formal-kernel
verification.

The submission refresh fetched the same canonical main and checked unchanged
guidance and geometry. Its snapshot covers 289 open PRs and 2,069 Discussion
records, with complete pagination and no refresh warning, at 2026-10-17
19:10:38 and 19:11:07 UTC, respectively. The targeted cached `C5 asymmetric`
query reports its offline freshness limits. PR3232's exact head was rechecked
live. Closed PR bodies and omitted local packages are not exhaustively searched;
the retained PR2484 and related C5 packages were inspected separately.

This is local algebraic progress. It supplies no arbitrary-term asymmetric
floor, global cost-224 statement, native program, restoration, frame, hosting,
precision, all-size or selected cold-chain proof. The selected result is
unchanged. Finite tests and internal review are separate from human or
proof-assistant verification.

## Open next questions

Can a decomposition with at least six terms cost at most 19 on one physical
C5? Start with a fully explicit rational fitting matrix and factorization,
then recompute every complete-span pairing tariff. The split control shows
why termwise charge four cannot be imposed in this larger class. Arbitrary
coefficients and supports remain an unbounded problem here.

A favorable local identity would still need its complete native and consumer
bill. Do not infer a supplier saving from term count or this local tariff.
No dependent construction expansion is proposed by this package.

## Credit and implementation notes

PR3232, thakrarsagar, supplies the arbitrary-coefficient Gram floor and the
explicit unequal-span handoff. Tekalign's PR2782 supplies the physical C5s,
complete-plane tariff and earlier finite-menu checks. Arham Tahir's PR2879
supplies the related principal-block rank method. Credit Sagar Thakrar/PR2484
for the named C5 core and existing scalar minimum of five,
Cinna Davis/PR1825 for the matching, Adam Gall/PR1889
for the strict scalar mask, ctoth and Philippe Van Velzen for the port/full-space
accounting, and the retained selected PR1094/E8 geometry lineage.

The new step is the edge-line classification at five scalar terms and its
dual-basis transfer to the complete-plane tariff. Apache-2.0.

Power-of-ten rule 3 has a Python managed-runtime deviation in `verify.py` and
`test_verify.py`: exact fractions and JSON allocate dynamically. Fixed geometry
sizes, matrices of at most ten rows and eight fixture columns, and bounded
enumerations bound live data. No recursive traversal, dynamic evaluation,
background processes or retained generated outputs are used. A future input
format beyond these fixed fixtures must add explicit size and bit-length
limits before lifting those bounds. Diagnostics and rejection controls are
part of the registered replay.
