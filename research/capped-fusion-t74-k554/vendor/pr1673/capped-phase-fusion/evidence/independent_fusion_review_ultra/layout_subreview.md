# Independent layout and halo subreview

Scope: read-only adversarial review of the geometry, sparse stream layout,
ordered q embeddings, local-table/global-H scheduling, and halo copying in
`work/phase_assembly_ultra/phase_fusion_note.tex` (especially lines 203–283
and 368–385). The Gaussian error/conditioning and boundary-solve stability
arguments are outside this subreview and remain with the parent reviewer.
The advertised PASS labels were not used as premises.

**Result: no blocking layout or copying gap found.** This conclusion retains
the explicitly stated paid equal-chunk/support-router and completed supplier
endpoint contracts; it is not an independent proof of those upstream
computational primitives.

## Issues tested independently

1. **Capping does not lose separator width or create long Schur edges.**
   The carving of note lines 205–211 and
   `phase_layout_audit_ultra/CAPPED-SIGNOFF.md:7–21` leaves at least W
   coordinates between successive eliminated intervals. Eliminating a
   band-W interval touches only the two neighboring boundary bands; in
   boundary order these have total O(W) extent. The O(d/B + log B)
   interval count gives O(W(d/B+log B)) boundary coordinates per cell.
   Since B<d and original cells have Theta(d) length, summing across an
   L-core gives O(LW/B polylog p + W polylog p), not an unpaid scan per
   capped block. The dyadic tail does not require a block larger than B.

2. **The union is used only when it is invariant.**
   In note lines 242–251 and `AUDIT.md:37–66`, E_i contains all nonidentity
   support of every sparse axis factor. Therefore a sparse axis operation
   can change x_i only between two members of E_i. If a point belongs to U
   because of a different coordinate, changing x_i preserves that fact.
   This proves closure without requiring sparse inverse bandwidth.
   A dense A stage is correctly excluded; scattering and regathering
   between the two sparse windows avoids the obvious closure
   counterexample.

3. **No full-key sort is needed for union work.**
   `U_i = E_i x [L]^(g-1)` is wholly present, with every needed RHS, and a
   subsequence of the lexicographic U stream is still in rectangle order.
   An increasing E_i rank counter resets at each outer prefix, with the
   suffix repeated inside each rank. It does not require random rank
   access. Renaming produces the mixed-radix rectangle [P] x [|E_i|] x [S].
   The explicit fixed-tape primitive in
   `integer-mult-current/references/semantic-bulk/rad20/reports/bulk-resampling-tape-transfer.md:21–46`
   moves a polynomial-size field across arbitrary spectators in
   O(volume log p), including temporary padding of only that field.
   After inverse movement the new stream has its original order, so a
   sequential merge replaces exactly U_i. Scanning U once per axis costs
   O(V g^2 W/B polylog p) per group, and O(V d g W/B polylog p) in total.
   The independent child review is in `union_subreview.md`.

4. **RHS batching does not introduce a hidden large transpose.**
   All other complete inner fields provide R>=L^(g-1) RHS records. After
   exposing E_i, the layout is [R_hi] x [q] x [row] for dyadic q in [W,2W).
   Moving the polynomial-size q/row field yields
   [R_hi] x [row] x [q] at the same O(volume log p) cost. A final incomplete
   batch has constant padding overhead. A W-square factor page per batch
   has volume O(W^2), hence O(z R) total for z boundary rows, below
   O(z R W^(omega-2)) arithmetic. This supports note lines 233–240;
   numerical stability of these products/solves was not re-proved here.

5. **The q scan is genuinely monotone.**
   For q_j=floor(tj/s+1/2), image membership is exactly
   s(2k-1)<=2tj<s(2k+1), and the least candidate j is the ceiling displayed
   in note lines 256–260. This handles the half-integer convention. Taking
   a Cartesian product preserves lexicographic order, so zero insertion
   or image extraction consumes the next record without a lookup. The
   ordering at lines 262 and `MATRIX-LAYOUT-SIGNOFF.md:47–59` is essential
   and correct: embeddings precede the global low-bit gather; extractions
   follow its inverse. Each intermediate volume is bounded by T/S<2.

6. **Local tables coexist with global completed H calls.**
   `inplace_algebra_ultra/TENSOR-COMPILER.md:64–97` makes the selected bit
   at each stage common across all local circuits; only diagonal tables
   depend on the coarse label. A completed supplier H call is H on those
   selected low bits and identity on every other bit, by the retained
   endpoint contract (`SUPPLIER-SUPPORT-AUDIT.md:27–41`). Consequently the
   call preserves every coarse-label subspace even though its internals
   borrow complete coarse fields. Undo the exposure before applying the
   next diagonal page. The diagonal odometer/page-return bound is an
   actual geometric sum (`TENSOR-COMPILER.md:112–132`), so visiting g
   tables does not cost g per data record.

   After the global low-bit gather, an original K-bit neighborhood may no
   longer be physically contiguous. Use its image under that known gather
   permutation as the selected support: disjointness and completeness are
   unchanged, and the arbitrary-spacing support router exposes its O(gK)
   coordinates. Restoring that exposure restores the local-table order.
   This is a coordinate relabeling, not an additional long-axis gather or
   an assumption that fixed coarse labels are complete inside one local
   microbox.

7. **Position dependence does not break the halo copying argument.**
   `HALO-THEOREM.md:88–125` partitions the output complement by first
   exceptional axis and side. The required input boxes have lengths L in
   preceding axes, 3A in the face axis, and L+2A in later axes. Thus the
   total input traffic is exactly
   3V[(1+2A/L)^g-1]=O(VgA/L), including corner duplication. This part uses
   interval geometry only, not a translation-invariant kernel. The note
   correctly uses only that part at lines 266–271 and then supplies actual
   position-dependent one-axis maps on the copied boxes. Early cropping
   is valid for tensor products of those restricted maps; the unprocessed
   fields retain their original halos. Accuracy of the restricted inverse
   maps is a separate analytic obligation, not established by copying.

   Sparse keys have K=O(g log s) bits. Even a conservative K^2 metadata
   cost per copied record, plus K radix passes and g sequential local
   passes, is lower order with A/L=O(p^-5). This remains true for the
   matrix-corollary beta near 1/4. The full-key union sort that would be
   too costly is absent from the rectangle algorithm, whereas the halo
   sort is paid on the genuinely sparse copy volume.

8. **The matrix-corollary parameter change preserves these arguments.**
   The substantive geometry inequalities are xi>1/2, xi<epsilon,
   beta+1/2-xi<0, and beta+2(1-epsilon)<1. The quoted values in note
   lines 355–372 satisfy them. Neither the rectangle proof nor the
   short-field transpose requires g to fit inside one original axis.
   Only each selected neighborhood must fit; total support is spread
   across the globally complete rectangle.

## Independent finite controls

Executed without calling any candidate script's output-writing main:

- Exhaustive q-image membership/inverse check for 2,144 pairs with
  1<=s<=64 and s<=t<=2s, including tie cases.
- 1,831 cap/endpoint partitions with W=1..4 and B in {8,16,32,64}, plus
  band-fill checks at endpoint and full-block transition examples.
- A separate three-axis position-dependent signed band-map check on a
  16^3 tensor, with core side 8 and radius 1. It tested 2,368 corrected
  outputs from 11,712 copied input records against the direct tensor map.
  This extends the candidate's translation-invariant finite examples in
  precisely the geometry-only direction used by the note.

All passed. The checks are corroboration; the all-size reasoning above
does not follow merely from these finite runs.

## Nonblocking evidence limitation

`phase_layout_audit_ultra/check_union.py:54–85` uses dictionaries instead
of simulating tape ranks, nondyadic field padding, or RHS batching. It also
gathers/scatters C and S^-1 separately while its metadata describes sharing
one window. Thus that script alone is not evidence for the claimed stream
implementation or exact two-window reuse. The explicit tape primitive and
invariance proof supply what the test omits; separate extra gathers would
in any event alter a constant, not the exponent. No blocking finding is
assigned for this test-coverage limitation.
