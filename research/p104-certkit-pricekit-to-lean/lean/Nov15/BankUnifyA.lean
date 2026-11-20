/-
BankUnifyA (lane LEAN-UNIFY, Nov 19).  ONE tied layout covering BankBig (DescentLayout) and Theorem G (GLayout).
Kernel only.
  UPre                : a GROUP = zigzag descent route a_j ⊇ b_j, b_j ≤ a_{j+1}, β ≠ 0 (pure chain: a_{j+1} = b_j).
  ULayout G R Tr Tu Tz: groups R (zigzags incl. pure chains), trunks Tr (W-side DAGs, OrdW from the head chart a_0),
                        tails Tu (fresh-free; may branch at ANY step `att u r` of a group), free zero-relay chains Tz
                        (W1, arbitrary β, no trunk/tail), silent descents.  Deposits of EVERY group step may carry
                        trunk content (`dep`: inside the W hull), subject to `reasc`: a deposit at step j lies in the
                        output chart of every earlier gatherable step of that group; a mid-chain tail sees only
                        later deposits inside its own output chart (`ureasc`).  Gathers are read off G.
  UPre.carried_mul    : the piece-collapse lemma (zig_row generalised): carried_k · c = P_k · φ · c when later deposits
                        are killed by c.
  ULayout.core        : rank-8 hull facts per group + DECOUPLING  descMass G ≥ 56 + E_W + E_U.
-/
import Nov15.ThmGB

open Module Submodule Finset

namespace BankUnify
open DecoderWall ChainRow BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankTie
  BankPrem BankCallerGen BankBig ThmG

/-- a unified GROUP: a zigzag descent route with nonzero relays (deposits constrained in the layout). -/
structure UPre where
  a : ℕ → Ch
  b : ℕ → Ch
  b_le : ∀ j, b j ≤ a j
  route : ∀ j, b j ≤ a (j + 1)
  fresh : ℕ → Fin 104 → ℚ
  beta : ℕ → ℚ
  beta_ne : ∀ k, beta k ≠ 0

namespace UPre
variable (C : UPre)

def carried : ℕ → Fin 104 → ℚ
  | 0 => C.fresh 0
  | k + 1 => fun p => C.beta (k + 1) * carried k p + C.fresh (k + 1) p

def P (k : ℕ) : ℚ := ∏ i ∈ range (k + 1), C.beta i

theorem P_ne (k : ℕ) : C.P k ≠ 0 := prod_ne_zero_iff.2 fun i _ => C.beta_ne i

/-- the row's deposit vector over steps 0..n. -/
def phi (n : ℕ) (p : Fin 104) : ℚ := ∑ j ∈ range (n + 1), (C.P j)⁻¹ * C.fresh j p

theorem carried_eq (k : ℕ) (p : Fin 104) :
    C.carried k p = ∑ j ∈ range (k + 1), C.P k * (C.P j)⁻¹ * C.fresh j p := by
  induction k with
  | zero => simp [carried, C.P_ne 0]
  | succ k ih =>
    simp only [carried]
    rw [ih, sum_range_succ _ (k + 1), mul_sum]
    have hP : C.P (k + 1) = C.P k * C.beta (k + 1) := by
      simp only [P]; rw [prod_range_succ _ (k + 1)]
    rw [mul_inv_cancel₀ (C.P_ne (k + 1)), one_mul]
    congr 1
    refine sum_congr rfl fun j _ => ?_
    rw [hP]; ring

/-- **PIECE COLLAPSE.**  If every later deposit (k < j ≤ n) is killed by the coefficient c, the carried vector of
step k times c is the full row deposit times P_k c. -/
theorem carried_mul (n k : ℕ) (hk : k ≤ n) (p : Fin 104) (c : ℚ)
    (h : ∀ j, k < j → j ≤ n → C.fresh j p * c = 0) :
    C.carried k p * c = C.P k * C.phi n p * c := by
  rw [carried_eq, sum_mul, phi, mul_sum, sum_mul]
  have hsub : range (k + 1) ⊆ range (n + 1) := by
    intro j hj; simp only [mem_range] at *; omega
  refine Eq.trans ?_ (sum_subset hsub ?_)
  · exact sum_congr rfl fun j _ => by ring
  · intro j hj hj'
    simp only [mem_range, not_lt] at hj hj'
    have := h j (by omega) (by omega)
    calc C.P k * ((C.P j)⁻¹ * C.fresh j p) * c = C.P k * (C.P j)⁻¹ * (C.fresh j p * c) := by ring
      _ = 0 := by rw [this, mul_zero]

theorem phi_ne (n : ℕ) (p : Fin 104) (h : C.phi n p ≠ 0) : ∃ j ≤ n, C.fresh j p ≠ 0 := by
  obtain ⟨j, hj, hj'⟩ := exists_ne_zero_of_sum_ne_zero h
  exact ⟨j, by simp only [mem_range] at hj; omega, right_ne_zero_of_mul hj'⟩

noncomputable def mass (n : ℕ) : ℕ := ∑ j ∈ range (n + 1), (dm (C.a j) - dm (C.b j))

/-- potential lemma along the route (ChainRow.inf_drop). -/
theorem potential : ∀ n, dm (C.a 0) - dm (C.a 0 ⊓ C.b n) ≤ C.mass n
  | 0 => by simp only [mass, sum_range_one, inf_eq_right.2 (C.b_le 0)]; exact le_refl _
  | n + 1 => by
    have ih := potential n
    simp only [mass] at *
    rw [sum_range_succ]
    have h1 := inf_drop (C.a 0) (C.a (n + 1)) (C.b (n + 1)) (C.b_le (n + 1))
    have h2 : dm (C.a 0 ⊓ C.b n) ≤ dm (C.a 0 ⊓ C.a (n + 1)) :=
      Submodule.finrank_mono (inf_le_inf_left _ (C.route n))
    have h3 := Submodule.finrank_mono (C.b_le (n + 1))
    have h4 : dm (C.a 0 ⊓ C.b (n + 1)) ≤ dm (C.a 0) := Submodule.finrank_mono inf_le_left
    have h5 : dm (C.a 0 ⊓ C.b n) ≤ dm (C.a 0) := Submodule.finrank_mono inf_le_left
    simp only [dm] at *
    omega

end UPre

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- **THE UNIFIED TIED LAYOUT.** -/
structure ULayout (G : BankedGraph ℚ Fld Bank) (R Tr Tu Tz : Type) [Fintype R] [Fintype Tr] [Fintype Tu]
    [Fintype Tz] where
  xin : Fin 104 → Fld
  yout : Fin 104 → Fld
  -- groups (zigzags; pure chains are the case a (j+1) = b j)
  zl : R → ℕ
  grp : R → UPre
  eg : (Σ r : R, Fin (zl r + 1)) → Bank
  -- trunks, tails, free zero-relay chains
  eT : Tr → Bank
  eU : Tu → Bank
  zlen : Tz → ℕ
  zch : Tz → ZPre
  ez : (Σ c : Tz, Fin (zlen c)) → Bank
  inj : Function.Injective (Sum.elim eg (Sum.elim eT (Sum.elim eU ez)))
  gsrc : ∀ x : (Σ r : R, Fin (zl r + 1)), (grp x.1).a x.2 = G.N.src (eg x)
  gdst : ∀ x : (Σ r : R, Fin (zl r + 1)), (grp x.1).b x.2 = G.N.dst (eg x)
  gcar : ∀ (x : Σ r : R, Fin (zl r + 1)) p, (grp x.1).carried x.2 p = G.N.d (eg x) (xin p)
  zsrc : ∀ x : (Σ c : Tz, Fin (zlen c)), (zch x.1).ch x.2 = G.N.src (ez x)
  zdst : ∀ x : (Σ c : Tz, Fin (zlen c)), (zch x.1).ch ((x.2 : ℕ) + 1) = G.N.dst (ez x)
  zcar : ∀ (x : Σ c : Tz, Fin (zlen c)) p, (zch x.1).carried x.2 p = G.N.d (ez x) (xin p)
  -- W side: trunks folded into the group hull
  ancL : R → List Tr
  anc_nodup : ∀ r, (ancL r).Nodup
  anc_ord : ∀ r, OrdW (fun t => G.N.src (eT t)) (fun t => G.N.dst (eT t)) ((grp r).a 0) (ancL r)
  tdesc : ∀ t, G.N.dst (eT t) ≤ G.N.src (eT t)
  dep : ∀ r j p, j ≤ zl r → (grp r).fresh j p ≠ 0 →
    DF.lq p ∈ hullW (fun t => G.N.src (eT t)) ((grp r).a 0) (ancL r)
  reasc : ∀ r (k : Fin (zl r + 1)) j p, (k : ℕ) < j → j ≤ zl r → Gatherable G yout (eg ⟨r, k⟩) →
    (grp r).fresh j p ≠ 0 → DF.lq p ∈ (grp r).b k
  gath_ge : ∀ r (k : Fin (zl r + 1)), Gatherable G yout (eg ⟨r, k⟩) →
    (grp r).a 0 ⊓ (grp r).b (zl r) ≤ (grp r).b k
  -- U side: tails branching at step `att u r` of group r
  mu : Tu → R → ℚ
  att : Tu → R → ℕ
  att_le : ∀ u r, mu u r ≠ 0 → att u r ≤ zl r
  ucar : ∀ u p, G.N.d (eU u) (xin p) = ∑ r, mu u r * (grp r).carried (att u r) p
  ureasc : ∀ u r j p, mu u r ≠ 0 → Gatherable G yout (eU u) → att u r < j → j ≤ zl r →
    (grp r).fresh j p ≠ 0 → DF.lq p ∈ G.N.dst (eU u)
  tailL : R → List Tu
  tail_nodup : ∀ r, (tailL r).Nodup
  tail_mem : ∀ u r, mu u r ≠ 0 → u ∈ tailL r
  tail_ord : ∀ r, OrdU (fun u => G.N.src (eU u)) (fun u => G.N.dst (eU u)) ((grp r).a 0 ⊓ (grp r).b (zl r))
    (tailL r)
  udesc : ∀ u, G.N.dst (eU u) ≤ G.N.src (eU u)
  -- no bypass
  silent : ∀ k, ¬ G.N.src k ≤ G.N.dst k →
    (∃ x, eg x = k) ∨ (∃ u, eU u = k) ∨ (∃ x, ez x = k) ∨ (∀ p, G.N.d k (xin p) = 0) ∨ ¬ Gatherable G yout k

variable {G : BankedGraph ℚ Fld Bank} {R Tr Tu Tz : Type} [Fintype R] [Fintype Tr] [Fintype Tu] [Fintype Tz]
  [DecidableEq Tr] [DecidableEq Tu]

namespace ULayout
variable (Λ : ULayout G R Tr Tu Tz)

def sT (t : Tr) : Ch := G.N.src (Λ.eT t)
def tT (t : Tr) : Ch := G.N.dst (Λ.eT t)
def sU (u : Tu) : Ch := G.N.src (Λ.eU u)
def tU (u : Tu) : Ch := G.N.dst (Λ.eU u)
def hd (r : R) : Ch := (Λ.grp r).a 0
def en (r : R) : Ch := (Λ.grp r).a 0 ⊓ (Λ.grp r).b (Λ.zl r)
def hW (r : R) : Ch := hullW Λ.sT (Λ.hd r) (Λ.ancL r)
def hU (r : R) : Ch := hullU Λ.tU (Λ.en r) (Λ.tailL r)
noncomputable def dTr (t : Tr) : ℕ := dm (Λ.sT t) - dm (Λ.tT t)
noncomputable def dTu (u : Tu) : ℕ := dm (Λ.sU u) - dm (Λ.tU u)
noncomputable def mG (r : R) : ℕ := (Λ.grp r).mass (Λ.zl r)
/-- pure pieces: free W1 chains with their inner zero relays, plus groups. -/
noncomputable def pieces : ℕ := ∑ c, ((Λ.zch c).zc (Λ.zlen c) + 1) + Fintype.card R

theorem inj3 : Function.Injective (Sum.elim Λ.eg (Sum.elim Λ.eU Λ.ez)) := by
  have e : Sum.elim Λ.eg (Sum.elim Λ.eU Λ.ez) =
      Sum.elim Λ.eg (Sum.elim Λ.eT (Sum.elim Λ.eU Λ.ez)) ∘ Sum.map id Sum.inr := by
    funext x; rcases x with x | x | x <;> rfl
  rw [e]
  exact Λ.inj.comp (Sum.map_injective.2 ⟨Function.injective_id, Sum.inr_injective⟩)

open Classical in
/-- **CORE.**  Folding groups (with trunks / tails) and flattening the free W1 chains gives an 8-row decoder;
per group the W hull has dim ≥ 8 and the U hull dim ≤ 1; and descMass G ≥ 56 + E_W + E_U. -/
theorem core (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Λ.pieces ≤ 8) :
    (∀ r, 8 ≤ dm (Λ.hW r) ∧ dm (Λ.hU r) ≤ 1) ∧
    56 + ((∑ t, (Λ.dTr t : ℤ)) - ∑ r, dW (Λ.hd r)) + ((∑ u, (Λ.dTu u : ℤ)) - ∑ r, dU (Λ.en r)) ≤
      descMass G := by
  obtain ⟨γ, hγ, hsplit⟩ := BankMed.last_descent_split G.N Λ.xin Λ.yout hin hout
  have hγL : ∀ s k, γ (Λ.yout s) k ≠ 0 → ∀ y ∈ G.N.dst k, dot (DF.lq s) y = 0 := fun s k h y hy =>
    hout s y ((hγ _ k h).2 hy)
  have hγG : ∀ s k, γ (Λ.yout s) k ≠ 0 → Gatherable G Λ.yout k := fun s k h => ⟨s, (hγ _ k h).2⟩
  -- a nonzero gather kills every deposit lying in its bank's output chart (odd pair)
  have kill : ∀ p s k, dot (DF.lq p) (DF.lq s) = 1 → γ (Λ.yout s) k ≠ 0 → DF.lq p ∈ G.N.dst k → False := by
    intro p s k hps hk hm
    have h0 := hγL s k hk (DF.lq p) hm
    rw [show dot (DF.lq s) (DF.lq p) = dot (DF.lq p) (DF.lq s) from dotProduct_comm _ _, hps] at h0
    exact one_ne_zero h0
  -- free W1 chains, gathered by γ
  let zg : ∀ c : Tz, ℕ → Fin 104 → ℚ := fun c k s =>
    if h : k < Λ.zlen c then γ (Λ.yout s) (Λ.ez ⟨c, ⟨k, h⟩⟩) else 0
  have hzg : ∀ c k s, zg c k s ≠ 0 → ∀ y ∈ (Λ.zch c).ch (k + 1), dot (DF.lq s) y = 0 := by
    intro c k s hne y hy
    by_cases h : k < Λ.zlen c
    · simp only [zg, dif_pos h] at hne
      exact hγL s _ hne y (by rw [← Λ.zdst ⟨c, ⟨k, h⟩⟩]; exact hy)
    · simp only [zg, dif_neg h] at hne; exact absurd rfl hne
  let Z : ZLayout ℚ DF.lq Tz := ⟨Λ.zlen, fun c => (Λ.zch c).toZ (zg c) (hzg c)⟩
  have hZb : ∀ p s, Z.block p s =
      ∑ x : (Σ c : Tz, Fin (Λ.zlen c)), G.N.d (Λ.ez x) (Λ.xin p) * γ (Λ.yout s) (Λ.ez x) := by
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
  obtain ⟨T1, i1, L1, hc1, hb1, hm1⟩ := Z.exists_flat
  -- group rows
  let Φ : Fin 104 → R → ℚ := fun p r => (Λ.grp r).phi (Λ.zl r) p
  let Γ : Fin 104 → R → ℚ := fun s r =>
    ∑ k : Fin (Λ.zl r + 1), (Λ.grp r).P k * γ (Λ.yout s) (Λ.eg ⟨r, k⟩) +
      ∑ u, Λ.mu u r * (Λ.grp r).P (Λ.att u r) * γ (Λ.yout s) (Λ.eU u)
  let W : Fin 104 → T1 ⊕ R → ℚ := fun p => Sum.elim (L1.W p) (Φ p)
  let U : Fin 104 → T1 ⊕ R → ℚ := fun s => Sum.elim (L1.U s) (Γ s)
  let E3 := Sum.elim Λ.eg (Sum.elim Λ.eU Λ.ez)
  have hodd : ∀ p s, dot (DF.lq p) (DF.lq s) = 1 → G.N.O (Λ.yout s) (Λ.xin p) = ∑ r, W p r * U s r := by
    intro p s hps
    rw [hsplit p s hps]
    have hsub : ∑ k ∈ univ.image E3, G.N.d k (Λ.xin p) * γ (Λ.yout s) k =
        ∑ k, G.N.d k (Λ.xin p) * γ (Λ.yout s) k := by
      refine sum_subset (subset_univ _) fun k _ hk => ?_
      by_cases hγk : γ (Λ.yout s) k = 0
      · rw [hγk, mul_zero]
      · have hd := hγ _ k hγk
        rcases Λ.silent k hd.1 with ⟨x, hx⟩ | ⟨u, hu⟩ | ⟨x, hx⟩ | h0 | hng
        · exact absurd (mem_image.2 ⟨Sum.inl x, mem_univ _, hx⟩) hk
        · exact absurd (mem_image.2 ⟨Sum.inr (Sum.inl u), mem_univ _, hu⟩) hk
        · exact absurd (mem_image.2 ⟨Sum.inr (Sum.inr x), mem_univ _, hx⟩) hk
        · rw [h0 p, zero_mul]
        · exact absurd ⟨s, hd.2⟩ hng
    rw [← hsub, sum_image fun x _ y _ h => Λ.inj3 h, Fintype.sum_sum_type, Fintype.sum_sum_type]
    simp only [Sum.elim_inl, Sum.elim_inr]
    -- group part
    have hgrp : ∑ x : (Σ r : R, Fin (Λ.zl r + 1)), G.N.d (Λ.eg x) (Λ.xin p) * γ (Λ.yout s) (Λ.eg x) =
        ∑ r, Φ p r * ∑ k : Fin (Λ.zl r + 1), (Λ.grp r).P k * γ (Λ.yout s) (Λ.eg ⟨r, k⟩) := by
      rw [Fintype.sum_sigma]
      refine sum_congr rfl fun r _ => ?_
      rw [mul_sum]
      refine sum_congr rfl fun k _ => ?_
      rw [← Λ.gcar ⟨r, k⟩ p]
      rw [(Λ.grp r).carried_mul (Λ.zl r) k (Nat.lt_succ_iff.1 k.2) p _ fun j hkj hjn => ?_]
      · simp only [Φ]; ring
      · by_contra hne
        have hg := right_ne_zero_of_mul hne
        have hm := Λ.reasc r k j p hkj hjn (hγG s _ hg) (left_ne_zero_of_mul hne)
        rw [Λ.gdst ⟨r, k⟩] at hm
        exact kill p s _ hps hg hm
    -- tail part
    have htail : ∑ u, G.N.d (Λ.eU u) (Λ.xin p) * γ (Λ.yout s) (Λ.eU u) =
        ∑ r, Φ p r * ∑ u, Λ.mu u r * (Λ.grp r).P (Λ.att u r) * γ (Λ.yout s) (Λ.eU u) := by
      simp only [Λ.ucar, sum_mul, mul_sum]
      rw [sum_comm]
      refine sum_congr rfl fun r _ => sum_congr rfl fun u _ => ?_
      by_cases hm : Λ.mu u r = 0
      · rw [hm]; ring
      · rw [mul_assoc, (Λ.grp r).carried_mul (Λ.zl r) (Λ.att u r) (Λ.att_le u r hm) p _ fun j hj hjn => ?_]
        · simp only [Φ]; ring
        · by_contra hne
          have hg := right_ne_zero_of_mul hne
          exact kill p s _ hps hg (Λ.ureasc u r j p hm (hγG s _ hg) hj hjn (left_ne_zero_of_mul hne))
    -- W1 part
    have hz : ∑ x : (Σ c : Tz, Fin (Λ.zlen c)), G.N.d (Λ.ez x) (Λ.xin p) * γ (Λ.yout s) (Λ.ez x) =
        ∑ c, L1.W p c * L1.U s c := by
      rw [← hZb, ← hb1, L1.block_eq hps]
    rw [hgrp, htail, hz, Fintype.sum_sum_type]
    simp only [W, U, Sum.elim_inl, Sum.elim_inr, Γ, mul_add, sum_add_distrib]
    ring
  -- the decoder
  let Cg : Fin 104 → T1 ⊕ R → ℚ := fun s r => (cs s)⁻¹ * U s r
  have hd : IsDecoder DF.lq W Cg :=
    { diag := fun t => by
        have h := hodd t t (lq_odd t)
        rw [(hC.1 t).2] at h
        simp only [Cg, mul_left_comm (W t _), ← mul_sum, ← h]
        exact inv_mul_cancel₀ (hC.1 t).1
      odd := fun t s hts h => by
        have h2 := hodd t s h
        rw [hC.2 t s hts h] at h2
        simp only [Cg, mul_left_comm (W t _), ← mul_sum, ← h2, mul_zero] }
  have hcardle : Fintype.card (T1 ⊕ R) ≤ 8 := by
    rw [Fintype.card_sum]
    have : Z.pieces = ∑ c, ((Λ.zch c).zc (Λ.zlen c) + 1) := rfl
    have hp : Λ.pieces = ∑ c, ((Λ.zch c).zc (Λ.zlen c) + 1) + Fintype.card R := rfl
    omega
  have hcard : Fintype.card (T1 ⊕ R) = 8 := le_antisymm hcardle (DF.decoder_rows_ge_eight W Cg hd)
  -- per-row rank facts
  have hrow : ∀ r, 8 ≤ dm (Λ.hW r) ∧ dm (Λ.hU r) ≤ 1 := by
    intro r
    refine ⟨dep_hull_ge_8 W Cg hd hcard (Sum.inr r) _ fun p hp => ?_,
      gat_hull_le_1 W Cg hd hcard (Sum.inr r) _ fun s hs y hy => ?_⟩
    · obtain ⟨j, hj, hf⟩ := (Λ.grp r).phi_ne _ p hp
      exact Λ.dep r j p hj hf
    · have hΓ : Γ s r ≠ 0 := right_ne_zero_of_mul hs
      have hyen : y ∈ Λ.en r := hullU_le _ _ _ hy
      rcases (show (∑ k : Fin (Λ.zl r + 1), (Λ.grp r).P k * γ (Λ.yout s) (Λ.eg ⟨r, k⟩)) ≠ 0 ∨
          (∑ u, Λ.mu u r * (Λ.grp r).P (Λ.att u r) * γ (Λ.yout s) (Λ.eU u)) ≠ 0 by
        by_contra hc; push_neg at hc; exact hΓ (by simp only [Γ, hc.1, hc.2, add_zero])) with h1 | h1
      · obtain ⟨k, -, hk'⟩ := exists_ne_zero_of_sum_ne_zero h1
        have hne := right_ne_zero_of_mul hk'
        refine hγL s _ hne y ?_
        rw [← Λ.gdst ⟨r, k⟩]
        exact Λ.gath_ge r k (hγG s _ hne) hyen
      · obtain ⟨u, -, hu⟩ := exists_ne_zero_of_sum_ne_zero h1
        have hγu := right_ne_zero_of_mul hu
        have hmu : Λ.mu u r ≠ 0 := left_ne_zero_of_mul (left_ne_zero_of_mul hu)
        exact hγL s _ hγu y (hullU_le_mem _ _ _ _ (Λ.tail_mem u r hmu) hy)
  have hL1 : ∀ c, 7 ≤ (L1.chain c).descentMass := by
    intro c
    have h1 := dep_hull_ge_8 W Cg hd hcard (Sum.inl c) ((L1.chain c).ch 0) fun p hp =>
      (L1.chain c).phi_supp p hp
    have h2 := gat_hull_le_1 W Cg hd hcard (Sum.inl c) ((L1.chain c).ch (L1.len c)) fun s hs =>
      (L1.chain c).cv_supp s (right_ne_zero_of_mul hs)
    have h3 := (L1.chain c).drop_le_descentMass
    simp only [dm] at h1 h2
    omega
  refine ⟨hrow, ?_⟩
  -- fold bounds and mass accounting
  have hgm : ∀ r, (7 : ℤ) - dW (Λ.hd r) - dU (Λ.en r) ≤ Λ.mG r := by
    intro r
    have hp := (Λ.grp r).potential (Λ.zl r)
    have hle : dm ((Λ.grp r).a 0 ⊓ (Λ.grp r).b (Λ.zl r)) ≤ dm ((Λ.grp r).a 0) :=
      Submodule.finrank_mono inf_le_left
    show (7 : ℤ) - (8 - (dm ((Λ.grp r).a 0) : ℤ)) - ((dm ((Λ.grp r).a 0 ⊓ (Λ.grp r).b (Λ.zl r)) : ℤ) - 1) ≤
      ((Λ.grp r).mass (Λ.zl r) : ℤ)
    omega
  set f : Bank → ℤ := fun k => max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0 with hf
  have hg : ∑ r, (Λ.mG r : ℤ) = ∑ x : (Σ r : R, Fin (Λ.zl r + 1)), f (Λ.eg x) := by
    rw [Fintype.sum_sigma]
    refine sum_congr rfl fun r _ => ?_
    simp only [mG, UPre.mass]; push_cast
    rw [← Fin.sum_univ_eq_sum_range]
    refine sum_congr rfl fun j _ => ?_
    rw [term_eq]
    show max ((dm ((Λ.grp r).a j) : ℤ) - dm ((Λ.grp r).b j)) 0 = _
    rw [Λ.gsrc ⟨r, j⟩, Λ.gdst ⟨r, j⟩]
  have ht' : ∀ t, (Λ.dTr t : ℤ) = f (Λ.eT t) := fun t => by
    simp only [dTr, sT, tT]; rw [term_eq]
  have hu' : ∀ u, (Λ.dTu u : ℤ) = f (Λ.eU u) := fun u => by
    simp only [dTu, sU, tU]; rw [term_eq]
  have hZm : (Z.descentMass : ℤ) = ∑ x : (Σ c : Tz, Fin (Λ.zlen c)), f (Λ.ez x) := by
    simp only [ZLayout.descentMass, ZData.descentMass, Z]
    rw [Fintype.sum_sigma]; push_cast
    refine Finset.sum_congr rfl fun c _ => ?_
    rw [← sum_fin_range_z]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [term_eq]
    show max ((finrank (ZMod 2) ((Λ.zch c).ch j) : ℤ) - finrank (ZMod 2) ((Λ.zch c).ch (j + 1))) 0 = _
    rw [Λ.zsrc ⟨c, j⟩, Λ.zdst ⟨c, j⟩]
  have hacct : ∑ r, (Λ.mG r : ℤ) + ∑ t, (Λ.dTr t : ℤ) + ∑ u, (Λ.dTu u : ℤ) + (Z.descentMass : ℤ) ≤
      descMass G := by
    simp only [ht', hu', hg, hZm]
    have e4 : ∑ x : (Σ r : R, Fin (Λ.zl r + 1)), f (Λ.eg x) + ∑ t, f (Λ.eT t) + ∑ u, f (Λ.eU u) +
        ∑ x : (Σ c : Tz, Fin (Λ.zlen c)), f (Λ.ez x) =
        ∑ x, f (Sum.elim Λ.eg (Sum.elim Λ.eT (Sum.elim Λ.eU Λ.ez)) x) := by
      rw [Fintype.sum_sum_type, Fintype.sum_sum_type, Fintype.sum_sum_type]
      simp only [Sum.elim_inl, Sum.elim_inr]; ring
    rw [e4, ← sum_image (f := f) fun x _ y _ h => Λ.inj h]
    exact sum_le_sum_of_subset_of_nonneg (subset_univ _) fun k _ _ => le_max_right _ _
  have hZ7 : 7 * (Fintype.card T1 : ℤ) ≤ Z.descentMass := by
    rw [← hm1]
    simp only [ChainLayout.descentMass]; push_cast
    have := Finset.sum_le_sum fun c (_ : c ∈ (univ : Finset T1)) => (show (7 : ℤ) ≤ (L1.chain c).descentMass
      by exact_mod_cast hL1 c)
    simpa [mul_comm] using this
  have hR7 : 7 * (Fintype.card R : ℤ) - ∑ r, dW (Λ.hd r) - ∑ r, dU (Λ.en r) ≤ ∑ r, (Λ.mG r : ℤ) := by
    have := Finset.sum_le_sum fun r (_ : r ∈ (univ : Finset R)) => hgm r
    simp only [sum_sub_distrib, sum_const, card_univ, nsmul_eq_mul] at this
    linarith
  have hc8 : (Fintype.card T1 : ℤ) + Fintype.card R = 8 := by
    rw [Fintype.card_sum] at hcard; exact_mod_cast hcard
  linarith

/-- FOLD bounds (both sides). -/
theorem fold_bounds (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Λ.pieces ≤ 8) (r : R) :
    dW (Λ.hd r) ≤ ∑ t ∈ (Λ.ancL r).toFinset, (Λ.dTr t : ℤ) ∧
      dU (Λ.en r) ≤ ∑ u ∈ (Λ.tailL r).toFinset, (Λ.dTu u : ℤ) := by
  obtain ⟨hw, hu⟩ := (Λ.core cs hC hin hout h8).1 r
  have fw := fold_W Λ.sT Λ.tT Λ.tdesc (Λ.ancL r) (Λ.hd r) (Λ.anc_ord r)
  have fu := fold_U Λ.sU Λ.tU Λ.udesc (Λ.tailL r) (Λ.en r) (Λ.tail_ord r)
  have ew : (dropL Λ.sT Λ.tT (Λ.ancL r) : ℤ) = ∑ t ∈ (Λ.ancL r).toFinset, (Λ.dTr t : ℤ) := by
    rw [List.sum_toFinset _ (Λ.anc_nodup r), dropL]; push_cast; rw [List.map_map]; rfl
  have eu : (dropL Λ.sU Λ.tU (Λ.tailL r) : ℤ) = ∑ u ∈ (Λ.tailL r).toFinset, (Λ.dTu u : ℤ) := by
    rw [List.sum_toFinset _ (Λ.tail_nodup r), dropL]; push_cast; rw [List.map_map]; rfl
  have hw' : 8 ≤ dm (hullW Λ.sT (Λ.hd r) (Λ.ancL r)) := hw
  have hu' : dm (hullU Λ.tU (Λ.en r) (Λ.tailL r)) ≤ 1 := hu
  constructor
  · rw [← ew]; simp only [dW]; omega
  · rw [← eu]; simp only [dU]; omega

end ULayout
end BankUnify

#print axioms BankUnify.UPre.carried_mul
#print axioms BankUnify.UPre.potential
#print axioms BankUnify.ULayout.core
#print axioms BankUnify.ULayout.fold_bounds
