# Prose statements refuted or tightened by Lean (second package)

Each item is a Lean theorem in `lean/Nov15/`. None of the source notes was published: they are local notes from Nov 15-17. The corrected form is proved in the same file.
Where Lean gives no named counterexample (a vacuity or bookkeeping point) this is said. Nothing here is a κ claim.
1. **Charge certificate covers "all first-order insertions, all ADD/SCALE combinations" (TCCharge).** True for a single insertion (`pure_holder_rule`), FALSE for combinations.
   Counterexample: `TCCharge.ce_base, ce_one, ce_two, ce_both, ce_confined, ce_weak_hyp` (3 registers over ℚ; the first insertion makes `g` ℓ-live and μ-charged in the modified program, so the second delivers `e_h`
   although each is harmless alone, and the change is confined to column h). Fixes: single insertion only (`pure_holder_rule`); or μ ⊥ X at every inserted source in the modified run (`ins_invariant`, `column_pinned`); or recompute liveness after each insertion (not formalised).
2. **TCDepart, "a dirty departure forces h to stay AT F".** False. `TCDepart.CE` (`legal`, `nd`, `final_clean`, `dirty`, `no_stay_at_F`): a legal ascending, ND, final-clean run where the receiver leaves F dirty and h is read at F only for the import.
   Correct: `dirty_departure` (a read of h outside every chart R not containing the departure chart: the cone climb).
3. **TCDepart, "stay at F, or rank(rows at F) covers cargo + e_h".** Vacuous as worded, because the rows of h itself (= cargo + e_h) and of the receiver are always at F at the import. No Lean counterexample (it is a point about the definition).
   Correct form (`clean_departure`, `forced_stay`): a THIRD register j ≠ h, r with e_h content resident at F inside the window, else a stay at F. The cover is stated as presence of e_h, not as span containment of the cargo vector.
4. **FLOOR3, "Σ w0 − corr = 0" (FreeEnd).** False as written: `corr = w0 + ρ(d0) − ρ(e)` contains the potential. Correct: `Σ w0 − w0(d0,e) = D0` (`chD0_eq_sum_w0`), and with the full corr `Σ w0 − corr = D0 + ρ(e) − ρ(d0)` (`sum_w0_sub_corr`).
   Counterexample: `FreeEnd.slip_counterexample` (θ = 1, one move 1 → 2: `w0 − corr = −B1 < 0`, `B1_pos`). The conclusion (relaxation value 0, `floor3_collapse`) is unaffected: it uses the corr-free form.
5. **Spread identity with a single λ (Spread).** The source's "window where z̃ is untouched by h-reads" needs λ CONSTANT, i.e. no h-read in the window. With an h-read inside, the single-λ formula is false:
   `Spread.varying_lambda_counterexample` (true channel −1; λ₀ = 0 gives 0, λ_end = 1 gives −2). The general statement is the time-weighted sum `−Σ_t λ_t y_t`.
6. **WFPort / Y-side theorem, missing hypotheses.** (a) The port charts `H_q` must form an ANTICHAIN: `WFPort.antichain_needed` (two ports with `H q0 < H q1`, one unit of slack serves both: `2 > 1 = Σσ`). (b) `o_C` must count owned BIRTHS, not only owned MOVEs into C, since an owned
   register born in C is a generator of `I_C`; this is the hypothesis `hm` of `forced_stops` (and the same remark applies to `WFUp.up_entry`: the source's bound needs "no owned register born in U"). No separate counterexample theorem for (b). Also needed as hypotheses: q is not born strictly below `q^⊥` (odd weight) and `Bs(q^⊥) ⊆ {q}` (data in the source).
7. **StayRemove, "holders are public registers inside c".** False as worded. `StayRemove.CE` (`base_legalA`, `base_nd`, `base_clean`, `split_legalW`, `split_nd`, `split_clean`, `split_reads`, `not_held`): a base word that is fully ascending, and a split word in which an owned register cleans the public receiver at chart 2,
   DESCENDS 2 → 1 and reads h there; the public receiver then holds `e_h` at chart 2, outside chart 1. Correct: holders (public AND owned) sit inside c UNLESS the continuation contains an owned descent; the hypothesis is `LegalA` on the continuation (`stay_removable_necessary`).

## Statements checked and found true as written (for the record)
Fusion obstruction (scoped to one instant/chart), Lemma TS and Lemma UR (the audits' two hypotheses, char ≠ 2 and clique = all active jobs, are explicit; `tight_needed` shows tightness cannot be dropped),
the INV / SPLIT lemmas (two points where the Lean form is sharper: INV needs only the first factor to be a transvection; the SPLIT determinant term is `det J · ε ≠ σ ε^N`), Lemma COV (spanning cannot be dropped: `cov_needs_span`),
TC and `cancel_only_by_read` (the hypotheses made explicit: final cleanliness and ND).

8. **Per-row W0 law** ("a V-ending row's off-S_V junk must be cancelled below V") is false: `W0Cancel.counter_individual` (ℚ, Fin 3) cancels shared junk at V between two co-resident rows. Corrected: the joint/rank form `w0_cancel`.
9. **"134× W0 multiplicity"** compared a nonzero count with a rank (basis-dependent). Corrected: the terminal labels force rank ≥ p of the W0 block (`loaded_pairs_ge_ports`); `nnz_can_exceed` shows the count can exceed the rank.
10. **JORDAN-U, odd U** ("m = U − 1 ⇒ single 2-block, rank(I − g) = U") fails for odd U: `SpecJordan.odd_counterexample` (U = 3, g = diag(−1, −1, 1)). Corrected: `jordan_even`.
11. **"A public that ever reads X_a never meets Y_a"** holds only AFTER the read: `FrameSep.meet_before_read_possible`.
12. **CONTENT-PIN as first stated** ("distinct helpers' rows always differ, so no re-sourcing preserves finals") omits two hypotheses: a reader that reaches no final makes the swap harmless (`ContentPin.dead_reader_preserves`), and a COPY can equalise rows despite distinct birth tokens (`copy_equalises`). Corrected: `no_reassign`.
