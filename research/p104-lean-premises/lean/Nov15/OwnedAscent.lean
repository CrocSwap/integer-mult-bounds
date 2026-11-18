/-
OwnedAscent (lane LEAN-PREM2, Nov 17). Premise 6 (A6 "owned ascent"): cost symmetry, no credit,
conservativity of the relaxed legality over the strict one. See OwnedAscent.md.
-/
import Nov15.FloorEndToEnd

open Finset Module Submodule

namespace OwnedAscent
open FloorE2E

/-! ## 1. Cost symmetry -/

section Rank
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- rank cost of a chart change `T` : the rank of the residual `T - 1`. -/
noncomputable def rc (T : V →ₗ[K] V) : ℕ := Module.finrank K (LinearMap.range (T - LinearMap.id))

/-- the inverse of a chart change has the same rank cost: a rise and a fall cost the same. -/
theorem rc_inv (T : V ≃ₗ[K] V) : rc (T.symm : V →ₗ[K] V) = rc (T : V →ₗ[K] V) := by
  unfold rc
  have h : LinearMap.range ((T.symm : V →ₗ[K] V) - LinearMap.id) =
      Submodule.map (T.symm : V →ₗ[K] V) (LinearMap.range ((T : V →ₗ[K] V) - LinearMap.id)) := by
    ext x
    simp only [LinearMap.mem_range, Submodule.mem_map, LinearMap.sub_apply, LinearEquiv.coe_coe,
      LinearMap.id_apply]
    constructor
    · rintro ⟨v, rfl⟩
      exact ⟨T (-v) - (-v), ⟨-v, by simp⟩, by simp; abel⟩
    · rintro ⟨y, ⟨v, rfl⟩, rfl⟩
      exact ⟨-v, by simp; abel⟩
  rw [h]
  exact (T.symm.finrank_map_eq _)


/-- subadditivity: composing chart changes costs at most the sum. -/
theorem rc_comp (A B : V →ₗ[K] V) :
    rc (A ∘ₗ B) ≤ rc A + rc B := by
  unfold rc
  have h : LinearMap.range (A ∘ₗ B - LinearMap.id) ≤
      Submodule.map A (LinearMap.range (B - LinearMap.id)) ⊔ LinearMap.range (A - LinearMap.id) := by
    rintro x ⟨v, rfl⟩
    refine Submodule.mem_sup.2 ⟨A (B v - v), ⟨_, ⟨v, rfl⟩, rfl⟩, A v - v, ⟨v, rfl⟩, ?_⟩
    simp
  refine (Submodule.finrank_mono h).trans
    ((Submodule.finrank_add_le_finrank_add_finrank _ _).trans ?_)
  rw [Nat.add_comm (Module.finrank K (LinearMap.range (A - LinearMap.id)))]
  exact add_le_add (Submodule.finrank_map_le _ _) le_rfl

end Rank


/-- direction-free price: if the compiled rank of every nested chart change is `|dim b - dim a|`
(the paper's hypothesis, checked by `lowerup.py` on 2964 pairs; NOT derived here), the price of a
move `a → b` equals that of `b → a`. -/
theorem price_symm {C : Type*} (dim : C → ℤ) (a b : C) : |dim b - dim a| = |dim a - dim b| :=
  abs_sub_comm _ _

section Rank2
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
/-- if the chart change `a → b` is the invertible `T` with rank cost `|dim b - dim a|`, then the
chart change back is `T⁻¹`, and its rank cost is the same number, with no further hypothesis. -/
theorem back_cost (T : V ≃ₗ[K] V) (r : ℕ) (h : rc (T : V →ₗ[K] V) = r) :
    rc (T.symm : V →ₗ[K] V) = r := by rw [rc_inv, h]
end Rank2

/-! ## 2. No credit (the pricer: paid = Σ|Δdim| over all moves; credit only from public endpoints) -/

variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- charge of one event: a MOVE pays `|Δdim|` whether public or owned, all else is rank 0. -/
def mvCost (dim : C → ℤ) (s : GSt K Reg C) : GEv K Reg C → ℤ
  | .move r c => match s.loc r with | some a => |dim c - dim a| | none => 0
  | _ => 0

/-- the owned share of the charge. -/
def ownCost (Pub : Finset Reg) (dim : C → ℤ) (s : GSt K Reg C) : GEv K Reg C → ℤ
  | .move r c => if r ∈ Pub then 0 else mvCost dim s (.move r c)
  | _ => 0

/-- the public share of the charge. -/
def pubCost (Pub : Finset Reg) (dim : C → ℤ) (s : GSt K Reg C) : GEv K Reg C → ℤ
  | .move r c => if r ∈ Pub then mvCost dim s (.move r c) else 0
  | _ => 0

/-- owned ascent charge: `max(Δdim, 0)` of owned moves (what the strict verifier forces to 0). -/
def ownAsc (Pub : Finset Reg) (dim : C → ℤ) (s : GSt K Reg C) : GEv K Reg C → ℤ
  | .move r c => if r ∈ Pub then 0 else match s.loc r with | some a => max (dim c - dim a) 0 | none => 0
  | _ => 0

/-- sum of a per-event charge along a run. -/
def sumFrom (f : GSt K Reg C → GEv K Reg C → ℤ) : GSt K Reg C → List (GEv K Reg C) → ℤ
  | _, [] => 0
  | s, e :: es => f s e + sumFrom f (gstep s e) es

theorem sumFrom_add (f g : GSt K Reg C → GEv K Reg C → ℤ) :
    ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
      sumFrom (fun s e => f s e + g s e) s w = sumFrom f s w + sumFrom g s w
  | _, [] => by simp [sumFrom]
  | s, e :: es => by simp only [sumFrom, sumFrom_add f g (gstep s e) es]; ring

/-- the charge splits into public and owned parts: an owned move is charged exactly like a public
one, nothing cheaper. -/
theorem cost_split (Pub : Finset Reg) (dim : C → ℤ) (s : GSt K Reg C) (w : List (GEv K Reg C)) :
    sumFrom (mvCost dim) s w = sumFrom (pubCost Pub dim) s w + sumFrom (ownCost Pub dim) s w := by
  rw [← sumFrom_add]
  congr 1; funext s e
  cases e <;> simp [pubCost, ownCost, mvCost]
  split_ifs <;> simp

theorem ownCost_nonneg (Pub : Finset Reg) (dim : C → ℤ) (s : GSt K Reg C) (e : GEv K Reg C) :
    0 ≤ ownCost Pub dim s e := by
  cases e <;> simp [ownCost, mvCost]
  split_ifs <;> first | exact le_rfl | skip
  all_goals (split <;> simp)

theorem sumFrom_nonneg (f : GSt K Reg C → GEv K Reg C → ℤ) (hf : ∀ s e, 0 ≤ f s e) :
    ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)), 0 ≤ sumFrom f s w
  | _, [] => by simp [sumFrom]
  | s, e :: es => by simp only [sumFrom]; exact add_nonneg (hf _ _) (sumFrom_nonneg f hf _ _)

/-- the owned part of the invoice is never negative: owned moves (ascending or descending) never
lower the price. -/
theorem ownedCost_nonneg (Pub : Finset Reg) (dim : C → ℤ) (s : GSt K Reg C)
    (w : List (GEv K Reg C)) : 0 ≤ sumFrom (ownCost Pub dim) s w :=
  sumFrom_nonneg _ (ownCost_nonneg Pub dim) s w

/-- credit as the pricer takes it: only public registers, only from endpoint dimensions. -/
def credit (Pub : Finset Reg) (dim : C → ℤ) (ini fin : Reg → Option C) (r : Reg) : ℤ :=
  if r ∈ Pub then
    (match fin r with | some b => dim b | none => 0) - (match ini r with | some a => dim a | none => 0)
  else 0

/-- an owned register earns no credit, whatever its path (ascending or descending). -/
theorem owned_no_credit (Pub : Finset Reg) (dim : C → ℤ) (ini fin : Reg → Option C) (r : Reg)
    (h : r ∉ Pub) : credit Pub dim ini fin r = 0 := by simp [credit, h]

/-- invoice = public paid + owned paid - credit over helpers; credit is summed over helpers only
(`H ⊆ Pub`), so owned registers contribute nothing to it. -/
def invoice (Pub H : Finset Reg) (dim : C → ℤ) (ini fin : Reg → Option C) (s : GSt K Reg C)
    (w : List (GEv K Reg C)) : ℤ :=
  sumFrom (mvCost dim) s w - ∑ r ∈ H, credit Pub dim ini fin r

theorem invoice_eq (Pub H : Finset Reg) (dim : C → ℤ) (ini fin : Reg → Option C) (s : GSt K Reg C)
    (w : List (GEv K Reg C)) :
    invoice Pub H dim ini fin s w =
      (sumFrom (pubCost Pub dim) s w - ∑ r ∈ H, credit Pub dim ini fin r)
        + sumFrom (ownCost Pub dim) s w := by
  unfold invoice; rw [cost_split Pub]; ring

/-- an owned ascent is charged at least 1 (never free, never negative), given strict-monotone dim. -/
theorem owned_ascent_charged (Pub : Finset Reg) (dim : C → ℤ) (hd : StrictMono dim)
    (s : GSt K Reg C) (r : Reg) (c : C) (hr : r ∉ Pub) (a : C) (ha : s.loc r = some a) (hlt : a < c) :
    1 ≤ ownCost Pub dim s (.move r c) := by
  have := hd hlt
  simp [ownCost, mvCost, hr, ha]
  have := abs_of_pos (sub_pos.2 this)
  omega

/-! ## 3. Conservativity -/

/-- the STRICT verifier: public moves climb, owned moves DESCEND (`frames[b] < frames[a]`). -/
def LegalEvS (Pub : Finset Reg) (s : GSt K Reg C) : GEv K Reg C → Prop
  | .move r c => ∃ a, s.loc r = some a ∧ (r ∈ Pub → a < c) ∧ (r ∉ Pub → c < a)
  | e => LegalEvG Pub s e

def LegalS (Pub : Finset Reg) : GSt K Reg C → List (GEv K Reg C) → Prop
  | _, [] => True
  | s, e :: es => LegalEvS Pub s e ∧ LegalS Pub (gstep s e) es

theorem legalEv_of_S (Pub : Finset Reg) (s : GSt K Reg C) (e : GEv K Reg C) (h : LegalEvS Pub s e) :
    LegalEvG Pub s e := by
  cases e with
  | move r c =>
    obtain ⟨a, ha, h1, h2⟩ := h
    exact ⟨a, ha, h1, fun hr => Or.inr (h2 hr)⟩
  | _ => exact h

/-- every strict-legal word is relaxed-legal. -/
theorem legal_of_S (Pub : Finset Reg) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
    LegalS Pub s w → LegalG Pub s w
  | _, [], _ => trivial
  | s, e :: es, ⟨h1, h2⟩ => ⟨legalEv_of_S Pub s e h1, legal_of_S Pub _ es h2⟩

/-- the two predicates agree on everything but owned ascents. -/
theorem legal_diff (Pub : Finset Reg) (s : GSt K Reg C) (e : GEv K Reg C)
    (hG : LegalEvG Pub s e) (hS : ¬ LegalEvS Pub s e) :
    ∃ r c a, e = .move r c ∧ r ∉ Pub ∧ s.loc r = some a ∧ a < c := by
  cases e with
  | move r c =>
    obtain ⟨a, ha, h1, h2⟩ := hG
    by_cases hr : r ∈ Pub
    · exact absurd ⟨a, ha, h1, fun h => absurd hr h⟩ hS
    · rcases h2 hr with h | h
      · exact ⟨r, c, a, rfl, hr, ha, h⟩
      · exact absurd ⟨a, ha, fun h => absurd h hr, fun _ => h⟩ hS
  | _ => exact absurd hG hS

/-- public-side legality is untouched by the relaxation. -/
theorem public_unchanged (Pub : Finset Reg) (s : GSt K Reg C) (r : Reg) (c : C) (hr : r ∈ Pub) :
    LegalEvS Pub s (.move r c) ↔ LegalEvG Pub s (.move r c) := by
  constructor
  · exact legalEv_of_S Pub s _
  · rintro ⟨a, ha, h1, -⟩; exact ⟨a, ha, h1, fun h => absurd hr h⟩

/-- acceptance by the strict verifier. -/
structure AcceptedS (Pub H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) : Prop where
  legal : LegalS Pub (s0 ini) w
  pub_ini : ∀ r, r ∈ Pub ↔ ini r ≠ none
  helpers_pub : H ⊆ Pub
  helper_final : ∀ h ∈ H, (grun (s0 ini) w).row h = Pi.single h 1

/-- strict acceptance implies relaxed acceptance: EVERY theorem of FloorEndToEnd (stated for
`Accepted`, the relaxed class) holds for strict words. So a floor proved on the relaxed class is
a floor for the strict class too. -/
theorem AcceptedS.toAccepted {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}
    (h : AcceptedS Pub H ini w) : Accepted Pub H ini w :=
  ⟨legal_of_S Pub _ w h.legal, h.pub_ini, h.helpers_pub, h.helper_final⟩

/-- sample transfer: hOnce for strict words, from the relaxed theorem. -/
theorem hOnce_strict {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}
    (h : AcceptedS Pub H ini w) (c : C) (r : Reg) (hr : r ∈ Pub) (hini : ini r ≠ none) :
    ExportLaw.nEnt {r} (proj c ini w) ≤ 1 :=
  hOnce_proj Pub c ini w (legal_of_S Pub _ w h.legal) r hr hini

/-- under strict legality owned ascents do not occur: their ascent charge is 0. This is the
property the strict-only floors (owned-paid-56 etc.) rest on. -/
theorem strict_no_owned_asc (Pub : Finset Reg) (dim : C → ℤ) (hd : StrictMono dim) :
    ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)), LegalS Pub s w → sumFrom (ownAsc Pub dim) s w = 0
  | _, [], _ => by simp [sumFrom]
  | s, e :: es, ⟨h1, h2⟩ => by
    simp only [sumFrom, strict_no_owned_asc Pub dim hd _ es h2, add_zero]
    cases e with
    | move r c =>
      obtain ⟨a, ha, -, h⟩ := h1
      by_cases hr : r ∈ Pub
      · simp [ownAsc, hr]
      · have := hd (h hr)
        simp [ownAsc, hr, ha]; omega
    | _ => simp [ownAsc]

/-! ### The relaxation is strictly larger (counterexample to "strict = relaxed") -/

abbrev W1 : List (GEv ℚ (Fin 1) Bool) := [.init 0 false, .move 0 true]

def dimB : Bool → ℤ := fun b => if b then 1 else 0

theorem W1_relaxed : LegalG (∅ : Finset (Fin 1)) (s0 (fun _ => (none : Option Bool))) W1 := by
  simp [W1, LegalG, LegalEvG, gstep, s0]

theorem W1_not_strict : ¬ LegalS (∅ : Finset (Fin 1)) (s0 (fun _ => (none : Option Bool))) W1 := by
  simp [W1, LegalS, LegalEvS, LegalEvG, gstep, s0]

/-- the relaxed class prices an owned ascent: charge 1 and ascent charge 1 on `W1`; the strict
verifier forbids it, so floors resting on `strict_no_owned_asc` do NOT transfer to the relaxed class. -/
theorem W1_charge : sumFrom (mvCost dimB) (s0 (fun _ => (none : Option Bool))) W1 = 1 ∧
    sumFrom (ownAsc (∅ : Finset (Fin 1)) dimB) (s0 (fun _ => (none : Option Bool))) W1 = 1 := by
  simp [W1, sumFrom, mvCost, ownAsc, gstep, s0, dimB]


#print axioms rc_inv
#print axioms rc_comp
#print axioms back_cost
#print axioms cost_split
#print axioms ownedCost_nonneg
#print axioms owned_no_credit
#print axioms invoice_eq
#print axioms owned_ascent_charged
#print axioms legal_of_S
#print axioms legal_diff
#print axioms public_unchanged
#print axioms AcceptedS.toAccepted
#print axioms hOnce_strict
#print axioms strict_no_owned_asc
#print axioms W1_relaxed
#print axioms W1_not_strict
#print axioms W1_charge

end OwnedAscent
