# Exact monotone rank tariffs for central UT3 block calls

This scoped proof removes the concavity requirement from the common-price
version of the UT3 block-call tariff. Every nonnegative nondecreasing rank
price has an exact finite integer-partition optimum, attained on the target
roles alone. Arbitrarily many restored dirty roles cannot lower that optimum.
There is no new kappa or physical supplier claim.

The first nonconcave fixture has five central targets, rank cap four, and
complete call price `tau(d)=5+d^2` for either letter. Its exact bill is **90**,
attained by ten rank-two calls. The earlier six-call constructions cost 98
and 102 under this same hypothetical price. This comparison changes the
abstract price, not an admitted supplier's recursive profile.

This contribution is produced by Nick Petalas. New work is Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Model and exact theorem

Keep Arham Tahir's [PR1919](https://github.com/CrocSwap/integer-mult-bounds/pull/1919)
alphabet. In `G=UT3(F2)`, write

```
(u,v,z)(U,V,Z) = (u+U,v+V,z+Z+uV),
a=(1,0,0), b=(0,1,0), c=abab=(0,0,1).
```

For arbitrary finite integers `r>=w>=1` and `k>=1`, paid calls in
`M_r(F2[G])` are `D_N(g)=I+([g]+1)N`, with `g` equal to `a` or `b` and
`1<=rank_F2(N)<=k`. The binary matrix `N` need not be idempotent. Every
factor is an involution because `([g]+1)^2=0`. The full required endpoint is
`diag([c] repeated w, 1 repeated r-w)`. All inputs, including spectators,
are arbitrary. All off-diagonal coefficients must vanish, and every
spectator must return. There are no clean ancillas, central-letter calls,
free address maps, erasures or uncharged inverse calls.

Scalar invertible binary maps are free in this formal model. Conjugation
pushes them to one endpoint while preserving ranks. Augmentation forces
the remaining scalar map to be identity, as in PR1919. This is not a
statement that scalar mixing is free in a physical implementation.

Let `tau:{0,...,k}->[0,infinity)` be any nondecreasing real function with
`tau(0)=0`. Each nonzero call of either letter costs `tau(rank N)`.
Invocation overhead can be included in positive-rank entries of `tau`.
Concavity, convexity and strict positivity are unnecessary.

Set `K=min(k,w)`. Define a finite recurrence

```
F(0)=0,
F(s)=min_{1<=d<=min(K,s)} (tau(d)+F(s-d)),  1<=s<=2w.
```

**Theorem.** The exact minimum complete formal bill is `2 F(2w)`.
Every minimizing partition of `2w` into parts at most `K` gives an
attaining diagonal-projector word, with that rank list for each letter.
No extra roles are needed. The recurrence has `2w` states after its initial
state and at most `2w*K` candidate transitions.

PR1919 proves rank-volume and affine pricing. Nick Petalas's
[PR2129](https://github.com/CrocSwap/integer-mult-bounds/pull/2129) proves the
concave special case and its loopless-incidence attainment. The new step
here is a monotone truncation lemma that reduces every feasible, possibly
rank-wasteful word to an exact-mass partition without a concavity assumption.
The finite recurrence then gives an attainable optimum, including convex
and nonconvex monotone tables. No predecessor executable is imported or
replayed.

## Proof

Use the inherited PR1919 coefficient-span lemma. For either letter in any
valid word, let its positive scalar ranks be `d_1,...,d_m` and `S=sum d_i`.
That lemma gives `S>=2w`. Its zero degree-one coefficient also gives
`sum N_i=0`, so

```
d_i = rank(sum_{j!=i} N_j) <= sum_{j!=i} d_j,
thus 2 max(d_i) <= S.
```

These are necessary conditions for the original full dirty boundary, for
every finite number of roles and arbitrary noncommuting scalar matrices.
They are cited predecessor results, not new claims here.

**Monotone truncation lemma.** Suppose a positive integer list has
`S>=2w` and `2 max d_i<=S`. Then it has a coordinatewise smaller list of
nonnegative integers `e_i<=min(d_i,w)` with `sum e_i=2w`.

To prove this, first clip every entry at `w`. If no entry exceeds `w`, the
sum remains at least `2w`. If at least two exceed `w`, those two clipped
entries alone sum to `2w`. If exactly one entry `d_j` exceeds `w`, all
other entries remain unchanged and sum to at least `d_j>w`, by the rank
triangle inequality. Together with the clipped entry `w`, they still sum
to at least `2w`. Finally remove individual units until the sum is exactly
`2w`. This only decreases entries. The original cap also gives `e_i<=k`.

Monotonicity and nonnegativity imply
`sum tau(d_i)>=sum tau(e_i)>=F(2w)`, dropping zero entries. Apply this
independently to the two letters. Every valid word therefore costs at
least `2 F(2w)`. This is a relaxation of its rank lists, not an assertion
that one may truncate the original word's matrices and preserve its endpoint.

For attainment, take any minimizing partition `e_1,...,e_m`. It has total
degree `2w` and maximum at most `w`. The loopless-multigraph construction
credited to PR2129 realizes it as the degrees of a multigraph with `w`
edges. One explicit construction repeatedly joins the two largest positive
remaining degrees, then decrements both. With `h` edges remaining, the
degree sum is `2h` and maximum at most `h`. After this operation, every
unchosen degree is at most `h-1`, since three degrees of size `h` would
exceed `2h`. The two chosen degrees also become at most `h-1`. Induction
finishes the construction in exactly `w` steps.

Assign one target coordinate to each edge. For each vertex `i`, let `P_i`
be the diagonal projector onto its incident edges, extended by zero on all
spectators. Execute an `a` call and then a `b` call on each `P_i`. Every
target belongs to exactly two distinct vertices, so sees `a,b,a,b`, whose
endpoint is `c`. Every spectator sees identity. All factors are diagonal,
so there are no off-diagonal couplings. Each letter has the chosen rank
list and costs `F(2w)`. This proves the full formal endpoint and equality
in the bound for every finite `r,w,k`.

## First improvement and stopping point

At `w=5,k=4,tau(d)=5+d^2`, the minimizing per-letter ranks are
`(2,2,2,2,2)` and the complete bill is `2*5*9=90`.
The old balanced list `(4,3,3)` costs `2*(21+14+14)=98`; the old
concentrated list `(4,4,2)` costs `2*(21+21+9)=102`.
For a short exact lower certificate, each of the four allowed ranks obeys
`5+d^2 >= (9/2)d`, with equality at rank two. The inherited rank mass of
at least ten per letter therefore forces the complete price to be at least 90.
These are the displayed lists from PR1919 and PR2129, priced here, rather
than independent reconstructions of their receipts. The finite recurrence
enumerates every allowable exact-mass partition, including longer words.
The written theorem excludes cheaper words with excess rank mass as well.

This is the first verified extension. Stop here. Neither the abstract price
table nor the saving of eight establishes a physical or recursive gain.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ut3-monotone-rank-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ut3-monotone-rank-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/ut3-monotone-rank-tariff/verify.py
```

Both direct modes print `PASS_UT3_MONOTONE_RANK_TARIFF no_new_kappa` and a
generated receipt binding every package file by SHA256. They write nothing.
The exact evidence is:

- 736 formal construction fixtures, `w=1..16`, `k=1..w+3`, and four rational
  price families, with two restored dirty roles per fixture.
- 6,368 complete basis columns in an independently coded faithful regular
  action, forward and inverse, for the subdomain `w<=6,k<=w+2`.
- 766 nondecreasing integer price tables with values in `{0,1,2,3}`,
  `w=1..5,k=1..w+2`. An independent exhaustive partition iterator agrees
  with the dynamic program for every table.
- 2,010 rank lists in that domain with total mass `2w..2w+4` satisfying
  the rank triangle. Their clipped lists and prices satisfy the new lemma
  for every enumerated table for that `w,k`.
- 18 rejection controls, including each of the ten omitted calls in the
  new fixture, dirty leakage, negative/decreasing prices, invalid degree
  data, missing zero-sum constraints and domain/capacity errors.

The finite fixtures corroborate the written arbitrary-size proof. They are
not a census of all formal words, a proof-kernel certificate or a full
multiplication theorem. The standalone checker needs no Git or predecessor
files; metadata authenticates historical provenance separately.

## Scope, cost ledger and implementation bounds

The boundary, formal prices and complete rank-call bill above are proved.
Native realization, scalar mixing costs, frames, routing, hosting, physical
storage, precision/tape, recursive child-rank identification and a complete
consumer are unknown here. Unknown costs are not zero. No physical
implementation campaign, selected cold replay, Lean or Docker run is part
of this package. The selected conditional kappa remains `0.00302015`.

The task changes `bit-new-register-model` from mechanism exploration to a
formal nonlinear-pricing side result. PR1974's GL3 census and PR2027's UT4
tariff use different groups and hypotheses; this package does not claim to
escape either result or provide a native operation alphabet. The current
selected source-binding control passed; the card's historical baseline
command is replaced by `scripts/research_selected_baseline.py` as current
guidance requires. No scientific predecessor replay was used as a deliverable.

`verify.py` uses finite domains: at most 32 targets and cap 35 in the
optimizer, at most 16 targets in fixtures, and total at most 16 in partition
probes. All functions are below 60 lines. Checks use exceptions and remain
active under `-O`; no recursion, subprocess, network or file writes occur.
File reads only hash package sources. Python-managed integer,
tuple and list allocation is a Power-of-Ten rule-3 deviation, confined to
these fixed small domains, with no hard real-time allocation claim. Rule 9
has a bounded synchronous exception-control callback set. Warning-strict
normal and optimized runs are the available recurring Python diagnostics;
no separate linter is installed. Larger domains would require a fresh
capacity/diagnostic review rather than removal of these limits.

## Open next questions

- Can different nonproportional monotone prices for `a` and `b` attain both
  independent partition optima simultaneously? The separate lower bounds
  follow, but the construction here uses one shared degree list. First find
  a pair of tables with incompatible minimizing degree lists and write a
  complete alternating-incidence word or an obstruction. Attainability is
  the unresolved step.
- Can an actual native interface realize the ten-call rank-two fixture
  more cheaply than its six-call comparator? First price both whole
  boundaries with scalar work, frames, setup, restoration, hosting and
  precision. A native realization and the connection between scalar rank
  and recursive child rank are missing; the abstract saving cannot supply
  them.

## Sources, overlap and credit

Scientific base is canonical main
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
`SOURCES.json` pins the retained PR1919 and PR2129 READMEs as provenance.
Credit Arham Tahir for PR1919's rank cap, affine bill and nonlinear-pricing
gap; steph4n-gh/PR1573, Arham Tahir/PR1589, Hanson Sun/PR1607 and Josie
Elliston/PR1792 for the coefficient/rank and model lineage; and Nick
Petalas/PR2129 for the concave tariff and loopless-incidence attainment.
Their credit and source files are unchanged.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133304)
records the new question. Entry overlap covered 365 open PRs and 3,817
Discussion records, paginated at 21:44 UTC on 2026-10-22. Local notes were
sparse, so distinctive searches also read all matching main-branch READMEs
through Git and live merged-PR searches. The last-hour handoff posts from
this account and all UT3 candidate PR titles/bodies were checked. Closed
diffs, arbitrary nested files and unpublished work remain outside this
coverage. No novelty guarantee follows from a lack of matches.
