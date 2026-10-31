import Mathlib

/-!
# Network-coded carriers on P104: the dual-span walk bound (Lemmas S, A, M of PROOF.md)

Frames are subspaces `C` of `F₂⁹`.  We work with their orthogonal complements (`C^⊥` for the dot product).
A public ascent `C ≤ C'` shrinks the dual (free), an owned descent `C' ≤ C` grows it and costs
`dim C - dim C' = dim C'^⊥ - dim C^⊥` (`descent_cost_dual`).  A receiver whose final frame is `p^⊥` can read
only in a frame `C` with `p ∈ C^⊥`.

An information walk is a sequence of dual subspaces `Z 0, Z 1, …`; node `k ≥ 1` is produced from an earlier node
`par k` (a copy, a stop, a relay through public helpers or a branch) either by shrinking (free) or by growing (paid).
The union span of all visited nodes grows by at most the paid amount (`union_bound`).
-/

namespace NetCode

open Module

abbrev V := Fin 9 → ZMod 2
abbrev Sub := Submodule (ZMod 2) V

/-- The dot-product form on `F₂⁹`. -/
def dotForm : LinearMap.BilinForm (ZMod 2) V := Matrix.toBilin' 1

theorem dotForm_apply (x y : V) : dotForm x y = x ⬝ᵥ y := by
  simp [dotForm, Matrix.toBilin'_apply', dotProduct]

/-- The dual of a frame. -/
def orth (C : Sub) : Sub := dotForm.orthogonal C

theorem mem_orth {C : Sub} {p : V} : p ∈ orth C ↔ ∀ x ∈ C, x ⬝ᵥ p = 0 := by
  simp [orth, LinearMap.BilinForm.mem_orthogonal_iff, dotForm_apply]

/-- `dim C + dim C^⊥ = 9`. -/
theorem finrank_add_orth (C : Sub) : finrank (ZMod 2) C + finrank (ZMod 2) (orth C) = 9 := by
  have h := dotForm.finrank_add_finrank_orthogonal' C
  have hker : LinearMap.ker dotForm = ⊥ := by
    rw [eq_bot_iff]
    intro x hx
    rw [Submodule.mem_bot]
    funext i
    have := congrArg (fun f => f (Pi.single i 1)) (LinearMap.mem_ker.mp hx)
    simp only [dotForm_apply, LinearMap.zero_apply] at this
    simpa [dotProduct_single] using this
  rw [show (dotForm.ker : Submodule (ZMod 2) V) = LinearMap.ker dotForm from rfl, hker, inf_bot_eq,
    finrank_bot, add_zero, Module.finrank_fin_fun] at h
  exact h

theorem orth_anti {C C' : Sub} (h : C' ≤ C) : orth C ≤ orth C' := by
  intro p hp
  rw [mem_orth] at hp ⊢
  exact fun x hx => hp x (h hx)

/-- An owned descent `C → C'` (`C' ≤ C`) costs exactly the growth of the dual. -/
theorem descent_cost_dual {C C' : Sub} (_h : C' ≤ C) :
    finrank (ZMod 2) C - finrank (ZMod 2) C' =
      finrank (ZMod 2) (orth C') - finrank (ZMod 2) (orth C) := by
  have := finrank_add_orth C
  have := finrank_add_orth C'
  omega

/-! ## The walk bound (Lemma S) -/

attribute [local instance] Classical.propDecidable

/-- Paid amount of step `k`: zero for a shrinking (free) step, the dimension growth otherwise. -/
noncomputable def cost (Z : ℕ → Sub) (par : ℕ → ℕ) (k : ℕ) : ℕ :=
  if Z k ≤ Z (par k) then 0 else finrank (ZMod 2) (Z k) - finrank (ZMod 2) (Z (par k))

/-- Union span of the first `n + 1` nodes. -/
def U (Z : ℕ → Sub) : ℕ → Sub
  | 0 => Z 0
  | n + 1 => U Z n ⊔ Z (n + 1)

theorem le_U (Z : ℕ → Sub) : ∀ {i n : ℕ}, i ≤ n → Z i ≤ U Z n
  | i, 0, h => by
    rw [Nat.le_zero.mp h]; exact le_rfl
  | i, n + 1, h => by
    rcases Nat.lt_or_eq_of_le h with h | h
    · exact le_trans (le_U Z (Nat.lt_succ_iff.mp h)) le_sup_left
    · rw [h]; exact le_sup_right

/-- **Walk bound.** If every step shrinks or grows its (earlier) parent, the union span of all visited dual subspaces
has dimension at most `dim Z 0` plus the total paid amount. -/
theorem union_bound (Z : ℕ → Sub) (par : ℕ → ℕ) (hpar : ∀ k, 0 < k → par k < k)
    (hstep : ∀ k, 0 < k → Z k ≤ Z (par k) ∨ Z (par k) ≤ Z k) :
    ∀ n, finrank (ZMod 2) (U Z n) ≤
      finrank (ZMod 2) (Z 0) + ∑ k ∈ Finset.Icc 1 n, cost Z par k
  | 0 => Nat.le_add_right _ _
  | n + 1 => by
    have ih := union_bound Z par hpar hstep n
    have hp : par (n + 1) ≤ n := Nat.lt_succ_iff.mp (hpar (n + 1) (Nat.succ_pos n))
    have hparU : Z (par (n + 1)) ≤ U Z n := le_U Z hp
    rw [Finset.sum_Icc_succ_top (by omega : 1 ≤ n + 1)]
    show finrank (ZMod 2) ((U Z n ⊔ Z (n + 1) : Sub)) ≤ _
    by_cases hfree : Z (n + 1) ≤ Z (par (n + 1))
    · have hc : cost Z par (n + 1) = 0 := by simp [cost, hfree]
      have : (U Z n ⊔ Z (n + 1) : Sub) = U Z n := sup_eq_left.mpr (le_trans hfree hparU)
      rw [this, hc]
      omega
    · have hgrow : Z (par (n + 1)) ≤ Z (n + 1) := (hstep (n + 1) (Nat.succ_pos n)).resolve_left hfree
      have hc : cost Z par (n + 1) =
          finrank (ZMod 2) (Z (n + 1)) - finrank (ZMod 2) (Z (par (n + 1))) := by simp [cost, hfree]
      have hmod := Submodule.finrank_sup_add_finrank_inf_eq (U Z n) (Z (n + 1))
      have hinf : finrank (ZMod 2) (Z (par (n + 1))) ≤ finrank (ZMod 2) ((U Z n ⊓ Z (n + 1) : Sub)) :=
        Submodule.finrank_mono (le_inf hparU hgrow)
      have hmono := Submodule.finrank_mono hgrow
      rw [hc]
      omega

/-- **Lemma S.** A walk starting at `Z 0` that visits, for every receiver vector `p ∈ R`, some node containing `p`
pays at least `dim (Z 0 ⊔ span R) - dim Z 0`.  With `Z 0 = (span S)^⊥` this is the binary rank of the pairing between
the receivers and the sources (`verify.py` checks the equality), so stops, branches, copies and relays through public
helpers never make one carrier cheaper than its COPY cost. -/
theorem lemma_S (Z : ℕ → Sub) (par : ℕ → ℕ) (hpar : ∀ k, 0 < k → par k < k)
    (hstep : ∀ k, 0 < k → Z k ≤ Z (par k) ∨ Z (par k) ≤ Z k) (n : ℕ) (R : Set V)
    (hR : ∀ p ∈ R, ∃ i ≤ n, p ∈ Z i) :
    finrank (ZMod 2) ((Z 0 ⊔ Submodule.span (ZMod 2) R : Sub)) ≤
      finrank (ZMod 2) (Z 0) + ∑ k ∈ Finset.Icc 1 n, cost Z par k := by
  have hle : Z 0 ⊔ Submodule.span (ZMod 2) R ≤ U Z n := by
    refine sup_le (le_U Z (Nat.zero_le n)) (Submodule.span_le.mpr ?_)
    intro p hp
    obtain ⟨i, hi, hpi⟩ := hR p hp
    exact le_U Z hi hpi
  exact le_trans (Submodule.finrank_mono hle) (union_bound Z par hpar hstep n)

/-! ## Lemma A: free additions along one path touch only free pairs -/

/-- If a port `pi` lies in a frame `C` and a receiver `pj` reads in a frame `C' ⊇ C` (so `pj ∈ C'^⊥`), the pair is
free: `pj · pi = 0`.  Hence content added at `C` from ports of `C` changes no costly pair of any receiver served higher
on the same path, and could have been loaded at the top. -/
theorem lemma_A {C C' : Sub} (h : C ≤ C') {pi pj : V} (hi : pi ∈ C) (hj : pj ∈ orth C') :
    pj ⬝ᵥ pi = 0 := by
  rw [mem_orth] at hj
  rw [dotProduct_comm]
  exact hj pi (h hi)

/-- Content form of Lemma A: an addition `f` supported on ports of `C` vanishes on every costly pair
(`port j · port i = 1`) of a receiver `j` reading in a frame containing `C`. -/
theorem lemma_A_rows {L K : Type*} [Zero K] (port : L → V) (f : L → K) {C C' : Sub} (h : C ≤ C')
    (hf : ∀ i, f i ≠ 0 → port i ∈ C) (j : L) (hj : port j ∈ orth C') (i : L)
    (hcost : port j ⬝ᵥ port i = 1) : f i = 0 := by
  by_contra hne
  have := lemma_A h (hf i hne) hj
  rw [this] at hcost
  exact zero_ne_one hcost

/-! ## Lemma M: merging carriers -/

/-- If the receivers `S` of a carrier lie in `Z ∪ T`, `G ≤ Z` and `G ⊔ span S = ⊤`, then `Z ⊔ T = ⊤`. -/
theorem sup_top_of_cover {Z T G : Sub} {S : Set V} (hS : ∀ p ∈ S, p ∈ Z ∨ p ∈ T) (hG : G ≤ Z)
    (htop : G ⊔ Submodule.span (ZMod 2) S = ⊤) : Z ⊔ T = ⊤ := by
  rw [eq_top_iff, ← htop]
  refine sup_le (le_trans hG le_sup_left) (Submodule.span_le.mpr ?_)
  intro p hp
  rcases hS p hp with h | h
  · exact (le_sup_left : Z ≤ Z ⊔ T) h
  · exact (le_sup_right : T ≤ Z ⊔ T) h

/-- Dimension count behind Lemma M: if `Z ⊔ T = ⊤` and `W ≤ Z ⊓ T` then `dim Z ≥ 9 - (dim T - dim W)`. -/
theorem path_dim {Z T W : Sub} (htop : Z ⊔ T = ⊤) (hW : W ≤ Z ⊓ T) :
    9 + finrank (ZMod 2) W ≤ finrank (ZMod 2) Z + finrank (ZMod 2) T := by
  have hmod := Submodule.finrank_sup_add_finrank_inf_eq Z T
  rw [htop, finrank_top, Module.finrank_fin_fun] at hmod
  have := Submodule.finrank_mono hW
  omega

/-- **Lemma M, general count.** Carriers `c ∈ Fin k` merge in a frame with dual `W`; path `c` has union span `Z c`
(from a line, so it pays at least `dim Z c - 1`), the common tail has union span `T ⊇ W` and pays at least
`dim T - dim W`.  If every carrier's content tree spans everything (`Z c ⊔ T = ⊤`), then
`total + (k - 1)·tail ≥ 8 k`.  Short tails therefore never beat `7 k`. -/
theorem merge_count (k : ℕ) (Z : Fin k → Sub) (T W : Sub) (hW : ∀ c, W ≤ Z c ⊓ T)
    (htop : ∀ c, Z c ⊔ T = ⊤) (pay : Fin k → ℕ) (hpay : ∀ c, finrank (ZMod 2) (Z c) ≤ pay c + 1)
    (tail : ℕ) (htail : finrank (ZMod 2) T ≤ tail + finrank (ZMod 2) W) :
    8 * k ≤ (∑ c, pay c) + tail + (k - 1) * tail := by
  have h : ∀ c, 8 ≤ pay c + tail := by
    intro c
    have := path_dim (htop c) (hW c)
    have := hpay c
    omega
  have hsum : ∑ _c : Fin k, 8 ≤ ∑ c, (pay c + tail) := Finset.sum_le_sum fun c _ => h c
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, smul_eq_mul,
    Finset.sum_add_distrib] at hsum
  rcases k with _ | k
  · simp
  · simp only [Nat.add_sub_cancel]
    nlinarith

/-- A receiver whose need is not proportional to the merged ratio must read some pure path. -/
theorem must_read_path {K : Type*} [Field K] {k : ℕ} (lam d : Fin k → K) (μ : K) (ν : Fin k → K)
    (hd : d = μ • lam + ν) (hnot : ∀ μ' : K, d ≠ μ' • lam) : ∃ c, ν c ≠ 0 := by
  by_contra h
  push Not at h
  apply hnot μ
  rw [hd]
  funext c
  simp [h c]

/-- **Lemma M for pairs.** Two carriers whose paths start on lines merge; the network pays
`pay a + pay b + tail` with the bounds of `merge_count`.  A network cheaper than 14 forces both path unions to have
dimension at most 6.  If no two subspaces containing `G`, each of dimension at most 6, cover the non-proportional
receivers `N` (the finite fact checked by `verify.py`), the merged network costs at least 14, the price of the two
separate carriers. -/
theorem pair_merge (Za Zb T W G : Sub) (hG : G ≤ W) (hWa : W ≤ Za ⊓ T) (hWb : W ≤ Zb ⊓ T)
    (hta : Za ⊔ T = ⊤) (htb : Zb ⊔ T = ⊤) (N : Set V) (hN : ∀ p ∈ N, p ∈ Za ∨ p ∈ Zb)
    (nocover : ∀ A B : Sub, G ≤ A → G ≤ B →
      finrank (ZMod 2) A ≤ 6 → finrank (ZMod 2) B ≤ 6 → ¬ ∀ p ∈ N, p ∈ A ∨ p ∈ B)
    (pa pb tail : ℕ) (hpa : finrank (ZMod 2) Za ≤ pa + 1) (hpb : finrank (ZMod 2) Zb ≤ pb + 1)
    (htail : finrank (ZMod 2) T ≤ tail + finrank (ZMod 2) W) :
    14 ≤ pa + pb + tail := by
  have h1 := path_dim hta hWa
  have h2 := path_dim htb hWb
  by_contra hlt
  have ha6 : finrank (ZMod 2) Za ≤ 6 := by omega
  have hb6 : finrank (ZMod 2) Zb ≤ 6 := by omega
  exact nocover Za Zb (le_trans hG (le_trans hWa inf_le_left)) (le_trans hG (le_trans hWb inf_le_left))
    ha6 hb6 hN

end NetCode
