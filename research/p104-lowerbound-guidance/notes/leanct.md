# LEANCT (Nov 20): THEOREM CT in Lean -- lean/decoder-duality/Nov15/CarrierTree.lean
Kernel-only; imports Nov15.FutureAttr (and PriceLemma through it). Built via runlean.sh; olean at .lake/build/lib/lean/Nov15/CarrierTree.olean.
Axioms of every headline: [propext, Classical.choice, Quot.sound].

## What landed
- `ARun0 P X s0` : FutureAttr's ARun minus `hcold` (and without xs/ys/Fy/q, which only hcold used). GTD (`hgtd`) kept.
  CHANGE vs FutureAttr: a read of an owned register e by ANY d (public OR owned) sets `B e := B e ⊔ ch e` and `dep e := true`
  (FutureAttr only counts reads into publics). This is SP.md's "GTD w.r.t. read-outs (reads of it by anything)" and is needed so that
  a carrier read only by an owned register has B = its read chart (else A_{p(k)} ⊆ B_k fails on FLUSHROW's own witness).
- `InvS` (i1 identity, charts, i3/i3b GTD, i4 weights on B, i6 `dim(A⊔B⊔ch) ≤ dim A + lc`, closed rows `Ok0`, cost) + `invS_of_run`
  (proof ported from Inv.*, i5 dropped, B/dep rule changed; simpler because d ≠ e kills a case).
- `Fo` forests (`leaf | node k children siblings`), `labels/roots/nonroots`, `asub` (meet of A over a forest), `wf` (A_k ≤ B_c for roots c of k's children),
  `lcSum`, `cold` (each root's eff content cold at A_k ⊓ asub children).
- `row_step`, `forest_bound` (the S(k) induction, additive form: dim Z ≤ dim(Z ⊓ asub f) + Σlc for any Z inside every root's B),
  `price_le_star` (price ≤ dim B − dim(B ⊓ A*)), `price_sum_le` (Σ root prices ≤ Σ lc).
- `ident0` (decoder identity from ALL lifetimes, no coldness), `carrier_tree_decoder` (CT), `mass_le_R_ct`, `R_ge_of_wall_ct` (Wall N explicit, as in FutureAttr).
- Non-vacuity `Toy2.toy_witness`: FLUSHROW's pinned hot-carry run (1 port, q=1, regs X,Y,H public; O, O' owned; 8 moves). O has a HOT intake
  (A=⊤, eff content 1, a=1 odd), so it is outside class F; forest `node O (node O' leaf leaf) leaf`, A* = ⊥, price 1 = cost 1; `mass ≤ 1` via mass_le_R_ct.

## Gaps / sharpenings against SP.md (report)
1. B/dep rule (above): CT needs owned->owned reads to count as outputs. With FutureAttr's public-only B the attach hypothesis fails for the witness.
   Side effect: an owned register read by another owned register cannot take a later intake (stricter GTD). SP's "GTD wrt all read-outs" says this; flag it for the PR text.
2. Forest vs parent map: Lean encodes the acyclic parent map as an explicit forest over the multiset of lifetimes (Perm to finalRows). Equivalent, but "acyclic p" in SP
   hides that duplicates/identical rows are matched by multiplicity; no loss.
3. SP states roots = nonzero-weight lifetimes. Lean is more general: any forest whose NON-roots have weight 0; zero-weight roots are allowed (they price 0).
4. The final-data hypotheses (hfx hfy hfyX hbal, hXinj, h0, hq, publics never descend, no public INIT) are exactly those of attribution_decoder; CT does not remove them.
5. Cost bound is used only in the form dim(A⊔B) ≤ dim A + lc per lifetime (from i6); the tree adds the single hypothesis A_{p(k)} ≤ B_k. hcold is replaced by cold-at-A*.
6. Not done: shared carriers (SP §3a), multi-epoch (3b), CT-COVER (3c): they are hypotheses-level, not formalised.

## Status
Built clean (rc=0, ~11 s, ~2.1 GB, 844 lines); all #print axioms = [propext, Classical.choice, Quot.sound]. Scratch file removed. Toy facts (evaluated by simp on the 8-move run) all discharged; no sorry.
