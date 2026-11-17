# What is proved (Lean only), part 3

Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Nothing here is a κ claim.
Every theorem below is kernel-checked in `lean/` (no `sorry`, no `axiom` declaration, no `native_decide`; the word `sorry` occurs only in comments). Every file's axioms are within {propext, Classical.choice, Quot.sound} (CHECK.txt).
"Input" means the Lean statement takes it as a hypothesis or as data; Lean proves nothing about it. Files already in #7632/#7634 are listed in `SHIPPED.txt`. Premise-level status (fact vs assumed) is in `PREMISES.md`.

## A. Premise narrowing for #7620

### ClearCert.lean (imports TokenCancel)
Model: TokenCancel rows over a field K in initial-row coordinates; `Good` = what the #7630 checker enforces besides legality (no birth in the tail, SCALE unit, ADD between distinct registers, COPY/INIT into a zero row).
- `span_step_le`: any non-birth event only shrinks the row span. `span_step_ge`: any Good non-CLEAR event preserves it. `lossless_iff`, `finrank_clear_le` (a CLEAR lowers the rank by at most 1).
- `every_clear_lossless`: hypotheses `rowSpan s ≤ U`, all events non-birth, `FullEnd U s es` (final rows span U); conclusion: every CLEAR acts on a row in the span of the others. No legality hypothesis.
- `checker_sound`: hypotheses `rowSpan s ≤ U`, `U ≤ rowSpan s`, `GoodRun s es`, `Certified s es cs`; conclusion `FullEnd U s es` and every CLEAR lossless. `certOK_lossless`, `lossless_certOK`; `checker_complete`: an endpoint-exact legal word has certificates at all CLEARs.
- `legal_congr`: legality reads only `loc`, never rows. `clearform`: for an arbitrary predicate `Sk` of the owned-event skeleton, two endpoint-exact words with equal owned events satisfy `ErasureOK Sk` together or not at all.
- `copy_nonzero_loses_rank` (counterexample, see FALSE.md); `toy_end`: a 4-register word in the real certificate shape. **Inputs:** `Sk` (arbitrary); the 180 real certificates and the 208,738-event word are NOT replayed (hypothesis `Certified W0 W certs`).

### OwnedAscent.lean (imports FloorEndToEnd)
- `rc_inv`: the rank of the residual of a chart change is inverse-invariant; `back_cost`; `rc_comp` (subadditive). `cost_split`, `ownedCost_nonneg`, `owned_ascent_charged` (≥ 1, given strictly monotone dim). `owned_no_credit`, `invoice_eq`.
- `legal_of_S`, `AcceptedS.toAccepted`, `public_unchanged`, `legal_diff`: strict legality implies relaxed legality, differing only on owned ascents. `hOnce_strict`: the FloorEndToEnd hOnce bound holds for strict-accepted words (hence every FloorEndToEnd theorem does).
- `strict_no_owned_asc`; `W1_relaxed`, `W1_not_strict`, `W1_charge`: a 2-event word that is relaxed-legal, strict-illegal, charge 1.
- **Inputs:** compiled rank = |Δdim| for each chart pair (hypothesis of `price_symm`), dim and nesting, and the admission of owned ascent by the contract. `rc` is a generic rank-of-(T−1) proxy, not the Pauli/Fourier rank.

### NativeColumns.lean (imports TokenCancel)
- `all_columns_of_exact_rows`: if `(run s es).row = T`, the word applied to data `x` in ANY K-module gives `T x`. `exact_rows_iff_columns`: exact rows ⇔ correct on every unit column.
- `matrix_ext_cols`, `linear_ext_span`, `partial_columns_insufficient` (2×2 over ℚ), `adjoint_iff_forward`, `phase_visible`, `census_coverage` (logic only).
- **Not modelled:** Pauli frames, complex phase, the Fourier recipe; the checker script.

### CensusData.lean, CensusComplete.lean (imports NativeColumns)
Data: census 981, #7623 census 964, used(#7630) 3,024 distinct MOVE pairs, used(#7623) 3,021 (generated lists; fidelity by reading).
- `used_subset_base_or_census`: used(#7630) ⊆ used(#7623) ∪ census. `new_in_census`, `leaving_in_census`, `newPairs_facts`, `leavePairs_facts`, `census_extends`.
- `used_not_subset_census` (witness (0,249)): used(#7630) ⊄ census.
- `all_used_correct`: for any predicate `Correct` on pairs, `Correct` on all census pairs and on all pairs used by #7623's word imply `Correct` on all pairs used by #7630. **Inputs:** both hypotheses.

### OwnedSkeletonData.lean, OwnedSkeleton.lean (imports ClearCert)
Skeleton = time-ordered owned INIT / MOVE / CLEAR events of #7630's word (407 events: 180 + 180 + 47; 68 labels). `Sk := E1 ∧ E2 ∧ E3` as a decidable proposition.
- `sk_skel : Sk skel` (E1, E2, E3 separately too), by `decide +kernel`. Counts: `n_lifetimes` 180, `n_clears` 180, `n_moves` 47, `n_labels` 68, `peak_skel` 50, `bank_count` 17 · 68 = 1,156, `lifetimes_exceed_labels`, `total_lifetimes` 3,060.
- `erasure_ok_on_skel`: for every endpoint-exact, birth-free word with rows in U whose owned events equal `skel`, `ErasureOK Sk owned s es` holds. Negative controls rejected: `c_not_nested`, `c_skel_truncated`, `c_peak`, and others.
- **Inputs:** the extracted skeleton; E3 parent/child, E4-E6, compiler admission (not here).

### OwnedTreeData.lean, OwnedTree.lean, OwnedTreeCheck.lean
Model: the unit tree comes from the contract's execution model (a child unit is a complete call made at a paid round, atomic from the parent's view, with its own bank tag); the word carries no unit tags.
- `go_frame`: E1 of one unit transports to the tagged run in any context with nothing live at or below the unit. `execU_id`: from `e1run [] skel = some []`, by induction on depth, running a unit returns the context unchanged.
- `e3_tree sites d : execU sites d [] [] = some []` for ALL depths and ALL call-site lists. `e3_tree_real`: at the 6,250 real MOVE sites (`n_sites`). `caller_tree`: the 17 sequential native calls of the #7113 caller each run to completion from the empty state and end empty; `caller_alphabet`: the caller's op alphabet has no owned-storage op.
- `concrete_d1_owned` (root plus the first 4 owned-MOVE sites as children, kernel-evaluated); negative controls `c_child_leak`, `c_child_steals`, `c_clear_with_desc`, `c_caller_leak`, `c_real_child_leak`, with accepting twins.
- **Inputs:** atomic calls, "child = same word", the extracted sites and caller alphabet (from a local copy of the #7113 caller, sha 255d89f3).

## B. Caller-tied ceiling

### CallerCost.lean (Mathlib only)
Histograms of (rank, count); S = Σ r·(T−P) (`Sinv`), D0 = Σ (T−P)·r ln r; `invoice c n L = caller + L · native`. Caller family C(a|b): 96 A ports x 4 thin queries, 8 B ports; Lean parameters a' = a−2, b' = b−2.
- `reproduction`: C(8|9) (= `caller 6 7`) equals the #7113 caller invoice term for term as histograms (data lists transcribed from the pricer's output); `caller89_S`, `caller89_D0`; S = 57,728.
- `S_caller : S = 3408(a'+b'+4) − 208`. `S_7630_k17`: with native S = −3312 per call and k = 17, S = 1,424. `D0_caller`, `invoice_S`, `invoice_D0` (exact).
- `single_crossing` (first-order proxy K = S/D0, hypotheses 0 < ρ, k1 ≤ k2, d ≤ d'), `cheaper_native_lowers_k`, `crossing_value`, `stationarity_slope` (+ρ, see FALSE.md).
- `composition`: abstract caller class, `Fc(calls) ≤ Dc` and total native floor `Fn ≤ Dn` give `Fc(k) + k·Fn ≤ invoice D0`. `composition_helper` (explicit credit cap R). `kappa_proxy_le`. `naive_composition_false`, `rest_negative` (FALSE.md item 1).
- **Scope:** proxy S/D0, not the exact root κ of F(t) = 0.

### JointCeiling.lean (imports CallerCost; Mathlib rpow)
Convention F(s) = Σ (T−P) r^s with s = 1 − t. `invoice_F`, `natFloor_F` (native floor Nfl(s) = 400·8^s + 16 + 88(2 − 2^s)), `FB_eq` (bridge to `CallerCost.caller` for a,b ≥ 2).
- **Correction:** `FBc a b th s = FB a b th s + 208·8^s·(#arms of 1)`; `callerG_F`, `callerG_S : S(callerG a b 4) = 3408(a+b) − 208` for all a,b ≥ 1; `FBc_two`, `callerG_eq_caller_F`.
- **`ceiling`, `ceiling4`, `ceiling3` (conditional):** for `c : InClass th0`, native `n` with `hN : ∀ s ∈ [0,1], F_nat(s) ≤ −Nfl(s)`, and `hnum : NumCert th0 tbar`: `F(1−t)` of the invoice is < 0 for tbar ≤ t ≤ 1. With th0 = 4, tbar = tbar4 = .0419448764 (rounded up from the certified root .041944876391, peak at 1|1, k = 2); th0 = 3: tbar3 = .0681203280, certified only for the th3 B-form-A class under hB.
  Named hypotheses: `InClass.hB` (B-form per-split optimality pointwise in F on [0,1]), `hth` (th ≥ th0: A ports use th0 QUERY sign units), `hrho` (ρ ≥ 2, i.e. Theorem H plus the t = −1 closure; recorded only), `hN` (native floor; not re-proved), `NumCert` (a finite list of interval inequalities, ~1,800 pairs of 40-digit covers plus the tail step; NOT in the kernel; the tail step "U ≥ F by Jensen/MVT" is unaudited), plus [H-centre] (no line crosses the centre at h ≤ 4) and [H-odd] (a B sign unit costs ≥ ψ(1)) as conditions on the class, and realisability of arms of 1 / k = 2 (no root built).
- **Fully kernel-checked numerics (no NumCert):** `split22_ceiling`: `F(1−t) < 0` for t ≥ 141/4096 (= .034424) for the invoice `I22` of the 2|2 caller and the floor native (28 rational cells); `split11_ceiling`: t ≥ 176/4096 (= .04297) for `I11` (36 rational cells). The class-level forms `ceiling_split22` (`c.a = c.b = 2`) and `ceiling_split11` (`c.a = c.b = 1`) still take `hB`, `hth` (via `InClass 4`) and `hN` as hypotheses. The sharp root is not reachable on the 4096 grid; it is in NumCert.
- `control_bracket`: for the #7113 caller at the floor native with k = 17, F(.0204) > 0 > F(.0205); `I89_F`.
- **Outside the class:** trees, multi-centre callers, shared own roles. The .0336 / .0400 statement is withdrawn (FALSE.md item 5).

## C. SwapNull
Included: see section C below.

## C. SWAP-NULL (SwapNull)
4-op swap gadget at a shared chart (`add h1 h2 +1; add h2 h1 −1; add h1 h2 +1; scale h2 −1`) swaps two helper rows. `undo_one_iff`: with identity finals the swap is hub-undoable iff both helpers end in V or both are born in G0. `stays_multiset`, `delta_eq`, `swap_null`: the stay multiset is unchanged and the cost change is f(e2−b1)+f(e1−b2)−f(e1−b1)−f(e2−b2), zero when ends or births agree. `nonzero_not_undoable`, `converse_witness`: a swap with nonzero cost change cannot be undone by the hubs.

## D. B-form optimality (BFormOpt)
Pointwise in s, for all arm lengths a, b and parameters h, e: `bill_lb` (any feasible schedule), `CB_closed` (arms of 1 included), `own_abel`, `hub_nonpos`, `bform_optimal` (F ≤ F(B form) on B ports), `port_total` (96 A + 8 B ports reproduce the caller cost). `hB_discharge` / `ceiling_of_ports` discharge JointCeiling's hB for B ports, with A ports of the built type. `A_drop_*`: on A ports the B form is NOT optimal (dropping a last-stage own role gains 1 − ψ(1)), which is why A ports are fixed to the built type. Still hypotheses: H-odd, the native floor, NumCert.

## E. Fibre structure, first pieces (FibreK)
`K_word`, `K_invoice`, `kappa_depends_only`: with the cost table P0 as an explicit parameter, the invoice F(t) depends only on the ends E, the timed helper step multiset S and the climb multiset Π = {e_h − b_h}. `tail_pairs` / `head_pairs` (proved directly), `tail_F_null`, `head_F_null`: with helpers ending as identity, any hub-undoable pure relabel preserves the (birth, end) multiset, hence Π and F(t). `c3_not_undoable`. NOT covered: relabel combined with an interior gauge, loops, mixed head+tail relabels, and any "native is optimal over its fibre" statement (open).

# Added in the combined package (ceilings, word structure, spec-break kills, small lemmas)
Each file has a `.md` note in `lean/Nov15/` with the full statement list. Hypotheses are named in the theorems; "input" means Lean takes it as a hypothesis or as data and proves nothing about it. Labels such as R3, R5, RB4, AUDIT5 in the notes refer to internal working notes that are not part of this package.

## F. Whole-word ceilings (WholeFloor*, NumCertK*, FloorK22*, CongestionI3*)
Convention as in JointCeiling: F(s) = Σ (T−P) r^s, s = 1 − t; "κ ≤ t0" means F(1−t) < 0 for all t in [t0, 1].

### WholeFloorModel, WholeFloorSlack (Mathlib only)
Ghosted run state, events (birth, same-chart gate, public MOVE strictly ascending, owned MOVE any chart, owned CLEAR). `reach_inv`, `cs_final` (every row that sits at c at any moment lies in I_c of the end state). `slack_rank`: under hypothesis `Indep` (final rows of stayers plus unit rows of c-born leavers independent) I_c = F_stay ⊕ E_BL ⊕ K_c with dim K_c ≤ σ_c = s_c + o_c; `count_id`, `gens_finrank_le`. **Inputs:** `Indep`; the port lemma (Theorem Y: Σσ ≥ 104 over C ≠ V) is the hypothesis `h_Y`.

### WholeFloorPrice, WholeFloorLogs, WholeFloorEnd (import JointCeiling, JunkLB2)
`d0_floor` (hyps: helper floor `h_help`, main price `h_main`, owned pricing D0 = −Σ f(k_i) with k_i in 1..9, mass ≤ 112, ≥ 16 paid owned MOVEs, `h_Y`): D0_nat ≥ −400 f 8 − 12 f 9 + 2 ln 2 · max 0 (88 − lat), where lat = number of lateral owned MOVEs. `WholeFloorLogs.key` (kernel, 11 prime-log brackets): D0(#7113 caller C(8|9)) ≥ 270,812.8 and the 17-call figure ≥ 155,730.9. `d0_whole_floor` (lat = 0): 17-call invoice D0 ≥ 155,730.9; `d0_whole_floor_any_lat`: any lat gives ≥ 153,656.9. `F_floor`: s in [0,1] gives F_nat ≤ −NflL lat s (JointCeiling's hN derived for lat = 0). `cex`, `cex_priced`, `r3_stops_not_forced`: the lateral-MOVE counterexample (FALSE.md item 11). `fixed_caller_point`.

### WholeFloorNest, WholeFloorCover, WholeFloorCoverData(1) (import NumCertK, JointCeiling)
`Geo`/`NestOwn`/`RunL`: the verifier's nesting rule (public MOVE: proper nested ascent; owned: nested either direction) added to the model; `nest_rank_pos` (every legal MOVE has rank ≥ 1), `nest_lat_zero`. `d0_whole_floor_nested`: priced words obeying nesting have 17-call invoice D0 ≥ 155,730.9 (no lat hypothesis). `hN_nested`.
- **`kappa_whole_floor_nested`:** for nested priced words, F(1−t) < 0 on the invoice (caller 6 7) + 17 native for every t in [.0204110965, 1]. **κ ≤ .0204110965 over legal (nested) words.** Hypotheses: `Priced w` (h_Y = Theorem Y, h_help, h_main, owned pricing), `Indep`, and the F-currency pricing link `hF`. The numeric cover is discharged in the kernel (`WholeFloorCover.cover`: 11 negative pieces on [0, .93] and one monotone piece on [.93, .9795889035], `decide +kernel`, split across the Data files for memory); no numeric hypothesis remains. Digit note: the exact root is .02041109645; the kernel statement uses the 10th-digit round-up.
- **Not in the kernel:** Theorem Y itself, `Indep`, the cost-model link `hF`, and the verifier-nesting reading of the SPEC (a statement about the verifier source, recorded in the note).

### NumCertK, NumCertKData, NumCertK22 (kernel interval arithmetic)
Library: `lnLo ≤ ln ≤ lnHi` (36-term atanh chain, ~1e-28), exp enclosure, `pow_lo` (1 ≤ r, 0 ≤ a ≤ s ⇒ pLo r a ≤ r^s), `pow_hi` (1 ≤ r ≤ 145, s ≤ b ≤ 1 ⇒ r^s ≤ pHi r b), `Fc_le`, `dFc_ge`, `Fc_hasDerivAt`, `Fc_mono`. `cfK_neg`: F(s) < 0 on [0, 1 − .0060197405] for the K(S22) invoice histogram (24 ranks). `numCert22 : NumCert22 tbar22`, `ceiling22_unconditional`.

### FloorK22, FloorK22Data (import FloorD0, JointCeiling)
`ClassK22` = class K(S22): kept data fixed, helpers free and verifier-accepted. `R1Y_row`, `forced_sum` (kernel: Σ over 978 charts of max(0, rk − ab − oa) = 748), `stays_ge_748`, `helperD0_ge_748` (helper D0 ≥ 748 · 2 ln 2 ≥ 1,036.948), `D0_K22` (invoice D0 ≥ 240,134.84; input `CallerD0Input`, the ~70 caller logs), `helperF_le` (F-form native floor derived for every s), `entries_are_registers`, `reentry_two_events`.
- **`ceiling22` / `ceiling22_unconditional`: κ ≤ .0060197405 for class K(S22).** Hypotheses: `ClassK22.rank_ge` (rank of the kept rows at each chart ≥ rk; the 378-coordinate rows are not exported), the cost-model links `hnat`/`hF`, and `CallerD0Input`. `NumCert22` is discharged (NumCertK22). Not formalised: the 845-stop dual (`D0_K22_R6` is conditional on it).

### CongestionI3, CongestionI3Cfg/Data/Mu/NumA/NumC1–C4 (import WholeFloorCover)
`pair_bound`, `i3_D0_per_call` (0.541495 per pair, |J| ≥ 1936 ⇒ ≥ 1048.33 D0/call). `cfgs_ok`, `cfg_uniq0..7`, `uniqCells_disjoint` (the 8 rank-8 C = 56 configurations, 330 unique cells per chain recomputed from the labels), `mu_sum`, `forced_junk_ge` (|J| ≥ 1936). `f1_floor` (max, not sum: `sum_not_implied`), `Fc_mono`, `nine_chord`, `own56_floor`, `dprice_ge`.
- **`ceiling_A`: κ ≤ .0183952347** on the 8|9 invoice, for the restricted class M_V (every public register except Y mains ends at V, owned code fixed, X_q born at A_q).
- **`ceiling_C`: κ ≤ .0134769139**, same class, with descent mass ≥ 56 (rank-8 decoder, C = 56).
- **Hypotheses (named in the theorems):** `MV` (class M_V); I3 as `I3Path` (path-distance telescoping bound, not formalised); `Rank8C56` (exactly the C = 56 rank-8 decoders on P104 labels; exhaustiveness over the 12,870 subsets and rigidity are quoted, C ≥ 58 is not covered); `hDP` (flag-DP minima, python data, not kernel-checked); `hdist`, `hLc` (per-pair lower bounds, numerical); `Prov`/`I3Cap` (public-provenance direction law, open cases listed in the note); `PlaneSep` (ceiling_A only); `hY` (Theorem Y under nesting). **No known native lies in M_V** (224 of 1,501 public registers end at dim ≤ 7), so these are ceilings for the restricted class, not floors on the native class.

### Supporting files for the ceilings
`FloorCertDefs/Data/Check`, `FloorCert` (class-K LP certificate: the support sub-LP of 892 rows × 18,868 columns, `len_ok`, `Y_nonneg_ok`, `bDot_ok`, `cols_ok` by `decide +kernel` with no axioms; `lp_floor`, `stops_ge_780`, `cost_ge_780`, `cost_ge_real`: 780 stays, ≥ 1,081.31 D0/call); `DescentPrice` (paid − credit = 2·descent ranks); `FloorD0` (helper D0 ≥ 2 ln 2 · #paid stays, `floor_D0_classK`: ≥ 780·2 ln 2 under ClassK + H2); `JunkLB2` (g9 pricing and the corrected T4 with owned arrivals, `T4_public_only_false`). Their notes list hypotheses.

## G. Word structure (Shadow, Annihilator, Delivery, DesignLaws, SharedCourier, PsiLaw, WordDuality, PlaneLaws; supporting HubSettle, RankLaw, RankLawC, FrameSep)
- **Shadow** (imports FibreK): the 4-gate birth swap and swap-back are exact swaps (`swapIn_eq`, `swapOut_eq`); `shadow` replaces each main by a single-jump main plus a twin helper; `shadow_net`, `shadow_F`, `shadow_D0`: the NET histogram T − P, hence S, F(t), D0 and κ, are unchanged, under hypothesis `Sym` (P0 symmetry on mains) and the model-membership hypothesis `hM` (replay legality of the twin). The raw T and P counts are not equal (FALSE.md item 15). Not covered: laws that read raw T or P counts, or the gated verifier.
- **Annihilator:** `modular_le`, `step_bound`, `run_bound`, `annihilator`, `sparse_serves_le`: along a nested lineage, served ports ≤ descending owned rank. Model: functionals with support vectors in the start chart, vanishing on a leaf chart.
- **Delivery** (imports TokenCancel, FibreK, Annihilator): `single_contact_null`, `two_contacts_needed`, `const_rows_null`, `two_contacts_suffice` (net delivery needs ≥ 2 contacts with different courier rows); `three_hop_cost`, `ctype_cost`, `fL_three_gt` (three genuine hops cost ≥ f(3)); `zero_gap_counterexample` (FALSE.md item 12); `direct_read_capacity`, `entry_rank_multihop`, `dense_needed`; `never_meet_after_read`, `carrier_before_read`. R = 56 is an input.
- **DesignLaws:** `pcl`, `pcl_orth`, `one_read` (needs the DESCENT hypothesis on the owned lineage; `one_read_needs_descent`), `one_stop_per_dim`, `hyperplane_dedicated`, `rank_feed`, `matrix_rank_le`, `rank_feed_st1` (N = 104, s = 96 ⇒ ≥ 8 ports), `xclose_add`, `xclose_exact`. Not covered: multiplicity, floor numbers.
- **SharedCourier** (imports TokenCancel, FibreK): `shared_row`, `sep_row`, `exact_mod_tokens`, `tc_cleanup`, `legal_tail_iff`. Hypotheses: snapshot row constant during the chain, consumers are never couriers, couriers distinct.
- **PsiLaw** (imports HubSettle): `mapRows_comp`, `psi_two_conditions`, `span_strip_iff`, `span_law_necessary`, `span_law_prefix(_necessary)`, `span_law_not_sufficient`, `unshed_forces_span`, `three_meetings`, `relation_obstruction`, `exposed_read_no_prefix`, `add_swap`, `move_early`. Not formalised: the census counts and the G0-column-operation claim.
- Supporting: `HubSettle` (`solve_inGL`, `iff_false_example`), `RankLaw`/`RankLawC` (`copy_lossy_example`, `rank_law_proj`), `FrameSep` (`X_Y_never_share`, `reader_never_meets_Y_after`, `meet_before_read_possible`).
- **WordDuality** (imports FibreK; model data as hypotheses: charts with an involution ⊥, dim ⊥c = N − dim c, hubs z, V with ⊥z = V): `dual_run`, `dual_legal`, `dual_boundary`, `dual_dim_boundary` (legal words map to legal words; boundaries (b,e) ↦ (N−e, N−b); hub rules swap; ascent stays ascent, descent stays descent); `Mrec_dual` (for MOVE/ADD/SCALE words the matrix is the σ-relabelled transpose); `helperOf_dual`, `dualH_invoice`, `dualH_root`, `word_invoice` (the Theorem-K invoice and the roots of the caller invoice are unchanged; hyps b ≤ e ≤ N, step dims ≤ N); `selfdual_boundary` (P104's X_p/Y_p boundaries are self-dual, g = id); `hosted_block`; `nonhosted_block` (the non-hosted F block is reconstructed as data from the dual block). `copy_not_add`: COPY does not dualise to ADD as matrices (FALSE.md item 22). Not formalised: the P104 chart/physical check, the missing ⊥ frames, the palindromic construction.
- **PlaneLaws** (Mathlib only; Vec n = Fin n → ZMod 2, odd tokens/ports): SPLIT holds for any n (`split_xor`, `split_lemma`, `split_partition`); the claim that t'' is a port holds only on the full odd set when t ≠ t' (`tok_t''`, `t''_eq_one`), not for an arbitrary odd-port set; E7 counts (`e7_split`, 63×62 pairs, kernel `decide`). QUARTER is an exact partition for any n and any subspace B ∋ 1 (`QHyp`, `qhyp_Hs`, `qhyp_unique`, `quarter_partition`, `qtok_junk`, `readers_see_all`). The counts (2^(d−2) quarters × 2^(n−d) tokens each, 4 readers each at n = 7, d = 4) are kernel-checked on E7 only (`e7_block`, `e7_quarter`, `e7_totals`), in a 7-bit-mask encoding whose bridge to `Vec 7` is not proved; the general-n counts are formulas, not formalised.

## H. Spec-break kills (SpecTS, SpecGC, SpecRankP, SpecRankP2, SpecLemmaU, SpecLemmaU2, Spec6, PadLift, Spec0Sym; supporting SpecTSUR, SpecINV, CallerBorrow, Spec0K0Core)
Setting throughout: reflection jobs 1 − x yᵀ, characteristic ≠ 2 where stated; each file's model hypotheses are stated in its note and are inherited, not re-derived.
- **SpecTSUR / SpecTS:** product formula `pp_eq`, `lemmaTS` / `lemmaTS_model`: product of k jobs = a ±1 diagonal flipping exactly k coordinates ⇒ Gram y_i·x_j = 2δ_ij, rank X = rank Y = k, range(I−D) = span(x_i). `tight_needed` (r = k cannot be dropped).
- **SpecINV / SpecGC:** `inv_word`, `det_refl`; `jobs_commute`, `twin_rule`, `twin_empty`, `split_word`, `K_data`, `gap_le`, `gc_strict`, `gc_h0`, `gc_h1` and the word versions `gc_dead_h0/h1/strict`.
- **SpecRankP / PadLift / SpecRankP2:** `rank_ge`, `rank_ge_four` (hyps: Δ = −1 on S, Δ e1 = e1 with e1 ∉ S, im(P−1) ⊆ V with dim V ≤ 2, det P = 1; `det_needed` shows det P = 1 cannot be dropped); `rank_blockdiag`, `pad_rank` (char ≠ 2; `pad_rank_char2_fails`), `pad_sq`, `lift_kill`, `lift_budget`, `job_dark`; `anc_zero`, `JNJ`, `rhoJ_invol`, `Jrho_invol`, `spec7_dead_U34` (U ∈ {3,4}; hypotheses hΛ, hP: Theorem A and the class reduction; U ≥ 5 not covered).
- **SpecLemmaU / SpecLemmaU2:** `lemmaU`, `lemmaU_mat(_T)`, `sylvester`, `sylvester_step`, `p0_q0_le_two`; `kb`, `key3`, `key4`, `Em1_bound`, `spec0_core_U4`. Open hypothesis: the k = 0 involution step `hk0`.
- **Spec6:** the group-theoretic kill L1–L4, F1 and the case split (`GX`, `job_of_GX`, …), n-free and order-free, char ≠ 2.
- **Spec0Sym + Spec0K0Core:** `Gl_closed`, `cover`, `distinct` (90 orbit representatives of the 720 orders under a group of order 8), `step_F`, `step_T`, `reduction`. Named gaps: wp vs explicit-word bridge, the model definition (`ModelOK`/`Rel`), k = 0 statements only.
- **PARTIAL: Spec0K0_ABCEDF_s0 … s6** (radical certificates, class ABCEDF): of 68 targets, 28 are identically zero (`ring`), 32 are certified by `linear_combination` certificates, **8 are NOT certified** (ω1, ω2, ω5, ω6 and the four (1,4) entries); that is 60 of 68 targets of this one class. Needs CharZero (denominators 2^k). No kill claim is made from these files.
- **CallerBorrow:** BORROW lemmas R/OS/GS in an abstract caller model (`commute_of_line`, `RebaseData.lemmaR`, `not_both`; the GS block identities are checked numerically outside Lean).

## I. Smaller lemmas
- **LemmaW** (imports CallerBorrow): `pp_window_entry`, `lemmaW_defect` (exact; needs only that the prefix before R commutes with the mask), `lemmaW` / `lemmaW_vec` (also needs A commuting with the mask and 2 ≠ 0), `lemmaW_unique`.
- **SmallRoots** (+ SmallRootsDefs, SmallRootsData, SmallRootsA22Corners): `smallcaller_1_1_A`, `smallcaller_1_1_B`, `smallcaller_2_2_A` (`IsRoot` for the three small-caller roots, N = n + 2 units; one condition per field of the checker, `decide +kernel` on exact rationals with rank certificates), `pair_types`. Data are generated; their fidelity to the source roots rests on reading.
