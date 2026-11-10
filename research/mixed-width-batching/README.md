# Exact chronological batching with compatible width menus

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
For a finite menu of compatible completed supplier widths at each chronological
cut, [PROOF.md](PROOF.md) gives the exact least common replication, constructive
invocation partitions and a proved finite search bound. Each cut finishes
independently. No new kappa or physical supplier is claimed.

The first strict improvement is an unbounded family. Two cuts containing N
and N+1 jobs, with the same menu {N,N+1}, need replication exactly one. Choosing
one menu width for both cuts needs replication at least N, with equality for
width N. Thus the menu reduces parent productive width by the exact factor N
for every N>=2. Within one cut, widths {4,7} can serve eleven jobs with one
invocation of each program, also at replication one.

The changed premise is the menu of completed programs. Mihir Srivastava /
mihir-s-05's [PR4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507)
provides the chronological batch contract and single-width LCM theorem.
Nick Petalas's PR4892 and recent PR6612 keep one prescribed width per rank;
their library-minimality and homogeneous-width results do not optimize this
menu policy. Their results are cited, without replay or audit. Classical
Apéry sets, shortest paths and gcd/LCM arithmetic retain their credit.

## Exact procedure

For a menu W, divide by d=gcd(W), put m=min(W/d), and compute the least
representable normalized size A_r in every residue r modulo m. A total z is
feasible exactly when d divides z and z/d>=A_((z/d) mod m). Attaining
coefficient vectors and all residue-edge inequalities certify that table.

For batches (W_j,q_j), define

    C_j = max_r A_(j,r)-m_j+1,
    L = lcm_j d_j/gcd(d_j,q_j),
    h_j = L q_j/d_j,
    T = max(1, max_j ceil(C_j/h_j)).

The answer is L times the first t in 1,...,T for which every batch passes its
residue test at h_j t. Formula (3) in the proof returns literal whole-program
counts. Singleton menus reduce exactly to the earlier LCM policy. Replacing
each menu by its gcd is insufficient: {4,7} cannot serve a single job until
replication four. Pooling two separate one-job cuts remains forbidden.

## Evidence and reproduction

Use CPython 3.12 and its standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/mixed-width-batching/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/mixed-width-batching/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mixed-width-batching
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/mixed-width-batching --check-source-history --check-modes
```

Other hosts may substitute their CPython 3.12 path. Expected markers are
PASS_MIXED_WIDTH_BATCHING, PASS_REGISTERED_RESEARCH_PACKAGE and
PASS_RESEARCH_COMMIT_BYTES. The standalone verifier writes nothing and prints
a generated receipt bound to all seven package files by SHA256.

The finite checks cover all 175 menus of one through three distinct widths in
1..10, with 44,975 membership comparisons against a separate total-size dynamic
program. Exhaustive positive-integer search agrees on all 6,264 declared batch
systems: 1,400 one-cut, 3,136 two-cut and 1,728 three-cut systems. This oracle
uses neither the residue tables nor the replication formula.

For N=2..24, literal menu invocations and the best single-width comparator
execute 10,718 bank triples in total. Each complete output includes the unchanged
dirty coordinate, and every chronological cut is checked. A synthetic complete
linear bill has identical normalized cost. Sixteen invalid boundaries, six
residue-certificate corruptions, gcd/pooling controls and five capacity fixtures
also pass. The {63,64} conductor is 3906; 3905 rejects and 3906 admits.

These finite domains corroborate the written theorem. They are not exhaustive
over its unbounded input parameters. Independent human and formal proof-kernel
review are unclaimed. Hosted CI is reported separately in the PR body.

## Scope and limits

The theorem optimizes a fixed invocation policy under specified compatible
menus. A physical application must actually supply at least two useful widths
with compatible arbitrary-input, frame, ownership and return contracts. This
package supplies no such native menu. Widths generated only by making disjoint
copies of one smallest program cannot yield the displayed improvement.

Normalized cost is preserved only when each menu member's complete charged cost
is proportional to its width with a common coefficient. Unequal costs and fixed
per-invocation overheads need separate accounting. Routing, storage extent,
native adaptation, precision/tape, stock, the uniform compiler, analytic recovery
and all five selected framework assumptions remain separate. The literal shear
programs are synthetic interface examples, not selected native suppliers.

No selected scientific replay, Lean or Docker build is run or required by this
package. No all-size multiplication theorem, practical speedup, new kappa or
selected-frontier change follows from smaller replication.

The independent-moment card is explicitly changed from invoice verification to
this compiler-width side result. Scientific base is canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8, selected PR6030.
The selected binding-only positive control passed. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19376781)
preceded substantive work. Live PRs, recent account contributions, Discussions,
local reservations, distinctive main/merged searches and the cached overlap
inventory were inspected. Sparse local notes, arbitrary diffs and unpublished
work remain limits of that coordination check.

## Open next questions

- Can an actual recursive supplier supply two nondividing completed widths with
  matching return contracts and a favorable complete cost? Start with one rank
  and two exact source-bound programs. Their physical compatibility and all
  invocation overheads are the missing evidence.
- When menu members have different complete per-job costs, what width/cost
  frontier is attainable at each cut? Start with a finite priced menu and retain
  the residue feasibility certificates. Equal normalized cost is essential to
  the preservation result here; no priced-menu optimum is claimed.

## Executable bounds

The reusable module accepts at most eight cuts, eight widths per menu, widths
1..64 and multiplicities 1..4096. Residue Dijkstra settles at most 64 vertices;
the replication scan has at most 3969 iterations. Integer partition totals are
below 2^80. Every function is shorter than sixty physical lines. Explicit
checks remain active under optimized Python. There is no recursion, network,
subprocess or generated code. The scientific checker imports no predecessor
program. The only callbacks are the fixed Dijkstra comparison and bounded
rejection controls. Python allocation is a managed-runtime deviation from fixed
storage, bounded by the declared domains. Package hash reads are capped at
256 KiB per file. Warning-strict normal/optimized checks and source inspection
provide diagnostics; no proof-kernel or independent static-analysis result is
claimed.

Credit also Jacob Alan Sussman for integer compilation, zxv for chronological
forest flows, codyw912 for adaptive batching, and Cinna Davis and Ryanson Jonathan
for the retained native/flow lineage. Predecessor bytes and credit are unchanged.
