/-
UniInhabitWs4Sound (lane UNI-INHABIT, Nov 19).  Soundness of the computable LOC replay (UniInhabitWs4Defs.Par) for Uni traces.
A `Model` fixes registers (reg : ℕ → R, a bijection [0,N) ≃ R), frames (ch : ℕ → Ch) and the checker parameters.
`toEv` reads a packed event as a Uni.Ev (ADD = gate with coef e_r + k·e_a, SCALE = gate with coef k·e_r).
* `step_sound` / `run_sound` / `chain_sound`: a successful checker run from a tree related to s gives
  LegalFrom (WordModelDefs.Step, every event's precondition) and the end tree is related to the end state;
  invariants: every birth chart / owned MOVE chart pair / public MOVE chart pair is a frame, owned MOVEs nested.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniTrace
import Nov15.UniInhabitWs4Defs

set_option linter.unusedSectionVars false

namespace UniInhabitWs4
open Uni WordModel Finset

theorem beq_iff (a b : Nat) : Nat.beq a b = true ↔ a = b := by simp [Nat.beq_eq]
theorem blt_iff (a b : Nat) : Nat.blt a b = true ↔ a < b := by simp [Nat.blt_eq]
theorem ble_iff (a b : Nat) : Nat.ble a b = true ↔ a ≤ b := by simp [Nat.ble_eq]

theorem gt_st (d : Nat) : ∀ (t : Tr Nat) (j j' x : Nat), j < 2 ^ d → j' < 2 ^ d →
    gt d (st d t j x) j' = if j' = j then x else gt d t j' := by
  induction d with
  | zero =>
    intro t j j' x hj hj'
    have : j = 0 := by simpa using hj
    have : j' = 0 := by simpa using hj'
    subst j; subst j'; simp [gt, st, Tr.val]
  | succ d ih =>
    intro t j j' x hj hj'
    have hj2 : j / 2 < 2 ^ d := by rw [pow_succ] at hj; omega
    have hj2' : j' / 2 < 2 ^ d := by rw [pow_succ] at hj'; omega
    have key : j' = j ↔ (j' % 2 = j % 2 ∧ j' / 2 = j / 2) := by omega
    by_cases a : j % 2 = 0 <;> by_cases b : j' % 2 = 0
    · have ea : Nat.beq (j % 2) 0 = true := (beq_iff _ _).2 a
      have eb : Nat.beq (j' % 2) 0 = true := (beq_iff _ _).2 b
      simp only [gt, st, ea, eb, cond_true, Tr.lft, Tr.rgt]
      rw [ih _ _ _ _ hj2 hj2']
      by_cases h : j' / 2 = j / 2
      · rw [if_pos h, if_pos (key.2 ⟨by omega, h⟩)]
      · rw [if_neg h, if_neg (fun e => h (key.1 e).2)]
    · have ea : Nat.beq (j % 2) 0 = true := (beq_iff _ _).2 a
      have eb : Nat.beq (j' % 2) 0 = false := by
        cases h : Nat.beq (j' % 2) 0; rfl; exact absurd ((beq_iff _ _).1 h) b
      simp only [gt, st, ea, eb, cond_true, cond_false, Tr.lft, Tr.rgt]
      rw [if_neg (fun e => b (by omega))]
    · have ea : Nat.beq (j % 2) 0 = false := by
        cases h : Nat.beq (j % 2) 0; rfl; exact absurd ((beq_iff _ _).1 h) a
      have eb : Nat.beq (j' % 2) 0 = true := (beq_iff _ _).2 b
      simp only [gt, st, ea, eb, cond_true, cond_false, Tr.lft, Tr.rgt]
      rw [if_neg (fun e => a (by omega))]
    · have ea : Nat.beq (j % 2) 0 = false := by
        cases h : Nat.beq (j % 2) 0; rfl; exact absurd ((beq_iff _ _).1 h) a
      have eb : Nat.beq (j' % 2) 0 = false := by
        cases h : Nat.beq (j' % 2) 0; rfl; exact absurd ((beq_iff _ _).1 h) b
      simp only [gt, st, ea, eb, cond_false, Tr.lft, Tr.rgt]
      rw [ih _ _ _ _ hj2 hj2']
      by_cases h : j' / 2 = j / 2
      · rw [if_pos h, if_pos (key.2 ⟨by omega, h⟩)]
      · rw [if_neg h, if_neg (fun e => h (key.1 e).2)]

theorem Tr.beq_eq : ∀ a b : Tr Nat, Tr.beq a b = true → a = b
  | .lf x, .lf y, h => by simp [Tr.beq, beq_iff] at h; rw [h]
  | .nd l r, .nd l' r', h => by
    simp only [Tr.beq, Bool.and_eq_true] at h
    rw [Tr.beq_eq l l' h.1, Tr.beq_eq r r' h.2]
  | .lf _, .nd _ _, h => by simp [Tr.beq] at h
  | .nd _ _, .lf _, h => by simp [Tr.beq] at h

theorem cond_some {α : Type} {b : Bool} {x : Option α} {y : α} (h : cond b x none = some y) :
    b = true ∧ x = some y := by
  cases b <;> simp_all

/-! ## the model -/

structure Model (R : Type) where
  pb : R → Bool
  reg : ℕ → R
  N : ℕ
  ch : ℕ → Ch
  P : Par

structure Model.OK {R : Type} (M : Model R) : Prop where
  inj : ∀ i j, i < M.N → j < M.N → M.reg i = M.reg j → i = j
  surj : ∀ r, ∃ j < M.N, M.reg j = r
  hpb : ∀ j < M.N, (M.pb (M.reg j) = true ↔ j < M.P.NP)
  hNR : M.P.NR ≤ M.N
  hN : M.N ≤ 2 ^ 11
  hss : ∀ c d, M.P.ssub c d = true → M.ch c < M.ch d

variable {R : Type} [Fintype R] [DecidableEq R]

/-- the coefficient of a packed event. -/
def coefQ (e : PE) : ℚ := (if e.neg then -1 else 1) * (e.num : ℚ) / (e.den : ℚ)

/-- a packed event as a Uni event. -/
def Model.toEv (M : Model R) (e : PE) : Ev R :=
  if e.op = 0 then .birthPub (M.reg e.r) (M.ch e.c)
  else if e.op = 1 then .birthOwn (M.reg e.r) (M.ch e.c)
  else if e.op = 2 then .gate (M.reg e.r) (M.ch e.c) (Pi.single (M.reg e.r) 1 + Pi.single (M.reg e.a) (coefQ e))
  else if e.op = 3 then .gate (M.reg e.r) (M.ch e.c) (Pi.single (M.reg e.r) (coefQ e))
  else if e.op = 4 then
    (if e.r < M.P.NP then .movePub (M.reg e.r) (M.ch e.c) (M.ch e.d) else .moveOwn (M.reg e.r) (M.ch e.c) (M.ch e.d))
  else .clearOwn (M.reg e.r) (M.ch e.c)

def Model.locOf (M : Model R) (k : ℕ) : Loc :=
  if k = 0 then .unborn else if k = 1 then .cleared else .sit (M.ch (k - 2))

def Model.Rel (M : Model R) (s : St R) (t : Tr Nat) : Prop :=
  ∀ j < M.N, s.loc (M.reg j) = M.locOf (gt 11 t j)

def Model.Inv (M : Model R) (s : St R) : Prop :=
  (∀ r c, r ∈ s.B c → ∃ i < M.P.NF, c = M.ch i) ∧
  (∀ m ∈ s.olog, ∃ i i', i < M.P.NF ∧ i' < M.P.NF ∧ m.1 = M.ch i ∧ m.2.1 = M.ch i' ∧ (m.1 < m.2.1 ∨ m.2.1 < m.1)) ∧
  (∀ m ∈ s.plog, ∃ i i', i < M.P.NF ∧ i' < M.P.NF ∧ m.2.1 = M.ch i ∧ m.2.2 = M.ch i')

variable {M : Model R}

theorem rel_update (hM : M.OK) {s : St R} {t : Tr Nat} (h : M.Rel s t) {r k : ℕ} (hr : r < M.N) :
    ∀ j < M.N, Function.update s.loc (M.reg r) (M.locOf k) (M.reg j) = M.locOf (gt 11 (st 11 t r k) j) := by
  intro j hj
  rw [gt_st 11 t r j k (lt_of_lt_of_le hr hM.hN) (lt_of_lt_of_le hj hM.hN)]
  by_cases e : j = r
  · subst e; simp
  · rw [Function.update_of_ne (fun h' => e (hM.inj _ _ hj hr h')), if_neg e, h j hj]

theorem locOf_c2 (c : ℕ) : M.locOf (c + 2) = .sit (M.ch c) := by
  simp [Model.locOf]

theorem step_sound (hM : M.OK) {s : St R} {t t' : Tr Nat} {e : PE} (hst : M.P.step t e = some t')
    (hR : M.Rel s t) (hI : M.Inv s) :
    (M.toEv e).ok M.pb s ∧ M.Rel ((M.toEv e).apply s) t' ∧ M.Inv ((M.toEv e).apply s) := by
  obtain ⟨h1, h2⟩ := cond_some hst
  simp only [Bool.and_eq_true, blt_iff] at h1
  obtain ⟨hr, hc⟩ := h1
  have hrN : e.r < M.N := lt_of_lt_of_le hr hM.hNR
  have hloc := hR e.r hrN
  set l := gt 11 t e.r with hl
  obtain ⟨hB, hO, hP⟩ := hI
  unfold Par.stepOp at h2
  by_cases o0 : e.op = 0
  · have : Nat.beq e.op 0 = true := (beq_iff _ _).2 o0
    simp only [this, cond_true] at h2
    obtain ⟨h3, h4⟩ := cond_some h2
    simp only [Bool.and_eq_true, beq_iff, blt_iff] at h3
    cases h4
    have hev : M.toEv e = .birthPub (M.reg e.r) (M.ch e.c) := by simp [Model.toEv, o0]
    rw [hev]
    refine ⟨⟨by rw [hloc, h3.1]; simp [Model.locOf], (hM.hpb _ hrN).2 h3.2⟩, ?_, ?_⟩
    · intro j hj
      simp only [Ev.apply]
      rw [← locOf_c2]; exact rel_update hM hR hrN j hj
    · refine ⟨?_, hO, hP⟩
      intro r' c' hm
      simp only [Ev.apply] at hm
      by_cases ec : c' = M.ch e.c
      · exact ⟨e.c, hc, ec⟩
      · rw [Function.update_of_ne ec] at hm; exact hB r' c' hm
  have n0 : Nat.beq e.op 0 = false := by cases h : Nat.beq e.op 0; rfl; exact absurd ((beq_iff _ _).1 h) o0
  simp only [n0, cond_false] at h2
  by_cases o1 : e.op = 1
  · have : Nat.beq e.op 1 = true := (beq_iff _ _).2 o1
    simp only [this, cond_true] at h2
    obtain ⟨h3, h4⟩ := cond_some h2
    simp only [Bool.and_eq_true, beq_iff, ble_iff] at h3
    cases h4
    have hev : M.toEv e = .birthOwn (M.reg e.r) (M.ch e.c) := by simp [Model.toEv, o1]
    rw [hev]
    refine ⟨⟨by rw [hloc, h3.1]; simp [Model.locOf], ?_⟩, ?_, ⟨hB, hO, hP⟩⟩
    · cases hp : M.pb (M.reg e.r)
      · rfl
      · have := (hM.hpb _ hrN).1 hp; omega
    · intro j hj
      simp only [Ev.apply]
      rw [← locOf_c2]; exact rel_update hM hR hrN j hj
  have n1 : Nat.beq e.op 1 = false := by cases h : Nat.beq e.op 1; rfl; exact absurd ((beq_iff _ _).1 h) o1
  simp only [n1, cond_false] at h2
  by_cases o23 : e.op = 2 ∨ e.op = 3
  · have : (Nat.beq e.op 2 || Nat.beq e.op 3) = true := by
      simp only [Bool.or_eq_true, beq_iff]; exact o23
    simp only [this, cond_true] at h2
    obtain ⟨h3, h4⟩ := cond_some h2
    simp only [beq_iff] at h3
    cases h4
    have hok : s.loc (M.reg e.r) = .sit (M.ch e.c) := by rw [hloc, h3, locOf_c2]
    rcases o23 with o | o
    · have hev : M.toEv e = .gate (M.reg e.r) (M.ch e.c)
          (Pi.single (M.reg e.r) 1 + Pi.single (M.reg e.a) (coefQ e)) := by simp [Model.toEv, o]
      rw [hev]
      exact ⟨hok, fun j hj => hR j hj, ⟨hB, hO, hP⟩⟩
    · have hev : M.toEv e = .gate (M.reg e.r) (M.ch e.c) (Pi.single (M.reg e.r) (coefQ e)) := by
        simp [Model.toEv, o]
      rw [hev]
      exact ⟨hok, fun j hj => hR j hj, ⟨hB, hO, hP⟩⟩
  have n23 : (Nat.beq e.op 2 || Nat.beq e.op 3) = false := by
    cases h : (Nat.beq e.op 2 || Nat.beq e.op 3); rfl
    simp only [Bool.or_eq_true, beq_iff] at h; exact absurd h o23
  simp only [n23, cond_false] at h2
  push_neg at o23
  by_cases o4 : e.op = 4
  · have : Nat.beq e.op 4 = true := (beq_iff _ _).2 o4
    simp only [this, cond_true] at h2
    obtain ⟨h3, h4⟩ := cond_some h2
    simp only [Bool.and_eq_true, beq_iff, blt_iff] at h3
    obtain ⟨⟨h5, hd⟩, h6⟩ := h3
    cases h4
    have hok : s.loc (M.reg e.r) = .sit (M.ch e.c) := by rw [hloc, h5, locOf_c2]
    have hrel : ∀ j < M.N, Function.update s.loc (M.reg e.r) (.sit (M.ch e.d)) (M.reg j) =
        M.locOf (gt 11 (st 11 t e.r (e.d + 2)) j) := by
      rw [← locOf_c2]; exact rel_update hM hR hrN
    by_cases hpub : e.r < M.P.NP
    · have hpbt : Nat.blt e.r M.P.NP = true := (blt_iff _ _).2 hpub
      simp only [hpbt, cond_true] at h6
      have hev : M.toEv e = .movePub (M.reg e.r) (M.ch e.c) (M.ch e.d) := by simp [Model.toEv, o4, hpub]
      rw [hev]
      refine ⟨⟨hok, (hM.hpb _ hrN).2 hpub, hM.hss _ _ h6⟩, hrel, ⟨hB, hO, ?_⟩⟩
      intro m hm
      simp only [Ev.apply, List.mem_cons] at hm
      obtain hm | hm := hm
      · rw [hm]; exact ⟨e.c, e.d, hc, hd, rfl, rfl⟩
      · exact hP m hm
    · have hpbt : Nat.blt e.r M.P.NP = false := by
        cases h : Nat.blt e.r M.P.NP; rfl; exact absurd ((blt_iff _ _).1 h) hpub
      simp only [hpbt, cond_false, Bool.or_eq_true] at h6
      have hev : M.toEv e = .moveOwn (M.reg e.r) (M.ch e.c) (M.ch e.d) := by simp [Model.toEv, o4, hpub]
      rw [hev]
      refine ⟨⟨hok, ?_⟩, hrel, ⟨hB, ?_, hP⟩⟩
      · cases hp : M.pb (M.reg e.r)
        · rfl
        · exact absurd ((hM.hpb _ hrN).1 hp) hpub
      · intro m hm
        simp only [Ev.apply, List.mem_cons] at hm
        obtain hm | hm := hm
        · rw [hm]; refine ⟨e.c, e.d, hc, hd, rfl, rfl, ?_⟩
          rcases h6 with h6 | h6
          · exact Or.inl (hM.hss _ _ h6)
          · exact Or.inr (hM.hss _ _ h6)
        · exact hO m hm
  have n4 : Nat.beq e.op 4 = false := by cases h : Nat.beq e.op 4; rfl; exact absurd ((beq_iff _ _).1 h) o4
  simp only [n4, cond_false] at h2
  by_cases o5 : e.op = 5
  · have : Nat.beq e.op 5 = true := (beq_iff _ _).2 o5
    simp only [this, cond_true] at h2
    obtain ⟨h3, h4⟩ := cond_some h2
    simp only [Bool.and_eq_true, beq_iff, ble_iff] at h3
    cases h4
    have hev : M.toEv e = .clearOwn (M.reg e.r) (M.ch e.c) := by simp [Model.toEv, o5]
    rw [hev]
    refine ⟨⟨by rw [hloc, h3.1, locOf_c2], ?_⟩, ?_, ⟨hB, hO, hP⟩⟩
    · cases hp : M.pb (M.reg e.r)
      · rfl
      · have := (hM.hpb _ hrN).1 hp; omega
    · intro j hj
      simp only [Ev.apply]
      have : (Loc.cleared : Loc) = M.locOf 1 := by simp [Model.locOf]
      rw [this]; exact rel_update hM hR hrN j hj
  have n5 : Nat.beq e.op 5 = false := by cases h : Nat.beq e.op 5; rfl; exact absurd ((beq_iff _ _).1 h) o5
  simp only [n5, cond_false] at h2
  cases h2

theorem run_sound (hM : M.OK) : ∀ (es : List PE) (s : St R) (t t' : Tr Nat), M.P.run t es = some t' →
    M.Rel s t → M.Inv s →
    LegalFrom M.pb s (es.map M.toEv) ∧ M.Rel (run s (es.map M.toEv)) t' ∧ M.Inv (run s (es.map M.toEv)) := by
  intro es
  induction es with
  | nil =>
    intro s t t' h hR hI
    simp only [Par.run, Option.some.injEq] at h
    subst h
    exact ⟨trivial, hR, hI⟩
  | cons e es ih =>
    intro s t t' h hR hI
    simp only [Par.run] at h
    cases hs : M.P.step t e with
    | none => rw [hs] at h; cases h
    | some t1 =>
      rw [hs] at h
      obtain ⟨hok, hR1, hI1⟩ := step_sound hM hs hR hI
      obtain ⟨a, b, c⟩ := ih _ _ _ h hR1 hI1
      exact ⟨⟨hok, a⟩, b, c⟩

/-- chain of checkpointed segments. -/
def chainOK (P : Par) : Tr Nat → List (List (Nat × Nat) × Tr Nat) → Bool
  | _, [] => true
  | a, (cs, b) :: L => P.seg a cs b && chainOK P b L

def lastCk : Tr Nat → List (List (Nat × Nat) × Tr Nat) → Tr Nat
  | a, [] => a
  | _, (_, b) :: L => lastCk b L

def chainEvs (L : List (List (Nat × Nat) × Tr Nat)) : List PE := (L.map (fun x => decodeAll x.1)).flatten

theorem legalFrom_append (pb : R → Bool) (l1 l2 : Trace R) :
    ∀ s, LegalFrom pb s (l1 ++ l2) ↔ LegalFrom pb s l1 ∧ LegalFrom pb (run s l1) l2 := by
  induction l1 with
  | nil => intro s; simp [LegalFrom, run]
  | cons e l ih =>
    intro s
    simp only [List.cons_append, LegalFrom, run, List.foldl_cons]
    rw [ih]; simp only [run]; tauto

theorem run_append' (s : St R) (l1 l2 : Trace R) : run s (l1 ++ l2) = run (run s l1) l2 := by
  simp [run, List.foldl_append]

theorem chain_sound (hM : M.OK) : ∀ (L : List (List (Nat × Nat) × Tr Nat)) (a : Tr Nat) (s : St R),
    chainOK M.P a L = true → M.Rel s a → M.Inv s →
    LegalFrom M.pb s ((chainEvs L).map M.toEv) ∧ M.Rel (run s ((chainEvs L).map M.toEv)) (lastCk a L) ∧
      M.Inv (run s ((chainEvs L).map M.toEv)) := by
  intro L
  induction L with
  | nil => intro a s _ hR hI; exact ⟨trivial, hR, hI⟩
  | cons x L ih =>
    obtain ⟨cs, b⟩ := x
    intro a s h hR hI
    simp only [chainOK, Bool.and_eq_true] at h
    obtain ⟨hseg, hL⟩ := h
    unfold Par.seg at hseg
    cases hr : M.P.run a (decodeAll cs) with
    | none => rw [hr] at hseg; cases hseg
    | some t =>
      rw [hr] at hseg
      have htb := Tr.beq_eq _ _ hseg
      subst htb
      obtain ⟨l1, r1, i1⟩ := run_sound hM _ s a t hr hR hI
      obtain ⟨l2, r2, i2⟩ := ih t _ hL r1 i1
      have he : (chainEvs ((cs, t) :: L)).map M.toEv = (decodeAll cs).map M.toEv ++ (chainEvs L).map M.toEv := by
        simp [chainEvs]
      rw [he, legalFrom_append, run_append']
      exact ⟨⟨l1, l2⟩, r2, i2⟩

end UniInhabitWs4

#print axioms UniInhabitWs4.chain_sound
