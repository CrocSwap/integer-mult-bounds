/- Publication snapshot: actual bank endpoints and conditional finite arithmetic only. -/
import Mathlib.LinearAlgebra.Prod
import Mathlib.Tactic.Abel
import Mathlib.Algebra.BigOperators.Group.List.Defs
import Mathlib.Data.List.Pairwise
import Mathlib.Data.List.FinRange
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum


/-! Exact partial bit address interchanges for split-projector bank packing.
No supplier, routing, recurrence, precision, or tape theorem is assumed here. -/
namespace Mathproof.BeyondNLogN.TakeoverBit

variable {R V : Type*} [CommRing R] [AddCommGroup V] [Module R V]

/-- Exchange the P-address component between two arbitrary incoming banks. -/
def partialSwap (P : V →ₗ[R] V) : (V × V) →ₗ[R] (V × V) where
  toFun z := (z.1 - P z.1 + P z.2, z.2 - P z.2 + P z.1)
  map_add' a b := by
    apply Prod.ext <;> simp only [Prod.fst_add, Prod.snd_add, map_add] <;> abel
  map_smul' r z := by
    apply Prod.ext <;> simp only [Prod.smul_fst, Prod.smul_snd, map_smul,
      RingHom.id_apply, smul_add, smul_sub]

@[simp] theorem partialSwap_apply (P : V →ₗ[R] V) (z : V × V) :
    partialSwap P z = (z.1 - P z.1 + P z.2, z.2 - P z.2 + P z.1) := rfl

@[simp] theorem partialSwap_zero : partialSwap (0 : V →ₗ[R] V) = LinearMap.id := by
  apply LinearMap.ext
  intro z
  simp

/-- Every disjoint projector pair composes by adding its exchanged components.
The incoming pair is arbitrary, so correlated dirty contents are included. -/
theorem partialSwap_comp_disjoint (P Q : V →ₗ[R] V)
    (hPQ : P.comp Q = 0) (hQP : Q.comp P = 0) :
    (partialSwap P).comp (partialSwap Q) = partialSwap (P + Q) := by
  have hpq (z : V) : P (Q z) = 0 := by
    simpa using LinearMap.congr_fun hPQ z
  have hqp (z : V) : Q (P z) = 0 := by
    simpa using LinearMap.congr_fun hQP z
  apply LinearMap.ext
  intro z
  rcases z with ⟨x,y⟩
  apply Prod.ext <;>
    simp only [LinearMap.comp_apply, partialSwap_apply, map_add, map_sub,
      LinearMap.add_apply, hpq] <;> abel

/-- A completed split-projector core is its own exact inverse. -/
theorem partialSwap_involutive (P : V →ₗ[R] V) (hP : P.comp P = P) :
    Function.Involutive (partialSwap P) := by
  have hpp (z : V) : P (P z) = P z := by
    simpa using LinearMap.congr_fun hP z
  intro z
  rcases z with ⟨x,y⟩
  apply Prod.ext <;> simp only [partialSwap_apply, map_add, map_sub, hpp] <;> abel

@[simp] theorem partialSwap_id (z : V × V) :
    partialSwap (LinearMap.id : V →ₗ[R] V) z = (z.2,z.1) := by
  simp

/-- Split-projector factors commute at the actual address-map level. -/
theorem partialSwap_commute (P Q : V →ₗ[R] V)
    (hPQ : P.comp Q = 0) (hQP : Q.comp P = 0) :
    (partialSwap P).comp (partialSwap Q) =
      (partialSwap Q).comp (partialSwap P) := by
  rw [partialSwap_comp_disjoint P Q hPQ hQP,
    partialSwap_comp_disjoint Q P hQP hPQ, add_comm]




/-- Execute completed cores in any explicit chronological bank schedule. -/
def bankSwap : List (V →ₗ[R] V) → ((V × V) →ₗ[R] (V × V))
  | [] => LinearMap.id
  | P :: Ps => (partialSwap P).comp (bankSwap Ps)

private theorem comp_sum_zero (P : V →ₗ[R] V) (Ps : List (V →ₗ[R] V))
    (h : ∀ Q ∈ Ps, P.comp Q = 0) : P.comp Ps.sum = 0 := by
  induction Ps with
  | nil => simp
  | cons Q Ps ih =>
    have hQ := h Q (by simp)
    have ht : ∀ A ∈ Ps, P.comp A = 0 := fun A hA => h A (by simp [hA])
    simp only [List.sum_cons, LinearMap.comp_add, hQ, ih ht, zero_add]

private theorem sum_comp_zero (P : V →ₗ[R] V) (Ps : List (V →ₗ[R] V))
    (h : ∀ Q ∈ Ps, Q.comp P = 0) : Ps.sum.comp P = 0 := by
  induction Ps with
  | nil => simp
  | cons Q Ps ih =>
    have hQ := h Q (by simp)
    have ht : ∀ A ∈ Ps, A.comp P = 0 := fun A hA => h A (by simp [hA])
    simp only [List.sum_cons, LinearMap.add_comp, hQ, ih ht, zero_add]

/-- A whole shared bank executes exactly the swap on the sum of its disjoint
address blocks. The statement is on every input, not only clean scratch. -/
theorem bankSwap_eq_sum (Ps : List (V →ₗ[R] V))
    (h : Ps.Pairwise (fun P Q => P.comp Q = 0 ∧ Q.comp P = 0)) :
    bankSwap Ps = partialSwap Ps.sum := by
  induction Ps with
  | nil => simp [bankSwap]
  | cons P Ps ih =>
    rcases List.pairwise_cons.mp h with ⟨hp, ht⟩
    rw [bankSwap, ih ht, List.sum_cons]
    exact partialSwap_comp_disjoint P Ps.sum
      (comp_sum_zero P Ps (fun Q hQ => (hp Q hQ).1))
      (sum_comp_zero P Ps (fun Q hQ => (hp Q hQ).2))

/-- A complete split partition needs no exterior auxiliary child. -/
theorem bankSwap_full (Ps : List (V →ₗ[R] V))
    (h : Ps.Pairwise (fun P Q => P.comp Q = 0 ∧ Q.comp P = 0))
    (hsum : Ps.sum = LinearMap.id) (z : V × V) :
    bankSwap Ps z = (z.2,z.1) := by
  rw [bankSwap_eq_sum Ps h, hsum]
  exact partialSwap_id z

/-- One common ancestor-dependent weighted chart, retained for the whole bank. -/
def weighted (A : (V × V) ≃ₗ[R] (V × V))
    (T : (V × V) →ₗ[R] (V × V)) : (V × V) →ₗ[R] (V × V) :=
  A.toLinearMap.comp (T.comp A.symm.toLinearMap)

@[simp] theorem weighted_apply (A : (V × V) ≃ₗ[R] (V × V))
    (T : (V × V) →ₗ[R] (V × V)) (z : V × V) :
    weighted A T z = A (T (A.symm z)) := rfl

/-- Chart conjugations telescope exactly, with no restriction on dirty data. -/
theorem weighted_comp (A : (V × V) ≃ₗ[R] (V × V))
    (T U : (V × V) →ₗ[R] (V × V)) :
    (weighted A T).comp (weighted A U) = weighted A (T.comp U) := by
  apply LinearMap.ext
  intro z
  simp

@[simp] theorem weighted_id (A : (V × V) ≃ₗ[R] (V × V)) :
    weighted A (LinearMap.id : (V × V) →ₗ[R] (V × V)) = LinearMap.id := by
  apply LinearMap.ext
  intro z
  simp

def weightedBank (A : (V × V) ≃ₗ[R] (V × V)) :
    List (V →ₗ[R] V) → ((V × V) →ₗ[R] (V × V))
  | [] => LinearMap.id
  | P :: Ps => (weighted A (partialSwap P)).comp (weightedBank A Ps)

/-- Every paid weighted core is retained in its chronological product. -/
theorem weightedBank_eq (A : (V × V) ≃ₗ[R] (V × V))
    (Ps : List (V →ₗ[R] V)) : weightedBank A Ps = weighted A (bankSwap Ps) := by
  induction Ps with
  | nil => simp [weightedBank, bankSwap]
  | cons P Ps ih =>
    rw [weightedBank, ih, weighted_comp, bankSwap]

/-- Heterogeneous completed-core packing has the exact full weighted endpoint. -/
theorem weightedBank_full (A : (V × V) ≃ₗ[R] (V × V))
    (Ps : List (V →ₗ[R] V))
    (h : Ps.Pairwise (fun P Q => P.comp Q = 0 ∧ Q.comp P = 0))
    (hsum : Ps.sum = LinearMap.id) (z : V × V) :
    weightedBank A Ps z = A ((A.symm z).2,(A.symm z).1) := by
  rw [weightedBank_eq, weighted_apply, bankSwap_full Ps h hsum]



section CoordinateBanks
variable {ι κ : Type*} [DecidableEq ι]

/-- Explicit split address blocks from an actual coordinate-owner ledger. -/
def coordinateProjector (owner : κ → ι) (s : ι) :
    (κ → R) →ₗ[R] (κ → R) where
  toFun v k := if owner k = s then v k else 0
  map_add' v w := by
    funext k
    by_cases h : owner k = s <;> simp [h]
  map_smul' r v := by
    funext k
    by_cases h : owner k = s <;> simp [h]

@[simp] theorem coordinateProjector_apply (owner : κ → ι) (s : ι)
    (v : κ → R) (k : κ) :
    coordinateProjector (R := R) owner s v k = if owner k = s then v k else 0 := rfl

theorem coordinateProjector_idempotent (owner : κ → ι) (s : ι) :
    (coordinateProjector (R := R) owner s).comp (coordinateProjector (R := R) owner s) =
      coordinateProjector (R := R) owner s := by
  apply LinearMap.ext
  intro v
  funext k
  by_cases h : owner k = s <;> simp [h]

theorem coordinateProjector_disjoint (owner : κ → ι) (s t : ι) (hst : s ≠ t) :
    (coordinateProjector (R := R) owner s).comp (coordinateProjector (R := R) owner t) = 0 := by
  apply LinearMap.ext
  intro v
  funext k
  by_cases h : owner k = s
  · have ht : owner k ≠ t := by simpa [h] using hst
    simp [h,hst]
  · simp [h]

private theorem coordinateProjector_sum_apply (owner : κ → ι)
    (roles : List ι) (hroles : roles.Nodup) (v : κ → R) (k : κ) :
    (roles.map (coordinateProjector (R := R) owner)).sum v k =
      if owner k ∈ roles then v k else 0 := by
  induction roles with
  | nil => simp
  | cons s roles ih =>
    rcases List.nodup_cons.mp hroles with ⟨hs, ht⟩
    simp only [List.map_cons, List.sum_cons, LinearMap.add_apply, Pi.add_apply,
      coordinateProjector_apply, ih ht, List.mem_cons]
    by_cases he : owner k = s
    · have hn : owner k ∉ roles := by simpa [he] using hs
      simp [he,hs]
    · simp [he]

/-- A disjoint exhaustive coordinate ledger gives an actual identity projector. -/
theorem coordinateProjector_sum (owner : κ → ι) (roles : List ι)
    (hroles : roles.Nodup) (hcover : ∀ k, owner k ∈ roles) :
    (roles.map (coordinateProjector (R := R) owner)).sum = LinearMap.id := by
  apply LinearMap.ext
  intro v
  funext k
  rw [coordinateProjector_sum_apply owner roles hroles v k]
  simp [hcover k]

/-- The concrete coordinate-owner construction supplies every projector premise
of the heterogeneous bank endpoint, including arbitrary incoming correlations. -/
theorem coordinateBank_full (owner : κ → ι) (roles : List ι)
    (hroles : roles.Nodup) (hcover : ∀ k, owner k ∈ roles)
    (z : (κ → R) × (κ → R)) :
    bankSwap (roles.map (coordinateProjector (R := R) owner)) z = (z.2,z.1) := by
  apply bankSwap_full
  · rw [List.pairwise_map]
    exact (List.nodup_iff_pairwise_ne.mp hroles).imp (fun hst =>
      ⟨coordinateProjector_disjoint owner _ _ hst,
        coordinateProjector_disjoint owner _ _ (Ne.symm hst)⟩)
  · exact coordinateProjector_sum owner roles hroles hcover

end CoordinateBanks

section Routing
variable {G S : Type*} [Group G]

/-- Actual bank address for invocation g and fixed role embedding H_s. -/
def bankAddress (H : S → G) (g : G) (s : S) : G := g * (H s)⁻¹

/-- Every role visits every physical bank once; no favorable subset is selected. -/
theorem bankAddress_bijective (H : S → G) (s : S) :
    Function.Bijective (fun g => bankAddress H g s) := by
  constructor
  · intro g g' h
    exact mul_right_cancel h
  · intro b
    refine ⟨b * H s, ?_⟩
    simp [bankAddress, mul_assoc]

/-- Distinct role embeddings rule out within-invocation physical aliasing. -/
theorem bankAddress_roles_injective (H : S → G) (hH : Function.Injective H)
    (g : G) : Function.Injective (bankAddress H g) := by
  intro s t h
  apply hH
  have hi : (H s)⁻¹ = (H t)⁻¹ := mul_left_cancel h
  exact inv_injective hi

end Routing
end Mathproof.BeyondNLogN.TakeoverBit





/-! Concrete PR155 p12 bit orbit-bank construction and complete paid ledger.
The inherited all-input local word, stage cover and routing contracts remain
explicit upstream dependencies; this file proves the new address endpoints,
coordinate capacities and exact inventory, not an all-size running-time claim. -/
namespace Mathproof.BeyondNLogN.TakeoverBit.P12
open Mathproof.BeyondNLogN.TakeoverBit

variable {R : Type*} [CommRing R]

/-- The 18 actual disjoint four-coordinate blocks for retained-gauge cores. -/
def selectedOwner (j : Fin 72) : Fin 18 := ⟨j.val / 4, by omega⟩

/-- The three actual disjoint 24-coordinate blocks for undeferred cores. -/
def undeferredOwner (j : Fin 72) : Fin 3 := ⟨j.val / 24, by omega⟩

theorem selected_block_capacity (s : Fin 18) :
    (Finset.univ.filter (fun j : Fin 72 => selectedOwner j = s)).card = 4 := by
  fin_cases s <;> decide

theorem undeferred_block_capacity (s : Fin 3) :
    (Finset.univ.filter (fun j : Fin 72 => undeferredOwner j = s)).card = 24 := by
  fin_cases s <;> decide

/-- Eighteen completed selected cores cover the entire address module. -/
theorem selected_bank_full (z : (Fin 72 → R) × (Fin 72 → R)) :
    bankSwap ((List.finRange 18).map (coordinateProjector (R := R) selectedOwner)) z =
      (z.2,z.1) := by
  exact coordinateBank_full selectedOwner (List.finRange 18)
    (List.nodup_finRange 18) (fun k => by simp) z

/-- Three completed undeferred cores also cover the entire address module. -/
theorem undeferred_bank_full (z : (Fin 72 → R) × (Fin 72 → R)) :
    bankSwap ((List.finRange 3).map (coordinateProjector (R := R) undeferredOwner)) z =
      (z.2,z.1) := by
  exact coordinateBank_full undeferredOwner (List.finRange 3)
    (List.nodup_finRange 3) (fun k => by simp) z

/-- Every child in the immutable freshly replayed p12 profile, including rank60. -/
def inheritedHistogram : List (Nat × Nat) :=
  [(1,120468),(2,68080),(3,28824),(4,7200),(5,11952),(6,3312),
   (7,6120),(8,4464),(9,1440),(10,2016),(11,2664),(12,3528),
   (13,1944),(14,2736),(15,1152),(16,4104),(17,6192),(18,5832),
   (19,4536),(20,7260),(21,8580),(22,15912),(60,5720)]

/-- The actual coordinate-full orbit banks remove precisely auxiliary exteriors;
all internal, source, target, center and data exterior entries remain charged. -/
def packedHistogram : List (Nat × Nat) :=
  inheritedHistogram.filter (fun p => p.1 != 60)

def rankMass (H : List (Nat × Nat)) : Nat :=
  (H.map (fun p => p.1*p.2)).sum

theorem inherited_rank_mass : rankMass inheritedHistogram = 2096432 := by decide

theorem removed_exterior_count :
    (inheritedHistogram.filter (fun p => p.1 == 60)).map Prod.snd = [5720] := by decide

theorem packed_rank_mass : rankMass packedHistogram = 1753232 := by decide

theorem packed_max_rank : ∀ p ∈ packedHistogram, p.1 ≤ 22 := by decide

/-- Three private stage banks for every full orbit, including fractional stock. -/
def normalizedVolume : ℚ := 2*1760 + 3*((5720:ℚ)/18 + (19904:ℚ)/3)

theorem normalized_volume : normalizedVolume = 73132/3 := by
  norm_num [normalizedVolume]

theorem packed_deficit : (72:ℚ)*normalizedVolume - rankMass packedHistogram = 1936 := by
  rw [packed_rank_mass, normalized_volume]
  norm_num

theorem actual_role_counts :
    5720 + 19904 = (25624:Nat) ∧ 18*4 = (72:Nat) ∧ 3*24 = (72:Nat) := by decide




/-- The actual common weighted chart retains the selected-bank full endpoint. -/
theorem selected_weighted_bank_full
    (A : ((Fin 72 → R) × (Fin 72 → R)) ≃ₗ[R] ((Fin 72 → R) × (Fin 72 → R)))
    (z : (Fin 72 → R) × (Fin 72 → R)) :
    weightedBank A ((List.finRange 18).map (coordinateProjector (R := R) selectedOwner)) z =
      A ((A.symm z).2,(A.symm z).1) := by
  rw [weightedBank_eq, weighted_apply, selected_bank_full]

/-- The same exact weighted endpoint holds for every undeferred bank. -/
theorem undeferred_weighted_bank_full
    (A : ((Fin 72 → R) × (Fin 72 → R)) ≃ₗ[R] ((Fin 72 → R) × (Fin 72 → R)))
    (z : (Fin 72 → R) × (Fin 72 → R)) :
    weightedBank A ((List.finRange 3).map (coordinateProjector (R := R) undeferredOwner)) z =
      A ((A.symm z).2,(A.symm z).1) := by
  rw [weightedBank_eq, weighted_apply, undeferred_bank_full]

end Mathproof.BeyondNLogN.TakeoverBit.P12



/-! Lift the checked address maps to actual arbitrary register contents.
No clean-scratch or independence assumption occurs in these statements. -/
namespace Mathproof.BeyondNLogN.TakeoverBit.Contents
open Mathproof.BeyondNLogN.TakeoverBit

variable {R V B : Type*} [CommRing R] [AddCommGroup V] [Module R V]

/-- Chronological execution on the complete contents of a physical bank. -/
def run : List (V →ₗ[R] V) → ((V × V) → B) → ((V × V) → B)
  | [], contents => contents
  | P :: Ps, contents => run Ps (fun z => contents (partialSwap P z))

theorem run_eq_address (Ps : List (V →ₗ[R] V)) (contents : (V × V) → B)
    (z : V × V) : run Ps contents z = contents (bankSwap Ps z) := by
  induction Ps generalizing contents with
  | nil => rfl
  | cons P Ps ih =>
    simp only [run, ih, bankSwap, LinearMap.comp_apply]

/-- A complete split partition executes the full transform on every dirty table. -/
theorem run_full (Ps : List (V →ₗ[R] V))
    (h : Ps.Pairwise (fun P Q => P.comp Q = 0 ∧ Q.comp P = 0))
    (hsum : Ps.sum = LinearMap.id) (contents : (V × V) → B) (z : V × V) :
    run Ps contents z = contents (z.2,z.1) := by
  rw [run_eq_address, bankSwap_full Ps h hsum]

/-- The actual p12 selected orbit bank works for arbitrary full bank contents. -/
theorem p12_selected_contents
    (contents : ((Fin 72 → R) × (Fin 72 → R)) → B)
    (z : (Fin 72 → R) × (Fin 72 → R)) :
    run ((List.finRange 18).map (coordinateProjector (R := R) P12.selectedOwner)) contents z =
      contents (z.2,z.1) := by
  rw [run_eq_address, P12.selected_bank_full]

/-- The actual p12 undeferred orbit bank has the same unconditional endpoint. -/
theorem p12_undeferred_contents
    (contents : ((Fin 72 → R) × (Fin 72 → R)) → B)
    (z : (Fin 72 → R) × (Fin 72 → R)) :
    run ((List.finRange 3).map (coordinateProjector (R := R) P12.undeferredOwner)) contents z =
      contents (z.2,z.1) := by
  rw [run_eq_address, P12.undeferred_bank_full]

end Mathproof.BeyondNLogN.TakeoverBit.Contents



/-! Immutable PR161 p12 bank specialization.  The actual coordinate-owner,
weighted-chart and dirty-content endpoints are reused from the independently
checked P12 construction; only the new frozen supplier inventory is specialized.
The retained all-input local word, charts, stage cover, routing, fallback and
sharp all-size framework are upstream contracts, not proved by this ledger. -/
namespace Mathproof.BeyondNLogN.TakeoverBit.PR161P12
open Mathproof.BeyondNLogN.TakeoverBit

/-- Complete child inventory from immutable PR161 head
`d14e29157bc905be1ced0776dd893d0714013f3a`, profile_p12.json. -/
def inheritedHistogram : List (Nat × Nat) :=
  [(1,120972),(2,73336),(3,29832),(4,8208),(5,12096),(6,4392),
   (7,4824),(8,2736),(9,648),(10,2160),(11,2016),(12,4464),
   (13,1080),(14,2232),(15,216),(16,2808),(17,2736),(18,3888),
   (19,3672),(20,7260),(21,8580),(22,15912),(60,5720)]

/-- Eighteen actual four-coordinate selected cores cover Fin72, so their
auxiliary rank60 exterior is removed; all other children remain charged. -/
def packedHistogram : List (Nat × Nat) :=
  inheritedHistogram.filter (fun p => p.1 != 60)

/-- Three stage banks, with selected roles grouped eighteen at a time and
undeferred roles grouped three at a time. -/
def normalizedVolume : ℚ := 2*1760 + 3*((5720:ℚ)/18 + (17648:ℚ)/3)

theorem inherited_rank_mass : P12.rankMass inheritedHistogram = 1934000 := by decide

theorem removed_exterior_count :
    (inheritedHistogram.filter (fun p => p.1 == 60)).map Prod.snd = [5720] := by decide

theorem packed_rank_mass : P12.rankMass packedHistogram = 1590800 := by decide

theorem packed_max_rank : ∀ p ∈ packedHistogram, p.1 ≤ 22 := by decide

theorem normalized_volume : normalizedVolume = 66364/3 := by
  norm_num [normalizedVolume]

theorem packed_deficit :
    (72:ℚ)*normalizedVolume - P12.rankMass packedHistogram = 1936 := by
  rw [packed_rank_mass, normalized_volume]
  norm_num

theorem actual_role_counts :
    5720 + 17648 = (23368:Nat) ∧ 18*4 = (72:Nat) ∧ 3*24 = (72:Nat) := by decide

/-- New source binding assembled with actual reused coordinate projectors;
no new abstract packing gadget or independence of register contents is assumed. -/
theorem actual_bank_and_inventory_certificate
    {R : Type*} [CommRing R] (z : (Fin 72 → R) × (Fin 72 → R)) :
    (∀ s : Fin 18, (Finset.univ.filter
      (fun j : Fin 72 => P12.selectedOwner j = s)).card = 4) ∧
    (∀ s : Fin 3, (Finset.univ.filter
      (fun j : Fin 72 => P12.undeferredOwner j = s)).card = 24) ∧
    bankSwap ((List.finRange 18).map
      (coordinateProjector (R := R) P12.selectedOwner)) z = (z.2,z.1) ∧
    bankSwap ((List.finRange 3).map
      (coordinateProjector (R := R) P12.undeferredOwner)) z = (z.2,z.1) ∧
    normalizedVolume = 66364/3 ∧
    P12.rankMass packedHistogram = 1590800 ∧
    (72:ℚ)*normalizedVolume - P12.rankMass packedHistogram = 1936 := by
  exact ⟨P12.selected_block_capacity, P12.undeferred_block_capacity,
    P12.selected_bank_full z, P12.undeferred_bank_full z,
    normalized_volume, packed_rank_mass, packed_deficit⟩

end Mathproof.BeyondNLogN.TakeoverBit.PR161P12



/-! The finite literal guard is discharged by an elementary universal charge
bound. No positive-guard oracle is used. The condition s ≤ mW is the ordinary
rank-mass bound of a finite supplier, not an unknown algorithm interface. -/
namespace Mathproof.BeyondNLogN.TakeoverLiteralGuard20261008

theorem literal_charge_lt (W m G s : ℝ)
    (hW : 0 ≤ W) (hm : 0 ≤ m) (hG : 0 ≤ G) (hs : s ≤ m*W) :
    2*G*W*W+8*s+4*W+4+32*m < 64*(W+m+G+1)^3 := by
  let X := W+m+G+1
  have hX : 1 ≤ X := by dsimp [X]; linarith
  have hX0 : 0 ≤ X := by linarith
  have hWX : W ≤ X := by dsimp [X]; linarith
  have hmX : m ≤ X := by dsimp [X]; linarith
  have hGX : G ≤ X := by dsimp [X]; linarith
  have hcube : 0 < X^3 := by positivity
  have hquad : X ≤ X^2 := by nlinarith
  have hquad_cube : X^2 ≤ X^3 := by
    have hp := mul_nonneg (show 0 ≤ X-1 by linarith) (sq_nonneg X)
    nlinarith
  have hfirst : 2*G*W*W ≤ 2*X*X*X := by gcongr
  have hsecond : m*W ≤ X*X := by gcongr
  have hlarge : 2*G*W*W+8*s+4*W+4+32*m ≤ 50*X^3 := by
    nlinarith
  dsimp [X] at hlarge hcube
  linarith

theorem finite_row_reserve : (0 : ℝ) < 70000-(51*12320/25) := by norm_num

theorem row_reserve_value : (70000-(51*12320/25) : ℝ) = 224336/5 := by norm_num


end Mathproof.BeyondNLogN.TakeoverLiteralGuard20261008



/- Source-bound arithmetic for PR163 paid balanced transfer and our new nullity-bank refinement.
   This is not a formalization of all-size integer multiplication. -/
namespace Mathproof.BeyondNLogN.TakeoverBalanced16320261009
noncomputable def a : ℝ := (297370240363722999999999702129759636277/500000000000000000000000000000000000000000)
noncomputable def b : ℝ := (297370240363723/500000000000000000)
noncomputable def eta : ℝ := (1/1000000000000000000000000)
noncomputable def beta : ℝ := (1/1000000000000000000000000)
noncomputable def kappa : ℝ := (118877394946471/200000000000000000)
noncomputable def tau : ℝ := 1-a
noncomputable def sigma : ℝ := 1-b
noncomputable def q : ℝ := a*(1-2*eta)
noncomputable def c : ℝ := q+eta/4
noncomputable def eps : ℝ := (1-eta)/(1+q)
noncomputable def lp : ℝ := 1-q
noncomputable def lam : ℝ := (tau+lp)/2
noncomputable def g : ℝ := eps*q
noncomputable def r : ℝ := (g+1-eps)/2
noncomputable def delta : ℝ := eta/8
noncomputable def internal : ℝ := tau+(1-beta)*max (sigma-tau) 0
noncomputable def leaf : ℝ := sigma+beta*(1-sigma)
noncomputable def coreSlacks : List ℝ := [
  (a) /- bit_positive -/,
  (b-a) /- complex_above_bit -/,
  (1/32-b) /- complex_below_one_over32 -/,
  (beta) /- beta_positive -/,
  (1-beta) /- beta_below_one -/,
  ((1-beta)*b-a) /- leaf_saving_above_bit -/,
  (q) /- q_positive -/,
  (1-internal-q) /- q_below_internal -/,
  (1-leaf-q) /- q_below_leaf -/,
  (c) /- c_positive -/,
  (1-c) /- c_below_one -/,
  (c-q) /- q_below_reservations -/,
  (lam-tau) /- lambda_above_tau -/,
  (lam-sigma) /- lambda_above_sigma -/,
  (lam-internal) /- lambda_above_internal -/,
  (lp-lam) /- lambda_prime_above_lambda -/,
  (lp-leaf) /- compact_leaf -/,
  (lp-(1-c)) /- compact_reservations -/,
  (q) /- lambda_prime_below_one -/,
  (eps) /- epsilon_positive -/,
  (1-eps) /- epsilon_below_one -/,
  (1-eps) /- guard_width -/,
  (1-eps*(1+c)) /- K_geometry -/,
  (eps*c) /- K_dominates_log -/,
  (1-eps) /- record_suffix -/,
  (1-eps-delta) /- phase_local -/,
  (r-delta) /- phase_boundary -/,
  (1-eps-r) /- gamma_sublinear -/,
  (eps-(1-r)/2) /- cell_above_band -/,
  (1-eps) /- prime_interval_packing -/,
  (r) /- alpha_positive -/,
  (1-r) /- alpha_below_one -/,
  (1/4-r) /- alpha_below_one_fourth -/,
  (delta) /- delta_positive -/,
  (1/8-delta) /- delta_below_one_eighth -/,
  (eps-a) /- short_record_fallback -/,
  (1-eps-g) /- small_field_exposure -/,
  (8-eps+r-delta-g) /- artificial_boundary -/,
  ((1-eps)-kappa) /- paid_balanced_prefix_above_kappa -/,
  ((a)-kappa) /- coordinate_movement_above_kappa -/,
  ((g)-kappa) /- compact_phase_layer_above_kappa -/,
  ((a)-kappa) /- bulk_exposure_above_kappa -/,
  ((min (1-eps-delta) (r-delta))-kappa) /- Gaussian_arithmetic_above_kappa -/,
  ((1-eps-delta)-kappa) /- scalar_work_above_kappa -/,
  ((eps)-kappa) /- dimension_above_kappa -/
]
theorem core_slacks_positive : ∀ x ∈ coreSlacks, 0 < x := by
  norm_num [coreSlacks, a, b, eta, beta, kappa, tau, sigma, q, c, eps, lp, lam, g, r, delta, internal, leaf]

theorem all_47_slacks_positive (literal row : ℝ)
    (hl : 0 < literal) (hr : 0 < row) :
    ∀ x ∈ coreSlacks ++ [literal, row], 0 < x := by
  intro x hx
  rcases List.mem_append.mp hx with h | h
  · exact core_slacks_positive x h
  · simp only [List.mem_cons, List.not_mem_nil, or_false] at h
    rcases h with h | h
    · simpa [h] using hl
    · simpa [h] using hr

theorem strengthened_public_margin :
    (148492550769873/250000000000000000 : ℝ) < kappa ∧ kappa < g := by
  norm_num [kappa, g, eps, c, q, a, eta]

/-- Complete arithmetic composition of our certified bit bank with the
pinned PR163 paid balanced transfer physical complex supplier. All finite guards are proved, subject
only to explicit nonnegative counts and their standard rank-mass bound.
This theorem does not claim the retained analytic/tape interfaces. -/
theorem all_47_concrete_guards (W m G s : ℝ)
    (hW : 0 ≤ W) (hm : 0 ≤ m) (hG : 0 ≤ G) (hs : s ≤ m*W) :
    ∀ x ∈ coreSlacks ++
      [64*(W+m+G+1)^3-(2*G*W*W+8*s+4*W+4+32*m),
       70000-(51*12320/25)], 0 < x := by
  apply all_47_slacks_positive
  · exact sub_pos.mpr
      (Mathproof.BeyondNLogN.TakeoverLiteralGuard20261008.literal_charge_lt
        W m G s hW hm hG hs)
  · exact Mathproof.BeyondNLogN.TakeoverLiteralGuard20261008.finite_row_reserve

end Mathproof.BeyondNLogN.TakeoverBalanced16320261009
