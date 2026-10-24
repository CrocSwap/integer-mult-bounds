# Four frames suffice for concave three-contact subspace pricing

This contribution is produced by Nick Petalas. It gives a **scoped proof with
finite corroboration**, with no new kappa or native supplier claim.

For three fixed subspaces, the exact minimum sum of nondecreasing concave
rank-distance prices is attained at one of four explicit frames. The fourth
frame is the sum of the three pairwise intersections. Thus this local search
needs no enumeration of all intermediate subspaces, at any ambient dimension
or over any field. The theorem also respects a common mandatory subspace and
receiver cap when the entire interval between them is allowed.

The distance is exactly the schematic charge declared in Chrisbryan17's
[PR #2844](https://github.com/CrocSwap/integer-mult-bounds/pull/2844),
`research/p104-signed-mixed-carrier-bank/README.md`. That package leaves physical
lowering separate from its frame experiment. Cinna Davis's
[PR #4447](https://github.com/CrocSwap/integer-mult-bounds/pull/4447),
`research/missing-join-frame/README.md`, supplies the distinct motivation to
close contact catalogues under spans and intersections. Neither predecessor
executable or numerical result is rechecked here. The new result is an exact
local optimization rule in the explicitly stated distance model. The metric
median construction and elementary concavity argument are standard ingredients;
no claim of literature priority for those ingredients is made.

## Exact contract and formula

Let V be a finite-dimensional vector space over any field. Fix three subspaces
A, B, C of V, and allow every subspace X of V. Define

```
d(U,W) = dim(U) + dim(W) - 2 dim(U intersect W).
M = (A intersect B) + (B intersect C) + (C intersect A).
F(X) = phi_A(d(X,A)) + phi_B(d(X,B)) + phi_C(d(X,C)).
```

Each phi is a nonnegative, nondecreasing concave function on `[0, dim V]`.
The functions can differ, so arbitrary nonnegative contact weights are covered.
Discrete tariffs are allowed when their nonnegative successive increments are
nonincreasing; use their piecewise linear interpolation. An additive constant
in any tariff has no effect on the minimizing frame. In particular, the result
covers `phi_i(r)=w_i*r^t` for any `w_i>=0` and `0<t<=1`.

The exact answer is

```
min_X F(X) = min(F(A), F(B), F(C), F(M)).
```

Set `a=d(A,B)`, `b=d(B,C)`, `c=d(C,A)`, and

```
alpha = (a+c-b)/2,
beta  = (a+b-c)/2,
gamma = (b+c-a)/2.
```

The four price vectors are respectively
`(0,a,c)`, `(a,0,b)`, `(c,b,0)` and `(alpha,beta,gamma)`.
Only the pairwise intersection dimensions are needed to find the minimum
price. Constructing an attaining fourth frame requires ordinary subspace sums
and intersections. The theorem asserts existence of a minimizing candidate;
other minimizing frames can exist.

More generally, suppose every contact lies in a common interval
`L <= A,B,C <= H`, and all frames `L <= X <= H` are allowed. The same formula
holds, using exactly the same four frames and distances. It does not cover an
arbitrary catalogue or additional restrictions on X.

## Proof

First, d is a metric. For subspaces U,W,Z, both `U intersect W` and
`W intersect Z` lie in W, and their intersection lies in `U intersect Z`.
The dimension identity therefore gives

```
dim(U intersect W) + dim(W intersect Z)
    <= dim(W) + dim(U intersect Z),
d(U,Z) <= d(U,W) + d(W,Z).
```

Next, M is a metric median of A,B,C. It contains `A intersect B` and is the sum
of subspaces lying in A or B. Hence

```
M = (M intersect A) + (M intersect B),
(M intersect A) intersect (M intersect B) = A intersect B.
```

The dimension identity yields `d(A,M)+d(M,B)=d(A,B)`. The same reasoning applies
to the other two pairs. Solving these three equalities gives
`d(M,A)=alpha`, `d(M,B)=beta`, `d(M,C)=gamma`. These radii are nonnegative
integers, including in characteristic two. No division in the coefficient
field is involved.

For any competing X, write its three distances as `(x,y,z)`. The triangle
inequalities give

```
x+y >= alpha+beta,
x+z >= alpha+gamma,
y+z >= beta+gamma.
```

If each coordinate is at least its median radius, monotonicity gives
`F(X)>=F(M)`. Otherwise at most one coordinate is below its radius. Suppose
`x<alpha`; the other cases follow by permuting contacts. Then `alpha>0` and

```
(x,y,z) >= (x, beta+alpha-x, gamma+alpha-x)
        = (x/alpha)*(alpha,beta,gamma)
          + (1-x/alpha)*(0,alpha+beta,alpha+gamma).
```

The inequality is coordinatewise. Monotonicity followed by concavity gives

```
F(X) >= (x/alpha)*F(M) + (1-x/alpha)*F(A)
     >= min(F(M),F(A)).
```

Thus every X costs at least the cheapest candidate. Every candidate is itself
allowed, which proves equality. For the interval version, meets and joins of
subspaces between L and H remain between L and H. All four candidates are
therefore feasible, and the same argument applies. This completes the scoped
all-field proof; the finite checks below corroborate it.

## Sharp scope boundaries

All three terminal candidates are necessary when contact tariffs may differ,
by permuting a price that places sufficient weight on one contact. The median
can also be strictly necessary. For three distinct lines in `F2^2`, the median
zero frame has distances `(1,1,1)` and each terminal has a permutation of
`(0,2,2)`. With tariff `(phi(0),phi(1),phi(2))=(0,3,5)`, the median costs 9
and every terminal costs 10. With tariff `(0,1,1)`, a terminal costs 2 and the
median costs 3. Neither a terminals-only nor a median-only rule suffices.

Concavity matters. In `F2^4`, take

```
A=span(e1,e2), B=span(e3,e4), C=span(e1+e3,e2+e4).
phi_A(r)=5*r^2, phi_B(r)=phi_C(r)=r^2.
```

Here M is zero and the cheapest of the four candidates costs 28. The frame
`span(e1)` has distance vector `(1,3,3)` and costs 23. This explicit convex
counterexample prevents extending the rule to arbitrary increasing prices.

The candidate set also depends on allowing unequal frame dimensions. If only
lines in `F2^2` are allowed, the zero median of three distinct lines is absent;
the linear-price minimum is 4 rather than the unrestricted minimum 3. These
lines are Lagrangian in the two-dimensional alternating space, so the theorem
cannot be transferred to Lagrangian-only charts by merely rescaling d.
No native Clifford tariff is identified with this schematic charge.

## Finite evidence and reproduction

From the repository root, using the standard library and CPython 3.12:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/subspace-three-contact-pricing
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/subspace-three-contact-pricing/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/subspace-three-contact-pricing/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/subspace-three-contact-pricing --check-source-history
```

The direct verifier is read-only and works without Git, network access or
predecessor files. `--emit` generates the deterministic receipt on stdout;
ordinary verification recomputes it and compares every field with
[RESULT.json](RESULT.json), including the hashes of all five other package
files. A receipt is generated from computation, never handwritten.
The metadata commands additionally check the contextual source pins in
[SOURCES.json](SOURCES.json); those sources are not runtime dependencies of
the mathematical verifier.

The RREF enumeration includes every subspace of `F2^2`, `F2^3`, `F2^4`,
`F3^2` and `F3^3`. Vector-set addition constructs joins; vector-set intersection
constructs meets. For every unordered triple, the verifier checks the proposed
median and segment domination against every possible competing frame. Ordered
triples differ only by contact permutation, and independently varying all
three tariff tables covers these permutations.

For direct optimum comparisons, tariffs have nonincreasing increments in
`{0,1,2}`. Every independent triple of such tables is tested. Equivalent
finite optimization problems with identical candidate vectors and identical
sets of attainable distance vectors are checked once. This lossless grouping
is reported explicitly, with exact transcript hashes. It is not a sampling
argument. The verifier also checks every common subspace interval in `F2^3`,
the strict candidate examples, the convex counterexample and invalid tariffs.
Across the five domains, this checks 57,361 unordered contact triples against
3,637,645 competing frames, then makes 388,002 exact optimum comparisons
after the stated signature grouping. The interval check adds 66 intervals,
1,462 contact triples and 15,802 competing frames. These are separate coverage
counts.
The written proof covers arbitrary dimensions, fields and admissible tariffs;
finite enumeration alone does not establish that universal statement.

## Limits and implementation discipline

This package supplies no new scalar word, native realization, profitable paid
consumer, compiler, ownership scheme, precision bound, physical tape cost,
supplier admission or multiplication exponent. It does not optimize a graph
with several variable frames. It does not assert that the actual native
rank of a Clifford transport equals d. Predecessor operators, source numbers
and the selected construction are cited context and are not replayed.
Independent human and formal proof-kernel review are unclaimed.

The verifier has no recursion or dynamic code loading. Every loop is bounded
by the five fixed domains, at most 67 subspaces, 81 vectors, 15 tariffs per
contact and the corresponding finite products. Receipt reads are limited to
1 MiB per file. Functions stay within 60 physical lines. Checks use explicit
exceptions and survive optimized Python. Warning-strict normal and optimized
registered replays are the available recurring diagnostics; no repository
Python static analyzer is configured for this package.

Power-of-Ten rule 3 deviation: CPython and its standard library allocate
managed objects during the exact enumeration. Replacing those allocations
requires a different runtime. The scope is this one bounded verifier;
geometry tables have at most 67 squared entries, there are at most 52,394
contact triples per domain, and all tariff checks stream over fixed finite
products. Only distinct optimization signatures are retained. Both local
modes exercise these limits. A move to larger domains must establish new
capacity bounds before changing these guards. Runtime/library allocations
are not independently instrumented or claimed allocation-free.

## Open next questions

- Can a comparable finite candidate rule handle a four-contact junction in
  this same schematic distance model? First inspect all quadruples in
  `F2^3` and identify which extra distance vectors are essential. The
  three-coordinate proof does not supply such a rule.
- Can a physical P104 frame operation realize a useful instance with these
  exact prices? First name a literal carrier, its three contacts, all allowed
  frames and a fully paid preparation/restoration word. The native realization
  gap of PR #2844 remains a blocker; this local theorem does not close it.

## Credit

The new theorem application, exact optimization reduction and checker are
produced by Nick Petalas. Credit Chrisbryan17 / PR #2844 for the declared
schematic distance and signed-carrier context; Ali Romman / PR #1125, the
PR #968 frame-pair decoder contributors and Chrisbryan17 / PR #2820 for its
retained geometry lineage; Cinna Davis / PR #4447 and PR #4440/#4441, zxv,
Jacob Alan Sussman and the retained native/controller/bit/transfer contributors
for the separate span/intersection contact motivation. Their results and
credit lines are unchanged. New material is Apache-2.0.
