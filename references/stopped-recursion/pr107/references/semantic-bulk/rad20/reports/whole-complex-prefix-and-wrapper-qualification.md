# Whole-complex transfer: explicit leading rows and wrapper charge

This is an additional targeted qualification of the frozen
[whole-field construction](whole-complex-concatenation.md), SHA256
`5781af807210dc3ac740e876cdb8073683ea3658f4b8aa067605608919a8f520`.
It supplies a concrete leading-row prefix and a conservative additional
unit-phase charge. Historical producer/control files remain unchanged.

Let `Q_rows=W_complex^D_complex*W_bit^D_bit` and
`q0=ceil(log2 Q_rows)`. The logarithm need not be approximated: use the
integer bit length of `Q_rows-1`. Both depth bounds are O(log p), so q0
is O(log p), with a fixed finite constant. In a top-level call on e
selected positions, first apply exact C1 to its first min(e,q0) selected
positions, preserving their entire complete K-bit chunks. Each fixed-tape
C1 costs O(V), including all coefficients and spectator coordinates.
This initial work costs O(V log p). If e<=q0 it completes the call.

Otherwise the first q0 COMPLETE chunks form a physically preceding row
prefix of cardinality `R=2^(q0*K)>=Q_rows`. No suffix-to-prefix gather is
performed. The selected q0 axes have already received C, while all their
unselected bits remain complete spectators. The active recursive field
starts immediately after this leading q0K field, with width e-q0, the
same K and the same relative selected offset rho. Factorization
`C^e=C^q0 tensor C^(e-q0)` makes this exact for arbitrary Gaussian
coefficients, not only a zero or separable input.

After completing that leading transform, round its complete row count R
up once to `Q_rows*ceil(R/Q_rows)<2R`, attaching zero rows and external
activation metadata. The remaining phase operation is identical within
each complete row. It returns every added zero row to zero and restores
its arbitrary auxiliary scratch. Remove the padding only at this complete
boundary; the original transformed prefix and all inactive coordinates
then remain in place. The complex depth consumes only its W_complex
factor. Each nested bit adapter temporarily consumes, parks, and restores
its W_bit factor, leaving it available for later adapters. At deeper
complex nodes the same original leading prefix is inherited; it is not
transformed again or duplicated. Recursive children consequently need
no additional initial padding.

For a balanced outer round, K and rho are common within that round and
constant in all of its descendants. Repeat the one leading preparation
only at a new outer invocation. Its O(V log p) charge fits the retained
strict recurrence and final polylogarithm absorption; it is not treated
as a free setup operation. If a required leading prefix exceeds the
available axes, the elementary fallback above handles that invocation.
Any eventual comparison of O(log p) with the stopped threshold remains
part of the separately scoped fixed-constant/logarithm conditions.

For conservative coefficient-operation accounting, allow up to three
additional unit-phase operations for each grouped nonalternating call:
two selected-slot Z wrappers and the scalar `(-i)^(f*n_minus)`. There
are at most s positive calls. Inverting the call changes the sign of
the scalar but not that bound. Although unit phases do not increase the
dyadic denominator or absolute size, a deliberately conservative node
depth charge is

`2G W^2+8s+4W+4+32m < E`.

This pays the original4s term, at most3s wrapper operations, and leaves
one extra s of slack. The accepted R88377 literal guard has more than
enough exact slack for both this addition and the32m tails. The linear
active-width proof uses this charged E unchanged, so its B, C0 and C1
remain valid. A final assembly must check this stronger literal inequality
and pin this qualification with the independent complete transfer review.
No multiplication exponent is asserted here.
