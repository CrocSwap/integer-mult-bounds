# Actual byte extents for the retained tagged routes

Source: `aliromman/integer-mult-bounds` PR #8042, commit
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. `SOURCE-BINDINGS.json` identifies
the exact installed modules, including restored predecessors. This note proves
a local historical **byte** bound needed by the retained stage estimate. It
does not replace the analytic mass, movement, macroheight, private-control or
full-site-coverage premises of that estimate.

## 1. The claimed inequality and its precise residual obligation

`STAGE-STORE.md` reserves 20 named and 91 work-file heads per ordinary stage.
Seven sets use 777 heads; allowing the public rectangle and cold terminal a
complete eighth set gives 888. Its complete logarithmic allowance is

\[
7+(m+12)+800+1024+5+35+3\operatorname{bitlength}(s+128).
\]

For `m=7` this is `1890+3 bitlength(s+128)`, strictly below the installed
`D(s)=1984+4 bitlength(s+128)`. The terms retain, respectively, the initial
stripe allowance, genuine incoming extent, local native homes, outer homes,
native heights and the physical-role count. The table of sites alone cannot
justify the local native factor: tags, padding, complete high representatives,
and maxima reached by a tape at different times must be measured in bytes.

`ACTIVATION.md` uses a route allowance of 25 payload spools plus ten times the
aggregate tag volume, then 256 local volumes including padding, repairs and
scrubs. It applies `2·8·256·80·22·3 < 2^25` at each immediate adapter and at
most 32 immediate adapters to obtain `2^800`. The proof below supplies a
stronger byte bound for the installed quotient route, the padded type route,
and the positive-column repair tags. It does **not** establish all the other
sites or the bound of 32 adapters anew.

The exact inventory extracted from the installed bodies is:

| Named page kind | Heads |
|---|---:|
| weighted | 2 |
| compiler | 3 |
| issued-leaf | 1 |
| chart-line | 2 |
| chart-packet | 2 |
| direct-coordinate | 2 |
| exposed-leaf | 2 |
| matcher | 2 |
| triangular-body | 2 |
| pending and answers | 2 |

| Work-file site | Positions |
|---|---:|
| ordinary_carrier.ordinary_swap | 2 |
| triangular_ordinary.root_body | 5 |
| receiver.OwnerBanks.route | 1 |
| direct_body.scale_atom | 22 |
| module_atoms.lower_tape | 3 |
| module_atoms.negate_tape | 3 |
| module_atoms.weighted_pair | 2 |
| quotient_route.affine_packet | 3 |
| quotient_route.high_packet | 2 |
| quotient_route.quotient_right_route | 10 |
| limb_scale.unit_scale, permanent | 3 |
| limb_scale.unit_scale.odd_step | 7 |
| limb_scale.unit_scale.carry_step | 1 |
| raw_binary.Banks.clone | 1 |
| raw_binary.Banks.swap | 2 |
| raw_binary.Banks.xor | 2 |
| streaming_routes.cold_swap_tape | 11 |
| streaming_routes.type_route | 5 |
| compact_crt.binary_swap | 6 |

There are 19 work-file sites and 91 tuple positions. This reproduces the
retained inventory; the source's selected-body coverage is inherited, not a
new whole-program call-graph certification. Empty roles still occupy these
positions even when their payload length is zero.

## 2. Main theorem: one actual owner route uses fewer than eight new volumes

Consider an installed wide `OwnerBanks.route` call. Let `N≥2`, let `w≥1` be
the complete atom width, and let `f≥1` be the number of atoms per coordinate.
Write `α=3^w`, let `d≥1` be the chart digit width, and retain all genuine
spectators from `Receiver.transition`:

\[
b=O\alpha^{2Nf}GS,\quad
Q=\prod_{j=1}^{N}(3^j-1),\quad
H=3^{(d-1)N(N+1)/2},\quad R=Hb,\quad P=QR,\quad V=UP.
\]

Here `O,G,S,U` are the actual positive older, gap, suffix-byte and group
extents. Thus `b` is one compensated body in bytes, `R` is one complete high
packet, `P` is one all-low group, and `V` is the complete owner supplied to the
route. These are the executed expressions in `Receiver.transition`,
`quotient_right_route` and `OwnerBanks.route`, rather than replacement field
counts. Each tag is the literal `bytes(x for row in image for x in row)`, of
length `N²`. The aggregate tag extent per group is `T=QN²`.

Let a role's historical length be its greatest local endpoint reached at any
time in the trace, including erasure, seeks and retired contents. Sum these
lengths for the **fixed tuple positions**, even if their maxima occur at
different times. Lengths are exclusive byte endpoints, as in the source's
`FileHead.peak`; fixed markers and control descriptors retain their separate
control charge, including when the payload endpoint is zero. For the current stage's route-owned work files and its two
compensation pages, that sum obeys

\[
\boxed{\quad L\le V+5P+5T+\frac{32}{3}R+5b<8V.\quad}                 \tag{1}
\]

The borrowed compiler bank is excluded from `L` because it already exists;
its complete actual size remains separately charged. Dirty ancestor page
prefixes and earlier-stage scratch likewise retain their own charges. This
is the source's existing ownership separation, not permission to omit them
from complete storage.

### Literal tag dominance

`b≥3^(2Nfw)` and `H≥1`, so

\[
\frac{T}{P}=\frac{N^2}{Hb}\le\frac{N^2}{3^{2N}}\le\frac4{81}.
\]

The last inequality holds at `N=2`; incrementing `N` multiplies its left-hand
sequence by `((N+1)/N)²/9≤1/4`. Also `Q≥16`. This proves dominance in actual
stored bytes. Neither a large tag count nor a small source descriptor is
used as a proxy for those bytes.

### Fixed-role proof

| Current-stage roles | Historical sum bound | Executed reason |
|---|---:|---|
| OwnerBanks.route output | `V` | transition returns one complete owner, then install reads it |
| quotient route data, other data, three data buckets | `5P` | every pass partitions and rejoins one all-low group |
| quotient tags, other tags, three tag buckets | `5T` | exactly one `N²`-byte tag accompanies each high packet |
| high_packet pair | `2R` | one complete high packet per low; each next row rewrites it |
| affine_packet triple | `3R` | exposed-prefix calls have volume `R/side^used≤R` |
| unit_scale permanent and auxiliary positions | `17R/3` | proof immediately below |
| compensate named pair and lower_tape triple | `5b` | each correction acts on one complete body, serially |

In `sort_packets`, distribution erases its data and tag inputs; merging
erases every bucket; the final copy erases both surviving input streams.
Consequently both ping-pong positions are empty at group return, including
when the number `N²` of sorting passes is odd. All groups reuse the same
zero-based roles. The bound therefore depends on one group, not the number
of groups or sibling routes. The actual `N=3` test exercises odd pass parity.

`high_packet` applies each body correction into its packet stream and then
processes row prefixes in sequence. A correction cannot grow from `b` to a
whole high packet; the callback receives exactly the original `piece=b`.
`Receiver.compensate` builds dimensions whose product is `b`, and each
`pair_shape` plus `lower_tape` preserves that same product. Its coefficient
runs cover exactly the source prefix: `older` runs of `front` repetitions.
Its named pair is reused by `pipe`, and each component erase precedes the
next component. The whole high packet is retained separately in the two
`high_packet` roles; it is never silently omitted.

For `unit_scale`, let its incoming byte extent be `R'≤R`. The three
permanent work files are each bounded by `R'`. In the iterative schedule
the invariant is `front·3^v·tail=R'`. An odd step has
`front·3·side·branch_piece=R'`; its seven auxiliary positions are each at
most `side·branch_piece≤R'/3`. The three output branches are distinct because
the multiplier is a unit modulo three. Each prefix empties them before the
next prefix. A carry step has `R'=front·base²·branch_piece` and `base≥3`;
its one temporary is at most `base·branch_piece≤R'/3`.

Thus the historical sum over **all** scaler sites is
`3R'+7R'/3+R'/3=17R'/3`. In particular it counts the odd-step and carry-step
maxima even though the two sites are never simultaneously open. Replacing
this argument with the largest simultaneous number of spools would leave a
historical-space obligation. The iterative list of finishes holds scalar
descriptors and does not open recursively nested scaler files; that control
storage remains in the private-control bill.

Adding the rows yields (1). Indeed

\[
L\le V+\left(5+\frac{20}{81}+\frac{47}{48}\right)P
  <V+7P\le8V.
\]

An empty word directly copies `V` bytes and is cheaper. The generic helper
also allows `U=0`: it opens ten empty work-file roles for a nonempty word but
never visits a payload byte. This case is treated separately rather than
dividing by `V=0`.

## 3. Historical addresses, borrowing and suspended ordinary parents

Equation (1) bounds a local role suffix. A named child page opens at the end
of its current parent. Therefore its absolute highest touched byte is its
parent's actual open-end address plus the local suffix length. Its release
zeros that suffix, pops the marker, and lets the next sibling reuse the same
base. Reading a borrowed owner or an ancestor page does not create a new
owner, but the borrowed backing and all intervening addressed bytes remain
part of that role's historical extent. Counting only nonzero bytes would be
wrong.

For varying entry windows, first take a common bound `V*` on their true
incoming volumes and apply each **individual role** bound at `V*`. Taking
maxima afterward preserves (1). Adding maxima measured at separate times
does not require their coincidence. For ancestors with different live
prefix bases, the applicable statement is

\[
\mathrm{high}(h)\le\max_t
  \sum_{\text{open local intervals on }h\text{ at }t}\mathrm{extent}(t).
\]

The previous packet audit supplies the stack/interval and same-stage-call
induction; it is an explicit input here. Same-stage temporary work scopes
finish before the next paid edge. Named pages may span that edge. A
`previous_swap` invocation can suspend local route work, but it invokes a
strictly earlier ordinary stage with distinct fixed roles; its new local
volume and the at-most-two pad remain separately charged. This note does
not relabel those ancestor or earlier-stage bytes as free local scratch.

The byte meter exercises real `TemporaryFile` objects. It checks every
read, write and seek endpoint, rejects dirty truncation, requires zero
physical file length on return, and rejects same-stage reentry of a fixed
work-file role. The fixture retains dirty compiler and triangular-body
parents, a second dirty complete owner, pending and answer prefixes, and
verifies every historical named-page tail is zero after the route returns.

## 4. Padding is a byte extent

For `type_route`, let `q≥2` be the true number of types and let `τ` be the
least power of three at least `q`. The actual input is
`V=rows·q·suffix_bytes`; the padded byte extent is
`V'=rows·τ·suffix_bytes<3V`. Each of the two permanent roles is at most
`V'`. Each of the three ternary buckets is at most `V'/3`, because a pass
holds only one third of one current prefix slab and erases the buckets
before advancing. The sum of fixed-role historical maxima is therefore

\[
2V'+3(V'/3)=3V'<9V.
\]

The inverse path uses the same bounds. Padding cells are written as real
zeros and remain counted until discarded and scrubbed. For zero rows or
zero suffix the function opens no scratch; for `q=1` it directly copies
without opening scratch. Borrowed input and output extents remain separate.

## 5. Positive repair tags: exact bound and production binding

The actual `Columns.repair` has ambient dimension `L`, grouped suffix `z`,
Gaussian record size `c=2·component_bytes`, group payload `a=c·2^z`,
`r=L-z` remaining bits and tag width `t=max(1,ceil(r/8))` **bytes**. Let
`M=2^r`, `E≤M` be the number of bad groups, and `V=Ma` the field bytes.
Its four scratch roles obey

\[
\begin{array}{c|c}
\text{dirty, zero, one (each)}&E(a+t)\\
\text{clean}&(M-E)a
\end{array}
\]

even if the zero and one maxima occur in different radix passes. The
source resets their heads at each pass, writes exactly `E` tagged records
in aggregate, and reads only the current returned counts. Old trailing
bytes remain below these historical maxima and the closing scratch scope
zeros the full old extent. Thus all four scratch maxima sum to at most
`V+2Ea+3Et≤3V+3Et`. Adding both the original field and its one actual
replacement yields at most `5V+3Et`. If `t≤a`, this is at most `8V`.

The tag-to-payload condition is **not** true for the generic repair API.
An exact actual-tape counterexample is `L=17`, `z=0`, `component_bytes=1`,
all groups marked bad, and identity correction. Then `a=2`, `t=3`,
`V=262144` bytes, and the dirty role has exactly `655360` bytes, exceeding
`2V=524288`. It still returns the correct payload. With the same field and
`z=1`, `a=4`, `t=2`, and the dirty role has `393216` bytes. These are boundary
controls, not counterexamples to the installed multiplier.

For the actual positive entrance, `t≤a` follows directly from the validated
production header and its caller, without an extra geometric assumption:

1. `band_product.Product` inherits the retained `Product` constructor through
   the pack wrapper. It enforces `b≥5`, `P≥6b`, and `prod(sides)≤2^b`.
   `CRTTree` requires each successful side to satisfy `1<side<2^width`,
   where `width=(side-1).bit_length()`.
2. For every integer `side≥2`, `2^width≤side²`. Multiplying and using the
   constructor's true-product check gives `sum(widths)≤2b`.
3. `spectator_layout.packed_width=sum(widths)-removed_bits`, so a root field
   created by `positive_dispatch.h_pack` has `L≤2b`. That same call sets its
   component size to `machine.wide=(2P+47)//8≥b`, hence `c≥2b`.
4. `complex_stage.entrance` places a slab within that field. `place_and_apply`
   preserves `component_bytes`. Before the cohort runs, `Positive.hadamard`
   increases the component size by `(2·selected+33)//8+1`; the widened working
   field is separately charged. Paid positive children subtract owner bits
   from the ambient dimension; `Arena.child`, `Field.blank` and `replace`
   preserve that widened component size. Therefore every descended repair
   field still has `L≤2b≤c`.
5. For each valid `0≤z≤L`, `t=max(1,ceil((L-z)/8))≤max(1,L)≤2b≤c≤a`.
   The native call actually supplies `z≥bitlength(P+1)²`; the bound above
   does not need that stronger suffix.

This closes the repair byte comparison on the stated production path. The
local generic counterexample shows why an unqualified API-wide statement
or a field-count-only argument would be false. The theorem does not cover
an independently supplied `Field` with an arbitrary smaller component
size. CRT marker routes and their own outer census remain separately
charged; this argument does not certify the outer `2^1024` allowance.

## 6. Evidence and remaining obligation

`evidence/RESULT.json` records the source pins, exact files and checker
outputs. The actual-file tests cover wide ranks two and three, changed
spectator/group extents, 27 genuine highs per low, four serial route/inverse
calls under suspended dirty parents, all scaler sites over digits zero
through seven, both type-route directions and zero-length roles. The
permutation oracle for the isolated unit scaler is independent; quotient
cover enumeration and its arithmetic are inherited from the pinned source.
These traces do not constitute a recursive production-size execution.

Three in-memory source mutations omit radix-bucket erasure, collide the
unit scaler's odd output branches, and truncate dirty data. They are
rejected respectively by a byte-cap overrun, a byte-cap overrun and the
physical dirty-tail check. The repair counterexample plus the one-bit
grouped control distinguish a missing hypothesis from a false generic
statement. Successful actual `Product` headers, rejected invalid headers,
and exact independent integer cases support the production binding.

The next obligation is the remaining source-specific local byte census:
bind the other ordinary roles (especially direct `scale_atom`, root
rectangle/root pad, complete owner banks and all return routes), their
allowed adapter nesting, and the outer CRT/control allocation to the
retained `256`, `32`, `80` and `2^1024` factors. The Gaussian owner-count
theorem, source mass certificate, historical stack lemma and paid movement
argument remain explicit premises. Nothing here alone proves the complete
`297.6n` ceiling or its advertised activation threshold.
