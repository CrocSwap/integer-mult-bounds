# A linear signed-residue phase during numerator rewind

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped constructive proof, corroborated by exact finite execution.
No new kappa or complete multiplication theorem is claimed.

## Contract and new statement

Use CubeJerry's compact rounded ADD compiler from [PR6990](https://github.com/CrocSwap/integer-mult-bounds/pull/6990).
For a fixed reduced rational coefficient `a/b`, write `b=2^d o`, with `o`
positive and odd. Let `L=max(bitlength(abs(a)),bitlength(b))`, `K=L+2`.
The inherited numerator construction supplies the signed integer

    N = b*x + a*y + floor(b/2)

in `M=W+K` two's-complement bits on private port 2. Its local layout is
marker 6, the M bits in least-significant-first order, delimiter 2. At
`offset-done`, the port-2 head is on that delimiter. Public heads and the
other private bank obey the inherited contract. Numerator correctness,
its width bound, subsequent exact division and the lifecycle are credited
premises here, not new theorems or audit deliverables.

For `o>1`, replace only the outgoing rewind-to-residue edge at each of
the two component parities. The new phase has exactly `8o+2` graph labels
and `14o+4` six-opcode rows, counting both parities. It returns the head
to the first numerator bit and enters the original `drop` state with
carry `-r`, where `r` is the unique element of `[0,o)` congruent to N.
It writes nothing, reads no public field and uses no new bank.

For every positive M the phase uses exactly `M+1` virtual reads, `M+2`
virtual unit moves and `3M+4` executed rows, including the exit goto and
excluding the first row of `drop`. The old route uses `3M+3` reads,
`3M+4` moves and `7M+10` rows with the same boundary convention.
Thus the replacement saves `2M+2` reads, `2M+2` moves and `4M+6` executed
rows per component. Integral and dyadic coefficients have `o=1`; their
compiled tables remain identical.

The mathematical graph construction is valid for every finite odd o.
The executable retains `o<=125` and additionally bounds L by 24, matching
the coefficient-size range of the cited current compact ADD application.
No full coefficient catalogue is constructed here.

## Signed backward Horner recurrence

Let the bits be `n_0,...,n_(M-1)` and `s=n_(M-1)`. Then

    N = sum_(j=0)^(M-1) n_j 2^j - s 2^M.

Move once left from the delimiter and read s. Start the finite residue
state at `h=-s mod o`. Process the bits in descending index order,
including this first sign bit, using

    h <- (2h+n_j) mod o.

After t processed bits, induction gives

    h = -s 2^t + sum_(j=M-t)^(M-1) n_j 2^(j-(M-t)) mod o.

At t=M this is N modulo o. The final left move encounters marker 6;
one right move returns to the first bit. The marker separates successive
components, so the phase cannot cross into a preceding numerator. Neither
the width nor a power of two needs to be stored. This is classical Horner
evaluation applied to the supplied signed tape boundary.

The source quotient accepts carry `-r` because `N-r` is divisible by o.
Its original low-bit discard therefore produces

    floor((N-r)/(o*2^d)) = floor(N/(o*2^d)).

Indeed, writing `N=oQ+r` with `0<=r<o`, the fractional addition
`r/(o*2^d)` cannot cross the next integer after `Q/2^d`. This argument
also holds for negative Q. The output is the original nearest-up ADD,
including representability, cancellation and signed ties. The unchanged
staging and lifecycle retain whole-target protection on detected failure,
source preservation, success head return and private-history retirement.
The proof makes no stronger assertion about malformed external encodings,
failure rollback or full recursive Controller execution.

## Graph and literal instruction counts

For each parity the labels are one start, `2o` digit labels `(h,bit)`, o
scan labels and o end labels. A start emits a left move and a sign branch.
A digit emits a left move and a goto. A scan emits one bit/marker branch.
An end emits a right move and a goto to the original quotient. Thus there
are `4o+1` labels and `7o+2` rows per parity. Every residue scan label is
generated: start with sign zero, then binary strings represent every
residue once sufficiently many low bits are allowed. Each scan generates
both digit labels and its marker exit. The counts are consequently exact
for the generated graph, rather than a minimum-state claim.

During an M-bit execution there is one initial sign read, M digit visits,
M scan visits including the marker, and one end visit. This gives the
new operation counts above. The old phase has two full rewinds around
one forward residue scan. Each rewind takes `M+2` moves and `M+1` reads;
the forward scan takes M moves and `M+1` reads. Its row count follows
from two move/branch rewind loops, their move/goto exits, the bit branches,
the digit move/goto pairs and the res-done goto. No payload writes occur
on either route.

For canonical nonblank codes in the retained CodedPort, a virtual read
costs four raw reads and six raw moves. A successful virtual move in
either direction costs one raw read and three raw moves. The saved
physical action count is therefore

    10(2M+2) + 4(2M+2) = 28(M+1).

The corresponding reduction in physical actions plus executed rows is
`32M+34` per component. These are exact operation counts under that
executor, not wall-time measurements or a supplier-tariff conversion.
No visited extent or backing requirement increases. The prior positive
complete primitive bound remains valid; its recursive invoice is not
changed by this package.

The numerator Horner phases and quotient retain their inherited graph
bounds. Replacing the residue/power product by this linear phase changes
the compact graph bound from `O(LK+o^2+Ko)` to `O(LK+Ko+o)`. Nothing here
claims logarithmic size in the divisor, minimal finite control, a physical
random-access table lookup, or a better recursive exponent.

## Source adapter and evidence boundary

`adapter.py` authenticates four immutable source files against SOURCES.json.
It loads the exact named compiler definition in a private namespace with
an explicit Builder dependency. The new Builder redirects only the two
exact `rewind(residue(0,1 mod o,2,parity))` edges. It reserves the existing
quotient entries, lets the original compiler finish its other states,
then appends the new phase before resolving labels. No predecessor file
is edited or copied, and no runtime numerical callback is added. Runtime
tables still contain only branch, write, unit move, goto, halt and reject.

The direct verifier separately interprets every tested new phase, and
executes complete changed tables through the retained literal lifecycle
and coded ports. An integer-floor oracle supplies the expected values.
The old compiler is run only as a resource comparator for the new step,
not as a scientific audit. The universal result rests on this proof;
finite execution and source hashes alone do not establish its quantifiers.
