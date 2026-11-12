# Sequential production of the actual monomial phase

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Source contract and result

Jose Manuel's [PR #2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250)
implements the Gaussian monomial with the retained
[source phase formula](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/selected-complex-compact-adapters/monomial.py).
Its phase_pass calls tensor_phase on decoded addresses. This package replaces
that address oracle with sequential counter tapes. The retained algebra and
Gaussian coefficient operations are not new results.

Fix a compiled recipe of dimension m>=1. Its linear coefficients alpha_i are
in Z/4, its quadratic bits Q_ij use only i<j, and its absolute phase is p0.
The supplied physical mask has b>=1 binary symbols followed by END. Its
ones identify active low-bit positions in each of m equal-width fields.
For the source geometry, b=fK and the ones are rho+jK, 0<=j<f. The mask is
read-only and starts at its origin. It is an explicit supplied input; this
package does not manufacture it from encoded f,K,rho.

Enumerate the m b-bit address fields lexicographically, with the last field
fastest. Put R=2^(mb), and let x_ij be bit j of field i. The required phase is

```text
p(x) = f p0 + sum_(active j) [sum_i alpha_i x_ij
                            + 2 sum_(i<k) Q_ik x_ij x_kj] mod 4.
```

The producer emits exactly this four-state phase at each record. It receives
neither b, f, R nor a decoded address as runtime control data. It uses m owned
counter tapes, one borrowed mask and fixed recipe tables. All heads start at
their current segment origins after LEFT; arbitrary ancestor prefixes are
preserved. At completion the counter segments are blank and all heads and the
mask return exactly. No complete phase table is stored.

The complete physical read/write/unit-move bill is at most

```text
32(m+1)(R+b+1).
```

For fixed recipe dimension, this is linear in the complete record count plus
initial mask width. There is no per-record factor b or f. This is a concrete
source-specific construction. Binary-counter amortization is classical;
Cinna Davis's cached chirp construction and Ryanson Jonathan's
[PR #4325](https://github.com/CrocSwap/integer-mult-bounds/pull/4325)
are credited related predecessors. Their
[pinned audit](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/pr4100-chirp-odometer-tariff/README.md)
uses cached table products at a different port, not this quadratic bit phase.

## Initialization and phase update

Scan the physical mask once. For each bit, append zero to every counter.
When the mask bit is one, add p0 to the phase state modulo four. Thus the
initial phase is f p0 without decoding f. Append END to each counter and
restore all heads. Each counter now holds the corresponding address field
in least-significant-bit-first order.

Advance the last field by a binary carry. At a changed bit j, all counter
heads and the mask head stand at j. Read its old value x from counter i.
If the mask is active, update the phase by

```text
delta = (1-2x) alpha_i + 2 sum_(k != i) Q_(min(i,k),max(i,k)) x_kj mod 4.
```

Then replace x by 1-x. The linear part changes by the displayed signed term.
Each quadratic term changes by plus or minus 2 x_kj; these are equal modulo
four. No diagonal or lower-triangular raw Q entry is used. Thus this update
is exactly the difference of the retained source polynomial.

If x was zero, the increment is complete. Rewind all heads to their current
LEFT markers. If x was one, move every counter and mask one cell right and
continue the carry. At mask END, check all counter END symbols, rewind, and
carry into the preceding field. When all fields wrap, the complete domain
has been consumed. The counters are zero again, and the phase returns to its
initial value. Erase every counter bit and END, then restore its head.

Induction over bit flips proves phase correctness. Standard binary carry
induction proves lexicographic order, no omitted or repeated record, and exact
termination after R outputs. All variable-sized progress is encoded in head
positions and counter cells. Recipe indexes, current symbols, phase and carry
range over fixed finite sets. The executable is a finite-symbol program; a
separate native transition-table compiler or proof-kernel artifact is not supplied.

## Complete action and space proof

A rewind from offset h costs 2h+3 actions. Initialization, including checking
empty counter owners, writing END and restoring the borrowed mask, costs

```text
(4m+4)b + 8m+4.
```

Consider one field increment which changes t>=1 bits. Each changed bit costs
at most m+2 reads/writes for the mask, old bit, cross terms and update. Carry
movement costs at most (m+1)t. The final rewinds cost at most
(m+1)(2t+3). END checks cost at most m+1. The total is at most
(4m+5)t+4(m+1), hence at most 9(m+1)t.

Across all R increments, including the final wrap, the global mb-bit counter
changes exactly 2R-2 bits. Grouping them by field does not change that sum.
Therefore all advance operations cost less than 18(m+1)R. Counter cleanup
costs m(5b+9), including each erased END, blank check and final rewind.
Combining these quantities gives the stated conservative bound.

The owned counter bodies use m(b+1) cells, plus their LEFT markers. The
borrowed mask uses b+1 body cells plus its LEFT marker. Blank counter backing
remains physical capacity after cleanup. Fixed recipe tables contain O(m^2)
compiled bits. There is no R-entry phase cache. The caller consumes each
four-state output before advancing; it must pay for any retained copy.

## Actual Gaussian consumer

apply_phase retains the source's real/imaginary coefficient loop, with two
coefficient scratch tapes and one-bit negation carry. Its loop is driven by
physical counter overflow, not layout.records or layout.decode. It consumes
one Gaussian coefficient per record in the demonstrated ABI. Multiple packed
coefficients require a separately bound repetition grammar.

For coefficient width p>=2 and V=2pR payload bits, the retained coefficient
path uses exactly 18V source tape actions when erases are counted as one
operation per erased cell. This includes input consumption and erasure,
coefficient scratch cleanup, and output head return. The new complete local
phase/coefficient interval therefore costs at most

```text
18V + 32(m+1)(R+b+1).
```

The input is owned and consumed. A caller which must preserve it needs a paid
copy. Borrowed mask and dirty counter ancestors are preserved. The output is
separately owned; its V cells and the two p-cell coefficient scratch bodies
remain charged. Coefficient primitives retain their source representation
and precision assumptions. Equality is exact modulo 2^p; ordinary Gaussian
integer interpretation also needs the source's symmetric headroom condition.

For an inverse monomial, apply the negative phase after the affine inverse
has recovered the input coordinates. This producer does not authorize phase
evaluation on unrecovered output coordinates. Zero-coefficient equal-width
spectator fields can be inserted into the compiled recipe; their counters
still determine physical record order. Other mixed-width packing geometries
remain a caller integration obligation.

## Evidence and limits

The actual recipe is the retained family 65689/event 8814 right recipe, with
offset 426 and absolute phase 1. Its affine map is not executed by this package;
only its phase is supplied here. The source binding and native scalar theorem
remain inherited from the pinned package, not independently rederived.

The verifier checks 224 generic complete domains with 9760 records. Three
actual source domains contain 512,262144,262144 records. They cover f=1,K=1,
f=2,K=1, and f=1,K=2,rho=1, including inactive bits and the nonzero tensor
constant. Six 1024-record payload cases include an independent spectator bit,
both signs and dirty ancestor lengths 16,257,4096. They match the unchanged
source output, a separate modular Gaussian oracle and every coefficient
meter field. Each adds 120506 physical phase actions. Six malformed-state
controls reject. Failed ABI calls need not restore partial work.

Mask manufacture, arbitrary mixed-width caller packing, affine routing,
recursive C, physical owner allocation, production codebook, full monomial
invoice, native/stock/precision and outer recovery remain separate. No full
147-bit production payload was materialized. The complete kappa calculation
and selected frontier are unchanged. Independent human and proof-kernel
acceptance remain open.
