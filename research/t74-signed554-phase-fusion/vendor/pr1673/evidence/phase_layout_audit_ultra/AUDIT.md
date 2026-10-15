# Grouped phase-cell layout audit

The sparse-union layout in `REFINED-PHASE-FUSION.md` has a constructive
implementation with its stated `V g^2 W polylog(p)/d` per-group movement
budget. It does not require sorting the full tensor or retaining d full
payload scans. The conclusion is conditional on the separately supplied
dense local tensor compiler, rounded phase-cell factorization, and precision
bounds. This audit does not prove those algebraic/analytic inputs.

The maximum physical bandwidth **W**, including the broad forward map, must
be used in the dyadic carving and support sets below. The narrower inverse
bandwidth alone is insufficient for the broad map. The phase-assembly
branch confirms this convention.

## Exact operator order and the union that is actually invariant

Write H in interior/boundary order as `[A B; C D]` and let
`S=D-C A^-1 B`. The displayed identity in the parent note is correct. In
execution order its inverse can be scheduled as

```
diag(A^-1,I)
[I 0; -C I]
diag(I,S^-1)
diag(A,I)
[I -B; 0 I]
diag(A^-1,I).
```

The middle two diagonal factors commute. Thus there are three dense
interior stages and two sparse windows: the C and S^-1 stages share one
window; B uses the second window. For H itself, reverse and invert this
sequence: the same original B,C and S occur, with signs reversed and dense
A/A^-1 interchanged. No dense A^-1 B or C A^-1 shear is smuggled into the
sparse boundary cost.

For each active axis i, let J_i be its designated boundary coordinates.
Let E_i contain J_i and every interior coordinate incident to an original
nonzero entry of B_i or C_i. Original physical bandwidth W implies that E_i
lies within O(W) of the carved endpoints. Include physical-period cuts,
artificial phase cuts and clipped microbox endpoints. Dyadic carving gives

```
|E_i| <= C (L/d+1) W log d,
mu := max_i |E_i|/L = O(W log d/d + W log d/L)
```

inside a length-L microbox. All sparse factors have the block form
`T_i = I_(E_i^c) direct_sum T_i|E_i`. In particular S_i^-1 can be dense on
J_i: J_i is already included in E_i. Let

```
U = {x in [L]^g : some x_i belongs to E_i}.
```

Then `|U|/L^g <= g mu`. Every sparse tensor-axis operation preserves U and
its complement. If x_i is changed by a nonzero off-diagonal entry, both
its old and new coordinates belong to E_i; otherwise it is unchanged.
This proves closure for an arbitrarily long sequence of these sparse
operations, not just one application.

Dense A or A^-1 is **not** covered. It can move a near-boundary interior
coordinate into the deep interior. Scatter U before a dense stage and
regather afterwards. `check_union.py` includes an exact example in which
dense A^-1 sends union-supported data outside U. The actual schedule above
therefore uses two union gathers, not one retained union for all six stages.

## Complete rectangles inside the union: no missing-zero assumption

For one sparse axis i define

```
U_i = {x : x_i in E_i} = E_i x [L]^(g-1).
```

This is a **complete rectangle**, and it is wholly present in U regardless
of which other coordinates are near a boundary. All nonidentity data needed
by T_i is in U_i. A line with every other coordinate outside its own E_j
still has every E_i coordinate present. A line with another boundary
coordinate may contain more data, but those extra E_i^c entries are identity
coordinates and need no boundary computation.

Keep a copy of U in its original microbox lexicographic order, with a short
coordinate/membership header. For each axis i:

1. Scan U once and copy records with x_i in E_i to an auxiliary stream.
   The copied stream is lexicographic E_i x [L]^(g-1).
2. Rename the increasing E_i coordinates by their ordinal 0,...,|E_i|-1.
   This is a stream counter; no rank/select query is needed.
3. Expose that one field at the line suffix using the retained small-field
   transpose. Its length is at most L=poly(p), so only O(log p) binary
   block moves are needed. Pad only this field to its next power of two
   temporarily, at a factor below two, and remove that padding before the
   next axis. The other fields may be arbitrary spectators.
4. Apply the original B/C or boundary S/S^-1 factor on its complete E_i
   line, retaining identity coordinates E_i\J_i when appropriate.
5. Undo the transpose at the actual field length. Merge the ordered E_i
   stream back into a fresh copy of U, replacing exactly those entries.

No array is completed by invented zero coordinates. The finite checker
verifies the extracted rectangle cardinality and the full tensor result.

The extraction/merge costs O(|U|) per axis. Transposition costs
O(|U_i| polylog p). Consequently one sparse window costs

```
O(V [g^2 mu + g mu polylog p])
 = O(V g^2 W polylog p/d) + O(V g^2 W polylog p/L).
```

There is no factor `K=g log s` from a computed-key sort in this part of the
algorithm. A more general radix implementation would still fit with extra
small powers of g, but the complete-rectangle construction avoids it.

## Union extraction and piece catalogues

Only one full microbox scan is needed to form U, and one to scatter it.
For every complete p-bit coefficient record, compute its g membership flags
from its coordinate tuple and OR them. The flags and coordinate header have
O(g log L) bits. A nonzero number of flags sends the whole record once to U;
it is not duplicated for each active axis.

This is a charged descriptor calculation. For actual source periods of
bitlength h=Theta(p/d), q_j inversion and phase-cell endpoint calculations
use O(h^2 polylog p) elementary bit operations per axis. Within a phase
cell, the greedy dyadic carve is found by at most O(log d) halvings and
integer comparisons. Thus a conservative membership cost is
`O(g h^2 polylog p)` per record, which is o(p) for
`g=p^(1-epsilon-r-zeta)` and epsilon>2/3. At the proposed epsilon this has
power about 0.005. It is absorbed by reading the p-bit record once.
Alternatively the original remainder phase generator and an odometer give
the same membership flags in sequential coordinate order.

Factor pages may be regenerated once per complete microbox/group from its
actual coarse origins, using the supplied polynomial-time coefficient
generation. The complete inner microbox and untouched spectator payload
are superpolynomial in p and amortize this polynomial setup. This avoids
random access to a global catalogue in the scrambled coarse order created
by a support-limited gather. Online row/factor pages are then visited in
the ordered extracted E_i line. All page rewinds are within that line or
RHS batch and are included in the corresponding boundary arithmetic.

## Batched right-hand sides do not add a large transpose

All other inner coordinates and following tensor axes are independent
right-hand sides for an axis operation. Their count R is superpolynomial.
Batch them in a dyadic width between W and 2W; the final incomplete batch
can be padded once at constant cost. To put the batch index outside the
boundary-row field, move only that polynomial-width row field. This costs
O(log p) times the boundary volume, not a transpose of the long spectator
field. Each W-by-W factor page is scanned once per RHS batch and reused in
the block product. Reverse the small-field layout after the solve.

Thus the assumed Strassen `W^omega` per W RHS gives the quoted total
`O(V W^(omega-1) polylog p)` boundary arithmetic. This audit checks the
layout and factor reuse; stability and the no-pivot factor theorem remain
the phase-assembly branch's responsibility.

## q_j embeddings, selections and source order need one group scan

For a group, each coordinate map `j -> q_j=floor(tj/s+1/2)` is increasing
and injective. Its tensor product preserves lexicographic order on its
image. Enumerate the target-group rectangle once. At target coordinate k,
set

```
j=max(0,ceil(s(2k-1)/(2t))).
```

The coordinate belongs to the image iff `j<s` and `2tj<s(2k+1)`. These
inequalities include half-integer tie behavior exactly. If every group
coordinate belongs to its image, consume the next source record; otherwise
write zero. No source permutation or lookup occurs. A final extraction
copies only image records and restores the original increasing source
order by the same tensor monotonicity.

The g membership tests cost O(g h^2 polylog p)=o(p) per p-bit record.
Partial tensor volumes remain bounded by the retained total T/S<2. These
are one full scan per group, not one per axis. Earlier processed groups
and later unprocessed source axes are arbitrary prefix/suffix spectators.

For the square narrow operator, `Haug=EHC+(I-EC)` is permutation-similar to
`H direct_sum I`. Its inverse is `E H^-1 C+(I-EC)`. Holes are identity
coordinates, and selected rows recover precisely the original inverse.
Physical target bandwidth is at most twice the source bandwidth plus two.
The final normalization/zero-hole selection can be fused into the same
ordered output scan. Any separable diagonal is evaluated by one grouped
scan with bounded prefix products, not g scans of the whole payload.

## Microbox halos stay on a separately sparse path

Keep the retained dyadic target core side `L~p^8`. Do not make the dense
tensor compiler act on `(L+2A)^g` or pad that shape to `(2L)^g`.

On the dense core path, compute the exact principal restriction of the same
rounded square target-grid operator. Keep only outputs farther than a
fixed multiple of `A~p^3` from every artificial core edge. The phase-assembly
branch supplies the principal-window locality comparison for these outputs.
For narrow compression, q_j spacing at most two converts this target margin
to the required original-source distance. The remaining output set has
fraction O(gA/L).

Use the source-driven first-boundary-axis rectangles from
`work/halo_layout_ultra/HALO-THEOREM.md`, with radius a sufficiently large
constant times A. This movement lemma does not need translation-invariant
coefficients: it only copies the actual input windows. On this sparse path
apply the already retained local principal-window inverse or broad forward
map in each axis, using their original coefficients, true-period cuts and
one-field temporary mixed-radix padding. Early cropping is justified by the
tensor product of the restricted one-axis maps, as in the retained microbox
proof; no halo refresh is needed.

The sparse-copy volume is O(VgA/L). Actual keys use O(g log s) bits, and all
key passes are paid. The old per-axis local solver has per-record work
`polylog(p) p^delta (1+W^2/d)` plus boundary terms, with fixed small delta;
g sequential such passes on this sparse volume are negligible because
A/L=O(p^-5). Polynomial setup per complete rectangle is amortized by its
superpolynomial spectator/inner volume. An unspecified arbitrarily high
per-record polynomial is not being declared free.

## Ledger and remaining dependencies

There are a constant number of scans and sparse windows per group, plus
polylogarithmically many dense circuit rounds. Across d/g groups the layout
costs are

```
group scans:        O(V d/g polylog p),
union movement:     O(V g W polylog p),
boundary arithmetic: O(V W^(omega-1) polylog p),
microedge corrections: lower order by the p^-5 volume factor.
```

Dense tensor compilation and its support-limited group routing remain
`O(V d/g^q polylog p)` and `O(V d/g^a_bit polylog p)`. This audit leaves no
necessary Vd payload scan for q_j placement, normalization, union handling,
microhalo creation or corrected source order.

It does not establish that the proposed dense A/A^-1 circuits represent
both actual Gaussian operators with the claimed O(p) conditioning, nor that
the assembled rounded resampler has the final required error. Those must
be supplied by the other branches before any exponent is promoted.
