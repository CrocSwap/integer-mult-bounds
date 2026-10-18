# Minimum-query endpoint of the mutable-source connector

**Scoped recursive-interface theorem and construction; no new kappa.**
For all nonzero masks on `n >= 1` sources, allowing arbitrarily many paid
source XORs and even readouts, the generic common-B connector needs at least
`n+1` queries. At exactly that minimum, the minimum total readouts is
`(n+1)*2^(n-1)`. A construction attains both counts with `2(n-1)` source XORs.
The XOR count is attained, **not asserted optimal**.

For five sources this gives **6 Q / 96 R / 8 X**, compared with the credited
paired-readout **10 Q / 62 R / 4 X** and read-only repairs. The changed premise
is permission for more than two readouts per output. The ten-query
paired-readout obstruction of PR1340/1370 is preserved. This answers part of
[PR1524's unequal-price handoff](https://github.com/CrocSwap/integer-mult-bounds/blob/5c1f39788a0fc669b7e37e27785c63e85788c350/research/mutable-source-uniform-tariff/README.md),
without determining the global unequal-price optimum.

## Exact interface and proof

Use distinct arbitrary-dirty length-L rows over F2: sources `x_j`, one output
`y_m` for each `1 <= m < 2^n`, connector `z`, and private scratch, with `L>=1`.
The fixed exact maps B and A_m are read-only; none need commute or be
invertible. B is common to every source port. Generic correctness means
correctness for every admissible map and incoming data. The requested exit is

    y_m += A_m B(sum_{j: bit_j(m)=1} x_j_initial),

with all sources, z and private scratch restored. The only complete operations
are `Q_j: z += B x_j`, `R_m: y_m += A_m z`, and paid
`X_(s,t): x_t += x_s` for `s != t`. Every call preserves other rows, restores
private scratch and returns its heads to promised positions; its additive
behavior is independent of its old target. The straight-line word is data
independent. Sources and outputs cannot be observed until completion.
Extra connectors, copies, direct AB calls, output mixing, source-specific B_j
and other data operations are excluded. This is PR1340/1370's source-shear
alphabet, not a newly invented alphabet.

Specialize to `L=1, B=A_m=identity`, with all incoming bits independent.
At a boundary the connector is `z_in + q dot x_in`, for `q in F2^n`. Only Q
changes q; X changes the source direction used by a later Q. Every output
needs an even number of R calls to cancel z_in. Its mask is the XOR of the
prefix points at those calls. Source restoration is a separate obligation.

**Query lower bound.** With t queries, connector restoration gives increments
`v_1,...,v_t` satisfying `sum v_i=0`. Every prefix lies in their span, of rank
at most `t-1`. The n singleton output masks must be expressible by readouts,
so that span has rank n. Thus `t>=n+1`, regardless of the number or positions
of source XORs and readouts. There is no bounded-word extrapolation.

**Readout lower bound at minimum queries.** At `t=n+1` the prefixes before the
last query are `q_0=0,q_1,...,q_n`; the final point duplicates q_0. To span
dimension n, `q_1,...,q_n` must be independent. Combine occurrences at the
duplicate zero boundary and reduce readout counts modulo two. Every output
then selects an even subset of these n+1 points. The map from even subsets to
F2^n is bijective: the coefficients of the n independent nonzero points are
fixed by the mask; the coefficient of zero is fixed by even parity.
Consequently each output needs at least its unique subset's cardinality.
Repeated reads can only increase the count.

Among all `2^n` even subsets, each coordinate is present in `2^(n-1)` subsets:
fix it to one and choose the other n bits with odd parity. The zero mask has
the empty subset and contributes zero. Summing over every nonzero mask gives
the exact lower bound `(n+1)*2^(n-1)`. This includes n=1. Restricted maps or
input domains need not inherit a generic lower bound.

**Attainment.** Query the original sources in order to obtain prefixes
`q_t=2^t-1`, for `0<=t<=n`. At these boundaries read every output at its unique
even subset. Then XOR sources 1,...,n-1 into x0, query x0 once, and undo the
source XORs in reverse order. Common-B linearity makes the final query add
the sum of the original source contributions and restore z. The source
compute/uncompute restores x0, and every other source is preserved.
Even parity cancels readout dirt; the subset identity gives every A_m B target.
This proves the construction for all n,L and arbitrary exact maps.

For n=5 the prefix points are `0,1,3,7,15,31`. The readout histogram is
15 outputs with two, 15 with four, and one (mask 21) with six: 96 total R.
[CERTIFICATE.json](CERTIFICATE.json) contains every literal root/leaf event
and readout position. The code's n=1..9 fixtures support the implementation;
the written argument supplies the all-n result.

## Complete unequal-price comparison

Let b,a,x be uniform **complete** Q,R,X prices, including per-call dispatch,
source/coefficient access, cleanup, head return, precision and required frames.
Shared admission/preparation I+P is additional. Add each schedule's actual
residual program-construction/storage/control bill D if these obligations are
not already priced. With a pure complete-call tariff, the new bill is

    C_6 = I+P + 6b + 96a + 8x.

It beats the four-X word iff `4b>34a+4x`, the twelve-Q read-only repair iff
`6b>34a+8x`, and the ten-Q/64-R read-only repair iff `4b>32a+8x`.
These compare attained words, not global optima. Residual D differences must
be included; port-dependent costs require actual per-call sums.

In the **abstract complete-price fixture**, B has five independent exact
noncommuting factors in application order, while each A_m is a single arbitrary
exact map. Split a compound map contiguously into right R and left L. With a
distinct dirty row w, execute `R(source,w), L(w,target), inverse R, inverse L`.
Every inverse includes its complete reversed child word. The recurrences are

    ell(1)=1; ell(d)=2ell(floor(d/2))+2ell(ceil(d/2));
    nodes(1)=0; nodes(d)=1+2nodes(floor(d/2))+2nodes(ceil(d/2));
    height(1)=0; height(d)=1+max(height(floor(d/2)),height(ceil(d/2))).

Thus B has 28 completed map leaves, nine executed internal nodes and depth
three. Pay one abstract unit per complete map leaf, complete source XOR,
internal node and root dispatch: `(b,a,x)=(38,2,2)`. All four words use the
same 36 primitive map descriptors, 36 source/output rows, and four borrowed
dirty rows (z plus three private rows); no clean full row is assumed.

| Word | Q / R / X | Map leaves | Echo nodes | Root dispatches | Abstract bill |
|---|---:|---:|---:|---:|---:|
| Minimum-query endpoint | 6 / 96 / 8 | 264 | 54 | 110 | **436** |
| PR1370 four-X word | 10 / 62 / 4 | 342 | 90 | 76 | 512 |
| PR943 extra-source repair | 12 / 62 / 0 | 398 | 108 | 74 | 580 |
| PR943 extra-output repair | 10 / 64 / 0 | 344 | 90 | 74 | 508 |

The four-X path is attributed to PR1370. Both old repair words are read from
the pinned main certificate and repriced with the **same** common B and A_m.
No historical heterogeneous invoice is reused. The 72-unit difference from
the least costly displayed comparator includes every inverse leaf, internal
node, source XOR and root dispatch. It is not a physical runtime saving.
At the old equal-Q/R five-factor tariff this word costs 3892 versus 2744;
the checker includes this non-improvement control.

An eventual physical implementation must justify each complete price. A source
XOR pays L XORs, 2L reads, L writes, travel, return and control. A slow dense
map leaf can compute each target dot product in an admitted clean scalar bit,
update the target, then recompute to clear the bit. This pays 2L^2 coefficient
reads, 2L^2 source reads, L target updates, and all travel/control. With
S=36L^2+40L data cells, loose travel bounds are `S*(4L^2+L+1)` per leaf and
`S*(3L+1)` per source XOR. Pay scalar-bit admission, coefficient preparation,
indices and instruction access too. These finite implementability bounds do
not establish the favorable abstract tariff on a physical supplier. Scheduling
enumerates the even subsets; program construction/storage must be paid in I
or residual D, rather than supplied by a free oracle.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/mutable-source-minimum-queries
```

Default checks are read-only. Explicit regeneration is
`python3 -B research/mutable-source-minimum-queries/verify.py --generate`.

The symbolic engine checks all incoming dirty roles, all four root words and
their noncommutative factor expansions, forward and inverse. It checks n=1..9,
all 168 independent 3D prefix bases and all 168 full-span four-query circuits.
Twelve semantic controls address source restoration with correct outputs,
dirty-z leakage, omitted queries, wrong masks, factor order, private scratch,
aliases, unpaid nodes/dispatch, heterogeneous B, dependent prefixes and the
six-readout certificate. These finite controls accompany the written proof.

The second oracle uses bit matrices and imports no symbolic implementation.
Its 7,360 root/expanded forward/inverse executions cover every dirty basis
input and mixed states at L=1,2,3,4, explicit noncommuting factors and two
concrete failure witnesses. Both implementations were written by the same
assisted author; this is implementation diversity, not independent human
review. [VALIDATION.md](VALIDATION.md) records environments, commands and seven
test groups, including optimized replay, real source/receipt corruption,
duplicate-key rejection, deterministic regeneration and relocation without Git.

Base main: `680967accfd4311f3241dc154e1f434869747b43`. Selector nonce
`edb6b50cf28c576de3f77fc578cfdfb4`, priority revision 2. The concrete refinement,
overlap coverage and advisory [claim #1579](https://github.com/CrocSwap/integer-mult-bounds/discussions/1579)
are recorded in [TASK.json](TASK.json). [SOURCES.json](SOURCES.json) binds the
main inputs; [PREDECESSORS.json](PREDECESSORS.json) records exact reference heads
and their publication status.
No predecessor executable is imported. Selected cold replay, supplier adoption,
physical owner/frame/precision/tape admission, outer all-size transfer,
proof-assistant verification and new moment/kappa are outside this result.

## Open next questions

The global unequal-price optimum remains open: first bound attainable R/X
bills at seven, eight and nine queries, which may undercut this endpoint.
The minimum source-XOR count at six queries is also open; the eight-X word
alone does not settle it. Physical use requires an actual common-B boundary,
exclusive temporary source access and a favorable complete bill. Structured
first steps and blockers are in TASK.json.

## Credit

Prepared by **Arham Tahir** with substantial **OpenAI Codex assistance** in
proof, both implementations, checking and writing; no subagents or independent
human review. New material is Apache-2.0 under the repository LICENSE.

Credit Arham Tahir's PR1340 for the source-shear alphabet/paired-readout bound,
PR1370 for the four-X word and fixed-count theorem; TennisBowling's PR1524 for
the arbitrary-count equal-price theorem and unequal-price handoff; Ross
Richardson's PR943/934 for the prefix framework, repairs and dirty lowering;
shhxera/CubeJerry's PR889 and Chafik Boukhalfa's PR628 for the retained batching
and commutator lineage. The classical affine-basis/even-subset argument is not
claimed as a new general technique. Selected Rohan Arun/Jeremy Kothe
construction credit and cumulative repository attribution are preserved.

Submission was resumed on main `0b1cccf86e2f5132ed286a26ef0a681a495740ea` after PR1340/1370 were merged
unchanged. Revision-3 guidance was inspected; AGENTS.md says to retain an
already assigned task. The mathematical inputs and selected record are
unchanged. The updated registered replay passes. Final resumption overlap
covers 542 open PRs and
528 Discussion/comment/reply records;
PR1770's read-only unequal source tariff and PR1811's hyperplane families have
different contracts. Exact scopes and freshness limits are in TASK.json.
