import Extracted

namespace Model
variable {K : Type} {Γ : K → Type} {Λ σ : Type}

def pushSymbols (states : List σ) : Stmt Γ Λ σ → List (Sigma Γ)
  | .push k f q => states.map (fun v => ⟨k, f v⟩) ++ pushSymbols states q
  | .peek _ _ q | .pop _ _ q | .load _ q => pushSymbols states q
  | .branch _ q₁ q₂ => pushSymbols states q₁ ++ pushSymbols states q₂
  | .goto _ | .halt => []

def Allowed (A : List (Sigma Γ)) (S : ∀ k, List (Γ k)) : Prop :=
  ∀ k x, x ∈ S k → Sigma.mk k x ∈ A

variable [DecidableEq K]

theorem allowed_update {A : List (Sigma Γ)} {S : ∀ k, List (Γ k)}
    (hS : Allowed A S) (k : K) (xs : List (Γ k))
    (hx : ∀ x ∈ xs, Sigma.mk k x ∈ A) : Allowed A (update S k xs) := by
  intro j x h
  by_cases hj : j = k
  · subst j
    exact hx x (by simpa [update] using h)
  · exact hS j x (by simpa [update, hj] using h)

theorem stepAux_allowed (states : List σ) (hs : ∀ v, v ∈ states)
    (q : Stmt Γ Λ σ) (A : List (Sigma Γ))
    (hq : ∀ z ∈ pushSymbols states q, z ∈ A)
    (v : σ) (S : ∀ k, List (Γ k)) (hS : Allowed A S) :
    Allowed A (stepAux q v S).stk := by
  induction q generalizing v S with
  | push k f q ih =>
    apply ih (fun z hz => hq z (List.mem_append.mpr (Or.inr hz)))
    apply allowed_update hS
    intro x hx
    rcases List.mem_cons.mp hx with hx | hx
    · subst x
      apply hq
      exact List.mem_append.mpr (Or.inl (List.mem_map.mpr ⟨v, hs v, rfl⟩))
    · exact hS k x hx
  | peek k f q ih => exact ih hq _ _ hS
  | pop k f q ih =>
    apply ih hq
    apply allowed_update hS
    intro x hx
    exact hS k x (List.mem_of_mem_tail hx)
  | load f q ih => exact ih hq _ _ hS
  | branch f q₁ q₂ ih₁ ih₂ =>
    cases h : f v with
    | false =>
      simp only [stepAux, h]
      exact ih₂ (fun z hz => hq z (List.mem_append.mpr (Or.inr hz))) v S hS
    | true =>
      simp only [stepAux, h]
      exact ih₁ (fun z hz => hq z (List.mem_append.mpr (Or.inl hz))) v S hS
  | goto f => exact hS
  | halt => exact hS

def alphabet (labels : List Λ) (states : List σ) (M : Λ → Stmt Γ Λ σ)
    (initialSymbols : List (Sigma Γ)) : List (Sigma Γ) :=
  initialSymbols ++ labels.flatMap (fun l => pushSymbols states (M l))

theorem step_allowed (labels : List Λ) (hl : ∀ l, l ∈ labels)
    (states : List σ) (hs : ∀ v, v ∈ states) (M : Λ → Stmt Γ Λ σ)
    (I : List (Sigma Γ)) (c c' : Cfg Γ Λ σ)
    (hS : Allowed (alphabet labels states M I) c.stk) (h : step M c = some c') :
    Allowed (alphabet labels states M I) c'.stk := by
  cases c with
  | mk l v S =>
    cases l with
    | none => simp [step] at h
    | some l =>
      simp only [step, Option.some.injEq] at h
      subst c'
      apply stepAux_allowed states hs (M l) _ _ v S hS
      intro z hz
      exact List.mem_append.mpr (Or.inr (List.mem_flatMap.mpr ⟨l, hl l, hz⟩))

def run (M : Λ → Stmt Γ Λ σ) : Nat → Cfg Γ Λ σ → Option (Cfg Γ Λ σ)
  | 0, c => some c
  | n+1, c => (step M c).bind (run M n)

theorem all_prefixes_allowed (labels : List Λ) (hl : ∀ l, l ∈ labels)
    (states : List σ) (hs : ∀ v, v ∈ states) (M : Λ → Stmt Γ Λ σ)
    (I : List (Sigma Γ)) (n : Nat) (c c' : Cfg Γ Λ σ)
    (hS : Allowed (alphabet labels states M I) c.stk) (h : run M n c = some c') :
    Allowed (alphabet labels states M I) c'.stk := by
  induction n generalizing c with
  | zero => simp [run] at h; subst c'; exact hS
  | succ n ih =>
    cases he : step M c with
    | none => simp [run, he] at h
    | some d =>
      apply ih d (step_allowed labels hl states hs M I c d hS he)
      simpa [run, he] using h

theorem input_prefixes_allowed (labels : List Λ) (hl : ∀ l, l ∈ labels)
    (states : List σ) (hs : ∀ v, v ∈ states) (M : Λ → Stmt Γ Λ σ)
    (inputSymbols : List (Sigma Γ)) (k₀ : K) (input : List (Γ k₀))
    (hin : ∀ x ∈ input, Sigma.mk k₀ x ∈ inputSymbols)
    (entry : Option Λ) (v : σ) (n : Nat) (c' : Cfg Γ Λ σ)
    (h : run M n ⟨entry, v, update (fun _ => []) k₀ input⟩ = some c') :
    Allowed (alphabet labels states M inputSymbols) c'.stk := by
  apply all_prefixes_allowed labels hl states hs M inputSymbols n _ c' ?_ h
  apply allowed_update
  · intro k x hx
    exact False.elim (List.not_mem_nil hx)
  · intro x hx
    exact List.mem_append.mpr (Or.inl (hin x hx))

def depth : Stmt Γ Λ σ → Nat
  | .push _ _ q | .peek _ _ q | .pop _ _ q | .load _ q => 1 + depth q
  | .branch _ q₁ q₂ => 1 + max (depth q₁) (depth q₂)
  | .goto _ | .halt => 1

def work : Stmt Γ Λ σ → σ → (∀ k, List (Γ k)) → Nat
  | .push k f q, v, S => 1 + work q v (update S k (f v :: S k))
  | .peek k f q, v, S => 1 + work q (f v (S k).head?) S
  | .pop k f q, v, S => 1 + work q (f v (S k).head?) (update S k (S k).tail)
  | .load f q, v, S => 1 + work q (f v) S
  | .branch f q₁ q₂, v, S => 1 + if f v then work q₁ v S else work q₂ v S
  | .goto _, _, _ | .halt, _, _ => 1

theorem work_le_depth (q : Stmt Γ Λ σ) (v : σ) (S : ∀ k, List (Γ k)) :
    work q v S ≤ depth q := by
  induction q generalizing v S with
  | push k f q ih => exact Nat.add_le_add_left (ih _ _) 1
  | peek k f q ih => exact Nat.add_le_add_left (ih _ _) 1
  | pop k f q ih => exact Nat.add_le_add_left (ih _ _) 1
  | load f q ih => exact Nat.add_le_add_left (ih _ _) 1
  | branch f q₁ q₂ ih₁ ih₂ =>
    cases h : f v with
    | false => simp [work, depth, h]; exact Nat.le_trans (ih₂ _ _) (Nat.le_max_right _ _)
    | true => simp [work, depth, h]; exact Nat.le_trans (ih₁ _ _) (Nat.le_max_left _ _)
  | goto f => exact Nat.le_refl _
  | halt => exact Nat.le_refl _

def programBound (labels : List Λ) (M : Λ → Stmt Γ Λ σ) : Nat :=
  (labels.map (fun l => depth (M l))).foldr max 1

theorem member_le_fold_max (xs : List Nat) (n : Nat) (h : n ∈ xs) :
    n ≤ xs.foldr max 1 := by
  induction xs with
  | nil => exact False.elim (List.not_mem_nil h)
  | cons x xs ih =>
    rcases List.mem_cons.mp h with h | h
    · subst n; exact Nat.le_max_left _ _
    · exact Nat.le_trans (ih h) (Nat.le_max_right _ _)

theorem work_le_programBound (labels : List Λ) (hl : ∀ l, l ∈ labels)
    (M : Λ → Stmt Γ Λ σ) (l : Λ) (v : σ) (S : ∀ k, List (Γ k)) :
    work (M l) v S ≤ programBound labels M := by
  apply Nat.le_trans (work_le_depth (M l) v S)
  exact member_le_fold_max _ _ (List.mem_map.mpr ⟨l, hl l, rfl⟩)

#print axioms all_prefixes_allowed
#print axioms input_prefixes_allowed
#print axioms work_le_depth
#print axioms work_le_programBound
end Model
