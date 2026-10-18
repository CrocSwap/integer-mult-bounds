# A sharp two-occurrence failure count

## Model and source

Fix PR2979's final words at `be191346391661f4d35fc0d1508d0a6029572576`,
retained byte-for-byte on canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`. The source package is by
Marius-Paul Dumitrean and retains the full predecessor attribution.
Use its claimed complex saving

\[
b=1729033982646513517717/10^{24}.
\]

Define \(H_r=r(73/r)^b\) for positive ranks and \(H_0=0\).
The inherited model has 74 replicas, 666 calls, and denominator
\(73\cdot896\cdot74\). Each replica has 672 capacity-eight bins and
448 bins of each capacity 16, 32 and 48. Each bin pays one idle child
of rank capacity minus occupied width, including empty bins.

The independently recounted per-call local profile is
`{1:2445,2:706,3:232,4:108,5:18,8:8}`. The entrance-relative helper
inventory is `{4:26,5:2,6:16,7:52,8:99,9:213}`. Both providers agree.
These counts include all 408 live helpers. The nominal source stock remains
`66304+408+8+91+2=66813`; no private buffer is removed.

We hold scalar gates, partner frames, later construction stages, cleanup,
entrances and the capacity pool fixed. A change widens one of the original
22 lowered helper endpoints at one call from its literal rank-seven frame
back to the rank-eight parent frame recorded in stage one. There are
\(22\cdot666=14652\) possible occurrences. Occurrences may be chosen
nonuniformly across helpers, calls and providers.

The result concerns arbitrary whole-helper fractional packing in this fixed
pool. Ignoring chronology and family exclusion only enlarges the feasible
set, so its rejection also rejects integral chronological packings in the
same model. Splitting helpers, coding, changed words, changed entrances or a
changed capacity pool are outside the theorem.

## Literal terminal accounting

`frames.py` reconstructs all register frames through A, the centre chains,
B with its interleaved warps, restore and final completion. It uses independent
nine-bit elimination, not the producer or its frame accountant.

For each of the 22 helpers, both providers satisfy all of the following:

- The current frame immediately before terminal completion is exactly the
  recorded rank-seven endpoint.
- The recorded parent endpoint contains that frame and has rank eight.
- The entrance lies inside the endpoint.
- The entrance has dimension zero or one, so widening changes owned width
  from seven to eight or from six to seven, respectively.

Thus a widened occurrence adds exactly one rank-one terminal child and
one unit of helper width. It does not replace a preexisting nonzero terminal
child. Different occurrences change different terminal completions, so their
local and inventory deltas add without interaction. The tests also reconstruct
every literal single-widening word with its expected changed report.

## Complete packing dual

For a bin pattern of capacity \(c\) and multiset of helper widths \(P\),
let its feature vector contain four capacity indicators and six width counts.
The checker independently enumerates all 2,551 feasible patterns over widths
4 through 9. It solves the ten tight-pattern equations of the source basis
as rational combinations of \(H_1,H_3,H_5,H_{48}\). Let the resulting
capacity and width dual variables be \(z_c\) and \(y_w\).

For every pattern the checker proves

\[
z_c+\sum_{w\in P}y_w\le H_{c-\sum_{w\in P}w}.
\]

Twelve inequalities are polynomial identities; the other 2,539 have strictly
positive certified reduced cost at the stated saving. The square-root interval
engine is reused from Nick Petalas's `coupled-cap-independent/arithmetic.py`.
It is a separately implemented alternative to the supplier's log/exp engine,
not a new arithmetic method claimed here. Every live byte is authenticated
before that module is imported.

Sum these inequalities over any fractional packing, then add all local
children. The resulting lower cost per replica for the original inventory is

\[
B=22239H_1+6354H_2+\frac{43101}{20}H_3+972H_4
 +\frac{741}{4}H_5+72H_8+\frac{7619}{20}H_{48}.
\]

The computed width prices have the exact identity

\[
y_7-y_6=y_8-y_7=\frac{H_3+5H_5-H_{48}}{20}.
\]

Consequently every widened occurrence, regardless of helper or entrance
class, increases this complete lower cost by the same quantity

\[
D=H_1+\frac{H_3+5H_5-H_{48}}{20}>0.
\]

For any chosen set of \(n\) occurrences, weak duality gives

\[
M(n)\ge\frac{74B+nD}{73\cdot896\cdot74}.
\]

This statement requires no feasible candidate basis for the changed
inventory. Dual feasibility depends on the unchanged pattern alphabet,
not on the inventory right-hand side.

## Exact rejection and sharpness in the relaxation

`RESULT.json` contains rational, outward-rounded enclosures for every
proof-relevant quantity. In particular,

\[
\frac{74B+2D}{73\cdot896\cdot74}
 >1.000000000041>1.
\]

Since \(D>0\), every set with at least two widened occurrences fails the
source complex budget, even after arbitrary fractional repacking.

The count two is sharp for this relaxation. For either single-occurrence
width change, the checker solves the original ten-pattern primal with the
changed integer capacity and width totals at T74. All resulting pattern
amounts are nonnegative. They satisfy every capacity and width equation,
use tight patterns, and have complete moment

\[
\frac{74B+D}{73\cdot896\cdot74}<0.999999997492<1.
\]

The exact amounts are in `singleton_fractional_primals`. Some are fractional.
This proves relaxed feasibility, not a chronological integer allocation or
a physical one-change implementation. The unchanged literal source profile
also passes its positive moment check.

A uniform widening of any one named endpoint changes 666 occurrences, so
all \(2^{22}-1\) nonempty uniform endpoint subsets fail as a corollary.
PR3237 already proves the analogous rejection for the four uniform V45
endpoints. The new coverage is nonuniform occurrence selection across all
five groups and the sharp one-versus-two relaxed threshold.

## Limits and next decision

This is a finite certificate plus a written weak-duality argument. No native
phase identity, scalar dirty-state semantics, cleanup executor, physical
movement or backing, precision/tape invoice, bit-side cap, outer release,
all-size compiler or complete multiplication theorem is verified here.
The original allocation's moment profile is an authenticated positive input;
its 271,728 placements are not replayed by this package. The negative result
needs no allocation search because it rejects the more favorable fractional
relaxation. It does not change or scientifically admit PR2979's supplier.

The decision is to stop fixed-word terminal-widening experiments in this
model. A further construction must change another charged obligation or
its consumer, rather than assume a widened endpoint can reuse the final
invoice. A physical one-occurrence realization remains a different question.
