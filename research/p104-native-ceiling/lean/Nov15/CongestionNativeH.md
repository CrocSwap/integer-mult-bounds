# CongestionNativeH.lean: ceiling_native' with reduced hypotheses
Imports CongestionNative + PathCut (so path_cut, transported_card_le, hcong_of_capclass are now WIRED into the corollary via `hcong_of_paths`). Existing files unchanged. Kernel only; `#print axioms` of every theorem = [propext, Classical.choice, Quot.sound]. Build 8-20 s, 2.9 GB peak.

## Proved here (no longer hypotheses)
- `q_mono`, `psi_superadd`, `tri_anti`, `c2_anti`: for s in [.9,1], psi_s(x)=x^s ln x is superadditive on [0,9] (via q(x)=x^(s-1) ln x monotone on (0,9]; first-derivative proof, HC3's convexity not needed), so `c2 (gs s) a b` is nonincreasing in s (nondecreasing in t=1-s) for 0<=a<=b<=9. The paper step was TRUE as written.
- `wsum_mono`, `spShape_mono`, `cstShape_mono`: min / max over a finite family of paths (lists of moves (kappa>=0,a,b), 0<=a<=b<=9, priced kappa*c2) is monotone in t on [0,1/10]. => hspMono, hcstMono DERIVED from `hspShape`/`hcstShape` (spF = inf', cstF = sup' of the path costs on [tC0,1/10]) + `hPv`/`hCv` (validity of moves). NOTE: "spF/cst are such min/max of c2-weighted sums (weights = c2 / (n m), constants)" is now the hypothesis; completeness of the 230+dual shape DAG is NOT checked by Lean.
- `hdist_of_shape`: hdist DERIVED from `hdistShape` (for s in [.9,1-tC0], p in J: distF s p equals the cost of SOME path of the family P at t=1-s) because spF = inf' over P.
- `hcong_of_paths` (+ `path_cut`, `transported_card_le`, `hcong_of_capclass`): hcong* DERIVED from per-cell chart paths (see below).

## `ceiling_native'`: EVERY hypothesis (copied from the Lean statement)
Data: `{ι} [DecidableEq ι] R : Finset ι, nR : ι→ℕ, dR : ι→ℕ→ℕ` (public registers: level d r 0..n r), `n : Inv`, `ks : List ℕ`, `mr st : ℕ`, `E : ℝ→ℝ`, `J : Finset (ℕ×ℕ)`, `distF : ℝ→ℕ×ℕ→ℝ`, `spF cstF : ℝ→ℝ`; all abstract (nothing in Lean ties them to a word).
Carried over unchanged from ceiling_native:
1. hmono: ∀ r∈R, ∀ i<nR r, dR r i ≤ dR r (i+1); hd9: ∀ r∈R, dR r (nR r) ≤ 9; hmix: #{r∈R : Mixed (1 ≤ dR r 0 ∧ dR r (nR r) ≤ 8)} ≤ 5.
2. hk: ∀ k∈ks, 1≤k≤9; hmass: 56 ≤ ks.sum; hmd: 8 ≤ ks.length; hmr: 8 ≤ mr; hY: 104 ≤ st + (ks.length + mr).
3. hF: ∀ s∈[0,1], Finv s n ≤ -400·8^s - dprice ks s - mr - E s   (exact ≤, a real-continuum inequality).
4. hst: ∀ s∈[0,1], (2 - 2^s)·st ≤ E s   (zero slack at s=1).
5. hEex: ∀ s∈[0,1], Σ_{r∈R} ex (gs s) (lev dR r) (nR r) ≤ E s   (≤, not an identity).
6. hJ: 1936 ≤ J.card.
7. hspTab, hcstTab, hunitTab: certified rational tables (spFlo ≤ spF(tC_j); cstF(t_{j+1}) ≤ cH_j; unitLo ≤ 9^s-8^s), numerics outside the kernel (hc9.py).
NEW (replace hcong, hdist, hspMono, hcstMono):
8. Shape DAG: finite families P (nonempty), C (nonempty) with `pthP, pthC : κ → List Move`, `hPv, hCv` (every move valid), `hspShape: ∀ t∈[tC0,1/10], spF t = P.inf' (wsum (pthP q) t)`, `hcstShape: ... cstF t = C.sup' ...`.
9. hdistShape: ∀ s∈[.9,1-tC0], ∀ p∈J, ∃ q∈P, distF s p = wsum (pthP q) (1-s).
10. Per-cell paths: `{α} [Preorder α] {ν} [DecidableEq ν]`, `c : ℕ×ℕ→ℕ→α`, `nP`, `Hold : ℕ×ℕ→α→Prop`, `G`, `owned`, with (for all p∈J): hHold (Hold monotone under ≤), hpub (¬owned i → c i ≤ c (i+1)), hnest (owned i → comparable), **hconf (∀ i ≤ nP p, c p i ≤ G p: the WHOLE path stays in G)**, **hstart (Hold p (c p 0))**.
11. Visits: `V : Finset ν`, `cells : ν→Finset (ℕ×ℕ)`, h48 (∀v∈V, |cells v| ≤ 48), **hvisit**: for p∈J, i<nP p, owned i, Hold(c i), ¬Hold(c (i+1)), c(i+1) < c i, c i ≤ G p, (∀ j≤i, Hold (c j)) ⟹ ∃ v∈V, p∈cells v.
12. Cap class: reals Rm Nf, `V.card ≤ Nf`; hleg: ∀ s∈[.9,1-tC0], Σ_{p∈J, legal} distF s p ≤ Σ_pub c2 + cstF(1-s)·Rm  (legal = every chart of the path holds u_s); hclass: cstF(1-s)(Rm-8) + (9^s-8^s) Nf ≤ Omega ks mr s.
Still NOT proved in Lean: hleg (I3 charge + rise saving on legal cells), hvisit, hconf/hstart/hpub/hnest for the actual register machine (SP span law, ADD paths), 48-law (h48), the DAG facts of item 8-9, hJ, hF/hst/hEex continuum inequalities, tables 7, hclass (numeric on natives: margin 19.356, computed).

## Caveats the Lean statement makes explicit (from RESULT-D)
- (b) `hstart : Hold (c 0)` is a premise of path_cut and of hcong_of_paths (fails at n=0 otherwise).
- (d) The Preorder cannot tell rank-descent MOVEs from owned INITs. The needed premise is: the chart path of a cell consists of register MOVE edges only (it never crosses an INIT/birth edge); this is exactly what `hpub`/`hnest`/`hvisit` quantify over, and it is NOT derivable in Lean.
- Path-Cut wording (corrected, from the Nov 17 review of the re-entry case): the lemma is applied ONLY to the cancellation path of a junk cell in J^arr, i.e. the path along which the birth symbol of X_s reaches the final row of Y_t by symbol bookkeeping inside D_t = the down-closed set of charts below G_t. `hconf` (every chart of the path is <= G_t) and `hstart` (Hold at the first chart, u_s in <u_s>) are consequences of that arrival decomposition, not free premises. They are still hypotheses of `path_cut` in Lean; the decomposition that supplies them is not formalised. For an arbitrary X_s -> Y_t path the conclusion "(t,s) in cells(C_a)" is false (a path that rises outside D_t and re-enters it by a nested owned descent dropping u_s is a path of an ARRIVAL; such cells are counted on the left-hand side as J^arr, never cut). The statement of the lemma is unchanged. On the three natives, 0 of the 4962 junk cells need a cut (every one has a legal owned-descent-free path).
- Corrections to CongestionNative.md (file untouched): its items 3-7, 9 misdescribe hk/hY/hF/hEex/hst/hdist as in item list above; item 8 should read cstF (1-s) not cst; hdist holds for s in [.9,1-tC0]; "natives satisfy hypotheses" rests on computed facts, and hcong/hdist/hspMono/hcstMono additionally on unformalised DAG/register-machine papers (AUD2 did not recheck ID1/DAG/hc9).
