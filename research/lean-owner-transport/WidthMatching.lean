/-
Copyright (c) 2026 Rohan Arun. All rights reserved.
Released under Apache 2.0; substantial OpenAI Codex assistance.

Largest-demand-first whole-owner matching. Owner identities are retained,
including distinct owners with the same width. Threshold-count feasibility
supports any admissible choice, not only a particular tie-breaking heuristic.
-/
import OwnerTransport

namespace OwnerTransport.WidthMatching

/-- Number of entries whose width is at least a threshold. -/
def countGE (width : α → Nat) (threshold : Nat) : List α → Nat
  | [] => 0
  | a :: rest => (if threshold ≤ width a then 1 else 0) + countGE width threshold rest

/-- Every threshold has enough owners for the demands of at least that width. -/
def Feasible (width : α → Nat) (demands : List Nat) (owners : List α) : Prop :=
  ∀ threshold, countGE id threshold demands ≤ countGE width threshold owners

/-- A complete assignment, listed in demand order. -/
def Fits (width : α → Nat) : List Nat → List α → Prop
  | [], [] => True
  | d :: ds, a :: owners => d ≤ width a ∧ Fits width ds owners
  | _, _ => False

/-- Reordering owners preserves every threshold count. -/
theorem countGE_perm (width : α → Nat) (t : Nat) {xs ys : List α}
    (h : xs.Perm ys) : countGE width t xs = countGE width t ys := by
  induction h with
  | nil => rfl
  | cons a h ih => simp only [countGE, id, ih]
  | swap a b xs => simp only [countGE, id]; omega
  | trans h₁ h₂ ih₁ ih₂ => exact ih₁.trans ih₂

/-- Capacity feasibility is invariant under owner reordering. -/
theorem feasible_perm (width : α → Nat) (ds : List Nat) {xs ys : List α}
    (h : xs.Perm ys) : Feasible width ds xs ↔ Feasible width ds ys := by
  unfold Feasible
  simp only [countGE_perm width _ h]

/-- A list with all widths below a threshold contributes no eligible entries. -/
theorem countGE_zero (width : α → Nat) (t : Nat) (xs : List α)
    (h : ∀ a, a ∈ xs → width a < t) : countGE width t xs = 0 := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    have ha := h a (by simp)
    have hr := ih (fun b hb => h b (by simp [hb]))
    simp only [countGE, id, if_neg (by omega : ¬ t ≤ width a), hr]

/-- Pointwise width domination gives threshold feasibility. -/
theorem fits_feasible (width : α → Nat) (ds : List Nat) (owners : List α)
    (h : Fits width ds owners) : Feasible width ds owners := by
  induction ds generalizing owners with
  | nil => intro t; simp [countGE]
  | cons d ds ih =>
    cases owners with
    | nil => cases h
    | cons a owners =>
      obtain ⟨hda, hrest⟩ := h
      have hr := ih owners hrest
      intro t
      have ht := hr t
      simp only [countGE, id]
      split <;> split <;> omega

/-- A complete assignment contains exactly one owner per demand. -/
theorem fits_length (width : α → Nat) (ds : List Nat) (owners : List α)
    (h : Fits width ds owners) : ds.length = owners.length := by
  induction ds generalizing owners with
  | nil => cases owners <;> simp_all [Fits]
  | cons d ds ih =>
    cases owners with
    | nil => cases h
    | cons a owners => simp only [List.length_cons]; exact congrArg (· + 1) (ih owners h.2)

/-- Exchange lemma: choosing ANY fitting owner for a largest remaining demand
preserves all threshold inequalities for the remaining owners and demands. -/
theorem remove_largest (width : α → Nat) (d : Nat) (ds : List Nat)
    (a : α) (rest : List α)
    (hmax : ∀ x, x ∈ ds → x ≤ d)
    (hfit : d ≤ width a) (hf : Feasible width (d :: ds) (a :: rest)) :
    Feasible width ds rest := by
  intro t
  by_cases ht : t ≤ d
  · have ha : t ≤ width a := Nat.le_trans ht hfit
    have h := hf t
    simp only [countGE, id, ht, ha, if_true] at h
    omega
  · have hz := countGE_zero id t ds (fun x hx => by
      change x < t
      have := hmax x hx
      omega)
    rw [hz]
    exact Nat.zero_le _

/-- The exchange lemma on the actual owner list, with its identities preserved. -/
theorem remove_selected (width : α → Nat) (d : Nat) (ds : List Nat)
    (owners : List α) (a : α) (rest : List α)
    (hmax : ∀ x, x ∈ ds → x ≤ d) (hfit : d ≤ width a)
    (hperm : owners.Perm (a :: rest)) (hf : Feasible width (d :: ds) owners) :
    Feasible width ds rest :=
  remove_largest width d ds a rest hmax hfit ((feasible_perm width _ hperm).mp hf)

/-- A concrete first-fitting-owner selector. The exchange lemma also permits
other selectors (such as PR527's best-fit heuristic) with the same contract. -/
def select (width : α → Nat) (d : Nat) : List α → Option (α × List α)
  | [] => none
  | a :: rest =>
      if d ≤ width a then some (a, rest)
      else match select width d rest with
        | none => none
        | some (b, tail) => some (b, a :: tail)

/-- Every successful selection removes one fitting owner and preserves all others. -/
theorem select_sound (width : α → Nat) (d : Nat) (owners : List α)
    (a : α) (rest : List α) (h : select width d owners = some (a, rest)) :
    d ≤ width a ∧ owners.Perm (a :: rest) := by
  induction owners generalizing a rest with
  | nil => simp [select] at h
  | cons b bs ih =>
    simp only [select] at h
    split at h
    · cases h
      exact ⟨by assumption, List.Perm.refl _⟩
    · cases hs : select width d bs with
      | none => simp [hs] at h
      | some pair =>
        obtain ⟨c, cs⟩ := pair
        simp only [hs] at h
        obtain ⟨hfit, hp⟩ := ih c cs hs
        cases h
        exact ⟨hfit, (hp.cons b).trans (List.Perm.swap a b cs)⟩

/-- Failure means no remaining owner meets the requested width. -/
theorem select_none_count (width : α → Nat) (d : Nat) (owners : List α)
    (h : select width d owners = none) : countGE width d owners = 0 := by
  induction owners with
  | nil => rfl
  | cons a rest ih =>
    simp only [select] at h
    split at h
    · contradiction
    · rename_i hbad
      have hr : select width d rest = none := by
        cases hs : select width d rest with
        | none => rfl
        | some pair => obtain ⟨b, bs⟩ := pair; simp [hs] at h
      simp only [countGE, id, if_neg hbad, ih hr, Nat.zero_add]

/-- Feasibility ensures a largest-first allocator can always take its next step. -/
theorem select_exists (width : α → Nat) (d : Nat) (ds : List Nat) (owners : List α)
    (hf : Feasible width (d :: ds) owners) :
    ∃ a rest, select width d owners = some (a, rest) := by
  cases hs : select width d owners with
  | none =>
    have hz := select_none_count width d owners hs
    have h := hf d
    simp only [countGE, id, Nat.le_refl, if_true, hz] at h
    omega
  | some pair => exact ⟨pair.1, pair.2, rfl⟩

/-- Executable allocation in demand order; excess owners are returned unchanged. -/
def allocate (width : α → Nat) : List Nat → List α → Option (List α × List α)
  | [], owners => some ([], owners)
  | d :: ds, owners =>
      match select width d owners with
      | none => none
      | some (a, rest) =>
        match allocate width ds rest with
        | none => none
        | some (assigned, unused) => some (a :: assigned, unused)

/-- Largest-demand-first allocation succeeds, assigns fitting owners and
preserves the entire multiset of owner identities. -/
theorem allocate_correct (width : α → Nat) (ds : List Nat) (owners : List α)
    (hsorted : ds.Pairwise (fun a b => b ≤ a)) (hf : Feasible width ds owners) :
    ∃ assigned unused, allocate width ds owners = some (assigned, unused) ∧
      Fits width ds assigned ∧ owners.Perm (assigned ++ unused) := by
  induction ds generalizing owners with
  | nil => exact ⟨[], owners, rfl, trivial, List.Perm.refl _⟩
  | cons d ds ih =>
    obtain ⟨hmax, htail⟩ := List.pairwise_cons.mp hsorted
    obtain ⟨a, rest, hselect⟩ := select_exists width d ds owners hf
    obtain ⟨hfit, hperm⟩ := select_sound width d owners a rest hselect
    have hrest := remove_selected width d ds owners a rest hmax hfit hperm hf
    obtain ⟨assigned, unused, hrun, hfits, hp⟩ := ih rest htail hrest
    refine ⟨a :: assigned, unused, ?_, ⟨hfit, hfits⟩, ?_⟩
    · simp [allocate, hselect, hrun]
    · exact hperm.trans (hp.cons a)

/-- With equal list lengths, a successful feasible run uses every owner once. -/
theorem allocate_complete (width : α → Nat) (ds : List Nat) (owners : List α)
    (hsorted : ds.Pairwise (fun a b => b ≤ a)) (hf : Feasible width ds owners)
    (hlen : ds.length = owners.length) :
    ∃ assigned, allocate width ds owners = some (assigned, []) ∧
      Fits width ds assigned ∧ owners.Perm assigned := by
  obtain ⟨assigned, unused, hrun, hfits, hp⟩ := allocate_correct width ds owners hsorted hf
  have hl := fits_length width ds assigned hfits
  have hpLen := hp.length_eq
  simp only [List.length_append] at hpLen
  have hu : unused = [] := List.eq_nil_of_length_eq_zero (by omega)
  subst unused
  exact ⟨assigned, hrun, hfits, by simpa using hp⟩

/-- Threshold feasibility also ignores the original order of the demands. -/
theorem feasible_demand_perm (width : α → Nat) (owners : List α)
    {ds es : List Nat} (h : ds.Perm es) :
    Feasible width ds owners ↔ Feasible width es owners := by
  unfold Feasible
  simp only [countGE_perm id _ h]

/-- Executable largest-first ordering, with core-library sorting proofs. -/
def descending (ds : List Nat) : List Nat :=
  ds.mergeSort (fun a b => decide (b ≤ a))

/-- Sorting preserves every demand, including equal-width occurrences. -/
theorem descending_perm (ds : List Nat) : (descending ds).Perm ds :=
  List.mergeSort_perm ds _

/-- The executable sorter discharges the maximal-demand premise. -/
theorem descending_sorted (ds : List Nat) :
    (descending ds).Pairwise (fun a b => b ≤ a) := by
  have hs := List.sorted_mergeSort
    (le := fun a b : Nat => decide (b ≤ a))
    (fun a b c hab hbc => by simp only [decide_eq_true_eq] at *; omega)
    (fun a b => by simp only [Bool.or_eq_true, decide_eq_true_eq]; omega) ds
  simpa only [descending, decide_eq_true_eq] using hs

/-- The rankwise certificate is checked after sorting both demand and owner widths. -/
def rankedOwners (width : α → Nat) (owners : List α) : List α :=
  owners.mergeSort (fun a b => decide (width b ≤ width a))

/-- Sorted componentwise dominance suffices for complete executable allocation.
No matching, no threshold inequalities and no successful run are assumed. -/
theorem allocation_from_sorted_dominance (width : α → Nat)
    (ds : List Nat) (owners : List α)
    (hdom : Fits width (descending ds) (rankedOwners width owners)) :
    ∃ assigned, allocate width (descending ds) owners = some (assigned, []) ∧
      Fits width (descending ds) assigned ∧ owners.Perm assigned := by
  have hrank : (rankedOwners width owners).Perm owners := List.mergeSort_perm owners _
  have hf := (feasible_perm width (descending ds) hrank).mp
    (fits_feasible width _ _ hdom)
  have hlen := (fits_length width _ _ hdom).trans hrank.length_eq
  exact allocate_complete width _ owners (descending_sorted ds) hf hlen

/-- Distinct physical owner identities stay distinct through the complete assignment. -/
theorem allocation_preserves_distinct_owners (width : α → Nat)
    (ds : List Nat) (owners : List α)
    (hdom : Fits width (descending ds) (rankedOwners width owners))
    (howners : owners.Nodup) :
    ∃ assigned, allocate width (descending ds) owners = some (assigned, []) ∧
      Fits width (descending ds) assigned ∧ owners.Perm assigned ∧ assigned.Nodup := by
  obtain ⟨assigned, hrun, hfit, hp⟩ := allocation_from_sorted_dominance width ds owners hdom
  exact ⟨assigned, hrun, hfit, hp, hp.nodup howners⟩

/-- Stateful allocator interface: a policy may use owner priorities or a running
capacity ledger, provided each step selects one fitting available owner. -/
def allocateBy (choose : σ → Nat → List α → Option (α × List α × σ)) :
    σ → List Nat → List α → Option (List α × List α × σ)
  | state, [], owners => some ([], owners, state)
  | state, d :: ds, owners =>
    match choose state d owners with
    | none => none
    | some (a, rest, next) =>
      match allocateBy choose next ds rest with
      | none => none
      | some (assigned, unused, finalState) => some (a :: assigned, unused, finalState)

/-- Any total admissible policy succeeds on feasible largest-first demands.
State changes and tie-breaking are unrestricted; owner identity is conserved. -/
theorem allocation_policy_correct (width : α → Nat)
    (choose : σ → Nat → List α → Option (α × List α × σ))
    (hsound : ∀ state d owners a rest next,
      choose state d owners = some (a, rest, next) →
      d ≤ width a ∧ owners.Perm (a :: rest))
    (htotal : ∀ state d owners, 0 < countGE width d owners →
      ∃ a rest next, choose state d owners = some (a, rest, next))
    (state : σ) (ds : List Nat) (owners : List α)
    (hsorted : ds.Pairwise (fun a b => b ≤ a)) (hf : Feasible width ds owners) :
    ∃ assigned unused finalState,
      allocateBy choose state ds owners = some (assigned, unused, finalState) ∧
      Fits width ds assigned ∧ owners.Perm (assigned ++ unused) := by
  induction ds generalizing owners state with
  | nil => exact ⟨[], owners, state, rfl, trivial, List.Perm.refl _⟩
  | cons d ds ih =>
    obtain ⟨hmax, htail⟩ := List.pairwise_cons.mp hsorted
    have hpos : 0 < countGE width d owners := by
      have h := hf d
      simp only [countGE, id, Nat.le_refl, if_true] at h
      omega
    obtain ⟨a, rest, next, hchoose⟩ := htotal state d owners hpos
    obtain ⟨hfit, hp⟩ := hsound state d owners a rest next hchoose
    have hrest := remove_selected width d ds owners a rest hmax hfit hp hf
    obtain ⟨assigned, unused, finalState, hrun, hfits, hperm⟩ := ih next rest htail hrest
    refine ⟨a :: assigned, unused, finalState, ?_, ⟨hfit, hfits⟩, hp.trans (hperm.cons a)⟩
    simp [allocateBy, hchoose, hrun]

end OwnerTransport.WidthMatching
