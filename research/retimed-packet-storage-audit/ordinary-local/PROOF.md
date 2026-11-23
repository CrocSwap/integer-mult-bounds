# Uniform byte envelopes for the installed ordinary work tapes

## 1. Result and exact scope

For the installed binary ordinary receiver of Ali Romman's #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`, every transient work-tape tuple
position has the coordinatewise bound in Section 3. If W is the complete
input byte volume of the containing weighted activation, B is its compiler
owner count, and V=W/B is one complete owner, the sum of the uniform local
coefficients is

\[
\boxed{A(B)\le 17+54/B.}                                      \tag{1}
\]

In particular A<=71 for B>=1 and A<21 for B>=17. These are **uniform bounds
per fixed site and tuple position**, followed by a sum. They are not inferred
from the maximum of a simultaneous sum in one measured invocation.

The retained 91-slot inventory contains six `compact_crt.binary_swap` slots
which occur only in the public cold binary branch and are never reached
inside a native weighted activation. Excluding these six as well as the two
public rectangle, five root and eleven cold ternary slots leaves **67 native
transient positions**. The six binary slots have zero coefficient in A;
their separate public-branch historical envelope is at most 3X for one
complete unpadded binary prefix slab X. This resolves all 73 positions left
after the original 2+5+11 subtraction without misclassifying the cold six.

This proves local file-byte envelopes and permits their substitution in the
separately reviewed ordinary ancestor-composition theorem. It does not prove
the binary raw owner-capacity premise, private-control/header costs, fixed
tape movement, outer Gaussian/CRT allocation, activation thresholds,
analytic recovery, or a new kappa. `owned_erasure` remains the source's
ownership contract; a zero-test is not substituted for it.

`SOURCE-BINDINGS.json` pins the exact resolved source modules. The installed
inheritance and selected-body census are the retained
`check_stage_inventory.py` contract; `ROLE-INVENTORY.json` records its 19
work sites. The proof applies to successful installed calls with complete
input intervals and the source's positive dimensions. It does not assert
the same bounds for every standalone call accepted by a low-level API.

## 2. Complete caller volumes and legal shapes

Write the weighted input as

\[
W=A O\alpha^{2c}GS,\quad \alpha=3^{w},\quad
w=\operatorname{total\_width}(layout),\quad c=Nf+r.
\]

When f>0 the source checks `A=U B Q H`, with U positive, B=`core.owners`,
Q=`core.low` and H=`core.high`. The two residual factors `alpha^r` multiply
the true gap and suffix. Thus `binary_receiver.Receiver.compiled` constructs
each `OwnerBanks` slot with volume

\[
V=UQHO\alpha^{2Nf}(G\alpha^r)(S\alpha^r)=W/B.       \tag{2}
\]

This is the size of one owner, not the historical extent of its backing
bank. The backing and its potentially many live owners are separately
charged named storage. `clone`, `swap`, `xor` and `OwnerBanks.route` copy
one or two such complete owner intervals; they do not copy the backing's
full capacity into their work files.

`direct_route` acts on exactly V. Its `pair_shape` removes the two selected
atom axes from prefix/gap/suffix, and `lower_tape` or the earlier swap
reinstates both. A direct scale removes one selected axis and reinstates it
as `3**total_width(layout)`. Covered `Receiver.transition` passes

\[
D=O\alpha^{2Nf}G'S',\qquad V=UQHD                 \tag{3}
\]

as its body and owner volumes, where G',S' include the residual factors.
`quotient_right_route` processes one group of volume QHD at a time.
`high_packet` has size HD. Each affine subpacket is
`3**((digits-1)*(q-used))*D <= HD`, and its scale is the same complete
affine volume. The transform callback receives a complete body D and
`Receiver.compensate` outputs exactly D. No unused, older, high, gap or
suffix coordinate has been discarded in these inequalities.

The eight `lower_tape`, `negate_tape`, and `weighted_pair` positions can also
be used by stopped pairs in the weighted activation itself, of volume W.
They therefore receive W bounds even when a particular use acts on a much
smaller owner or low packet. Compiler type transposes use W; line type
transposes use V. The shared type-route roles receive the W envelope.

### Run-length and positive-width contracts

For `lower_tape`, every component must receive a coefficient run list whose
lengths sum to its declared prefix. This follows at every installed caller:

- stopped pairs emit `available*older` runs of length `alpha**axis`;
- direct routes emit `unused*older` runs of length the product of all
  intervening visible axes;
- compensation emits `older` runs of that visible product;
- `five_exchange.same_order_line` emits `unused*heights*older` runs of
  the visible product;
- `weighted_pair` preserves these lengths when it transforms coefficients;
  its ungrouped form emits one length-one run per prefix.

In each case multiplication gives exactly the prefix from `pair_shape`.
Arbitrary externally supplied run lists are outside this source contract.

The installed layout has positive component widths: `stage_body` uses a
positive width, a positive component width, and
`count=ceil(width/component_width)<=width`; hence its `short>=1` and every
emitted component has size at least one. The receiver requires N>=2.
Compiled routes occur only when f>=1, and all outer cardinalities and byte
suffixes are positive. These facts are needed for the tag argument below.

## 3. Complete coordinatewise table

Every table entry bounds **each individual named position** for every
successful installed invocation, regardless of mode, coefficients, sibling
history or which position happens to attain the largest peak.

| Source site | Positions | Individual upper envelope | Contribution to A(B) |
| --- | ---: | --- | ---: |
| `direct_body.scale_atom` | 22 | V for each | 22/B |
| `module_atoms.lower_tape` | 3 | W for each | 3 |
| `module_atoms.negate_tape` | 3 | W for each | 3 |
| `module_atoms.weighted_pair` | 2 | W for each | 2 |
| `quotient_route.affine_packet` | 3 | V for each | 3/B |
| `quotient_route.high_packet` | 2 | V for each | 2/B |
| `quotient_route.quotient_right_route` | 10 | V for each | 10/B |
| `limb_scale.unit_scale`, main tuple | 3 | V for each | 3/B |
| nested `unit_scale.odd_step` | 7 | V for each | 7/B |
| nested `unit_scale.carry_step` | 1 | V | 1/B |
| `raw_binary.Banks.clone` | 1 | V | 1/B |
| `raw_binary.Banks.swap` | 2 | V for each | 2/B |
| `raw_binary.Banks.xor` | 2 | V for each | 2/B |
| `receiver.OwnerBanks.route` | 1 | V | 1/B |
| `streaming_routes.type_route` | 5 | (3,3,1,1,1) W | 9 |
| **Native transient total** | **67** | | **17+54/B** |
| `compact_crt.binary_swap` | 6 | unreachable inside native weighted calls | **0** |

The excluded root/public/cold ternary positions retain their separate
composition charges. A retired invocation's peak is not discarded:
the table bounds its retained historical endpoint as well as its live size.

## 4. Proof of the local envelopes

### Full-volume alternating spools and direct factor buckets

The standard two-spool step seeks its current source to zero, executes a
whole-interval map into the blank other spool, erases the current spool,
then swaps the Python references. Thus each physical spool's endpoint never
exceeds the complete input volume. The result holds across arbitrarily many
components and gates because erasure resets the destination before reuse.
It applies to the main pairs in scale, lower, negate, weighted pair, affine,
high and unit scaling. For high packets, serial transformed bodies and
affine prefixes append to exactly HD, not one extra HD per subcall.

In `scale_atom`, `abs(numerator)` and denominator are at most 20; twenty
bucket positions are reserved. For `integer_scale` with k>1, a forward
bucket contains at most `ceil(side/k)*piece <= side*piece` bytes. The
inverse selector distributes the same side records among k buckets, with
that same bound. Each bucket is emptied and erased for every prefix.
Negation's reused bucket holds `(side-1)*piece`. Both are bounded by the
complete component interval `prefix*side*piece=V`. The global current and
other files each hold V. This proves all 22 coordinatewise V bounds, with
no factor proportional to the number of components or the factor magnitude.

For a shift, scratch holds at most `side*piece`; for a negation it holds
`(side-1)*piece`. The remaining dimensions are positive, so these are no
larger than the complete input. The actual run-length identities ensure
lowering appends exactly that input to the other spool. Weighted pairs keep
two complete spools across strictly earlier swaps; the earlier service
receives the true full pair, not an enlarged scratch copy. Clone, swap, XOR
and owner route each fill their listed work positions with precisely one
owner. Chunked reads do not add file extent; their private control/buffer
realization is outside this data-byte statement.

### Unit-scale odd and even finishes

The `unit_scale` schedule preserves

\[
front\,3^v\,tail=E,
\]

where E is its incoming complete field, at most V. On an odd step v decreases
by one and tail is multiplied by three. The saved finish is on the full
`front*side*3*branch_piece=E` interval. Each of the three input buckets, three
output buckets and shift scratch holds at most `side*branch_piece<=E/3`.
The output-bucket assignment is a permutation because the valid scale unit
is nonzero modulo three. All seven positions are cleared for each prefix.

On an even step v is halved. The present two limbs have complete volume
`front*base**2*tail=E`; subsequent tail multiplication by base preserves
the invariant. The saved carry finish has `front` prefixes and `base` low
values; each shift's one temporary holds at most `base*branch_piece<=E`.
Every finish retains its saved complete shape. The main temporary is used
only for rotations or a final negation, each bounded by E. The schedule
stores descriptors, not a new payload spool per level. All eleven fixed
positions therefore satisfy V, independently of recursion depth and unit.

### Tags and the installed body guard

Set `t=N**2`, `Q=low_count(N)` and `L=H*D`. For one quotient group the
data volume is QL and the tag volume is Qt. Because f>=1, alpha>=3 and all
other factors in (3) are positive,

\[
D\ge3^{2N}\ge N^2=t.                              \tag{4}
\]

For example `3^N>=N` follows by induction from `3N>=N+1`; squaring proves
the second inequality. Hence `Qt<=QL<=V`.

The ten route files are two data streams, two tag streams and three pairs
of data/tag radix buckets. A stable pass partitions all Q records; a data
bucket has at most QL bytes and a tag bucket at most Qt. The source data and
tags are erased before collection; every bucket is erased after copying.
Alternating outputs are consequently blank before the next pass. At return
both stream copies are empty, so a new group does not append to old tags.
Every one of the ten fixed positions is bounded by V, including tag-heavy
low orders and different historical maximizing groups.

The guard is essential. The standalone API accepts N=2, digits=1,
groups=1, suffix_bytes=1. Here Q=16, input=16 bytes, and a tag stream holds
64 bytes. A nontrivial legal word therefore gives a valid API example whose
tag head exceeds three input volumes. It is not an installed production
counterexample: `Receiver.transition` supplies D>=81 in this smallest
compiled geometry. The theorem uses that actual caller, not the API's
weak suffix validation.

### Type transposition and the public binary branch

For type input R=`rows*types*suffix_bytes`, let E be the least power of three
at least `types`. If types=1, no work files are opened. Otherwise
`types<=E<3*types`. The two alternating files hold at most
`rows*E*suffix_bytes<3R`. Each of three bucket files holds at most a third
of that padded interval, hence less than R. Forward and inverse loops
erase all buckets per group, so (3,3,1,1,1)R is uniform in direction and
shape. Here R<=W at every installed use.

In the public no-native-stage branch, `ordinary_swap` calls `binary_swap`
one prefix slab at a time. Its two spools are at most X each; four digit
buckets each hold at most X/4 and are cleared per outer prefix. Their
coordinatewise historical sum is at most 3X, even though their peaks may
occur at different times. This branch returns before the ternary rectangle
or any weighted receiver is opened. Native recursion calls `ternary`,
whose terminal branch is the separately charged eleven-file cold ternary
interchange. It never returns through `ordinary_swap` into the binary six.

## 5. Composition and limitations

Substitute (1) as A_j for each stage j in the ordinary ancestor proof's
equation (8). Its source-derived fence ensures a work role is not reentered
by a same-stage weighted child while live; strictly earlier stages have
different indexed roles. Since W_child<=W_parent, every same-stage use is
bounded by this stage's largest entering W. Thus these **coordinatewise**
local envelopes compose exactly as required, without multiplying the true
child by a scratch constant or summing simultaneous maxima incorrectly.

For the retained binary owner-capacity premise beta_j=2 and B_j>=17,
using the convenient A=21 gives the seven-stage corollary

\[
H_{ordinary}<9530T<85770X.                         \tag{5}
\]

The exact substitution `A_j=17+54/B_j` is stronger. Equation (5) includes
the separately charged root files, cold ternary roles and public rectangle
from that theorem; caller input/output backing is excluded as before.
The alternative public cold binary branch is at most 3X and is disjoint
from this native branch. These coefficients concern historical data-file
endpoints. Fixed delimiter allowances, source-header and Python control
objects, machine movement and external services retain their own bills.

These numerical entrance bounds concern a fresh reservation. On a warm
reservation with preexisting role endpoints K0_r, zeroing a head does not
reclaim its historical interval: the new endpoint is bounded using
`max(K0_r,h_r)` for each role. A sufficient aggregate allowance is the old
sum plus the fresh bound. Across multiple differently shaped entrances use
one uniform Xmax for every role, and include the cold binary six's 3Xmax
even if the last entrance was native. The cold and native branches are
disjoint within one call, but their different heads can retain peaks from
different calls. This is the boundary recorded independently in the
ancestor-composition review's `ENTRY-HISTORY.md`.

The proof is universal in installed valid shapes; finite exact-source byte
traces corroborate the bindings and catch implementation mistakes. They do
not execute the selected enormous ranks, prove all allocation contracts,
or provide external human or formal-kernel acceptance. The source's
binary owner/mass premise is still needed by the ancestor theorem.

## 6. Credit and next questions

Ali Romman and the retained predecessor authors receive the #8042 algorithm,
stage-role, arena and owner-interface credit. The existing packet, byte,
type-route and wide-owner audits supply the earlier local and composition
context. #5404 and #5286 are predecessors for coordinatewise historical
accounting; generic sum-of-head-maxima reasoning is not new here. The new
contribution is this complete source-bound ordinary table, its all-caller
volume and tag guards, and the finite API counterexample identifying why
those guards matter.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI ChatGPT
assistance. Apache-2.0. Remaining tasks include an independent proof of the
binary owner-capacity premise and explicit physical/control/header charges;
they are not silently absorbed into A or the historical data-byte bound.
