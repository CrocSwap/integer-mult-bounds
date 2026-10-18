# Sharp concave rank tariffs for UT3 block calls

For the formal rank-capped UT3 alphabet of [Arham Tahir's
PR1919](https://github.com/CrocSwap/integer-mult-bounds/pull/1919), this note
completes the nonlinear pricing question left in its
[Limits section](../ut3-rank-bounded-block-calls/README.md#limits).
Every nondecreasing concave rank tariff has a sharp closed-form optimum,
attained with no workspace preparation and with arbitrary dirty roles restored.
This is a scoped theorem about an abstract interface. It supplies no physical
bit supplier, recursive child-rank identification or new kappa.

## Model and result

Keep PR1919's alphabet unchanged. Let `G = UT3(F2)`, written as

`(u,v,z)(U,V,Z) = (u+U, v+V, z+Z+uV)`.

The paid letters are `a=(1,0,0)`, `b=(0,1,0)`; the central target is
`c=abab=(0,0,1)`. In `M_r(F2[G])`, a paid call is

`D_N(g) = I + ([g]+1) N`, with `g in {a,b}` and `1 <= rank_F2(N) <= k`.

Here `r >= w >= 1` and `k >= 1` are arbitrary finite integers. The scalar
matrix `N` need not be idempotent. The required **whole dirty boundary** is
`diag([c] repeated w, 1 repeated r-w)`. Extra roles have arbitrary inputs
and must be restored. Free scalar basis changes can be normalized into `N`
as in the predecessor; the remaining scalar map is identity by augmentation.
There are no clean ancillas, free address maps, central-letter calls, COPY,
ERASE or uncharged inverse calls. Each permitted factor is an involution
because `([g]+1)^2=0`.

Price a complete letter-g call of rank d at `alpha_g + f_g(d)`, where
`alpha_g >= 0` and `f_g:[0,infinity)->[0,infinity)` is nondecreasing and
concave, with `f_g(0)=0`. The two letters may have different prices.
Let

```
K = min(k,w)
q, rho = divmod(2w,K)
t = q + [rho > 0]
```

**Theorem.** The exact minimum complete abstract bill is

```
t(alpha_a + alpha_b)
  + q(f_a(K) + f_b(K)) + f_a(rho) + f_b(rho).
```

A single word simultaneously attains both letters' rank costs, both minimum
invocation counts and both rank-volume floors. Its per-letter rank list is
`K` repeated q times, followed by rho when rho is positive. It needs no extra
roles. Extending it by identity on any dirty workspace preserves the endpoint.
The theorem also applies to increasing discrete concave tariffs after their
piecewise-linear interpolation.

For `f_g(d)=beta_g*d^p`, `0<p<=1`, `beta_g>=0`, the formula gives the sharp
power tariff. This includes an abstract moment-shaped `p=1-a` price, but scalar
coupling rank d is **not** an admitted supplier's recursive child rank.

## Lower bound

The following rank-volume argument is inherited from PR1919 and its
PR1573/1589/1607 lineage. It is included to make the new cost implication
self-contained.

Use the necessary-condition quotient
`F2<X,Y>/(X^2,Y^2, all monomials of length >=3)`.
The group homomorphism sends

`(u,v,z)` to `1+uX+vY+zXY+(z+uv)YX`.

Put `Q=diag(I_w,0)`. The target's X and Y coefficients are zero, and its XY
and YX coefficients both equal Q. For one letter, factor each rank-d_i scalar
matrix as `N_i=U_i V_i`, with d_i inner coordinates. Concatenate the U_i
horizontally and the V_i vertically, giving U,V with inner dimension
`S=sum d_i`. The degree-one coefficient gives `UV=sum N_i=0`. The XY
coefficient puts `col(Q)` inside `col(U)`; the YX coefficient puts `row(Q)`
inside `row(V)`. Therefore

`S >= rank(U)+rank(V) >= 2w`.

The same argument applies to the other letter. This is valid for arbitrary
noncommuting scalar matrices and any restored dirty workspace. In addition,
`sum N_i=0` implies

`d_i = rank(sum_{j!=i} N_j) <= sum_{j!=i} d_j`, hence `d_i <= S/2`.

Each letter has at least two nonzero calls.

If `k<=w`, reduce the nonnegative d_i to total mass 2w, allowing zeros and
keeping the cap k. Monotonicity cannot increase the cost. For fixed total mass
and cap, moving mass from a smaller interior entry to a larger one cannot
increase a concave sum. Continue until at most one entry is strictly between
zero and k. The resulting list is q copies of k and the remainder rho.
Thus `sum f_g(d_i) >= q*f_g(k)+f_g(rho)`. Independently, the call count is
at least `ceil(2w/k)=t`.

If `k>w`, each d_i is at most S/2. Concavity and `f_g(0)=0` give the chord
inequality

`f_g(d_i) >= (2d_i/S)*f_g(S/2)`.

Adding yields `sum f_g(d_i) >= 2*f_g(S/2) >= 2*f_g(w)`. At least two calls
are required. This is exactly the formula with `K=w`, q=2 and rho=0.
Summing the two letter bounds and their nonnegative overheads proves the
claimed complete lower bill. No search extrapolation is used.

## Attaining word

View the desired per-letter ranks as degrees of a loopless multigraph with
w edges. The degree list has sum 2w and maximum at most w. Pair the two largest
remaining positive degrees, assign the next target coordinate to that pair,
and decrement them. Repeat w times. This always terminates: with 2h remaining
stubs and maximum at most h, the chosen two degrees remain at most h-1 after
decrementing. Any unchosen degree was already at most h-1, since three degrees
of size h would exceed 2h. The invariant holds until all stubs disappear.

For each vertex j, let P_j be the diagonal projector onto the coordinates
assigned to its incident edges, extended by zero on all dirty roles. Execute
one a call and one b call on each P_j. Each target coordinate belongs to
exactly two distinct vertices, so its formal word is `abab=c`; inverse order
also gives c. Every dirty coordinate sees identity. Projector ranks are the
prescribed degrees, all at most k. This proves attainment for every finite
r,w,k, including caps larger than w.

The multigraph is only an incidence description; no physical graph routing
or unpriced preparation is part of the construction.

## First priced fixture and delta from the predecessor

For `w=5,k=4`, PR1919's balanced cyclic formula gives ranks `(4,3,3)` per
letter. The concentrating construction gives `(4,4,2)`. One explicit support
list is `{0,1,2,3}`, `{0,1,2,4}`, `{3,4}`. Both words use six calls and twenty
rank units across both letters.

For the exact strictly concave price `f(d)=d/(d+1)`, the per-letter bills are
`23/10` and `34/15`, so the complete two-letter saving is **1/15**. Any fixed
per-letter invocation overhead cancels in this comparison. For `d^p` with
`0<p<1`, strict concavity likewise makes the new rank list cheaper. No floating
point is used to accept this fixture.

PR1919 already proves the optimal invocation count and affine rank bill.
This note does not claim those as new. It replaces balanced incidence with
an extreme-degree incidence and proves optimality for concave costs, including
words that spend additional rank mass. It does not assert that the predecessor
balanced word is optimal under nonlinear pricing. That predecessor explicitly
leaves nonlinear pricing outside its scope.

## Evidence and reproduction

From the repository root, using Python 3.12 and only the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/ut3-concave-rank-tariff
```

Standalone replay, also supporting read-only source exports:

```sh
python3.12 -I -B research/ut3-concave-rank-tariff/verify.py
python3.12 -I -O -B research/ut3-concave-rank-tariff/verify.py
python3.12 -I -B research/ut3-concave-rank-tariff/test_verify.py
```

[RESULT.json](RESULT.json) records 624 fixtures with `w=1..32`, `k=1..w+3`
and two restored dirty roles. Exact formal diagonal group-algebra endpoints
agree with a separately implemented faithful regular action using literal
binary address matrices on all 114,176 basis columns, in both directions.
Eleven meaningful controls reject omissions, undercharging, a smaller cap,
an unpaid letter, dirty-role action and a rank-preserving wrong incidence.

The verifier also exhausts 2,492 rank lists in the favorable scalar-rank
relaxation for `w=1..5,k=1..7`, mass `2w..2w+4`. Exact rational prices and
all integer hinge tariffs `min(d,c)` agree with the formula. Controls show
why the zero-sum condition and concavity are necessary. This finite check
corroborates, but does not replace, the arbitrary-size written proof.
The separate tests compare the partition iterator with an independent
count-vector oracle, check the group law against literal multiplication,
and exercise optimized, relocated and corrupted-receipt CLI paths.

## Limits

This is a formal nonabelian alphabet with hypothetical complete prices.
Physical realization, rational-frame conversion, H1-H5 admission, hosting,
precision/tape, supplier source binding, selected cold replay, outer analytic
transfer and proof-kernel formalization were not performed. No change to the
selected frontier follows. Increasing convex, decreasing or negative tariffs
are outside the theorem. No literature-priority or independent human-review
claim is made.

The computational fixture bounds do not restrict the theorem. The rank-volume
lemma and the uniform incidence proof supply the arbitrary-size statements.
The change is confined to a new package; predecessor sources remain untouched.

## Open next questions

Can a physical interface realize this alphabet with a genuinely concave
complete rank bill? Compare the five-target cap-four `(4,4,2)` boundary with
`(4,3,3)` after pricing frame changes, source preparation, dispatch, hosting,
restoration and precision. The blocker is a legal physical realization and a
justified connection between scalar coupling rank and recursive child size.
Without it, the abstract saving cannot enter the selected moment.

For mixed central and noncentral target roles, can one derive an attainable
concave tariff rather than only a rank-volume floor? Start from the retained
[UT3 mixed-target tariffs](../ut3-mixed-target-tariffs/README.md) and determine
whether a single incidence word can attain the separate coefficient bounds.
The central-only zero-sum hypothesis used above no longer holds for both
letters. Structured questions are in [TASK.json](TASK.json).

## Sources and credit

Base canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4. [SOURCES.json](SOURCES.json) pins the predecessor and historical
selected-record/catalogue provenance. [TASK.json](TASK.json) declares the
scope change from alphabet exploration to this nonlinear pricing side result.
The entry overlap search covered 379 open PRs and 789 Discussion records.
The final refresh at 2026-10-14 20:12 UTC covered 381 open PRs and 789
Discussion records with complete pagination and no warnings. Canonical main
and PR1919's head were unchanged. No matching nonlinear tariff was found;
this is not a novelty guarantee. No Discussion claim was
posted because the session's engineering-mode communication rule forbids it.

Credit Arham Tahir/PR1919 at `f5610483cab0b5547be778a4e8983faf78aefa69`
for the rank-capped alphabet, rank-volume bound, balanced incidence construction
and explicit nonlinear-pricing gap. Retain steph4n-gh/PR1573, Arham Tahir/PR1589,
Hanson Sun/PR1607 and Josie Elliston/PR1792 for the predecessor's rank-one,
nilpotent, coefficient-span and rank-decomposition lineage. Related concave
histogram comparisons in
[CubeJerry's Steinberg fan package](../bit589-steinberg-fan-seed06/README.md)
concern a different fixed-word rational-frame problem, not this UT3 tariff.
No predecessor implementation is imported. New work is Apache-2.0.

### Implementation bounds

The checker has no recursion, network, subprocesses or writes. Fixture loops
have explicit bounds: w<=32, at most 128 calls and 34 roles, with eight group
basis elements. The receipt read is capped at 4,096 bytes. The partition probe
has total<=14 and cap<=7; its iterative work bound is `2**total`. Each function
is shorter than 60 lines. Input and receipt checks use exceptions and remain
active under `-O`; the two assertions only repeat degree invariants already
checked at construction exit. The count-vector test oracle has total<=11
and cap<=6.

Power-of-Ten rules 8 and 9 use the standard unittest discovery/dispatch
mechanism in `test_verify.py`, with exactly six named tests and synchronous
lifetimes. No runtime-generated code or unbounded callback targets are added.
Tests exercise every target; replacing framework dispatch would require a
dedicated non-unittest runner if an indirect-call-free environment needed it.

Power-of-Ten rule 3 has a managed-runtime deviation in `verify.py` and
`test_verify.py`: Python allocates tuples, integers and temporary collections.
The stated domains bound all live algorithmic collections; the partition
stack has depth at most 14 and at most 98 pending siblings. Tests use temporary
directories with scoped cleanup and bounded CLI timeouts. Runtime allocation
internals were not instrumented. A native fixed-capacity implementation would
be required before applying this checker in an allocation-prohibited context.
Rule 10 uses Python development-mode diagnostics, normal/optimized tests and
AST syntax/function-length checks. No Python static type checker or linter is
configured for this standalone package; repository-wide tooling changes are
outside this scoped mathematical contribution.
