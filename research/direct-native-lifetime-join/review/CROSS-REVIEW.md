# Independent review of the source convolution/native-window lifetime join

**Decision: accept the scoped conditional lifetime theorem.** Author proof
SHA256: `f51241c10a4bfb9e64aa35de0d89eb2e5e91f636c9ca4917e7f3b2862de6ae8b`.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance and
separate author/reviewer execution; not human or formal-kernel acceptance.

## Universal ownership argument

I independently read the exact original `TensorWord.apply`,
`Multiplier.convolution_grid` and the calling portion of `Multiplier.multiply`.
The caller retains original operands a0,b0 while convolution rebinds its own
a,b. Those aliases reference existing owners; they allocate no extra fields.

A forward apply allocates a working field. Its public-map destination is a
second field while the iterator retains the raw output. The second transform
additionally retains the first public output. Once both public outputs and
the pointwise product exist, the opposite transform allocates its working
field and a separate conjugated return. Finally a public-map destination
coexists with that return. This source reference-retention schedule has native
counts 3,4,6 and a seven-field peak. All eight new fields and both held
originals are accounted for; only the originals and final result survive.

Any number of stages updates the same working field. A destination counts
from reservation, before consuming its first input. Explicit full clearing
at the stated retirement event makes the seven fixed roles reusable. Tuple
sharing does not justify aliasing independently mutable physical cells.

Seven is a sufficient schedule preserving those source references. The
six-slot control tests the delivered literal-lifetime emulator; it is not a
lower bound for every out-of-place implementation. Changing reference
lifetimes or allocation schedules could reduce the required slots and needs
a separate argument. No optimality claim is accepted.

## Conversion, histories and native boundary

The preceding grid theorem supplies Q and the entrance shift. One complete
conversion window suffices because requests are serial, the complete result
is installed before the next stage, and the whole reserved width is cleared.
All padded records and holes are included. Entrance, installation and erasure
give three complete passes per call; head returns and formatting preserve
O(T W_*) work. Eight constructions and seven retirements add O(TB). Numerical,
native and coefficient work keep their separate invoices.

Historical backing is the sum of seven slot extents, the window extent, and
each native tape's own maximum including its initial reservation. Clearing a
native frame before the seven-field cut does not erase its history. Native
tapes can peak on different calls, so max of a simultaneous total cannot
replace the sum of their individual maxima.

Native return contract N is substantive. It requires in-window installation,
restoration of borrowed values/heads, full private retirement, no escaping
mutable aliases, fixed origins, and a legal capacity-independent trace with
established A_t bounds. The final clarification charges every auxiliary
owner's full backing among caller/window roles, M or A_t. No unnamed borrowed
owner is free. Native legality and extents precede wrapper-capacity admission,
so the argument is noncircular.

Coefficient tables, schedules, scalar suffixes, arithmetic temporaries and
other controls remain in M or the additional displayed terms. Their stated
O(p)/o(Tp) conditions and the native extent bound are explicit premises; this
local join does not prove them.

## Executed independent corroboration

`independent.py` imports no author lifetime implementation or checker. It
authenticates the two original files, extracts their methods, and transforms
full-field allocations into a separate weak-reference owner census. A pending
destination is registered before its iterator is consumed, and original
method references determine retention. Scalar arithmetic is abstracted:
this verifies lifetimes, not Fourier arithmetic or native execution.

Fifteen combinations of sizes 2,4,8 and repeated schedules 0,1,2,7,16 give
seven peak owners, 3/4/6 native-cut sequences, unchanged roots and three
owners at return. Normal and optimized JSON agree. Removing caller-held
roots or aliasing the input owners changes the census and is detected.
Altered source bytes fail authentication. These finite checks corroborate
the source-level induction rather than establish it by sampling.

The separately replayed author suite compares exact source arithmetic with
its fixed-slot/window construction: 22 cases, 528 calls, 483,696 complete
record visits, padded volume through 2,048 and ten controls. That is author
regression evidence. Its normalized callback is an exact sequential oracle,
not an accelerated supplier. Lease guards detect later API access but cannot
prove arbitrary native code has no hidden captures.

## Limits and credit

The result intentionally survives convolution. Reusing the seven slots for
later public calls requires paid transfer/retirement of surviving owners or
a separate outer lifecycle bound. Native no-escape alone is insufficient.
The later physical/original/coeffs/result_digits arrays and growing final
integer accumulator are excluded; that accumulator is not scalar scratch.

Credit remains with Ali Romman's caller and mixed-rank contracts, Ross
Richardson's historical/noncircular arena accounting, and the preceding grid
theorem. New content binds those interfaces to actual source lifetimes.
All five canonical assumptions and selected kappa remain unchanged. No full
native implementation, multiplier-space theorem or new exponent is accepted.
