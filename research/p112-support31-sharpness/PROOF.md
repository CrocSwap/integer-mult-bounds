# Common support thirty is sharp for the P112 shortening contract

Let P be the 112 E8 root lines outside the fixed orthogonal frame
`{e_0+e_1,e_0-e_1,...,e_6+e_7,e_6-e_7}`. For rational representatives
r_t, over a characteristic-zero field K define

```
C = { (<r_t,h>)_t : h in K^8 }.
```

The support-thirty theorem of Nick Petalas/[PR3205](https://github.com/CrocSwap/integer-mult-bounds/pull/3205)
states that collectively independent pieces `a_1,...,a_k,q_0,...,q_5`
with `|union supp(a_j)|<=30` and `|supp(q_i)|<=20` have
`dim(span(a_j,q_i) intersect C)<=4`. PR3207 replaces its root-frame
census with an analytic proof. Both leave the thirty-one-cut equality as
a relaxation, without an actual independent-piece construction.

**New result.** The same assertion is false with thirty-one in place of
thirty. The following rational witness has five small pieces and six endpoints,
all eleven pieces independent, common small support exactly 31, all endpoint
supports exactly twenty, and code-intersection dimension exactly five.
Consequently thirty is the largest integer common-support bound in this
general contract, conditional only on the cited support-thirty theorem for
the lower side of that sharpness statement. The counterexample itself needs
no root-direction classification, mixed-edge census or Weyl-chamber theorem.

## Literal coordinates and construction

Use doubled root representatives. Enumerate all vectors with two entries
`+/-2` and all others zero, and all vectors with eight entries `+/-1` and
an even number of negative entries. Identify signs by taking the
lexicographically larger of r and -r. Remove the eight doubled frame roots
and sort the remaining 112 tuples in ascending lexicographic order.
All indices below are zero based. Changing representatives rescales code
coordinates and does not change this support statement.

Let H be the following five doubled roots, with h_0=0:

```
h_1 = (0, 0, 0, 0, 2, 0,-2, 0)
h_2 = (2, 0, 0, 0, 0, 0,-2, 0)
h_3 = (2, 0, 0, 0, 2, 0, 0, 0)
h_4 = (1,-1,-1, 1, 1, 1,-1,-1)
h_5 = (1,-1,-1, 1, 1,-1,-1, 1).
```

Their Gram matrix has diagonal eight and off-diagonal four, so they are
independent. Put `c_i(t)=dot(r_t,h_i)/4`, with `c_0=0`. These are integral
codewords in C, because the code is unchanged by a common rational scaling.
Take the common cut set

```
S = {0,3,5,6,7,8,23,38,44,45,46,47,48,49,50,51,
     53,58,62,74,85,87,88,90,98,101,103,105,106,108,111}.
```

For each t, let z_t be the most frequent value among
`0,c_1(t),...,c_5(t)`, choosing the smaller value in a tie. Define

```
a_i(t) = c_i(t) if t in S, otherwise 0,          i=1,...,5,
q_i(t) = 0 if t in S, otherwise c_i(t)-z_t,      i=0,...,5.
```

[WITNESS.json](WITNESS.json) contains H, S and all six literal sparse
endpoint vectors. The primary verifier reconstructs the formula and compares
every coefficient with that literal list. The independent verifier reads
the literal endpoints and checks the codeword identities directly.

The small supports have sizes `18,20,20,19,13`, and their union is S.
Each q_i has exactly twenty nonzero coordinates, all outside S.
The removed coordinates have cost histogram `2:15,3:16`; the retained
coordinates have histogram `0:3,1:36,2:42`, of total cost 120.
Here coordinate cost is six minus the largest equality class among the
six c_i evaluations. The cut selection balances the retained support as
`20+20+20+20+20+20`, rather than merely attaining the total 120.

## Independence and code intersection

The five small rows restricted to columns `0,3,5,8,38` form

```
 1 -1  1 -1  0
 1 -1  0  0  1
 0  0  1 -1  0
 1  0  1  0  1
 0 -1  0  0  0
```

Its determinant is one. The six endpoint rows restricted to columns
`1,4,9,10,13,36` form

```
 0 -1  0 -1  0  0
 0  1  0  0 -1  0
 0  0  0  0 -1  1
 0  0  0 -1  0  0
 1  0  0  0  0  0
-1  0  1  0  0  1
```

This determinant is also one. The two groups have disjoint support, so
all eleven rows are independent. For every i=1,...,5 the construction gives

```
c_i = q_i - q_0 + a_i.
```

The five c_i are independent codewords. Indeed, the h_i are independent,
and `sum_t r_t r_t^T = 112 I` makes evaluation injective. Thus T, the
span of the eleven pieces, has intersection with C of dimension at least
five. This already disproves the proposed support31 assertion.

The exact intersection dimension is five. The rational verifier computes
`rank(T)=11`, `rank(C)=8` and `rank(T+C)=14`. A separately implemented
checker reconstructs P112 by lattice membership and finds modular ranks
11,8,14 modulo the prime 101. A nonzero minor modulo a prime is a nonzero
integer minor, so these are rational lower bounds. The five explicit
independent inclusion relations give the matching upper bound
`dim(T+C)<=11+8-5=14`. No zero modulo a prime is used to infer a rational
upper bound. Therefore

```
dim(T intersect C) = 11+8-14 = 5.
```

All matrices and relations are rational. A nonzero rational determinant
remains nonzero over every characteristic-zero field, and rational row
reduction remains valid there. The same counterexample therefore works over K.

## What this settles and what remains

This closes the general support31 sharpness question left by PR3207 and
PR3205. Extending the general lemma to thirty-one common coordinates requires
an additional hypothesis. The witness is an actual collection of independent
pieces, not just a failed lower bound or an unbalanced cost relaxation.

The original TWOSIDE reduction imposes binary label-span and weight constraints.
Those are stronger than the arbitrary support hypotheses above. This result
does not satisfy the rank-six support constraint: the separately reconstructed
binary labels give endpoint support ranks `8,9,8,8,9,8` and small-support
ranks `8,8,8,9,7`, retained in [INDEPENDENT.json](INDEPENDENT.json). It
does not realize or exclude an original low-weight profile, settle C5, disprove
the decoder floor, construct a supplier, or change kappa. The support-thirty
theorem itself is cited at its exact public source; it is not re-proved here.

Credit Nick Petalas/PR3207 for the analytic frame argument and equality lead,
PR3205 for support-thirty shortening, PR3203 for the earlier support contract,
PR3188/3176 for the geometry and spectrum, and DreamingOfClouds/PR3154 for
TWOSIDE. The retained E8/P112 lineage includes joaqcoo's decoder model.
Exact sources and provenance are in [SOURCES.json](SOURCES.json). New work
is Apache-2.0. Development used substantial automated drafting, exact checks
and internal review; no human or proof-kernel review is claimed.
