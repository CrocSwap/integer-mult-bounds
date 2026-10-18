# A guarded Boolean caller for the complete prelude/A scalar layer

## Statement

Use the two PR3076 words and their exact native streams retained by PR3090 at
`47a2bcec53667f490df6d40550e14a8ae465cba4`. The scientific main baseline is
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
[FROZEN.json](FROZEN.json) pins every reused byte and its predecessor commit.

Let normalized real and imaginary input components be integers in
`[-2^(P-1), 2^(P-1)-1]`, with `3 <= P <= 128`. Retain the exact residual
adapter endpoint premise, the canonical frame interpretation, Gaussian
monomial warp semantics and conjugated frames in the backward orientation.
PR3090's common capacity is seven fractional bits and `W=P+20` signed bits.

Conditioned on supplying each intervening non-scalar operation with that
contract, every ordinary prelude/A scalar can execute with the reversible
Boolean circuits here. Each ADD preserves its source. All `W-1` owned carry
bits return to zero after every scalar. The direct implementation uses no
coefficient scratch. Both real components can execute serially using the same
carry bank. At `P=64`, W=84 and the bank has 83 bits.

The result covers 5,964 prelude scalars and 4,028 A scalars per provider and
orientation, ending immediately before centres. It gives Boolean gates for
the scalar subsequence and an authenticated dispatch/count, conditional on
non-scalar operations. It does not give an executable full native computation.
In particular, residual adapter interiors, frame conversions, climbs, warps,
recursive children, centres/later consumers, clean-stock production, routing,
ownership and the complete physical/recursive invoice remain obligations.
The selected kappa and paid recursive profile do not change.

## From the native capacity to integer scalar guards

For a normalized correlated row u in a rank-r common frame, the inherited
paired Fourier bound gives fractional depth at most `d(u)+ceil(r/2)` and
component magnitude at most `L*N(u)*2^ceil(r/2)`, where `L=2^(P-1)` and N is
the sum of absolute row coefficients. The same bounds hold in conjugated
backward frames. Real scalar operations commute with these frames.

A physical scalar component v is encoded as the integer `V=2^7*v`. The cold
replay reruns PR3090's complete native compilation and two coefficient-row
interpreters, and compares its entire receipt with the pinned predecessor
receipt. The new guard ledger explicitly checks every ADD source, target
input, increment and target output, plus every target-walk/scale recipe
prefix on its actual correlated rows. It checks the same common capacity.
Unchanged fields retain their preceding bound. The inherited entrance and
conversion checks supply their bounds when a non-scalar operation changes a
frame. These are inherited semantic premises, not new Boolean converters.

For ADD coefficient `q=n/2^k` in lowest terms, integer target input and output
imply integer increment `q*S`. Since the encoded source S is integer and n
is odd when k>0, `2^k` divides S. Thus source divisibility is established for
every reached ADD; it is not assumed from a coefficient histogram. The
explicit source-row check also establishes source representability.

For SCALE, the exact prefix ledger establishes each negation's signed range,
each HALF's even input, and each DOUBLE's signed range. A final endpoint
check alone is insufficient: negating the most negative integer before
halving can overflow although the final scaled result fits. The public
`guards` function rejects that invocation. Actual native rows satisfy the
stronger prefix conditions through the inherited capacity bound.

The complete inherited envelope has component magnitude at most `4896*L`
forward and `934*L` backward. Since `4896*128 < 2^20`, W=`P+20` gives a strict
symmetric signed margin for every allowed P. This is a sufficient capacity,
not a claim of a sharp minimum. The new scalar-only guard ledger is recorded
in [RESULT.json](RESULT.json).

## Reversible primitives

### ADD and subtraction

The byte-identical PR3080 [bitadder.py](bitadder.py) supplies a read-only
shifted-source ripple adder. For an active width n>=2 it uses `4n-5` CNOTs
and `4n-6` Toffolis, clearing its n-1 carry bits. The forward carry equation
is `c_(i+1) = a_i*b_i XOR c_i*(a_i XOR b_i)`. Its reverse sweep uncomputes
each carry before writing the lower sum bit. Reversing all gates subtracts
at the same price. The predecessor contains the induction and exact code.

A left shift j uses the upper W-j target bits. A right shift k reads source
bit i+k, with repeated source sign controls beyond the width. These are
explicit control connections, not moved or modified source registers. When
`2^k` divides S, the represented value is exactly S/2^k modulo `2^W`.
Routing and the production of the owned carry bank are separate costs.

An exact signed-power expansion of q composes these shifted additions and
subtractions. Every summand restores its carry bank. Intermediate bit strings
may wrap modulo `2^W`; no signed-real interpretation is imposed at those
cuts. The final modular sum is the exact signed endpoint because that endpoint
fits W bits. Consequently this ADD does not need coefficient-construction
scratch or physical HALF/DOUBLE operations on the source or target.

### HALF and DOUBLE

HALF uses a rotation implemented by W-1 adjacent SWAPs. Each SWAP is three
CNOTs. Move bit 0 to the top and shift the other bits down. For even input,
the new top bit is zero; one CNOT from the relocated sign bit fills it with
the old sign. This is arithmetic division by two, with exactly `3W-2` CNOTs.

Reverse those gates for DOUBLE. A representable exact doubling has equal
old top and next-to-top sign bits. The inverse sign-fill clears the top bit;
the inverse rotation moves that zero into the low position. Thus DOUBLE is
exact on its guarded range, at the same charged price. Neither operation
erases an unknown bit. Both are reversible permutations on all bit strings;
the arithmetic meaning uses the stated input guard.

### NEG

Compute `c_i = OR(t_0,...,t_i)` for i=0,...,W-2 into clean carry bits. The
first prefix uses one CNOT; each further OR uses two CNOTs and one Toffoli.
Then flip t_i, for i>=1, controlled by c_(i-1). This preserves the least
significant set bit and flips all more significant bits, which is negation
modulo `2^W`. The zero word stays zero.

Divisibility by every power of two is invariant under negation. Therefore
each lower-prefix OR has the same value before and after the flips. Running
the prefix computation backwards on the changed target clears every carry.
The total is `5W-7` CNOTs and `2W-4` Toffolis, or `7W-11` gates. Exact signed
NEG additionally requires its guarded endpoint to fit. The SCALE prefixes
supply that guard. Combining NEG with guarded shifts implements every reached
power-of-two SCALE and its original instruction order.

## The explicit comparison

The comparison is a newly implemented reversible interpretation of PR3078's
literal target-walk recipes, rather than a claim about an existing bit compiler.
Every unit ADD uses the same unshifted ripple adder; HALF, DOUBLE and NEG use
the circuits above. COPY into initially-zero coefficient scratch uses W CNOTs.
A scratch recipe's final CLEAR is replaced by the inverse of its complete
source-only preparation, including all copies, shifts and additions.

The preparation reads only the preserved source and writes scratch. The target
ADD therefore leaves that preparation's inputs unchanged. Its inverse returns
scratch to zero while holding the updated target fixed. It retraces already
certified scratch prefix values, so it needs no larger capacity. This charges
cleanup without using destructive CLEAR. The direct caller avoids that scratch
entirely. All non-scalar costs are excluded equally from this local comparison;
they must be included in a later complete bill.

For both real components, each provider and orientation at W=84 has:

| Implementation | CNOTs | Toffolis | Total gates | Local data/carry bits |
|---|---:|---:|---:|---:|
| Reversible target-walk control | 17,163,992 | 6,593,136 | 23,757,128 | 335 |
| Direct scalar caller | 6,806,482 | 6,426,884 | 13,233,366 | 251 |
| Saving | 10,357,510 | 166,252 | 10,523,762 | 84 |

The bit figures refer to one target/source pair with serial real components,
not total supplier storage. They are `4W-1` and `3W-1`; carry is explicit,
clean and reusable between macros. No inherited private buffer is removed or
borrowed. The 91 native cleanup buffers remain part of the supplier contract.
CNOT and Toffoli are reported separately; their sum is an unweighted logical
gate count, not runtime or a physical technology tariff.

For `23 <= W <= 256`, the literal tariff formulas are:

```text
                         CNOT                  Toffoli
control            206466*W - 179152       79928*W - 120816
direct              82274*W - 104534       77936*W - 119740
saving             124192*W - 74618         1992*W - 1076
```

Each shifted adder has at least two active bits throughout this width domain;
the primitive tariffs above are affine, and the fixed source histogram fixes
their multiplicities. Summing them proves these formulas. Literal recounts
at W=23,64,84,148,256 corroborate them. The native P domain uses W=23,...,148.
This extends the earlier ADD-only and local half-ADD work by supplying SCALE,
all reached caller guards and a complete scalar-layer comparison. It does
not claim new elementary arithmetic algorithms, optimality, or a kappa gain.
