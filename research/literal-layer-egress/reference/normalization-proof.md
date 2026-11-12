# Encoded Gaussian normalization in one packet pass

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.

## Statement and inherited model

Let `h >= 2`, `N >= 1` and `0 <= D <= h` be canonical encoded Counts.
The borrowed source consists of exactly N Gaussian fields, each with h real
bits followed by h imaginary bits, least significant bit first, in signed
two's-complement form on a common fixed grid. Set `V = 2hN` and
`b = (1-i)/2`. Descriptors and source are disjoint physical tapes at their
origins and do not alias this engine's owned roles. The caller supplies grid
meaning, field order and descriptor validity.

`Normalizer.run` returns the exact fieldwise product `b^D z` if it is
integral on that grid, and raises `NormalizationError` otherwise. On success
it preserves the source and descriptors, returns their heads and the output
head to their origins, and erases every owned work body and marker. Output
is protected until consumed. The same cleanup applies to named arithmetic
rejection, including erasing any partial output; the engine is reusable.
This rollback statement excludes malformed packets/descriptors, arbitrary
exceptions, resource faults and violation of the caller's disjointness contract.

Under the pinned physical-tape and encoded-Count implementations, total time
is O(V), local scratch is O(h + log(N+1)), and the protected output occupies
V additional bits. These are structured-program arguments under those source
contracts, accompanied by finite executable checks, not a formally verified
Turing-machine compiler or a complete multiplication theorem.

The operator identity and O(V) normalization specification are already in
PR2287, `selected-complex-layer-closure/PROOF.md` section 8 and `normalize_b`
in its `arithmetic.py`. The new work realizes that boundary with encoded D,
unit tape movement, a fixed scratch inventory, exact acceptance and complete
cleanup. It does not improve PR2287's stated asymptotic normalization tariff.
PR3091/3087 supply the physical framework; PR3098 separately implements the
finite scalar recipes and their packet access.

## Exact signed transducer

Write `D = 2m + e`, with `e` either zero or one. The credited identity is

    b^(2m)   = (-i)^m / 2^m,
    b^(2m+1) = (-i)^m (1-i) / 2^(m+1).

For `e=0`, the two numerator rows on `(a,c)` are `(1,0)` and `(0,1)`.
For `e=1`, they are `(1,1)` and `(-1,1)`, giving `(a+c,c-a)`.
Multiplication by `(-i)^m` selects one of four fixed rotations of those rows.
The shift is the encoded Count `s=m+e`. The only rank-derived host control
is e and `m mod 4`, at most eight states. No h-, N- or D-sized integer is
decoded by the production program.

For a fixed numerator row `(epsilon_1,epsilon_2)`, read the two h-bit
component buffers in parallel, with initial carry zero, using

    t_k = carry_k + epsilon_1*x_(1,k) + epsilon_2*x_(2,k),
    digit_k = t_k mod 2,
    carry_(k+1) = floor(t_k / 2).

The signed bit sum is in [-2,2], and the carry set {-2,-1,0,1} is closed:
`-4 <= t_k <= 3`. All host arithmetic in this loop is finite-state arithmetic.
The usual induction gives

    sum_j epsilon_j*low_k(x_j)
        = sum_(r<k) digit_r*2^r + 2^k*carry_k.

With `L=2^(h-1)`, every numerator has absolute value at most 2L. After the
h source digits, two iterations on the input sign bits therefore produce
its exact h+2-bit two's-complement representation. No complete numerator
is stored in a width-h word. This matters for inputs such as `(3,3)` at
h=3, D=1: the answer `(3,0)` fits although the unhalved sum 6 does not.

An encoded countdown discards exactly s low digits and rejects any nonzero
one. This is equivalent to divisibility by `2^s`, including negative
numerators. A second countdown emits exactly h output bits. Any remaining
high digits must agree with the last retained sign bit. If fewer than h
bits remain after the shift, the last numerator sign bit fills the rest.
Here `s <= ceil(h/2) < h+2`, so the last sign digit is always reached after
all low digits have been checked. Thus these guards are necessary and
sufficient for exact signed division and output representability.

For the particular b^D rows, integrality already implies representability.
D=0 is the identity. For D=1 the outputs are the average and half-difference,
which, when integral, lie in [-L,L-1]. For D>=2 the real row l1 norm is at
most 1/2, so both components have magnitude at most L/2. We nevertheless
keep the general signed-output guard in the component implementation.

## Packet, failure and ownership induction

The N countdown controls complete Gaussian fields. For each one, copy two
h-bit components into two reusable local buffers, execute the two rows,
clear the buffer bodies, and decrement N. Induction gives the complete
output in the original field order. There is no address permutation or
hidden access to a helper. The source advances monotonically and is rewound
once on exit. The descriptors are only borrowed by the encoded operations.

A discarded nonzero low bit raises the named arithmetic error. The component's
`finally` block closes all three countdowns and rewinds the buffers. The
outer `finally` releases the buffers and setup Counts and rewinds the source.
Then every work marker is erased, partial output is cleared and its marker
is erased before the error is raised again. The same path handles h<2 or
D>h after canonical positive h,N have been admitted. The verifier exercises
rejection in the third field after two successful fields, followed by reuse.

At a nested caller boundary, suspend the parent's allocator scope, pass
physical borrowed views of its payload and Counts, run the normalizer,
restore the parent scope, copy the protected output into a parent lease,
and clear the output body and marker. The test preserves four live parent
Counts and its input lease across this exchange. The parent-to-child input
requires no payload copy; the return copy and protected-output disposal
cost O(V) and are separately priced.

## Complete cost and storage

The encoded division of D by the literal 2 takes O(log^2(h+1)) tape work
with the inherited general divider; comparison, phase extraction and shift
setup fit this bound. We do not use host `divmod(D,2)`. Since D<=h and h>=2,
this setup is O(h). The N countdown initializes in O(log(N+1)).

| Work | Complete charge |
| --- | --- |
| Parameter reads, encoded divide, shift and phase setup | O(log^2(h+1) + log(N+1)) |
| Copy two input components into reusable buffers, per field | O(h) |
| Two numerator scans, low-bit tests, output and sign extension, per field | O(h) |
| Counter setup and closure, buffer rewind and clearing, per field | O(h) |
| N countdown over the whole packet | O(N + log(N+1)) |
| Source return, protected output return, work erasure | O(V) |
| Caller copies protected result and erases it | O(V) |
| Physical marker setup/erasure over a fixed inventory | O(1) |

The inherited countdown has amortized linear movement over a complete
countdown; there is no log h surcharge on each digit. Two output counters
and low-digit counters are each traversed at most O(h) times per field.
All charges sum to O(V), including named rejection's partial work and
rollback. The normalizer makes no recursive child calls and no frame changes.
Any enclosing recursive supplier retains those separate costs.

The production engine preallocates **10 scratch roles** and one protected
output, once. The maximum live inventory follows directly from the calls:

- Setup: the literal-two Count plus divider divisor, quotient, remainder
  and at most one subtraction result or temporary literal word: at most 5.
- Payload: retained two, half, remainder and shift Counts (4), N countdown
  (1), two h-bit buffers (2), three component countdowns (3): exactly 10.
- Input copy: those seven retained roles and one copy countdown: 8.

`Count.increment`, comparison and phase reads allocate no tape. The divider
closes its temporary subtraction result's predecessor before its next loop.
Each role has extent O(h + log(N+1)); a sharper sum is two h-bit buffers,
one O(log(N+1)) countdown and a fixed number of O(log(h+1)) Counts. Every
owned work role is blank on return. Retained backing extents after erasure
are not live logical contents. The borrowed V-bit source, input descriptors
and protected V-bit output are distinct from local scratch. No tape is
allocated per field or per bit; sealed constructors reject such allocation.

## Comparator and limits

The comparator is an explicitly implemented physical D-countdown repeatedly
calling this same kernel with literal degree one. Each call preserves its
input, copies its protected result into a parent lease, and disposes of the
old parent packet and child output. All its parent/child physical tape meters
are counted once by physical identity. It is a controlled D-pass baseline,
not a measurement of the old high-level PR2287 code or a lower bound on every
alternative implementation.

Both versions receive exactly the same successfully divisible packet. If
`b^D z` is a Gaussian integer, then `z=(1+i)^D w` for a Gaussian integer w,
because `b=1/(1+i)`. Hence every intermediate `b^j z` is integral. Each
one-step b maps integral h-bit inputs into h-bit outputs as proved above.
The comparator therefore stays in its admitted domain. Its D passes cost
O(DV); the fused implementation performs O(V) work. The input construction,
static engine reservation and observer-side oracle calculations are excluded
from both invoices; source/descriptor accesses, runtime setup, unit moves,
output construction, all runtime copying and final disposal are included.
Meter totals describe abstract tape events, not elapsed-time speedup.

This scalar kernel does not execute the full
`b^D S_D C^(tensor D) S_D` Hadamard conversion. Its phase sweeps, C supplier,
caller grid-admission proof, root truncation, recursive child implementation,
frame restoration and whole multiplication recurrence remain separate.
The explicit D<=h contract must be established at each intended caller.
No new kappa or selected-frontier change follows from this package.
