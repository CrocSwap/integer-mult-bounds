# Four source XORs are necessary and sufficient at ten queries

## Contract and statement

Use the exact common-map interface of [PR1340](https://github.com/CrocSwap/integer-mult-bounds/pull/1340),
pinned at `f1dcab36fa63f8226f70dd07e26f44afb9d39b51`. Its original
[proof](sources/PROOF.md), [README](sources/README.md) and certificate are
preserved byte-for-byte. There are five distinct arbitrarily dirty source rows
`x_j`, 31 distinct dirty outputs `y_m`, a distinct dirty connector `z`, and
distinct dirty private scratch. All are length-L vectors over F2. The exact
linear maps B and A_m are fixed and read-only, and need not commute or be
invertible. B is the **same map at every source port**.

The allowed complete calls are:

* Q_j: `z += B x_j`;
* R_m: `y_m += A_m z`;
* X_{s,t}: `x_t += x_s`, with s != t.

Every call preserves its source and other rows, restores its private scratch,
and returns its heads to the promised positions. Its additive behavior is
independent of the old target value. No source or output may be observed
externally until batch completion. No other data operations or scratch aliases
are admitted. The straight-line word cannot depend on data contents. The
required exit is

    y_m += A_m B(sum_{j: bit_j(m)=1} x_j),  1 <= m < 32,

with every source, connector and scratch row restored.

**Theorem.** Among words correct for every admissible B, A_m and dirty input,
with exactly ten Q calls and exactly two R_m calls for each output, the minimum
number of complete source XORs is four.
This is a source-XOR minimum under fixed query/readout counts. It does not give
the weighted optimum over other counts or other operation alphabets.
Specialized maps, operator relations or restricted inputs can be cheaper; the
minimum concerns the generic interface.

PR1340 already proves that ten queries is the smallest possible with paired
readouts, allowing arbitrary source shears. That result is credited there and
is not a new claim of this package. The new lower bound concerns source XORs.

## A four-XOR construction

Use the closed connector coefficient path

    0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0.

Its ten edge masks are

    4, 1, 4, 2, 4, 1, 8, 18, 12, 16.

The first seven and last edges are single-source queries. For edge 18, execute
`x_1 += x_4; Q_1; x_1 += x_4`. For edge 12, execute
`x_2 += x_3; Q_2; x_2 += x_3`. Each source restores immediately on its edge,
and the total source-XOR count is four. Linearity implements the two combined
queries without an additional full row.

The 32 differences of these boundary values include every five-bit mask.
For each nonzero mask m, choose the first pair (s,t) in lexicographic boundary
order whose XOR is m; [CERTIFICATE.json](CERTIFICATE.json) records every pair.
At boundary s the connector is

    z_initial + B(sum_j bit_j(q_s) x_j).

The two R_m calls cancel `A_m z_initial` and produce the required output.
The closed path restores z. Distinct outputs allow readouts to commute; they
do not change z or the sources. This establishes the map for every L and all
admissible maps and dirty inputs.

The path was found by omitting boundaries 8 and 10 from Ross Richardson's
PR943 twelve-toggle repair: `0,4,5,1,3,7,6,14,12,28,24,16,0`. This is an explicit
reuse of that construction, with two paired source mutations replacing four
single-source query edges. No priority for the original path or dirty echo is
claimed.

## Why fewer than four XORs cannot suffice

Specialize to L=1 and B=A_m=identity, with every incoming source and z bit
independent. This specialization is necessary for any generic valid word.
The source projection must be the identity at exit. Q and R never modify a
source, so this projection depends only on the source-XOR subsequence.

On five source coordinates there are exactly 20 directed elementary XORs.
The exact complete census of subsequences of lengths 0,1,2,3 gives respectively
**1,0,20,0** identity words. Every length-two identity is the same XOR repeated.
The primary implementation uses row images; the separate implementation uses
column bit images. Both check all `1+20+400+8000=8421` words. Projection makes
this finite census apply regardless of how queries and readouts are interleaved.

With zero XORs, restoring z forces every query-label count even. Full difference
coverage requires the directions to span F2^5; at ten queries, all five basis
directions therefore occur exactly twice.

For two XORs, rename their donor s and target t to 0 and 1. Between those XORs,
Q_t adds the direction `e_t+e_s`; outside them it adds `e_t`. Every other query
adds its ordinary basis direction. Let c_j count all queries to label j, and
let p count Q_t queries between the XORs. Connector restoration implies

    sum_j c_j e_j + p e_s = 0  (over F2).

Thus c_j is even for j != s and c_s equals p modulo two. Since
`sum_j c_j=10` is even, p is even and so are all c_j. Full coverage requires
the directions actually used to have rank five. There are only two possibilities:

1. All five labels occur twice. Then p is 0 or 2, so precisely one of `e_t`
   and `e_t+e_s` occurs. The five effective directions form a basis, each twice.
2. Exactly four labels occur. They can span five dimensions only if the absent
   label is s, label t occurs four times, the other three occur twice, and
   p=2. The effective directions are `e_t`, `e_t+e_s` and those other three
   basis vectors, again an independent basis with each direction twice.

Fewer than four active labels cannot span five dimensions: only t can contribute
an extra direction. These alternatives also exhaust the even multiplicity
vectors in the executable check. No restriction is imposed on the positions
of the repeated source XORs or on the readout positions.

In each surviving case, an invertible source coordinate change reduces the
connector path to ten steps on five independent directions, each used twice.
Paired readouts give only XOR differences of path prefixes. Rename the directions
by their first occurrence: the ten-step words are exactly the 945 pairings of
ten positions. PR943's complete obstruction has maximum coverage 31 of 32.
We recheck all 945 by two methods, agreeing on every coverage set and its digest:
restricted-growth words with pair differences, and endpoint matchings with
integer Walsh autocorrelation. Its histogram is

| Coverage | 16 | 19 | 21 | 22 | 23 | 24 | 26 | 28 | 31 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Words | 42 | 120 | 180 | 56 | 45 | 220 | 110 | 150 | 22 |

Therefore zero or two XORs cannot realize all 31 masks; one or three cannot
restore the sources. Four is attained by the construction. The all-size linear
argument and source projection are written proofs; the two finite exclusions
are exact computational certificates, not proof-assistant theorems.

## Complete conditional invoice

Let b, a and x be uniform **complete** prices for Q, R and source XORs.
Let I+P pay admission and coefficient preparation, and D_4 pay the actual
remaining schedule construction, storage, control and dispatch. The bill is

    C_4 = I + P + D_4 + 10b + 62a + 4x.

The predecessor's bill is `I+P+D_12+10b+62a+12x`. Thus the new schedule is
cheaper precisely when `D_4-D_12 < 8x`, under this shared uniform tariff and
the same preparation/admission contract. Port-dependent prices require actual
per-call sums: fewer instructions alone does not order arbitrary routing costs.

Against PR943's two read-only repairs, the exact conditions are

    4x + D_4 - D_source < 2b,
    4x + D_4 - D_output < 2a.

The inherited map/readout-only minimum is `10b+62a+2min(a,b)`; the two repair
words and that lower bound are retained predecessor results. This new package
does not optimize words with extra readouts or queries.

For the predecessor's five-factor fixture, lower each B and A_m through its
balanced contiguous dirty echo, retaining every inverse and child. With five
factors there are 28 map leaves, nine executed internal nodes and peak depth
three. The root connector plus three private dirty rows gives four borrowed
rows; source mutations need no extra full row. The recurrences are

    ell(1)=1; ell(d)=2ell(floor(d/2))+2ell(ceil(d/2));
    n(1)=0; n(d)=1+2n(floor(d/2))+2n(ceil(d/2));
    h(1)=0; h(d)=1+max(h(floor(d/2)),h(ceil(d/2))).

| Quantity | PR1340 | This word | Each read-only repair |
|---|---:|---:|---:|
| B / A calls | 10 / 62 | 10 / 62 | 12 / 62 or 10 / 64 |
| Arbitrary-map leaves | 2016 | 2016 | 2072 |
| Complete source XORs | 12 | 4 | 0 |
| Executed internal nodes | 648 | 648 | 666 |
| Root instructions | 84 | 76 | 74 |
| Borrowed dirty rows | 4 | 4 | 4 |

Under PR1340's abstract tariff paying one unit per complete map leaf, source
XOR, internal node and root instruction, this is **2744 versus 2760**, or
**2812** for either read-only repair. The new saving is 16 tariff units against
PR1340. This is an abstract complete-price comparison, not measured physical
runtime. Complete source XORs must pay row reads/writes, head travel and return,
loop/index work, precision and instruction access. Every child similarly pays
coefficient/source access, restoration, frames and head returns. The retained
predecessor proof gives an explicit dense tape implementation; no favorable
physical tariff is established here.

## Scope

The code checks universal free noncommutative maps on all 40 formal incoming
dirty rows, forward and inverse root/expanded words, and separately instantiated
dense F2 maps at L=1,2,3,4. Source immutability, distinct heterogeneous B_j,
nonlinear or rounded leaves, externally observed temporary sources, other source
operations and scratch aliases are outside the contract. Exact matrix tests
support implementation checks; the algebraic identity establishes all L.

There is no selected-supplier instance, native compiler admission, physical
owner/frame/precision/tape admission, all-size outer transfer, complete cold
replay, proof-assistant multiplication theorem or new kappa. The selected
frontier is unchanged. Source credits and exact pins are in README.md,
SOURCES.json and PREDECESSOR.json.
