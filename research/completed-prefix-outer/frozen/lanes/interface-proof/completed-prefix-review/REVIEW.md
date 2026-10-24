# Independent review of completed-prefix codes and past-coordinate layout

The two source notes pass within their stated scope. They give an exact
opposite DIF procedure, an outer composition rule for physical completed
coordinates, and a conditional address wrapper for a fixed past-space
native word. They do not give that native word or its recursive closure.

The reviewed notes are `temporal-reuse/COMPLETED-PREFIX-CODES.md` and
`temporal-reuse/PAST-CATALYST-LAYOUT.md`. Their exact hashes, both producer
hashes, both receipt hashes, and six Git source hashes are in `REVIEW.json`.
The Git revision is `3ae9a6f3ac74ded022ab3b4872a7357a621af6fb`.
The source files were read directly from Git. No frozen source changed.

## Exact opposite and completed coordinates

Let an axis have length `2^a`, with input bits `x_h` and output bits `z_h`
in their physical positions. Use the proposed low-to-high opposite
procedure. Its exact matrix entry has magnitude `2^-a` and phase

\[
r\sum_h x_hz_h+
\sum_{h<v}r2^{h-v}z_hx_v\pmod {2r}.
\]

The first sum is the sign from each butterfly. The second sum is the new
twiddle. Expanding

\[
(2r/2^a)z\operatorname{rev}_a(x)
 =\sum_{h,v}r2^{h-v}z_hx_v
\]

gives the same value: the terms with `h>v` are multiples of `2r`.
The scalar is the required normalized transform scalar. This proves
`F_plus B^-1` over the actual polynomial quotient ring, for every axis
length. It does not rely on a finite-field example. Different axes
tensor together, and each long or short axis uses its own `a`.

The source layout L only relocates named slots. Applying this new word
in that layout, then restoring L, gives
`F_plus B^-1 L^-1`. No extra physical bit reversal is needed. The
butterfly at physical position h is unchanged from the retained
opposite schedule. Only its monomial exponent and its position relative
to the butterfly change. The same statement holds if all axes are
short; the header value ell still defines L.

After the new opposite round at h, every later twiddle uses only higher
physical slots. The forward source has the corresponding property with
lower unprocessed slots. Thus the remaining exact operator is identity
on every completed slot in both procedures. A code confined to those
physical slots commutes with the remaining exact transform. Arbitrary
row values and arbitrary correlations between rows are permitted.

The layer and monomial are contractions in the source norm. The monomial
is a signed coefficient permutation, so it commutes with componentwise
truncation toward zero. There is still one truncation per round. The
original unencoded disk and error bounds therefore apply to this new
opposite procedure. A proposed encoded procedure needs the separate
code-growth allowance described below; this review does not transfer
the unencoded error bound to it without that allowance.

The current named-slot table computes the new exponent with polynomial
work in p per polynomial record. The source record size absorbs that
work. The same two-piece monomial scan applies. The layer slots, number
of rounds, chunk movement, and time order remain unchanged.

## What the decoder bound does and does not cover

For a fixed h-bit completed prefix, the code dimension `w=2^h` is fixed.
Suppose each whole-layer endpoint leaves a member of one fixed finite
alphabet in `GL_w(Z[i,1/2])`, and the program supplies its inverse. The
product order is the actual chronological order. The matrices need not
commute. All entries of the product and inverse have `O(ell)` bits,
including denominator exponents, because the number of factors is
`O(ell)` and the dimension and alphabet are fixed.

One can form the inverse as the reverse product of the supplied inverses.
No new division or field extension is required. A fixed number of row
buffers and direct shift-and-add arithmetic then apply it in
`O(V ell)` time. Polynomial controller setup is absorbed by the full
polynomial-record stream. The code and inverse norms require `O(ell)`
extra integer, grid, and error-control bits. Since `ell=o(p)`, this does
not change the width exponent. It does require a new finite precision
allowance. The exact selected margins for this order and the startup
order are checked from the pinned assembly.

This theorem has fixed matrix dimension. The whole-axis row construction
is a different lemma. It provides enough completed row bits for all
`W^k0` recursive row classes, but it does not prove an `O(V ell)` decoder
for an arbitrary code on that growing bank. Nor does it prove that bound
for arbitrary codes on `Theta(d)` past payload bits. Repeating a
`Theta(d)`-factor decoder for every round would still cost
`O(V ell d)`. A finite-order tensor code can avoid that cost only after
its physical endpoint and composition law have been proved.

Completing one whole synthetic axis first is valid in either direction:
different-axis transform factors commute. It costs `O(V ell)` and
supplies `Theta(ell)` completed bits. The required row digits number
`ceil(ceil(log_m d) log_2 W)=O(log d)`. They fit for all sufficiently
large source parameters. Padding the complete row range to a multiple
of `W^k0` increases volume by less than two. Every split `u=Wg+w`
retains the same full remaining suffix and has exact child volume
`V/W`. Padded rows must remain until the code is inverted and they are
zero again. The extra truncation or exact-grid choice for the first axis
is part of the new allowance, not the old finite certificate.

## Current-twiddle criterion

The criterion in the source note is correct for codes with complex
scalar entries which fix the lower unprocessed index and the polynomial
payload. At a nonterminal selected axis, set one lower input bit to one.
Its diagonal twiddle has eigenvalues 1 and
`z=y^(-2r/u)`. The intertwining equation forces every nonzero entry in
one output row of the code to come from the same branch value. Repeating
this for every selected axis forces a unique branch address in that row.
Dense mixing within the completed row index at that address remains
allowed.

Allowing a record permutation in the replacement monomial does not
remove the restriction. The conjugate satisfies
`(D'-I)(D'-zI)=0`. A permutation cycle of length at least three puts
the three terms in different positions. A two-cycle leaves the nonzero
off-diagonal term `-(1+z)D'`. Here `1+z` is a unit: `z^(u/2)=-1`, and
the finite geometric sum gives an inverse with denominator two. Thus
the conjugate must be diagonal. This argument is valid in the quotient
ring even though that ring has zero divisors.

An odd line `C_q=aI+bX_q` mixes two branch addresses when q has a current
coordinate. Its conjugated one-coordinate twiddle has four unit entries
in the `2 x 2` block over `C[y]/(y^2+1)`. The inverse line has the same
property. Diagonal H0 phases do not change support. In the paired code,
the replica exchange does not remove these entries. Independent tensor
copies give `2^lambda` dependencies. A pure address permutation is a
counterexample to an overbroad rejection: it passes with a changed
twiddle exponent. Terminal axes of length two, codes with polynomial
entries, and a new arithmetic twiddle algorithm are outside the stated
necessity theorem. Cancellation in a complete encoded endpoint is also
not excluded by testing one factor.

## Physical past-block wrapper

For complete fields X and Z of length L, the three specified disjoint
interchanges send `X=A B, Z=C D` to `X=B A, Z=D C`. Taking
`c=(L-rho) mod L` puts every old selected position `jK` at `jK+rho`.
Conjugating a native word by this permutation therefore gives exactly
its action on the old selected coordinates, provided that the native
word fixes Z and all unselected positions. The conclusion applies to
every linear value map on the selected coordinates, not only to an XOR
mask. All address bits and arbitrary data outside that support return
to their required positions after the literal inverse wrapper.

The temporary adjacent-block exchange is also valid on arbitrary
values. With three or more chunk groups, a neighbor distinct from the
active group and the reserve exists. At the `64:9` split, the past block
and its equally sized spectator fit inside an inactive group. Before
that reserve group becomes active, the initial bit exchanges are undone
and a new reserve is made in a fully completed group. Displaced future
bits keep their named-slot identities in the descriptor. Their changed
physical location does not make them completed bits, and every current
native word must fix them. The twiddle still reads their logical names.

The entire address rectangle remains complete. No zero-address or
clean-value premise is used. Six rotation interchanges, two adjacency
interchanges, and the fixed slot-order permutation have the source
`O(V ((eK)^tau+1))` node bound. The one-time named-bit placement and
restoration use `O(Vd)` work. The exact selected inequalities give both
the startup margin and asymptotically three chunk groups. The literal
map counts, descriptors, and compact precision guards still need a new
finite invoice. This review adds no native Fourier children and grants
no new productive field.

## Exact remaining supplier obligation

A useful new whole-layer interface must prove its physical map to be
`A_P tensor H_current`, with P a fixed completed physical space, and
must restore all required arbitrary helper inputs. Its declared
recursive child must implement `E_V F E_U^-1` at each parent edge.
Every parent scalar gate needs equal physical codes on its operands.
All preparation, address maps, helper conversions, native children,
padding retention, final decoding, precision, and stack work must be
priced with the active child dimension and volume actually used.

The selected cover does not satisfy this condition merely because its
local nine-dimensional space can be packed into past positions.
The separate, pinned Schur notes prove that closure under the retained
stage routes expands the common line span to all 73 coordinates.
They also give an active-rank lower count of 1,615,856 for the prescribed
local-nine gauge visits, versus productive active mass 917,504. Adjacent
gauge-only fusion does not reduce that count because an owner's active
visit masks are disjoint. These scoped results do not rule out a new
cover, exterior gauge, content factorization, or typed child family.
Their proof and count review is separate; this review uses them only to
state the unresolved interface, not as a newly reproduced native bill.

## Checks and reproduction

Both producers were run with `-I -O -B` into new output paths. Their
outputs match the frozen receipts. The independent `review_prefix.py`
imports neither producer. It checks exact forward and opposite phase
entries for axis widths one through eight in the polynomial-ring
convention; actual long/short/all-short chunk offsets; nonadjacent
rotation and literal inverse maps; early and late reserve placement
with three, four, or five groups; and exact Gaussian-rational twiddle
unit entries. The finite checks validate the formulas. The all-size
claims use the proofs above and the pinned stream lemmas.

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/completed-prefix-review/review_prefix.py
```

Expected output:

```text
PASS_INDEPENDENT_COMPLETED_PREFIX_AND_PAST_LAYOUT_REVIEW
Exact DIF phases, current twiddle, selected offsets, full guard and reserve restoration
```

This external review needs the pinned workspace files. It is not a
portable repository test. It was prepared with OpenAI Codex assistance.
No complete encoded supplier or kappa improvement is certified.
