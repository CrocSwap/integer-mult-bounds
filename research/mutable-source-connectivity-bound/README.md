# The restoration cost of mutable-source connectivity

**All-n scoped theorem, with exact finite evidence; no new kappa.** This closes
Arham Tahir's [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898)
[explicit open question](https://github.com/CrocSwap/integer-mult-bounds/discussions/1579):
at the minimum `Q=n+1` common-map queries, the minimum number of paid elementary
source XORs is **`X=2(n-1)`**, even with arbitrarily many readouts and arbitrary
interleaving. PR1898 already supplies the attaining construction and the minimum
readout count; neither is claimed as new here.

The new lower bound is more general. If the historical source-interaction graph
has `k` components, every restored generic word satisfies

```
Q >= n+k,             X >= 2(n-k),
Q >= n+1,            2Q+X >= 4n.
```

Consequently the projected query/XOR Pareto frontier is exactly
`(Q,X)=(n+k,2(n-k))`, `k=1,...,n`, when readout counts are unrestricted.
This is not the full three-resource frontier: intermediate points can have
very different readout costs. A further consequence is a sufficient **global
unequal-price optimality region**, proved below. For five sources, if complete
prices satisfy `b >= 34a+2x`, then the exact minimum over **all finite words** is
`6b+96a+8x`. This is a sufficient region, not a classification outside it.

## Contract and provenance

Use the exact F2 interface of PR1340/PR1370/PR1898: `n>=1` distinct arbitrary-dirty
length-L source rows, one dirty connector, and one dirty output for every nonzero
binary source mask. The common B and the output maps A_m are arbitrary fixed
exact linear maps, possibly singular or noncommuting. The requested endpoint is

```
y_m += A_m B(sum_{j in m} x_j_initial),
```

with sources, connector and private scratch restored. The only complete calls
are `Q_j: z += B x_j`, `R_m: y_m += A_m z`, and
`X_(s,t): x_t += x_s` with distinct source indices. The straight-line program
must work for every admissible map and input. Calls preserve other rows, restore
private scratch, and return to promised entry/exit frames and head positions.
No output observation occurs before the batch ends. There are no extra root
connectors, free copies, source-specific B_j, source resets, source swaps,
output mixing, direct product calls, or unpriced combined operations.

The changed alphabet relative to Ross Richardson's PR943 is the **paid source
XOR**, introduced by Arham Tahir in PR1340. This package refines that already
established extension to its missing restoration lower bound. It does not
rebrand a new seed or a larger finite domain as a new mechanism. PR1370 fixes
ten queries and 62 paired readouts; PR1524 fixes equal query/readout prices;
PR1898 explicitly does not claim XOR optimality at minimum queries. Exact heads,
base, source bytes, selection and scope are in [SOURCES.json](SOURCES.json),
[SELECTION.json](SELECTION.json) and [TASK.json](TASK.json).

## Proof 1: a closed source circuit pays twice for connectivity

Ignore Q and R when following the source state. Write it as `x_current=T x_in`,
where T is an invertible n-by-n binary matrix. An X replaces row t by the sum
of rows t and s. T starts and ends at the identity, because no other permitted
operation changes source rows and sources must restore for every input.

Let G(T) be the bipartite support graph on **n row vertices and n original-input
column vertices**, with an edge exactly at each nonzero entry. Let c(T) be its
number of connected components. Every vertex is incident to an edge because T
is invertible. In particular, `c(I)=n`.

**Single-gate lemma.** Join row vertices s and t by one auxiliary edge. The
connected-component partition of this augmented graph is identical before and
after `row_t ^= row_s`. Indeed, all changed target edges lead to columns already
incident to row s; once s and t are joined, deleting or adding those edges cannot
change any connectivity. Removing the one auxiliary edge can change component
count by at most one. Therefore `|c(T_next)-c(T)|<=1`. If s and t were in
distinct components before the gate, their column supports were disjoint:
no target edge is lost, and exactly those two components merge, so the change
is exactly -1. This also handles arbitrary cancellations when they were in the
same component; it does not assume every gate creates a persistent nonzero entry.

Now form the **historical** undirected graph H on source-register indices: add
edge `{s,t}` whenever an X uses those two registers, retaining it even if that
operation is later undone. Let its final component count be k. Exactly `n-k`
edge insertions merge formerly distinct historical components. At any time,
each current row has support only on original columns in its own current
historical component, by induction on the gates. Thus at each such historical
merge, rows s and t lie in distinct components of G(T), and c(T) decreases by one.

Let d and u be the numbers of X gates decreasing and increasing c(T). We have
`d>=n-k`. The circuit starts and ends at I, so `u=d`. Gates with zero change
are additional. Hence

```
X >= d+u = 2d >= 2(n-k).
```

No word-length bound, monotone support assumption, or simultaneous all-source
mixing is used. A certificate control visits only two-source mixed states but
has a connected historical graph; it would invalidate a proof that confused
current and historical components. Redundant/cancelling inter-component gates
are fully covered by the count of decreases, compensating increases, and
zero-change gates.

## Proof 2: each historical component costs an extra query

Specialize to scalar identity maps and independent incoming bits. A query adds
a nonzero current row direction v in F2^n to the connector's source coefficient.
Every v is supported inside one final component C of H. Connector restoration
requires that all query increments sum to zero. Since the components have
disjoint coordinates, the increments in each component sum to zero separately.

Each required singleton output is an even sum of connector prefixes (evenness
cancels the arbitrary connector dirt), hence lies in the span of all query
increments. Therefore the increments in a component of size n_C have rank n_C.
If there are t_C such queries, their zero sum is a nontrivial dependence, so
`t_C>=n_C+1`. This remains true with arbitrarily many readouts and with queries
interleaved with any source mutations. Summing over components proves
`Q>=n+k`. Combining with Proof 1 gives `2Q+X>=4n` and `Q>=n+1`.

Only a spanning requested mask set is needed for these lower bounds. The full
nonzero-mask set is used below for the readout total and the tariff consequence.
Special maps or restricted inputs need not satisfy generic lower bounds.

## Attainment and what is, and is not, new

Partition the n sources into k nonempty blocks. Within each block, use PR1898's
construction: query its original sources once each, gather their sum into its
first source with d-1 XORs, query that source once to close the connector path,
then undo those XORs in reverse order. Other source rows are untouched. Do this
for each block. Counts are `Q=n+k`, `X=2(n-k)` and the sources/connector restore.

The distinct prefixes are zero and n independent vectors: within each block,
the nonzero prefixes are successive partial sums of its basis sources, and
different blocks have disjoint supports. Every mask is consequently represented
by a unique subset of those n nonzero prefixes. Include zero if needed to make
the readout subset even. This realizes all outputs without assuming clean rows.

There are `2^n` even subsets of an affine basis of n+1 points; every point lies
in `2^(n-1)` of them. The total is `(n+1)2^(n-1)` readouts (zero mask uses none).
At Q=n+1, rank forces exactly such an affine basis, proving PR1898's inherited
readout lower bound. Thus the old minimum-query construction simultaneously
attains the new X floor and the old R floor. The new contribution is the
all-word connectivity proof and its consequences, not that construction.

For a fixed query count `n+1<=Q<=2n`, choose `k=Q-n` to attain
`X=2(2n-Q)`. These are the nondominated projected Q/X points. The continuation
above 2n is dominated by `(2n,0)`. Readout costs cannot be silently discarded:
for example, the n=5 block witnesses all use 96 readouts, while the credited
PR1370 `(10,62,4)` word uses fewer readouts at the cost of more source XORs.

## Full tariff and a globally optimal unequal-price region

Let b,a,x>0 be **complete**, uniform Q,R,X prices, including arithmetic,
coefficient/source access, target updates, private scratch restoration, head
returns, frames, precision and per-call dispatch. Let I+P cover common admission,
layout and coefficient preparation. Add each schedule's actual residual program
construction/storage/control cost D when it is not included in these prices.
The following exact optima concern the complete-call tariff. Unequal I/P/D or
port-dependent prices must be added before a physical comparison.

At Q=n+1, the exact tariff is

```
C_minQ = (n+1)b + (n+1)2^(n-1)a + 2(n-1)x.
```

For n>=2 put `Delta=(n+1)2^(n-1)-2(2^n-1)` (nonnegative). Each active output
needs at least two reads. If Q=n+1+s, `1<=s<=n-1`, our new bound gives
`X>=2(n-1-s)`, hence every such word costs at least

```
C_minQ + s(b-2x) - Delta*a.
```

If **`b>=Delta*a+2x`**, this difference is nonnegative. For Q>=2n, use X>=0
and R>=2(2^n-1); the lower bound at Q=2n is already nonnegative and rises by b
per extra query. At Q=n+1 the inherited R floor and the new X floor apply.
Therefore C_minQ is the global tariff minimum over arbitrary finite words in
this sufficient price region. Strict inequality makes every larger-Q word
strictly more expensive. This is not an exact boundary of the optimality region.
For n=1, the elementary two-query/two-readout word is optimal without a source
mutation and needs no price restriction.

For n=5, Delta=34. The replay includes the fully expanded abstract fixture with
B composed of **eight** independent exact factors and each A_m one factor.
Contiguously splitting F=LR over a distinct dirty scratch row executes
`R, L, inverse(R), inverse(L)`, retaining every inverse leaf. With one abstract
unit per complete leaf, source XOR, executed internal echo node and root
dispatch, eight-factor B has 64 leaves, 21 executed echo nodes and height 3:
`(b,a,x)=(86,2,2)`. Thus `86>34*2+2*2`, and the proved global minimum is
**724**: 480 map leaves + 126 internal-node charges + 8 source XORs + 110 root
dispatches. Every Q>=7 competitor has tariff at least **738**. This establishes
an abstract fixed-price optimum, not a physical-time optimum.

The eight-factor word requires four borrowed dirty rows (root plus three
recursive scratch rows), 36 source/output rows, and 39 primitive map descriptors.
All 40 incoming dirty row variables and all noncommuting factors are retained
in the free-linear forward/inverse replay. For physical realization, source
XORs must pay L XORs, 2L reads, L writes, traversal and return. Dense exact map
leaves can use an admitted clean scalar bit, accumulate each dot product,
update the target, and recompute to clear the bit; charge 2L^2 coefficient reads,
2L^2 source reads, L target updates, arithmetic and all travel/control. Here a
literal storage region uses `S=39L^2+40L` cells, plus scalar/index/program storage.
Loose per-leaf travel is `S(4L^2+L+1)`, and per-X travel is `S(3L+1)`; scalar
initialization, indices, admission, map preparation and instruction work are
additional. These implementability bounds do **not** imply uniform physical
prices (86,2,2). No selected supplier exposing this common-B seam is identified.

## Reproduce and evidence

From the repository root (standard library, CPython 3.12):

```sh
uv run --python 3.12 --no-project python -I -O -B \
  research/mutable-source-connectivity-bound/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py \
  --package research/mutable-source-connectivity-bound
```

[RESULT.json](RESULT.json) is the deterministic exact receipt; regeneration is
`verify.py --write`. The verifier checks source SHA256 pins before using input
bytes, recomputes all evidence, and compares every proof-relevant receipt field.
[VERIFY.json](VERIFY.json) registers the semantic replay and focused corruption,
relocation and optimized-execution controls. Small finite checks support the
implementation and proof steps; the all-n claim rests on the written proof,
not extrapolation from a bounded search or formal-kernel acceptance.

The evidence includes the full single-gate support-partition census on GL(n,2)
for n=1,...,4, with an independently implemented row-intersection oracle;
closed source-word checks; all integer-partition witnesses for n=1,...,8;
formal noncommuting root and full-leaf endpoints/inverses; independent concrete
dirty-state matrix executions; and controls for source restoration, connector
dirt, private cleanup, output masks, factor order, omitted charges and missing
full-span queries. No selected frontier cold replay or hosted CI pass is claimed.

The observed CPython **3.12.12** replay on macOS arm64 passes the optimized
direct command and the registered package: **242,940** GL transitions,
**66** partition witnesses, **12** primary semantic controls, **288**
independent forward/inverse dirty cases, **five** independent controls and
**five** focused test groups. Regeneration compares JSON arrays canonically
(Python tuples and lists are not treated as different mathematical evidence).
The initial noncanonical tuple/list comparison failed and was corrected; no
mathematical receipt field was weakened or omitted.

The final cached overlap check retains the 329-open-PR / 692-discussion snapshot
from 2026-10-14 18:11--18:12 UTC, with complete pagination and explicit offline
freshness warnings. A targeted live GraphQL check confirms PR1898, PR1370,
PR1340, PR1524 and PR943 all merged at the exact heads in TASK.json. Local merged
review notes and live discussion1579 were inspected. These checks found no
closure of the same X-optimality question; they are not a novelty guarantee.

## Open next questions

* Determine the minimum readout totals on intermediate Q/X faces, beginning with
  n=5, Q=7, X=6. This matters for the full unequal-price frontier outside the
  sufficient cone. Enumerate the feasible full-span prefix sets and their
  even-subset weights; the present connectivity proof discards that geometry.
* Identify an actual selected-supplier common-B boundary with exclusive source
  ownership, then charge routing, frames, precision, program storage and all
  restorations. A local tariff theorem cannot supply that missing caller or
  physical admission. Structured first steps and blockers are in TASK.json.

## Credit, source scope and disclosure

Arham Tahir supplies PR1340's alphabet, PR1370's paired-readout source-XOR floor,
and PR1898's minimum-query/readout theorem, attaining construction and explicit
missing-X-optimality handoff. TennisBowling supplies PR1524's equal-price global
tariff theorem. Ross Richardson supplies PR943/934's connector prefix framework,
945-pairing exclusion, repairs and dirty recursive lowering; the inherited
common-factor/commutator lineage includes shhxera/CubeJerry and Chafik Boukhalfa.
The selected construction and its retained authors' credit remain unchanged.
No predecessor executable is imported or overwritten.

Prepared for **Adam Gall** with substantial **OpenAI Codex (GPT-6 Astra)**
assistance in proof, research, code, experiments and writing. New material is
Apache-2.0 under the repository license. This is not independent human review,
formal verification of the multiplication theorem, an admitted recursive
supplier, a paid moment improvement, or a new kappa.
