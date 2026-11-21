import Mathlib.Data.Finset.Card
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset

namespace NativeForest

def sourceKey (depth steps : ℕ) (future : List ℕ) : ℕ × List ℕ :=
  (depth - steps, List.replicate steps 0 ++ future)

theorem recover_future {d i j : ℕ} {u v : List ℕ}
    (hi : i ≤ d) (hj : j ≤ d) (same : sourceKey d i u = sourceKey d j v) :
    u = v := by
  have heads : d - i = d - j := congrArg Prod.fst same
  have eq : i = j := by omega
  subst j
  have tails : List.replicate i 0 ++ u = List.replicate i 0 ++ v := congrArg Prod.snd same
  exact List.append_cancel_left tails

def externalSource (live : ℕ → List ℕ → Bool) : ℕ → List ℕ → ℕ × List ℕ
  | 0, f => (0, f)
  | d + 1, f => if live d (0 :: f) then externalSource live d (0 :: f) else (d + 1, f)

theorem one_parent (d k : ℕ) (f : List ℕ) :
    sourceKey d k (0 :: f) = sourceKey (d + 1) (k + 1) f := by
  simp [sourceKey, List.replicate_succ', List.append_assoc]

theorem external_witness (live : ℕ → List ℕ → Bool) (d : ℕ) (f : List ℕ) :
    ∃ k ≤ d, externalSource live d f = sourceKey d k f := by
  induction d generalizing f with
  | zero => exact ⟨0, by omega, by simp [externalSource, sourceKey]⟩
  | succ d ih =>
    by_cases parent : live d (0 :: f) = true
    · obtain ⟨k, h, eq⟩ := ih (0 :: f)
      exact ⟨k+1, by omega, by simpa [externalSource, parent, eq] using one_parent d k f⟩
    · exact ⟨0, by omega, by simp [externalSource, parent, sourceKey]⟩

theorem external_injective (live : ℕ → List ℕ → Bool) (d : ℕ) :
    Function.Injective (externalSource live d) := by
  intro f g eq
  obtain ⟨i, hi, fi⟩ := external_witness live d f
  obtain ⟨j, hj, gj⟩ := external_witness live d g
  exact recover_future hi hj (fi.symm.trans (eq.trans gj))

def actualExternal (live : ℕ → List ℕ → Bool) (q : ℕ × List ℕ) : Prop :=
  live q.1 q.2 = true ∧ ∀ j, q.1 = j + 1 → live j (0 :: q.2) = false

theorem ends_at_external (live : ℕ → List ℕ → Bool) (d : ℕ) (f : List ℕ)
    (openUnit : live d f = true) : actualExternal live (externalSource live d f) := by
  induction d generalizing f with
  | zero => simp [actualExternal, externalSource, openUnit]
  | succ d ih =>
    by_cases parent : live d (0 :: f) = true
    · simpa [externalSource, parent] using ih (0 :: f) parent
    · simp [actualExternal, externalSource, parent, openUnit]

theorem source_layer {d : ℕ} {units : Finset (List ℕ)} {sources : Finset (ℕ × List ℕ)}
    (live : ℕ → List ℕ → Bool) (opened : ∀ u ∈ units, live d u = true)
    (catalogue : ∀ q, actualExternal live q → q ∈ sources) : units.card ≤ sources.card := by
  apply Finset.card_le_card_of_injOn (externalSource live d)
  · intro u hu
    exact catalogue _ (ends_at_external live d u (opened u hu))
  · intro u hu v hv eq
    exact external_injective live d eq

theorem active_layer {d : ℕ} {units : Finset (List ℕ)}
    {sources : Finset (ℕ × List ℕ)} (steps : List ℕ → ℕ)
    (bound : ∀ u ∈ units, steps u ≤ d)
    (lands : ∀ u ∈ units, sourceKey d (steps u) u ∈ sources) :
    units.card ≤ sources.card := by
  exact Finset.card_le_card_of_injOn (fun u => sourceKey d (steps u) u) lands
    (fun u hu v hv he => recover_future (bound u hu) (bound v hv) he)

theorem active_units {ind : Finset ℕ} (count : ℕ → ℕ) {sources copies slots : ℕ}
    (each : ∀ i ∈ ind, count i ≤ sources) (fund : copies * sources ≤ slots) :
    (∑ i ∈ ind, count i) * copies ≤ ind.card * slots := by
  have h : (∑ i ∈ ind, count i) ≤ ∑ _i ∈ ind, sources :=
    Finset.sum_le_sum each
  calc
    (∑ i ∈ ind, count i) * copies ≤ (∑ _i ∈ ind, sources) * copies :=
      Nat.mul_le_mul_right copies h
    _ = ind.card * (copies * sources) := by simp [mul_comm, mul_left_comm]
    _ ≤ ind.card * slots := Nat.mul_le_mul_left _ fund

theorem allocate_high_water {high live vacant : ℕ} (count : high = live + vacant) :
    (if vacant = 0 then high + 1 else high) = max high (live + 1) := by
  split <;> omega

theorem retire_high_water {high live vacant : ℕ} (count : high = live + vacant)
    (owned : 0 < live) : high = (live - 1) + (vacant + 1) := by omega

#print axioms recover_future
#print axioms one_parent
#print axioms external_witness
#print axioms external_injective
#print axioms ends_at_external
#print axioms source_layer
#print axioms active_layer
#print axioms active_units
#print axioms allocate_high_water
#print axioms retire_high_water

end NativeForest
