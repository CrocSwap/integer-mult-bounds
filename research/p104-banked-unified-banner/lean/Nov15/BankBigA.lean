/-
BankBigA.  GENERAL DECODER-MASS FLOOR over a banked graph G (kernel only).
  DescentLayout G T U : a layout TIED to G covering the five Theorem-W shapes at once (and their mixtures):
    * live relay chains with ARBITRARY β (zero relays split; ChainRowW1)  -- pure chains = all β ≠ 0 (ChainRowA/B),
    * contained zigzags (ChainRowW2) whose reasc / gath_ge side conditions are stated for every GATHERABLE step
      (a bank delivering into some output chart B (yout s)), so they hold for any legal regathering,
    * SILENT descents: every other descent bank of G is either input-dead (d k (xin p) = 0 ∀ p: fresh-free trunks,
      ChainRowW3 (b)) or not gatherable (no output chart contains its target: gather-free tails, ChainRowW3 (c)).
    Every step is an injective bank e x of G with G's charts and carried vector = G.N.d (e x) (xin ·); gathers are NOT
    data: they are read off G by BankMed.last_descent_split (Net semantics + chart locality).
  layout_mass_ge_56 : ComputesS + locality + pieces ≤ 8  ⟹  56 ≤ descMass G
    (dispatch: W1 flattening ZLayout.exists_flat, W2 ZigLayout.toLayout, ChainRowB.chain_mass_ge_56).
  silent_of_trunk   : a tied fresh-free trunk is input-dead (so W3 (b) trunks are silent descents).
-/
import Nov15.BankMedA
import Nov15.ChainRowW2
import Nov15.ChainRowW3

namespace BankBig
open Finset Module Submodule BankNC0 BankHelp BankFit SafeRungsPrice BankFitHS BankBanner DecoderWall BankWireC
  BankTie ChainRow

/-- a zero-relay chain without gathers (gathers are read off G). -/
structure ZPre where
  ch : ℕ → Submodule (ZMod 2) (Fin 9 → ZMod 2)
  desc : ∀ j, ch (j + 1) ≤ ch j
  fresh : ℕ → Fin 104 → ℚ
  fresh_supp : ∀ j p, fresh j p ≠ 0 → DF.lq p ∈ ch j
  beta : ℕ → ℚ

namespace ZPre
variable (P : ZPre)

def carried : ℕ → Fin 104 → ℚ
  | 0 => P.fresh 0
  | k + 1 => fun p => P.beta (k + 1) * carried k p + P.fresh (k + 1) p

def toZ (g : ℕ → Fin 104 → ℚ) (hg : ∀ k s, g k s ≠ 0 → ∀ y ∈ P.ch (k + 1), dot (DF.lq s) y = 0) :
    ZData ℚ DF.lq where
  ch := P.ch
  desc := P.desc
  fresh := P.fresh
  fresh_supp := P.fresh_supp
  gath := g
  gath_supp := hg
  beta := P.beta

theorem toZ_carried (g) (hg) : ∀ k, (P.toZ g hg).carried k = P.carried k
  | 0 => rfl
  | k + 1 => by
    funext p
    show P.beta (k + 1) * (P.toZ g hg).carried k p + P.fresh (k + 1) p = _
    rw [toZ_carried g hg k]; rfl

/-- number of inner zero relays (pieces − 1) of the first m steps. -/
noncomputable def zc (m : ℕ) : ℕ := (P.toZ (fun _ _ => 0) (fun _ _ h => absurd rfl h)).zc m

theorem toZ_zc (g) (hg) (m : ℕ) : (P.toZ g hg).zc m = P.zc m := rfl

end ZPre

/-- a contained zigzag without gathers. -/
structure ZigPre (n : ℕ) where
  a : ℕ → Submodule (ZMod 2) (Fin 9 → ZMod 2)
  b : ℕ → Submodule (ZMod 2) (Fin 9 → ZMod 2)
  b_le : ∀ j, b j ≤ a j
  route : ∀ j, b j ≤ a (j + 1)
  fresh : ℕ → Fin 104 → ℚ
  fresh_supp : ∀ j p, fresh j p ≠ 0 → DF.lq p ∈ a j
  beta : ℕ → ℚ
  beta_ne : ∀ k, beta k ≠ 0
  fresh_in : ∀ j p, fresh j p ≠ 0 → DF.lq p ∈ a 0

namespace ZigPre
variable {n : ℕ} (P : ZigPre n)

def carried : ℕ → Fin 104 → ℚ
  | 0 => P.fresh 0
  | k + 1 => fun p => P.beta (k + 1) * carried k p + P.fresh (k + 1) p

end ZigPre

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- bank k delivers into some output chart (only such banks can carry a legal gather). -/
def Gatherable (G : BankedGraph ℚ Fld Bank) (yout : Fin 104 → Fld) (k : Bank) : Prop :=
  ∃ s, G.N.dst k ≤ G.N.B (yout s)

/-- **the general tied descent layout** (five Theorem-W shapes and their mixtures). -/
structure DescentLayout (G : BankedGraph ℚ Fld Bank) (T U : Type) [Fintype T] [Fintype U] where
  xin : Fin 104 → Fld
  yout : Fin 104 → Fld
  len : T → ℕ
  zch : T → ZPre
  zl : U → ℕ
  zg : ∀ u, ZigPre (zl u)
  e : (Σ c : T, Fin (len c)) ⊕ (Σ u : U, Fin (zl u + 1)) → Bank
  inj : Function.Injective e
  zsrc : ∀ x : (Σ c : T, Fin (len c)), (zch x.1).ch x.2 = G.N.src (e (Sum.inl x))
  zdst : ∀ x : (Σ c : T, Fin (len c)), (zch x.1).ch ((x.2 : ℕ) + 1) = G.N.dst (e (Sum.inl x))
  zcar : ∀ (x : Σ c : T, Fin (len c)) p, (zch x.1).carried x.2 p = G.N.d (e (Sum.inl x)) (xin p)
  gsrc : ∀ x : (Σ u : U, Fin (zl u + 1)), (zg x.1).a x.2 = G.N.src (e (Sum.inr x))
  gdst : ∀ x : (Σ u : U, Fin (zl u + 1)), (zg x.1).b x.2 = G.N.dst (e (Sum.inr x))
  gcar : ∀ (x : Σ u : U, Fin (zl u + 1)) p, (zg x.1).carried x.2 p = G.N.d (e (Sum.inr x)) (xin p)
  reasc : ∀ u (k : Fin (zl u + 1)) j, (k : ℕ) < j → Gatherable G yout (e (Sum.inr ⟨u, k⟩)) →
    (∃ p, (zg u).fresh j p ≠ 0) → (zg u).a j ≤ (zg u).b k
  gath_ge : ∀ u (k : Fin (zl u + 1)), Gatherable G yout (e (Sum.inr ⟨u, k⟩)) →
    (zg u).a 0 ⊓ (zg u).b (zl u) ≤ (zg u).b k
  silent : ∀ k, ¬ G.N.src k ≤ G.N.dst k →
    (∃ x, e x = k) ∨ (∀ p, G.N.d k (xin p) = 0) ∨ ¬ Gatherable G yout k

variable {G : BankedGraph ℚ Fld Bank} {T U : Type} [Fintype T] [Fintype U]

namespace DescentLayout
variable (Λ : DescentLayout G T U)

/-- pure pieces: chains + inner zero relays + zigzags. -/
noncomputable def pieces : ℕ := ∑ c, ((Λ.zch c).zc (Λ.len c) + 1) + Fintype.card U

end DescentLayout

/-! ## proof of the floor -/

theorem sum_fin_range {m : ℕ} (F : ℕ → ℚ) : ∑ j : Fin m, F j = ∑ j ∈ range m, F j :=
  Fin.sum_univ_eq_sum_range F m

theorem sum_fin_range_z {m : ℕ} (F : ℕ → ℤ) : ∑ j : Fin m, F j = ∑ j ∈ range m, F j :=
  Fin.sum_univ_eq_sum_range F m

/-- **GENERAL DECODER-MASS FLOOR.** -/
theorem layout_mass_ge_56 (Λ : DescentLayout G T U) (cs : Fin 104 → ℚ)
    (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Λ.pieces ≤ 8) : 56 ≤ descMass G := by
  classical
  obtain ⟨γ, hγ, hsplit⟩ := BankMed.last_descent_split G.N Λ.xin Λ.yout hin hout
  set g : Fin 104 → Bank → ℚ := fun s k => (cs s)⁻¹ * γ (Λ.yout s) k with hgdef
  have hgG : ∀ s k, g s k ≠ 0 → Gatherable G Λ.yout k := fun s k h =>
    ⟨s, (hγ _ k (right_ne_zero_of_mul h)).2⟩
  have hgL : ∀ s k, g s k ≠ 0 → ∀ y ∈ G.N.dst k, dot (DF.lq s) y = 0 := fun s k h y hy =>
    hout s y ((hγ _ k (right_ne_zero_of_mul h)).2 hy)
  -- live zero-relay chains, regathered
  let zg : ∀ c : T, ℕ → Fin 104 → ℚ := fun c k s =>
    if h : k < Λ.len c then g s (Λ.e (Sum.inl ⟨c, ⟨k, h⟩⟩)) else 0
  have hzg : ∀ c k s, zg c k s ≠ 0 → ∀ y ∈ (Λ.zch c).ch (k + 1), dot (DF.lq s) y = 0 := by
    intro c k s hne y hy
    by_cases h : k < Λ.len c
    · simp only [zg, dif_pos h] at hne
      exact hgL s _ hne y (by rw [← Λ.zdst ⟨c, ⟨k, h⟩⟩]; exact hy)
    · simp only [zg, dif_neg h] at hne; exact absurd rfl hne
  let Z : ZLayout ℚ DF.lq T := ⟨Λ.len, fun c => (Λ.zch c).toZ (zg c) (hzg c)⟩
  -- zigzags, regathered
  let yg : ∀ u : U, ℕ → Fin 104 → ℚ := fun u k s =>
    if h : k < Λ.zl u + 1 then g s (Λ.e (Sum.inr ⟨u, ⟨k, h⟩⟩)) else 0
  have hyg : ∀ u k s, yg u k s ≠ 0 → ∃ h : k < Λ.zl u + 1, Gatherable G Λ.yout (Λ.e (Sum.inr ⟨u, ⟨k, h⟩⟩)) ∧
      ∀ y ∈ (Λ.zg u).b k, dot (DF.lq s) y = 0 := by
    intro u k s hne
    by_cases h : k < Λ.zl u + 1
    · simp only [yg, dif_pos h] at hne
      exact ⟨h, hgG s _ hne, fun y hy => hgL s _ hne y (by rw [← Λ.gdst ⟨u, ⟨k, h⟩⟩]; exact hy)⟩
    · simp only [yg, dif_neg h] at hne; exact absurd rfl hne
  let zig : ∀ u : U, ZigChain ℚ DF.lq (Λ.zl u) := fun u =>
    { a := (Λ.zg u).a, b := (Λ.zg u).b, b_le := (Λ.zg u).b_le, route := (Λ.zg u).route,
      fresh := (Λ.zg u).fresh, fresh_supp := (Λ.zg u).fresh_supp,
      gath := yg u
      gath_supp := fun k s hs => (hyg u k s hs).2.2
      beta := (Λ.zg u).beta, beta_ne := (Λ.zg u).beta_ne
      reasc := fun k j hkj ⟨s, hs⟩ hf => by
        obtain ⟨h, hG, -⟩ := hyg u k s hs
        exact Λ.reasc u ⟨k, h⟩ j hkj hG hf
      fresh_in := (Λ.zg u).fresh_in
      gath_ge := fun k ⟨s, hs⟩ => by
        obtain ⟨h, hG, -⟩ := hyg u k s hs
        exact Λ.gath_ge u ⟨k, h⟩ hG }
  let Y : ZigLayout ℚ DF.lq U := ⟨Λ.zl, zig⟩
  have zig_car : ∀ u k, (zig u).carried k = (Λ.zg u).carried k := by
    intro u k
    induction k with
    | zero => rfl
    | succ k ih =>
      funext p
      show (Λ.zg u).beta (k + 1) * (zig u).carried k p + (Λ.zg u).fresh (k + 1) p = _
      rw [ih]; rfl
  -- block identities
  have hZb : ∀ p s, Z.block p s =
      ∑ x : (Σ c : T, Fin (Λ.len c)), G.N.d (Λ.e (Sum.inl x)) (Λ.xin p) * g s (Λ.e (Sum.inl x)) := by
    intro p s
    simp only [ZLayout.block, ZData.block, Z]
    rw [Fintype.sum_sigma]
    refine Finset.sum_congr rfl fun c _ => ?_
    rw [← sum_fin_range (fun k => ((Λ.zch c).toZ (zg c) (hzg c)).carried k p *
      ((Λ.zch c).toZ (zg c) (hzg c)).gath k s)]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [ZPre.toZ_carried, Λ.zcar ⟨c, j⟩ p]
    show _ * zg c j s = _
    simp only [zg, dif_pos j.2, Fin.eta]
  have hYb : ∀ p s, Y.block p s =
      ∑ x : (Σ u : U, Fin (Λ.zl u + 1)), G.N.d (Λ.e (Sum.inr x)) (Λ.xin p) * g s (Λ.e (Sum.inr x)) := by
    intro p s
    simp only [ZigLayout.block, ZigChain.block, Y]
    rw [Fintype.sum_sigma]
    refine Finset.sum_congr rfl fun u _ => ?_
    rw [← sum_fin_range (fun k => (zig u).carried k p * (zig u).gath k s)]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [zig_car, Λ.gcar ⟨u, j⟩ p]
    simp only [zig, yg, dif_pos j.2, Fin.eta]
  -- mediation: odd cells of O are cs s · (Z.block + Y.block)
  have hmed : ∀ p s, dot (DF.lq p) (DF.lq s) = 1 →
      G.N.O (Λ.yout s) (Λ.xin p) = cs s * (Z.block p s + Y.block p s) := by
    intro p s hps
    rw [hsplit p s hps, hZb, hYb, ← Fintype.sum_sum_type
      (f := fun x => G.N.d (Λ.e x) (Λ.xin p) * g s (Λ.e x))]
    have hsub : ∑ k ∈ univ.image Λ.e, G.N.d k (Λ.xin p) * γ (Λ.yout s) k =
        ∑ k, G.N.d k (Λ.xin p) * γ (Λ.yout s) k := by
      refine Finset.sum_subset (Finset.subset_univ _) fun k _ hk => ?_
      by_cases hγk : γ (Λ.yout s) k = 0
      · rw [hγk, mul_zero]
      · have hd := (hγ _ k hγk)
        rcases Λ.silent k hd.1 with ⟨x, hx⟩ | h0 | hng
        · exact absurd (Finset.mem_image.2 ⟨x, Finset.mem_univ _, hx⟩) hk
        · rw [h0 p, zero_mul]
        · exact absurd ⟨s, hd.2⟩ hng
    rw [← hsub, Finset.sum_image fun x _ y _ h => Λ.inj h, Finset.mul_sum]
    refine Finset.sum_congr rfl fun x _ => ?_
    simp only [hgdef]
    rw [mul_left_comm (cs s), mul_inv_cancel_left₀ ((hC.1 s).1)]
  -- flatten and combine into one pure ChainLayout
  obtain ⟨T1, i1, L1, hc1, hb1, hm1⟩ := Z.exists_flat
  let L2 := Y.toLayout
  let L : ChainLayout ℚ DF.lq (T1 ⊕ U) :=
    { len := Sum.elim L1.len L2.len
      chain := fun c => Sum.rec (motive := fun c => RelayChain ℚ DF.lq (Sum.elim L1.len L2.len c))
        (fun c => L1.chain c) (fun c => L2.chain c) c }
  have hLb : ∀ p s, dot (DF.lq p) (DF.lq s) = 1 → L.block p s = Z.block p s + Y.block p s := by
    intro p s h
    have : L.block p s = L1.block p s + L2.block p s := by
      simp only [ChainLayout.block, Fintype.sum_sum_type]; rfl
    rw [this, hb1, Y.toLayout_block h]
  have hR : L.Realises :=
    { diag := fun t => by
        rw [hLb t t (lq_odd t)]
        have h := hmed t t (lq_odd t)
        rw [(hC.1 t).2] at h
        exact mul_left_cancel₀ (hC.1 t).1 (by rw [mul_one]; exact h.symm)
      odd := fun t s hts h => by
        rw [hLb t s h]
        have h2 := hmed t s h
        rw [hC.2 t s hts h] at h2
        exact (mul_eq_zero.1 h2.symm).resolve_left (hC.1 s).1 }
  have hcard : Fintype.card (T1 ⊕ U) ≤ 8 := by
    rw [Fintype.card_sum]
    have : Z.pieces = ∑ c, ((Λ.zch c).zc (Λ.len c) + 1) := rfl
    have hp : Λ.pieces = ∑ c, ((Λ.zch c).zc (Λ.len c) + 1) + Fintype.card U := rfl
    omega
  have h56 := chain_mass_ge_56 L hR hcard
  -- mass accounting
  have hLm : L.descentMass ≤ Z.descentMass + Y.descentMass := by
    have : L.descentMass = L1.descentMass + L2.descentMass := by
      simp only [ChainLayout.descentMass, Fintype.sum_sum_type]; rfl
    rw [this, hm1]; exact Nat.add_le_add_left Y.toLayout_mass _
  set f : Bank → ℤ := fun k => max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0 with hf
  have hZm : (Z.descentMass : ℤ) = ∑ x : (Σ c : T, Fin (Λ.len c)), f (Λ.e (Sum.inl x)) := by
    simp only [ZLayout.descentMass, ZData.descentMass, Z]
    rw [Fintype.sum_sigma]; push_cast
    refine Finset.sum_congr rfl fun c _ => ?_
    rw [← sum_fin_range_z]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [term_eq]
    show max ((finrank (ZMod 2) ((Λ.zch c).ch j) : ℤ) - finrank (ZMod 2) ((Λ.zch c).ch (j + 1))) 0 = _
    rw [Λ.zsrc ⟨c, j⟩, Λ.zdst ⟨c, j⟩]
  have hYm : (Y.descentMass : ℤ) = ∑ x : (Σ u : U, Fin (Λ.zl u + 1)), f (Λ.e (Sum.inr x)) := by
    simp only [ZigLayout.descentMass, ZigChain.descentMass, Y]
    rw [Fintype.sum_sigma]; push_cast
    refine Finset.sum_congr rfl fun u _ => ?_
    rw [← sum_fin_range_z]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [term_eq]
    show max ((finrank (ZMod 2) ((Λ.zg u).a j) : ℤ) - finrank (ZMod 2) ((Λ.zg u).b j)) 0 = _
    rw [Λ.gsrc ⟨u, j⟩, Λ.gdst ⟨u, j⟩]
  have hsum : (Z.descentMass : ℤ) + Y.descentMass ≤ descMass G := by
    rw [hZm, hYm, ← Fintype.sum_sum_type (f := fun x => f (Λ.e x)),
      ← Finset.sum_image (f := f) fun x _ y _ h => Λ.inj h]
    exact Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ _) fun k _ _ => le_max_right _ _
  have : (56 : ℤ) ≤ L.descentMass := by exact_mod_cast h56
  have : (L.descentMass : ℤ) ≤ Z.descentMass + Y.descentMass := by exact_mod_cast hLm
  linarith

/-- W3 (b): a tied fresh-free trunk (carried = d on inputs) is input-dead, i.e. a silent descent. -/
theorem silent_of_trunk (P : ZPre) {t : ℕ} (hfree : ∀ j, j < t → ∀ p, P.fresh j p = 0)
    (xin : Fin 104 → Fld) (eb : ℕ → Bank) (hcar : ∀ j, j < t → ∀ p, P.carried j p = G.N.d (eb j) (xin p)) :
    ∀ j, j < t → ∀ p, G.N.d (eb j) (xin p) = 0 := by
  intro j hj p
  rw [← hcar j hj p, ← P.toZ_carried (fun _ _ => 0) (fun _ _ h => absurd rfl h)]
  exact ZData.carried_eq_zero _ hfree j hj p

end BankBig
#print axioms BankBig.layout_mass_ge_56
#print axioms BankBig.silent_of_trunk
