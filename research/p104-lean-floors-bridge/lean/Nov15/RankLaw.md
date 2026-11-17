# RankLaw.lean: REBUILD-CORE's RANK law (RESULT §7, ROUNDLOG CORE r2). No sorry, ~7 s, 2.2 GB RSS
Lane LEAN-NEXT9, Nov 16. Source: cards/WILD/REBUILDKIT/RESULT.md §7 and the CORE r2 line in ROUNDLOG.md.
Axioms: [propext, Classical.choice, Quot.sound].

Build (imports the TokenCancel olean):
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean -o .lake/build/lib/lean/Nov15/RankLaw.olean Nov15/RankLaw.lean

**Model.** TokenCancel's op model and legality (born/init/move/add/scale/clear/copy, co-presence; z, V arbitrary).
- Tokens = registers present at the start plus births so far (`tokRun`). Token span `TS T` = span of the e_r, r ∈ T, with `finrank_TS` = |T|.
- `Good`: absent registers have row 0 and tokens are present. `start l` (own coordinate if present, 0 if absent) satisfies `Good`, and its rows span its tokens (`start_good`, `start_span`).
- `Lossy s e`: a CLEAR of i, or a COPY into i from j ≠ i, while row i ∉ span(other rows) at that instant. `Loss` = some lossy event in the run. `NZ`: SCALE factor ≠ 0.

**The V-mix target (a linear system).** `VMixM X R` := ∃ C, det C a unit, C·X = R. X = end rows of the V-enders G1 after a run with the V-hub ops deleted, R = their targets.
- `vmixM_iff_span`: solvable iff rowspan X = rowspan R. Built on `exists_equiv_comp`: two maps with equal range differ by an automorphism.
- `vmix_ops`: every such C is a product transvections · diag(D) · transvections with all D ≠ 0, i.e. V-hub ADDs and nonzero SCALEs (Mathlib Pivot).
- `vmixM_indep`: independent targets imply independent end rows. `vmixM_unique`: independent end rows make C unique.

**Only CLEAR (and COPY) lose rank.**
- `add_inverse` and `scale_inverse` (u ≠ 0): the inverse op restores the state exactly.
- `Sp_step_le`: no non-birth op enlarges the row span.
- `rank_step`, `rank_run`: (row rank) + (slack) never exceeds |tokens|, and a lossy step costs one unit for good.
- `span_run`: with no loss, end row span = token span.
- `full_rank_iff_noloss`: end row span = token span ⟺ no lossy CLEAR/COPY.

**`rank_law` (the iff).** Assume:
- a legal run with NZ, from a state whose rows span its tokens;
- non-V registers already end on their targets (`hNon`);
- the target end state spans the final tokens (`hTgt`; true when the target is the end of any loss-free legal word with the same births, by `span_run`);
- U ⊇ V targets (`hRU`), and U ∩ span(non-V targets) = 0 (`hUN`).

Then: V mix exists ⟺ (i) no lossy CLEAR/COPY and (ii) every V-ender end row ∈ U.

**Token order** (`vmixM_fill` + the shape of `rank_law`).
- Neither existence statement has an order hypothesis, so correctness never depends on the LATE order.
- An order b only shapes C: if X = T·R with T block-triangular for b and invertible, then the V mix C = T⁻¹ is block-triangular. No fill outside the triangle.

**Findings (prose statements false or underspecified as written).**
1. **"Every op except CLEAR is invertible" is false with COPY.** `copy_lossy_example` (over ℚ, 2 registers): COPY 0←1 is lossy.
   - Also SCALE by 0 is a CLEAR.
   - Minimal fix: "every op except CLEAR, COPY-over-a-live-row and SCALE 0", or treat COPY as CLEAR + ADD. The law then holds verbatim with Lossy covering COPY.
   - #7623 behaviour is unaffected if its words contain no such COPY. Not checked here.
2. **(ii) "zero W0 part" is only the right criterion relative to a U that meets the span of the non-V targets trivially (`hUN`).** Without that, the iff fails.
   - Hand example: G1 = {g}, N = {n}, Rf g = e1, Rf n = e2, U = everything, X g = e1 + e2. There is no loss and X g ∈ U, but X g ∉ span{e1}.
   - The "only if" of (i) also needs `hTgt`, the target state's full token rank.
3. "The V mix is unique" needs independent end rows. rank X[G1] = |G1| was checked [C] on #7623.

**Scope.** "Owned" is not used; the law holds for any register. The W0/T_X split enters only through U.
