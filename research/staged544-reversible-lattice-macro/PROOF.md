# One actual rank-five residual on a finite lattice

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
This is a finite implementation and an admission discriminator, not a replacement
of the staged544 recursive provider or a new kappa.

## Source and paid boundary

PR3945 at `91f81d131252db704f945891da1ea54e29d46b8b` gives helper 277
an empty entrance and terminal U=[388,74,40,26,1], in both providers.
`bw_adapters.py:S_of,main` constructs its residual T_U and lowers it to
L C_[5] R. The exact serialized L/R recipe is the corresponding PR3987
descriptor at `fc536202fdaa924158789a5ef59ac079bbe21922`; frozen source and
recipe hashes are authenticated before tests. These definitions include all
global/relative phases. The source's charged object is a rank-five recursive
child, tensored with the other coordinates. Its exact compiler's `zero_state`
uses Gaussian integer numerators and a growing denominator; it is a semantic
evaluator, not a paid finite-precision implementation.

We implement this actual 512-coordinate residual with spectator multiplicity f.
No scalar instruction, native mathematical map, selected frontier or recursive
paid profile is changed. The basis-size convention is 512f complex coordinates,
so there are 256f pairs at each of five layers, or 1280f pairs. A source caller
using f for a different tensor-factor exponent must convert that dimension;
there is no silent reuse of an incompatible f convention.

## Reversible half-sum with one dirty word

Data words have b bits, modulus M=2^b; scratch D has b+1 bits, modulus 2M.
Let a,c be signed b-bit integers and s=a+c or a-c. The following operations
are modular, with source sign-extension into the scratch word:

    D += a; D += (+/- c)
    y += floor(unsigned(D)/2)
    D -= (+/- c); D -= a
    y -= floor(unsigned(D)/2)
    y -= (D mod 2) * ((a mod 2) XOR (c mod 2))

The four scratch operations restore every possible initial D exactly. For
integers d,s, floor((d+s)/2)-floor(d/2) equals floor(s/2) plus the product
of their parities. Reducing d+s modulo 2M changes its half by a multiple of M,
which vanishes in y. Signed versus unsigned s has the same property. Thus this
implements y += floor(s/2) mod M independently of D. No low bit is discarded
from a data or scratch register; shifts are read-only source slices. The final
parity correction is essential: a=1,c=0,D=1 gives the wrong increment if it is
omitted. Reversing target updates implements the inverse accumulation.

This costs seven real-word addition/subtraction/conditional-decrement
primitives per component. An explicitly constructed clean comparison starts
D=0 and omits the last two target corrections: five primitives. This comparison
is ours, not a claimed pre-existing physical implementation. Both compute the
same rounded map. The improvement is removal of the clean initialization
requirement for b+1 workspace bits, at a cost of two extra primitives per
half-sum. Scratch is dirty, not absent.

## Literal bit realization and tariff

The gate alphabet is NOT and generalized controlled-X with arbitrary positive
or negative controls. Source-controlled addition of 2^j flips target bits
k=b-1,...,j when source_j=1 and all target bits j,...,k-1 are one.
Descending order leaves the lower controls unchanged. Composing these increments
for each source bit is modular addition; reversing the gate list subtracts.
There are b(b+1)/2 gates, with no ancilla. Sign-extension into b+1 target bits
adds the sign bit at position b as well as its ordinary position; its cost is
b(b+3)/2+1 gates. A read-only right shift uses the existing scratch bits 1..b.

The parity-controlled decrement splits into the two disjoint conjunctions
D0 & a0 & !c0 and D0 & !a0 & c0. For each conjunction, descending target-bit
flips controlled on lower zeros implement decrement. Cost:2b gates; the controls
are preserved source/scratch bits, so no predicate scratch is hidden. A real
word SWAP uses3b CNOTs. Negation uses b NOTs followed by b increment gates.
These conservative counts intentionally retain canceling gates.

The dirty half-sum costs 3b²+9b+4 gates. Its clean counterpart costs
(5b²+13b+8)/2. These circuits are explicitly simulated against the modular
arithmetic specification on all small-bit states. They are finite Boolean
permutations with no clean ancilla. The next paragraphs supply bounded-fanin
counts; the supplier's recursive stock/tape admission remains separate.

For n>=3 controls, the classical borrowed-bit construction of Barenco et al.,
[Elementary gates for quantum computation, Lemma 7.2](https://arxiv.org/pdf/quant-ph/9503016),
implements controlled-X with 4n-8 literal Toffoli gates and n-2 arbitrary
borrowed bits restored. Here is a self-contained reconstruction. Set
A=Toffoli(a1,a2;d1). Let F compute the chain d2^=d1*a3,...,
d[n-2]^=d[n-3]*a[n-1], flip t by d[n-2]*an, then undo that chain.
For n=3, F is just Toffoli(d1,a3;t). The sequence F,A,F,A cancels all terms
involving the initial dirty bits; changing d1 by a1*a2 changes F's target
increment by the product of all controls. F has 2n-5 gates. Negative controls
are conjugated by X before and after. No relative-phase substitute is used.

Every actual pair gate has at most b+2 controls and 5b+1 available data/scratch
bits. After excluding its controls and target, at least4b-2 bits remain, enough
for the at most b borrowed bits. They are selected within the existing pair
and scratch, returned after each gate; no additional clean or dirty workspace
is allocated. This requires transient access to those actual bits, explicitly
part of this implementation's interface. Each generalized gate costs at most
4b core elementary gates plus2(b+2) X gates, giving the bound below.
The executable emits literal X/CNOT/Toffoli gate lists, verifies the borrowed
ladder on every small state, and tests complete pair circuits with dirty data.

## Reversible C pair and completed numerical error

For C=((1+i)I+(1-i)X)/2, define t(d) by componentwise floor of (1-i)d/2.
On two complex words execute

    x -= y; y += t(x); x *= i; x += y.

Each half of t uses the preceding accumulator with the same dirty scratch.
The exact inverse is x-=y; x*=-i; y-=t(x); x+=y. Both are permutations on
all b-bit data states, including overflowing states, and return arbitrary D.
Four ordinary real additions and two half-sums give18 word primitives plus
one quarterturn; the clean comparison uses14. With the bit circuit above the
pair costs 8b²+25b+8 gates dirty, versus 7b²+20b+8 clean.

Numerical interpretation is separate from modular reversibility. Let grid
spacing be Delta. When data operations do not wrap, t(d)=(1-i)d/2+e where
each real component of e lies in [-Delta/2,0]. The exact C output is perturbed
by (e,e), whose two-complex-coordinate Hilbert norm is at most Delta.
This applies to the exact inverse map as well: applying the unitary C^-1
to the forward error preserves its norm. Alternatively the inverse's explicit
formula gives the same bound directly. Arbitrary dirty D cannot change output.

At one layer, 256f disjoint pairs contribute squared error at most256f Delta²,
so its Hilbert error is at most16 sqrt(f) Delta. Exact C layers and L/R are
unitary; telescoping five layers bounds the completed macro and its inverse by
80 sqrt(f) Delta. This is an absolute bound for arbitrary data, not a sampled
state claim. The scalar inverse controls do not establish linearity of the
rounded transformation.

With initial whole-block Hilbert norm at most H, every completed layer has
norm at most B=H+80 sqrt(f) Delta. Within a pair the difference has magnitude
at most2B; the half-sum target has magnitude below3B+Delta. Thus signed data
range greater than4B+2Delta is a conservative sufficient no-wrap condition.
Scratch may wrap freely and does not need a numerical range premise. The
sign-extended numerator lives modulo2M and its wrap is handled by the proved
half-accumulation identity. If Delta<=H/(128 sqrt(f)), signed range8H suffices.
For H a power of two and Delta=H2^-p, choose b=p+4, giving that range.

## Full wrapper and comparison bill

Each exact monomial is implemented by its fixed coordinate-permutation cycles
and coordinate phases. A cycle of length k takes k-1 complex swaps, decomposed
into two real swaps. Multiplication by i or -i takes a real swap and a real
negation; -1 takes two negations. These use only live coordinate words.
The exact source recipe gives L:1248 real swaps,512 negations; R:1264 swaps,
512 negations per spectator lane. Both phase histograms are [128,128,128,128].
No full vector copy is needed: cycle swaps use existing data words. The Python
simulator's allocated lists are not claimed as the circuit's workspace.

The completed rank-five residual therefore costs, per spectator lane:

* 1280 C pairs,23040 real-word addition/subtraction/conditional-decrement
 primitives,3792 real swaps and 2304 real negations;
* 10240b²+41584b+10240 generalized controlled-X/NOT gates;
* one arbitrary dirty (b+1)-bit word, restored exactly and reusable serially
 across all pairs and f lanes. The 1024bf data bits are not counted as scratch.

The constructed clean comparison uses17920 word primitives, the same routing
and quarterturns, and 8960b²+35184b+10240 gates per lane. Dirty operation costs
5120 additional word primitives or1280(b²+5b) additional gates per lane.
Serial depth is at most the total gate count. Five conceptual butterfly layers
do not mean five physical clock steps when sharing one scratch word.

After borrowed-bit decomposition, the complete dirty macro has at most
`(6b+4)(10240b²+41584b+10240)f` elementary reversible gates and no additional
workspace. RESULT.json records exact X/CNOT/Toffoli counts rather than treating
this coarse upper bound as measured. For example b=32 gives, per spectator
lane, 5482752 X,1031936 CNOT and 442109184 Toffoli gates, versus 76032 X,950016
CNOT and 380425984 Toffoli for the constructed clean comparison. These large
constructive counts make no speed or recursive-tariff affordability claim.

## Mapping to PR3994, and why replacement stops here

PR3994's full-state-cut theorem permits each completed cut an absolute defect
at most H2^(-beta-25). This single macro meets that allowance whenever
80 sqrt(f) Delta <= H2^(-beta-25). For power-of-two H, the sufficient choice
p >= beta+32+ceil(log2(sqrt(f))) meets it. This is an explicit module-to-cut
mapping, conditional on the actual caller placing this macro at that cut and
paying its time/space bill. It is not an improved selected stock coefficient.

Local bijectivity does NOT preserve the provider's linear dirty-cleanup proof.
The exact source's `bw_transport.py` applies row-linear additions, scales and
operator composition; substituting a nonlinear rounded map is outside that
contract. For the actual rank-five L C_[5] R above, let h=s be real unit input
at coordinate0. The checked witness Q(h+s)-Q(h)-Q(s) has 24 nonzero complex
coordinates; coordinate0 is1 grid unit. Thus a dirty helper increment transformed
before and after adding s depends on h and is not Q(s). This is an actual
source-bound macro witness, not merely a generic nonlinear example.

Destructive coordinate flooring is worse: even one C followed by its adjoint
and flooring fails to restore the input ((1,0),(0,0)); the verifier records its
round-trip result. Our lift restores it exactly, but the preceding additivity
failure remains. A full implementation must account for its nonlinear errors
and exact borrowed-bit cleanup jointly, or retain extra reversible information
in an affordable lifecycle. A single rank-five child charge is not evidence
that the explicit scalar circuit above fits the recursive tariff. We stop
implementation expansion at that missing actual caller/native budget.
