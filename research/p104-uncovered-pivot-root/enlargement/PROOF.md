# Ninety enlarged masks: exact carrier prices and complete exclusion

This extends the minimal-mask result by changing the masks while keeping the
literal 18-site uncovered-pivot query word and native invoice fixed. It is a
finite theorem for the 90 masks below, not a classification of all enlargements.
Geometry is over Q and therefore C; no finite-characteristic transfer is claimed.
Pending #6858 prices 81 central dense masks on the different 9|9 chain root
with three thin queries. The 90 cases here change the one-thin-query,
18-field uncovered-pivot root. Its results are context, not an imported proof
or an inference that either finite family covers the other.

## 1. Exactly which masks change

Use the root in `../PROOF.md` at L=18, pivot p=8. Its fields are A and F_i for
i in {0,...,17} except 8. Choose integers `0<=kL<=8` and `0<=kR<=9`.
Starting from the minimal masks:

- Add F_(8-kL),...,F_7 to every strict right-site mask.
- Add F_9,...,F_(8+kR) to every strict left-site mask.
- Leave the pivot mask equal to the full 18-field space.

Empty ranges are empty. The vectors x_i,y_i and the single thin query do not
change. Every enlarged mask contains its former mask. There are exactly
9 times 10=90 cases, including the original (0,0).

The arbitrary-D identity remains valid. For a left site, the entire query
prefix is supported on its old mask. For a right site, the scalar endpoint
expresses that prefix as minus the inverse of a query product supported on its
old mask. Thus each prefix acts as a scalar on the complement of the old mask
and preserves every enlarged mask. Equivalently its coordinate projector
commutes with the prefix and suffix. The stage-factor proof in the parent
package applies unchanged. The checker independently verifies all 1,620
prefix/projector commutations.

Each of the 18 coordinate fields remains an independent whole target. If field
c occurs in m_c enlarged masks, its rank is `8m_c+1`. Each full site i has exact
idle rank demand `d_i=|M_i|-2`, because its native main interface still has rank
two. One thin rank-one query is mandatory. The root surplus remains

`sum_c (8m_c+1) - 1 - 8 sum_i d_i = 305`.

Adding the unchanged native helper/request census from #6833 over 18 calls and
104 ports gives complete surplus 760 in every case.

## 2. Exact capacity of a proposed job's site set

Use the same one-independent-field whole-idle contract as the parent accounting
proof. A job may cover any nonempty subset J of full sites, including
nonconsecutive sites. It is paid at rank `8|J|`. Between covered sites its line
and dual may be transported by the literal query word. Ordinary source frames
are data independent, or have a nondegenerate specialization at D=1,S=-1.
No arbitrary rank packing or spectral restriction of an input is permitted.

Set D=1,S=-1 and write U_i for the query prefix strictly before site i.
Transport each candidate projector to one common chart by U_i. Put

`alpha_i = y_i U_i`, `beta_i = U_i^(-1) x_i`.

Both primal and dual support reduce to the coordinate mask M_i because U_i
commutes with its coordinate projector, as proved above. For a site set J,
let C be the intersection of its masks and n_C its dimension. Let A_J have
rows alpha_i restricted to C, and B_J have rows beta_i restricted to C.
The allowed primal vectors are `K=ker A_J`; allowed dual vectors are
`L=ker B_J`. A nonzero rank-one idempotent with the required annihilations exists
exactly when the pairing of L and K has positive rank.

That rank is

`cap(J) = n_C - rank A_J - rank B_J + rank(A_J B_J^T)`.

Indeed, the radical of the pairing on K is `K intersect row(B_J)`. Its dimension
is `rank B_J - rank(A_J B_J^T)`, by rank-nullity on the row space of B_J.
Subtract this from `dim K=n_C-rank A_J`. Choosing dual bases of the resulting
nondegenerate pairing realizes exactly cap(J) mutually dual directions.

For the exclusion it is sufficient to retain every J with cap(J)>0; mutual
compatibility of different jobs and arbitrary-D transparency can only remove
possibilities. Adding sites shrinks both allowed subspaces, so pairing rank
cannot increase. The verifier exhaustively enumerates the positive-capacity
subsets by a recursion that stops as soon as capacity is zero. Its rank
calculations use integer row operations. They do not assume an interval shape
or global orthogonality between jobs at disjoint times.

## 3. The site-price certificates

Fix `kappa_0=.00337180`, `t=1-kappa_0` and `Q=10^18`.
For each of the 90 masks, `DUALS.json` supplies 18 nonnegative integers w_i.
The verifier checks, for every enumerated feasible site set J,

`sum_(i in J) w_i <= floor(Q (8|J|)^t)`.

The floor is obtained from the lower endpoint of an exact rational power
interval, so the displayed inequality certifies

`sum_(i in J) w_i/Q <= (8|J|)^t`.

Sum this inequality over any actual whole-idle cover. Site i occurs exactly
d_i times. Its total paid idle cost is therefore at least

`sum_i d_i w_i/Q`.

This lower bound is valid even though the certificate ignores capacities
between different jobs and allows many nonrealizable combinations. No solver
or rounding heuristic is part of the proof: the committed integers and all
of their inequalities are rechecked. A deterministic greedy search found the
prices, but the replay does not rerun or trust that search.

The complete upper margin is formed from every native helper target, every
native request, all 18 main targets, the thin query, and this proved idle lower
bound. Additional ordinary adapters and compiler/precision costs are
optimistically free. Every case has a strictly negative exact upper margin.
The largest is at (kL,kR)=(7,8), and is at most

`-0.210890121535325573`.

This is a whole-construction margin, with 104 ports and all 18 native calls;
it is not a root entropy proxy or a per-port number. The exact scaled integers
and case counts are in `RESULT.json`.

## 4. A uniform derivative prevents re-entry on an explicit interval

The benchmark certificate alone does not assert failure at every larger kappa.
Here is the separate uniform bound used for that statement.

For any cover with job lengths m_j, let
`v_l = number of sites i with d_i>=l`. The vector v majorizes the sorted lengths:
any k jobs cover at most `sum_i min(k,d_i)` incidences, and total incidence is
fixed. Since `f(x)=x log x` is convex with f(0)=0,

`sum_j (8m_j) log(8m_j) <= sum_l (8v_l) log(8v_l)`.

Throughout `0<=kappa<=.01`, every paid derivative contribution obeys
`r^(1-kappa) log r <= r log r`; every negative target derivative contribution
obeys `-r^(1-kappa) log r <= -r^(1-.01) log r`. The thin rank-one cost has
zero derivative. Thus an upper bound, simultaneously for every actual cover,
is obtained by native paid entropy and root paid entropy on v at kappa=0,
minus all native and root target derivatives at kappa=.01.

The checker evaluates this with rational lower/upper log and power bounds.
Every one of the 90 derivative bounds is less than -166817. Hence no actual
cover can cross back into a favorable margin on [.00337180,.01]. A cover
chosen differently for another kappa is also excluded: each individual cover
has the same benchmark bound and its own derivative satisfies this uniform
bound.

This is a raw caller exclusion through .01, beyond the currently admitted
BIT saving .0034. It supplies no improved BIT stock. The package does not claim failure for arbitrarily large kappa, changed native profiles,
other mask patterns, data-dependent singular frames, altered queries, or a
different whole-target/whole-idle compiler interface.

## 5. Reproduction and independence

Run from the integrated package:

```
python3 -I -B research/p104-uncovered-pivot-root/enlargement/verify.py
```

A standalone review copy accepts `--root-package PATH`. The root-construction
and interval modules are SHA256-pinned and loaded from their exact source bytes,
without Python bytecode-cache reuse. The native census is independently
source-authenticated by the retained accounting module.

The proof-relevant artifacts are the 90 sets of integer prices in `DUALS.json`,
the exact query/mask definitions, and the rational checks. `RESULT.json` binds
every per-case count, upper margin and derivative bound. Optimized Python does
not disable checks. Controls reject a price above a singleton tariff and a
singleton-only tariff assigned to a feasible multi-site merge; explicit pairing
examples require both native annihilation conditions and the AB^T correction
in the capacity formula.

Prepared for @CubeJerry with substantial OpenAI GPT-6 assistance. The root and
native source lineage is the parent package's. The capacity calculation and
pricing were independently reviewed by different workers, with separately
implemented nullspace and invoice checks. This is exact finite verification
plus the displayed proofs, not a formal proof-kernel or compiler-admission
claim. No kappa or framework assumption is changed.
