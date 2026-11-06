# Four-axis retained-port binding

This binds the phase-covariant four-axis result to two exact retained port
programs. No complete multiplication improvement is claimed.

## Exact model and boundary

Use the exact two-/three-call retained port bodies in
CrocSwap/integer-mult-bounds#6509, head
`a4173e810c4d34a1d13b9745af123ad0ec6cfed5`, package
`research/conservative-gaussian-rounding`, by Ali Romman. Its retained
`inputs/rounded.py` originates with JoyboyBrian's #5485, and the underlying
port algebra comes from #4743. Pin and credit these sources in the final
package. This claim is only for `f=4`, hence `N=4096`, and axes zero and two.

The four active bits are `3*j+axis`, `0<=j<4`. Fixing all eight spectator
bits gives 256 disjoint fibers of length16. Apply the new block map F to
each fiber, or its literal inverse in a reverse call. Its ideal matrix on
that fiber is exactly the fourfold native Gaussian tensor, with entries
`-i^(4-popcount(r xor s))/4`. This coefficient formula is independently
used by the port oracle; the implemented factorization is `-D*(W/4)*D`.

All retained monomials and triangular mixes are exact maps of the Gaussian
integer grid and have their displayed literal inverses. Therefore reversing
the port body with the true inverse block map restores both arbitrary dirty
banks exactly. Both composition orders are covered. No `F^2=J`, `F^4=I`,
additivity or commutation of independently rounded layers is required.

## Coordinate precision and finite words

The finite certificate verifies `|e_j|<=3` and `|f_j|<=5`, where
`f=-W e/4` is the inverse correction. Applying the real map independently
to real and imaginary components, with quarter phases, proves pointwise
complex-coordinate errors at most `3*sqrt(2)*h/4` forward and
`5*sqrt(2)*h/4` inverse. Both are strictly below `2*h`. These are universal
claims conditional on the finite table predicates, not extrapolations from
the port fixtures. In particular `g=q+1` suffices for a call tolerance
`2^-q`, replacing the predecessor's four-axis `g=q+3`.

Retain the predecessor's source-ordered call requests:

| Direction | q at f=4 | New g | Old g |
|---|---|---|---|
| Two calls forward | P+7 | P+8 | P+10 |
| Three calls forward | P+9 | P+10 | P+12 |
| Two calls reverse | P+4 | P+5 | P+7 |
| Three calls reverse | P+6 | P+7 | P+9 |

The new call meets exactly the same actual-input premise used by those
budgets, so the complete port coordinate error is at most `2^-P`.
This leaves initial quantization charged separately, as in the predecessor.
It does not optimize the external requests q. An independent direct check
is possible: the native infinity norm is4 and the mixing matrix P+2Q has
infinity norm at most3. For a uniform completed-call error epsilon, the
two-/three-call forward error multipliers are13 and53, and the reverse
multipliers are1 and5. These constants also imply the displayed budgets.

For source coordinate magnitude at most `2^H`, retain the source entry
bound `U=2^(H+12)` and signed width `w=H+g+19`. In a block call, each real
input component is bounded by `M=2^g U`. Every fast Walsh intermediate is
bounded by `16M`; the final corrected numerator is bounded by `16M+5`.
For H,g>=0 this is at most `2^(H+g+16)+5 < 2^(H+g+18)`, the positive
w-bit limit. Quarter phases and exact shifts are also safe. The retained
monomial/mix width argument is unchanged, as the actual-input error
premise still holds. Thus both fractional precision and signed word width
can be lowered by two relative to that retained request, with its large
headroom margin left intact. A different tape representation may have a
different bill; this is not a lower bound on all implementations.

## Direct accounting

One complex block executes two real 16-point fast Walsh transforms:128
full-word sums/differences in total, followed by32 correction additions
and32 exact quarter shifts. The finite residue calculation uses only
three-bit residues, but is still payable, as are table access, phase/sign
operations, source reads, writes and word checks. A fixed 2048-entry scan
is an explicit bounded implementation of table access if constant-time
indexed lookup is not available; no physical tape speedup is inferred.
Each native call executes256 blocks, including all-zero blocks. A k-call
port executes `256k` blocks, `40960k` full-word block additions and
`8192k` exact quarter shifts, plus the unchanged retained monomial/mix
work. In particular the retained mixes cost4N real additions and2N left
shifts, and there are four/six monomial passes for two/three-call ports.

The implementation can load32 words, perform the two transforms in place,
apply offsets and store the result, then clear all owned scratch. Tables
and quotient/control storage are finite constants. Such scratch work costs
O(w) per block, and source/index/control work is also paid. This proves a
finite direct reference interface only. No accelerated recursive tariff,
fixed multitape placement, compiler-stock estimate, outer admission or new
kappa is established.

## Verification distinction

The independent caller oracle uses native coefficients rather than the
Walsh factorization. Exact scaled integers represent all ideal intermediates;
the common scale64 suffices for three calls. It verifies both composition
orders, global Gaussian phase covariance, every actual paid input cut,
all spectator-fiber sums, exact operation totals and complete-port error.
Separate boundary fixtures use the new g and width. Negative controls cover
aliasing, unsupported f, overflow, forward replay substituted for an inverse,
and a wrong native axis that remains reversible but has the wrong operator.
These finite fixtures corroborate the algebraic interface proof. They do
not certify a complete multiplication supplier or graph consistency.
