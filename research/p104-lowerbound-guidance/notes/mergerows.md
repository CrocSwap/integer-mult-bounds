# MERGEROWS MR (Nov 20, Opus, theory + exact checks). Own code in this dir. venv python, threads=1, 1 heavy proc. No Lean, no SAT, no advisor.
How this differs from ISO3/DEN4: they bound one decoder as given (digits, gauges, Sylvester S_l, Toeplitz T_l). This lane changes the decoder first,
using cost-non-increasing refactorizations, and then applies the level-1 bound. ISO3 §5 listed this as escape (2); nobody had tested it.

## 0. Verdict
- [P] NORMAL-FORM LEMMA (cost-safe refactorization). It is port-general and works for any 2-power (or general) denominators. §1.
- [P] In normal form, the ISO3 §3 mechanism cannot occur inside a free class.
  - Normalised digit-0 masks of the class rows are F2-independent on the w side AND the u side at the same time (Goldman–Iwahori / 2-adic elementary divisors).
  - ISO3's Delta had both mask ranks = 1. After normal form both are 6.
- [C exact, explicit gauges] Every decoder that was LOW for S1 = alpha+beta is >= threshold after normal form. Cost never rises, and it often drops. §3.
  - Delta: S1 <= 30 [ISO3 P] becomes S1 = 41 in the canonical gauge and 46 after a gauge climb, at C = 61 <= 62.
- [P] All-saturated decoders are trivial: C >= rank_F2(Q) * omega(Q) (omega = largest Q-clique).
  - HS64 >= 64, E7 >= 49, P104 >= 72.
  - Every E7 Gram decoder is all-saturated (DS: every row has price 7), so E7 Gram cannot be a counterexample. Normal form actually reaches the 49-optimum.
- [C] P104 consistency: E8-56 has NO free class (prices 7 < rank Q = 9, distinct supports). So normal form = identity there, and S1 = 28 + 28 = 56 = C, tight. Nothing above E8 = 56.
- NOT proved: "normal form => alpha+beta >= threshold" for every decoder. That would be PORTWALL itself.
  - No counter-decoder was found: 15 HS64 lows, 6 E7 lows, Delta, a 70-step adversarial SA on HS64 Gram (min normal-form S1 = 46), and 60 + 40 hunted Gram decoders. 0 rigid lows.
  - The open case is named exactly in §4.

## 1. Normal-form lemma [P]
Decoder: rows (w_k, u_k) over Q, with sum_k w_k u_k^T o Q = I on Q-cells. The price is r_k = rank_F2 Q[D_k, S_k], with D_k = supp w_k and S_k = supp u_k. rho := rank_F2 Q.
- (a) TRANSVECTION T(k->k', c): w_k' += c w_k, u_k -= c u_k'.
  - It preserves sum_k w_k u_k^T exactly (expand).
  - New supports: row k' is (subset of D_k ∪ D_k') x S_k', and row k is D_k x (subset of S_k ∪ S_k').
  - It is cost-safe if rank Q[D_k ∪ D_k', S_k'] = r_k' and rank Q[D_k, S_k ∪ S_k'] = r_k. In particular this holds if D_k ⊆ D_k' and S_k' ⊆ S_k.
- (b) FREE CLASS: a set G of rows that are either all saturated (r_k = rho) or all with equal (D, S).
  - Any refactorization W_G -> W_G H, U_G -> U_G H^{-T} with H in GL_g(Q) gives rows of price <= rho (resp. <= rank Q[D,S]). So C does not rise.
  - Reason: supports stay inside the union, and a saturated row cannot exceed rho.
  - If W_G or U_G has dependent columns, one row can be made zero. Then C drops strictly (nf.drop_kernel).
- (c) SIMULTANEOUS REDUCTION.
  - L1 = {h : W_G h ∈ Z_2^n} and L2 = {h : U_G h ∈ Z_2^n} are lattices (full rank after (b)).
  - The sup-norm restricted to the column space is the gauge of L1. So a basis is orthogonal, meaning its normalised mod-2 reductions are F2-independent, iff it is a Z_2-basis of L1.
  - Elementary divisors of L2* relative to L1 give a basis H of L1 such that (H^{-T} 2^{-d_k}) is a basis of L2. Hence both families of reductions are F2-independent. ∎
  - nf.normal_form implements this exactly: lattice_basis + smith2 over Z_(2).
- (d) Validity: C(orig) >= C(NF) >= alpha + beta (NF) for every legal 2-power gauge of the NF decoder (ISO3 §1(a)). So S1^NF := max over normal forms and gauges is a decoder floor.
- (e) Schur form: alpha = dim sum_k a_k ⊙ colspace Q[:, S_k].
  - D(a + a') V ⊆ D(a) V + D(a') V, so for saturated rows (colspace = V := colspace Q) the class term depends only on span{a_k}.
  - So ISO3's "counted once" is exactly dim(span{a} ⊙ V) with span 1-dimensional. Normal form makes the span g-dimensional.
- (f) All-saturated [P]: C = rho * m and m >= rank M >= omega(Q), since M restricted to a Q-clique is I.
  - Q-cliques are orthogonal line sets: omega = 8 for HS64, 7 for E7, 8 for P104.
- Port-general form: all of (a)-(f) use only the label form mod 2 (Q) and rho = rank Q (about h; HS64 8 = h, E7 7 = h, P104 9 = h). No E8 data is used.

## 2. Why Delta is fixed (mechanism)
- Six saturated rows have v2(w) ≡ 1 and v2(v) ≡ -5, and the same full digit-0 mask. Elementary divisors give depths (2, 2, 1, 1, 1, 1). Rows 2 and 3 have depth 2.
- After normal form, the w reductions have rank 6 and the u reductions have rank 6 (Delta: 1 and 1). One row's support shrinks: C goes from 62 to 61.
- ISO3's upper bound (8 + 8 + r2 + r3) assumed one shared mask. That hypothesis is gone.

## 3. Numbers [C exact; S1 = exact alpha+beta at explicit legal gauges found by climb, so lower bounds on the max]
| decoder | C0 | S1 before | free classes (size, depths) | C after NF | S1 after NF | thr |
|---|---|---|---|---|---|---|
| Delta (ISO3) | 62 | 22 (<= 30 [P]) | (6; 2,2,1,1,1,1) | 61 | 41 canon / 46 | 38 |
| HS64 F0·R lows (14, m3_HS64_2_*.pkl) | 52-60 | 27-36 | one class, size 2 or 4 | 48-59 | 38-46 (min 38: m3_HS64_1_4) | 38 |
| E7 lows (e7f_3_0, e7_low_7_4, m3_E7s_3_{1,12}) | 49-56 | 35-38 | (7; 1,...,1,0) after kernel drop | 49 | 49 | 41 |
| E8-56 on P104 (halves) | 56 | 56 | none | 56 | 56 = C | 56 |
| SA over HS64 Gram U (m7, 70 steps) | 61-64 | - | - | - | min 46 | 38 |
- Transvection-only search (m2, no Smith step) also lifts Delta to 43 and the E7 decoders to 38-49. One of them (e7f_3_0) needed the kernel drop to pass.
- Rigid hunt (m3): HS64 F0·R / R·F0 / root-basis Gram decoders (60) and E7 Gram decoders (40). No decoder was both rigid (no cost-safe transvection for any coefficient) and low. Every HS64 low had a saturated class of size 2-4.

## 4. Exact remaining gap (where a counter-decoder must live)
A counterexample to "NF => S1 >= thr" must have its low S1 caused by rows that are:
- (i) unsaturated (price < rho),
- (ii) in pairwise different supports, and
- (iii) without cost-safe transvections (rigid),
- yet sharing digit-0 structure (overlapping a_k ⊙ V_{S_k}), OR suffering depth splitting: rows with depth < e feed only one side of alpha+beta in a uniform port gauge.

Gram-class HS64 and E7 never produced (i)-(iii) with low S1. E8-56 is rigid but tight. The unsearched region is general-model (non-Gram) quarter decoders. That is ISO3's open region too, reached by mod-8 Gibbs moves.

## 5. Next
- (1) Prove the depth-splitting part: in a uniform port gauge a free class contributes sum over depth levels. Combine with Sylvester S_2 (ISO3 §2). The normal-form generator count is exactly len_2(im A) - alpha in the F2[x] picture, so NF-S1 is a level-2 law realised at level 1.
- (2) Run the NF pipeline (m5.py) on general-model Gibbs quarter decoders (TAU gibbs-type moves mod 8). This is the only place a rigid low can hide.
- (3) A Lean candidate: (a) + (b) + (f) are short. The transvection identity and the price monotonicity need no 2-adics.

FILES: nf.py (lattice_basis, smith2, normal_form, drop_kernel), m1.py (Delta U regen, random GL6), m2.py (prices, transvections, safe_any/rigid, search), m3.py (rigid hunt), m4.py (Delta NF; delta_nf.pkl), m5.py (NF pipeline), m6.py (E8-56 check), m7.py (adversarial SA).
Logs: m2_e7.log, m3_hs.log, m3_e7.log, m5_hs.log, m5_e7.log, m6.log, m7_hs.log.
