import Std

namespace CompactRepair

def fill {α : Type} (badAt : Nat → Bool) :
    List Nat → List (Nat × α) → List α → Option (List α)
  | [], [], [] => some []
  | [], _, _ => none
  | q :: qs, bad, good =>
    if badAt q then
      match bad with
      | [] => none
      | (key, value) :: rest =>
        if key = q then (fill badAt qs rest good).map (value :: ·) else none
    else
      match good with
      | [] => none
      | value :: rest => (fill badAt qs bad rest).map (value :: ·)

def Valid {α : Type} (target : Nat → α) (records : List (Nat × α)) : Prop :=
  ∀ kv, kv ∈ records → kv.2 = target kv.1

theorem valid_tail {α : Type} {target : Nat → α} {kv : Nat × α}
    {xs : List (Nat × α)} (h : Valid target (kv :: xs)) : Valid target xs := by
  intro x hx
  exact h x (List.mem_cons_of_mem _ hx)

theorem fill_correct {α : Type} (badAt : Nat → Bool) (target : Nat → α)
    (qs : List Nat) (records : List (Nat × α)) (good out : List α)
    (hg : good = (qs.filter (fun q => !(badAt q))).map target)
    (hv : Valid target records)
    (hf : fill badAt qs records good = some out) : out = qs.map target := by
  induction qs generalizing records good out with
  | nil =>
    simp at hg
    subst good
    cases records <;> simp_all [fill]
  | cons q qs ih =>
    cases hq : badAt q with
    | false =>
      simp [List.filter, hq] at hg
      subst good
      simp only [fill, hq, Bool.false_eq_true, ↓reduceIte] at hf
      cases he : fill badAt qs records ((qs.filter (fun q => !badAt q)).map target) with
      | none => simp [he] at hf
      | some rest =>
        simp [he] at hf
        subst out
        rw [ih records _ rest rfl hv he]
        rfl
    | true =>
      simp [List.filter, hq] at hg
      cases records with
      | nil => simp [fill, hq] at hf
      | cons kv records =>
        rcases kv with ⟨key, value⟩
        by_cases hk : key = q
        · subst key
          have hval : value = target q := hv (q, value) (List.mem_cons_self)
          simp only [fill, hq, ↓reduceIte] at hf
          cases he : fill badAt qs records good with
          | none => simp [he] at hf
          | some rest =>
            simp [he] at hf
            subst out
            rw [hval, ih records good rest hg (valid_tail hv) he]
            rfl
        · simp [fill, hq, hk] at hf

def radixPass {α : Type} (bit : Nat → Bool) (xs : List (Nat × α)) : List (Nat × α) :=
  xs.filter (fun x => !(bit x.1)) ++ xs.filter (fun x => bit x.1)

theorem radixPass_perm {α : Type} (bit : Nat → Bool) (xs : List (Nat × α)) :
    (radixPass bit xs).Perm xs := by
  simpa [radixPass] using List.filter_append_perm (fun x : Nat × α => !(bit x.1)) xs

def radix {α : Type} (bits : List (Nat → Bool)) (xs : List (Nat × α)) : List (Nat × α) :=
  match bits with
  | [] => xs
  | bit :: rest => radix rest (radixPass bit xs)

theorem radix_perm {α : Type} (bits : List (Nat → Bool)) (xs : List (Nat × α)) :
    (radix bits xs).Perm xs := by
  induction bits generalizing xs with
  | nil => exact List.Perm.refl _
  | cons bit rest ih => exact (ih _).trans (radixPass_perm bit xs)

theorem valid_perm {α : Type} {target : Nat → α} {a b : List (Nat × α)}
    (hp : a.Perm b) (hv : Valid target b) : Valid target a := by
  intro x hx
  exact hv x (hp.mem_iff.mp hx)

def extract {α : Type} (badAt : Nat → Bool) (key : Nat → Nat)
    (raw : Nat → α) (qs : List Nat) : List (Nat × α) :=
  (qs.filter badAt).map (fun q => (key q, raw q))

theorem extract_valid {α : Type} (badAt : Nat → Bool) (key : Nat → Nat)
    (raw target : Nat → α) (qs : List Nat)
    (h : ∀ q, badAt q = true → raw q = target (key q)) :
    Valid target (extract badAt key raw qs) := by
  intro kv hkv
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hkv
  exact h q (List.mem_filter.mp hq).2

theorem inverse_key_valid {α : Type} (input : Nat → α) (sinv t tinv : Nat → Nat)
    (ht : ∀ q, tinv (t q) = q) (q : Nat) :
    input (sinv q) = (input ∘ tinv) (t (sinv q)) := by
  simp [ht]

theorem guarded_repair {α : Type} (badAt : Nat → Bool) (qs : List Nat)
    (input : Nat → α) (sinv t tinv : Nat → Nat) (bits : List (Nat → Bool))
    (out : List α) (ht : ∀ q, tinv (t q) = q)
    (hgood : ∀ q, badAt q = false → sinv q = tinv q)
    (hcomplete : fill badAt qs
      (radix bits (extract badAt (t ∘ sinv) (input ∘ sinv) qs))
      ((qs.filter (fun q => !(badAt q))).map (input ∘ sinv)) = some out) :
    out = qs.map (input ∘ tinv) := by
  apply fill_correct badAt (input ∘ tinv) qs _ _ out _ _ hcomplete
  · apply List.map_congr_left
    intro q hq
    have hfalse : badAt q = false := by simpa using (List.mem_filter.mp hq).2
    simp [hgood q hfalse]
  · apply valid_perm (radix_perm _ _)
    apply extract_valid
    intro q _
    exact inverse_key_valid input sinv t tinv ht q

theorem good_inverse_agreement (badAt : Nat → Bool) (s sinv t tinv : Nat → Nat)
    (hs : ∀ q, s (sinv q) = q) (ht : ∀ q, tinv (t q) = q)
    (hpres : ∀ q, badAt (s q) = badAt q)
    (hagree : ∀ q, badAt q = false → s q = t q)
    (q : Nat) (hq : badAt q = false) : sinv q = tinv q := by
  have hb : badAt (sinv q) = false := by
    rw [← hpres (sinv q), hs q, hq]
  have hdest : t (sinv q) = q := (hagree (sinv q) hb).symm.trans (hs q)
  exact (ht (sinv q)).symm.trans (congrArg tinv hdest)

theorem guarded_compact_repair {α : Type} (badAt : Nat → Bool) (qs : List Nat)
    (input : Nat → α) (s sinv t tinv : Nat → Nat) (bits : List (Nat → Bool))
    (out : List α) (hs : ∀ q, s (sinv q) = q) (ht : ∀ q, tinv (t q) = q)
    (hpres : ∀ q, badAt (s q) = badAt q)
    (hagree : ∀ q, badAt q = false → s q = t q)
    (hcomplete : fill badAt qs
      (radix bits (extract badAt (t ∘ sinv) (input ∘ sinv) qs))
      ((qs.filter (fun q => !(badAt q))).map (input ∘ sinv)) = some out) :
    out = qs.map (input ∘ tinv) := by
  apply guarded_repair badAt qs input sinv t tinv bits out ht _ hcomplete
  exact good_inverse_agreement badAt s sinv t tinv hs ht hpres hagree

end CompactRepair

#print axioms CompactRepair.fill_correct
#print axioms CompactRepair.radix_perm
#print axioms CompactRepair.guarded_repair
#print axioms CompactRepair.guarded_compact_repair
