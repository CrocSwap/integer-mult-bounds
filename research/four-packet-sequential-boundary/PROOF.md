# A complete sequential packet boundary

This construction fills the physical ordering and output-installation step
for the retained event 8814, family 65689, with native chart d that exchanges
axes 0 and 1. It is a reference implementation with a linear-width bill.
It does not meet the claimed sublinear node allowance.

## Domain and child contract

Fix f>=1 and e=73f+t, 0<=t<=72. Each of the f columns has the nine active
axes of the actual source recipe, plus 64 inactive axes. Include all
remainder, row and spectator axes. The input is a complete binary address
rectangle in any declared physical axis order. Each address holds one
fixed-width Gaussian coefficient. The record width is R=2b, b>=2. Integer
use requires headroom for all intermediate values; modular use is exact
on the declared fixed-width encoding. No coefficient can change its own
address or supply a control key.

Source and owned output have distinct tapes, a common meter and heads at
their origins. The old owned output can have any finite length W. Borrowed
words are outside the wrapper's access set. The chart d is the specific
source fixture's swap; this is not an adapter for arbitrary cover charts.
The source scalar compiler identity remains an inherited premise.

The child receives one complete tape, with the 3f active bits first in
column order. It also receives the full axis order, including all inactive
and spectator axes. It acts as one C tensor 3f on each fixed spectator
value. On return it supplies one equal-length tape at its origin, retires
its old input if it returns a different tape, clears its local work and
does not access the caller's source or owned output. The wrapper checks
the observable shape and ownership conditions. It does not implement C
or enforce a malicious host callback's internal behavior.

## Construction and equality

First copy the complete input to owned work and rewind both tapes. The
source then remains unchanged. In each column, apply d^-1 by a physical
digit interchange, then run the unchanged source monomial interpreter at
f=1 on that column. All other axes are spectators. The interpreter applies
the phase to the input address before the affine map. Thus f calls apply
the right monomial tensor f, with the correct repeated translation and
f copies of the absolute phase. No tensor phase is dropped when f is even.

Bring the first three axes from each column to the front, in the source
child order. Use at most 3f digit interchanges. The remaining axis order is
retained in the descriptor. There is no need to sort inactive axes: the
child fixes each one, and the wrapper reverses exactly the same swaps.
Every elementary operation uses four sequential buckets, append-only
writes, complete consumption and erasure. It never writes a payload by
its destination address. The list of axis labels is control data only.

Call the child once on the full 3f-bit field. Reverse the ordering swaps.
Apply the actual left monomial separately to each column, then d. The
source equation L(C tensor 3)R, tensor functoriality and spectator identity
give exactly the source packet operator, conditional on the stated child
and compiler contracts. This is not f separate calls to C tensor 3.

Finally erase the old owned output, copy the complete result into it,
erase the temporary result and rewind the output. The source and every
borrowed word are unchanged. All work regions created by the retained
routines are erased on normal return. Their fixed collection of tapes
can be reused between passes; tape count does not grow with f or volume.
The child has its own stated fixed-tape return contract. Failed callbacks
have no rollback guarantee in this construction.

## Exact payload bill

Let V be the payload bit count, g the number of ordering swaps in one
direction, and w_R,w_L the lengths of the actual affine words. A full
physical digit permutation, a bit flip, or a phase pass costs exactly
18V read/write/move/erase transitions when input and output heads are at
zero. Each has 2V reads, 2V writes, 2V erasures and 12V moves. This includes
all bucket returns, scratch erasure, input retirement and output rewind.

There are P=f(w_R+w_L+4)+2g such passes. The four extra passes per column
are its two chart swaps and its two phase passes. The source-preserving
copy costs 6V. Installation and cleanup cost 9V+3W. Therefore

```text
wrapper = 18 V [f(w_R+w_L+4)+2g] + 15 V + 3 W
child calls = 1
ordinary supplier calls = 0
0 <= g <= 3f.
```

The child cost is additional. This formula counts payload transitions,
not Python elapsed time or free machine arithmetic. If A is the full
address/descriptor length and M the record count, a polynomial control
charge O(M A^C + A^C), for one fixed C, is additional. The source's large
record premise can absorb this charge; it cannot remove the f full-volume
passes. Source descriptor production and recursive continuation are not
part of this wrapper bill.

The resulting payload bound is O(Vf+W). For positive a2 it does not prove
O(V e^(1-a2) polylog(p)) uniformly in the growing-width regime. Compact
parallel monomials and a faster group-ordering implementation are still
needed. A complete functional boundary is not the missing fast supplier.

## Evidence boundary

The verifier executes all 512 active addresses with two independent
spectator records, a nontrivial integer Walsh calibration child, the actual
right/left recipes, and three old output lengths. A separate complete
18-bit rectangle executes the two-column recipes around one identity
child. These test the physical wrapper; they do not execute production C.
An independent retained address/phase oracle uses indexed writes only in
the checker. Twenty-seven ordering tests use distinct complete records.
The written proof, not these finite domains, supplies the uniform claim.

JoyboyBrian supplied the packet proof and fixture. Jose Manuel supplied
the sequential primitives. Douglas Colkitt's compact construction remains
credited in that source. Cinna Davis supplied the actual mixed caller;
unpaidmoon and Matarener supplied volume/stock distinctions. Native and
Clifford contributors retain their source credit. New work: Ali Romman
with substantial OpenAI Codex assistance, Apache-2.0.
