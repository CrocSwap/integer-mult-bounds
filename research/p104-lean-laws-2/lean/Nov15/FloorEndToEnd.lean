/-
Class-K floor, end to end on the word (lane LEAN-NEXT17, Nov 16). See FloorEndToEnd.md.

A global multi-chart op model with the shipped verifier's legality (independent.py `native()`, incl.
l.51: public MOVEs strictly climb, owned MOVEs nested either way), the class-K definition, and the
three kept LP row families (R1 local rank, R3 hop rows α/β, F4 single-source u rows) as theorems about
the WORD. Floor/FloorGlue's hypotheses hOnce, class N, ρ kills helper tokens, `hent`, hP, hvec, the
memberships in S_c and the hd/fibre identity are DERIVED here.

Build (oleans of ExportLaw, Floor, FloorGlue must exist):
  lake env lean -o .lake/build/lib/lean/Nov15/FloorEndToEnd.olean Nov15/FloorEndToEnd.lean
-/
import Nov15.FloorGlue

open Finset Module Submodule

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace FloorE2E

/-! ## 1. Global model -/

/-- Verifier ops (independent.py): INIT (owned, row 0), CLEAR (owned leaves), MOVE, ADD `i += a·j`,
SCALE `i := u·i`, COPY `i := a·j`. Rows are in initial-row coordinates. -/
inductive GEv (K Reg C : Type*)
  | init (o : Reg) (c : C)
  | clear (o : Reg)
  | move (r : Reg) (c : C)
  | add (i j : Reg) (a : K)
  | scale (i : Reg) (u : K)
  | copy (i j : Reg) (a : K)

structure GSt (K Reg C : Type*) where
  row : Reg → Reg → K
  loc : Reg → Option C

variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

def gstep (s : GSt K Reg C) : GEv K Reg C → GSt K Reg C
  | .init o c => ⟨Function.update s.row o 0, Function.update s.loc o (some c)⟩
  | .clear o => ⟨s.row, Function.update s.loc o none⟩
  | .move r c => ⟨s.row, Function.update s.loc r (some c)⟩
  | .add i j a => ⟨Function.update s.row i (s.row i + a • s.row j), s.loc⟩
  | .scale i u => ⟨Function.update s.row i (u • s.row i), s.loc⟩
  | .copy i j a => ⟨Function.update s.row i (a • s.row j), s.loc⟩

def grun : GSt K Reg C → List (GEv K Reg C) → GSt K Reg C
  | s, [] => s
  | s, e :: es => grun (gstep s e) es

/-- Legality of one op, as independent.py `native()` checks it (coefficient-size/smoothness checks
dropped: the model is a relaxation). `Pub` = public registers. l.51: a public MOVE goes from
frame a to b with a ⊊ b; an owned MOVE with a ⊊ b or b ⊊ a. -/
def LegalEvG (Pub : Finset Reg) (s : GSt K Reg C) : GEv K Reg C → Prop
  | .init o _ => o ∉ Pub ∧ s.loc o = none
  | .clear o => o ∉ Pub ∧ s.loc o ≠ none
  | .move r c => ∃ a, s.loc r = some a ∧ (r ∈ Pub → a < c) ∧ (r ∉ Pub → a < c ∨ c < a)
  | .add i j _ => i ≠ j ∧ s.loc i ≠ none ∧ s.loc i = s.loc j
  | .scale i u => u ≠ 0 ∧ s.loc i ≠ none
  | .copy i j a => a ≠ 0 ∧ i ≠ j ∧ s.loc i ≠ none ∧ s.loc i = s.loc j

def LegalG (Pub : Finset Reg) : GSt K Reg C → List (GEv K Reg C) → Prop
  | _, [] => True
  | s, e :: es => LegalEvG Pub s e ∧ LegalG Pub (gstep s e) es

/-- initial state: public registers at their initial frame with their own token; owned absent. -/
def s0 (ini : Reg → Option C) : GSt K Reg C := ⟨fun r => Pi.single r 1, ini⟩

/-! ## 2. Projection to one chart and simulation of ExportLaw's one-chart model -/

abbrev LEv (K Reg : Type*) := ExportLaw.Ev K Reg
abbrev LSt (K Reg : Type*) := ExportLaw.St K Reg

/-- the one-chart events at `c` produced by a global op. -/
def pev (c : C) (s : GSt K Reg C) : GEv K Reg C → List (LEv K Reg)
  | .init o c' => if c' = c then [.arrive o 0] else []
  | .clear o => if s.loc o = some c then [.depart o] else []
  | .move r c' => (if s.loc r = some c then [.depart r] else []) ++
      (if c' = c then [.arrive r (s.row r)] else [])
  | .add i j a => if s.loc i = some c then [.add i j a] else []
  | .scale i u => if s.loc i = some c then [.scale i u] else []
  | .copy i j a => if s.loc i = some c then [.copy i j, .scale i a] else []

def projFrom (c : C) : GSt K Reg C → List (GEv K Reg C) → List (LEv K Reg)
  | _, [] => []
  | s, e :: es => pev c s e ++ projFrom c (gstep s e) es

/-- the registers born at `c` (public registers whose initial frame is `c`). -/
def bornAt (c : C) (ini : Reg → Option C) : Finset Reg := univ.filter fun r => ini r = some c

noncomputable def births (c : C) (ini : Reg → Option C) : List (LEv K Reg) :=
  (bornAt c ini).toList.map .born

/-- the event list of chart `c` (ExportLaw's model, from the empty state). -/
noncomputable def proj (c : C) (ini : Reg → Option C) (w : List (GEv K Reg C)) : List (LEv K Reg) :=
  births c ini ++ projFrom c (s0 ini) w

def Sim (c : C) (s : GSt K Reg C) (t : LSt K Reg) : Prop :=
  (∀ r, r ∈ t.pres ↔ s.loc r = some c) ∧ ∀ r, s.loc r = some c → t.row r = s.row r

open ExportLaw in
lemma run_append (t : LSt K Reg) (l1 l2 : List (LEv K Reg)) :
    run t (l1 ++ l2) = run (run t l1) l2 := by
  induction l1 generalizing t with
  | nil => rfl
  | cons e l ih => exact ih _

open ExportLaw in
lemma legal_append (t : LSt K Reg) (l1 l2 : List (LEv K Reg)) :
    Legal t (l1 ++ l2) ↔ Legal t l1 ∧ Legal (run t l1) l2 := by
  induction l1 generalizing t with
  | nil => simp [Legal, run]
  | cons e l ih => simp only [List.cons_append, Legal, run, ih, and_assoc]

open ExportLaw in
lemma held_append_right (t : LSt K Reg) (l1 l2 : List (LEv K Reg)) :
    held (run t l1) l2 ⊆ held t (l1 ++ l2) := by
  induction l1 generalizing t with
  | nil => exact le_rfl
  | cons e l ih => exact (ih _).trans Set.subset_union_right

open ExportLaw in
lemma held_append_left (t : LSt K Reg) (l1 l2 : List (LEv K Reg)) :
    held t l1 ⊆ held t (l1 ++ l2) := by
  induction l1 generalizing t with
  | nil => exact cur_sub_held t l2
  | cons e l ih => exact Set.union_subset_union le_rfl (ih _)

open ExportLaw in
lemma entRows_append (l1 l2 : List (LEv K Reg)) :
    entRows (l1 ++ l2) = entRows l1 ++ entRows l2 := by
  induction l1 with
  | nil => rfl
  | cons e l ih => cases e <;> simp [entRows, ih]

open ExportLaw in
lemma nEnt_append (S : Finset Reg) (l1 l2 : List (LEv K Reg)) :
    nEnt S (l1 ++ l2) = nEnt S l1 + nEnt S l2 := by
  induction l1 with
  | nil => simp [nEnt]
  | cons e l ih => cases e <;> simp [nEnt, ih] <;> omega

open ExportLaw in
lemma nDep_append (S : Finset Reg) (l1 l2 : List (LEv K Reg)) :
    nDep S (l1 ++ l2) = nDep S l1 + nDep S l2 := by
  induction l1 with
  | nil => simp [nDep]
  | cons e l ih => cases e <;> simp [nDep, ih] <;> omega

open ExportLaw in
lemma bornSet_append (l1 l2 : List (LEv K Reg)) :
    bornSet (l1 ++ l2) = bornSet l1 ∪ bornSet l2 := by
  induction l1 with
  | nil => simp [bornSet]
  | cons e l ih => cases e <;> simp [bornSet, ih, Finset.insert_union]

open ExportLaw in
/-- every entering row is held. -/
lemma entRows_held : ∀ (t : LSt K Reg) (l : List (LEv K Reg)), ∀ v ∈ entRows l, v ∈ held t l
  | t, [], v, h => by simp [entRows] at h
  | t, .arrive i u :: l, v, h => by
    simp only [entRows, List.mem_cons] at h
    rcases h with rfl | h
    · exact Set.mem_union_right _ (cur_sub_held _ l ⟨i, by simp [step], by simp [step]⟩)
    · exact Set.mem_union_right _ (entRows_held _ l v h)
  | t, .born b :: l, v, h => by
    simp only [entRows, List.mem_cons] at h
    rcases h with rfl | h
    · exact Set.mem_union_right _ (cur_sub_held _ l ⟨b, by simp [step], by simp [step]⟩)
    · exact Set.mem_union_right _ (entRows_held _ l v h)
  | t, .add _ _ _ :: l, v, h => Set.mem_union_right _ (entRows_held _ l v h)
  | t, .scale _ _ :: l, v, h => Set.mem_union_right _ (entRows_held _ l v h)
  | t, .depart _ :: l, v, h => Set.mem_union_right _ (entRows_held _ l v h)
  | t, .clear _ :: l, v, h => Set.mem_union_right _ (entRows_held _ l v h)
  | t, .copy _ _ :: l, v, h => Set.mem_union_right _ (entRows_held _ l v h)

open ExportLaw in
/-- **one-step simulation**: a legal global op projects to a legal one-chart event list, and the
projected state still tracks the registers located at `c`. -/
theorem step_sim (Pub : Finset Reg) (c : C) (s : GSt K Reg C) (e : GEv K Reg C) (t : LSt K Reg)
    (hL : LegalEvG Pub s e) (hS : Sim c s t) :
    Legal t (pev c s e) ∧ Sim c (gstep s e) (run t (pev c s e)) := by
  obtain ⟨hP, hR⟩ := hS
  cases e with
  | init o c' =>
    obtain ⟨-, ho⟩ := hL
    by_cases hc : c' = c
    · subst hc
      refine ⟨?_, ?_, ?_⟩
      · simp only [pev, ↓reduceIte, Legal, LegalEv]; exact ⟨by rw [hP]; simp [ho], trivial⟩
      · intro r; by_cases hr : r = o
        · subst hr; simp [pev, run, step, gstep]
        · simp [pev, run, step, gstep, hr, hP]
      · intro r hr; by_cases hro : r = o
        · subst hro; simp [pev, run, step, gstep]
        · simp only [gstep, Function.update_of_ne hro] at hr ⊢
          simp [pev, run, step, Function.update_of_ne hro, hR r hr]
    · refine ⟨by simp [pev, hc, Legal], ?_, ?_⟩
      · intro r; by_cases hr : r = o
        · subst hr; simp [pev, hc, run, gstep, hP, ho, Ne.symm hc]
        · simp [pev, hc, run, gstep, hr, hP]
      · intro r hr; by_cases hro : r = o
        · subst hro; simp [gstep, hc] at hr
        · simp only [gstep, Function.update_of_ne hro] at hr ⊢
          simp [pev, hc, run, hR r hr]
  | clear o =>
    by_cases hc : s.loc o = some c
    · refine ⟨?_, ?_, ?_⟩
      · simp only [pev, hc, ↓reduceIte, Legal, LegalEv]; exact ⟨by rw [hP]; exact hc, trivial⟩
      · intro r; by_cases hr : r = o
        · subst hr; simp [pev, hc, run, step, gstep]
        · simp [pev, hc, run, step, gstep, hr, hP]
      · intro r hr; by_cases hro : r = o
        · subst hro; simp [gstep] at hr
        · simp only [gstep, Function.update_of_ne hro] at hr ⊢
          simp [pev, hc, run, step, hR r hr]
    · refine ⟨by simp [pev, hc, Legal], ?_, ?_⟩
      · intro r; by_cases hr : r = o
        · subst hr; simp [pev, hc, run, gstep, hP]
        · simp [pev, hc, run, gstep, hr, hP]
      · intro r hr; by_cases hro : r = o
        · subst hro; simp [gstep] at hr
        · simp only [gstep, Function.update_of_ne hro] at hr ⊢
          simp [pev, hc, run, hR r hr]
  | move m c' =>
    obtain ⟨a, ha, h1, h2⟩ := hL
    have hac : a ≠ c' := by
      by_cases hm : m ∈ Pub
      · exact (h1 hm).ne
      · rcases h2 hm with h | h
        · exact h.ne
        · exact h.ne'
    by_cases hc : a = c
    · subst hc
      have hc' : c' ≠ a := Ne.symm hac
      refine ⟨?_, ?_, ?_⟩
      · simp only [pev, ha, hc', ↓reduceIte, List.append_nil, Legal, LegalEv]
        exact ⟨by rw [hP]; exact ha, trivial⟩
      · intro r; by_cases hr : r = m
        · subst hr; simp [pev, ha, hc', run, step, gstep]
        · simp [pev, ha, hc', run, step, gstep, hr, hP]
      · intro r hr; by_cases hro : r = m
        · subst hro; simp [gstep, hc'] at hr
        · simp only [gstep, Function.update_of_ne hro] at hr ⊢
          simp [pev, ha, hc', run, step, hR r hr]
    · have hmc : s.loc m ≠ some c := by rw [ha]; simpa using hc
      by_cases hc' : c' = c
      · subst hc'
        refine ⟨?_, ?_, ?_⟩
        · simp only [pev, hmc, ↓reduceIte, List.nil_append, Legal, LegalEv]
          exact ⟨by rw [hP]; exact hmc, trivial⟩
        · intro r; by_cases hr : r = m
          · subst hr; simp [pev, hmc, run, step, gstep]
          · simp [pev, hmc, run, step, gstep, hr, hP]
        · intro r hr; by_cases hro : r = m
          · subst hro; simp [pev, hmc, run, step, gstep]
          · simp only [gstep, Function.update_of_ne hro] at hr ⊢
            simp [pev, hmc, run, step, Function.update_of_ne hro, hR r hr]
      · refine ⟨by simp [pev, hmc, hc', Legal], ?_, ?_⟩
        · intro r; by_cases hr : r = m
          · subst hr; simp [pev, hmc, hc', run, gstep, hP, Ne.symm hc']
          · simp [pev, hmc, hc', run, gstep, hr, hP]
        · intro r hr; by_cases hro : r = m
          · subst hro; simp [gstep, hc'] at hr
          · simp only [gstep, Function.update_of_ne hro] at hr ⊢
            simp [pev, hmc, hc', run, hR r hr]
  | add i j a =>
    obtain ⟨hij, -, hji⟩ := hL
    by_cases hc : s.loc i = some c
    · have hjc : s.loc j = some c := hji ▸ hc
      refine ⟨?_, ?_, ?_⟩
      · simp only [pev, hc, ↓reduceIte, Legal, LegalEv]
        exact ⟨⟨hij, (hP i).2 hc, (hP j).2 hjc⟩, trivial⟩
      · intro r; simp [pev, hc, run, step, gstep, hP]
      · intro r hr
        simp only [gstep] at hr
        by_cases hro : r = i
        · subst hro; simp [pev, hc, run, step, gstep, hR r hr, hR j hjc]
        · simp [pev, hc, run, step, gstep, Function.update_of_ne hro, hR r hr]
    · refine ⟨by simp [pev, hc, Legal], ?_, ?_⟩
      · intro r; simp [pev, hc, run, gstep, hP]
      · intro r hr
        simp only [gstep] at hr
        have hro : r ≠ i := fun h => hc (h ▸ hr)
        simp [pev, hc, run, gstep, Function.update_of_ne hro, hR r hr]
  | scale i u =>
    obtain ⟨hu, -⟩ := hL
    by_cases hc : s.loc i = some c
    · refine ⟨?_, ?_, ?_⟩
      · simp only [pev, hc, ↓reduceIte, Legal, LegalEv]
        exact ⟨⟨hu, (hP i).2 hc⟩, trivial⟩
      · intro r; simp [pev, hc, run, step, gstep, hP]
      · intro r hr
        simp only [gstep] at hr
        by_cases hro : r = i
        · subst hro; simp [pev, hc, run, step, gstep, hR r hr]
        · simp [pev, hc, run, step, gstep, Function.update_of_ne hro, hR r hr]
    · refine ⟨by simp [pev, hc, Legal], ?_, ?_⟩
      · intro r; simp [pev, hc, run, gstep, hP]
      · intro r hr
        simp only [gstep] at hr
        have hro : r ≠ i := fun h => hc (h ▸ hr)
        simp [pev, hc, run, gstep, Function.update_of_ne hro, hR r hr]
  | copy i j a =>
    obtain ⟨ha, -, -, hji⟩ := hL
    by_cases hc : s.loc i = some c
    · have hjc : s.loc j = some c := hji ▸ hc
      refine ⟨?_, ?_, ?_⟩
      · simp only [pev, hc, ↓reduceIte, Legal, LegalEv]
        exact ⟨⟨(hP i).2 hc, (hP j).2 hjc⟩, ⟨ha, by simpa [step] using (hP i).2 hc⟩, trivial⟩
      · intro r; simp [pev, hc, run, step, gstep, hP]
      · intro r hr
        simp only [gstep] at hr
        by_cases hro : r = i
        · subst hro; simp [pev, hc, run, step, gstep, hR j hjc]
        · simp [pev, hc, run, step, gstep, Function.update_of_ne hro, hR r hr]
    · refine ⟨by simp [pev, hc, Legal], ?_, ?_⟩
      · intro r; simp [pev, hc, run, gstep, hP]
      · intro r hr
        simp only [gstep] at hr
        have hro : r ≠ i := fun h => hc (h ▸ hr)
        simp [pev, hc, run, gstep, Function.update_of_ne hro, hR r hr]

open ExportLaw in
theorem proj_sim (Pub : Finset Reg) (c : C) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C))
    (t : LSt K Reg), LegalG Pub s w → Sim c s t →
    Legal t (projFrom c s w) ∧ Sim c (grun s w) (run t (projFrom c s w))
  | s, [], t, _, hS => ⟨by simp [projFrom, Legal], by simpa [projFrom, grun, run] using hS⟩
  | s, e :: es, t, ⟨he, hL⟩, hS => by
    obtain ⟨h1, h2⟩ := step_sim Pub c s e t he hS
    obtain ⟨h3, h4⟩ := proj_sim Pub c (gstep s e) es _ hL h2
    refine ⟨(legal_append _ _ _).2 ⟨h1, h3⟩, ?_⟩
    simp only [projFrom, grun, run_append]; exact h4

open ExportLaw in
lemma births_aux (t : LSt K Reg) : ∀ (l : List Reg), l.Nodup → (∀ r ∈ l, r ∉ t.pres) →
    Legal t (l.map .born) ∧ (∀ r, r ∈ (run t (l.map .born)).pres ↔ r ∈ t.pres ∨ r ∈ l) ∧
    ∀ r, (run t (l.map .born)).row r = if r ∈ l then Pi.single r 1 else t.row r
  | [], _, _ => by simp [Legal, run]
  | b :: l, hnd, hab => by
    obtain ⟨hb, hnd'⟩ := List.nodup_cons.1 hnd
    have hab' : ∀ r ∈ l, r ∉ (step t (.born b)).pres := by
      intro r hr
      simp only [step, Finset.mem_insert]
      rintro (rfl | h)
      · exact hb hr
      · exact hab r (List.mem_cons_of_mem _ hr) h
    obtain ⟨h1, h2, h3⟩ := births_aux (step t (.born b)) l hnd' hab'
    refine ⟨⟨hab b (by simp), h1⟩, ?_, ?_⟩
    · intro r; simp only [List.map_cons, run]; rw [h2]; simp only [step, Finset.mem_insert,
        List.mem_cons]; tauto
    · intro r; simp only [List.map_cons, run]; rw [h3]
      by_cases hr : r ∈ l
      · simp [hr]
      · by_cases hrb : r = b
        · subst hrb; simp [step]
        · simp [hr, hrb, step, Function.update_of_ne hrb]

open ExportLaw in
theorem births_sim (c : C) (ini : Reg → Option C) :
    Legal start (births (K := K) c ini) ∧ Sim c (s0 ini) (run start (births (K := K) c ini)) := by
  obtain ⟨h1, h2, h3⟩ := births_aux (K := K) (start (K := K) (Reg := Reg))
    (bornAt c ini).toList (Finset.nodup_toList _) (by simp [start])
  unfold births
  refine ⟨h1, fun r => ?_, fun r hr => ?_⟩
  · rw [h2]; simp [start, bornAt, s0]
  · rw [h3]; simp only [s0] at hr ⊢; simp [bornAt, hr]

open ExportLaw in
/-- **the chart-`c` list of a legal word is a legal ExportLaw run from the empty state, and its final
state holds exactly the registers ending at `c`, with their global rows.** -/
theorem proj_legal (Pub : Finset Reg) (c : C) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (hL : LegalG Pub (s0 ini) w) :
    Legal start (proj c ini w) ∧ Sim c (grun (s0 ini) w) (run start (proj c ini w)) := by
  obtain ⟨h1, h2⟩ := births_sim (K := K) c ini
  obtain ⟨h3, h4⟩ := proj_sim Pub c _ w _ hL h2
  exact ⟨(legal_append _ _ _).2 ⟨h1, h3⟩, by rw [proj, run_append]; exact h4⟩

/-! ## 3b. Sharpened forward count: zero-row entries (owned INITs) are free

ExportLaw.forward_count bounds dim S_c by ALL entries; an owned INIT enters with row 0 and adds
nothing to the span. The data (rsdata.py / indep_word.py) counts oa = owned MOVE arrivals only, so the
floor needs this sharper count. -/

open ExportLaw in
lemma filter_ne_zero_length (l : List (Reg → K)) :
    (l.filter fun v => v ≠ 0).length + l.count 0 = l.length := by
  rw [← List.countP_eq_length_filter, List.count_eq_countP,
    List.length_eq_countP_add_countP (fun v => decide (v ≠ 0)) (l := l)]
  congr 1
  apply List.countP_congr
  intro v _
  simp

open ExportLaw in
theorem forward_count' (φ : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (LEv K Reg))
    (hL : Legal start evs) (Tk : Finset Reg)
    (hTk : ∀ t ∈ Tk, (Pi.single t 1 : Reg → K) ∈ held start evs)
    (hφ : ∀ t ∈ Tk, φ (Pi.single t 1) = 0) :
    finrank K ((span K (held start evs)).map φ) + Tk.card ≤
      nEnt univ evs - (entRows evs).count 0 := by
  classical
  have hfz := filter_ne_zero_length (entRows evs)
  rw [entRows_length] at hfz
  set l := (entRows evs).filter fun v => v ≠ 0
  have hlen : l.length = nEnt univ evs - (entRows evs).count 0 := by omega
  have hAc : finrank K (span K {v | v ∈ l}) ≤ l.length := by
    have eqA : span K {v | v ∈ l} = span K (((l.toFinset : Finset (Reg → K)) : Set (Reg → K))) := by
      congr 1; ext v; simp
    rw [eqA]
    exact (finrank_span_finset_le_card _).trans (List.toFinset_card_le _)
  set A := span K {v | v ∈ l}
  have hSA : held start evs ⊆ A := by
    refine forward_span A start evs hL (by simp [cur, start]) (fun v hv => ?_)
    by_cases h0 : v = 0
    · rw [h0]; exact A.zero_mem
    · exact Submodule.subset_span (show v ∈ l from List.mem_filter.2 ⟨hv, by simpa using h0⟩)
  let f := φ.domRestrict A
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have hrange : LinearMap.range f = A.map φ := LinearMap.range_domRestrict A φ
  have hker : Tk.card ≤ finrank K (LinearMap.ker f) := by
    let g : Tk → LinearMap.ker f := fun t =>
      ⟨⟨Pi.single t.1 1, hSA (hTk t.1 t.2)⟩, by simp [f, hφ t.1 t.2]⟩
    have hli : LinearIndependent K g := by
      apply LinearIndependent.of_comp ((LinearMap.ker f).subtype)
      apply LinearIndependent.of_comp A.subtype
      have e : (⇑A.subtype ∘ ⇑(LinearMap.ker f).subtype ∘ g) = (Pi.basisFun K Reg) ∘ Subtype.val := by
        funext t; simp [g]
      rw [e]; exact (Pi.basisFun K Reg).linearIndependent.comp _ Subtype.val_injective
    simpa using hli.fintype_card_le_finrank
  have hmono : finrank K ((span K (held start evs)).map φ) ≤ finrank K (A.map φ) :=
    Submodule.finrank_mono (Submodule.map_mono (Submodule.span_le.mpr hSA))
  rw [← hrange] at hmono
  omega

open ExportLaw in
/-- FloorGlue.entry_count with oa sharpened to (owned entries − zero-row entries). -/
theorem entry_count' (evs : List (LEv K Reg)) (hL : Legal start evs)
    (H Kp Ow : Finset Reg) (hHK : Disjoint H Kp) (hHO : Disjoint H Ow) (hKO : Disjoint Kp Ow)
    (hcov : H ∪ Kp ∪ Ow = univ) (hOnce : ∀ i ∈ Kp, nEnt {i} evs ≤ 1) :
    finrank K (span K (held start evs)) ≤
      (nDep H evs - ((H ∩ bornSet evs) \ (run start evs).pres).card)
      + ((run start evs).pres ∩ H).card
      + ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs).card
      + (nEnt Ow evs - (entRows evs).count 0)
      + ((H ∩ bornSet evs) \ (run start evs).pres).card
      + (Kp ∩ bornSet evs).card := by
  classical
  obtain ⟨hHB, -⟩ := FloorGlue.entry_count evs hL H Kp Ow hHK hHO hKO hcov hOnce
  set F := (run (start (K := K) (Reg := Reg)) evs).pres
  set HB := (H ∩ bornSet evs) \ F
  have fc := forward_count' (K := K) LinearMap.id evs hL ∅ (by simp) (by simp)
  rw [Submodule.map_id, Finset.card_empty, add_zero] at fc
  have hsplit : nEnt univ evs = nEnt H evs + nEnt Kp evs + nEnt Ow evs := by
    rw [FloorGlue.nEnt_eq_sum, FloorGlue.nEnt_eq_sum H, FloorGlue.nEnt_eq_sum Kp,
      FloorGlue.nEnt_eq_sum Ow, ← hcov,
      Finset.sum_union (Finset.disjoint_union_left.2 ⟨hHO, hKO⟩), Finset.sum_union hHK]
  have hH : nEnt H evs = nDep H evs + (F ∩ H).card := by
    have := stay_count (K := K) H start evs hL
    have h0 : (start (K := K) (Reg := Reg)).pres = ∅ := rfl
    rw [h0] at this; simpa using this
  have hKp : nEnt Kp evs ≤ ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs).card
      + (Kp ∩ bornSet evs).card := by
    rw [FloorGlue.nEnt_eq_sum]
    have h1 : ∑ i ∈ Kp, nEnt {i} evs ≤ (Kp.filter fun i => 0 < nEnt {i} evs).card := by
      rw [Finset.card_filter]
      exact Finset.sum_le_sum fun i hi => by
        have := hOnce i hi
        split_ifs with h <;> omega
    have h2 : (Kp.filter fun i => 0 < nEnt {i} evs) ⊆
        ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs) ∪ (Kp ∩ bornSet evs) := by
      intro i hi
      obtain ⟨hiK, hpos⟩ := Finset.mem_filter.1 hi
      by_cases hb : i ∈ bornSet evs
      · exact Finset.mem_union_right _ (Finset.mem_inter.2 ⟨hiK, hb⟩)
      · exact Finset.mem_union_left _ (Finset.mem_filter.2 ⟨Finset.mem_sdiff.2 ⟨hiK, hb⟩, hpos⟩)
    exact h1.trans ((Finset.card_le_card h2).trans (Finset.card_union_le _ _))
  omega

open ExportLaw in
/-- FloorGlue.chart_floor with the sharpened oa. -/
theorem chart_floor' {W : Type*} [AddCommGroup W] [Module K W] (ρ : (Reg → K) →ₗ[K] W)
    (evs : List (LEv K Reg)) (hL : Legal start evs)
    (H Kp Ow : Finset Reg) (hHK : Disjoint H Kp) (hHO : Disjoint H Ow) (hKO : Disjoint Kp Ow)
    (hcov : H ∪ Kp ∪ Ow = univ) (hOnce : ∀ i ∈ Kp, nEnt {i} evs ≤ 1)
    (hN : ∀ h ∈ H, h ∈ (run start evs).pres → (run start evs).row h = Pi.single h 1)
    (hρ : ∀ h ∈ H, ρ (Pi.single h 1) = 0)
    (X : Set (Reg → K)) (hX : X ⊆ held start evs) :
    finrank K (span K (ρ '' X)) ≤
      (nDep H evs - ((H ∩ bornSet evs) \ (run start evs).pres).card)
      + ((Kp \ bornSet evs).filter fun i => 0 < nEnt {i} evs).card
      + (nEnt Ow evs - (entRows evs).count 0) + (Kp ∩ bornSet evs).card := by
  classical
  set F := (run (start (K := K) (Reg := Reg)) evs).pres
  set HB := (H ∩ bornSet evs) \ F
  have hent := entry_count' evs hL H Kp Ow hHK hHO hKO hcov hOnce
  set Tok := (F ∩ H) ∪ HB
  have hdisj : Disjoint (F ∩ H) HB := by
    rw [Finset.disjoint_left]
    intro x hx hx'
    exact (Finset.mem_sdiff.1 hx').2 (Finset.mem_inter.1 hx).1
  have hTokc : Tok.card = (F ∩ H).card + HB.card := Finset.card_union_of_disjoint hdisj
  have hTokS : ∀ i ∈ Tok, (Pi.single i 1 : Reg → K) ∈ span K (held start evs) := by
    intro i hi
    apply Submodule.subset_span
    rcases Finset.mem_union.1 hi with h | h
    · obtain ⟨hF, hH⟩ := Finset.mem_inter.1 h
      have : (run start evs).row i ∈ cur (run start evs) := ⟨i, hF, rfl⟩
      rw [hN i hH hF] at this
      exact final_sub_held start evs this
    · exact born_held start evs i (Finset.mem_inter.1 (Finset.mem_sdiff.1 h).1).2
  have hTokρ : ∀ i ∈ Tok, ρ (Pi.single i 1) = 0 := by
    intro i hi
    rcases Finset.mem_union.1 hi with h | h
    · exact hρ i (Finset.mem_inter.1 h).2
    · exact hρ i (Finset.mem_inter.1 (Finset.mem_sdiff.1 h).1).1
  exact Floor.stay_floor ρ (span K (held start evs)) X Tok _ _ _ _ _ _
    (hX.trans Submodule.subset_span) hTokS hTokρ hTokc hent

/-! ## 3. States visited, MOVE records -/

def snaps : GSt K Reg C → List (GEv K Reg C) → List (GSt K Reg C)
  | s, [] => [s]
  | s, e :: es => s :: snaps (gstep s e) es

open ExportLaw in
/-- every row of a register located at `c` at any visited state is held at `c` (in S_c). -/
theorem snap_held (Pub : Finset Reg) (c : C) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C))
    (t : LSt K Reg), LegalG Pub s w → Sim c s t →
    ∀ st ∈ snaps s w, ∀ r, st.loc r = some c → st.row r ∈ held t (projFrom c s w)
  | s, [], t, _, hS, st, hst, r, hr => by
    simp only [snaps, List.mem_singleton] at hst; subst hst
    exact ⟨r, Finset.mem_coe.2 ((hS.1 r).2 hr), hS.2 r hr⟩
  | s, e :: es, t, ⟨he, hL⟩, hS, st, hst, r, hr => by
    obtain ⟨-, h2⟩ := step_sim Pub c s e t he hS
    simp only [snaps, List.mem_cons] at hst
    simp only [projFrom]
    rcases hst with rfl | hst
    · exact cur_sub_held t _ ⟨r, Finset.mem_coe.2 ((hS.1 r).2 hr), hS.2 r hr⟩
    · exact held_append_right _ _ _ (snap_held Pub c _ es _ hL h2 st hst r hr)

/-- a MOVE record: register, frame left (tail), frame entered (head), row carried. -/
structure Mv (K Reg C : Type*) where
  reg : Reg
  tail : C
  head : C
  row : Reg → K

def mvOf (s : GSt K Reg C) : GEv K Reg C → List (Mv K Reg C)
  | .move r c' => match s.loc r with
    | some a => [⟨r, a, c', s.row r⟩]
    | none => []
  | _ => []

def moves : GSt K Reg C → List (GEv K Reg C) → List (Mv K Reg C)
  | _, [] => []
  | s, e :: es => mvOf s e ++ moves (gstep s e) es

/-- MOVE records come from visited states; public MOVEs strictly climb (l.51). -/
theorem moves_facts (Pub : Finset Reg) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
    LegalG Pub s w → ∀ m ∈ moves s w, (∃ st ∈ snaps s w, st.loc m.reg = some m.tail ∧
      st.row m.reg = m.row) ∧ (m.reg ∈ Pub → m.tail < m.head) ∧ m.tail ≠ m.head
  | s, [], _, m, hm => by simp [moves] at hm
  | s, e :: es, ⟨he, hL⟩, m, hm => by
    simp only [moves, List.mem_append] at hm
    rcases hm with hm | hm
    · cases e with
      | move r c' =>
        obtain ⟨a, ha, h1, h2⟩ := he
        simp only [mvOf, ha, List.mem_singleton] at hm
        subst hm
        refine ⟨⟨s, by simp [snaps], ha, rfl⟩, h1, ?_⟩
        by_cases hr : r ∈ Pub
        · exact (h1 hr).ne
        · rcases h2 hr with h | h
          · exact h.ne
          · exact h.ne'
      | init _ _ => simp [mvOf] at hm
      | clear _ => simp [mvOf] at hm
      | add _ _ _ => simp [mvOf] at hm
      | scale _ _ => simp [mvOf] at hm
      | copy _ _ _ => simp [mvOf] at hm
    · obtain ⟨⟨st, hst, h1, h2⟩, h3, h4⟩ := moves_facts Pub _ es hL m hm
      exact ⟨⟨st, by simp [snaps, hst], h1, h2⟩, h3, h4⟩

open ExportLaw in
/-- the row a MOVE carries enters its head chart. -/
theorem moves_arrive : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
    ∀ m ∈ moves s w, m.row ∈ entRows (projFrom m.head s w)
  | s, [], m, hm => by simp [moves] at hm
  | s, e :: es, m, hm => by
    simp only [moves, List.mem_append] at hm
    simp only [projFrom, entRows_append, List.mem_append]
    rcases hm with hm | hm
    · left
      cases e with
      | move r c' =>
        simp only [mvOf] at hm
        split at hm
        · rename_i a ha
          simp only [List.mem_singleton] at hm; subst hm
          by_cases h : s.loc r = some c'
          · simp [pev, h, entRows]
          · simp [pev, h, entRows]
        · simp at hm
      | init _ _ => simp [mvOf] at hm
      | clear _ => simp [mvOf] at hm
      | add _ _ _ => simp [mvOf] at hm
      | scale _ _ => simp [mvOf] at hm
      | copy _ _ _ => simp [mvOf] at hm
    · right; exact moves_arrive _ es m hm

open ExportLaw in
/-- every row entering chart `c` after time 0 is an owned INIT row (0) or a MOVE's row. -/
theorem entRows_proj (Pub : Finset Reg) (c : C) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
    LegalG Pub s w → ∀ v ∈ entRows (projFrom c s w),
      v = 0 ∨ ∃ m ∈ moves s w, m.head = c ∧ m.row = v
  | s, [], _, v, hv => by simp [projFrom, entRows] at hv
  | s, e :: es, ⟨he, hL⟩, v, hv => by
    simp only [projFrom, entRows_append, List.mem_append] at hv
    rcases hv with hv | hv
    · cases e with
      | init o c' =>
        left
        by_cases h : c' = c
        · simpa [pev, h, entRows] using hv
        · simp [pev, h, entRows] at hv
      | move r c' =>
        obtain ⟨a, ha, -, -⟩ := he
        right
        refine ⟨⟨r, a, c', s.row r⟩, by simp [moves, mvOf, ha], ?_⟩
        by_cases h : c' = c
        · subst h
          by_cases h' : s.loc r = some c'
          · simp [pev, h', entRows] at hv; exact ⟨rfl, hv.symm⟩
          · simp [pev, h', entRows] at hv; exact ⟨rfl, hv.symm⟩
        · by_cases h' : s.loc r = some c
          · simp [pev, h', h, entRows] at hv
          · simp [pev, h', h, entRows] at hv
      | clear o =>
        by_cases h : s.loc o = some c
        · simp [pev, h, entRows] at hv
        · simp [pev, h, entRows] at hv
      | add i j a =>
        by_cases h : s.loc i = some c
        · simp [pev, h, entRows] at hv
        · simp [pev, h, entRows] at hv
      | scale i u =>
        by_cases h : s.loc i = some c
        · simp [pev, h, entRows] at hv
        · simp [pev, h, entRows] at hv
      | copy i j a =>
        by_cases h : s.loc i = some c
        · simp [pev, h, entRows] at hv
        · simp [pev, h, entRows] at hv
    · rcases entRows_proj Pub c _ es hL v hv with h | ⟨m, hm, h1, h2⟩
      · exact Or.inl h
      · exact Or.inr ⟨m, by simp [moves, hm], h1, h2⟩

open ExportLaw in
lemma entRows_born (l : List Reg) : ∀ v ∈ entRows (l.map (Ev.born (K := K))),
    ∃ r ∈ l, v = Pi.single r 1 := by
  induction l with
  | nil => simp [entRows]
  | cons b l ih =>
    intro v hv
    simp only [List.map_cons, entRows, List.mem_cons] at hv
    rcases hv with rfl | hv
    · exact ⟨b, by simp, rfl⟩
    · obtain ⟨r, hr, rfl⟩ := ih v hv; exact ⟨r, by simp [hr], rfl⟩

open ExportLaw in
lemma nEnt_born (S : Finset Reg) : ∀ (l : List Reg), l.Nodup →
    nEnt S (l.map (Ev.born (K := K))) = (l.toFinset ∩ S).card
  | [], _ => by simp [nEnt]
  | b :: l, hnd => by
    obtain ⟨hb, hnd'⟩ := List.nodup_cons.1 hnd
    simp only [List.map_cons, nEnt, nEnt_born S l hnd', List.toFinset_cons]
    by_cases hbS : b ∈ S
    · rw [Finset.insert_inter_of_mem hbS, Finset.card_insert_of_notMem (by simp [hb])]
      simp [hbS]; omega
    · rw [Finset.insert_inter_of_notMem hbS]; simp [hbS]

open ExportLaw in
lemma nDep_born (S : Finset Reg) : ∀ (l : List Reg), nDep S (l.map (Ev.born (K := K))) = 0
  | [] => rfl
  | b :: l => by simp only [List.map_cons, nDep]; exact nDep_born S l

open ExportLaw in
lemma bornSet_born : ∀ (l : List Reg), bornSet (l.map (Ev.born (K := K))) = l.toFinset
  | [] => rfl
  | b :: l => by simp only [List.map_cons, bornSet, bornSet_born l, List.toFinset_cons]

open ExportLaw in
lemma bornSet_projFrom (c : C) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
    bornSet (projFrom c s w) = ∅
  | s, [] => rfl
  | s, e :: es => by
    rw [projFrom, bornSet_append, bornSet_projFrom c _ es, Finset.union_empty]
    cases e with
    | init o c' => by_cases h : c' = c <;> simp [pev, h, bornSet]
    | clear o => by_cases h : s.loc o = some c <;> simp [pev, h, bornSet]
    | move r c' =>
      by_cases h : s.loc r = some c <;> by_cases h' : c' = c <;> simp [pev, h, h', bornSet]
    | add i j a => by_cases h : s.loc i = some c <;> simp [pev, h, bornSet]
    | scale i u => by_cases h : s.loc i = some c <;> simp [pev, h, bornSet]
    | copy i j a => by_cases h : s.loc i = some c <;> simp [pev, h, bornSet]

open ExportLaw in
/-- **hOnce from l.51.** A public register enters a chart at most once after time 0, and never
again once it has stood at or above that chart. -/
theorem once_aux (Pub : Finset Reg) (c : C) (r : Reg) (hr : r ∈ Pub) :
    ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)) (a : C), LegalG Pub s w → s.loc r = some a →
      (c ≤ a → nEnt {r} (projFrom c s w) = 0) ∧ nEnt {r} (projFrom c s w) ≤ 1
  | s, [], a, _, _ => by simp [projFrom, nEnt]
  | s, e :: es, a, ⟨he, hL⟩, ha => by
    simp only [projFrom, nEnt_append]
    cases e with
    | move m c' =>
      obtain ⟨a', ha', h1, -⟩ := he
      by_cases hmr : m = r
      · subst hmr
        rw [ha] at ha'; cases ha'
        have hlt := h1 hr
        have hloc : (gstep s (.move m c')).loc m = some c' := by simp [gstep]
        obtain ⟨i1, i2⟩ := once_aux Pub c m hr _ es c' hL hloc
        by_cases hc : c' = c
        · subst hc
          have hne : s.loc m ≠ some c' := by rw [ha]; simpa using hlt.ne
          have h0 := i1 le_rfl
          refine ⟨fun hca => absurd (lt_of_le_of_lt hca hlt) (lt_irrefl _), ?_⟩
          simp [pev, hne, nEnt, h0]
        · have hpe : nEnt {m} (pev c s (.move m c')) = 0 := by
            by_cases h : s.loc m = some c <;> simp [pev, h, hc, nEnt]
          rw [hpe]
          exact ⟨fun hca => by simpa using i1 (hca.trans hlt.le), by simpa using i2⟩
      · have hloc : (gstep s (.move m c')).loc r = some a := by
          simp [gstep, Function.update_of_ne (Ne.symm hmr), ha]
        obtain ⟨i1, i2⟩ := once_aux Pub c r hr _ es a hL hloc
        have hpe : nEnt {r} (pev c s (.move m c')) = 0 := by
          by_cases h : s.loc m = some c <;> by_cases h' : c' = c <;>
            simp [pev, h, h', nEnt, hmr]
        rw [hpe]; exact ⟨fun hca => by simpa using i1 hca, by simpa using i2⟩
    | init o c' =>
      have hor : o ≠ r := fun h => he.1 (h ▸ hr)
      have hloc : (gstep s (.init o c')).loc r = some a := by
        simp [gstep, Function.update_of_ne (Ne.symm hor), ha]
      obtain ⟨i1, i2⟩ := once_aux Pub c r hr _ es a hL hloc
      have hpe : nEnt {r} (pev c s (.init o c')) = 0 := by
        by_cases h' : c' = c <;> simp [pev, h', nEnt, hor]
      rw [hpe]; exact ⟨fun hca => by simpa using i1 hca, by simpa using i2⟩
    | clear o =>
      have hor : o ≠ r := fun h => he.1 (h ▸ hr)
      have hloc : (gstep s (.clear o)).loc r = some a := by
        simp [gstep, Function.update_of_ne (Ne.symm hor), ha]
      obtain ⟨i1, i2⟩ := once_aux Pub c r hr _ es a hL hloc
      have hpe : nEnt {r} (pev c s (.clear o)) = 0 := by
        by_cases h : s.loc o = some c <;> simp [pev, h, nEnt]
      rw [hpe]; exact ⟨fun hca => by simpa using i1 hca, by simpa using i2⟩
    | add i j x =>
      obtain ⟨i1, i2⟩ := once_aux Pub c r hr _ es a hL (by simpa [gstep] using ha)
      have hpe : nEnt {r} (pev c s (.add i j x)) = 0 := by
        by_cases h : s.loc i = some c <;> simp [pev, h, nEnt]
      rw [hpe]; exact ⟨fun hca => by simpa using i1 hca, by simpa using i2⟩
    | scale i u =>
      obtain ⟨i1, i2⟩ := once_aux Pub c r hr _ es a hL (by simpa [gstep] using ha)
      have hpe : nEnt {r} (pev c s (.scale i u)) = 0 := by
        by_cases h : s.loc i = some c <;> simp [pev, h, nEnt]
      rw [hpe]; exact ⟨fun hca => by simpa using i1 hca, by simpa using i2⟩
    | copy i j x =>
      obtain ⟨i1, i2⟩ := once_aux Pub c r hr _ es a hL (by simpa [gstep] using ha)
      have hpe : nEnt {r} (pev c s (.copy i j x)) = 0 := by
        by_cases h : s.loc i = some c <;> simp [pev, h, nEnt]
      rw [hpe]; exact ⟨fun hca => by simpa using i1 hca, by simpa using i2⟩

open ExportLaw in
/-- **hOnce, derived**: every public register enters each chart at most once. -/
theorem hOnce_proj (Pub : Finset Reg) (c : C) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (hL : LegalG Pub (s0 ini) w) (r : Reg) (hr : r ∈ Pub) (hini : ini r ≠ none) :
    nEnt {r} (proj c ini w) ≤ 1 := by
  obtain ⟨a, ha⟩ := Option.ne_none_iff_exists'.1 hini
  obtain ⟨i1, i2⟩ := once_aux (K := K) Pub c r hr (s0 ini) w a hL ha
  rw [proj, nEnt_append, births, nEnt_born _ _ (Finset.nodup_toList _)]
  by_cases hrc : ini r = some c
  · rw [ha] at hrc; cases hrc
    have : ((bornAt c ini).toList.toFinset ∩ {r}).card = 1 := by
      rw [Finset.toList_toFinset, Finset.inter_singleton_of_mem (by simp [bornAt, ha])]; rfl
    rw [this, i1 le_rfl]
  · have : ((bornAt c ini).toList.toFinset ∩ {r}).card = 0 := by
      rw [Finset.toList_toFinset, Finset.inter_singleton_of_notMem (by simp [bornAt, hrc])]; rfl
    rw [this]; simpa using i2

/-! ## 4. ρ, acceptance, class K, chart quantities -/

/-- ρ deletes helper coordinates. -/
def rhoH (H : Finset Reg) : (Reg → K) →ₗ[K] (Reg → K) where
  toFun v i := if i ∈ H then 0 else v i
  map_add' v u := by ext i; simp only [Pi.add_apply]; split_ifs <;> simp
  map_smul' a v := by ext i; simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]; split_ifs <;> simp

lemma rhoH_single (H : Finset Reg) (h : Reg) (hh : h ∈ H) : rhoH (K := K) H (Pi.single h 1) = 0 := by
  ext i
  simp only [rhoH, LinearMap.coe_mk, AddHom.coe_mk, Pi.zero_apply]
  split_ifs with hi
  · rfl
  · have : i ≠ h := fun e => hi (e ▸ hh)
    simp [Pi.single_apply, this]

/-- acceptance by the shipped verifier (independent.py), the parts used here:
legality of every op (incl. l.51), public registers = those with an initial frame, helpers are
public, and the final Jacobian check (`bad_inputs == []`) on helper rows: a helper ends as its own
token (target[r] = {r: 1} for every non-main public r). -/
structure Accepted (Pub H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) : Prop where
  legal : LegalG Pub (s0 ini) w
  pub_ini : ∀ r, r ∈ Pub ↔ ini r ≠ none
  helpers_pub : H ⊆ Pub
  helper_final : ∀ h ∈ H, (grun (s0 ini) w).row h = Pi.single h 1

section Chart
variable (Pub H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))

open ExportLaw

/-- S_c: every row ever held at c. -/
def heldAt (c : C) : Set (Reg → K) := held start (proj c ini w)

/-- hd(c): paid helper stays at c (helper departures minus departures of helpers born at c). -/
noncomputable def hdW (c : C) : ℕ :=
  nDep H (proj c ini w) - ((H ∩ bornSet (proj c ini w)) \ (run start (proj c ini w)).pres).card
/-- ka(c): kept public registers that arrive at c. -/
noncomputable def kaW (c : C) : ℕ :=
  (((Pub \ H) \ bornSet (proj c ini w)).filter fun i => 0 < nEnt {i} (proj c ini w)).card
/-- oa(c): owned entries at c with a nonzero row (INITs, row 0, are free; sharpened count). -/
noncomputable def oaW (c : C) : ℕ :=
  nEnt (univ \ Pub) (proj c ini w) - (entRows (proj c ini w)).count 0
/-- kb(c): kept public registers born at c. -/
noncomputable def kbW (c : C) : ℕ := ((Pub \ H) ∩ bornSet (proj c ini w)).card

end Chart

open ExportLaw in
/-- **Chart floor on the word** (FloorGlue.chart_floor with every hypothesis discharged):
for an accepted word and any rows X held at c, rank ρ(X) ≤ hd + ka + oa + kb. -/
theorem chart_floor_word {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}
    (hA : Accepted Pub H ini w) (c : C) (X : Set (Reg → K)) (hX : X ⊆ heldAt ini w c) :
    finrank K (span K (rhoH H '' X)) ≤
      hdW H ini w c + kaW Pub H ini w c + oaW Pub ini w c + kbW Pub H ini w c := by
  classical
  obtain ⟨hL, hS⟩ := proj_legal Pub c ini w hA.legal
  have hHK : Disjoint H (Pub \ H) := Finset.disjoint_sdiff
  have hHO : Disjoint H (univ \ Pub) := Finset.disjoint_left.2 fun x hx hx' =>
    (Finset.mem_sdiff.1 hx').2 (hA.helpers_pub hx)
  have hKO : Disjoint (Pub \ H) (univ \ Pub) := Finset.disjoint_left.2 fun x hx hx' =>
    (Finset.mem_sdiff.1 hx').2 (Finset.mem_sdiff.1 hx).1
  have hcov : H ∪ (Pub \ H) ∪ (univ \ Pub) = univ := by
    ext x; by_cases hx : x ∈ Pub <;> by_cases hy : x ∈ H <;> simp [hx, hy]
  have hOnce : ∀ i ∈ Pub \ H, nEnt {i} (proj c ini w) ≤ 1 := fun i hi =>
    hOnce_proj Pub c ini w hA.legal i (Finset.mem_sdiff.1 hi).1
      ((hA.pub_ini i).1 (Finset.mem_sdiff.1 hi).1)
  have hN : ∀ h ∈ H, h ∈ (run start (proj c ini w)).pres →
      (run start (proj c ini w)).row h = Pi.single h 1 := fun h hh hp => by
    rw [hS.2 h ((hS.1 h).1 hp)]; exact hA.helper_final h hh
  have h := chart_floor' (rhoH H) (proj c ini w) hL H (Pub \ H) (univ \ Pub) hHK hHO hKO
    hcov hOnce hN (fun h hh => rhoH_single H h hh) X hX
  unfold hdW kaW oaW kbW
  exact h

/-! ## 5. Class K -/

/-- class-K data: the kept ρ-content of every chart (word-independent in class K). -/
structure KData (C W : Type*) where
  Kρ : C → Set W
  Rρ : C → Set W
  ka : C → ℕ
  oa : C → ℕ
  kb : C → ℕ

section ClassK
variable (Pub H : Finset Reg) (Kfin : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))

/-- kept arrival content at c: ρ-rows of kept and owned MOVEs into c, kept birth tokens. -/
def keptArr (c : C) : Set (Reg → K) :=
  {v | ∃ m ∈ moves (s0 ini) w, m.reg ∉ H ∧ m.head = c ∧ v = rhoH H m.row} ∪
  {v | ∃ r, r ∉ H ∧ ini r = some c ∧ v = rhoH H (Pi.single r 1)}

/-- token finals of the kept enders `Kfin` at c (the non-Y enders below V in the prose). -/
def keptFin (c : C) : Set (Reg → K) :=
  {v | ∃ r ∈ Kfin, (grun (s0 ini) w).loc r = some c ∧ v = rhoH H ((grun (s0 ini) w).row r)}

/-- ρ-rows of non-helper registers at c at any visited state (kept rows at kept events ⊆ this). -/
def keptSnap (c : C) : Set (Reg → K) :=
  {v | ∃ st ∈ snaps (s0 ini) w, ∃ r, r ∉ H ∧ st.loc r = some c ∧ v = rhoH H (st.row r)}

/-- **Class K relative to data D** (D = the kept data of #7623, read off by rsdata.py /
indep_word.py). An accepted word whose kept ρ-content at every chart is D's: every nonzero kept/owned
arrival ρ-row and kept birth token is in D.Kρ (K1), every element of D.Kρ is such a row or a kept
token final (K2), D's kept rows R(c) occur at c (R), and the kept counts are at most D's (ka, oa, kb;
`classK_of_counts` shows the literal MOVE/birth counts used by the data qualify). Helpers (routes,
frames, ops, rows) are free. -/
structure ClassK (D : KData C (Reg → K)) : Prop where
  acc : Accepted Pub H ini w
  kept_K1 : ∀ c, ∀ v ∈ keptArr H ini w c, v ≠ 0 → v ∈ D.Kρ c
  kept_K2 : ∀ c, D.Kρ c ⊆ keptArr H ini w c ∪ keptFin H Kfin ini w c
  kept_R : ∀ c, D.Rρ c ⊆ keptSnap H ini w c
  kept_ka : ∀ c, kaW Pub H ini w c ≤ D.ka c
  kept_oa : ∀ c, oaW Pub ini w c ≤ D.oa c
  kept_kb : ∀ c, kbW Pub H ini w c ≤ D.kb c

end ClassK

variable {Pub H Kfin : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}
  {D : KData C (Reg → K)}

open ExportLaw in
lemma born_ent (r : Reg) : ∀ l : List Reg, r ∈ l →
    (Pi.single r 1 : Reg → K) ∈ entRows (l.map (Ev.born (K := K)))
  | [], hm => by simp at hm
  | b :: l, hm => by
    simp only [List.map_cons, entRows, List.mem_cons] at hm ⊢
    rcases hm with rfl | hm
    · exact Or.inl rfl
    · exact Or.inr (born_ent r l hm)

open ExportLaw in
lemma births_ent (c : C) (r : Reg) (hr : ini r = some c) :
    (Pi.single r 1 : Reg → K) ∈ entRows (births (K := K) c ini) :=
  born_ent r _ (by simp [bornAt, hr])

open ExportLaw in
lemma move_held (_hA : Accepted Pub H ini w) (m : Mv K Reg C) (hm : m ∈ moves (s0 ini) w) :
    m.row ∈ heldAt ini w m.head := by
  apply entRows_held
  rw [proj, entRows_append]
  exact List.mem_append_right _ (moves_arrive _ w m hm)

open ExportLaw in
lemma snapRow_held (hA : Accepted Pub H ini w) (c : C) (st : GSt K Reg C)
    (hst : st ∈ snaps (s0 ini) w) (r : Reg) (hr : st.loc r = some c) :
    st.row r ∈ heldAt ini w c := by
  obtain ⟨-, hS⟩ := births_sim (K := K) c ini
  exact held_append_right _ _ _ (snap_held Pub c _ w _ hA.legal hS st hst r hr)

lemma tail_held (hA : Accepted Pub H ini w) (m : Mv K Reg C) (hm : m ∈ moves (s0 ini) w) :
    m.row ∈ heldAt ini w m.tail := by
  obtain ⟨⟨st, hst, h1, h2⟩, -, -⟩ := moves_facts Pub _ w hA.legal m hm
  rw [← h2]; exact snapRow_held hA _ st hst _ h1

open ExportLaw in
/-- K_c ⊆ ρ(S_c): every kept ρ-row is the ρ-image of a row held at c. -/
lemma K_held (hK : ClassK Pub H Kfin ini w D) (c : C) :
    ∀ v ∈ D.Kρ c, ∃ u ∈ heldAt ini w c, rhoH H u = v := by
  intro v hv
  replace hv := hK.kept_K2 c hv
  rcases hv with (⟨m, hm, -, rfl, rfl⟩ | ⟨r, -, hr, rfl⟩) | ⟨r, -, hr, rfl⟩
  · exact ⟨m.row, move_held hK.acc m hm, rfl⟩
  · refine ⟨_, entRows_held _ _ _ ?_, rfl⟩
    rw [proj, entRows_append]; exact List.mem_append_left _ (births_ent c r hr)
  · obtain ⟨hL, hS⟩ := proj_legal Pub c ini w hK.acc.legal
    refine ⟨_, final_sub_held _ _ ⟨r, Finset.mem_coe.2 ((hS.1 r).2 hr), hS.2 r hr⟩, rfl⟩

lemma R_held (hK : ClassK Pub H Kfin ini w D) (c : C) :
    ∀ v ∈ D.Rρ c, ∃ u ∈ heldAt ini w c, rhoH H u = v := by
  intro v hv
  obtain ⟨st, hst, r, -, hr, rfl⟩ := hK.kept_R c hv
  exact ⟨_, snapRow_held hK.acc c st hst r hr, rfl⟩

/-- preimage trick: a set of ρ-rows all realised by held rows is ρ of a set of held rows. -/
lemma image_pre (c : C) (Y : Set (Reg → K))
    (hY : ∀ v ∈ Y, ∃ u ∈ heldAt ini w c, rhoH H u = v) :
    rhoH H '' {u | u ∈ heldAt ini w c ∧ rhoH H u ∈ Y} = Y := by
  ext v; constructor
  · rintro ⟨u, ⟨-, hu⟩, rfl⟩; exact hu
  · intro hv; obtain ⟨u, hu, rfl⟩ := hY v hv; exact ⟨u, ⟨hu, hv⟩, rfl⟩

/-! ## 6. The three kept row families as theorems about the word -/

/-- **R1 (λ rows), on the word.** For every class-K word and every chart c:
hd(c) ≥ rank(ρK_c + ρR(c)) − ka − oa − kb, with K_c, R(c), ka, oa, kb the class-K data. -/
theorem R1_row (hK : ClassK Pub H Kfin ini w D) (c : C) :
    (finrank K (span K (D.Kρ c) ⊔ span K (D.Rρ c) : Submodule K (Reg → K)) : ℤ)
      - D.ka c - D.oa c - D.kb c ≤ hdW H ini w c := by
  have hY : ∀ v ∈ D.Kρ c ∪ D.Rρ c, ∃ u ∈ heldAt ini w c, rhoH H u = v := by
    rintro v (hv | hv)
    · exact K_held hK c v hv
    · exact R_held hK c v hv
  have h := chart_floor_word hK.acc c {u | u ∈ heldAt ini w c ∧ rhoH H u ∈ D.Kρ c ∪ D.Rρ c}
    (fun u hu => hu.1)
  rw [image_pre c _ hY, span_union] at h
  have := hK.kept_ka c; have := hK.kept_oa c; have := hK.kept_kb c
  omega

/-! Descent data on the word. -/

/-- helper MOVEs into c (the arrivals HelpArr_c; all of them, not a basis). -/
def HBw (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) (c : C) :
    Set (Mv K Reg C) :=
  {m | m ∈ moves (s0 ini) w ∧ m.reg ∈ H ∧ m.head = c}

/-- P(c) = ρ(S_c). -/
def Pw (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) (c : C) :
    Submodule K (Reg → K) :=
  (span K (heldAt ini w c)).map (rhoH H)

open ExportLaw in
/-- **hP, derived (R0(a))**: ρ(S_c) ⊆ span ρK_c + span ρ(helper arrival rows at c). -/
theorem hP_word (hK : ClassK Pub H Kfin ini w D) (c : C) :
    Pw H ini w c ≤ span K (D.Kρ c) ⊔ span K ((fun m => rhoH H m.row) '' HBw H ini w c) := by
  classical
  obtain ⟨hL, -⟩ := proj_legal Pub c ini w hK.acc.legal
  set N := (span K (D.Kρ c) ⊔ span K ((fun m => rhoH H m.row) '' HBw H ini w c)).comap (rhoH H)
  have hArr : ∀ v ∈ keptArr H ini w c, v ∈ span K (D.Kρ c) := fun v hv => by
    by_cases h0 : v = 0
    · rw [h0]; exact zero_mem _
    · exact subset_span (hK.kept_K1 c v hv h0)
  have hent : ∀ v ∈ entRows (proj c ini w), v ∈ N := by
    intro v hv
    rw [proj, entRows_append, List.mem_append] at hv
    simp only [N, Submodule.mem_comap]
    rcases hv with hv | hv
    · unfold births at hv
      obtain ⟨r, hr, rfl⟩ := entRows_born _ v hv
      have hr' : ini r = some c := by simpa [bornAt] using hr
      by_cases hrH : r ∈ H
      · rw [rhoH_single H r hrH]; exact zero_mem _
      · exact mem_sup_left (hArr _ (Or.inr ⟨r, hrH, hr', rfl⟩))
    · rcases entRows_proj Pub c _ w hK.acc.legal v hv with rfl | ⟨m, hm, hmc, rfl⟩
      · rw [map_zero]; exact zero_mem _
      · by_cases hmH : m.reg ∈ H
        · exact mem_sup_right (subset_span ⟨m, ⟨hm, hmH, hmc⟩, rfl⟩)
        · exact mem_sup_left (hArr _ (Or.inl ⟨m, hm, hmH, hmc, rfl⟩))
  have hheld : heldAt ini w c ⊆ N :=
    forward_span N start _ hL (by simp [cur, start]) hent
  rw [Pw, Submodule.map_le_iff_le_comap]
  exact span_le.2 hheld

/-- **hvec, derived**: a helper arrival row was held at its tail, which is strictly below the head
(l.51, helpers are public). -/
theorem hvec_word (hA : Accepted Pub H ini w) (c : C) :
    ∀ m ∈ HBw H ini w c, rhoH H m.row ∈ Pw H ini w m.tail ∧ m.tail < c := by
  rintro m ⟨hm, hmH, rfl⟩
  obtain ⟨-, hpub, -⟩ := moves_facts Pub _ w hA.legal m hm
  exact ⟨⟨m.row, subset_span (tail_held hA m hm), rfl⟩, hpub (hA.helpers_pub hmH)⟩

lemma kills_span {X : Set (Reg → K)} (ψ : (Reg → K) →ₗ[K] K) (h : ∀ x ∈ X, ψ x = 0) :
    ∀ x ∈ span K X, ψ x = 0 := fun x hx =>
  LinearMap.mem_ker.1 ((span_le.2 fun y hy => LinearMap.mem_ker.2 (h y hy) :
    span K X ≤ LinearMap.ker ψ) hx)

/-- **F4 / R2 (u rows), on the word.** A certified single-source commodity (t, s, ψ): ψ kills
ρK_t and every ρK_{s'} with s' < t, s' ≠ s, and sees some kept row n ∈ ρR(t). Then every class-K
word has a helper MOVE out of s itself into some c with s < c ≤ t whose ρ-row ψ sees (its first hop). -/
theorem F4_row [WellFoundedLT C] (hK : ClassK Pub H Kfin ini w D) (ψ : (Reg → K) →ₗ[K] K)
    (s t : C) (hKt : ∀ x ∈ D.Kρ t, ψ x = 0)
    (hW : ∀ s', s' < t → s' ≠ s → ∀ x ∈ D.Kρ s', ψ x = 0)
    (n : Reg → K) (hn : n ∈ D.Rρ t) (hψn : ψ n ≠ 0) :
    ∃ m ∈ moves (s0 ini) w, m.reg ∈ H ∧ m.tail = s ∧ s < m.head ∧ m.head ≤ t ∧
      ψ (rhoH H m.row) ≠ 0 := by
  obtain ⟨u, hu, rfl⟩ := R_held hK t n hn
  obtain ⟨c₁, m, ⟨hm, hmH, rfl⟩, htail, hψ, hlt, hle⟩ :=
    Floor.F4_single_source (KA := fun c => span K (D.Kρ c)) (P := Pw H ini w)
      (HB := HBw H ini w) (tail := Mv.tail) (vec := fun m => rhoH H m.row)
      (hP_word hK) (hvec_word hK.acc) ψ s t (kills_span ψ hKt)
      (fun s' h1 h2 => kills_span ψ (hW s' h1 h2)) _ ⟨u, subset_span hu, rfl⟩ hψn
  exact ⟨m, hm, hmH, htail, hlt, hle, hψ⟩

/-- **R3 (α and β rows), on the word.** Helper MOVEs mv_j into c from pairwise distinct tails, each
serving a certified commodity (t_j, tail_j, ψ_j) with c ≤ t_j: ψ_j kills ρK_{c'} for all c' ≤ t_j,
c' ≠ tail_j, and sees the hop's ρ-row. Let RA ⊆ ρR(c) be killed by every ψ_j. Then
hd(c) ≥ rank(ρK_c + RA) − ka − oa − kb + #hops.
RA = ∅: α row (hd ≥ #hops − slr). RA = ρR(c) (every hop type A at c): β row (hd ≥ needR + #A-hops). -/
theorem R3_row [WellFoundedLT C] (hK : ClassK Pub H Kfin ini w D) (c : C) {ι : Type*} [Fintype ι]
    (mv : ι → Mv K Reg C) (hmv : ∀ j, mv j ∈ HBw H ini w c)
    (hinj : Function.Injective fun j => (mv j).tail) (t : ι → C) (ψ : ι → (Reg → K) →ₗ[K] K)
    (hψK : ∀ i c', c' ≤ t i → c' ≠ (mv i).tail → ∀ x ∈ D.Kρ c', ψ i x = 0)
    (hct : ∀ j, c ≤ t j) (hdiag : ∀ j, ψ j (rhoH H (mv j).row) ≠ 0)
    (RA : Set (Reg → K)) (hRA : RA ⊆ D.Rρ c) (hψR : ∀ i, ∀ x ∈ RA, ψ i x = 0) :
    (finrank K (span K (D.Kρ c) ⊔ span K RA : Submodule K (Reg → K)) : ℤ)
      - D.ka c - D.oa c - D.kb c + Fintype.card ι ≤ hdW H ini w c := by
  classical
  have hv := hvec_word hK.acc c
  have hind : Floor.IndepMod (span K (D.Kρ c) ⊔ span K RA) (fun j => rhoH H (mv j).row) :=
    Floor.R3_indep (fun c => span K (D.Kρ c)) (span K RA) c (fun j => (mv j).tail) t hinj
      (fun j => rhoH H (mv j).row) ψ (fun i c' h1 h2 => kills_span (ψ i) (hψK i c' h1 h2))
      (fun i => kills_span (ψ i) (hψR i)) (fun j => (hv _ (hmv j)).2) hct hdiag
      (fun j => Floor.R0b (KA := fun c => span K (D.Kρ c)) (P := Pw H ini w)
        (HB := HBw H ini w) (tail := Mv.tail) (vec := fun m => rhoH H m.row)
        (hP_word hK) (hvec_word hK.acc) _ (hv _ (hmv j)).1)
  have hY : ∀ v ∈ D.Kρ c ∪ RA, ∃ u ∈ heldAt ini w c, rhoH H u = v := by
    rintro v (hv | hv)
    · exact K_held hK c v hv
    · exact R_held hK c v (hRA hv)
  have hrow : ∀ j, (mv j).row ∈ heldAt ini w c := fun j => by
    obtain ⟨hm, -, hc⟩ := hmv j
    rw [← hc]; exact move_held hK.acc _ hm
  have hX : {u | u ∈ heldAt ini w c ∧ rhoH H u ∈ D.Kρ c ∪ RA} ∪ Set.range (fun j => (mv j).row)
      ⊆ heldAt ini w c := Set.union_subset (fun u hu => hu.1) (by rintro _ ⟨j, rfl⟩; exact hrow j)
  have h := chart_floor_word hK.acc c _ hX
  rw [Set.image_union, image_pre c _ hY, span_union, span_union, ← Set.range_comp] at h
  have := Floor.finrank_sup_of_indepMod _ _ hind
  simp only [Function.comp_def] at h
  have := hK.kept_ka c; have := hK.kept_oa c; have := hK.kept_kb c
  omega

/-! ## 7. hd(c) is the fibre of the global stay list -/

open ExportLaw in
lemma bornSet_proj (c : C) : bornSet (proj (K := K) c ini w) = bornAt c ini := by
  rw [proj, bornSet_append, births, bornSet_born, bornSet_projFrom, Finset.union_empty,
    Finset.toList_toFinset]

section Stays
variable [Fintype C]

/-- the paid helper stays of the word: (helper h, chart c) with h arriving at c (not born there)
and later leaving. Each helper visits each chart at most once (hOnce from l.51), so these are
distinct stays. -/
noncomputable def stays (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) :
    Finset (Reg × C) :=
  by classical exact univ.filter fun p => p.1 ∈ H ∧ ini p.1 ≠ some p.2 ∧
    0 < ExportLaw.nDep {p.1} (proj p.2 ini w)

open ExportLaw in
/-- **hd/fibre identity, derived**: FloorGlue's per-chart hd(c) (helper departures − hb) is the
number of global stays at c. -/
theorem hd_fibre (hA : Accepted Pub H ini w) (c : C) :
    ((stays H ini w).filter fun p => p.2 = c).card = hdW H ini w c := by
  classical
  obtain ⟨hL, -⟩ := proj_legal Pub c ini w hA.legal
  have hB := bornSet_proj (K := K) (ini := ini) (w := w) c
  have hone : ∀ h ∈ H, nEnt {h} (proj c ini w) ≤ 1 := fun h hh =>
    hOnce_proj Pub c ini w hA.legal h (hA.helpers_pub hh) ((hA.pub_ini h).1 (hA.helpers_pub hh))
  have hst : ∀ h, nEnt {h} (proj c ini w) = nDep {h} (proj c ini w) +
      ((run start (proj c ini w)).pres ∩ {h}).card := fun h => FloorGlue.stay_one _ hL h
  have hsum : nDep H (proj c ini w) =
      (H.filter fun h => 0 < nDep {h} (proj c ini w)).card := by
    rw [nDep_eq_sum, Finset.card_filter]
    refine Finset.sum_congr rfl fun h hh => ?_
    have := hone h hh; have := hst h
    split_ifs with hp <;> omega
  have hsplit := Finset.card_filter_add_card_filter_not
    (s := H.filter fun h => 0 < nDep {h} (proj c ini w)) (fun h => h ∈ bornAt c ini)
  have hb : ((H.filter fun h => 0 < nDep {h} (proj c ini w)).filter fun h => h ∈ bornAt c ini) =
      (H ∩ bornSet (proj c ini w)) \ (run start (proj c ini w)).pres := by
    ext h
    simp only [Finset.mem_filter, Finset.mem_sdiff, Finset.mem_inter, hB]
    constructor
    · rintro ⟨⟨hh, hp⟩, hb⟩
      refine ⟨⟨hh, hb⟩, fun hF => ?_⟩
      have h1 := hone h hh; have h2 := hst h
      have : ((run start (proj c ini w)).pres ∩ {h}).card = 1 := by
        rw [Finset.inter_singleton_of_mem hF]; rfl
      omega
    · rintro ⟨⟨hh, hb⟩, hF⟩
      have h0 := FloorGlue.one_le_nEnt_of_born (K := K) (proj c ini w) h (hB ▸ hb)
      have h2 := hst h
      have : ((run start (proj c ini w)).pres ∩ {h}).card = 0 := by
        rw [Finset.inter_singleton_of_notMem hF]; rfl
      exact ⟨⟨hh, by omega⟩, hb⟩
  have hf : ((stays H ini w).filter fun p => p.2 = c).card =
      ((H.filter fun h => 0 < nDep {h} (proj c ini w)).filter
        fun h => ¬ h ∈ bornAt c ini).card := by
    apply Finset.card_nbij' (fun p => p.1) (fun h => (h, c))
    · rintro ⟨h, c'⟩ hp
      simp only [stays, Finset.coe_filter, Finset.mem_filter, Finset.mem_univ, true_and,
        Set.mem_ofPred_eq] at hp
      obtain ⟨⟨hh, hini, hpos⟩, rfl⟩ := hp
      simp only [Finset.coe_filter, Finset.mem_filter, bornAt, Finset.mem_univ, true_and,
        Set.mem_ofPred_eq]
      exact ⟨⟨hh, hpos⟩, hini⟩
    · intro h hp
      simp only [Finset.coe_filter, Finset.mem_filter, bornAt, Finset.mem_univ, true_and,
        Set.mem_ofPred_eq] at hp
      obtain ⟨⟨hh, hpos⟩, hini⟩ := hp
      simp only [stays, Finset.coe_filter, Finset.mem_filter, Finset.mem_univ, true_and,
        Set.mem_ofPred_eq]
      exact ⟨⟨hh, hini, hpos⟩, by simp⟩
    · rintro ⟨h, c'⟩ hp
      simp only [stays, Finset.coe_filter, Finset.mem_filter, Set.mem_ofPred_eq] at hp
      simp [hp.2]
    · intro h _; rfl
  unfold hdW
  rw [hf]
  rw [hb] at hsplit
  omega

/-- Σ_c hd(c) = #stays. -/
theorem sum_hd (hA : Accepted Pub H ini w) :
    ∑ c, hdW H ini w c = (stays H ini w).card := by
  classical
  rw [Finset.card_eq_sum_card_fiberwise (f := Prod.snd) (t := univ) (fun _ _ => Finset.mem_univ _)]
  exact Finset.sum_congr rfl fun c _ => (hd_fibre hA c).symm

end Stays

/-! ## 7b. The literal kept counts (as the data defines them) qualify for class K -/

section Counts
open ExportLaw

/-- INITs of registers in S at chart c. -/
def nInitG (S : Finset Reg) (c : C) : List (GEv K Reg C) → ℕ
  | [] => 0
  | .init o c' :: es => (if o ∈ S ∧ c' = c then 1 else 0) + nInitG S c es
  | _ :: es => nInitG S c es

theorem nEnt_projFrom_le (Pub S : Finset Reg) (c : C) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
    LegalG Pub s w → nEnt S (projFrom c s w) ≤
      nInitG S c w + (moves s w).countP (fun m => decide (m.reg ∈ S ∧ m.head = c))
  | s, [], _ => by simp [projFrom, nEnt]
  | s, e :: es, ⟨he, hL⟩ => by
    have ih := nEnt_projFrom_le Pub S c _ es hL
    simp only [projFrom, nEnt_append, moves, List.countP_append]
    cases e with
    | init o c' =>
      have h1 : nEnt S (pev c s (.init o c')) = if o ∈ S ∧ c' = c then 1 else 0 := by
        by_cases h : c' = c <;> by_cases ho : o ∈ S <;> simp [pev, nEnt, h, ho]
      simp only [nInitG, mvOf, List.countP_nil]; rw [h1]; split_ifs <;> omega
    | move r c' =>
      obtain ⟨a, ha, -, -⟩ := he
      have h1 : nEnt S (pev c s (.move r c')) = if r ∈ S ∧ c' = c then 1 else 0 := by
        by_cases h : s.loc r = some c <;> by_cases h' : c' = c <;> by_cases hr : r ∈ S <;>
          simp [pev, nEnt, h, h', hr]
      have h2 : (mvOf s (.move r c')).countP (fun m => decide (m.reg ∈ S ∧ m.head = c)) =
          if r ∈ S ∧ c' = c then 1 else 0 := by
        simp only [mvOf, ha]; by_cases h' : c' = c <;> by_cases hr : r ∈ S <;> simp [h', hr]
      simp only [nInitG]; rw [h1, h2]; split_ifs <;> omega
    | clear o =>
      have h1 : nEnt S (pev c s (.clear o)) = 0 := by
        by_cases h : s.loc o = some c <;> simp [pev, nEnt, h]
      simp only [nInitG, mvOf, List.countP_nil]; rw [h1]; omega
    | add i j x =>
      have h1 : nEnt S (pev c s (.add i j x)) = 0 := by
        by_cases h : s.loc i = some c <;> simp [pev, nEnt, h]
      simp only [nInitG, mvOf, List.countP_nil]; rw [h1]; omega
    | scale i u =>
      have h1 : nEnt S (pev c s (.scale i u)) = 0 := by
        by_cases h : s.loc i = some c <;> simp [pev, nEnt, h]
      simp only [nInitG, mvOf, List.countP_nil]; rw [h1]; omega
    | copy i j x =>
      have h1 : nEnt S (pev c s (.copy i j x)) = 0 := by
        by_cases h : s.loc i = some c <;> simp [pev, nEnt, h]
      simp only [nInitG, mvOf, List.countP_nil]; rw [h1]; omega

theorem nInitG_le_count (S : Finset Reg) (c : C) : ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)),
    nInitG S c w ≤ (entRows (projFrom c s w)).count 0
  | s, [] => by simp [nInitG]
  | s, e :: es => by
    have ih := nInitG_le_count S c (gstep s e) es
    simp only [projFrom, entRows_append, List.count_append]
    cases e with
    | init o c' =>
      simp only [nInitG]
      by_cases h : c' = c
      · have : (entRows (pev c s (.init o c'))).count 0 = 1 := by simp [pev, h, entRows]
        rw [this]; split_ifs <;> omega
      · simp only [h, and_false, if_false]; omega
    | move _ _ => simp only [nInitG]; omega
    | clear _ => simp only [nInitG]; omega
    | add _ _ _ => simp only [nInitG]; omega
    | scale _ _ => simp only [nInitG]; omega
    | copy _ _ _ => simp only [nInitG]; omega

theorem nInitG_pub (Pub S : Finset Reg) (hS : S ⊆ Pub) (c : C) :
    ∀ (s : GSt K Reg C) (w : List (GEv K Reg C)), LegalG Pub s w → nInitG S c w = 0
  | s, [], _ => rfl
  | s, e :: es, ⟨he, hL⟩ => by
    have ih := nInitG_pub Pub S hS c _ es hL
    cases e with
    | init o c' =>
      have : o ∉ S := fun h => he.1 (hS h)
      simp [nInitG, this, ih]
    | move _ _ => simpa [nInitG] using ih
    | clear _ => simpa [nInitG] using ih
    | add _ _ _ => simpa [nInitG] using ih
    | scale _ _ => simpa [nInitG] using ih
    | copy _ _ _ => simpa [nInitG] using ih

/-- the data's ka: kept public MOVE arrivals into c (indep_word.py `nka`). -/
def kaM (Pub H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) (c : C) : ℕ :=
  (moves (s0 ini) w).countP fun m => decide (m.reg ∈ Pub \ H ∧ m.head = c)
/-- the data's oa: owned MOVE arrivals into c (indep_word.py `noa`; INITs not counted). -/
def oaM (Pub : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) (c : C) : ℕ :=
  (moves (s0 ini) w).countP fun m => decide (m.reg ∈ univ \ Pub ∧ m.head = c)
/-- the data's kb: kept public registers born at c (indep_word.py `nkb`). -/
def kbM (Pub H : Finset Reg) (ini : Reg → Option C) (c : C) : ℕ :=
  ((Pub \ H).filter fun r => ini r = some c).card

lemma nEnt_births_zero (S : Finset Reg) (c : C) (hS : ∀ r ∈ S, ini r ≠ some c) :
    nEnt S (births (K := K) c ini) = 0 := by
  rw [births, nEnt_born _ _ (Finset.nodup_toList _), Finset.toList_toFinset, Finset.card_eq_zero,
    Finset.eq_empty_iff_forall_notMem]
  intro r hr
  obtain ⟨h1, h2⟩ := Finset.mem_inter.1 hr
  exact hS r h2 (by simpa [bornAt] using h1)

theorem kaW_le (hA : Accepted Pub H ini w) (c : C) : kaW Pub H ini w c ≤ kaM Pub H ini w c := by
  classical
  unfold kaW
  rw [bornSet_proj]
  have key : ∀ i ∉ bornAt c ini, nEnt {i} (proj (K := K) c ini w) =
      nEnt {i} (projFrom c (s0 ini) w) := by
    intro i hi
    rw [proj, nEnt_append, nEnt_births_zero {i} c (by
      intro r hr; rw [Finset.mem_singleton] at hr; subst hr; simpa [bornAt] using hi), zero_add]
  have h1 : (((Pub \ H) \ bornAt c ini).filter fun i => 0 < nEnt {i} (proj c ini w)).card ≤
      ∑ i ∈ (Pub \ H) \ bornAt c ini, nEnt {i} (projFrom c (s0 ini) w) := by
    rw [Finset.card_filter]
    refine Finset.sum_le_sum fun i hi => ?_
    rw [key i (Finset.mem_sdiff.1 hi).2]
    split_ifs <;> omega
  have h2 : ∑ i ∈ (Pub \ H) \ bornAt c ini, nEnt {i} (projFrom c (s0 ini) w) ≤
      ∑ i ∈ Pub \ H, nEnt {i} (projFrom c (s0 ini) w) :=
    Finset.sum_le_sum_of_subset Finset.sdiff_subset
  have h3 := nEnt_projFrom_le Pub (Pub \ H) c (s0 ini) w hA.legal
  rw [nInitG_pub Pub (Pub \ H) Finset.sdiff_subset c _ w hA.legal, zero_add] at h3
  have h4 := FloorGlue.nEnt_eq_sum (Pub \ H) (projFrom c (s0 ini) w)
  unfold kaM
  omega

theorem oaW_le (hA : Accepted Pub H ini w) (c : C) : oaW Pub ini w c ≤ oaM Pub ini w c := by
  classical
  unfold oaW oaM
  rw [proj, nEnt_append, nEnt_births_zero (univ \ Pub) c (by
    intro r hr hc
    exact (Finset.mem_sdiff.1 hr).2 ((hA.pub_ini r).2 (by rw [hc]; simp))), zero_add,
    entRows_append, List.count_append]
  have h1 := nEnt_projFrom_le Pub (univ \ Pub) c (s0 ini) w hA.legal
  have h2 := nInitG_le_count (univ \ Pub) c (s0 ini) w
  omega

theorem kbW_eq (c : C) : kbW Pub H ini w c = kbM Pub H ini c := by
  unfold kbW kbM
  rw [bornSet_proj]
  congr 1; ext r; simp [bornAt]

/-- **The literal class K qualifies**: an accepted word whose kept ρ-content and kept rows are D's
(K1, K2, R) and whose kept public MOVE arrivals, owned MOVE arrivals and kept births per chart are
D's counts (the definitions used by rsdata.py / indep_word.py) is in ClassK D. -/
theorem classK_of_counts {Kfin : Finset Reg} {D : KData C (Reg → K)} (hA : Accepted Pub H ini w)
    (hK1 : ∀ c, ∀ v ∈ keptArr H ini w c, v ≠ 0 → v ∈ D.Kρ c)
    (hK2 : ∀ c, D.Kρ c ⊆ keptArr H ini w c ∪ keptFin H Kfin ini w c)
    (hR : ∀ c, D.Rρ c ⊆ keptSnap H ini w c)
    (hka : ∀ c, D.ka c = kaM Pub H ini w c) (hoa : ∀ c, D.oa c = oaM Pub ini w c)
    (hkb : ∀ c, D.kb c = kbM Pub H ini c) : ClassK Pub H Kfin ini w D :=
  ⟨hA, hK1, hK2, hR, fun c => (hka c).symm ▸ kaW_le hA c, fun c => (hoa c).symm ▸ oaW_le hA c,
    fun c => (hkb c).symm ▸ (kbW_eq c).le⟩

end Counts

/-! ## 8. The LP point x(word): rows α, β, γ, λ, u and the objective

LP data as parameters: commodities `Q` (target `tQ`, source `sQ`, functional `ψQ`), the Nat charts,
the type-A relation, and fresh minimal heads `head s c` (an index type `M` of head columns).
Variables: y_c (c ∈ Nat), z_{s,c}, a_{s,c}, x_m. -/
section LP
variable {Q M : Type*} [Fintype C] [Fintype Q] [Fintype M]
  (D : KData C (Reg → K)) (tQ sQ : Q → C) (ψQ : Q → (Reg → K) →ₗ[K] K)

/-- a certified single-source commodity (RANKSTEINER R2 / FANOUT F4; rsess.py's exact check). -/
def Certified (k : Q) : Prop :=
  (∀ x ∈ D.Kρ (tQ k), ψQ k x = 0) ∧
  (∀ s', s' < tQ k → s' ≠ sQ k → ∀ x ∈ D.Kρ s', ψQ k x = 0) ∧
  ∃ n ∈ D.Rρ (tQ k), ψQ k n ≠ 0

/-- hop m (a helper MOVE into c) serves commodity k at c. -/
def Serves (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) (k : Q) (c : C)
    (m : Mv K Reg C) : Prop :=
  m ∈ HBw H ini w c ∧ m.tail = sQ k ∧ c ≤ tQ k ∧ ψQ k (rhoH H m.row) ≠ 0

/-- sources s with a hop s → c serving some commodity of source s that satisfies `Pk`. -/
noncomputable def srcs (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (Pk : Q → Prop) (c : C) : Finset C :=
  by classical exact univ.filter fun s => ∃ k m, sQ k = s ∧ Pk k ∧ Serves tQ sQ ψQ H ini w k c m

variable (NC : Finset C) (TypeA : Q → C → Prop) (head : C → C → M)

/-- the word's LP point (as in rsnative.py / NativeFeas): y = hd on NC, z/a = first-hop
indicators, x = indicator of a fresh head used by a hop into a non-NC chart. -/
noncomputable def zv (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (s c : C) : ℕ :=
  by classical exact if s ∈ srcs tQ sQ ψQ H ini w (fun _ => True) c then 1 else 0
noncomputable def av (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (s c : C) : ℕ :=
  by classical exact if s ∈ srcs tQ sQ ψQ H ini w (fun k => TypeA k c) c then 1 else 0
/-- head m is used by some hop s → c into a non-Nat chart. -/
def headUsed (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C)) (m : M) : Prop :=
  ∃ s c, c ∉ NC ∧ head s c = m ∧ s ∈ srcs tQ sQ ψQ H ini w (fun _ => True) c

noncomputable def xv (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (m : M) : ℕ :=
  by classical exact if headUsed tQ sQ ψQ NC head H ini w m then 1 else 0

open scoped Classical in
/-- the u-row term of chart c for commodity k: a_{s,c} if k is type A at c, else z_{s,c}. -/
noncomputable def uterm (H : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (k : Q) (c : C) : ℕ :=
  if TypeA k c then av tQ sQ ψQ TypeA H ini w (sQ k) c else zv tQ sQ ψQ H ini w (sQ k) c

variable {D tQ sQ ψQ}

/-- the counting core of α, β and the objective: R3_row on one chosen hop per source. -/
theorem card_srcs [WellFoundedLT C] (hK : ClassK Pub H Kfin ini w D)
    (hcert : ∀ k, Certified D tQ sQ ψQ k) (c : C) (Pk : Q → Prop)
    (RA : Set (Reg → K)) (hRA : RA ⊆ D.Rρ c) (hPA : ∀ k, Pk k → ∀ x ∈ RA, ψQ k x = 0) :
    (finrank K (span K (D.Kρ c) ⊔ span K RA : Submodule K (Reg → K)) : ℤ)
      - D.ka c - D.oa c - D.kb c + (srcs tQ sQ ψQ H ini w Pk c).card ≤ hdW H ini w c := by
  classical
  set S := srcs tQ sQ ψQ H ini w Pk c
  have hS : ∀ s : S, ∃ k m, sQ k = s.1 ∧ Pk k ∧ Serves tQ sQ ψQ H ini w k c m := fun s => by
    have := s.2; simp only [S, srcs, Finset.mem_filter, Finset.mem_univ, true_and] at this
    exact this
  choose kk mm hkk using hS
  have h := R3_row hK c (ι := S) (fun j => mm j) (fun j => (hkk j).2.2.1)
    (by
      intro i j hij
      have hi := (hkk i).2.2.2.1; have hj := (hkk j).2.2.2.1
      have := (hkk i).1; have := (hkk j).1
      apply Subtype.ext
      simp only at hij
      rw [← (hkk i).1, ← (hkk j).1, ← hi, ← hj, hij])
    (fun j => tQ (kk j)) (fun j => ψQ (kk j))
    (by
      intro i c' h1 h2 x hx
      have htail : (mm i).tail = sQ (kk i) := (hkk i).2.2.2.1
      rw [htail] at h2
      rcases h1.lt_or_eq with h1 | h1
      · exact (hcert (kk i)).2.1 c' h1 h2 x hx
      · subst h1; exact (hcert (kk i)).1 x hx)
    (fun j => (hkk j).2.2.2.2.1) (fun j => (hkk j).2.2.2.2.2) RA hRA
    (fun i => hPA (kk i) (hkk i).2.1)
  simpa [Fintype.card_coe] using h

lemma sum_ind {α : Type*} [Fintype α] (S : Finset α) [DecidablePred (· ∈ S)] :
    (∑ a, if a ∈ S then (1 : ℕ) else 0) = S.card := by
  classical
  rw [Finset.sum_boole]; simp

/-- **λ row** (y_c ≥ L_c = max(0, needR_c); needK ≤ max(0, needR) on #7623's data). -/
theorem lam_row (hK : ClassK Pub H Kfin ini w D) (c : C) :
    max 0 ((finrank K (span K (D.Kρ c) ⊔ span K (D.Rρ c) : Submodule K (Reg → K)) : ℤ)
      - D.ka c - D.oa c - D.kb c) ≤ hdW H ini w c :=
  max_le (by positivity) (R1_row hK c)

/-- **α row**: y_c ≥ Σ_s z_{s,c} − slr_c, slr_c = ka + oa + kb − rank ρK_c. -/
theorem alpha_row [WellFoundedLT C] (hK : ClassK Pub H Kfin ini w D)
    (hcert : ∀ k, Certified D tQ sQ ψQ k) (c : C) :
    ((∑ s, zv tQ sQ ψQ H ini w s c : ℕ) : ℤ)
      - ((D.ka c + D.oa c + D.kb c : ℕ) - (finrank K (span K (D.Kρ c)) : ℤ)) ≤ hdW H ini w c := by
  classical
  have h := card_srcs hK hcert c (fun _ => True) ∅ (Set.empty_subset _) (by simp)
  rw [span_empty, sup_bot_eq] at h
  have hz : (∑ s, zv tQ sQ ψQ H ini w s c) = (srcs tQ sQ ψQ H ini w (fun _ => True) c).card := by
    rw [← sum_ind]; rfl
  rw [hz]; push_cast; omega

/-- **β row**: y_c ≥ needR_c + Σ_s a_{s,c} (type A: the commodity's ψ kills ρR(c)). -/
theorem beta_row [WellFoundedLT C] (hK : ClassK Pub H Kfin ini w D)
    (hcert : ∀ k, Certified D tQ sQ ψQ k)
    (hA : ∀ k c, TypeA k c → ∀ x ∈ D.Rρ c, ψQ k x = 0) (c : C) :
    (finrank K (span K (D.Kρ c) ⊔ span K (D.Rρ c) : Submodule K (Reg → K)) : ℤ)
      - D.ka c - D.oa c - D.kb c + ((∑ s, av tQ sQ ψQ TypeA H ini w s c : ℕ) : ℤ)
      ≤ hdW H ini w c := by
  classical
  have h := card_srcs hK hcert c (fun k => TypeA k c) (D.Rρ c) le_rfl (fun k hk => hA k c hk)
  have ha : (∑ s, av tQ sQ ψQ TypeA H ini w s c) =
      (srcs tQ sQ ψQ H ini w (fun k => TypeA k c) c).card := by
    rw [← sum_ind]; rfl
  rw [ha]; exact h

/-- **γ row**: z ≥ a. -/
theorem gamma_row (s c : C) : av tQ sQ ψQ TypeA H ini w s c ≤ zv tQ sQ ψQ H ini w s c := by
  classical
  unfold av zv
  split_ifs with h1 h2 <;> try omega
  exfalso; apply h2
  simp only [srcs, Finset.mem_filter, Finset.mem_univ, true_and] at h1 ⊢
  obtain ⟨k, m, h1, -, h3⟩ := h1
  exact ⟨k, m, h1, h3⟩

open scoped Classical in
/-- **u row** (F4 covering): for a certified commodity k, the first hop out of sQ k covers it:
Σ_{c ∈ NC, s < c ≤ t} (a_{s,c} if k is type A at c, else z_{s,c}) + Σ_{m ∈ heads k} x_m ≥ 1,
for any head column set containing head(s, c) for every non-NC c with s < c ≤ t. -/
theorem u_row [WellFoundedLT C] (hK : ClassK Pub H Kfin ini w D) (k : Q)
    (hk : Certified D tQ sQ ψQ k) (heads : Finset M)
    (hheads : ∀ c, c ∉ NC → sQ k < c → c ≤ tQ k → head (sQ k) c ∈ heads) :
    1 ≤ (∑ c ∈ NC.filter (fun c => sQ k < c ∧ c ≤ tQ k), uterm tQ sQ ψQ TypeA H ini w k c)
        + ∑ m ∈ heads, xv tQ sQ ψQ NC head H ini w m := by
  classical
  obtain ⟨hKt, hW, n, hn, hψn⟩ := hk
  obtain ⟨m, hm, hmH, htail, hlt, hle, hψ⟩ := F4_row hK (ψQ k) (sQ k) (tQ k) hKt hW n hn hψn
  have hserv : Serves tQ sQ ψQ H ini w k m.head m := ⟨⟨hm, hmH, rfl⟩, htail, hle, hψ⟩
  have hz : sQ k ∈ srcs tQ sQ ψQ H ini w (fun _ => True) m.head := by
    simp only [srcs, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨k, m, rfl, hserv⟩
  by_cases hN : m.head ∈ NC
  · have hmem : m.head ∈ NC.filter (fun c => sQ k < c ∧ c ≤ tQ k) :=
      Finset.mem_filter.2 ⟨hN, hlt, hle⟩
    have hterm : 1 ≤ uterm tQ sQ ψQ TypeA H ini w k m.head := by
      unfold uterm
      split_ifs with hA
      · unfold av
        rw [if_pos]
        simp only [srcs, Finset.mem_filter, Finset.mem_univ, true_and]
        exact ⟨k, m, rfl, hA, hserv⟩
      · unfold zv; rw [if_pos (by convert hz)]
    have := Finset.single_le_sum (f := fun c => uterm tQ sQ ψQ TypeA H ini w k c)
      (fun _ _ => Nat.zero_le _) hmem
    exact le_add_right (hterm.trans this)
  · have hmem := hheads m.head hN hlt hle
    have hx : 1 ≤ xv tQ sQ ψQ NC head H ini w (head (sQ k) m.head) := by
      unfold xv; rw [if_pos]
      exact ⟨sQ k, m.head, hN, rfl, by convert hz⟩
    have := Finset.single_le_sum (f := fun m => xv tQ sQ ψQ NC head H ini w m)
      (fun _ _ => Nat.zero_le _) hmem
    exact le_add_left (hx.trans this)

/-- **objective**: Σ_{c ∈ NC} y_c + Σ_m x_m ≤ #paid stays, when every non-NC chart has slr ≤ 0
(NC ⊇ {L > 0 or slr ≠ 0}). -/
theorem objective_le [WellFoundedLT C] (hK : ClassK Pub H Kfin ini w D)
    (hcert : ∀ k, Certified D tQ sQ ψQ k)
    (hNat : ∀ c, c ∉ NC → D.ka c + D.oa c + D.kb c ≤ finrank K (span K (D.Kρ c))) :
    ∑ c ∈ NC, hdW H ini w c + ∑ m, xv tQ sQ ψQ NC head H ini w m ≤ (stays H ini w).card := by
  classical
  -- non-NC chart: #sources ≤ hd
  have hnon : ∀ c, c ∉ NC → (srcs tQ sQ ψQ H ini w (fun _ => True) c).card ≤ hdW H ini w c := by
    intro c hc
    have h := card_srcs hK hcert c (fun _ => True) ∅ (Set.empty_subset _) (by simp)
    rw [span_empty, sup_bot_eq] at h
    have := hNat c hc
    have h' : ((D.ka c + D.oa c + D.kb c : ℕ) : ℤ) ≤ finrank K (span K (D.Kρ c)) := by exact_mod_cast this
    push_cast at h'
    omega
  set Z := fun c => srcs tQ sQ ψQ H ini w (fun _ => True) c
  -- heads used ⊆ image of (s, c) pairs with c ∉ NC
  set Pairs := (univ : Finset (C × C)).filter fun p => p.2 ∉ NC ∧ p.1 ∈ Z p.2
  have hx : ∑ m, xv tQ sQ ψQ NC head H ini w m ≤ Pairs.card := by
    have e : ∑ m, xv tQ sQ ψQ NC head H ini w m =
        ((univ : Finset M).filter fun m => headUsed tQ sQ ψQ NC head H ini w m).card := by
      rw [Finset.card_filter]; rfl
    rw [e]
    refine (Finset.card_le_card (t := Pairs.image fun p => head p.1 p.2) ?_).trans
      Finset.card_image_le
    · intro m hm
      obtain ⟨s, c, hc, rfl, hs⟩ := (Finset.mem_filter.1 hm).2
      exact Finset.mem_image.2 ⟨(s, c), Finset.mem_filter.2 ⟨Finset.mem_univ _, hc, hs⟩, rfl⟩
  have hP : Pairs.card = ∑ c ∈ univ.filter (· ∉ NC), (Z c).card := by
    rw [Finset.card_eq_sum_card_fiberwise (f := Prod.snd) (t := univ.filter (· ∉ NC))
      (by
        intro p hp
        simp only [Pairs, Finset.mem_coe, Finset.mem_filter, Finset.mem_univ, true_and] at hp
        simp [hp.1])]
    refine Finset.sum_congr rfl fun c hc => ?_
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hc
    apply Finset.card_nbij' (fun p => p.1) (fun s => (s, c))
    · rintro ⟨s, c'⟩ hp
      simp only [Pairs, Finset.coe_filter, Finset.mem_filter, Finset.mem_univ, true_and,
        Set.mem_ofPred_eq] at hp
      obtain ⟨⟨-, hs⟩, rfl⟩ := hp; exact hs
    · intro s hs
      simp only [Pairs, Finset.coe_filter, Finset.mem_filter, Finset.mem_univ, true_and,
        Set.mem_ofPred_eq]
      exact ⟨⟨hc, hs⟩, by simp⟩
    · rintro ⟨s, c'⟩ hp
      simp only [Pairs, Finset.coe_filter, Finset.mem_filter, Set.mem_ofPred_eq] at hp
      simp [hp.2]
    · intro s _; rfl
  have hsum := Finset.sum_filter_add_sum_filter_not (univ : Finset C) (· ∈ NC)
    (fun c => hdW H ini w c)
  have hNat' : ∑ c ∈ NC, hdW H ini w c = ∑ c ∈ univ.filter (· ∈ NC), hdW H ini w c := by
    congr 1; ext c; simp
  have hle : ∑ c ∈ univ.filter (· ∉ NC), (Z c).card ≤
      ∑ c ∈ univ.filter (· ∉ NC), hdW H ini w c :=
    Finset.sum_le_sum fun c hc => hnon c (Finset.mem_filter.1 hc).2
  rw [← sum_hd hK.acc]
  omega

end LP


/-! ## 9. Direct floor on the word (λ rows only, no LP) -/

/-- every class-K word pays cost ≥ κ · Σ_c max(0, needR_c), given per-stay cost ≥ κ. -/
theorem R1_floor_word {𝕜 : Type*} [Field 𝕜] [LinearOrder 𝕜] [IsStrictOrderedRing 𝕜] [Fintype C]
    (hK : ClassK Pub H Kfin ini w D) (cost : Reg × C → 𝕜) (κ : 𝕜) (hκ0 : 0 ≤ κ)
    (hκ : ∀ p ∈ stays H ini w, κ ≤ cost p) :
    κ * ((∑ c, max 0 ((finrank K (span K (D.Kρ c) ⊔ span K (D.Rρ c) : Submodule K (Reg → K)) : ℤ)
      - D.ka c - D.oa c - D.kb c) : ℤ) : 𝕜) ≤ ∑ p ∈ stays H ini w, cost p := by
  classical
  refine FloorGlue.global_floor_direct univ (stays H ini w) Prod.snd (fun _ _ => Finset.mem_univ _)
    _ (fun c _ => ?_) cost κ hκ0 hκ
  rw [hd_fibre hK.acc c]
  exact lam_row hK c

end FloorE2E

#print axioms FloorE2E.step_sim
#print axioms FloorE2E.proj_legal
#print axioms FloorE2E.hOnce_proj
#print axioms FloorE2E.forward_count'
#print axioms FloorE2E.chart_floor_word
#print axioms FloorE2E.R1_row
#print axioms FloorE2E.hP_word
#print axioms FloorE2E.hvec_word
#print axioms FloorE2E.F4_row
#print axioms FloorE2E.R3_row
#print axioms FloorE2E.hd_fibre
#print axioms FloorE2E.sum_hd
#print axioms FloorE2E.classK_of_counts
#print axioms FloorE2E.card_srcs
#print axioms FloorE2E.lam_row
#print axioms FloorE2E.alpha_row
#print axioms FloorE2E.beta_row
#print axioms FloorE2E.gamma_row
#print axioms FloorE2E.u_row
#print axioms FloorE2E.objective_le
#print axioms FloorE2E.R1_floor_word
