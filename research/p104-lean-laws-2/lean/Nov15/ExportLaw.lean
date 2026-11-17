/-
BIG-EXPORTLAW (cards/WILD/BIG/EXPORTLAW/THEORY.md), lane LEAN-NEXT4, Nov 16.

E1  reverse span law (any word): every row ever held at F lies in
    span(final rows at F) + span(departing / cleared / COPY-overwritten rows).
E2  export law (class N): rank(ρR(F) + ρK_F) + hb ≤ ke + kd + od + oe + (helper departures),
    i.e. hp ≥ rank − ke − kd − od − oe. This is STRONGER than the card's E2 (no −clr term): the proof
    here goes through the forward span law (T4's direction) plus a stay count, not through E1.
T4* owned arrivals counted: dim π(S_c) + (free non-X births that leave) ≤ public departures + y + oa.
Scope: dropping the owned terms (od, oe) is false (`drop_owned_false`, modelled on chart 1090 /
owned 1510, 1520); dropping od alone or oe alone is false too; dropping clr alone is TRUE (E2 above).
The event model extends JunkLB2's `Ev` (arrive / born / add / depart) with scale, clear and copy.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.LinearAlgebra.Dimension.OrzechProperty
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.LinearIndependent.Lemmas

open Finset Module Submodule

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace ExportLaw

variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

/-! ## The one-chart event model -/

/-- events at ONE chart `F`, in time order. `arrive i v`: register `i` arrives with row `v` (an owned
INIT is `arrive o 0`); `born b`: `b` is born at `F` (row = its token); `add i j c`: `row_i += c·row_j`;
`scale i u`: `row_i := u·row_i`; `depart i`; `clear i`: `row_i := 0`; `copy i j`: `row_i := row_j`. -/
inductive Ev (K Reg : Type*)
  | arrive (i : Reg) (v : Reg → K)
  | born (b : Reg)
  | add (i j : Reg) (c : K)
  | scale (i : Reg) (u : K)
  | depart (i : Reg)
  | clear (i : Reg)
  | copy (i j : Reg)

structure St (K Reg : Type*) where
  row : Reg → Reg → K
  pres : Finset Reg

def step : St K Reg → Ev K Reg → St K Reg
  | s, .arrive i v => ⟨Function.update s.row i v, insert i s.pres⟩
  | s, .born b => ⟨Function.update s.row b (Pi.single b 1), insert b s.pres⟩
  | s, .add i j c => ⟨Function.update s.row i (s.row i + c • s.row j), s.pres⟩
  | s, .scale i u => ⟨Function.update s.row i (u • s.row i), s.pres⟩
  | s, .depart i => ⟨s.row, s.pres.erase i⟩
  | s, .clear i => ⟨Function.update s.row i 0, s.pres⟩
  | s, .copy i j => ⟨Function.update s.row i (s.row j), s.pres⟩

def run : St K Reg → List (Ev K Reg) → St K Reg
  | s, [] => s
  | s, ev :: evs => run (step s ev) evs

/-- legality: arrivals/births of absent registers; ops only on present registers (co-presence);
ADD with `i ≠ j` and SCALE by a unit (invertible ops). -/
def LegalEv (s : St K Reg) : Ev K Reg → Prop
  | .arrive i _ => i ∉ s.pres
  | .born b => b ∉ s.pres
  | .add i j _ => i ≠ j ∧ i ∈ s.pres ∧ j ∈ s.pres
  | .scale i u => u ≠ 0 ∧ i ∈ s.pres
  | .depart i => i ∈ s.pres
  | .clear i => i ∈ s.pres
  | .copy i j => i ∈ s.pres ∧ j ∈ s.pres

def Legal : St K Reg → List (Ev K Reg) → Prop
  | _, [] => True
  | s, ev :: evs => LegalEv s ev ∧ Legal (step s ev) evs

/-- the rows present at a state. -/
def cur (s : St K Reg) : Set (Reg → K) := s.row '' (s.pres : Set Reg)

/-- `S_F`: every row ever held at `F` (at every state of the run). -/
def held : St K Reg → List (Ev K Reg) → Set (Reg → K)
  | s, [] => cur s
  | s, ev :: evs => cur s ∪ held (step s ev) evs

/-- the row an event removes from `F`: departing, cleared, or COPY-overwritten. -/
def remBy (s : St K Reg) : Ev K Reg → List (Reg → K)
  | .depart i => [s.row i]
  | .clear i => [s.row i]
  | .copy i _ => [s.row i]
  | _ => []

def removed : St K Reg → List (Ev K Reg) → List (Reg → K)
  | _, [] => []
  | s, ev :: evs => remBy s ev ++ removed (step s ev) evs

def start : St K Reg := ⟨fun _ => 0, ∅⟩

lemma cur_sub_held : ∀ (s : St K Reg) (evs : List (Ev K Reg)), cur s ⊆ held s evs
  | s, [] => le_rfl
  | s, _ :: _ => Set.subset_union_left

lemma final_sub_held : ∀ (s : St K Reg) (evs : List (Ev K Reg)), cur (run s evs) ⊆ held s evs
  | s, [] => le_rfl
  | s, ev :: evs => (final_sub_held (step s ev) evs).trans Set.subset_union_right

/-! ## E1. Reverse span law (any word) -/

lemma step_back (s : St K Reg) (ev : Ev K Reg) (hev : LegalEv s ev) :
    span K (cur s) ≤ span K (cur (step s ev)) ⊔ span K {v | v ∈ remBy s ev} := by
  rw [Submodule.span_le]
  rintro _ ⟨r, hr, rfl⟩
  simp only [Finset.mem_coe] at hr
  have keep : ∀ (t : St K Reg), r ∈ t.pres → t.row r = s.row r →
      s.row r ∈ span K (cur t) ⊔ span K {v | v ∈ remBy s ev} := fun t ht he =>
    Submodule.mem_sup_left (Submodule.subset_span ⟨r, ht, he⟩)
  have gone : s.row r ∈ remBy s ev → s.row r ∈ span K (cur (step s ev)) ⊔ span K {v | v ∈ remBy s ev} :=
    fun h => Submodule.mem_sup_right (Submodule.subset_span h)
  cases ev with
  | arrive i v =>
    have hri : r ≠ i := fun e => hev (e ▸ hr)
    exact keep _ (by simp [step, hr]) (by simp [step, Function.update_of_ne hri])
  | born b =>
    have hrb : r ≠ b := fun e => hev (e ▸ hr)
    exact keep _ (by simp [step, hr]) (by simp [step, Function.update_of_ne hrb])
  | add i j c =>
    obtain ⟨hij, hi, hj⟩ := hev
    by_cases hri : r = i
    · subst hri
      have e1 : s.row r = (step s (.add r j c)).row r - c • (step s (.add r j c)).row j := by
        simp only [step, Function.update_self, Function.update_of_ne (Ne.symm hij)]; abel
      rw [e1]
      exact Submodule.mem_sup_left (Submodule.sub_mem _ (Submodule.subset_span ⟨r, hi, rfl⟩)
        (Submodule.smul_mem _ _ (Submodule.subset_span ⟨j, hj, rfl⟩)))
    · exact keep _ hr (by simp [step, Function.update_of_ne hri])
  | scale i u =>
    obtain ⟨hu, hi⟩ := hev
    by_cases hri : r = i
    · subst hri
      have e1 : s.row r = u⁻¹ • (step s (.scale r u)).row r := by
        simp only [step, Function.update_self, smul_smul, inv_mul_cancel₀ hu, one_smul]
      rw [e1]
      exact Submodule.mem_sup_left (Submodule.smul_mem _ _ (Submodule.subset_span ⟨r, hi, rfl⟩))
    · exact keep _ hr (by simp [step, Function.update_of_ne hri])
  | depart i =>
    by_cases hri : r = i
    · subst hri; exact gone (by simp [remBy])
    · exact keep _ (by simp [step, hri, hr]) (by simp [step])
  | clear i =>
    by_cases hri : r = i
    · subst hri; exact gone (by simp [remBy])
    · exact keep _ hr (by simp [step, Function.update_of_ne hri])
  | copy i j =>
    by_cases hri : r = i
    · subst hri; exact gone (by simp [remBy])
    · exact keep _ hr (by simp [step, Function.update_of_ne hri])

/-- **E1 (reverse span law), any word.** `S_F ⊆ span(final rows at F) + span(removed rows)`, where
the removed rows are the departing, cleared and COPY-overwritten rows. -/
theorem E1_reverse : ∀ (s : St K Reg) (evs : List (Ev K Reg)), Legal s evs →
    span K (held s evs) ≤ span K (cur (run s evs)) ⊔ span K {v | v ∈ removed s evs}
  | s, [], _ => by
    simp only [held, run]; exact le_sup_left
  | s, ev :: evs, ⟨hev, hL⟩ => by
    have ih := E1_reverse (step s ev) evs hL
    have hrem : span K {v | v ∈ removed (step s ev) evs} ≤ span K {v | v ∈ removed s (ev :: evs)} :=
      Submodule.span_mono fun v hv => by simp only [removed, List.mem_append, Set.mem_ofPred_eq] at hv ⊢; exact Or.inr hv
    have hrem1 : span K {v | v ∈ remBy s ev} ≤ span K {v | v ∈ removed s (ev :: evs)} :=
      Submodule.span_mono fun v hv => by simp only [removed, List.mem_append, Set.mem_ofPred_eq] at hv ⊢; exact Or.inl hv
    have hcur : span K (cur (step s ev)) ≤ span K (held (step s ev) evs) :=
      Submodule.span_mono (cur_sub_held _ _)
    simp only [held, run, Submodule.span_union]
    refine sup_le ?_ (ih.trans (sup_le_sup_left hrem _))
    refine (step_back s ev hev).trans (sup_le ?_ (hrem1.trans le_sup_right))
    exact hcur.trans (ih.trans (sup_le_sup_left hrem _))

/-! ## Forward span law and the stay count -/

/-- the rows that ENTER `F`: arrival rows and birth tokens. -/
def entRows : List (Ev K Reg) → List (Reg → K)
  | [] => []
  | .arrive _ v :: evs => v :: entRows evs
  | .born b :: evs => Pi.single b 1 :: entRows evs
  | _ :: evs => entRows evs

/-- number of entries (arrivals + births) of registers in `C`. -/
def nEnt (C : Finset Reg) : List (Ev K Reg) → ℕ
  | [] => 0
  | .arrive i _ :: evs => (if i ∈ C then 1 else 0) + nEnt C evs
  | .born b :: evs => (if b ∈ C then 1 else 0) + nEnt C evs
  | _ :: evs => nEnt C evs

/-- number of departures of registers in `C`. -/
def nDep (C : Finset Reg) : List (Ev K Reg) → ℕ
  | [] => 0
  | .depart i :: evs => (if i ∈ C then 1 else 0) + nDep C evs
  | _ :: evs => nDep C evs

/-- number of CLEAR / COPY-overwrite events (the card's `clr`). -/
def nClr : List (Ev K Reg) → ℕ
  | [] => 0
  | .clear _ :: evs => 1 + nClr evs
  | .copy _ _ :: evs => 1 + nClr evs
  | _ :: evs => nClr evs

lemma entRows_length : ∀ evs : List (Ev K Reg), (entRows evs).length = nEnt univ evs
  | [] => rfl
  | .arrive _ _ :: evs => by simp [entRows, nEnt, entRows_length evs, add_comm]
  | .born _ :: evs => by simp [entRows, nEnt, entRows_length evs, add_comm]
  | .add _ _ _ :: evs => by simp [entRows, nEnt, entRows_length evs]
  | .scale _ _ :: evs => by simp [entRows, nEnt, entRows_length evs]
  | .depart _ :: evs => by simp [entRows, nEnt, entRows_length evs]
  | .clear _ :: evs => by simp [entRows, nEnt, entRows_length evs]
  | .copy _ _ :: evs => by simp [entRows, nEnt, entRows_length evs]

lemma nDep_union (C D : Finset Reg) (hCD : Disjoint C D) :
    ∀ evs : List (Ev K Reg), nDep (C ∪ D) evs = nDep C evs + nDep D evs
  | [] => rfl
  | .depart i :: evs => by
    have ih := nDep_union C D hCD evs
    simp only [nDep, mem_union, ih]
    by_cases hC : i ∈ C
    · have hD : i ∉ D := Finset.disjoint_left.mp hCD hC
      simp [hC, hD]; omega
    · by_cases hD : i ∈ D <;> simp [hC, hD] <;> omega
  | .arrive _ _ :: evs => by simp only [nDep]; exact nDep_union C D hCD evs
  | .born _ :: evs => by simp only [nDep]; exact nDep_union C D hCD evs
  | .add _ _ _ :: evs => by simp only [nDep]; exact nDep_union C D hCD evs
  | .scale _ _ :: evs => by simp only [nDep]; exact nDep_union C D hCD evs
  | .clear _ :: evs => by simp only [nDep]; exact nDep_union C D hCD evs
  | .copy _ _ :: evs => by simp only [nDep]; exact nDep_union C D hCD evs

/-- **stay count**: every entry at `F` ends in a departure or is still there at the end. -/
theorem stay_count (C : Finset Reg) : ∀ (s : St K Reg) (evs : List (Ev K Reg)), Legal s evs →
    nEnt C evs + (s.pres ∩ C).card = nDep C evs + ((run s evs).pres ∩ C).card
  | s, [], _ => by simp [nEnt, nDep, run]
  | s, ev :: evs, ⟨hev, hL⟩ => by
    have ih := stay_count C (step s ev) evs hL
    cases ev with
    | arrive i v =>
      simp only [nEnt, nDep, run] at ih ⊢
      have hp : ((step s (.arrive i v)).pres ∩ C).card =
          (s.pres ∩ C).card + (if i ∈ C then 1 else 0) := by
        simp only [step]
        by_cases hC : i ∈ C
        · rw [Finset.insert_inter_of_mem hC, Finset.card_insert_of_notMem
            (fun h => hev (Finset.mem_inter.mp h).1)]; simp [hC]
        · rw [Finset.insert_inter_of_notMem hC]; simp [hC]
      omega
    | born b =>
      simp only [nEnt, nDep, run] at ih ⊢
      have hp : ((step s (.born b)).pres ∩ C).card =
          (s.pres ∩ C).card + (if b ∈ C then 1 else 0) := by
        simp only [step]
        by_cases hC : b ∈ C
        · rw [Finset.insert_inter_of_mem hC, Finset.card_insert_of_notMem
            (fun h => hev (Finset.mem_inter.mp h).1)]; simp [hC]
        · rw [Finset.insert_inter_of_notMem hC]; simp [hC]
      omega
    | depart i =>
      simp only [nEnt, nDep, run] at ih ⊢
      have hp : ((step s (.depart i)).pres ∩ C).card + (if i ∈ C then 1 else 0) =
          (s.pres ∩ C).card := by
        simp only [step]
        rw [Finset.erase_inter]
        by_cases hC : i ∈ C
        · rw [Finset.card_erase_of_mem (Finset.mem_inter.mpr ⟨hev, hC⟩)]
          have : 0 < (s.pres ∩ C).card := Finset.card_pos.mpr ⟨i, Finset.mem_inter.mpr ⟨hev, hC⟩⟩
          simp only [hC, if_true]; omega
        · rw [Finset.erase_eq_of_notMem (fun h => hC (Finset.mem_inter.mp h).2)]; simp [hC]
      omega
    | add i j c => simp only [nEnt, nDep, run] at ih ⊢; exact ih
    | scale i u => simp only [nEnt, nDep, run] at ih ⊢; exact ih
    | clear i => simp only [nEnt, nDep, run] at ih ⊢; exact ih
    | copy i j => simp only [nEnt, nDep, run] at ih ⊢; exact ih

/-- **forward span law** (T4's direction): if every present row and every entering row lies in `N`,
so does every row ever held. Holds for every event, CLEAR and COPY included. -/
theorem forward_span (N : Submodule K (Reg → K)) : ∀ (s : St K Reg) (evs : List (Ev K Reg)),
    Legal s evs → cur s ⊆ N → (∀ v ∈ entRows evs, v ∈ N) → held s evs ⊆ N
  | s, [], _, hs, _ => hs
  | s, ev :: evs, ⟨hev, hL⟩, hs, hent => by
    have hent' : ∀ v ∈ entRows evs, v ∈ N := fun v hv => hent v (by
      cases ev <;> simp [entRows, hv])
    refine Set.union_subset hs (forward_span N _ evs hL ?_ hent')
    rintro _ ⟨r, hr, rfl⟩
    have old : ∀ q ∈ s.pres, s.row q ∈ N := fun q hq => hs ⟨q, hq, rfl⟩
    cases ev with
    | arrive i v =>
      simp only [step, Finset.coe_insert, Set.mem_insert_iff, Finset.mem_coe] at hr ⊢
      by_cases hri : r = i
      · subst hri; simp only [Function.update_self]; exact hent v (by simp [entRows])
      · rw [Function.update_of_ne hri]; exact old r (hr.resolve_left hri)
    | born b =>
      simp only [step, Finset.coe_insert, Set.mem_insert_iff, Finset.mem_coe] at hr ⊢
      by_cases hrb : r = b
      · subst hrb; simp only [Function.update_self]; exact hent _ (by simp [entRows])
      · rw [Function.update_of_ne hrb]; exact old r (hr.resolve_left hrb)
    | add i j c =>
      obtain ⟨_, hi, hj⟩ := hev
      simp only [step, Finset.mem_coe] at hr ⊢
      by_cases hri : r = i
      · subst hri; simp only [Function.update_self]
        exact N.add_mem (old r hi) (N.smul_mem c (old j hj))
      · rw [Function.update_of_ne hri]; exact old r hr
    | scale i u =>
      simp only [step, Finset.mem_coe] at hr ⊢
      by_cases hri : r = i
      · subst hri; simp only [Function.update_self]; exact N.smul_mem u (old r hr)
      · rw [Function.update_of_ne hri]; exact old r hr
    | depart i =>
      simp only [step, Finset.coe_erase, Set.mem_diff, Finset.mem_coe] at hr ⊢
      exact old r hr.1
    | clear i =>
      simp only [step, Finset.mem_coe] at hr ⊢
      by_cases hri : r = i
      · subst hri; simp only [Function.update_self]; exact N.zero_mem
      · rw [Function.update_of_ne hri]; exact old r hr
    | copy i j =>
      obtain ⟨_, hj⟩ := hev
      simp only [step, Finset.mem_coe] at hr ⊢
      by_cases hri : r = i
      · subst hri; simp only [Function.update_self]; exact old j hj
      · rw [Function.update_of_ne hri]; exact old r hr

/-- the registers born at `F`. -/
def bornSet : List (Ev K Reg) → Finset Reg
  | [] => ∅
  | .born b :: evs => insert b (bornSet evs)
  | _ :: evs => bornSet evs

lemma born_held : ∀ (s : St K Reg) (evs : List (Ev K Reg)) (b : Reg), b ∈ bornSet evs →
    (Pi.single b 1 : Reg → K) ∈ held s evs
  | s, [], b, h => by simp [bornSet] at h
  | s, .born b' :: evs, b, h => by
    rcases Finset.mem_insert.mp h with rfl | h
    · exact Set.mem_union_right _ (cur_sub_held _ evs ⟨b, by simp [step], by simp [step]⟩)
    · exact Set.mem_union_right _ (born_held _ evs b h)
  | s, .arrive _ _ :: evs, b, h => Set.mem_union_right _ (born_held _ evs b h)
  | s, .add _ _ _ :: evs, b, h => Set.mem_union_right _ (born_held _ evs b h)
  | s, .scale _ _ :: evs, b, h => Set.mem_union_right _ (born_held _ evs b h)
  | s, .depart _ :: evs, b, h => Set.mem_union_right _ (born_held _ evs b h)
  | s, .clear _ :: evs, b, h => Set.mem_union_right _ (born_held _ evs b h)
  | s, .copy _ _ :: evs, b, h => Set.mem_union_right _ (born_held _ evs b h)

/-- **forward count.** From the empty state: `dim φ(S_F) + |Tk| ≤ #entries`, for any linear `φ` and
any set `Tk` of registers whose tokens are held at `F` and killed by `φ`. -/
theorem forward_count (φ : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg))
    (hL : Legal start evs) (Tk : Finset Reg)
    (hTk : ∀ t ∈ Tk, (Pi.single t 1 : Reg → K) ∈ held start evs)
    (hφ : ∀ t ∈ Tk, φ (Pi.single t 1) = 0) :
    finrank K ((span K (held start evs)).map φ) + Tk.card ≤ nEnt univ evs := by
  classical
  have eqA : span K {v | v ∈ entRows evs} =
      span K ((((entRows evs).toFinset : Finset (Reg → K)) : Set (Reg → K))) := by
    congr 1; ext v; simp
  have hAc0 : finrank K (span K ((((entRows evs).toFinset : Finset (Reg → K)) : Set (Reg → K)))) ≤
      nEnt univ evs := by
    rw [← entRows_length]
    exact (finrank_span_finset_le_card _).trans (List.toFinset_card_le _)
  have hAc : finrank K (span K {v | v ∈ entRows evs}) ≤ nEnt univ evs :=
    (Submodule.finrank_mono eqA.le).trans hAc0
  set A := span K {v | v ∈ entRows evs}
  have hSA : held start evs ⊆ A :=
    forward_span A start evs hL (by simp [cur, start]) (fun v hv => Submodule.subset_span hv)
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

/-! ## E2. Export law (class N) -/

/-- **E2, export law (class N), strong form.** One chart `F ≠ V`, a legal event list from the empty
state. Registers are helpers `H`, kept publics `Kp`, owned `Ow` (a partition). Class N at `F`: a
helper still at `F` at the end ends as its own token. `ρ` kills helper tokens. `R` is any set of rows
held at `F` (e.g. the kept rows at kept events), `K_F` the span of the final rows of kept enders.
`HB` = helpers born at `F` that are gone at the end (free birth stays). Then
`rank(ρR + ρK_F) + |HB| ≤ ke + kd + od + oe + (helper departures)`.
Since helper departures = hp + hb (paid stays + birth stays), this is `hp ≥ rank − ke − kd − od − oe`:
the card's E2 WITHOUT the `− clr` term. -/
theorem E2_export (ρ : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg)) (hL : Legal start evs)
    (H Kp Ow : Finset Reg) (hKO : Disjoint Kp Ow) (hcov : univ \ H = Kp ∪ Ow)
    (hN : ∀ h ∈ H, h ∈ (run start evs).pres → (run start evs).row h = Pi.single h 1)
    (hρ : ∀ h ∈ H, ρ (Pi.single h 1) = 0)
    (R : Set (Reg → K)) (hR : R ⊆ held start evs) :
    finrank K ((span K R).map ρ ⊔
        (span K ((run start evs).row '' (((run start evs).pres ∩ Kp : Finset Reg) : Set Reg))).map ρ :
          Submodule K (Reg → K)) +
      ((H ∩ bornSet evs) \ (run start evs).pres).card ≤
    ((run start evs).pres ∩ Kp).card + nDep Kp evs + nDep Ow evs + ((run start evs).pres ∩ Ow).card +
      nDep H evs := by
  classical
  have hc := stay_count (K := K) univ start evs hL
  have h0 : (start (K := K) (Reg := Reg)).pres = ∅ := rfl
  rw [h0] at hc
  simp only [Finset.empty_inter, Finset.card_empty, add_zero, Finset.inter_univ] at hc
  set sf := run (start (K := K) (Reg := Reg)) evs
  set F := sf.pres
  set HB := (H ∩ bornSet evs) \ F
  set Tk := HB ∪ (F ∩ H)
  have hdisj : Disjoint HB (F ∩ H) := by
    rw [Finset.disjoint_left]; intro x hx hx'
    exact (Finset.mem_sdiff.mp hx).2 (Finset.mem_inter.mp hx').1
  have hTk : ∀ t ∈ Tk, (Pi.single t 1 : Reg → K) ∈ held start evs := by
    intro t ht
    rcases Finset.mem_union.mp ht with ht | ht
    · exact born_held _ evs t (Finset.mem_inter.mp (Finset.mem_sdiff.mp ht).1).2
    · obtain ⟨htF, htH⟩ := Finset.mem_inter.mp ht
      exact final_sub_held _ evs ⟨t, htF, hN t htH htF⟩
  have hφ : ∀ t ∈ Tk, ρ (Pi.single t 1) = 0 := by
    intro t ht
    rcases Finset.mem_union.mp ht with ht | ht
    · exact hρ t (Finset.mem_inter.mp (Finset.mem_sdiff.mp ht).1).1
    · exact hρ t (Finset.mem_inter.mp ht).2
  have hfc := forward_count ρ evs hL Tk hTk hφ
  rw [Finset.card_union_of_disjoint hdisj] at hfc
  -- rank of ρR + ρK_F is at most rank of ρ(S_F)
  have hsub : (span K R).map ρ ⊔ (span K (sf.row '' ((F ∩ Kp : Finset Reg) : Set Reg))).map ρ ≤
      (span K (held start evs)).map ρ := by
    rw [← Submodule.map_sup]
    refine Submodule.map_mono (sup_le (Submodule.span_mono hR) (Submodule.span_le.mpr ?_))
    rintro _ ⟨r, hr, rfl⟩
    exact Submodule.subset_span (final_sub_held _ evs ⟨r, (Finset.mem_inter.mp hr).1, rfl⟩)
  have hrk := Submodule.finrank_mono hsub
  -- counting
  have hdep : nDep (univ : Finset Reg) evs = nDep H evs + nDep Kp evs + nDep Ow evs := by
    have e : (univ : Finset Reg) = H ∪ (Kp ∪ Ow) := by
      rw [← hcov]; ext x; by_cases hx : x ∈ H <;> simp [hx]
    rw [e, nDep_union H _ (by rw [← hcov]; exact Finset.disjoint_sdiff), nDep_union Kp Ow hKO, add_assoc]
  have hF : F.card = (F ∩ H).card + (F ∩ Kp).card + (F ∩ Ow).card := by
    have e1 := Finset.card_inter_add_card_sdiff F H
    have e2 : F \ H = (F ∩ Kp) ∪ (F ∩ Ow) := by
      rw [← Finset.inter_union_distrib_left, ← hcov]; ext x; simp
    have e3 : Disjoint (F ∩ Kp) (F ∩ Ow) :=
      Finset.disjoint_of_subset_left Finset.inter_subset_right
        (Finset.disjoint_of_subset_right Finset.inter_subset_right hKO)
    rw [e2, Finset.card_union_of_disjoint e3] at e1; omega
  omega

/-- **E2 as stated on the card** (with `hp = helper departures − hb`, in ℤ): the `− clr` version
follows from the strong form, since `clr ≥ 0`. -/
theorem E2_card (ρ : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg)) (hL : Legal start evs)
    (H Kp Ow : Finset Reg) (hKO : Disjoint Kp Ow) (hcov : univ \ H = Kp ∪ Ow)
    (hN : ∀ h ∈ H, h ∈ (run start evs).pres → (run start evs).row h = Pi.single h 1)
    (hρ : ∀ h ∈ H, ρ (Pi.single h 1) = 0)
    (R : Set (Reg → K)) (hR : R ⊆ held start evs) :
    ((finrank K ((span K R).map ρ ⊔
        (span K ((run start evs).row '' (((run start evs).pres ∩ Kp : Finset Reg) : Set Reg))).map ρ :
          Submodule K (Reg → K)) : ℕ) : ℤ)
      - ((run start evs).pres ∩ Kp).card - nDep Kp evs - nDep Ow evs
      - ((run start evs).pres ∩ Ow).card - nClr evs ≤
    (nDep H evs : ℤ) - ((H ∩ bornSet evs) \ (run start evs).pres).card := by
  have := E2_export ρ evs hL H Kp Ow hKO hcov hN hρ R hR
  have h0 : (0 : ℤ) ≤ nClr evs := Int.natCast_nonneg _
  omega

/-! ## T4*. Owned arrivals counted (class N) -/

/-- **T4\*** (class N, owned arrivals counted). One chart `c ≠ V`. `Pub` = public registers, the rest
owned. Class N: a public register still at `c` at the end, other than a Y main in `Ey`, ends as its
own token, and `π` kills that token. `π` kills the tokens of non-X births (`Xs` = live-X registers).
`BNX` = non-X registers born at `c` that are gone at the end (free birth stays). Then
`dim π(S_c) + |BNX| ≤ (public departures) + |Ey| + (owned entries)`.
No "arrivals carry no c-born coordinates" hypothesis: owned registers may descend. -/
theorem T4_star (π : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg)) (hL : Legal start evs)
    (Pub Ey Xs : Finset Reg)
    (hN : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → (run start evs).row h = Pi.single h 1)
    (hπE : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → π (Pi.single h 1) = 0)
    (hπB : ∀ b, b ∉ Xs → π (Pi.single b 1) = 0) :
    finrank K ((span K (held start evs)).map π) +
      ((bornSet evs \ Xs) \ (run start evs).pres).card ≤
    nDep Pub evs + Ey.card + nEnt (univ \ Pub) evs := by
  classical
  have hc := stay_count (K := K) univ start evs hL
  have hco := stay_count (K := K) (univ \ Pub) start evs hL
  have h0 : (start (K := K) (Reg := Reg)).pres = ∅ := rfl
  rw [h0] at hc hco
  simp only [Finset.empty_inter, Finset.card_empty, add_zero, Finset.inter_univ] at hc hco
  set sf := run (start (K := K) (Reg := Reg)) evs
  set F := sf.pres
  set BNX := (bornSet evs \ Xs) \ F
  set PE := (F ∩ Pub) \ Ey
  have hdisj : Disjoint BNX PE := by
    rw [Finset.disjoint_left]; intro x hx hx'
    exact (Finset.mem_sdiff.mp hx).2 (Finset.mem_inter.mp (Finset.mem_sdiff.mp hx').1).1
  have hTk : ∀ t ∈ BNX ∪ PE, (Pi.single t 1 : Reg → K) ∈ held start evs := by
    intro t ht
    rcases Finset.mem_union.mp ht with ht | ht
    · exact born_held _ evs t (Finset.mem_sdiff.mp (Finset.mem_sdiff.mp ht).1).1
    · obtain ⟨htFP, htY⟩ := Finset.mem_sdiff.mp ht
      obtain ⟨htF, htP⟩ := Finset.mem_inter.mp htFP
      exact final_sub_held _ evs ⟨t, htF, hN t htP htF htY⟩
  have hφ : ∀ t ∈ BNX ∪ PE, π (Pi.single t 1) = 0 := by
    intro t ht
    rcases Finset.mem_union.mp ht with ht | ht
    · exact hπB t (Finset.mem_sdiff.mp (Finset.mem_sdiff.mp ht).1).2
    · obtain ⟨htFP, htY⟩ := Finset.mem_sdiff.mp ht
      obtain ⟨htF, htP⟩ := Finset.mem_inter.mp htFP
      exact hπE t htP htF htY
  have hfc := forward_count π evs hL _ hTk hφ
  rw [Finset.card_union_of_disjoint hdisj] at hfc
  have hdep : nDep (univ : Finset Reg) evs = nDep Pub evs + nDep (univ \ Pub) evs := by
    rw [← nDep_union Pub _ Finset.disjoint_sdiff, Finset.union_sdiff_of_subset (Finset.subset_univ _)]
  have hF : F.card = (F ∩ Pub).card + (F ∩ (univ \ Pub)).card := by
    have e1 := Finset.card_inter_add_card_sdiff F Pub
    have e2 : F \ Pub = F ∩ (univ \ Pub) := by ext x; simp
    rw [e2] at e1; omega
  have hPE : (F ∩ Pub).card ≤ PE.card + Ey.card := by
    calc (F ∩ Pub).card ≤ (PE ∪ Ey).card := by
          apply Finset.card_le_card; intro x hx
          by_cases hy : x ∈ Ey
          · exact Finset.mem_union_right _ hy
          · exact Finset.mem_union_left _ (Finset.mem_sdiff.mpr ⟨hx, hy⟩)
      _ ≤ _ := Finset.card_union_le _ _
  omega

/-! ## T4* card form d + y + oa + xb (LEAN-NEXT5) -/

/-- departures of a set = sum of single-register departures. -/
lemma nDep_eq_sum (C : Finset Reg) : ∀ evs : List (Ev K Reg), nDep C evs = ∑ i ∈ C, nDep {i} evs
  | [] => by simp [nDep]
  | .depart j :: evs => by
    simp only [nDep, nDep_eq_sum C evs, Finset.sum_add_distrib, Finset.mem_singleton]
    congr 1
    rw [Finset.sum_ite_eq C j]
  | .arrive _ _ :: evs => by simp only [nDep]; exact nDep_eq_sum C evs
  | .born _ :: evs => by simp only [nDep]; exact nDep_eq_sum C evs
  | .add _ _ _ :: evs => by simp only [nDep]; exact nDep_eq_sum C evs
  | .scale _ _ :: evs => by simp only [nDep]; exact nDep_eq_sum C evs
  | .clear _ :: evs => by simp only [nDep]; exact nDep_eq_sum C evs
  | .copy _ _ :: evs => by simp only [nDep]; exact nDep_eq_sum C evs

/-- **T4\* card form.** Under "each register enters the chart at most once" (`hOnce`; with Legal runs this
is: it leaves at most once and never comes back, i.e. monotone public charts; owned registers are
not restricted):
`dim π(S_c) ≤ d + y + oa + xb`, with `d` = public registers that ARRIVED (were not born at c) and later
depart, `y = |Ey|`, `oa` = owned entries, `xb` = X registers born at c. -/
theorem T4_card (π : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg)) (hL : Legal start evs)
    (Pub Ey Xs : Finset Reg)
    (hN : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → (run start evs).row h = Pi.single h 1)
    (hπE : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → π (Pi.single h 1) = 0)
    (hπB : ∀ b, b ∉ Xs → π (Pi.single b 1) = 0)
    (hOnce : ∀ i ∈ Pub, nEnt {i} evs ≤ 1) :
    finrank K ((span K (held start evs)).map π) ≤
      ((Pub \ bornSet evs).filter fun i => 0 < nDep {i} evs).card + Ey.card +
        nEnt (univ \ Pub) evs + (bornSet evs ∩ Xs).card := by
  classical
  have hT := T4_star π evs hL Pub Ey Xs hN hπE hπB
  set F := (run (start (K := K) (Reg := Reg)) evs).pres
  have hi1 : ∀ i, nEnt {i} evs = nDep {i} evs + (F ∩ {i}).card := by
    intro i
    have := stay_count (K := K) {i} start evs hL
    have h0 : (start (K := K) (Reg := Reg)).pres = ∅ := rfl
    rw [h0] at this
    simpa using this
  have hle1 : ∀ i ∈ Pub, nDep {i} evs ≤ 1 := fun i hi => by have := hi1 i; have := hOnce i hi; omega
  set Dp := Pub.filter fun i => 0 < nDep {i} evs
  have hsum : nDep Pub evs ≤ Dp.card := by
    rw [nDep_eq_sum, Finset.card_filter]
    exact Finset.sum_le_sum fun i hi => by
      have := hle1 i hi
      split_ifs with h <;> omega
  have hsub : Dp ⊆ ((Pub \ bornSet evs).filter fun i => 0 < nDep {i} evs) ∪
      ((bornSet evs \ Xs) \ F) ∪ (bornSet evs ∩ Xs) := by
    intro i hi
    obtain ⟨hiP, hid⟩ := Finset.mem_filter.mp hi
    by_cases hb : i ∈ bornSet evs
    · by_cases hx : i ∈ Xs
      · exact Finset.mem_union_right _ (Finset.mem_inter.mpr ⟨hb, hx⟩)
      · refine Finset.mem_union_left _ (Finset.mem_union_right _ ?_)
        refine Finset.mem_sdiff.mpr ⟨Finset.mem_sdiff.mpr ⟨hb, hx⟩, fun hF => ?_⟩
        have h1 := hi1 i
        have h2 := hOnce i hiP
        have h3 : (F ∩ {i}).card = 1 := by
          rw [Finset.inter_singleton_of_mem hF, Finset.card_singleton]
        omega
    · exact Finset.mem_union_left _ (Finset.mem_union_left _
        (Finset.mem_filter.mpr ⟨Finset.mem_sdiff.mpr ⟨hiP, hb⟩, hid⟩))
  have hc := (Finset.card_le_card hsub).trans (Finset.card_union_le _ _)
  have hc2 := Finset.card_union_le ((Pub \ bornSet evs).filter fun i => 0 < nDep {i} evs)
    ((bornSet evs \ Xs) \ F)
  omega

/-! ## Scope: which owned/clear terms can be dropped -/

/-- `e_0` and `e_0 + e_2` are independent: rank 2. -/
lemma rank_two {n : ℕ} (a b : Fin n) (hab : a ≠ b) :
    finrank ℚ (span ℚ (Set.range ![(Pi.single a 1 : Fin n → ℚ), Pi.single a 1 + Pi.single b 1])) = 2 := by
  have hli : LinearIndependent ℚ ![(Pi.single a 1 : Fin n → ℚ), Pi.single a 1 + Pi.single b 1] := by
    rw [LinearIndependent.pair_iff]
    intro s t hst
    have h1 := congrFun hst a
    have h2 := congrFun hst b
    simp [Pi.single_apply, hab, Ne.symm hab] at h1 h2
    exact ⟨by linarith, h2⟩
  rw [finrank_span_eq_card hli]; simp

/-- **Dropping the owned terms is false** (chart 1090 mirror: owned 1510 descends INTO F carrying
content and ends there, owned 1520 picks it up and LEAVES F). Registers: `0` = kept `x`, `1` = owned
`o₁` (1510), `2` = the kept register whose coordinate `o₁` carries (absent from F), `3` = owned `o₂`
(1520). Events: `o₁` arrives with `e₂`; `x` arrives with `e₀`; `x += o₁`; `x` departs; `o₂` INITs
(arrives with 0); `o₂ += o₁`; `o₂` departs; `o₁` stays. No helpers (`ρ = id`, hp = hb = 0), no kept
ender (`K_F = 0`). The kept rows of `x` at kept events, `e₀` and `e₀ + e₂`, have rank 2 > 1 =
ke + kd + hp; with the owned terms (od = oe = 1) the bound 3 holds (`E2_export`). -/
theorem drop_owned_false :
    let evs : List (Ev ℚ (Fin 4)) := [.arrive 1 (Pi.single 2 1), .arrive 0 (Pi.single 0 1),
      .add 0 1 1, .depart 0, .arrive 3 0, .add 3 1 1, .depart 3]
    let R : Set (Fin 4 → ℚ) := Set.range ![(Pi.single 0 1 : Fin 4 → ℚ), Pi.single 0 1 + Pi.single 2 1]
    Legal start evs ∧ R ⊆ held start evs ∧ (run start evs).pres = {1} ∧
      nDep ({0, 2} : Finset (Fin 4)) evs = 1 ∧ nDep ({1, 3} : Finset (Fin 4)) evs = 1 ∧
      finrank ℚ (span ℚ R) = 2 ∧
      ¬ finrank ℚ (span ℚ R) ≤ ((run start evs).pres ∩ {0, 2}).card + nDep ({0, 2} : Finset (Fin 4)) evs + 0 := by
  intro evs R
  have hrank : finrank ℚ (span ℚ R) = 2 := rank_two 0 2 (by decide)
  have hpres : (run start evs).pres = {1} := by
    simp [evs, run, step, start]
  have hd1 : nDep ({0, 2} : Finset (Fin 4)) evs = 1 := by simp [evs, nDep]
  refine ⟨?_, ?_, hpres, hd1, by simp [evs, nDep], hrank, ?_⟩
  · simp [evs, Legal, LegalEv, step, start]
  · rintro _ ⟨k, rfl⟩
    fin_cases k
    · -- e₀: x's row right after its arrival (third state)
      simp only [evs, held]
      refine Or.inr (Or.inr (Or.inl ⟨0, by simp [step, start], by simp [step, start]⟩))
    · -- e₀ + e₂: x's row right after `x += o₁` (fourth state)
      simp only [evs, held]
      refine Or.inr (Or.inr (Or.inr (Or.inl ⟨0, by simp [step, start], ?_⟩)))
      simp [step, start, Function.update_of_ne (show (0 : Fin 4) ≠ 1 by decide)]
  · rw [hrank, hpres, hd1]; decide

/-- **Dropping `od` alone is false**: one owned register `o` (= 1) brings `e₂` in, `x += o`, both
leave. Rank 2 > ke + kd + oe + hp = 0 + 1 + 0 + 0; with `od = 1` the bound 2 holds. -/
theorem drop_od_false :
    let evs : List (Ev ℚ (Fin 3)) := [.arrive 1 (Pi.single 2 1), .arrive 0 (Pi.single 0 1),
      .add 0 1 1, .depart 0, .depart 1]
    let R : Set (Fin 3 → ℚ) := Set.range ![(Pi.single 0 1 : Fin 3 → ℚ), Pi.single 0 1 + Pi.single 2 1]
    Legal start evs ∧ R ⊆ held start evs ∧ (run start evs).pres = ∅ ∧
      nDep ({0, 2} : Finset (Fin 3)) evs = 1 ∧ nDep ({1} : Finset (Fin 3)) evs = 1 ∧
      ¬ finrank ℚ (span ℚ R) ≤ 0 + nDep ({0, 2} : Finset (Fin 3)) evs + 0 + 0 := by
  intro evs R
  have hrank : finrank ℚ (span ℚ R) = 2 := rank_two 0 2 (by decide)
  have hd1 : nDep ({0, 2} : Finset (Fin 3)) evs = 1 := by simp [evs, nDep]
  refine ⟨?_, ?_, ?_, hd1, by simp [evs, nDep], ?_⟩
  · simp [evs, Legal, LegalEv, step, start]
  · rintro _ ⟨k, rfl⟩
    fin_cases k
    · simp only [evs, held]
      refine Or.inr (Or.inr (Or.inl ⟨0, by simp [step, start], by simp [step, start]⟩))
    · simp only [evs, held]
      refine Or.inr (Or.inr (Or.inr (Or.inl ⟨0, by simp [step, start], ?_⟩)))
      simp [step, start, Function.update_of_ne (show (0 : Fin 3) ≠ 1 by decide)]
  · simp [evs, run, step, start]
  · rw [hrank, hd1]; decide

/-- **Dropping `oe` alone is false**: as `drop_od_false`, but `o` stays at F (ends there). -/
theorem drop_oe_false :
    let evs : List (Ev ℚ (Fin 3)) := [.arrive 1 (Pi.single 2 1), .arrive 0 (Pi.single 0 1),
      .add 0 1 1, .depart 0]
    let R : Set (Fin 3 → ℚ) := Set.range ![(Pi.single 0 1 : Fin 3 → ℚ), Pi.single 0 1 + Pi.single 2 1]
    Legal start evs ∧ R ⊆ held start evs ∧ (run start evs).pres = {1} ∧
      nDep ({0, 2} : Finset (Fin 3)) evs = 1 ∧ nDep ({1} : Finset (Fin 3)) evs = 0 ∧
      ¬ finrank ℚ (span ℚ R) ≤ ((run start evs).pres ∩ {0, 2}).card +
        nDep ({0, 2} : Finset (Fin 3)) evs + nDep ({1} : Finset (Fin 3)) evs + 0 := by
  intro evs R
  have hrank : finrank ℚ (span ℚ R) = 2 := rank_two 0 2 (by decide)
  have hpres : (run start evs).pres = {1} := by
    simp [evs, run, step, start]
  have hd1 : nDep ({0, 2} : Finset (Fin 3)) evs = 1 := by simp [evs, nDep]
  have hd2 : nDep ({1} : Finset (Fin 3)) evs = 0 := by simp [evs, nDep]
  refine ⟨?_, ?_, hpres, hd1, hd2, ?_⟩
  · simp [evs, Legal, LegalEv, step, start]
  · rintro _ ⟨k, rfl⟩
    fin_cases k
    · simp only [evs, held]
      refine Or.inr (Or.inr (Or.inl ⟨0, by simp [step, start], by simp [step, start]⟩))
    · simp only [evs, held]
      refine Or.inr (Or.inr (Or.inr (Or.inl ⟨0, by simp [step, start], ?_⟩)))
      simp [step, start, Function.update_of_ne (show (0 : Fin 3) ≠ 1 by decide)]
  · rw [hrank, hpres, hd1, hd2]; decide

end ExportLaw

#print axioms ExportLaw.E1_reverse
#print axioms ExportLaw.stay_count
#print axioms ExportLaw.forward_span
#print axioms ExportLaw.forward_count
#print axioms ExportLaw.E2_export
#print axioms ExportLaw.E2_card
#print axioms ExportLaw.T4_star
#print axioms ExportLaw.nDep_eq_sum
#print axioms ExportLaw.T4_card
#print axioms ExportLaw.drop_owned_false
#print axioms ExportLaw.drop_od_false
#print axioms ExportLaw.drop_oe_false
