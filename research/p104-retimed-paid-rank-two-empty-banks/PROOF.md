# Exact scope and price

Write the old public ascent as A→C and let B be a strict intermediate
rank-four or rank-five chart of the same signed catalogue. The two
halves are rank one. The exact [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
head `5eec7ed633dcf9b9bbc95552aa653da296f863fb` fixes 95 ascents
on the #7334 word. In each quotient C/A over GF(2), the three nonzero
lines are all possible intermediate spans. Of the 285 lines, 254 have
no catalogue label. Each of the 31 others has exactly one existing
label, and these use 31 distinct old paid MOVEs and movers. The
reverse checker independently reconstructs the exact catalogue span
and label list from the original chart bases.

Let t be the old MOVE's zero-based event clock. If p and n are the
previous and next literal events incident to the mover, the inclusive
cut window is [p+1,n], with 0 or tape length for a missing end. A cut c
is the state after exactly c original events, before event c when it
exists. An incident operation includes using the mover as ADD or COPY
source. The MOVE under test is disregarded only for finding its
neighbors. We keep the original word as the reference for other
roles' chart states and add the mover virtually at B. As A⊂B⊂C and
the mover has no other contacts between p and n, its original chart
is A on cuts up to t and C on later cuts. It was never a B occupant in
these windows. Thus an empty reference B chart supplies no other
public or owned role.

The forward checker evaluates every frozen label at every cut.
The reverse checker reconstructs the same live B bank at the first
cut of each block, with blocks split after any literal B contact and
after t. Consecutive cuts without an intervening B contact have
identical original B occupancy. In the replay there are exactly two
blocks per label, split only by t, and both have zero public and
owned occupants. Together the checkers certify all 29,641 raw
label-cuts. Missing labels and an isolated virtual mover are outside
this mixed-bank test; #7362 reports the original-clock singleton
support separately. No native, compiler or caller change was built.

## Complete conditional price

The inherited native plus signed caller accounting has 110,519 paid
positions, 22,461 productive positions, rank surplus 1,424, and no
empty-root credit. In each of 17 copies this one-edit relaxation
debits two rank-one MOVEs and removes one rank-two MOVE. It replaces
one productive rank-nine return with ranks four and five. Thus
ΔP is {1:+34, 2:−17} and ΔT is {4:+17, 5:+17, 9:−17}.
The paid and productive counts become 110,536 and 22,478 and
their rank masses are each conserved. If
(H_r=r^{1-kappa}) and (G(p,q)=H_p+H_q-H_{p+q}), the net directed
credit is (17(G(4,5)-G(1,1))). Exact directed rational bounds
from the predecessor price are authenticated in the replay, which
rebuilds the 31-stock ceiling from the actual label list.

One relaxed edit grants at most 0.2948799646382698 raw units at
the old crossing upper. The complete margin remains positive at
that upper plus 10⁻⁹, about 0.2944924697296976 raw units. An
additional raw rank-one paid position leaves the full margin at
most −0.7051200353617302 at the old upper. Each old MOVE and
productive mover can fund at most one edit here. Even granting all
31 distinct resources pairwise compatible and free ancillary work,
the total credit is at most 9.141278903786365 raw units there. The
complete margin upper at the fixed κ target 0.0040075385047236 is
−129.72925726734536. These are price ceilings. The verified
mixed-bank saving is zero because no eligible cut exists.

The relaxation retains the five comparator premises. It grants no
credit for routing, ownership, restoration, precision or tape
changes and puts no new paid or ordinary operation into an
admitted word. A broader route needs a new directed price and the
full signed arbitrary-input and all-size verification.
