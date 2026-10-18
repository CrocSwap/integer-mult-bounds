# Paired negation, exact boundary and complete invoice

## Proposition and scope

Let `4 <= W <= 256`. Let `x` and `y` be the two W-bit component words of one
Gaussian target entry, with one distinct initially zero carry bit `c`.
Both component words are exclusively writable for the duration of the macro.
There is a literal reversible CNOT/Toffoli circuit on these `2W+1` wires with
endpoint `(-x mod 2^W, -y mod 2^W, 0)`. It needs no additional dirty or clean
component word. Its CNOT and Toffoli counts are respectively `16W-16` and
`8W-12`. This is a constructive tariff, not an optimum.

At the inherited signed SCALE boundary, each component separately obeys the
PR3094 canonical recipe guards. Pair negation followed by the original guarded
HALF/DOUBLE operations therefore implements the identical Gaussian SCALE.
The statement is conditional on availability of those encoded component words;
it does not establish their physical access cost or a complete supplier.

## Modular identity and carry

Work in the ring `R = Z/(2^W)`. Execute these four shears in order:

```text
x += y       (x+y, y)
y -= 2*x     (x+y, -2*x_original-y_original)
x += y       (-x_original, -2*x_original-y_original)
y -= 2*x     (-x_original, -y_original)
```

Each shear is invertible over R. The displayed calculation proves the whole
identity for every input bit pattern, including either minimum signed value.
Intermediate words may wrap modulo `2^W`; the Boolean circuit loses no
information and does not expose these words to the native consumer.
There is no additional signed range or alignment condition on the shears.

The inherited wired MAJ/UMA `adder(A,B,c)` implements `B += A mod 2^n`,
restores A, and returns c to zero. For `n>=2` its literal list contains
`4n-2` CNOTs and `2n-2` Toffolis. Reversing the list implements subtraction
with the same source/carry return. The primitive and its earlier realization
are credited to Cuccaro, Draper, Kutin and Moulton and PR3081/3152.

For `x += y`, use all W bits of y and x. For `y -= 2*x`, use the low `W-1`
bits of x as source and bits `1..W-1` of y as target. Leave y's bit 0 and
x's bit `W-1` outside that shortened adder. This is exactly subtraction of
twice x modulo `2^W`, with no physical shift, sign-fill word or lost bit.
The two wire sets and c are disjoint. Each adder returns c before the next
shear. Thus the same single carry serves all four steps.

Two W-bit and two `(W-1)`-bit adders give the claimed tariff:

```text
CNOT     2*(4W-2) + 2*(4*(W-1)-2) = 16W-16
Toffoli  2*(2W-2) + 2*(2*(W-1)-2) =  8W-12
```

Literal inverse gates recover the entire initial pair and c. Exhaustive checks
cover every bit pattern for widths 4 through 8; that finite check supports the
implementation, while the ring argument supplies the uniform identity.

## Signed SCALE and native ownership

Normalize `q = a/b` as a rational, including negative-denominator encodings.
SCALE here has `q = +/- 2^e`. Its canonical recipe negates if q is negative,
then performs `abs(e)` DOUBLE or HALF operations. Before executing the pair
circuit, `pairscale.scale` checks the inherited recipe guards for each component:

1. The input and the negation prefix fit the signed W-bit interval.
2. Every HALF prefix is even.
3. Each shifted prefix fits the interval and the endpoint equals `q*value`.

The normalized coefficient additionally obeys the inherited `abs(numerator) <=
255`, `denominator <= 4096` and power-of-two conditions. At the widest legal
negative HALF exponent the new pair circuit has 24,500 gates, while its control
has 29,112. The pair evaluator validates and applies at most two 20,000-gate
batches through the unchanged inherited interpreter. It retains the full state
between batches; no carry-reset or partial endpoint is assumed at a batch cut.

The modular NEG endpoint equals signed negation under these guards. The
componentwise shift circuits therefore receive exactly their original legal
inputs and produce the original exact signed result. In particular negative
HALF on `-2^(W-1)` stays rejected even though its final half-sized result fits.
The added modular internal microstates create no stronger alignment condition
and no rounding error. A literal signed SCALE recipe's inverse recovers its
legal input pair, because every constituent Boolean gate is reversible.

Native SCALE multiplies the Gaussian target by a real Fraction. Both component
words receive the same q, so they can participate in the one paired circuit.
For each coordinate, the first W wires are its real word, the next W its
imaginary word, and wire `2W` is c. This is the complete logical bank assignment.
For a multiple-coordinate role, process its coordinate pairs serially and reuse
c; multiply the scalar-pair tariff by the number of processed coordinates.
Neither component word is required to be initially zero or disposable.

The freshly emitted forward programs in both providers have native event 6872
`['scalar', ['scale', ['L', 292], 1, -1], 0]`. The immediately following event
reads L292 in `ADD(L333,L292,-1)`. Apply the pair circuit to the Gaussian
coordinates of L292, leave every other role untouched, and return c before that
read. The component-pair outputs satisfy exactly the old SCALE endpoint.
RESULT.json binds those events to the complete fresh dispatch hashes.

This names the same target owner and its macro lifetime, but does not bind
physical tape addresses, movement time, routing or a scheduler's exclusive
access grant. Those costs remain unknown. ADD's temporarily writable source,
all residual adapters, non-scalar native execution and the later consumer are
separate inherited or open obligations.

## Comparator and complete count

The exact PR3152 comparator performs one real NEG with three W-bit shears and
one W-bit SWAP, returning its dirty partner. To negate a whole Gaussian pair,
use y as the first dirty partner, then the updated x as the second. This legal
serial control also needs no separate dirty word once this bank assignment
is made. It costs `30W-12` CNOTs and `12W-12` Toffolis for the pair.
The new four-shear construction saves `14W+4` CNOTs and `4W` Toffolis.
The contribution therefore includes both the explicit same-owner bank closure
and a cheaper implementation of that closed boundary.

Fresh replay reconstructs the complete 9,992-scalar prelude/A streams of both
pinned PR3076 providers and orientations. Their dispatch hashes, guard ledgers
and histograms match the retained PR3094/3152 receipts. Each has exactly 462
negative Gaussian SCALEs. Encodings such as `1/-1` and `2/-1` are counted by
their normalized sign, not the numerator's sign. Other SCALE shifts and all
ADD circuits are unchanged.

For the entire scalar layer, counting each emitted scalar macro once on its
Gaussian component pair, the saving over PR3152 is therefore

```text
CNOT     462*(14W+4) = 6468W+1848
Toffoli  462*4W      = 1848W
Total                 8316W+1848
```

These are per-pair scalar-macro counts under the same convention as PR3152.
They are not a complete array execution bill: native roles can have different
coordinate cardinalities, and access/child work is not priced here.
For the retained `23 <= W <= 256` capacity domain, the complete normalized
scalar-layer invoice is `85046W-11324` CNOTs and `41740W-44544` Toffolis.
The circuit is strictly cheaper for every supported width. At W=84, the saving
is `545160+155232=700392` gates. One clean carry suffices, and SCALE requires
only its existing two target component words. Against PR3094 the total logical
gate saving becomes 2,639,210, while CNOTs still increase by 326,058.

The compiler emits the old and new literal circuits, recounts both and checks
the published baseline at seven widths. Every width 4 through 256 has its
literal paired-NEG tariff checked. The formula follows from the displayed
adder counts, the fixed negative-SCALE multiplicity and PR3152's unchanged
ADD/shift invoices. No new recursive rank profile, moment root, kappa,
supplier-admission claim or full multiplication theorem follows from this bill.
