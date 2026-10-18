# Conditional packet lifting of the interleaved COPY window

This review proves a sufficient interface for lifting PR2407's literal
303 target-to-target XORs and ten immutable-snapshot taps to complete
local-ring packets. It derives a 929-action route tariff for the specified
copy/route/update/return/discard implementation. That tariff is an action
inventory, not a numerical machine-work invoice or a reversible dirty-work
construction. The rank-seven creation and final erasure of the retained
snapshot are outside the reviewed fragment.

The mathematical argument was developed separately from this package's
finite routing implementation. It uses PR2195 and PR2437 source texts at the exact commits, blob IDs and
SHA256 hashes listed under `reviewed_documents` in `PREDECESSORS.json`,
and the literal window and tap witness in PR2407. Those public documents
are linked there; they are not duplicated in this package. It
does not independently reprove the predecessor's complete scalar endpoint
or certify its whole supplier. The scientific base is
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

## Complete packets and exact route convention

Fix a prime q, w >= 1, m >= 1, R = Z/q^w, and a low invocation
`d0 in GL_m(F_q)`. The fragment's routing argument works for every prime;
the inherited dyadic frame/weighted supplier argument retains the odd-prime
restriction. Set

```
F_a = {g in GL_m(R) : g mod q = a}.
```

Each such packet has `q^(m*m*(w-1))` matrix addresses. It retains every
spectator and suffix coordinate of the original stream, with their actual
volumes. Let role i have family f_i and unit chart `sigma_i in GL_m(R)`.
Charts may depend on already exposed ancestor data, which is fixed during
this argument; each chart is constant over the complete packet currently
being routed and does not consume an unused descendant row field. Its owned
packet and forward route are

```
P_i = F_(d0 sigma_i_bar^-1),
r_i : P_i -> F_d0,       g |-> g sigma_i.
```

The inverse is right multiplication by `sigma_i^-1`. These are exact
bijections over R. For any roles in the same family, require distinct low
owner classes. Equivalently at this fixed d0 their chart reductions are
distinct. Then their complete owned packets are disjoint. Different family
tapes are distinct storage regardless of chart equality. The original
copied source, every target, the snapshot work stream, and unrelated reserved
storage must obey the corresponding ownership exclusions.

Pointwise owner separation alone is weaker. In GL_1(Z/9), charts 1 and 4
give distinct owners d and 7d for every unit d, but both send the entire
low packet `F_1={1,4,7}` to itself. Thus those two roles cannot be treated as
disjoint complete packets of one family. This is a small instance of
Jose Manuel's PR2195 obstruction; no new owner-separation theorem is claimed.

Carries are part of r_i. For canonical integer representatives write
`g=g0+qG`, and let s represent sigma_i. If d0 is the entrywise residue of
`g0 s` modulo q, then the output high matrix is exactly

```
D = ((g0 s - d0)/q + G s) mod q^(w-1).
```

This includes the integral carry matrix `(g0 s-d0)/q`. The same formula
with an actual inverse chart supplies the return route. An operation on
high matrices that drops that carry is generally not the specified address
permutation. The case w=1 has a singleton high fibre and no nontrivial high
coordinate. No claim about uniform route complexity follows from this formula.

## Boundary contract and event induction

Let M be any F2-module. Payload values are arbitrary functions on complete
matrix packets and complete spectator/address coordinates. They may be
correlated, including identical values in different storage locations.
The frame/gauge contract is inherited: after routing to the same d, all
target operands and the snapshot use the same data-address correspondence.
Aligning the matrix header alone does not prove this if their data frames
differ. PR2407's interior uses a common target frame and no logical MOVE.

Write `Y_i(d,z)=F_(f_i)(d sigma_i^-1,z)` in this common gauge. Here z includes
all unaffected coordinates and suffix payload positions. Let S(d,z) be a
snapshot already stored in this same d order and gauge. The fragment
preserves S for every possible S. The stronger equation identifying S with
the transported original copied source must be supplied at entry by the
external rank-seven COPY contract.

At an event boundary, assume that fresh packet buffers are blank, their
heads are reset, the family's physical arrays decode to the current Y,
S is unchanged, and all unrelated live values and arbitrary dirty parked
values equal their specified current inputs. All elementary operations and
route callees must close their private work, restore spectator coordinates
pointwise and return the declared heads. A packet route acts on its selected
fresh packet; it cannot use other live ports or the snapshot as unproved
scratch.

For a target event `Y_t <- Y_t XOR Y_s`:

1. Select fresh copies of the complete target and source owned packets,
   without modifying either original family.
2. Apply r_t and r_s to those two copies. Their aligned entries now are
   exactly `Y_t(d,z)` and `Y_s(d,z)`.
3. XOR into the target copy, apply `r_t^-1` to it, and write the result to
   precisely the owned target packet. Leave every other original cell alone.
4. Discard the fresh copies and return their heads under the charged stream
   contract discussed below.

Therefore for `g in P_t` the physical update is exactly

```
F_(f_t)'(g,z)
  = F_(f_t)(g,z) XOR F_(f_s)(g sigma_t sigma_s^-1,z).
```

Disjoint ownership ensures that source and spectator originals survive
unchanged. There is no need to return the source copy to its old order before
discarding it in this model.

For a snapshot tap `Y_t <- Y_t XOR S`, select only the target packet, apply
r_t, XOR with the immutable aligned S, apply `r_t^-1`, and return precisely
the target packet. Discard its fresh copy and restore the declared heads,
including the snapshot read head. The physical increment is
`S(g sigma_t,z)`. S is read but neither modified nor borrowed.

Both macros restore the event-boundary invariant. Induction in the literal
313-event order proves the whole fragment for arbitrary payload functions,
arbitrary complete spectator ranges, and every admitted q,w,m and chart
tuple. No freshness or independence assumption is made about original
targets or helpers. Fresh work buffers are an additional blank resource;
they are not arbitrary dirty helpers.

More explicitly, let `H_0,...,H_302` be the target shears in execution order,
let `H=H_302 ... H_0`, and write (k,i) for a tap into i after k target shears.
Then

```
Y_out = H Y_in + sum_(k,i tapped) H_302 ... H_k e_i S,
S_out = S_in.
```

The literal cuts are `(0,13),(0,26),(0,34),(0,58),(0,79),(0,90),(0,95),
(104,6),(126,24),(182,3)`. At k=303 the suffix product is the identity.
Matching an aggregate tap count is insufficient. For example, tapping
`y1 += S` before `y2 += y1` propagates S into y2; doing it afterwards does
not. Reversing the literal event order gives the inverse fragment because
each decoded XOR shear is an involution. The surrounding complemented
orientation still needs its own inherited COPY/frame boundary binding.

Snapshot/source equality, if true at entry, survives because both terms are
immutable throughout the fragment. Consequently the external transported-
source ERASE guard is still true at exit. This establishes guard preservation,
not an implementation of either the initial COPY transport or final ERASE.

## Exact action inventory and the missing work terms

Let V_p be the logical volume of one complete packet, including spectators.
Let `T_i^+(V_p,w)` and `T_i^-(V_p,w)` denote the fully charged forward and
inverse route tariffs for role i. Neither equality nor uniform linearity of
these tariffs is assumed. For target event e=(t,s), a sufficient invoice is

```
A_e + T_t^+ + T_s^+ + X V_p + T_t^- + B_e + D_(2,e) + J_e.
```

Here A_e pays selection and fresh copying; B_e pays the full target-family
writeback scan; D_(2,e) pays disposal of two fresh copies; and J_e pays any
descriptor preparation, counters, rewinds and head restoration not already
inside those named complete tariffs. Do not charge the same operation in
both a route tariff and J_e. Selection can share a scan when both packets
are in one family; otherwise both family scans must be paid.

For snapshot tap e=t, replace the route part by `T_t^+ + T_t^-`, omit the
source-copy selection, and use `D_(1,e)`. Snapshot reads, positioning and
return are paid. Summing gives

```
target events: 303 * 3 = 909 route actions,
snapshot taps: 10 * 2 = 20 route actions,
total: 929 route actions and 313 packet XOR passes.
```

There are 616 fresh packet copies in total: `2*303+10`. Under the stated
discard implementation the same 616 packet volumes are disposed of. This
does not include the already-live snapshot's creation or final erasure.
An implementation which unnecessarily returns source copies would have a
different route inventory. No optimality claim is made for 929.

If all relevant families have volume V_F and the finite selector constants
are absorbed in C_sel(q,m), a coarse form of the nonroute bill is
`O(313 C_sel(q,m) V_F + 313 V_p)` plus any explicitly excluded descriptor,
parking or route preparation costs. This uses a fixed 313-event word and
fixed q,m, not an unpriced loop through the growing high-address set. A sweep
over low invocations multiplies the appropriate finite low-class costs.
It must still complete each whole local word before proceeding to the next
low invocation; packet reuse across different invocations does not authorize
commuting their partial words.

The peak outer payload reservation during a target event is two fresh
packets plus the one retained snapshot, namely 3 V_p. A tap needs one fresh
packet plus the snapshot. These are interface buffers only. Route-private
scratch, any implementation's scan/merge staging, controller tables,
descriptors, and ancestor parking storage are additional. Sequential reuse
means route scratch peaks by a maximum after proving disjoint allocation;
it is not summed across all 929 actions. No complete numeric peak-workspace
bound follows without those contracts. Work copies never increase the
logical-volume denominator in the recurrence.

## Erasure and parking: two model boundaries

The retained stream model in `upstream/build/sections/02-streams.tex`
explicitly charges copies, erasures, resets and complete-range scans. It is
a logical/Turing-stream implementation model; it does not require every
elementary machine step to be logically reversible. Discarding the routed
source copy is valid under this model after its read has finished. All
original inputs retained by the shear survive, so the logical input-output
map remains the specified invertible shear even though its implementation
uses overwrites and deletion of redundant copies.

The same procedure does not establish a circuit using arbitrary dirty
ancillas. In a reversible gate model, `B <- 0` is not a permitted operation
on arbitrary B, and a copied source sitting in d order cannot be cleaned by
XORing the original in a different owner order without an alignment proof.
The completed target copy likewise needs a justified clean-up operation.
One could seek a reversible schedule using uncomputation or transported
equality tests, but its operations and tariffs must be proved afresh. Simply
replacing a fresh blank packet by an arbitrary dirty packet introduces its
unknown dirt into the XOR result. This review makes no such replacement.

The fixed-tape parking schedule in `upstream/build/sections/04-swap.tex`
parks inactive parent streams, isolates child I/O, restores stack heads and
forbids scans through parked ancestors. Applying it here requires an enlarged
caller inventory which includes the live snapshot and whichever fresh packet
is inactive during each route. Their push/pop and copy/erase costs must be
paid at the actual call volume. A reserved snapshot cannot be declared free
descendant scratch because it will eventually be restored. For example,
`S ^= z; y ^= S; S ^= z` restores S but changes y by `S_old XOR z`, not by
`S_old`.

There is no logical RAW6 MOVE in this window, but the 929 physical route
actions may each invoke recursive callees. Thus every such call must honor
snapshot exclusion, spectator preservation and ancestor parking. The absence
of a logical MOVE does not discharge these recursive workspace obligations.

## Coverage and remaining implications

The argument above is an all-parameter written conditional implication. It
does not enumerate q,w,m, and it is not a proof-assistant/kernel proof.
A symbolic finite fixture using independent formal XOR atoms at every
physical input address establishes arbitrary-payload equality on its finite
address domain by substitution. A fixture on GL_2(Z/9) alone cannot establish
uniform route complexity, all selected GL_64 charts or every recursive
spectator/allocation contract. The independent oracle should use full-ring
matrix multiplication, distinct from a digit/carry route compiler, and
should compare all original addresses, the snapshot and closed fresh work.
Negative carry, inverse-return and snapshot-borrow controls address separate
failure modes. Replaying an existing verifier is distinct from an independent
implementation of its finite operator.

The separate reviewer inspected the package's `verify.py` after the finite
implementation was available. Its source binding reconstructs PR2407's exact
RAW6 digest, checks the source472/private661 frame510-to-zero boundaries and
extracts the 313 actual interior events. The baseline oracle is the credited
16 initial taps followed by 303 target shears. It is independently compared
with the literal interleaved Boolean column map before address routing.
The endpoint oracle then uses full-ring matrix multiplication and the
baseline column map, without using the compiled low/high permutations.
Thus formula-level independence is present, although source construction
and the credited scalar witness are deliberately reused.

For the finite domain, the implementation uses all 3,888 GL_2(Z/9) matrices
in each of 111 distinct target families. One identity low invocation owns
81 addresses in each family. It checks all 431,568 target records, including
422,577 unowned records, and retains 81 immutable aligned snapshot records.
The route comparison separately covers all 48 low matrices, 64 distinct
chosen charts and 81 high matrices: 248,832 forward-route cases. Forward
routes are compiled by the carry formula into adjacent record swaps;
literal inverse programs are also checked by round trips. This fixture
does not enumerate selected GL_64 charts or shared-family target pairs.
The written disjoint-packet proof supplies the latter conditional argument.

Each atom `(family,row)` can be substituted by an arbitrary vector of suffix
and spectator bits. The interpreter combines atoms by symmetric difference
and routes them as opaque records, so its symbolic equality is uniform in
those vector values and their correlations. This is not a separate finite
enumeration of internal spectator addresses, nor a test of a lower-level
bit compiler's preservation of their order.

The snapshot mutation aliases its read list, adds a fresh atom for the first
tap, and removes it afterwards. Consequently it leaves the final snapshot
unchanged while corrupting a target: it tests the actual transient-borrowing
failure, rather than only an exit-equality assertion. The inverse-fragment
fixture reverses both event lists on arbitrary fresh inputs. That is a
check of the affine inverse fragment; it does not simulate the surrounding
reflected rank-seven COPY/ERASE boundary. The final aligned snapshot clear
uses the preserved oracle tuple and establishes equality in common
coordinates; it is not a physical source-relative ERASE implementation.

The final reviewed finite schedule mutates the selected packet arrays in
place and explicitly clears every fresh packet record after writeback.
This closes the finite symbolic buffers. The record counters charge full
selector/writeback scans, pointwise XOR, deletion and returns; the declared
adjacent-swap path is `p,p+1,p,p+1`. These are stated record tariffs, not
instrumented single-bit tape execution. Compiler planning, stored route
tables, symbolic-set manipulation, descriptor/control arithmetic, record-
internal scans and physical parking remain outside that meter. In particular,
the 162 fresh packet records, 81 snapshot records and one adjacent-swap
auxiliary record are interface storage reservations, not measured Python
peak memory or a complete recursive-workspace bound.

Under the same three-/two-route macro tariff, the baseline has 941 route
actions and the candidate has 929. The difference of twelve actions need
not equal a weighted time saving: the tap targets can have different
forward/inverse route costs. A work comparison must sum their actual tariffs.

The reviewer separately invoked the existing verifier's `run()` under
`python3 -I -B`, without writing a receipt. This passed the 431,568-record
forward check, the separate 431,568-record inverse-fragment check, all
248,832 route comparisons and all five semantic controls. The verifier's
SHA256 before and after that execution was
`e42e6158007e3677caa44e0d1a578a6342402c861c15f225cf3d2405a9c21a80`.
This is a separate execution of the package implementation, not an
independently implemented verifier. The small GL_1(Z/9) owner/carry witness
and the 929/616 tariff arithmetic above were also checked directly.

For complete supplier admission the following obligations remain:

1. Bind the full changed local words and both orientations to the inherited
   complete-packet owner charts, exact data gauges, COPY/ERASE relative
   transports and complete arbitrary-dirty endpoint. The inherited PR2437
   point-owner replay and PR2195 original-word packet proof have different
   source premises; neither alone certifies the changed all-size compiler.
2. Implement every selected forward/inverse chart route, including carries,
   complete spectators and unused row-field restoration, uniformly in the
   intended recursive parameters. Produce complete work tariffs and a finite
   selected routing invoice. A finite adjacent-swap table is not that uniform
   compiler.
3. Supply rank-seven snapshot creation and cleanup, private work allocation,
   enlarged caller parking, descriptor/controller work, family scans and head
   restoration. Establish an actual finite peak-work bound if one is claimed.
4. Reuse chronological hosting only after complete calls have the required
   endpoints; integrate idle/bad-class/fallback pieces and their charged
   recursive interfaces. Low-packet separation must hold for every shared
   family used by the actual selected calls.
5. Discharge the rounded/precision implementation, complete recurrence and
   outer analytic admission obligations. Exact Boolean packet routing does
   not establish an integer lift, a selected-frontier change or a larger kappa.

No blocker was found to this conditional packet-fragment construction.
Its useful conclusion is the exact event simulation and explicit 929-action
and buffer boundary. It does not close the obligations listed above.

## Credit

Jose Manuel's PR2195 supplies complete local-ring packets, the low-owner
separation distinction, the three-route restricted-fibre procedure and its
conditional live-row layout. Alephnan's PR1627, crediting cheesegrader's
PR540, supplies the generic frame/owner event induction and complete-call
chronological theorem. Ross Richardson's PR2407 supplies the changed literal
interleaving, and PR2437 supplies its ideal-owner consumer binding and snapshot
footprint. Their pinned sources and inherited notices are retained. Prepared
by Ross Richardson with substantial OpenAI Codex assistance in a separate
recursive-interface review agent. This is AI-assisted review, not independent
human review. New text is Apache-2.0.
