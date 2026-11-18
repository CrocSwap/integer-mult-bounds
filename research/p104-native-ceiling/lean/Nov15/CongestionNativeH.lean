import Nov15.CongestionNative
import Nov15.PathCut

/-!
CONGESTION-NATIVE-H: hypothesis reduction for `CongestionNative.ceiling_native` (imported modules unchanged).
1. `c2_anti`: HC3's analytic monotonicity.  psi_s(x) = x^s ln x; q(x) = psi_s(x)/x = x^(s-1) ln x is monotone on (0,9] for s in [.9,1], so psi_s is superadditive there,
   so d/ds of both move prices h9, k0 is <= 0, so c2 (gs s) a b is nonincreasing in s (nondecreasing in t = 1 - s) for 0 <= a <= b <= 9.
2. `spShape`/`cstShape` (min / max over a finite family of nonnegative combinations of c2-weights) are monotone in t on [0, 1/10]; `hdist_of_shape`.
3. `hcong_of_paths`: Path-Cut + 48-law + `hcong_of_capclass` glued: hcong* from per-cell chart paths.
4. `ceiling_native'`: reduced hypothesis list (see CongestionNativeH.md).
-/
namespace CongestionNativeH
open NumCertK JointCeiling CallerCost CongestionI3 Real Finset CongestionI3Dual CongestionNative

/-! ### 1. superadditivity of psi and monotonicity of c2 in s -/

theorem q_mono (s : ℝ) (hs0 : 9 / 10 ≤ s) (hs1 : s ≤ 1) :
    MonotoneOn (fun x : ℝ => x ^ (s - 1) * Real.log x) (Set.Ioc 0 9) := by
  have hcont : ContinuousOn (fun x : ℝ => x ^ (s - 1) * Real.log x) (Set.Ioc 0 9) := by
    apply ContinuousOn.mul
    · intro x hx
      exact (Real.continuousAt_rpow_const x (s - 1) (Or.inl hx.1.ne')).continuousWithinAt
    · exact Real.continuousOn_log.mono (fun x hx => ne_of_gt hx.1)
  have hder : ∀ x : ℝ, 0 < x → HasDerivAt (fun x : ℝ => x ^ (s - 1) * Real.log x)
      ((s - 1) * x ^ (s - 1 - 1) * Real.log x + x ^ (s - 1) * x⁻¹) x := by
    intro x hx
    exact (Real.hasDerivAt_rpow_const (Or.inl hx.ne')).mul (Real.hasDerivAt_log hx.ne')
  apply monotoneOn_of_deriv_nonneg (convex_Ioc 0 9) hcont
  · intro x hx
    rw [interior_Ioc] at hx
    exact (hder x hx.1).differentiableAt.differentiableWithinAt
  · intro x hx
    rw [interior_Ioc] at hx
    obtain ⟨hx0, hx9⟩ := hx
    rw [(hder x hx0).deriv, Real.rpow_sub_one hx0.ne' (s - 1)]
    have hp : 0 < x ^ (s - 1) := Real.rpow_pos_of_pos hx0 _
    have hlog := Real.log_le_sub_one_of_pos hx0
    have key : 0 ≤ (s - 1) * Real.log x + 1 := by
      rcases le_total 0 (Real.log x) with h | h
      · nlinarith
      · nlinarith
    have : (s - 1) * (x ^ (s - 1) / x) * Real.log x + x ^ (s - 1) * x⁻¹ = x ^ (s - 1) / x * ((s - 1) * Real.log x + 1) := by
      field_simp
    rw [this]
    exact mul_nonneg (by positivity) key

/-- psi_s(x) = x^s ln x is superadditive on [0, 9] for s in [.9, 1] -/
theorem psi_superadd (s : ℝ) (hs0 : 9 / 10 ≤ s) (hs1 : s ≤ 1) (x y : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y) (hxy : x + y ≤ 9) :
    x ^ s * Real.log x + y ^ s * Real.log y ≤ (x + y) ^ s * Real.log (x + y) := by
  have hs : s ≠ 0 := by intro h; rw [h] at hs0; norm_num at hs0
  rcases hx.eq_or_lt with rfl | hx'
  · simp [Real.zero_rpow hs]
  rcases hy.eq_or_lt with rfl | hy'
  · simp [Real.zero_rpow hs]
  have hq := q_mono s hs0 hs1
  have e : ∀ z : ℝ, 0 < z → z ^ s * Real.log z = z * (z ^ (s - 1) * Real.log z) := by
    intro z hz
    rw [show z ^ s = z * z ^ (s - 1) by rw [← Real.rpow_one_add' hz.le (by linarith)]; ring_nf]; ring
  have h1 : x ^ (s - 1) * Real.log x ≤ (x + y) ^ (s - 1) * Real.log (x + y) :=
    hq ⟨hx', by linarith⟩ ⟨by linarith, hxy⟩ (by linarith)
  have h2 : y ^ (s - 1) * Real.log y ≤ (x + y) ^ (s - 1) * Real.log (x + y) :=
    hq ⟨hy', by linarith⟩ ⟨by linarith, hxy⟩ (by linarith)
  rw [e x hx', e y hy', e (x + y) (by linarith)]
  nlinarith

/-- `s ↦ gs s u + gs s v - gs s (u+v)` is nonincreasing on [.9, 1] when u, v >= 0, u + v <= 9 -/
theorem tri_anti (u v : ℝ) (hu : 0 ≤ u) (hv : 0 ≤ v) (huv : u + v ≤ 9) :
    AntitoneOn (fun s => gs s u + gs s v - gs s (u + v)) (Set.Icc (9 / 10) 1) := by
  have hd : ∀ z : ℝ, 0 ≤ z → ∀ s : ℝ, HasDerivAt (fun s => gs s z) (z ^ s * Real.log z) s := by
    intro z hz s
    rcases hz.eq_or_lt with rfl | hz'
    · have : (fun s : ℝ => gs s 0) = fun _ => 0 := by funext s; exact gs_zero s
      rw [this]
      simpa using hasDerivAt_const s (0 : ℝ)
    · have : (fun s : ℝ => gs s z) = fun s => z ^ s := by funext s; simp [gs, hz']
      rw [this]
      have := (hasDerivAt_id s).const_rpow hz'
      simpa [mul_comm] using this
  have hall : ∀ s : ℝ, HasDerivAt (fun s => gs s u + gs s v - gs s (u + v))
      (u ^ s * Real.log u + v ^ s * Real.log v - (u + v) ^ s * Real.log (u + v)) s :=
    fun s => ((hd u hu s).add (hd v hv s)).sub (hd (u + v) (by linarith) s)
  apply antitoneOn_of_deriv_nonpos (convex_Icc _ _)
  · exact fun s _ => (hall s).continuousAt.continuousWithinAt
  · exact fun s _ => (hall s).differentiableAt.differentiableWithinAt
  · intro s hs
    rw [interior_Icc] at hs
    rw [(hall s).deriv]
    linarith [psi_superadd s hs.1.le hs.2.le u v hu hv huv]

/-- c2 is nonincreasing in s on [.9, 1] (nondecreasing in t = 1 - s) for 0 <= a <= b <= 9. -/
theorem c2_anti (a b : ℝ) (ha : 0 ≤ a) (hab : a ≤ b) (hb : b ≤ 9) (s s' : ℝ) (hs : 9 / 10 ≤ s) (hss : s ≤ s') (hs' : s' ≤ 1) :
    c2 (gs s') a b ≤ c2 (gs s) a b := by
  have m1 := tri_anti (b - a) (9 - b) (by linarith) (by linarith) (by linarith) ⟨hs, by linarith⟩ ⟨by linarith, hs'⟩ hss
  have m2 := tri_anti (b - a) a (by linarith) ha (by linarith) ⟨hs, by linarith⟩ ⟨by linarith, hs'⟩ hss
  simp only [show b - a + (9 - b) = 9 - a by ring, show b - a + a = b by ring] at m1 m2
  unfold c2 h9 k0
  exact min_le_min (by linarith) (by linarith)

/-! ### 2. shape-DAG families: spF (min of sums) and cst (max of sums) are monotone in t; hdist from path membership -/

/-- a move of the shape DAG: (weight kappa >= 0, from a, to b), priced `kappa * c2 (gs (1-t)) a b` -/
abbrev Move := ℝ × ℝ × ℝ
def Valid (m : Move) : Prop := 0 ≤ m.1 ∧ 0 ≤ m.2.1 ∧ m.2.1 ≤ m.2.2 ∧ m.2.2 ≤ 9
/-- cost of a path (list of moves) at t -/
noncomputable def wsum (p : List Move) (t : ℝ) : ℝ := (p.map fun m => m.1 * c2 (gs (1 - t)) m.2.1 m.2.2).sum

theorem wsum_mono (p : List Move) (hp : ∀ m ∈ p, Valid m) (t t' : ℝ) (h0 : 0 ≤ t) (htt : t ≤ t') (h1 : t' ≤ 1 / 10) :
    wsum p t ≤ wsum p t' := by
  induction p with
  | nil => simp [wsum]
  | cons m r ih =>
    have hm := hp m (by simp)
    have hr := ih (fun x hx => hp x (by simp [hx]))
    have hc := c2_anti m.2.1 m.2.2 hm.2.1 hm.2.2.1 hm.2.2.2 (1 - t') (1 - t) (by linarith) (by linarith) (by linarith)
    simp only [wsum, List.map_cons, List.sum_cons] at hr ⊢
    have := mul_le_mul_of_nonneg_left hc hm.1
    linarith

theorem spShape_mono {κ : Type*} (P : Finset κ) (hP : P.Nonempty) (pth : κ → List Move) (hv : ∀ q ∈ P, ∀ m ∈ pth q, Valid m)
    (t t' : ℝ) (h0 : 0 ≤ t) (htt : t ≤ t') (h1 : t' ≤ 1 / 10) :
    P.inf' hP (fun q => wsum (pth q) t) ≤ P.inf' hP (fun q => wsum (pth q) t') := by
  apply Finset.le_inf'
  intro q hq
  exact le_trans (Finset.inf'_le _ hq) (wsum_mono _ (hv q hq) t t' h0 htt h1)

theorem cstShape_mono {κ : Type*} (P : Finset κ) (hP : P.Nonempty) (pth : κ → List Move) (hv : ∀ q ∈ P, ∀ m ∈ pth q, Valid m)
    (t t' : ℝ) (h0 : 0 ≤ t) (htt : t ≤ t') (h1 : t' ≤ 1 / 10) :
    P.sup' hP (fun q => wsum (pth q) t) ≤ P.sup' hP (fun q => wsum (pth q) t') := by
  apply Finset.sup'_le
  intro q hq
  exact le_trans (wsum_mono _ (hv q hq) t t' h0 htt h1) (Finset.le_sup' (fun q => wsum (pth q) t') hq)

/-- `hdist` from path membership: if dist equals the cost of SOME shape-DAG path, it is >= the minimum over the DAG. -/
theorem hdist_of_shape {κ : Type*} (P : Finset κ) (hP : P.Nonempty) (pth : κ → List Move) (d t : ℝ)
    (h : ∃ q ∈ P, d = wsum (pth q) t) : P.inf' hP (fun q => wsum (pth q) t) ≤ d := by
  obtain ⟨q, hq, rfl⟩ := h
  exact Finset.inf'_le _ hq

/-! ### 3. Path-Cut + 48-law + Cap accounting glued: hcong* from per-cell chart paths -/

open Classical in
/-- hcong* (one value of s) from per-cell chart paths.  Every cell `p` of `J` carries a chart path `c p 0 .. c p (n p)`; `Hold p C` = "u_s of p lies in C".
Premises of `PathCut.path_cut` hold per cell (public edges ascend, owned edges nested, confinement to `G p`, start holds). The path of a cell is its cancellation path (the beta-path of a J^arr cell); `hconf` and `hstart` are what the arrival decomposition supplies for that path, not free premises, and the lemma is not claimed for arbitrary X_s -> Y_t paths (a path that re-enters D_t by a nested owned descent is an ARRIVAL, counted as J^arr, never cut).  A cell whose path is not legal (some chart misses u_s) is cut at a first owned strict
descent `i` dropping u_s with all earlier charts holding it and `c p i <= G p`; `hvisit` says such a cut cell is one of the `cells v` of a visit `v in V` (the 48-law gives `|cells v| <= 48`).
Legal cells charge `Pub + cst Rm` (`hleg`), `|V| <= Nf`, and the Cap class `cst (Rm-8) + U Nf <= Om` closes. -/
theorem hcong_of_paths {α : Type*} [Preorder α] {ν : Type*} [DecidableEq ν]
    (J : Finset (ℕ × ℕ)) (dist : ℕ × ℕ → ℝ)
    (c : ℕ × ℕ → ℕ → α) (n : ℕ × ℕ → ℕ) (Hold : ℕ × ℕ → α → Prop) (G : ℕ × ℕ → α) (owned : ℕ × ℕ → ℕ → Prop)
    (hHold : ∀ p ∈ J, ∀ C C' : α, C ≤ C' → Hold p C → Hold p C')
    (hpub : ∀ p ∈ J, ∀ i < n p, ¬ owned p i → c p i ≤ c p (i + 1))
    (hnest : ∀ p ∈ J, ∀ i < n p, owned p i → (c p i ≤ c p (i + 1) ∨ c p (i + 1) ≤ c p i))
    (hconf : ∀ p ∈ J, ∀ i ≤ n p, c p i ≤ G p) (hstart : ∀ p ∈ J, Hold p (c p 0))
    (V : Finset ν) (cells : ν → Finset (ℕ × ℕ)) (h48 : ∀ v ∈ V, (cells v).card ≤ 48)
    (hvisit : ∀ p ∈ J, ∀ i < n p, owned p i → Hold p (c p i) → ¬ Hold p (c p (i + 1)) → c p (i + 1) < c p i → c p i ≤ G p →
      (∀ j ≤ i, Hold p (c p j)) → ∃ v ∈ V, p ∈ cells v)
    (cap U Pub cst Rm Nf Om : ℝ) (hcap : cap = U / 48) (hU : 0 ≤ U)
    (hleg : ∑ p ∈ J.filter (fun p => ∀ i ≤ n p, Hold p (c p i)), dist p ≤ Pub + cst * Rm)
    (hVcard : (V.card : ℝ) ≤ Nf) (hclass : cst * (Rm - 8) + U * Nf ≤ Om) :
    ∑ p ∈ J, min (dist p) cap - 8 * cst ≤ Pub + Om := by
  have hcut : ∀ p ∈ J.filter (fun p => ¬ ∀ i ≤ n p, Hold p (c p i)), ∃ v ∈ V, p ∈ cells v := by
    intro p hp
    rw [Finset.mem_filter] at hp
    obtain ⟨hpJ, hnl⟩ := hp
    rcases PathCut.path_cut (c p) (n p) (Hold p) (G p) (owned p) (hHold p hpJ) (hpub p hpJ) (hnest p hpJ) (hconf p hpJ) (hstart p hpJ) with h | ⟨i, hi, ho, h1, h2, h3, h4, h5⟩
    · exact absurd h hnl
    · exact hvisit p hpJ i hi ho h1 h2 h3 h4 h5
  have hT := PathCut.transported_card_le V cells _ h48 hcut
  have hT' : (((J.filter fun p => ¬ ∀ i ≤ n p, Hold p (c p i)).card : ℕ) : ℝ) ≤ 48 * Nf := by
    have : (((J.filter fun p => ¬ ∀ i ≤ n p, Hold p (c p i)).card : ℕ) : ℝ) ≤ 48 * (V.card : ℝ) := by exact_mod_cast hT
    linarith
  exact hcong_of_capclass J (fun p => ∀ i ≤ n p, Hold p (c p i)) dist cap U Pub cst Rm Nf Om hcap hU hleg hT' hclass

/-! ### 4. `ceiling_native'`: ceiling_native with hcong, hdist, hspMono, hcstMono replaced by structural hypotheses -/

open Classical in
theorem ceiling_native' {ι : Type*} [DecidableEq ι]
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ) (spF cstF : ℝ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    -- shape DAG: spF is the minimum, cstF the maximum, over finite families of paths of nonnegative combinations of c2-weights
    {κP κC : Type*} (P : Finset κP) (hP : P.Nonempty) (pthP : κP → List Move) (hPv : ∀ q ∈ P, ∀ m ∈ pthP q, Valid m)
    (C : Finset κC) (hC : C.Nonempty) (pthC : κC → List Move) (hCv : ∀ q ∈ C, ∀ m ∈ pthC q, Valid m)
    (hspShape : ∀ t, ((tC0 : ℚ) : ℝ) ≤ t → t ≤ 1 / 10 → spF t = P.inf' hP (fun q => wsum (pthP q) t))
    (hcstShape : ∀ t, ((tC0 : ℚ) : ℝ) ≤ t → t ≤ 1 / 10 → cstF t = C.sup' hC (fun q => wsum (pthC q) t))
    -- dist is realised by a shape-DAG path
    (hdistShape : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tC0 : ℚ) : ℝ) → ∀ p ∈ J, ∃ q ∈ P, distF s p = wsum (pthP q) (1 - s))
    (hJ : 1936 ≤ J.card)
    -- per-cell chart paths (Path-Cut premises), 48-law and visits
    {α : Type*} [Preorder α] {ν : Type*} [DecidableEq ν]
    (c : ℕ × ℕ → ℕ → α) (nP : ℕ × ℕ → ℕ) (Hold : ℕ × ℕ → α → Prop) (G : ℕ × ℕ → α) (owned : ℕ × ℕ → ℕ → Prop)
    (hHold : ∀ p ∈ J, ∀ C C' : α, C ≤ C' → Hold p C → Hold p C')
    (hpub : ∀ p ∈ J, ∀ i < nP p, ¬ owned p i → c p i ≤ c p (i + 1))
    (hnest : ∀ p ∈ J, ∀ i < nP p, owned p i → (c p i ≤ c p (i + 1) ∨ c p (i + 1) ≤ c p i))
    (hconf : ∀ p ∈ J, ∀ i ≤ nP p, c p i ≤ G p) (hstart : ∀ p ∈ J, Hold p (c p 0))
    (V : Finset ν) (cells : ν → Finset (ℕ × ℕ)) (h48 : ∀ v ∈ V, (cells v).card ≤ 48)
    (hvisit : ∀ p ∈ J, ∀ i < nP p, owned p i → Hold p (c p i) → ¬ Hold p (c p (i + 1)) → c p (i + 1) < c p i → c p i ≤ G p →
      (∀ j ≤ i, Hold p (c p j)) → ∃ v ∈ V, p ∈ cells v)
    (Rm Nf : ℝ) (hVcard : (V.card : ℝ) ≤ Nf)
    (hleg : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tC0 : ℚ) : ℝ) →
      ∑ p ∈ J.filter (fun p => ∀ i ≤ nP p, Hold p (c p i)), distF s p ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + cstF (1 - s) * Rm)
    (hclass : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tC0 : ℚ) : ℝ) → cstF (1 - s) * (Rm - 8) + ((9 : ℝ) ^ s - (8 : ℝ) ^ s) * Nf ≤ Omega ks mr s)
    (hspTab : ((spFloC0 : ℚ) : ℝ) ≤ spF ((tC0 : ℚ) : ℝ) ∧ ((spFloC1 : ℚ) : ℝ) ≤ spF ((tC1 : ℚ) : ℝ) ∧
      ((spFloC2 : ℚ) : ℝ) ≤ spF ((tC2 : ℚ) : ℝ) ∧ ((spFloC3 : ℚ) : ℝ) ≤ spF ((tC3 : ℚ) : ℝ))
    (hcstTab : cstF ((tC1 : ℚ) : ℝ) ≤ ((cHC0 : ℚ) : ℝ) ∧ cstF ((tC2 : ℚ) : ℝ) ≤ ((cHC1 : ℚ) : ℝ) ∧
      cstF ((tC3 : ℚ) : ℝ) ≤ ((cHC2 : ℚ) : ℝ) ∧ cstF (1 / 10) ≤ ((cHC3 : ℚ) : ℝ))
    (hunitTab : ((unitLoC0 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - ((tC1 : ℚ) : ℝ)) - (8 : ℝ) ^ (1 - ((tC1 : ℚ) : ℝ)) ∧
      ((unitLoC1 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - ((tC2 : ℚ) : ℝ)) - (8 : ℝ) ^ (1 - ((tC2 : ℚ) : ℝ)) ∧
      ((unitLoC2 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - ((tC3 : ℚ) : ℝ)) - (8 : ℝ) ^ (1 - ((tC3 : ℚ) : ℝ)) ∧
      ((unitLoC3 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - (1 / 10 : ℝ)) - (8 : ℝ) ^ (1 - (1 / 10 : ℝ))) :
    ∀ t : ℝ, ((tC0 : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have htC0 : (0 : ℝ) ≤ ((tC0 : ℚ) : ℝ) := by unfold tC0; norm_num
  have hspMono : MonotoneOn spF (Set.Icc ((tC0 : ℚ) : ℝ) (1 / 10)) := by
    intro a ha b hb hab
    rw [hspShape a ha.1 ha.2, hspShape b hb.1 hb.2]
    exact spShape_mono P hP pthP hPv a b (by linarith [ha.1]) hab hb.2
  have hcstMono : MonotoneOn cstF (Set.Icc ((tC0 : ℚ) : ℝ) (1 / 10)) := by
    intro a ha b hb hab
    rw [hcstShape a ha.1 ha.2, hcstShape b hb.1 hb.2]
    exact cstShape_mono C hC pthC hCv a b (by linarith [ha.1]) hab hb.2
  have hdist : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tC0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p := by
    intro s h1 h2 p hp
    rw [hspShape (1 - s) (by linarith) (by linarith)]
    exact hdist_of_shape P hP pthP _ _ (hdistShape s h1 h2 p hp)
  have hcong : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tC0 : ℚ) : ℝ) →
      ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s := by
    intro s h1 h2
    have hU : (0 : ℝ) ≤ (9 : ℝ) ^ s - (8 : ℝ) ^ s := by
      have := Real.rpow_le_rpow (show (0:ℝ) ≤ 8 by norm_num) (show (8:ℝ) ≤ 9 by norm_num) (show (0:ℝ) ≤ s by linarith)
      linarith
    exact hcong_of_paths J (distF s) c nP Hold G owned hHold hpub hnest hconf hstart V cells h48 hvisit
      (capC s) ((9 : ℝ) ^ s - (8 : ℝ) ^ s) _ (cstF (1 - s)) Rm Nf (Omega ks mr s) (by unfold capC; rfl) hU
      (hleg s h1 h2) hVcard (hclass s h1 h2)
  exact ceiling_native R nR dR hmono hd9 hmix n ks mr st E J distF spF cstF hk hmass hmd hmr hF hY hst hEex hcong hdist hJ
    hspMono hcstMono hspTab hcstTab hunitTab

end CongestionNativeH
#print axioms CongestionNativeH.ceiling_native'
