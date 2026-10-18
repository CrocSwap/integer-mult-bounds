# An aligned reversible ADD layer

## Contract

A macro has a read-only source register and an arbitrary target register, each
with W bits in two's-complement representation and a common binary point.
There are W-1 disjoint, owned carry bits, initially zero. They must return to
zero. These are clean ancillas, not arbitrary borrowed dirty bits.

For the reduced dyadic coefficient q=n/d, exact arithmetic requires the encoded
source integer S to be divisible by d. The circuit's unconditional endpoint
statement on that domain is

`(S,T,0) -> (S, T + q*S mod 2^W, 0)`.

If the signed integer `T+q*S` is in `[-2^(W-1),2^(W-1)-1]`, the endpoint also
equals the exact signed ADD. Alignment and the signed endpoint bound are caller
premises. They are not inferred from the native compiler's real-arithmetic
column checks. Different source and target binary points require the
corresponding exponent adjustment before using this contract.

## Read-only ripple addition

First consider adding the W-bit integer A, whose bits are read-only controls
`a_i`. Let `b_i` be the original target bits, and set `c_0=0`. The carry equation is

`c_(i+1) = a_i*b_i XOR c_i*(a_i XOR b_i)`.

For W>=2, compute `c_1=a_0*b_0` with one Toffoli, leaving `b_0` unchanged.
For each `i=1,...,W-2`, execute

```text
Toffoli(a_i,b_i; c_(i+1))
CNOT(a_i; b_i)
Toffoli(b_i,c_i; c_(i+1))
```

The new carry is correct, and the target bit holds the propagate value
`p_i=a_i XOR b_i`. Write the top sum bit with `CNOT(a_(W-1); b_(W-1))`
and `CNOT(c_(W-1); b_(W-1))`. Overflow is intentionally discarded modulo 2^W.

For `i=W-2,...,1`, execute

```text
Toffoli(b_i,c_i; c_(i+1))
CNOT(a_i; b_i)
Toffoli(a_i,b_i; c_(i+1))
CNOT(a_i; b_i)
CNOT(c_i; b_i)
```

The first three gates uncompute `c_(i+1)`, because lower target bits and `c_i`
still hold their forward values. The last two leave the correct sum bit
`p_i XOR c_i`. Finally erase `c_1` with `Toffoli(a_0,b_0;c_1)`, then write
`b_0 XOR a_0`. This proves the complete modular map and clean-carry return
by induction. No gate writes any source bit. The gate list contains exactly
`4W-6` Toffolis and `4W-5` CNOTs. For W=1, one CNOT suffices.

Each gate is self-inverse. Reversing the entire gate list therefore implements
subtraction for every target at the same cost and returns the carries to zero.

## Shifted source controls

For a left shift by j>=0, the low j target bits stay unchanged. Use the adder
only on the upper `max(0,W-j)` bits, taking its source controls directly from
the corresponding original source bits. Bits shifted above the target width
are discarded modulo 2^W. For a right shift by k, use source bit `i+k`, or
the source sign bit when that index is above the source width. Repeated sign
controls are legal because the source is never written.

If `2^k` divides S, those controls are the low W bits of the exact integer
`S/2^k`. Without divisibility they represent an arithmetic right shift, which
can differ from exact division. For example, exact `3/2` is not an integer
target increment. The API rejects that invocation rather than claiming a
precision result.

## Signed powers and modular intermediates

`terms` derives an exact signed-power expansion with at most nine iterations
for its bounded numerator domain. At each odd numerator, choose the low digit
`2-(n mod 4)`, except for the final numerator one. Subtract that digit, divide
by two, and increment the exponent. The executable rational reconstruction
checks the coefficient identity. Binary expansion is the control policy.

For example, `7/4 = -1/4 + 2`, and `3/2 = -1/2 + 2`.
Execute each shifted addition or subtraction using the unchanged original
source, restoring carries after each term. Summing the modular maps proves
the macro contract. A signed partial sum may wrap, even if the final signed
endpoint fits. Such wrapping is permitted. The internal bit strings have
modular semantics, not an exact signed-real interpretation after every gate.
There is no extra arithmetic source or target guard field in this circuit.
The base-format divisibility and permanent endpoint-width premises remain.

These elementary identities and the ripple construction are not claimed as
new algorithms. No Boolean optimality or unrestricted circuit lower bound is
claimed.

## Source-bound comparison

The frozen PR3076 producer checks 24 exact commuting contractions of the
PR3060 word and derives its inverse cleanup. This package reuses that proof
and producer, retaining attribution. It runs the inherited native transport
and emitter freshly for both parent and candidate providers. Their forward
and backward programs agree literally on every non-ADD event. In particular,
all climbs, centres, warps, SCALE/COPY/CLEAR events, helper widths and private
buffers remain present. Native checks preserve all 632 live input columns and
the paid profile `{1:2433,2:712,3:232,4:108,5:18,8:8}`.

For each literal ADD occurrence, both real components use the selected
coefficient template. The verifier serializes the W=64 templates, reads them
back, counts their gates, and independently aggregates their counts by the
actual emitted coefficient histogram. It requires agreement with the adder
formula. It does not serialize millions of repeated bit gates as a new flat
physical program.

For every W>=5 in the supported domain W<=256, each active adder has at least
two bits for this source alphabet. Thus the literal tariff is affine in W,
with coefficients in `RESULT.json`. Compared with the parent's binary policy,
the candidate's signed policy saves exactly

```text
Toffoli: 384*W - 144
CNOT:    384*W - 48
```

per provider and orientation. At W=64 this is 24,432 Toffolis and 24,528 CNOTs.
Using signed powers on both sides, PR3076 itself saves `352*W-272` Toffolis
and `352*W-184` CNOTs. Its saving under PR3078's separately certified exact
real recipes is 36 unit instructions per provider and orientation, rather
than the conservative native bound's 340 units.

This is a conditional ADD-layer gate-count improvement. The gate circuit is
proved for its format contract; the actual native caller has not been shown
to meet every alignment and range premise. Clean-carry storage/backing,
source routing, sign-control fanout, non-ADD physical execution, precision,
all-size/compiler and supplier/outer obligations are additional. The recursive
profile and kappa do not change.
