# Independent audit: support-local simultaneous-H supplier

Conclusion: the retained compact phase supplier can be used at width g with cost

    O(V g^(1-q) polylog(p))

without the previously charged additive V p^(1-a), **provided the call is made globally on the complete dyadic tensor, not separately on one fixed coarse-label microbox**. This is conditional on the same accepted finite complex circuit and arbitrary-width equal-chunk interchange as the retained supplier, and on the support-router transfer proved in `work/halo_layout_ultra/SUPPORT-ROUTER.md`. The new support-router's unequal-spacing algebra and its use here have been checked below.

The full address still has O(p) bits. That quantity remains in descriptor arithmetic, keys and error precision; it no longer determines the width of any newly required fast coordinate interchange.

## 1. What the actual phase frames touch

The primary source is `work/integer-mult-current/upstream/build/sections/05-layers.tex`.

At lines 86–139, a residual basis is a matrix M in GL(m,F_2), extended **inside F_2^m**. At width e=mf it is applied separately to the column

    (x_(1,j),...,x_(m,j)), 0<=j<f,

where x_(h,j) is the one selected bit in the jth K-bit chunk of slot h. A frame adapter therefore changes only e selected bits. It is not an arbitrary basis of the full O(p)-bit ambient address. Gaussian elimination gives a fixed number of simultaneous row additions because the finite network's m is fixed.

The compact replacement in `notes/compact-control-movement.tex` lines 38–44 and 143–166 implements each row addition using two front and one back dirty fields of at most (f-1)G bits, G=4 ceil(log2 p)+6. Its at most twelve fast interchanges have width (f-1)G, **not** the full distance between slots and not p. Long intervening fields are spectators. The modular rotations scan them, with polynomial descriptor arithmetic paid separately by complete records.

Residual children in `whole-complex-concatenation.md` use the first r complete fK slots after the same adapter. Their union is already one complete rfK field. The grouped child changes a descriptor; it does not gather a new p-dimensional frame. All remaining slots and the trailing tK field stay complete spectators. `whole-complex-prefix-and-wrapper-qualification.md` supplies a leading row prefix, not an unpriced suffix-to-front transpose.

The source/sink Z masks and inverse-child wrappers in source05 lines 123–175 depend only on selected bits. They are coefficientwise signs/fourth-root phases. Scalar network gates act between fixed role streams at aligned addresses; they do not change the address support.

## 2. Global selected-bit exposure

For one tensor-compiler H call, the selected position in each of the g original long axes lies among its O(log p) local low bits. Choose a K-bit neighborhood starting at that selected position, with common selected offset rho=0. More generally one may retain a common rho after shifting all neighborhood starts accordingly. Because the original axis length ell grows faster than log p, K+O(log p)<ell eventually. The g neighborhoods lie in different original axes and are disjoint.

Let S be these gK actual bit positions. Send them, preserving chunk order and each chunk's internal order, to a consecutive destination set T of gK slots. The explicit extension

    S -> T as prescribed,
    T\S -> S\T bijectively,
    identity outside S union T

is a coordinate permutation supported on at most 2gK positions. Its inverse restores the original coarse-coordinate interpretation. The target can be chosen before the payload and a reserved untouched suffix. No stable reordering of every coarse field is required.

Apply the H supplier to this full global stream, whose complete coarse-coordinate ranges remain present. A fixed coarse-label microbox alone does **not** contain enough complete K-bit fields: its high coarse bits are fixed. Borrowing those fixed labels inside such a microbox would violate the supplier's complete-field hypothesis. This audit approves the global call only.

The tensor compiler's H schedule is independent of all coarse labels. Those labels affect only diagonal coefficients between complete H calls. The diagonal scan can still be organized by coarse-label microboxes after undoing the global exposure permutation. Coarse-dependent coefficients therefore do not require separate supplier invocations.

## 3. Deferred reservoirs and the row prefix

At a phase with h unprocessed selected bits, reserve whole K-bit chunks for two front hG fields, one back hG field, and a leading row prefix. With K=128G, the field reservation is at most 3h/128+O(1) chunks. Row preparation needs O(log h) further chunks, including the product stock for nested bit and complex calls. For h above a fixed polylog(p) threshold the total R(h) is at most h/16. The remaining bounded/polylogarithmic h can be processed individually.

Every such chunk is one of the current selected chunks. The phase applies C only to the other h-R(h) selected bits and identity to the reserved chunks; the latter are deferred to the next phase.

This requires one explicit modification to the original exposition: **do not first apply C to the reserved row/front/back selected bits**. That preliminary work in the old all-axis construction only ensured those selected bits were eventually covered. It is not needed to create rows or complete temporary fields. Source `compact-control-layout.tex` lines 30–62 proves that the active invocation is the required C tensor separately on every row and identity on all reserved/spectator coordinates, for arbitrary incoming payloads. Hence dirty, unprocessed reserved selected bits are valid.

The leading q0 complete chunks have cardinality 2^(q0 K). Choose q0 from the actual product row stock Q_rows=W_complex^D_complex W_bit^D_bit. This preserves the accepted nesting contract; replacing the product by a maximum would be incorrect. Pad the leading row count to a multiple of Q_rows once for this phase, by adding whole rows. The factor is below two. All descendants inherit the same complete within-row fields and the same row stock; no new independent bit coordinates are allocated.

A completed active invocation is identity on the row label and every temporary coordinate. Each padded zero row is therefore zero at completion and can be deleted. Delete padding and restore the exposure layout **before the next deferred phase**. Consequently row padding does not multiply by 2 at every phase or tensor axis.

The next deferred phase gathers only its h'=R(h) remaining neighborhoods. A gather/restore can again be extended with support at most 2h'K; it may move previously processed coordinates temporarily but fixes them after the inverse placement. Their values need not be recomputed. There is no need to move all p coordinates back into a stable global axis order.

## 4. The logarithmic K choice is legal after tightening the statement

The original compact-control proposition states the sufficient asymptotic condition K/log p -> infinity. K=128G does not satisfy that literal condition. The source proof, however, uses it only at lines 149–154 to obtain

    K >= G+4 ceil(log2 p)+10,
    delta_bad <= 5/(128p^3).

K=128G satisfies the displayed finite inequality directly. The earlier/later-source guard proof, complete-field layout, row stock, scalar gates and semantic guard have no other use of K/log p -> infinity. Thus the transfer must cite the tightened finite guard hypothesis; it must not claim that the new K satisfies the old stronger asymptotic wording.

With this change, all compact interchanges retain width O(h log p), and the per-node movement overhead is O(V_node h^(1-a) polylog(p)). Here h is the current selected width, not the ambient number d of original Gaussian axes. The supplier's stopping threshold and branching analysis likewise use its own top width g; global p remains only in logarithmic guards and O(p)-bit descriptors.

## 5. Check of the support-router extension

The original arbitrary-source router colors active targets by their current location modulo K. Targets in one color have disjoint K-bit guards. The new router stores only the r active control digits, H=rG, even when the target spacings are unequal multiples of K.

The four-update proof depends solely on disjointness of the guard intervals: on a good address the first y update adds 2zt within a guard, the t update adds its old low bit e without carry, and the second y update adds z(1-2(t+e)). Their net is z(1-2e), changing exactly the selected low bit. The final t update restores t. Nothing uses equality between successive target gaps. A complete F therefore fixes every nontarget source bit, even inside another guard. F; load u from the sources; F; unload implements the desired simultaneous XOR for sources outside the target set.

All rotations remain globally bijective, because their controls precede the target after the prescribed back-field shuttle. Their current-control inverse is used on bad addresses. The ideal selected-bit XOR preserves the guard/control bad predicate, so the old sparse repair applies unchanged. Its O(p)-bit keys and polynomial per-record arithmetic remain explicit; they are not replaced by a unit-cost sort.

For a permutation moving k positions, factor it into two involutions and three XOR stages per matching. Three disjoint 3kG-bit reservoirs can be chosen when n>=9kG; the three matching cohorts avoid the respective reservoirs. Each target residue class then uses width at most kG in each control field, rather than ceil(n/K)G. Original equal-width interchanges place and restore the fields. This gives O(V k^(1-a) polylog p), plus descriptor setup.

When records are short, choose only ell_s=ceil(log2 p)^2 untouched binary bits, not a whole long original axis. Here is explicit noncircular suffix bookkeeping. For a requested permutation pi with moved support at most k, if n>2(k+1)ell_s, a gap in its support contains a consecutive ell_s-bit field S disjoint from the actual last ell_s bits. Use one original equal-ell_s interchange A to move S to the actual suffix. Route the conjugate A pi A^-1 on the n-ell_s prefix only, then undo A. The conjugate fixes that suffix pointwise because pi fixed S. Choose all control reservoirs inside the prefix, after this interchange, and recompute positions and residue classes after their placements. Thus no control operation touches the grouped suffix. Grouping its 2^ell_s complete values into a record preserves the data volume and gives a superpolynomial record length. If n<=2(k+1)ell_s, the retained full-span bound is already O(V(k+1)^(1-a) polylog p), so no suffix grouping is needed for this support bound. The placement costs O(V polylog p), not V ell^(1-a) for the original long axis length ell.

For the calls here, k=O(hK)=O(h log p), and n/(k log p) tends to infinity because g=p^beta with beta<1 while n is of order p in the retained full tensor. If this inequality fails in a small regime, n=O(k polylog p), so the retained full-span bound is already O(V k^(1-a) polylog p). The support theorem's own temporary reservoirs may have O(kG) bits; this is a polylogarithmic enlargement of support, already priced in the same bound.

## 6. Complete charge table

| Operation | Active coordinate/data support | Charge |
| --- | --- | --- |
| Initial and inverse neighborhood exposure | At most 2gK moved bit positions | O(V g^(1-a) polylog p) |
| Deferred phase exposure at width h | At most 2hK positions | O(V h^(1-a) polylog p) |
| Fixed binary residual adapter | h selected bits; compact controls O(hG) | O(V_node h^(1-a) polylog p) |
| Control-field shuttle | At most O(hG)-bit chunks | Original O(V_node(hG)^(1-a)) |
| Modular rotations and exceptional repair | Full scan; O(p)-bit descriptors/keys | O(V_node) after record grouping |
| Residual child concatenation | Existing contiguous first-r slots | Descriptor change only |
| Source/sink/inverse phases | Selected-bit masks and coefficients | O(V_node) |
| Scalar role gates, parking and restoration | Fixed role streams at aligned addresses | O(V_node) |
| Whole-row padding and deletion | One current-phase row prefix | O(V), factor below two, removed before next phase |

No row in this table requires an interchange of width p.

Let tau=1-a. The retained stopped branching argument gives O(V h^(1-q) polylog p) for each phase, with q<a and the same strict complex/leaf margin as the retained supplier. Since h_(j+1)<=h_j/16 above the polylogarithmic tail,

    sum_j h_j^(1-q)=O(g^(1-q)),
    sum_j h_j^tau=O(g^tau)<=O(g^(1-q)).

Therefore the entire selected-bit call, including support-local exposure/restoration, costs O(V g^(1-q) polylog p). The old V p^(1-a) term was the full-span exposure estimate. It is not needed for this support-local call family.

For the T74 specialization, "stopped branching" specifically means the mixed
weighted-tree argument in `notes/endpoint-gauge-complex.tex` (the rows/stopping
paragraph) and `notes/batched-complex-rows.tex`. Its children have unequal
widths `r floor(e/73)`, with weights `H_r/66304`. The uniform `e/73` tree cited
in some historical compact-control notes does not by itself justify using
the mixed moment endpoint. The mixed proof bounds weighted widths by depth,
not by assuming equal leaf depth; see
`review20261014/REVIEW-RESPONSE.md` for its explicit derivation.

The actual T74 stock is 2644 bits and its row coefficient is 19545, below the
retained 20161 allowance. The row reservation must use the complete
depth-dependent product stock. A conservative bound is
`R(h)<=3h/128+O(log(h+1)+loglog(p+2))<=h/16` above a fixed polylogarithmic
tail. A one-row-chunk estimate is not valid for this supplier. Processing
that tail individually adds only polylogarithmic work per group. No power
of g or p is changed by these fixed supplier-dependent constants.

## 7. Precision, normalization and validity boundary

The compact address operations only permute coefficient encodings. Their temporary binary combinations are address-control arithmetic, not coefficient values. The accepted whole-child semantic guard remains linear in selected width. Completed deferred phases act on disjoint selected bits, and the sum of their widths is g; only one current phase contributes unfinished internal excess. Thus its arithmetic guard is O(g), independently of the total address width and of the number of coarse labels.

The retained target is H0=(1/2)[[1,1],[1,-1]], while `TENSOR-COMPILER.md` uses the raw matrix H. Follow a supplied H0 tensor by the scalar 2^g. This is an O(V) binary shift/diagonal, with O(g) extra magnitude and error allowance. Repeated compiler calls and local/coarse-dependent diagonal factors retain the already proved total guard O(g ad+g polylog p), which is O(p) at the proposed strict parameters.

The positive conclusion is restricted to a globally complete dyadic stream, selected positions admitting the complete K neighborhoods, the retained exact common-frame/whole-child contract, and support-router calls using the original paid equal-chunk primitive. It does not approve per-coarse-microbox borrowing, stable compaction of every coarse axis, arbitrary computed-key full sorting, a maximum-only row stock, or reuse of the unmodified K/log p hypothesis.

## 8. Large groups do not have to fit inside one original axis

Let the ambient axis count be d=Theta(p^epsilon), with any fixed epsilon<1, and let each original binary axis have length ell=Theta(p^(1-epsilon)). The support argument permits

    g=Theta(p^beta),        0<beta<epsilon, beta<1.

It does **not** require beta<1-epsilon, g<ell, or gG<=ell.

Only one K-bit neighborhood per selected original axis must fit inside that axis. This is K+O(log p)<ell, true eventually because K=Theta(log p) and epsilon<1. The total neighborhoods have gK=O(p^beta log p) bit positions. The support router's temporary reservoirs have O(gKG)=O(p^beta log^2 p) positions, which fit the full Theta(p)-bit binary tensor whenever beta<1. An untouched log^2 p-bit suffix reservoir can be chosen outside this support.

The compact front/back controls are made by concatenating **multiple complete neighborhoods**. This is explicit in the primary layout: q_F=ceil(2H/K) and q_B=ceil(H/K) entire chunks supply the two front H-bit fields and one back H-bit field, respectively. With H=hG and K=128G, the complete-chunk cost is at most ceil(3h/128)+O(1). The row stock adds O(log(hG)) chunks. Consequently

    R(h) <= 3h/128 + O(log(hG)+1) <= h/16

above a polylogarithmic threshold. No step asks a single original axis to contain H=hG controls. Grouping these chunks changes their placement, not the number of full binary coordinates available. This removes the former beta<1-epsilon reservation restriction from the H supplier interface; independent Gaussian-gauge constraints may still impose their own relation between beta and an interior-length exponent.


## 9. Independent bookkeeping audit

`SUPPORT-ADVERSARIAL-AUDIT.md` independently checks the pre-reserved uniform
control width, post-placement target coloring, global complete-field use,
row restoration, and suffix conjugation above. Its suffix clarification
makes the existing short-record argument explicit without changing the
cost or imposing any new relation between g and one original axis length.
The primary/source coverage and hashes are recorded in
`SUPPLIER-AUDIT-SOURCES.json`; `SUPPLIER-CAPACITY-CONTROLS.json` is an exact
integer control in a regime where gG exceeds the entire single-axis width.
