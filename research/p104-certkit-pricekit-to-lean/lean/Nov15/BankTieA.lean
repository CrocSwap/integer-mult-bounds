/-
BankTieA (lane LEAN-TIE, Nov 18).  Fixes AUDIT-BANNERLEAN (2a): the chain layout is tied to the banked graph G (over ℚ).
  ChainTie G T : a ChainRow layout whose every chain step x = ⟨c, j⟩ IS a bank e x of G (e injective), with
                 chart j = G.N.src (e x), chart j+1 = G.N.dst (e x) (so the steps are G's descents), and whose carried
                 vector at step x is G's own bank form on the input fields: carried j p = G.N.d (e x) (xin p).
  layout_desc_le  : LEMMA (was premise hLD)  layout descent mass ≤ descMass G.
  Computes G xin yout : G's output matrix N.O realises the P104 pattern on (yout s, xin p): diag 1, 0 on odd off-diag.
  Mediated τ    : THE named premise (BD §1 last-descent split / CE1-ALT): on odd pairs, N.O (yout s) (xin p) equals the
                  descent-mediated part Σ_x G.N.d (e x) (xin p) · gath_x s  (gathers legal: support ⊥ G.N.dst (e x)).
  realises       : Computes ∧ Mediated ⟹ τ.L.Realises   (LEMMA).
  tie_desc_ge_56 : ≤ 8 chains + Computes + Mediated ⟹ 56 ≤ descMass G.
Kernel only.
-/
import Nov15.BankBannerXBal
import Nov15.ChainRowB

namespace BankTie
open Finset Module BankNC0 BankHelp BankFit SafeRungsPrice BankFitHS BankBanner DecoderWall

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- a chain layout extracted from G: chain steps are injectively banks of G, with G's charts and G's bank forms. -/
structure ChainTie (G : BankedGraph ℚ Fld Bank) (T : Type) [Fintype T] where
  L : ChainRow.ChainLayout ℚ DF.lq T
  e : (Σ c : T, Fin (L.len c)) → Bank
  inj : Function.Injective e
  hsrc : ∀ x : (Σ c : T, Fin (L.len c)), (L.chain x.1).ch (x.2 : ℕ) = G.N.src (e x)
  hdst : ∀ x : (Σ c : T, Fin (L.len c)), (L.chain x.1).ch ((x.2 : ℕ) + 1) = G.N.dst (e x)
  xin : Fin 104 → Fld
  yout : Fin 104 → Fld
  hcar : ∀ (x : Σ c : T, Fin (L.len c)) (p : Fin 104), (L.chain x.1).carried (x.2 : ℕ) p = G.N.d (e x) (xin p)

/-- G's output matrix realises the live P104 pattern on input fields xin / output fields yout. -/
def Computes (G : BankedGraph ℚ Fld Bank) (xin yout : Fin 104 → Fld) : Prop :=
  (∀ t, G.N.O (yout t) (xin t) = 1) ∧
  ∀ t s, t ≠ s → dot (DF.lq t) (DF.lq s) = 1 → G.N.O (yout s) (xin t) = 0

variable {G : BankedGraph ℚ Fld Bank} {T : Type} [Fintype T]

/-- **the one named premise**: on odd pairs G's output is mediated by its chain descents (BD §1 / CE1-ALT). -/
def Mediated (τ : ChainTie G T) : Prop :=
  ∀ p s, dot (DF.lq p) (DF.lq s) = 1 →
    G.N.O (τ.yout s) (τ.xin p) = ∑ x : (Σ c : T, Fin (τ.L.len c)), G.N.d (τ.e x) (τ.xin p) * (τ.L.chain x.1).gath x.2 s

/-- the layout block, rewritten through G's bank forms. -/
theorem block_eq_G (τ : ChainTie G T) (p s : Fin 104) :
    τ.L.block p s = ∑ x : (Σ c : T, Fin (τ.L.len c)), G.N.d (τ.e x) (τ.xin p) * (τ.L.chain x.1).gath x.2 s := by
  unfold ChainRow.ChainLayout.block ChainRow.RelayChain.block
  rw [Fintype.sum_sigma]
  refine Finset.sum_congr rfl fun c _ => ?_
  rw [← Fin.sum_univ_eq_sum_range (fun k => (τ.L.chain c).carried k p * (τ.L.chain c).gath k s)]
  refine Finset.sum_congr rfl fun j _ => ?_
  rw [τ.hcar ⟨c, j⟩ p]

theorem realises (τ : ChainTie G T) (hC : Computes G τ.xin τ.yout) (hM : Mediated τ) : τ.L.Realises where
  diag := fun t => by rw [block_eq_G, ← hM t t (ChainRow.lq_odd t)]; exact hC.1 t
  odd := fun t s hts h => by rw [block_eq_G, ← hM t s h]; exact hC.2 t s hts h

theorem term_eq (a b : ℕ) : (((a - b : ℕ)) : ℤ) = max ((a : ℤ) - b) 0 := by
  rcases le_total a b with h | h
  · rw [max_eq_right (by omega)]; omega
  · rw [max_eq_left (by omega)]; omega

/-- **hLD as a lemma**: the tied layout's descent mass is at most G's descent mass. -/
theorem layout_desc_le (τ : ChainTie G T) : (τ.L.descentMass : ℤ) ≤ descMass G := by
  classical
  set f : Bank → ℤ := fun k => max ((ht (G.N.src k) : ℤ) - ht (G.N.dst k)) 0 with hf
  have h1 : (τ.L.descentMass : ℤ) = ∑ x : (Σ c : T, Fin (τ.L.len c)), f (τ.e x) := by
    unfold ChainRow.ChainLayout.descentMass ChainRow.RelayChain.descentMass
    rw [Fintype.sum_sigma]
    push_cast
    refine Finset.sum_congr rfl fun c _ => ?_
    rw [← Fin.sum_univ_eq_sum_range]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [term_eq, τ.hsrc ⟨c, j⟩, τ.hdst ⟨c, j⟩]
  have h2 : ∑ x : (Σ c : T, Fin (τ.L.len c)), f (τ.e x) = ∑ k ∈ univ.image τ.e, f k :=
    (Finset.sum_image fun x _ y _ h => τ.inj h).symm
  have h3 : ∑ k ∈ univ.image τ.e, f k ≤ ∑ k, f k :=
    Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ _) fun k _ _ => le_max_right _ _
  rw [h1, h2]; exact h3

/-- **D ≥ 56 from G itself**: ≤ 8 tied chains, G computes the pattern, its odd part is chain-mediated. -/
theorem tie_desc_ge_56 (τ : ChainTie G T) (h8 : Fintype.card T ≤ 8) (hC : Computes G τ.xin τ.yout)
    (hM : Mediated τ) : 56 ≤ descMass G := by
  have := ChainRow.chain_mass_ge_56 τ.L (realises τ hC hM) h8
  have : (56 : ℤ) ≤ (τ.L.descentMass : ℤ) := by exact_mod_cast this
  have := layout_desc_le τ
  linarith

end BankTie
#print axioms BankTie.layout_desc_le
#print axioms BankTie.realises
#print axioms BankTie.tie_desc_ge_56
