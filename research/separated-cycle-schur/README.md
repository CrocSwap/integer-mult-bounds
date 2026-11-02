# Separated circular Schur complements retain bounded bandwidth

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. Eliminating
any number of arcs from a circular radius-w band retains linear
half-bandwidth at most `min(M-1,4w-2)`, provided consecutive eliminated arcs
are separated by at least w surviving vertices. Here M is the survivor count.
An explicit order attains this upper bound or better.

For the full negative host and t>=3 surviving runs of exactly w vertices,
the exact minimum over every simultaneous row/column order is `3w-1`.
Thus the earlier one-arc constant `2w` fails for separated multiple arcs
as soon as w>=2. This answers a bounded part of Open next question 2 in
[PR4879](https://github.com/CrocSwap/integer-mult-bounds/pull/4879).
The sharp constant for arbitrary separated run lengths remains open.
There is no new kappa or selected-frontier change.

## Statement and boundary

Let n>=3 and `1<=w<=floor(n/2)`. Label the circle `0,...,n-1`.
Let H be any matrix over a field with

```text
H[i,j]=0 whenever min(|i-j|,n-|i-j|)>w.
```

Partition the circle into t>=2 nonempty eliminated arcs A_i and t nonempty
surviving runs R_i in alternating order. Assume `|R_i|>=w` for every i.
Assume H_AA is invertible, and put `S=H_RR-H_RA H_AA^(-1) H_AR`.
Its half-bandwidth in an order p is the largest `|p(i)-p(j)|` over nonzero
off-diagonal entries, or zero if there are none. The upper bound requires
neither symmetry nor signs.

For the exact lower bound, use real `H=I-E`, where E has zero diagonal,
strictly positive entries at every circular distance 1 through w, zero
entries outside that band, and every row sum less than one. Require t>=3
and `|R_i|=w` for all i. Eliminated arc lengths may be any positive integers.
Equal couplings and symmetry are unnecessary.

## Proof of the uniform upper bound

The surviving run between two eliminated arcs has at least w vertices.
An edge of circular length at most w cannot jump across that entire run:
its two eliminated endpoints would be at distance at least w+1 in that
direction. Thus H_AA is block diagonal by eliminated arcs. Its inverse
has the same blocks. Invertibility of H_AA implies invertibility of each
arc block; no individual scalar-pivot assumption is needed.

Each arc A_i touches only the last w vertices of the preceding surviving
run and the first w vertices of the following surviving run. Call their
union B_i. No other surviving run is within distance w of A_i. Therefore
the Schur support is contained in the original survivor edges together
with the clique on each B_i. Cancellation can remove edges but cannot add
edges outside this set. This is the separated-component use of the
classical fill-path principle.

Compress the survivors to a circle of M positions in inherited cyclic
order. An original edge has circular distance at most w after compression.
Each B_i consists of 2w consecutive surviving positions, so its clique
edges have circular distance at most `2w-1`. Consequently every Schur edge
has compressed circular distance at most `r=2w-1`.

Use the linear order

```text
0, M-1, 1, M-2, 2, M-3, ...
```

Each vertex occurs once. Every ordinary M-cycle edge spans at most two
positions, including the closing edge. A pair at circular distance d is
joined by a cycle path of d edges, so the triangle inequality bounds its
position difference by 2d. This proves half-bandwidth at most `4w-2`.
The trivial bound M-1 gives `min(M-1,4w-2)`.

The order is independent of the number and lengths of the eliminated arcs.
It proves the requested O(w) bound under an explicit separation rule.
The upper constant is not asserted optimal.

## Exact periodic family

For the full negative host, each eliminated block has inverse
`(I-E_i)^(-1)=sum_(k>=0) E_i^k`. The row-sum hypothesis makes this series
converge. Its entries are strictly positive because an eliminated arc is
connected by positive nearest-neighbor edges in both directions. Every
pair in B_i therefore receives a strictly negative Schur update. Existing
off-diagonal entries are already negative and cannot cancel it. This is
James Reed's credited sign/support argument from PR4289.

If every surviving run has exactly w vertices, each run is a clique.
Each eliminated arc fills the complete join of its adjacent surviving
runs. There are no edges between nonadjacent runs: an original route
across a full intervening run and two nonempty eliminated arcs is longer
than w, while each Schur block touches only its adjacent runs. Thus the
exact support replaces every vertex of the t-cycle by a w-clique and each
cycle edge by a complete join. At t=3 it is the complete graph on 3w vertices.

Every vertex has degree `(w-1)+w+w=3w-1`. In a linear order of
half-bandwidth b, the first vertex has at most b neighbors. Hence
`b>=3w-1`. For equality, fold the t-cycle of whole runs as above, keeping
each run contiguous. Adjacent runs are at most two block positions apart,
so their scalar vertices span at most `2w+(w-1)=3w-1` positions. Internal
edges span at most w-1. This proves the exact optimum for every t>=3,w>=1.

For example, take n=9,w=2, eliminate `{2,5,8}`, and use diagonal 1 and
entries `-1/8` at circular distances 1 and 2. The six survivors have complete
Schur support and optimal half-bandwidth five. A bound of four fails in
every order. The exact rational checks include this example.

## Evidence and reproduction

The self-contained verifier imports no predecessor executable. It checks
all 9,451 separated multiple-arc layouts with `4<=n<=12` and
`1<=w<=min(3,floor(n/2))`. Literal vertex elimination agrees with the arc
neighborhood formula and the folded upper bound on every layout. Independent
exact rational Schur elimination checks the full negative host on all 936
of those layouts with n<=9.

It constructs 144 periodic layouts with `3<=t<=20`, `1<=w<=8`, and eliminated
arc lengths `1+(i mod 3)`. Literal elimination gives the predicted
clique-cycle support; the block order and degree lower bound agree. All
87,270 vertex permutations are evaluated across the eight periodic cases
with at most eight survivors. Ten invalid inputs and five semantic controls
exercise separation, the false one-arc constant, the order, missing couplings
and a zero scalar pivot. These are the enumerated domains; the written
argument supplies the all-size proof.

From the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/separated-cycle-schur/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -I -W error -B research/separated-cycle-schur/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/separated-cycle-schur
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/separated-cycle-schur --check-source-history
```

Any CPython 3.12 installation with the standard library can replace that
interpreter path. Expected marker: `PASS_SEPARATED_CYCLE_SCHUR`. Each run
prints a fresh receipt bound by SHA256 to all five package files. It writes
no files, and every check remains active under optimization. The generic
runner also authenticates the pinned provenance in Git.

## Scope and implementation constraints

This is a structural side result relevant to the precision/tape boundary
ordering obligation. It does not bind the order to an actual Gaussian
caller, price movement of its right-hand sides, or discharge a selected
framework assumption. Signed or missing couplings retain the upper bound
but need not have the periodic family's exact support. Unseparated layouts,
the sharp general constant, inverse norms, rounded coefficient generation,
restoration, native/supplier admission and the full multiplication theorem
remain outside scope. Selected cold replay, Lean and Docker are unrun.
Independent human and formal proof-kernel review are unclaimed.

The verifier has no recursion or generated code. Loops are bounded by fixed
case ranges, n<=256, or permutations of at most eight vertices. Rational
matrices have size at most nine. Functions remain below 60 lines. Python's
managed integer and Fraction arithmetic is a fixed-allocation deviation.
Each graph has at most 256 bitset rows; rational elimination has
two 9-by-9 matrices; permutations are streamed. Fixed finite inputs bound
integer sizes and allocation lifetime. Larger domains require fresh
capacity analysis. Warning-strict normal/optimized execution and repository
metadata/publication checks are the available diagnostics. No separate
static-analysis dependency is introduced.

## Open next questions

1. What is the sharp uniform constant for arbitrary separated run lengths?
   The lower family needs `3w-1`, while the order gives `4w-2`. First classify
   small width-two support graphs and test orders that split a surviving
   run. This matters for tighter boundary storage. A matching all-layout
   bound or a larger lower example is missing.
2. Can one actual circular Gaussian boundary solve use this order within
   its paid movement allowance? First specify both permutations, all
   right-hand sides, storage and restoration in a literal caller. Algebraic
   bandwidth alone does not price these operations. The physical
   producer/consumer and complete movement invoice are missing.

## Credit and overlap

Nick Petalas's PR4879 supplies the multiple-arc question and earlier one-arc
theorem. James Reed / jwr404's PR4286/4289 supply the circular sign/support
argument. unpaidmoon's PR4373 and Ryanson Jonathan's PR4407 supply linear
separated-carve/component context. Cinna Davis's PR4100 supplies the Gaussian
boundary motivation and retained framework lineage. These are cited
predecessors, not replay or audit deliverables. Folding, clique replacement
of a cycle, fill paths and minimum-degree bandwidth bounds are classical;
no literature-wide priority is claimed for them. The new step is the
separated multiple-arc theorem and its sharp periodic Schur family.

SOURCES.json pins the question and sign/support texts at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Priority revision 8 and selected
PR6030 were read; the baseline returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361577)
preceded the verifier. Live open PRs, recent account work, handoff claims,
local reservations, main README searches and merged keyword searches were
checked. The cached scan covered all 369 open PRs and 6,286 Discussion
records, but only 104 of 8,917 main-tree note paths. Direct main README
searches supplemented it. Unpublished work and arbitrary diffs remain
outside that coverage.
