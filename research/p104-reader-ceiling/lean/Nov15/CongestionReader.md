# CongestionReader: a per-reader endpoint charge on top of the tree ceiling of #7678 (labels CG2, AUD, F1, F2, F2b, TL-a/b/c, EP3 are internal note labels; those notes are not part of this package)

Files (`Nov15/`, kernel only: no sorry, no native_decide; axioms propext, Classical.choice, Quot.sound; each file built alone under runlean.sh, peak <= 3.2 GB; the generators of the data files are not part of this package):
`CongestionReaderCore` (registers + payers), `CongestionReaderTree` (`lineOKR`, `tree_lower_reader`), `CongestionReaderPiece` (`reader_regs_lower`, `reader_piece`),
data `CTree{rd,re,rf}{a,i}*` / `CTreeData{RD,RE,RF}{A,I}` (the two 230-row DP tables per variant, `decide +kernel` per row; ALL edges, and the I-class 48-port edge set),
`CongestionReaderCert{RD,RE,RF}*` (weights, delta, line, sigma, point, unit certs), finals `CongestionReader` / `CongestionReaderW10` / `CongestionReaderW16`.

## Certified results (true digits)
| theorem | w0 (omega <= w0) | allowances NDL = 15 + w0 | kappa <= (certified, t in [a0, 1]) | paper figure |
|---|---|---|---|---|
| `ceiling_reader_GD` | 0 | 15 | **.0115262** | AUD2 .0115250 |
| `ceiling_reader_GD_w10` (HEADLINE, F2b) | 10 | 25 | **.0115428** | .0115417 |
| `ceiling_reader_GD_w16` | 16 | 31 | **.0115528** | .0115516 |
Each is `F(1 - t, invoice (caller 6 7) n 17) < 0` for t in [a0, 1], by `ceiling_native_J` on [tJ0, 1] and by 2-3 `reader_piece`s on [a0, tJ0].
The certified digit is 1.0-1.2e-6 above the paper digit in each case (t quantised to 1e-7 after piece margins >= .002; lcp rounded down; weights/delta rounded outward).  For comparison `ceiling_tree_GD` is .0116750.

## What is Lean-proved (CongestionReaderCore/Tree/Piece)
* `resid_V`, `resid_Z` (EP3 identity, inequality form): residual `rho = ex - sum path c2`; V-class (ends at 9): `rho >= beta(d_j) - beta(d_0)`; Z-class (born 0): `rho >= beta(d_j) - beta(d_n)`, `beta a = g a + g (9-a)`; from `h9 - k0 = beta b - beta a`.
* `beta_ge` (concavity of x^s, `Real.concaveOn_rpow`): beta(a) >= beta(7) for a in [2,7]; `beta_one_eight`; `tied_rho`: a TIED register (Z, ends at 8, or V born at 1 ending at 9, with a stop at dim in [2,7]) has `rho >= delta = 7^s + 2^s - 8^s - 1`.
* `sum_c2_pay`: distinct readers tied to distinct registers of residual >= delta, <= m mixed: `sum path c2 + delta |Q| <= sum ex + m sigma` (non-payer registers keep `rho >= -sigma [mixed]`, from the `sum_all_c2_le` step).
* `tree_lower_reader`: `tree_lower` with the per-reader allowance: every reader is tied (in Q: line with +dI, dI <= SC delta), all-transported (x = k: needs only lam <= capI, tree >= 0), or in Uo (|Uo| <= NDL: allowance subtracted).  Conclusion `lam*4962 - gamma-sum - NDL*dI <= SC(sum w + cap sum x + delta |Q|)`.  `lineOKR` = the 49x49 integer check with `+ dI` and `gA, gB >= 0, lam <= capI`.
* `reader_regs_lower`, `reader_piece`: shape of `tree_piece`; the delta|Q| term cancels between the tree side and `sum_c2_pay`, so |Q| never needs a lower bound.
* Numerics: `hdel*` (dI <= SC delta on the window: `dLo (negCF cfDel) > 0` + point `Fup`, via `cf_lower`), `corr_nonneg*`, weight tables, line/num/cap/sigma/point/unit certs per piece.  The kernel-checked IN table is a DIFFERENT table from the OUT one in the I-class 48-port set (18 of 230 rows differ) but has the same root value.
* Floor on `gB`: gamma must be >= 0 (a reader with no cells); the first draft allowed gB < 0, which is unsound for k_s = 0 readers (caught by the Lean `ℕ` type), so `gamma = max(0, ...)`.

## Hypotheses generated from the Lean text (status)
Old (as `ceiling_tree_GD`, unchanged; see CongestionTree.md of #7678): hmono, hd9, hmix (<= 5 mixed), hk, hmass, hmd, hmr, hF, hY, hst, hEex = natives computed facts; hcong*, hdist, hJ (t >= tJ0 only) = open paper (I2); hspMono/hcstMono (HC3 paper); hspTab/hcstTab* (data brackets); `T : TreeData` (htree*, hcap, hMv..., hdim) and hP1, hP2 = open paper (CG1 sec. 2b; nested moves), `hcst0/1/2` (`hcst0/1` in the w10 and w16 variants: two pieces, not three), `hcstMonoT` data.
New:
1. `T` is now the READERS' tree data (IN side: `T.S` = readers, `T.J` = (reader, source) cells, `T.R` = sources of non-transported cells).  The IN DP table is the reflection of the OUT table (paper: F equal at every k; c2 is reflection symmetric, `k0_eq_h9_swapN`), the reflection is folded into `T.dA/T.dB`.  OPEN (paper).  Class counts: 104 readers, 48 partners, sum 4962 = natives (KS_IN = 101x48 + 3x38).  The restricted-edge set for 48 readers is the I-class set `E48^I` (natives computed, GD1 sec. 3-4, not enumerated in Lean).
2. `Q, Uo, hUo, hQ, hcase`: every reader is tied (Q), all-transported (`x = k`), or untied (Uo).  This is the CG2 dichotomy (sec. 2): cells on dim-1 moves carry <= 1 cell each at cost >= min(c18, capv) = capC (the cap class), else a dedicated register pays.  OPEN (paper; CG2 + AUD2 check (2) numerics: the dim-1 branch never binds).
3. `ω, hω : ω ≤ W0, hUc : Uo.card ≤ 15 + ω`: |Uo| <= 5 mixed + 10 owned last movers (AUD2 F1) + omega, omega = net G'-token rank absorbed by owned rows.  Review (F2 note): the F2 lemma as posed is FALSE (5-register token-swap counterexample, payer X_s outside S_t); correct form F2*: payers >= N_high - 15 - omega.  TL-a's "only public registers hold e_g" is FALSE on the natives (owned rows hold G' tokens) and is NOT used.  omega = 0 on all four natives -> w0 = 0 variant; F2b proved omega <= 10 for the class under two premises (no owned register rises to V from dim <= 7; every owned lifetime ends in CLEAR; both hold on the natives) -> w0 = 10 HEADLINE; w0 = 16 kept as the wide variant.  Status: omega <= w0 is a NAMED hypothesis (F2b is on paper; the CLEAR-certificate module (ClearCert, not part of this package) is not wired in).
4. `π, hπR, hπinj, hTied`: each tied reader has a distinct register `π t` in R with `Tied` (Z-class ending at dim 8 or V-class born at dim 1 ending at 9, with a stop at a dim in [2,7]).  `tied_rho` is Lean-proved, so the residual >= delta is NOT a hypothesis; what is assumed is the existence/uniqueness of the tied register = CG2 sec. 2 case analysis [premises: CG1 cell paths, own56 (<= 5 mixed; owned moves 6x9 + 2x1 descents + 8 unit rises), X/X2 born at dim 1 (audited as a restriction, holds on st1, x1t2a, e1, t7669), TL-b/TL-c (TL1)] + the F2* lineage step (public relays).  Per-reader uniqueness ("a payer tied to u_t^perp serves one reader") uses: every register visits <= 1 dim-8 chart.  OPEN (paper).
5. `hcstLo : 0 <= cstF t` on [a0, 1/10] (added after review; makes `corr_nonneg*`, i.e. the sign `0 <= corrC cstF s` needed for hP2, a Lean fact).  `cstF` is a free function in the Lean text with upper brackets only, so the lower bracket is a hypothesis: it follows from cst(t) = max c2(p,q)/(q-p) >= c2(7,8) > 0 (the weight table W(7,8) > 0 on the window, `W_lower`).  Word-side premises of hP1/hP2 and the tree: see NATIVES.md (the tree-premise script `tp1.py`, both primes): all five words (st1, w7637, x1t2a, e1, t7669) meet them except the sign now covered here.
6. `hdel*`/numeric certs: no hypotheses.

## Paper checks
* No false step found in the shippable formula once the F1 fix (NDL 15) is in; the old 99 delta / .0115086 form is not formalised (needs owned moves barred from dim-8 charts).
* F2 as posed is false (F2LEMMA counterexample); the Lean statement therefore never uses a per-reader lineage lemma, only the existence of a tied register (hypothesis 4) and the count bound omega (hypothesis 3).  If hypothesis 4 is replaced by the weaker F2* count `|Q| >= N_high - 15 - omega`, the Lean proof is unchanged (Uo absorbs the shortfall).
* Lean counterexample found: none needed for the paper steps; the one false statement found in the first draft was the sign of gamma (above).
