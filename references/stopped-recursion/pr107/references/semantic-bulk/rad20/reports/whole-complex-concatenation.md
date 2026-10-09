# Whole-rank complex phase children: actual fixed-tape construction

This report specifies a new transfer of the independently accepted binary
complex network. It is a written construction for independent review, not
by itself a final multiplication certificate. The main change is one child
of width `r*f` for a nonalternating residual of rank r, in place of r children
of width f. The paid binary address adapters and all scalar gates remain.
No improvement is claimed from ignoring those adapters.

The campaign start is 2026-10-07 22:25:21 UTC. The user-extended deadline
is 2026-10-08 10:00 UTC. Accepted finite inputs include the h28 controller
R92309 and the newly independently reviewed delayed-clone R88377 circuit.
The latter's full review is
[review-complex-delayed-clones.md](review-complex-delayed-clones.md), with
certificate SHA256
`67eb3d68e59355861444069f8839706884d5f44cb3e6464c41dd2b1cf6eab854`.
Only the three specified boundary families below receive new grouped
children. Every remaining positive residual keeps its original individual
calls; no histogram of unexamined internal edges is credited.

## Complete fields and the paid adapter

An invocation operates on e selected binary address positions, with global
spacing K and offset rho. Their enclosing complete field has length eK,
and the selected positions are exactly `rho+j*K`, `0<=j<e`. Complete
unselected coordinates in this field, outside fields, preceding rows and
all parked scratch remain spectators. K and rho are unchanged in every
descendant invocation.

For `e=m*f+t`, `f=floor(e/m)` and `0<=t<m`, the main field consists of m
adjacent complete fields of length fK. The trailing complete field tK is
a spectator throughout all main basis adapters, scalar role gates, source
and sink phases, and the main-bank exchange. The previously reviewed finite
identity therefore applies separately for every assignment of its t selected
tail bits and its unselected bits. Source and sink phases use the f columns
of the main array. They do not silently act on all e selected positions.

For a nondegenerate nonalternating residual E of rank r, choose its existing
binary orthonormal basis as the first r columns of the complete ambient
address basis. This column ordering is part of the same fixed binary
adapter table. It is paid through the accepted compact bit permutation
interface in both orientations. It is not an additional free permutation
of the physical data after the adapter.

After that adapter, the active r complete fK fields are first and adjacent.
Their union is literally one complete rfK field in its original order. Its
selected positions are still `rho+j*K`, now for `0<=j<r*f`. Changing its
descriptor to width rf requires no physical gather, no record duplication,
no reversal, no conversion of K, and no loss of inactive fields. All m-r
following fields and the tK tail remain spectators of the child. Returning
from the child, applying the paid inverse adapter and restoring parked
streams gives the original complete external layout.

## Mixed orientations and diagonal costs

The complex one-bit kernel is C, and orthonormal binary basis vectors can
have Hamming weight 1 or 3 modulo four. Thus active directions may require
both C and its inverse. For the conventional kernel,

`C^-1 = -i Z C Z`.

If n_minus of the r active directions are inverse directions, the exact
mixed tensor on the f columns is

`(-i)^(f*n_minus) Z_minus C^(r*f) Z_minus`.

Z_minus touches precisely the selected positions in those negative fields.
It does not use all bits of the complete fields. The accepted aligned
counter/mask scan computes their parity in O(V) bit time on fixed tapes:
the counters have O(p)-bit fields already included in the record format and
V is bit volume, not the number of coefficient records. The unit scalar
factor needs a bounded Gaussian integer phase operation. Its exponent
modulo four is fixed-table data and f modulo four. Neither an arbitrary
XOR address translation nor an uncharged resampling operation is required.
The same argument applies after reversing an invocation.

Replacing r completed children by the one completed child preserves the
exact tensor. A completed child has dyadic denominator at most `2^(r*f)`
and absolute row sum at most `2^(r*f)`, exactly the charge of the replaced
separate completed calls. Internal cancellation excursions do not remain
after its exact return.

## Arbitrary widths and short tails

The new contract accepts every integer e, not just powers of m. Once the
main mf selected positions have been transformed and the main role streams
are reassembled, apply the t exact C1 kernels to the trailing selected
positions, once per original row, including padded rows. Width e<m is this
same fixed-size base case.

Each C1 kernel pairs complete consecutive address blocks on two fixed
tapes, parks one block, then streams the other alongside it. Its selected
axis can have any global spacing K; its cost is one fixed number of full
volume passes, not a growing sort or a loop over K individual addresses.
There are fewer than m such kernels. Saved-input sums and differences,
unit phases and exact halves implement their scalar action. All preceding
and following coordinates are retained, and all temporary tapes return to
the original external contract. A conservative 32 coefficient-depth units
per tail bit add at most `32m` to the node guard. Padding bitmaps are neither
discarded nor read as coefficient data during this computation.

## Role volume and joint row reservations

The accepted physical network splits complete preceding rows among its W
role streams. Each child, including a larger grouped child, receives the
same logical bit volume V/W. Width rf changes the coordinates on which the
child acts; it does not change its row count, record precision, W factor,
or spectator volume. The fixed depth-first schedule parks the other W-1
streams, reuses the fixed role and I/O tapes, and restores them on return.
Splits, merges, scalar gates, masks and tails each use a fixed number of
passes. Constants can depend on the finite network and its tables.

The longest credited child has r_max=m-2h=21896 for m=21952, with
`m^272>2*r_max^272`. Thus complex depth is at most `272 ceil(log2 e)`.
For the current bit input, depth is at most `651 ceil(log2 e)`. A bit
adapter can run inside a complex role stream, so a safe simultaneous
reservation is the PRODUCT

`Q_rows = W_complex^D_complex * W_bit^D_bit`.

This explicitly avoids claiming that the larger of two separate row
polynomials alone covers their nested use. At complex depth j the remaining
row count is still divisible by `W_complex^(D_complex-j)*W_bit^D_bit`.
Every bit adapter therefore has its full bit-depth row stock; it returns
those rows before the next complex split. Unequal child widths may finish
earlier but consume no extra depth beyond their proved maximum. The two
sets of row-selection digits are disjoint from the complete coordinate
fields and from each other. No child strips the complete unused suffix.

Round the initial complete preceding row range up to a multiple of Q_rows
once, provided it is at least Q_rows. Volume grows by less than two. The
active-row bitmap, all padded rows and arbitrary scratch are retained until
the completed boundary. The earlier accepted complete-row padding argument
then applies to each nested split without successive doubling.

Under the independently retained eventual conditions `e<=C*p`, `p>=C`
and `log2 p>=25`, with `W_bit<2^49` and `W_complex<2^41`,

`log2 Q_rows <= (49*651+41*272)*(2+1/25)*log2 p < 89000*log2 p`.

The untouched suffix has at least `2^ell` complete rows with
`ell>=p^(1-epsilon)/2` eventually. A conservative sufficient common
condition for the new composition is

`b_input^(1-epsilon)>356000*(log2 b_input+8)`.

This uses the retained eventually valid comparison
`log2 p<=2*(log2 b_input+8)`. A final certificate must verify this new
reservoir, its six compressed exact power checks, the stopped-leaf cutoff,
and the separate fixed C/table/prime and logarithm-absorption thresholds.
It must not reuse the old maximum-only row estimate without this check.

## Actual precision and variable-width recurrence

For the R88377 circuit use the independently reconstructed scalar count
`G=13074237304128`, `W=1967894720064`, `s=43199206864789248` and
`E=487736851028968488321153678560340410432`. The literal saved-input
coefficient charge is conservatively

`2G W^2+4s+4W+4+32m < E`.

The first four terms are the actual accepted nonalternating-network charge;
the last pays the short tail. Regrouping reduces the number of calls but
keeps their total completed child width `s*f`. The diagonal inverse wrappers
can be charged within these per-rank phase units; an implementation that
uses additional units must account for them explicitly. The false shortcut
`G<6W` is not used. Set `B=s+E`, with B>=8. The new active guard is

`A(e)<=A(r_max*floor(e/m))+s*floor(e/m)+E`.

For e=mf+t and f>=1, induction with base A(e)<=8e gives A(e)<=2Be:
`2B(m-r_max)>=s+E`, so the complete child and all node charges fit.
Completed outer BASE-m pieces have total width at most d, and their boundary
overhead is below18d. Hence `A_layer<=(2B+18)d<C0*d`, where
`C0=32mB^2` and `C1=1`. The same fine-grid integers are used throughout;
no child rounding or automatic storage compaction is assumed.

Let n_r be the selected child counts, including all retained individual
calls as r=1. The three disjoint credited families have ranks m-h^2,
m-2h, and `(h^2-1)(h-1)`, with multiplicities `(R+h+1)*v^2`, the same
number, and 2N respectively. Their actual ranks and total rank s are
unchanged. A strict homogeneous exponent sigma satisfies

`z=sum_r (n_r/W)*(r/m)^sigma < 1`.

For the actual variable-width stopped tree, the volume-weighted sigma
potential at depth j is at most `z^j*d^sigma`. If tau>=sigma, the node
overhead sum is bounded by a convergent tau characteristic and O(d^tau).
If tau<sigma, every internal width is at least d^beta, giving the bound
`O(d^(sigma+beta*(tau-sigma)))` from its sigma potential. Terminal width
is below d^beta, and its linear cost is bounded by
`O(d^(sigma+beta*(1-sigma)))`. Positivity and the decreasing potential
also bound an unequal-depth leaf frontier; leaves need not be at one depth.

Thus retain `chi=tau+(1-beta)*max(sigma-tau,0)`, the leaf exponent
`sigma+beta*(1-sigma)`, reservation exponent `max(1-c,0)`, and
`max(tau,sigma,chi)<lambda<lambda_prime`. Bit overhead is still paid at
tau. The larger phase saving is a homogeneous branching parameter, not
a standalone complex runtime exponent that evades bit movement.

## Independent evidence and final boundary

The new independent control run is
[0718Z-review-whole-complex](../runs/20261008T0718Z-review-whole-complex/).
It checks mixed directions with complete binary adapters in both
orientations, selected offset masks, unequal-width cancellation children
on one preallocated integer grid, nonzero short tails, guard inequalities
and stopped trees with tau on both sides of sigma. Omitted tails and
unwrapped all-forward calls are separate negative controls. These tests
support the algebra and numerical contract; the complete tape and row
argument above still requires independent written review and a new exact
full multiplication assembly. No new kappa is asserted by this report.
