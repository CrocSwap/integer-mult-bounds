# A resident SCALE2 edge in the complete selected scalar policy

This is a source-bound complete policy certificate and an all-positive-D affine
cost proof. It combines credited components. It does not execute the full native
word physically or establish a new supplier, precision theorem or kappa.

## Fixed source contract and new result

Use Ali Romman's PR6530 exclusive two-field policy for the exact canonical
WORD pinned in SOURCE-PINS.json. Its 22,803 source events are followed by EXIT.
Fix width W=64 and any positive integer payload dimension D. Each staging bank
holds one complete complex field, 128D bits, in interleaved real/imaginary records.
The four tapes are unchanged: field-major owner backing 102272D bits, two clean
staging fields totaling256D bits, and one carry bit. Two clean finite-control
bits are retained. A resident field has its sole authoritative value on its bank;
its entire owner slot is zero. An empty bank is zero. All data-ribbon/carry heads
are at zero between events; the owner head is tracked and charged separately.

Every source policy edge remains available. The only added edge is:

    SCALE field by2, when that field is already resident:
      apply the credited PR6608 same-ribbon circuit on its current bank;
      retain both bank labels and the owner-head position;
      restore active ribbon head and finite control to zero;
      charge3284D-2 reads+writes+unit moves.

There is no added payload stock, uncharged acquisition, prefetch, owner read,
physical bank swap or change of scalar event order. Every other SCALE coefficient,
missing-target SCALE2 and native/reset/final boundary keeps the source flush and
origin-return rules. COPY retains its clean-target premise; ADD restores its
source. The source native/reset operations remain external premises, not zero
cost. The policy is a family of compiled W64,D schedules, not a uniform encoded-D
controller.

The complete scalar-operation bill in this enlarged policy class is

    old: 800847760D-5118198               (PR6530, reproduced)
    new: 800328108D-5109750               (this certificate)
    saving: 519652D-8448 > 0, for every integerD>=1.             (1)

At D=1 the saving is511204 operations. This is an operation count, not wall time
or a new complete native/physical-supplier invoice. The optimum is restricted
to exactly the stated no-prefetch whole-field policy with the additional eligible
SCALE2 edge. Arbitrary caching, new circuits and other layouts are outside it.

## Complete finite state graph

Represent a state by(s0,s1,h). Each s_b is its physical bank's field label or-1
for an empty bank. h=-1 means owner origin; h>=0 means the owner head is at the
end of fieldh. The initial and final state is(-1,-1,-1). Legal action orders are
independent of D>=1, so each fixed event layer has a finite state set.

For ADD/COPY, the two distinct required fields must end resident. Any required
resident field stays in its original bank. Enumerate every permitted assignment
of missing fields to banks and every interleaving of the necessary evictions
and acquisitions, subject to clean destination and exclusive authority at every
transfer. No other field is prefetched. For the old SCALE/native/reset/EXIT edge,
evict every resident field in either legal order. SCALE then uses its original
staging protocol; native/reset/EXIT return the owner head to origin. A resident
SCALE2 edge has no transfers and is a self-state edge. Its action kind is distinct
from an old empty transfer list, so certificate actions cannot confuse them.

Every old action remains in the enlarged graph. Source operand labels, physical
banks, layout, scalar local circuits, external barriers and workspace are fixed.
The source prices and source operation-correctness premises are inherited; no
frozen optimizer/checker is imported or executed by this package.

The complete baseline graph has59170 state rows and314133 edges, with maximum4
states/layer. The enlarged graph has59276 rows and314589 edges, maximum5. Each
has22805 layers. Thus the old four-state bound was not assumed for the new class.
The predeclared combined caps500000 states and3000000 edges were not reached;
no state/edge is pruned to meet them. Full potentials and one attaining action
per event are retained in POLICY.json.gz. Hashes index normalized complete
state/edge/potential data, but the independent checker must reconstruct and
validate all actual submitted data rather than accept digests alone.

## Exact affine edge prices

Write an edge price asAD+B. From owner origin to the start of fieldj, seek
cost is128jD. From the end of fieldi to the start of fieldj, it is

    abs(128(j-i-1)D+1).

Its sign is fixed for D>=1. Its coefficient pair is
(128*abs(j-i-1),+1) ifj-i-1>=0 and(128*abs(j-i-1),-1) otherwise. A complete
clean field transfer adds(1152,-3), including every payload read/write,
source/destination traversal, clean finite-control return and staging rewind.
The owner head then ends at that field. Eviction and acquisition use the same
charged reversible transfer, never copy-plus-unpriced-erasure.

Let C be the exact retained local template tariff from the authenticated43-row
CERTIFICATES/CIRCUITS table. Those template tariffs are credited pricing premises
from PR6530/6527/6513, not newly audited local implementations. After the named
transfers, ADD/COPY adds(512+2C,-256). Old SCALE adds a seek to its target plus
(2688+C,-267), ending at the target's owner-field end. An external boundary
adds owner return(128(h+1),-1) ifh>=0. The new resident edge adds(3284,-2)
and changes no owner-head or bank state. These are the source formulas plus the
single credited6608 component price; all required physical bank/owner returns
in this policy class are included.

## Why the certificate proves an all-D optimum

For every layer/state, the producer computes exact shortest prefix costs atD=1
andD=2. If they arev1,v2 it proposes potential

    pi(D)=(v2-v1)D+(2v1-v2).

Interpolation alone would not prove anything between or beyond those points.
For EVERY reachable edge s->t with affine costc, the checker instead verifies

    pi_i(s)+c-pi_(i+1)(t)=A_res D+B_res,
    A_res>=0 and A_res+B_res>=0.                              (2)

Those two inequalities imply nonnegativity for every realD>=1, hence every
positive integerD. Initial potential is0. Induction on any legal path then
bounds its accumulated cost below by the potential of its current state.
At the unique final origin state this gives a lower bound on every legal policy.
The retained complete action path is separately followed, with each action
matched to a unique legal physical-bank transition. Its accumulated affine cost
must equal the final potential exactly. Thus the lower bound is attained for
allD>=1, proving the new total in(1), not merely a two-point extrapolation.

Actual complete state coverage is also checked: successor sets are equal to,
not just contained in, the next retained layer, with unique strict integer rows.
The same process reproduces the credited baseline and its exact total. Every
boundary, including final owner return, lies on the attaining path. The gain
in(1) is positive because its slope519652 is nonnegative and its value at1 is
511204>0. No fallback to an upper-bound-only path was needed in the first attempt.

## New edge semantics and literal physical evidence

Nick Petalas6608 proves and implements resident doubling. For each signed64-bit
record, rotate left by adjacent CNOT swaps and clear the low bit with the final
sign CNOT. On the retained no-overflow domain-2^62<=x<2^62, the top two input bits
coincide, so the resulting record is exactly2x. On arbitrary bit strings the
word remains a reversible linear map. Two records per complex coordinate give
2D records. Compiling each CNOT as control-read, target-read/write, control-read
uses one existing clean finite-control bit and returns it to zero. Fixed unit
head moves return the active ribbon head to zero. No owner/other-bank/carry
instruction is present. Relative active-tape0 is bound to the field's existing
physical bank, not a free physical bank permutation.

The credited all-D component traffic is

    reads1140D, writes380D, moves1764D-2, total3284D-2.

The source bit-map and all-D component proof retain6608's credit. This package
retains actual expanded instruction words forD=1,2 as data. Primary literal
execution checks386 basis columns including unused carry and43 declared signed
fixtures, complete active tape/head/control/meter and the literal instruction
inverse. ForD=1 its129 basis columns also compare with the actual pinned source
SCALE2 gate data and unchanged carry, a dependency check rather than a new source
audit. The independent engine validates the submitted words on fixed complete spectator
fixtures with both physical-bank bindings after both blind firsts. Its literal
instruction grammar excludes owner/other-bank/carry access. Together with that
syntactic exclusion, the written disjoint-tape argument covers arbitrary spectator
values; the finite tests do not enumerate all102272D owner-payload states. They
do not physically replay the full owner tape throughout every source scalar or
native event. Finite physical checks corroborate the new edge only.

Cache authority is verified abstractly on every actual policy action. Together
with the unchanged source scalar/external contracts and the credited new edge,
this supports induction on the complete scalar event sequence. This package does
not rerun the source whole-word arithmetic/grid-stub trace or prove native/reset
semantics, actual clean stock production, full numerical admission or uniform
controller implementation. Those inherited obligations remain explicit.

## Attribution and remaining obligations

Ali Romman6530 supplies the exclusive policy, complete baseline and affine
certificate method;6527/6513/6511 supply staging/scalar/tape lineage. Nick Petalas6608
supplies the new physical edge and all-D component proof. Sagar Thakrar3241,
DreamingOfClouds6030 and all retained native/owner/precision/compiler authors
retain predecessor credit and notices. ywz65/PR2545 supplies earlier R439 window-
residency and restricted-DP scheduling context; its route/XOR totals and weaker
intermediate-restoration contract are not transferred. No new claim to caching
or dynamic programming as a principle is made. The new work is the single-edge
complete policy integration, its enlarged graph and exact attained all-D bill.

No native/reset implementation, initial layout, encoded-D controller, precision/
stock admission, complete supplier funding, outer transfer, human review or
formal proof-kernel acceptance is supplied. No new kappa or selected frontier
change follows. The finite certificate is not a complete multiplication theorem.
