/-
RELAY-SANDWICH law (NEWNATIVE R4 sec 3), See RelaySandwich.md.
Abstract: charts form a lattice; resident i of a relay chart c arrives from chart p i and departs to n i
(p i ≤ c ≤ n i, public steps ascend). Pinned: c = ⨆ p = ⨅ n.  Then any chart c' that keeps every
resident's route ascending equals c.  Bridge to FrameSep.Route (frames = submodules) included.
Also the cost identity for a 0 -> e helper with k evenly spaced stops: e * ln (k+1) (e = 9: 9 ln (k+1)).
-/
import Nov15.FrameSep
import Nov15.JunkLB2

namespace RelaySandwich

section Lattice
variable {L ι : Type*} [CompleteLattice L]

/-- c is pinned by residents with arrival charts p and departure charts n. -/
structure Pinned (p n : ι → L) (c : L) : Prop where
  arrive : ∀ i, p i ≤ c
  depart : ∀ i, c ≤ n i
  join : c = ⨆ i, p i
  meet : c = ⨅ i, n i

/-- Admissible replacement of the stop: every resident's route stays ascending through c'. -/
def Admissible (p n : ι → L) (c' : L) : Prop := ∀ i, p i ≤ c' ∧ c' ≤ n i

/-- **RELAY-SANDWICH**: the only admissible stop chart is c itself. -/
theorem admissible_unique {p n : ι → L} {c : L} (h : Pinned p n c) {c' : L}
    (hc : Admissible p n c') : c' = c := by
  apply le_antisymm
  · rw [h.meet]; exact le_iInf fun i => (hc i).2
  · rw [h.join]; exact iSup_le fun i => (hc i).1

theorem admissible_iff {p n : ι → L} {c : L} (h : Pinned p n c) (c' : L) :
    Admissible p n c' ↔ c' = c :=
  ⟨admissible_unique h, fun e => e ▸ fun i => ⟨h.arrive i, h.depart i⟩⟩

/-- Collapse onto a neighbour chart (some resident's previous or next chart d) is impossible
when no neighbour chart equals c. -/
theorem no_neighbour_collapse {p n : ι → L} {c : L} (h : Pinned p n c)
    (hp : ∀ i, p i ≠ c) (hn : ∀ i, n i ≠ c) (j : ι) :
    ¬ Admissible p n (p j) ∧ ¬ Admissible p n (n j) :=
  ⟨fun a => hp j (admissible_unique h a), fun a => hn j (admissible_unique h a)⟩

/-- Non-degenerate pinned relay needs two residents (indeed no single resident's chart is c). -/
theorem pinned_nontrivial {p n : ι → L} {c : L} (h : Pinned p n c)
    (hp : ∀ i, p i ≠ c) [Nonempty ι] : ¬ Subsingleton ι := by
  intro hs
  obtain ⟨i⟩ := ‹Nonempty ι›
  apply hp i
  rw [h.join]
  apply le_antisymm
  · exact le_iSup p i
  · exact iSup_le fun j => by rw [Subsingleton.elim j i]

/-- The non-equality hypotheses are not redundant (degenerate resident with p = n = c): the
"neighbour" chart p 0 is admissible, but it equals c, so nothing is collapsed. -/
example : ∃ (p n : Fin 1 → Prop) (c : Prop), Pinned p n c ∧ Admissible p n (p 0) ∧ p 0 = c :=
  ⟨fun _ => False, fun _ => False, False,
    ⟨fun _ => le_rfl, fun _ => le_rfl, by simp, by simp⟩, fun _ => ⟨le_rfl, le_rfl⟩, rfl⟩

end Lattice

section Route
open FrameSep
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- Replace the frame at time t+1 by c'. -/
def restop (R : Route K V) (t : ℕ) (c' : Submodule K V) : ℕ → Submodule K V :=
  Function.update R.f (t + 1) c'

/-- If steps t and t+1 are public, the stop-replaced frame sequence has every step ascending
iff c' sits between the frames at t and t+2 (the route-ordering side of a collapse). -/
theorem restop_valid_iff (R : Route K V) (t : ℕ) (h0 : ¬ R.owned t) (h1 : ¬ R.owned (t + 1))
    (c' : Submodule K V) :
    (∀ s, ¬ R.owned s → restop R t c' s ≤ restop R t c' (s + 1)) ↔
      (R.f t ≤ c' ∧ c' ≤ R.f (t + 2)) := by
  constructor
  · intro h
    have a := h t h0
    have b := h (t + 1) h1
    simp only [restop, Function.update_self, Function.update_of_ne (show t ≠ t + 1 by omega),
      Function.update_of_ne (show t + 2 ≠ t + 1 by omega)] at a b
    exact ⟨a, b⟩
  · rintro ⟨a, b⟩ s hs
    by_cases e1 : s = t
    · subst e1; simpa [restop] using a
    by_cases e2 : s = t + 1
    · subst e2; simpa [restop] using b
    have n1 : s ≠ t + 1 := e2
    have n2 : s + 1 ≠ t + 1 := fun h => e1 (by omega)
    simpa [restop, Function.update_of_ne n1, Function.update_of_ne n2] using R.pub s hs

/-- **Frame form.** Residents i with routes R i, each with public steps t i, t i + 1 and
frame c at time t i + 1; pinned by their frames at t i and t i + 2.  If every resident's
stop-replaced route (stop chart c') is valid, c' = c. -/
theorem route_collapse {ι : Type*} (R : ι → Route K V) (t : ι → ℕ)
    (h0 : ∀ i, ¬ (R i).owned (t i)) (h1 : ∀ i, ¬ (R i).owned (t i + 1))
    {c : Submodule K V}
    (hp : Pinned (fun i => (R i).f (t i)) (fun i => (R i).f (t i + 2)) c)
    {c' : Submodule K V}
    (hv : ∀ i, ∀ s, ¬ (R i).owned s → restop (R i) (t i) c' s ≤ restop (R i) (t i) c' (s + 1)) :
    c' = c :=
  admissible_unique hp fun i => (restop_valid_iff (R i) (t i) (h0 i) (h1 i) c').1 (hv i)

end Route

section Cost
open JunkLB2

/-- Cost of a helper going 0 -> e in k+1 equal moves (k stops), per-stay accounting:
D0 = f(e) - Σ f(gap) over the k+1 moves. -/
noncomputable def stopCost (f : ℝ → ℝ) (e : ℝ) (k : ℕ) : ℝ :=
  f e - ((List.replicate (k + 1) (f (e / (k + 1)))).sum)

theorem stopCost_eq (f : ℝ → ℝ) (e : ℝ) (k : ℕ) :
    stopCost f e k = f e - (k + 1) * f (e / (k + 1)) := by
  simp [stopCost, List.sum_replicate, nsmul_eq_mul]

/-- For f(r) = r ln r the cost is e ln (k+1). -/
theorem stopCost_fL (e : ℝ) (k : ℕ) : stopCost fL e k = e * Real.log (k + 1) := by
  have hk : (0 : ℝ) < (k : ℝ) + 1 := by positivity
  rw [stopCost_eq]
  unfold fL
  by_cases he : e = 0
  · simp [he]
  have hd : e / ((k : ℝ) + 1) ≠ 0 := div_ne_zero he hk.ne'
  rw [Real.log_div he hk.ne']
  field_simp
  ring

/-- The 0 -> 9 helper: 9 ln (k+1). -/
theorem stopCost_nine (k : ℕ) : stopCost fL 9 k = 9 * Real.log (k + 1) := stopCost_fL 9 k

/-- Integer-gap cases (gap 9/(k+1) integral): k = 0, 2, 8 give 0, 9 ln 3, 9 ln 9 = 18 ln 3. -/
theorem stopCost_k2 : stopCost fL 9 2 = 9 * Real.log 3 := by
  rw [stopCost_nine]; norm_num

/-- Stops are paid: cost is strictly increasing in k (convexity not needed for f = r ln r). -/
theorem stopCost_strictMono {k m : ℕ} (h : k < m) : stopCost fL 9 k < stopCost fL 9 m := by
  rw [stopCost_nine, stopCost_nine]
  have : Real.log ((k : ℝ) + 1) < Real.log ((m : ℝ) + 1) :=
    Real.log_lt_log (by positivity) (by exact_mod_cast Nat.add_lt_add_right h 1)
  linarith

end Cost

#print axioms admissible_unique
#print axioms no_neighbour_collapse
#print axioms pinned_nontrivial
#print axioms restop_valid_iff
#print axioms route_collapse
#print axioms stopCost_fL
#print axioms stopCost_nine
#print axioms stopCost_k2
#print axioms stopCost_strictMono

end RelaySandwich
