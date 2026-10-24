# Exact membership from bounded component residues

Let pi=1+i, N=2^r, and let f be a Gaussian-integer array on r binary address
bits. Its Boolean Newton coefficients are

```text
a_S = sum_(T subset S) (-1)^(|S|-|T|) f(T).
B_r = {f : pi^|S| divides a_S for every S}.
```

The lattice, its encoder and this criterion are Clear1nsight's PR3382. We
retain them. The new algorithm tests the criterion without reconstructing
wide coefficient words by repeated Gaussian division. It returns either
acceptance or one mask and bounded residues which certify failure.

## Sufficient and sharp modulus

For r>=1 put b=ceil(r/2) and M=2^b. Since 2=-i*pi^2, pi^r divides M. Reduction
of every real and imaginary component modulo M therefore preserves every
test pi^|S| divides a_S. The Boolean difference transform uses only additions
and subtractions, so it commutes with this reduction. It is enough to compute
all Newton coefficients in (Z/MZ)[i]. Negative inputs use the same canonical
nonnegative residues; signed-floor rounding is not involved.

This is the smallest common power-of-two component modulus. Let M'=2^(b-1)
and let f be zero except for f(1,...,1)=M'. Then a_[r]=M', whose pi valuation
is 2b-2<r. Thus f is outside B_r, but all its residues modulo M' are zero.
No validator which sees only those smaller residues can distinguish it from
the zero array. Smaller moduli also fail. For r=0 every Gaussian input is
admitted and zero residue bits suffice. This is a modulus lower bound, not
an optimal bit-operation or memory lower bound for all validators.

## Divisibility test without repeated division

For k=2h, pi^k divides a+ib exactly when 2^h divides both a and b. For
k=2h+1, require those two divisibilities and equal parity of a/2^h and b/2^h.
Indeed pi^(2h)=i^h*2^h differs from 2^h by a unit. A Gaussian number is
divisible by pi exactly when its real and imaginary parts have equal parity.
These conditions depend only on the stored residues because k<=r.

The implementation first validates the input shape and exact integer types.
It copies only component residues. For each address bit, it replaces the
upper entry of each Boolean pair with upper-minus-lower modulo M. Induction
on the processed bits gives the usual partial Newton transform. At completion
it applies the divisibility test to each mask. A failed mask S, its two
residues and b are a certificate: a separate subset sum reconstructs that
coefficient and checks the failed pi division. Acceptance checks every mask.
The input array is never changed. No floating point or random acceptance is
used. The all-rank claim follows from this algebra, not from finite sampling.

## Arithmetic and storage boundary

There are exactly rN modular component subtractions: N/2 pairs, two components,
and r passes. Every stored component lies in [0,2^b), and every temporary
subtraction lies between -(2^b-1) and 2^b-1. The two residue arrays contain
2Nb mathematical bits. Loop indices and Python object overhead are additional.
At r=9 this is five bits per component, 5120 residue-data bits and 4608
modular subtractions, irrespective of the input coefficient width.

For W-bit input components, a conservative bit bound is O(NW+Nr^2): include
reading and reducing the entire input, then the bounded subtractions and
tests. The source's full-width decoder has O(Nr(W+r)) elementary bit work
under the direct arithmetic model. This comparison does not price physical
tape access, movement, allocation, cleanup or a caller's paid validation
boundary. It does not say that high input bits are free to read on a tape.
The new validator does not emit decoded coefficients. A caller which needs
those wide coefficients must still pay for decoding.

The source finite reference caps rank at nine and component width at 8192.
The new mathematical predicate has no such artificial cap. Comparisons use
inputs and decoded outputs within that source domain. There is no claim that
the two APIs have identical rejection behavior outside it. The new API rejects
malformed lengths, floats, Boolean components and nonpair entries explicitly.

## Source-bound evidence

The verifier compares every new decision with the unchanged source decoder.
A separate subset-sum oracle checks all small Gaussian cases and selected
larger ones. For each rejection it reconstructs the reported coefficient and
checks the residue and failed divisibility independently. Positive inputs
include large signed encodings and arbitrary multiples of M added at every
address; the latter must not change membership. A top-mask change by one is
rejected. One-bit-too-small modulus witnesses cover ranks one through nine.

Three complete literal collectors use source events 2025 through 2039, both
separately archived rank-seven native recipes, and all four actual wrappers.
At every wrapper, pair-stage and whole-event boundary, old and new membership
agree. The source ideal and literal pair arrays also agree. Borrowed sources
are preserved and the private row is exactly zero before erasure. This is
local validation coverage, not a replay of the preceding 2025-event producer,
the entire P104 word or a proof that a physical caller supplies B9.

The explicit benchmark alternates old and new validators on the same accepted
rank-nine arrays, with the same repetitions and positive checks. Input encoding
is outside both timed intervals. Timings measure only membership on one host;
they do not establish an end-to-end collector, supplier or kappa improvement.
The exact decisions and source bytes, not elapsed time, are acceptance gates.

## Attribution and remaining work

Clear1nsight supplied PR3382's lattice, decoder and collector reference.
The literal word and recipe lineage includes ywz65, Arham Tahir, Tekalign,
Ross Richardson and the source notices. Their algorithms and lattice theorem
are not claimed as new. The period-lattice residue reducers concern a different
map and quotient; this validator does not replace them.

New bounded-residue algorithm, sharp modulus proof and validation: Ali Romman
with substantial OpenAI Codex assistance, Apache-2.0. No independent human or
formal-kernel review is claimed. An actual paid producer, complete physical
validation scan, ownership/precision admission and the whole supplier remain
open. The complete kappa calculation and selected frontier are unchanged.
