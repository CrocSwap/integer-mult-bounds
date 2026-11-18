# Corrections after an independent review

An independent review compared the package's prose (PR body, README.md, PROVED.md) with the Lean statements. Every item below was checked against the Lean source. The Lean theorems are unchanged and still compile; the prose overstated scope or misstated hypotheses. None of the three ceiling theorems is false, but each covers less, or assumes more, than the prose said. One number was false as written (item 13).

Format: **said** / **Lean proves** / **corrected statement**.

## Ceilings
1. **M_V class hypotheses.** Said: hypotheses MV, Rank8C56, PlaneSep / Prov define the restricted class. Lean: `ceiling_A`, `ceiling_C` take `MV Rank8C56 PlaneSep : Prop` (resp. `Prov`) as uninterpreted propositions that only guard `hI3`; any propositions, `True` included, can be supplied. Corrected: M_V is not formalised; the class restriction rests on the reading of the I3 hypothesis.
2. **M_V junk count.** Said: the ceilings use the flag-DP minima. Lean: both take `hJ : 1936 ≤ J.card` directly; `forced_junk_ge` (with `hDP`) is a separate theorem, not invoked. Corrected: |J| ≥ 1936 is a hypothesis of the ceilings; its derivation from the flag-DP minima is a separate, unlinked result.
3. **`ceiling_A` hypothesis list.** Said (PR body): I3, flag-DP minima, rank-8 C = 56, public provenance. Lean: also `PlaneSep`, `hF` (native F bound), `hmp : 16 ≤ mp`, `hY : 104 ≤ st + mp`, `hst`, `hdist`; fixed caller C(8|9), 17 calls; `Prov` is not a hypothesis of `ceiling_A`. Corrected: full list now in PROVED.md §F.
4. **`ceiling_C` hypothesis list.** Lean also needs `hk` (ranks 1..9), `hmd : 8 ≤ ks.length`, `hmr : 8 ≤ mr` (owned rises), `hcorr0`, `hF`, `hst`, `hLc`. Corrected: listed in PROVED.md §F.
5. **Whole-word scope.** Said: "κ ≤ .0204110965 over legal (nested) words". Lean: `kappa_whole_floor_nested` needs `Priced w`, which includes `h_m16 : 16 ≤ ow.length` and `h_mass : ow.sum ≤ 112`, plus `hF`; without `h_m16` the derived native floor fails (e.g. 0 owned MOVEs, 104 stops). Corrected: κ ≤ .0204110965 for nested words satisfying `Priced` (at least 16 paid owned MOVEs, owned mass ≤ 112, ranks 1..9, helper/main price floors, Theorem Y) and `hF`.
6. **Whole-word `Indep`.** Said: `Indep` is a hypothesis. Lean: `WholeFloorNest` does not import `WholeFloorSlack`; `Indep` does not occur in the theorem; `Word` is a pricing summary and `NestedWord` links only its lateral count to a MOVE log. Corrected: `Indep` is upstream of `h_Y` and not linked to the theorem.
7. **Whole-word caller.** PR body omitted that the statement is for the #7113 caller C(8|9) at 17 calls. Corrected: stated.
8. **K(S22) endpoint.** Said: F(1−t) < 0 on [t0, 1]. Lean: `0 < s`, so t in [.0060197405, 1). Corrected: stated.
9. **K(S22) hypotheses.** Said: `rank_ge`, `hnat`/`hF`, `CallerD0Input`. Lean: `ceiling22_unconditional` takes `hdim`, `ClassK22` (fields `kc`, `kfin_all`, `rank_ge`, `count_le`, `oa_le`, `keptP`) and `hF`; `hnat` and `CallerD0Input` belong to `D0_K22` only. Corrected: listed.
10. **K(S22) class.** Said: "helpers free and verifier-accepted". Lean: `Accepted` is the model's (legality, helpers public, helper finals unit vectors); no word, S22 included, is shown to lie in `ClassK22`. Corrected: stated.
11. **JointCeiling .0419.** [H-centre] and [H-odd] were called "conditions on the class"; they are not fields of `InClass` or hypotheses of any theorem. `hrho : 2 ≤ rho` is unused. `NumCert` (not kernel-checked) was not named in the PR body. Corrected: stated.
12. **2|2 and 1|1 "fully kernel-checked".** Lean: the numerics (`split22_ceiling`, `split11_ceiling`) are for the fixed invoices I22, I11 at the floor native; the class forms still take `hB`, `hth`, `hN`. Corrected: "numerics kernel-checked; class hypotheses remain".
13. **`cost_ge_real` "≥ 1,081.31".** False as written: 780 · 2 ln 2 = 1,081.3096 < 1,081.31. Lean proves 2 ln 2 · 780 ≤ cost (and `floor_D0_classK` ≥ 1,081.309). Corrected: ≥ 780 · 2 ln 2 ≈ 1,081.3096. The same rounding appears in `FloorCert.md` and a `FloorCert.lean` docstring.
14. **FloorCert / FloorD0.** The LP certificate is checked standalone and reaches class-K words only through hypothesis H2; `helperD0_ge_fL` needs `hdim` and `Accepted`. Corrected: stated.

## Premise narrowing
15. **PROVED.md "every theorem with its exact hypotheses".** Not so, by items 1-14 and 16-30. Corrected: "the theorems with their hypotheses; the Lean statements are authoritative".
16. **ClearCert.** `checker_complete` also needs `rowSpan s ≤ U`, `DeadZero s` and non-birth events; "every CLEAR is lossless" holds for birth-free, endpoint-exact words. Corrected.
17. **OwnedAscent.** `price_symm` is |dim b − dim a| = |dim a − dim b| with no hypothesis; symmetric pricing and zero owned credit are definitions (`mvCost`, `credit`). Corrected: "priced symmetrically, no credit" described as model definitions; the |Δdim| = compiled-rank assumption is built into them.
18. **NativeColumns.** `all_columns_of_exact_rows` concludes for data `evalRows s.row x`; the statement "the word applied to x gives T x" is `word_computes`, which needs `s.row = 1`. Corrected.
19. **CensusComplete.** The kernel checks list inclusion on extracted lists; correctness of all used pairs follows only from two input hypotheses. PR body corrected.
20. **OwnedSkeleton / OwnedTree.** The skeleton is extracted, not derived; the tree model runs the same word in every child; `caller_tree` models 17 atomic calls without reading the op list. Corrected.
21. **`caller_alphabet`.** Lean checks that every op code is ≤ 7; the meaning of the codes is a comment. Corrected.

## Word structure and kills
22. **SwapNull.** README said "zero cost change in exactly those cases"; Lean gives zero change whenever ends or births agree (undoable or not) and undoable ⇒ zero, not the converse. `undo_one_iff` assumes final matrix F = 1 on all registers. Corrected.
23. **FibreK `tail_F_null`.** Also needs σ fixing non-helpers, V-enders = helpers ending at one chart, G0 born at 0, shifted gauge `Undo (V ∘ σ) G0`. Corrected.
24. **Shadow.** PR body omitted the `Sym` hypothesis; S follows from the net histogram (no separate theorem). Corrected.
25. **Annihilator.** `sparse_serves_le` needs an injection ι with identity Gram block. Corrected.
26. **Delivery `three_hop_cost`.** Exactly three hops, climb = sum of gaps. Corrected.
27. **WordDuality.** `selfdual_boundary` contains no P104 data: boundaries, σ and ⊥ are hypotheses. "Legal" is `LegalL` (locations only). `word_invoice` needs climbing registers and `hR`. Corrected.
28. **PlaneLaws.** `tok_t''` needs n odd; QUARTER counts are checked for one block of E7; `e7_totals` is arithmetic. Corrected.
29. **SpecGC.** `gc_h0`, `gc_h1`, `gc_dead_h0/h1` take 0 < U. Corrected.
30. **Spec6.** `spec6_dead` is conditional on `R58_PL`, `R58_ALLX`, `R58_ALLY`. Corrected.

Also recommended outside the three corrected files: FALSE.md item 11 ("restores the floor for every legal word") should read "for every nested word satisfying `Priced`"; `FloorCert.md` "1,081.31" should read "≈ 1,081.3096".

Reviewed and not changed: `DescentPrice` "paid − credit = 2·descent ranks". `helper_identity` holds for any integer path with credit = end − start, with no hub or legality hypothesis.
