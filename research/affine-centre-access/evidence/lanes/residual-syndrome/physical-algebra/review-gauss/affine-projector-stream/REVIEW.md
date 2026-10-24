# Independent review of the affine projector stream

Result: accept the local stream construction and its conditional recursive
extension with `AMENDMENT.md`. The amendment is required. The original
`STREAM.md` remains unchanged.

This review covers the signed projector shear, the detail layout, the
exact arithmetic bound, the fixed-tape cost argument, and the stated
completed-frame interface. It does not cover the separate
`OWNER-BINDING.md` packet or a new supplier.

## Exact map and arbitrary inputs

For one selected bit, the two rows of the code are `(u-v)/2` and
`(u+v)/2`. The inverse rows are `a+d` and `d-a`. Each step retains both
outputs. Thus the full code is invertible on arbitrary inputs.

The leaf row on each selected-bit coset is its signed average. If all
detail inputs to the inverse are zero, the inverse sends that leaf to
its signed constant vector. This proves `B^-1 E B=Pi_0`. The leaf update
between two encoded owners therefore gives `(x,y+Pi_0 x)`. Both source
and target can have arbitrary detail values. The inverse changes the
leaf update sign.

The binary map on each pair is `(u,v)->(u+v,v)`. It sends translation
by `(1,1)` to translation by `(0,1)`. This proves the stated conjugacy
from the paired projector to `Pi_0`. It fixes all other address bits.
The proof does not need adjacent selected bits.

The independent checker uses symbolic rows, with a separate variable
for every physical source and target coefficient. It checks 1,280
arbitrary input columns in three small layouts. These include `K=2`,
selected offset 1, protected address bits, and multiple polynomial
coefficients. It checks the exact signed-translation projector, both
inverse orders, the full code inverse, and all retained detail rows.
Six mutations change or remove required graph data and are detected.
The producer checker was not imported or run.

## Fixed tapes, volume, and access

At step `j`, the active stream has `M/2^j` records and its new detail
has `M/2^(j+1)` records. The leaf and all details contain exactly `M`
records. Their lengths form a geometric sum. A stack push or pop scans
only its new or last block. A fixed number of tapes can hold two detail
stacks, the two active streams, and the fixed work areas of the pinned
stream primitives. This does not require a third arbitrary signal.
It still uses physical work tapes; that storage and its cleanup are
part of the implementation cost.

After a split, the remaining addresses have their original relative
order. The next selected bit has a known position in that shorter
address. Collapse the bits before and after it into the fields of the
elementary split lemma. A removed bit need not be adjacent to another
removed bit. Reverse splits and merges restore all original positions.
No row, compact, spectator, or polynomial field is projected away.

The binary basis maps run only before encoding and after full decoding.
At both points the compact fields are complete. The shorter half-slot
width `f` needs at most the existing `(lambda-1)G` control bits.
The fixed number of row additions therefore fits the pinned compact
movement theorem. It costs
`O(V((e log p)^tau+1))`; those address maps are not free. The code
and its inverse cost `O(V)`. Descriptor work is polynomial in the
global parameter and is absorbed only under the stated complete
record-length assumptions.

The source-copy variant is also valid in this stream model. Its erased
values are owned copies of the unchanged source. At each split or
merge, input and output streams together use at most two original
field volumes. Clear those owned inputs before the next pass. This
stock bound excludes the original two owners and the separately
charged compact-map work areas, as the note states.

The arithmetic counts follow from `sum_j M/2^(j+1)=M-M/2^k`.
Each code step has a difference, a sum, and two halvings per pair.
Each inverse step has a sum and a difference per pair. The leaf update
has `M/2^k` additions. These are arithmetic counts, not a complete
finite machine invoice.

## Exact arithmetic and the amended recurrence

Each stored code row has norm at most one relative to its owner's
input maximum. An unhalved sum or difference has norm at most two.
During target decoding, separate the original target contribution
from the added leaf contribution. The first is an original partial
average and the second is a signed constant. Their sum has magnitude
at most `||x||_infinity+||y||_infinity`. Thus one extra magnitude bit
and `k` fractional bits suffice for the stated shear, when the local
coefficient implementation saves both operands as specified.

The independent symbolic replay checks every arithmetic row in this
schedule, including the unhalved rows. The maximum row norm is 2 and
the maximum denominator is `2^k`. This result holds for every input
of the three finite layouts, not only for sample coefficient values.

The bare inverse code on unrelated encoded values has norm `k+1`.
For example, one output row can collect a leaf and one detail from
each level. The checker verifies this distinction. The constant
prefix bound applies to the correlated shear, as the note states.

The original sentence about increasing a local guard constant was not
enough. A new layer adds `O(e)` depth, while the old guard has a constant
local term. The amendment supplies the needed proof. With a valid path
bound `sum_j(e_j/e)^rho<=theta<1`, local depth `E+c e`, and the inherited
leaf bound, choose `C` to cover the leaf coefficient and
`(E+c)/(1-theta)`. At an internal node,
`d^(-beta(rho-1))e^rho>=e`, so the induction gap covers `E+c e`.
The guard exponent is unchanged.

This remains conditional on the resulting path bound. A cross-owner
operation inside the provider can change the old child paths even if
it adds no child. A boundary composition preserves those old path
classes when every old entry and exit role is covered by the inherited
bound. The separate actual-owner binding is not checked here.

## Completed-frame phase

The required convention is
`O_i=i^gamma_i (X_delta_i C_U_i)^(tensor lambda)`, where `gamma_i`
is the total phase. For each Fourier pair `(chi,chi+omega_n)`, an odd
line has one eigenvalue 1 and one eigenvalue i. An orthonormal basis
of rank `r_i` therefore contributes `i^(r_i f)` over `f` pairs.
A common translation contributes
`(-1)^(f omega_n.delta_i)`. This proves the amended `eta_i` formula.
An orthogonal coordinate conjugation fixes `omega_n` and preserves
the same support. A separate coordinate permutation is not a scalar
on that support and must remain in the interface.

The checker verifies 22,016 exact phase equalities over small ranks,
translations, total phases, and Fourier support points. A one-column
phase must be multiplied by `lambda` before it is used as `gamma_i`.
The separate amendment resolves this material notation ambiguity.

## Sources and limits

The review read the five source proofs pinned in `CHECK.json` directly
from Git object `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. This includes
the original four stream sources and `notes/bulk-complex-guard.tex`.
The numerical motif in that historical source is not a new selected
frontier. Its general stream and conditional guard arguments are the
dependencies used here.

No native owner placement, full controller, internal machine code,
new finite guard constant, full primitive invoice, recursive supplier,
or kappa improvement is certified. The affine projector still has
fraction `2^(-n lambda/2)`; this review provides no broader coverage.
No producer or earlier review file was changed. No PR, commit, or push
was made. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
