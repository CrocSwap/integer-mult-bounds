# Higher-moment strictification: tensor power 150 and a smaller uniform rank

**Submission authorized by the user on 2026-10-21.**

The complete p7 mixed supplier in [PR4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416)
has productive ranks down to 5 and paid ranks up to 48. Its chronological
product, paid target completion and disjoint splitting overcome that overlap.
This package improves the charged tail estimate in that construction, then
generalizes the logarithmic compiler bound of
[PR4411](https://github.com/CrocSwap/integer-mult-bounds/pull/4411).
At the same proposed conditional **κ = 0.00268647**, the results are:

| Quantity | PR4416 | This package |
| --- | ---: | ---: |
| Chronological tensor power | 6,240 | **150** |
| Product ambient rank | `121^6240` | **`121^150`** |
| Independent productive fields before uniform compilation | `7688^6240` | **`7688^150`** |
| Maximum paid rank after splitting | `10^6240` | **`10^150`** |
| Minimum productive rank after paid completion | `11^6240` | **`15^150`** |
| Sufficient uniform ambient rank | `2^16201843136005340321` | **`2^349300000000`** |

The tensor exponent decreases by **41.6×**; the exponent of the sufficient
uniform rank decreases by about **46.38 million×**. These are comparisons of
specified finite constructions and sufficient bounds. They are not runtime
speedups, practical template sizes or corresponding estimates for every
precision/storage constant. The winning uniform word is not materialized.
The selected frontier is unchanged.

There are three connected deliverables: a general higher-moment splitting
bound, an exact smaller paid native construction, and a uniform-rank proof
compatible with the complete consumer. This is the larger scope chosen after
the H completion obstruction; no numerical measure of scientific significance
is asserted.

## 1. Boundary contract and expansion decision

Retain PR4359/PR4416's all-column native contract: a finite chronological word
computes specified transforms on distinct arbitrary productive fields; paid
positions act on the actual current physical owners. Whole-job normalizers
are restored, complete spectators are preserved, and owned centers are
initialized, retained until safe erasure and never credited as new inputs.
At every positive column multiplicity, ranks multiply by that multiplicity.
Matching only rank numbers is insufficient without these native hypotheses.

The source product algorithm runs one U copy for every productive role of V,
then substitutes V into each common chronological paid position of those U
copies. Fields may contain correlated data but have distinct physical slots.
Never combine two different paid positions of the same suspended U copy.
The targets and paid ranks are products; their moments multiply. This is a
finite chronological substitution of algorithms. Read
[the pinned product proof](vendor/p7-TENSOR.md), especially §§1–3 and 6.

After the product finishes, normalize each complete rank-K output job by its
permitted whole-job conjugation. When K<L, pay for the positive transform on
L−K disjoint axes of that same owner. No new productive input is introduced.
Split every paid job on disjoint axes, keeping its whole-job adapters around
the complete replacement. All movements, scalars and center lifetimes remain
in the expanded finite program.

| Obligation | Status in this contribution |
| --- | --- |
| Literal p7 controller identity and raw invoice | Replayed by the unchanged, credited PR4426 oracle; supplier receipt remains inherited |
| All-column native correctness, legal routes, arbitrary inputs and restoration | Explicit inherited premises, with pinned construction and receipts; no new native admission |
| Product, completion, splitting and both moment charges | Proved below; one exact finite instance certified |
| Finite integer batching, source complements and owned-bank allocation | Inherited compiler algorithm; new sufficient rank proved below |
| Nine outer rows, 54 current predicates, three guards and 63 legacy predicates | Exact arithmetic replayed at the unchanged p7 parameter point |
| Actual scalar/movement counts and full precision/stock constants | Finite algorithmic prescription retained; numerical winning-word counts not emitted |
| Analytic, fine-prime, physical tape and exact-recovery premises | Inherited conditional obligations; not discharged by moment arithmetic |

**Decision: continue this one construction.** The source already gives a
complete charged way to repair overlapping ranks. Its tail bound is loose,
so a stronger bound changes the necessary product size without inventing an
unpriced consumer. A general direct compiler for overlapping ranks remains
open; no two-sided flow is assumed here. Stop before extending the supplier
or claiming another κ without new native and consumer evidence.

## 2. Higher-moment paid-tail theorem

For a fixed raw unit, let T_s and P_s be its productive and paid rank moments,
B its productive field count, and m its ambient rank. Choose

```
0 < C < 1,  t = 1−C,
1 < c < b < m,  integer v >= 1,
u >= C,  sigma = t+u >= 1,
J = c^v,  L = b^v.
```

The bases c,b and the power v are integers, so L and J are exact integer
ranks. All moments here are finite sums over the actual rank inventory.

For any original paid rank R>J, write R=qJ+r with 0<=r<J. Its exact split
charge obeys

```
q J^t + r^t <= R J^(−C) + J^t <= 2 R J^(−C)
              <= 2 R^(t+u) J^(−u).
```

The last step uses `(R/J)^(sigma−1) >= 1`; this is why sigma must be at
least one. Keeping the original P_t^v as an overcount for all unsplit calls
gives total original-paid charge at most

```
P_t^v + 2 P_(t+u)^v / J^u.
```

For a completion D=L−K with 0<D<L, the split charge is bounded by

```
D J^(−C) + J^t < 2 L J^(−C).
```

This also covers D<J, when no full J block occurs. There are at most B^v
completions, and completion only increases the productive t-moment. Thus the
**complete** normalized paid moment is bounded by

```
alpha^v + 2 gamma_u^v + 2 delta^v,
alpha   = P_t / T_t,
gamma_u = P_(t+u) / (c^u T_t),
delta   = B b / (c^C T_t).
```

If this bound is below one, the completed finite unit has a strict t-moment
advantage and `max paid <= c^v < b^v = min target`. Positive raw rank-one
surplus is preserved: product moments multiply, completion adds equal paid
and productive rank, and splitting preserves paid rank mass. The unchanged
integer compiler therefore applies under its native hypotheses.

When alpha, gamma_u and delta are all below one, a sufficiently large finite
v exists by geometric decay. The theorem gives a sufficient construction;
it neither characterizes every favorable mixed profile nor removes padding.
PR4416's rank-one tail is exactly the endpoint u=C, sigma=1. Choosing a
higher moment changes this part of the proof without changing the raw word.

The sigma restriction matters: at `t=1/2, sigma=3/4, R=100, J=1`, actual
split charge is 100 but the falsely extended bound is
`sqrt(100) + 2*100^(3/4) < 74`. The verifier records this counterexample.

## 3. An exact p7 instance with v=150

The unchanged source-bound raw invoice is

```
T = {5:420,6:270,7:840,8:1395,9:3195,
     25:448,41:448,57:448,121:224},
P = {1:37305,2:10695,3:3360,4:1530,5:300,
     8:1464,16:448,32:448,48:448}.
```

It has B=7,688, m=121, T_1=131,723 and P_1=131,115. The source p7 controller
and fresh helpers are unchanged. The credited PR4426 oracle independently
replays all 70 literal events and derives this invoice from the source
controller and supplier receipt. This package does not claim that replay as
a new discovery or independent audit of the supplier's internal paid bill.

Take `C=0.00268648`, `c=10`, `b=15`, `u=3/10` and `v=150`. Exact rational
intervals give

| Ratio | Certified interval, shortened | Rational upper bound |
| --- | --- | --- |
| alpha | (0.999999984403907977028692329024, 0.999999984403907977028692329025) | `1−10^−8` |
| gamma_u | (0.903981539721477814868265523050, 0.903981539721477814868265523051) | `181/200` |
| delta | (0.877942785206780917722562601792, 0.877942785206780917722562601793) | `439/500` |

Bernoulli's inequality bounds alpha^150 by `1/(1+150/10^8)`. The following
is a strict comparison of rational integers, with all padding charged:

```
1/(1+150/10^8) + 2*(181/200)^150 + 2*(439/500)^150 < 1.
```

Its strict surplus is greater than **0.000000864794339252354870976549**.
The corresponding old rank-one-tail bound is greater than 2.52448, even
before adding completion. This distinguishes the changed proof step from
simply reducing v in the old certificate. The rounded new bound also fails
at v=100; no least tensor power is claimed.

The finite construction has ambient `121^150`, minimum target `15^150` and
maximum paid `10^150`. Its exact inventories are generated by product,
per-owner completion and integer division; no fractional jobs are routed.
At every positive column count the same finite algorithm uses the inherited
generator substitution, with no new independent productive credit.

## 4. Logarithmic majorants with any positive power

PR4411 states its majorant using integer q>=1 and logarithm power p=1/q.
Its proof only needs the logarithmic factor to be increasing. The same
argument works for **any real p>0**, including p>1, which is useful when
the separated unit's ambient rank m is itself large.

Assume the finite source/exit compiler in
[FINITE-PRECOMPILATION.md](vendor/FINITE-PRECOMPILATION.md). Write
`L(n)=P_n/B_n`, with ordinary base `L(n)=n` for `0<=n<m`. At n>=m its exact
integer-batch construction gives

```
L(n) = sum_s w_s L(n−s) + sum_e x_e L(e),
sum_s w_s = 1,  n/m < s <= n,
sum_e x_e e^t <= sum_s w_s s^t,
e <= r_max (n/m)^theta < n,
theta = log(r_max)/log(k_min) < 1.
```

Choose `theta < theta_bar=a/b < 1` and p>0 with

```
2^(b−a) r_max^b <= m^a,
theta_bar^p < eta = t m^(t−1),
m^(1−t) < 2^p.
```

Then **`L(n) <= n^t (1+log2(n))^p` for every integer n>=1**; define the
right side to be zero at n=0.

For 2<=n<m, the last condition gives `n^(1−t) < 2^p <= (1+log2(n))^p`;
rank one is equality. At n>=m put `A(n)=(1+log2(n))^p`. The shifted logarithm
condition gives `A(e) <= theta_bar^p A(n)` for every exit, hence

```
sum_e x_e e^t A(e) <= theta_bar^p A(n) sum_s w_s s^t.
```

For y=s/n>1/m, concavity of x^t gives
`1−(1−y)^t >= t y >= eta y^t`. Since A is increasing, the source complement
capacity obeys

```
n^t A(n) − sum_s w_s (n−s)^t A(n−s)
    >= eta A(n) sum_s w_s s^t,
```

with zero-rank complements treated separately. The strict inequality
`theta_bar^p < eta` closes strong induction. This uses no concavity of A
and introduces no unknown multiplicative constant.

This is available for every separated unit with the stated t-superpotential.
Choose rational theta_bar sufficiently close to one: since r_max<m, both
the actual theta bound and the shifted logarithm condition then hold.
Any integer

```
p > max((1−t)*log2(m), log(eta)/log(theta_bar))
```

satisfies the other two conditions. Thus the leaf-count estimate has the
general form `L(n) <= n^t (1+log2(n))^p` with an effective fixed p. At fixed
p, a target gap z−t requires a sufficient H of order
`(p/(z−t))*log(p/(z−t))`. This concerns normalized rank-one leaf counts in
the finite compiler; it does not bound full word size or physical runtime.

The compiler's integral batch replication, arbitrary original arrays,
whole-job routing and finite owned-bank allocation are unchanged. With
N=2^H and desired uniform exponent z>t, the final sufficient condition is

```
(1+H)^p < 2^((z−t)H).
```

For the new p7 unit, take `theta_bar=6/7`, `p=13`. Exact tests give

```
10^7 < 15^6,
2*(10^150)^7 <= (121^150)^6,
eta > 0.144386809622024146828684313913 > (6/7)^13,
(121^150)^C < 6.907234273066686405887998346943 < 2^13.
```

The smaller logarithmic power 12 fails the stated eta condition. Let
`z−t = 1/700000000`, exactly the uniform-saving slack already used by
PR4416's outer point. The rank **N=2^349300000000** satisfies

```
349300000001^13 < 2^499.
```

The preceding grid point H=348600000000 fails its corresponding comparison
with 2^498. This is the first successful multiple of 700,000,000 for this
majorant: the function `(z−t)H ln(2) − p ln(1+H)` is strictly convex, starts
at zero with negative derivative, and has just one positive zero. This
does not certify a minimum native program.

To separate the two contributions, retaining the older power majorant on
the new v=150 unit already gives `H0=37443877100` and
`H1=140829080288374101`. That is about a 115× reduction in the exponent
from the changed tail/rank separation alone. The logarithmic majorant then
reduces that exponent by a further factor of about 403,175.

## 5. Complete consumer and finite constants

The complex uniform saving is **376107/140000000**, approximately
0.00268647857142857. This is exactly PR4416's uniform endpoint; neither
its tested saving nor its outer parameters change. Put

```
kappa = 0.00268647,  d=(0.00268648−kappa)/7 = 1/700000000,
uniform = kappa+6d,  b_outer = kappa+5d,
a_outer = kappa+4d,  q_outer = kappa+3d,
epsilon=1−d, beta=1−3d, r0=d/10, stop=layout=d,
ordinary_BIT_saving=0.0027.
```

The checker replays the byte-pinned PR4405/PR4416 parameter ledger and
requires exact equality with all saved p7 parameters, nine rows, 54 checks
and three extra guards. It separately executes only the historical
`check_ledger.py` ledger function and its comparison constants as another
oracle: all nine rows agree and all 63 predicates remain strict. Its derived
grid/backoff is recorded explicitly; the old m=73 admission code is not run.
The minimum nine-row saving minus κ is exactly
`524529867/122500000000000000`.

Mutations close epsilon, remove layout funding, raise unfunded κ, close
the uniform gap, underfund BIT, add an old per-axis scan or make group width
equal to global dimension. Each must fail its relevant ledger.

The newly compiled word supplies its **own** finite constants. If U counts
actual raw p7 instances, allocate U distinct owned centers. Let W be the
final productive width, P the paid rank-one count, and R the full native
record/normalizer count including completion, splits and compiler routes.
As in the pinned closure argument, use

```
G = 2490856*U + 8*R,  Z = W+U,
E = 64*(Z+N+P+G+1)^3,
B_constant = P+E,  C0 = 32*N*B_constant^2.
```

Pay actual coordinate movement separately. Retain every owned center until
its creating unit erases it; centers are excluded from productive W.
The fixed-word recurrence and eventual constant absorption have the source
form, with these newly expanded counts substituted. Numerical full-word
counts, denominator heights and practical precision thresholds are not
computed here. Neither a smaller N nor a favorable moment supplies an
independent proof of the inherited physical/analytic premises.

## 6. Reproduction, provenance and coverage

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/higher-moment-strictification/verify.py
python3.12 -B scripts/research_package.py --package research/higher-moment-strictification --check-only
python3.12 -B scripts/research_package.py --package research/higher-moment-strictification
```

To generate a fresh receipt, use `verify.py --out /absolute/new/path.json`.
The saved [RESULT.json](RESULT.json) records all intervals, finite parameters,
integer comparisons, ledgers, controls and source/verifier hashes.

Logarithms use 80 exact terms of the binary-reduced atanh series with the
geometric tail. Exponentials use 64 terms after binary scaling into [0,1/2],
outward rounding at precision 2^−192, twice the next term for the remaining
tail, and outward repeated squaring. Negative arguments use reciprocal
intervals. Every decision uses fractions or integers, with no floating-point
acceptance test. A separate exact small product/pad/split example checks
the inventory and preserved surplus, and a sublinear-tail counterexample
guards the theorem's exponent restriction.

Canonical base is `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision
7. [SOURCES.json](SOURCES.json) pins the orientation metadata. The 15 unchanged
exports in [VENDOR.json](VENDOR.json) include complete source paths, commit
IDs, Git blob names and SHA256 hashes; the verifier authenticates both hashes
without requiring Git. Pending commits are represented by self-contained
exports, not implied publication ancestry. Source exports remain unchanged.

The PR4426 invoice oracle is compiled from its authenticated source bytes,
with only ROOT and PHASES rebound to the exported file locations. Its literal
controller, supplier-receipt and port-recipe checks remain intact. The two
ledger oracles retain predecessor code and attribution; they are arithmetic
cross-checks, not fresh native supplier admission.

Local validation used Python 3.12.8 on macOS arm64. The registered replay,
metadata/pin check and committed-byte preflight passed. A separate Git-free
copy passed `python3.12 -I -O -B verify.py` in 0.333 seconds; changed-source
and changed-receipt controls rejected. The optional full source-history
preflight could not run because this checkout is shallow. All pending-source
inputs are self-contained exports; standalone replay does not need those
foreign Git objects. No Lean, Docker, native all-size or historical suite was
run. These checks authenticate the stated result, not independent scientific
acceptance.

Overlap at 18:19 UTC covered 536 open PR bodies and 3,279 discussion/comment
records with complete reported pagination, plus local notes. The newer
#4420/#4428/#4429 checks cover earlier strictification proof/arithmetic and
slightly smaller sufficient powers; #4426 supplies the invoice replay reused
here. No remote closed-PR-body or arbitrary code-diff search was performed.
The task metadata records the changed scope and remaining direct-compiler
question. Submission was authorized after local review; no Discussion claim was posted.

## Open next questions

1. **A direct compiler for overlapping ranks.** A finite acyclic integer
   schedule would remove strictification altogether. Start by replacing the
   Pascal matching step when a paid rank exceeds a target rank, retaining
   arbitrary inputs, complements and chronological suspension. No such
   termination/matching proof is supplied by the mixed moment alone.
2. **Full finite-word size and precision.** Derive compressed upper bounds
   for the compiler's batch denominators, widths, scalar passes and owned
   instances at the specified rank. Ambient rank is only one size parameter;
   this remains the main barrier to assessing practical constants.
3. **Independent scientific review.** Check the higher-moment inequality,
   the p>1 induction and the native product/adapters at their actual callers.
   The unchanged raw supplier's internal paid bill and all-column/physical
   premises remain separate inherited obligations. Another search of nearby
   c,b,u,v values would not resolve those obligations.

Prepared by zxv with substantial OpenAI Codex assistance in discovery,
implementation and writing. No subagents or independent human review were
used for this new work. New material is Apache-2.0. Native/controller lineage:
zxv's PR4359 and its retained contributors. Product/padding and p7 controller:
@1337isnot1337's PR4412/PR4414/PR4416. Integer mixed flow: Jacob Alan
Sussman, Theorem 1G. Logarithmic-majorant predecessor: zxv's PR4411.
Invoice replay: Ryanson Jonathan / @pinterbanget, PR4426, with Claude Code
assistance and Apache-2.0. The retained supplier and outer sources preserve
their original contributor credit and notices.
