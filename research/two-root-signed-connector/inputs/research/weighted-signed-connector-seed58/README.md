# Exact weighted repair for the signed three-by-three connector obstruction

**Recursive-interface research construction and scoped optimum; no new kappa.**
For the 288 signed/permuted obstructed patterns in Ross Richardson's
[PR944](https://github.com/CrocSwap/integer-mult-bounds/pull/944), every one of
the six operators can carry the necessary extra restoration pair. Thus, for
arbitrary positive complete-query prices equal between signs, the exact cost is

```
2 (c_B0 + c_B1 + c_B2 + c_A0 + c_A1 + c_A2) + 2 min_F c_F.
```

PR944 proves this formula for its particular example with B0 cheapest. This
contribution supplies all six repairs and proves it for every price ordering
in the same query alphabet. Seed 58 selects a different child-length ordering:
the cheapest child is A1. Its full balanced lowering uses **308 primitive
calls**, versus **332** when retaining the B0-repeat choice. All four borrowed
dirty rows restore. These are operation counts, not measured runtime savings.

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 -I -O -B research/weighted-signed-connector-seed58/verify.py
python3 -I -O -B research/weighted-signed-connector-seed58/test_package.py
```

The first prints
`PASS_WEIGHTED_SIGNED_CONNECTOR witnesses=6 orbit=288 paths=61200 leaves=308_vs_332 dense=378 no_new_kappa`.
The second prints JSON with `status: PASS_WEIGHTED_SIGNED_PACKAGE`, `count: 47`,
and passing isolated optimized replay and deterministic regeneration. To select
an exact priced word, append `--prices 16 28 40 52 4 10` to the first command.
Its additional JSON has `repeated: A1`, `minimum: 308` and the literal query word.
Rational prices such as `1/7` are accepted; zero/negative prices are rejected.

## Fixed interface and statement

There are distinct length-L arrays x0,x1,x2,y0,y1,y2,z over characteristic zero.
Every initial value, including z and each y, is arbitrary. Fixed additive linear
maps A_i,B_j need not commute or be invertible. Sources and coefficients are
immutable. The required map is

```
x_j unchanged; z unchanged; y_i += sum_j M_ij A_i B_j x_j,
M = [[1,1,1], [1,1,-1], [1,-1,0]].
```

The only queries are `B_j^s: z += s B_j x_j` and `A_i^s: y_i += s A_i z`,
where s is +1 or -1. A negative query subtracts the same increment; it does not
invert A_i or B_j. Each complete query restores its private work and tape heads,
preserves its source and other data, and is independent of old target contents.
All seven data rows stay reserved during children. Outputs are observed only
after completion. There are no other data operations, extra root connectors,
combined queries, direct products, free copies, frame changes or overwrites.

The optimum concerns uniform correctness for arbitrary admissible operators
and inputs. Particular zero maps or algebraic relations can reduce the cost.
The complete price c_F is a fixed positive charge common to both signs and
all admissible incoming states, at fixed ports. It includes child execution,
source/coefficient access, restoration, routing, frame adapters, head return,
and per-query dispatch. State-, sign- or word-dependent costs require their own
optimization; the displayed minimum is not asserted in those models.

## Proof of the weighted optimum

In any correct word, restoring z forces the signed sum of each B_j's occurrences
to be zero. Canceling each A_i z_initial forces the signed sum of each A_i's
occurrences to be zero. Every row and column of M is active, so each of the six
operators appears at least twice, and each occurrence count is even.

At twelve queries each B_j occurs exactly once with each sign. Let q_t be the
three signed source coefficients in z after its first t B queries. Each A_i
has one negative and one positive readout, so row i must be a difference of
two visited q vertices. There are exactly `6! = 720` source words with one
positive and one negative occurrence of each labeled B. None supports all
three rows of M. The independent DFS in verify.py exhausts precisely this
finite reduction; it is not a heuristic search failure. Thirteen queries are
excluded by evenness. Consequently some operator has at least four occurrences,
and every valid word costs at least `2 sum_F c_F + 2 min_F c_F`.

Here are six attaining words. Each has four occurrences of its named operator,
two of every other operator, and balanced signs:

```
B0: B0- A1- B0+ B0+ A2+ B1+ A0+ B0- A2- B2- A1+ B1- A0- B2+
B1: A0+ A2+ B0- B1+ A2- B1- B1- A1- B2- A0- B0+ B1+ A1+ B2+
B2: B0- A2- B1- A0- A1- B0+ A2+ B1+ B2- A1+ B2+ B2+ A0+ B2-
A0: A2+ B0- A1- B1+ A2- B2- A0- B0+ A1+ B2+ A0+ A0+ B1- A0-
A1: A2+ B1+ A1+ A0+ B0- A2- B1- A1- A1- B2- A1+ A0- B2+ B0+
A2: A2- B0+ A2+ A2+ B1+ A2- A1+ B2+ A0+ B1- B0- A1- B2- A0-
```

For a word with balanced operator signs its product coefficient M_ij is the
sum of `s_A s_B` over B_j calls preceding A_i calls. Reversing chronology and
exchanging A/B therefore transposes that coefficient matrix. Since this M is
symmetric, it turns each B-repeat witness into an A-repeat witness. No factor
commutation is used: the new word is checked in its new source/output roles.

For clarity, the A1 word has source-prefix vertices
`(0,0,0),(0,1,0),(-1,1,0),(-1,0,0),(-1,0,-1),(-1,0,0),(0,0,0)`.
Its A0 and A2 readouts have differences `(1,1,1)` and `(1,-1,0)`.
Its four A1 readouts sum to `(1,1,-1)` and cancel the initial connector dirt.
All six words can also be checked directly by this coefficient sum.

Permute rows/columns and multiply them by signs to obtain any member of the
288-matrix orbit. Relabel the corresponding queries and multiply their signs.
This preserves the six occurrence profiles, merely permuting their operator
names. Choosing the cheapest named operator attains the lower bound for every
positive price vector throughout the orbit. The verifier checks all 288 maps
and all six transformed words (1,728 query replays).

This is a written algebraic reduction plus exact finite certificates, not
proof-assistant verification of the statement or the multiplication theorem.

## Complete recursive price and the seed fixture

For ordered factors F=(f1,...,fn) in application order, split into the first
floor(n/2) factors R and the remainder S. With one fresh dirty child connector w:

```
R(x,w); S(w,y); inverse(R)(x,w); inverse(S)(w,y).
```

An inverse reverses the entire literal primitive word and negates every sign.
Induction gives y += SR x, with x and w unchanged, for exact additive children
over arbitrary noncommuting factors. Descendant private scratch is disjoint
from all current ports and restores on return. The complete recurrence is

```
C([f]) = c_f + d_leaf,
C(F)   = 2 C(R) + 2 C(S) + d_node,
h([f]) = 0; h(F) = 1 + max(h(R),h(S)).
```

Each c_f includes coefficient/source operations, full-row work, source
restoration, fixed-port/frame admission and head return. The d terms pay
control, selection and literal inverse dispatch. If costs differ by sign,
price the four actual child invocations separately and do not use the
sign-symmetric optimum. Shared initial admission I and factor preparation
P_F are paid once; no output count divides a full-row cost. The full batch bill
is `I + sum_F P_F + E + 2 sum_F C(F) + 2 min_F C(F)`, where E pays selector,
instruction emission/storage and any batch metadata not already in C.
A distinct E for different words is outside the fixed-price optimum.

For uniform unit primitive prices, the balanced leaf recurrence is
`ell(1)=1; ell(n)=2 ell(floor(n/2))+2 ell(ceil(n/2))`.
Seed `58 mod 6 = 4` places the length-two child at index four in B0,B1,B2,A0,A1,A2
order. The resulting lengths and complete primitive counts are:

| Operator | B0 | B1 | B2 | A0 | A1 | A2 |
|---|---:|---:|---:|---:|---:|---:|
| Factor length | 4 | 5 | 6 | 7 | 2 | 3 |
| Primitive calls | 16 | 28 | 40 | 52 | 4 | 10 |
| Batch repeating this operator | 332 | 356 | 380 | 404 | 308 | 320 |

These six literal primitive words are stored in CERTIFICATE.json and rebuilt
by an independent iterative expander. The free noncommutative interpreter
retains all ten independent dirty input symbols, checks the entire map and
its literal inverse, and forbids any primitive write to the three sources.
One batch connector plus maximum child depth `ceil(log2 7)=3` uses four
borrowed length-L dirty rows. Seven data rows plus three private child rows
make ten mutable rows total. Preparation, controller and scalar work are separate.

## Paid dense realization and limits

EXPECTED.json gives a literal dense integer realization for L=1,2,3 for every
repair word, with no zero-entry skipping. The data tape has ten mutable rows,
then 27 read-only L by L coefficient matrices. For every dot-product term,
the head visits its coefficient and source cell, then its target cell after
the dot product. Each primitive starts and ends at data cell zero. A separately
derived travel formula matches all 18 traces.

For N primitives it pays `N L^2` coefficient reads and source reads,
`N L` target read/write pairs, `N L^2` multiplies, and `N(L^2+L)` add/subtracts.
Four clean scalar work registers hold source, coefficient, product and
accumulator. Each term clears its three operand/product registers; each output
clears the reused target register and accumulator and begins with a zero
accumulator: `N(3L^2+3L)` scalar zero assignments plus four startup assignments.
There are O(log L + log N) additional loop/address/control bits. These scalar
operations and address arithmetic must be charged in the chosen backend.

A separate sequential read-only instruction tape stores 14 bits per primitive:
five factor bits, two four-bit ports and one sign bit. Reading it once and
returning its head costs 14N bit reads and 28N bit-cell movements. Emission and
the six-price selector are separately paid; this is no free precomputed advice.
The fixture's 27 supplied coefficient matrices cost 27L^2 read-only words;
constructing them from another representation is additional preparation.
Initial shape/port/word admission reads the `10L+27L^2` supplied data and
coefficient words; a separate supplied program is also scanned and priced.
No frame conversion is used by the dense fixture. Other realizations pay theirs.

With coefficient bound H and initial magnitude D>=1, N primitives have
intermediate infinity norm at most `D(1+LH)^N`. A sufficient common signed
word width for all six schedules is
`w=2+ceil(log2(max(1,D,H)))+404 ceil(log2(1+LH))`, also covering dot-product
intermediates. Loads/stores/zero assignments and word-cell motion pay w bits;
integer multiplication/addition use the backend's w-bit costs. The data-head
trace is not the program-head trace or a free random-access model.

The Python backend checks algebra and this specified accounting. It does not
implement a full physical tape compiler or benchmark runtime. Port-specific
head travel can differ between schedules; 308 versus 332 alone does not prove
a total runtime advantage for every backend. No precision or rounded-linearity
claim is made. The nonlinear control restores z but has a dirt-dependent output.

## Completed coverage, provenance and handoff

The search domain is exactly six repeated-operator source-path classes, with
counts (4,2,2) and balanced signs, plus the (2,2,2) lower-bound class. Stopping
rule: exhaust these domains, no stochastic pruning or further search. Independent
coverage is 720 support paths and six times 10,080 repeated paths, with feasible
counts 544,544,512 for each orientation. These censuses support the explicit
words; the global positive-price lower bound follows from the reduction above.

The checker additionally covers 378 dense basis/dirty cases, seven rational
price order/tie fixtures, literal recursive expansion, all data restoration,
and exact expected invoices. test_package.py has 47 controls, including every
root query's deletion and sign flip, noncommuting factor order, lost input
dirt, missing/aliased/unpaid work, a valid nonoptimal word, invalid prices,
nonlinear readouts, and optimized-process source/certificate/receipt corruptions.
It relocates the package and requires byte-identical deterministic regeneration.

Exact experimental base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
SOURCES.json pins the retained PR944 texts from that base and the read-only
orientation context. Mutable selected-pointer context is recorded, not consumed
by the standalone mathematical checker. The selected PR942/T37 construction
and conditional kappa `1661960547713947/10^18` remain unchanged.

The pattern has not been located or hosted in a selected supplier. Common-label
and mutable-source realization, compatible frames, owner/whole-call admission,
all-size compilation, precision/tape and outer analytic transfer remain open
or inherited. No binding supplier improvement, new moment/kappa, architecture-wide
optimum or full theorem is claimed. The exact query-alphabet optimum is broader
than a finite price search but narrower than an arbitrary-circuit optimum.

See CLAIM.md for task selection/overlap, VALIDATION.md for execution, and
NOTICE.md for contributor attribution and substantial AI assistance.
