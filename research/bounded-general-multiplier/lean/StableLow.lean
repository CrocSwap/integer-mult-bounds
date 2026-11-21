import Mathlib.Data.List.Count
import Mathlib.Data.Fin.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Data.Fintype.Fin

namespace StableLow

abbrev T := Fin 3

def bucket (xs : List (T × α)) (k : T) : List α :=
  xs.filterMap (fun p ↦ if p.1=k then some p.2 else none)

def replay : List T → (T → List α) → Option (List α × (T → List α))
  | [], q => some ([], q)
  | i::tags, q => do
    let value::rest := q i | none
    let (tail, remainder) ← replay tags (Function.update q i rest)
    return (value::tail, remainder)

theorem consume (xs : List (T × α)) (tail : T → List α) :
    replay (xs.map Prod.fst) (fun k ↦ bucket xs k ++ tail k) =
      some (xs.map Prod.snd,tail) := by
  induction xs with
  | nil => simp [bucket,replay]
  | cons p xs ih =>
    obtain ⟨i,v⟩ := p
    have advance : Function.update (fun k ↦ bucket ((i,v)::xs) k ++ tail k) i
        (bucket xs i ++ tail i) = fun k ↦ bucket xs k ++ tail k := by
      funext k
      by_cases h : i=k
      · subst k; simp
      · simp [Function.update_of_ne (Ne.symm h),bucket,h]
    simp only [List.map_cons,replay]
    have pick : bucket ((i,v)::xs) i ++ tail i = v::(bucket xs i ++ tail i) := by
      simp [bucket]
    rw [pick]
    simp only [advance,ih]
    rfl

def flat (q : T → List α) : List α := q 0 ++ q 1 ++ q 2

def slice (a b : ℕ) (out : List α) (k : T) : List α :=
  if k=0 then out.take a else if k=1 then (out.drop a).take b else out.drop (a+b)

theorem slice_flat (q : T → List α) : slice (q 0).length (q 1).length (flat q) = q := by
  funext i
  fin_cases i <;> simp [slice,flat,List.append_assoc]

def route (rows : List (T × α)) : List α := flat (bucket rows)

/-- The payload may change after its route. A shape-compatible returned
queue for each trit determines one complete restored record sequence. -/
theorem arbitrary_return (tags : List T) (q : T → List α)
    (size : ∀ k, (q k).length=tags.count k) :
    ∃ rows : List (T × α), rows.map Prod.fst=tags ∧
      (∀ k, bucket rows k=q k) ∧
      replay tags (slice (tags.count 0) (tags.count 1) (flat q)) = some (rows.map Prod.snd, fun _ ↦ []) := by
  have find (ts : List T) (qs : T→List α) (h : ∀ k, (qs k).length=ts.count k) :
      ∃ xs : List (T × α), xs.map Prod.fst = ts ∧ ∀ k, bucket xs k = qs k := by
    induction ts generalizing qs with
    | nil =>
      refine ⟨[],rfl,fun k ↦ ?_⟩
      have v := h k
      have empty : qs k=[] := List.length_eq_zero_iff.mp (by simpa only [List.count_nil] using v)
      simp [bucket,empty]
    | cons i ts ih =>
      cases hk : qs i with
      | nil =>
        have positive := h i
        simp [hk] at positive
      | cons v rest =>
        let qs' := Function.update qs i rest
        have sizes (k : T) : (qs' k).length = ts.count k := by
          by_cases e : k=i
          · subst k
            have xp := h i
            simpa [hk,qs'] using xp
          · simpa [qs',e,Ne.symm e] using h k
        obtain ⟨xs,hx,parts⟩ := ih qs' sizes
        refine ⟨(i,v)::xs,by simp [hx],fun k ↦ ?_⟩
        by_cases he : i=k
        · subst k
          have hpart : bucket xs i=rest := by simpa [qs'] using parts i
          simpa [bucket,hk] using congrArg (fun l : List α ↦ v::l) hpart
        · simpa [bucket,he,qs',Ne.symm he] using parts k
  obtain ⟨rows,ht,hq⟩ := find tags q size
  refine ⟨rows,ht,hq,?_⟩
  rw [←size 0,←size 1,slice_flat,←ht]
  simpa only [hq,List.append_nil] using consume rows (fun _ ↦ [])

#print axioms consume
#print axioms slice_flat
#print axioms arbitrary_return
end StableLow
