/-
BITE-DEPART Lemma D1 (kept-content departer law), lane LEAN-NEXT16, Nov 16.
Source: cards/WILD/BIG/BITE-DEPART/RESULT.md §3. See DepartD1.md.

D1: a_S(c) ≤ d(c) + e_S(c) + oa(c), where a_S = dim π_S(public arrival rows), d = public ARRIVALS that
later depart (paid stops; t4rho.py `d = len(dep)`, born registers excluded), e_S = ARRIVED enders whose
final has an S coordinate, oa = owned entries (arrivals + INITs).

Extends ExportLaw.T4_star / T4_card (same one-chart event model, imported).
* `D1_all`: with d counting ALL public departures (born-at-c ones too) and e_S all public enders with
  π(final) ≠ 0, D1 holds in class N with no further hypothesis.
* `D1`: the card's form (d and e_S over arrivals only) holds under `hArr`: public arrival rows carry no
  coordinate of a register born at c. Proof: T4_card with π' = π ∘ (kill c-born coordinates).
* `D1_false`: WITHOUT hArr the card's form is FALSE (an S register born at c leaves; a helper arrives
  carrying its coordinate, which only an owned descent can deliver, and is cleaned to its token).
-/
import Nov15.ExportLaw

set_option linter.unusedSectionVars false

namespace DepartD1
open Finset Module Submodule ExportLaw

variable {K Reg : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]

/-- rows of the arrivals of registers in `P`. -/
def arrRows (P : Finset Reg) : List (Ev K Reg) → List (Reg → K)
  | [] => []
  | .arrive i v :: evs => if i ∈ P then v :: arrRows P evs else arrRows P evs
  | _ :: evs => arrRows P evs

/-- registers in `P` that arrive (are not only born). -/
def arrSet : List (Ev K Reg) → Finset Reg
  | [] => ∅
  | .arrive i _ :: evs => insert i (arrSet evs)
  | _ :: evs => arrSet evs

lemma arr_held (P : Finset Reg) : ∀ (s : St K Reg) (evs : List (Ev K Reg)) (v : Reg → K),
    v ∈ arrRows P evs → v ∈ held s evs
  | s, [], v, h => by simp [arrRows] at h
  | s, .arrive i w :: evs, v, h => by
    simp only [arrRows] at h
    split_ifs at h with hi
    · rcases List.mem_cons.mp h with rfl | h
      · exact Set.mem_union_right _ (cur_sub_held _ evs ⟨i, by simp [step], by simp [step]⟩)
      · exact Set.mem_union_right _ (arr_held P _ evs v h)
    · exact Set.mem_union_right _ (arr_held P _ evs v h)
  | s, .born _ :: evs, v, h => Set.mem_union_right _ (arr_held P _ evs v h)
  | s, .add _ _ _ :: evs, v, h => Set.mem_union_right _ (arr_held P _ evs v h)
  | s, .scale _ _ :: evs, v, h => Set.mem_union_right _ (arr_held P _ evs v h)
  | s, .depart _ :: evs, v, h => Set.mem_union_right _ (arr_held P _ evs v h)
  | s, .clear _ :: evs, v, h => Set.mem_union_right _ (arr_held P _ evs v h)
  | s, .copy _ _ :: evs, v, h => Set.mem_union_right _ (arr_held P _ evs v h)

/-- `a_S`: dimension of π applied to the public arrival rows. -/
noncomputable def aS (π : (Reg → K) →ₗ[K] (Reg → K)) (Pub : Finset Reg) (evs : List (Ev K Reg)) : ℕ :=
  finrank K ((span K {v | v ∈ arrRows Pub evs}).map π)

lemma aS_le_held (π : (Reg → K) →ₗ[K] (Reg → K)) (Pub : Finset Reg) (evs : List (Ev K Reg)) :
    aS π Pub evs ≤ finrank K ((span K (held start evs)).map π) :=
  Submodule.finrank_mono (Submodule.map_mono (Submodule.span_mono fun v hv => arr_held Pub start evs v hv))

/-- **D1, all-departures form (class N).** `Ey` = public enders whose final has π ≠ 0; every other
public ender ends as its own token. Then `a_S ≤ (all public departures) + |Ey| + oa`. -/
theorem D1_all (π : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg)) (hL : Legal start evs)
    (Pub : Finset Reg)
    (hN : ∀ h ∈ Pub, h ∈ (run start evs).pres → π ((run start evs).row h) = 0 →
      (run start evs).row h = Pi.single h 1) :
    aS π Pub evs ≤ nDep Pub evs +
      (((run start evs).pres ∩ Pub).filter (fun h => π ((run start evs).row h) ≠ 0)).card +
      nEnt (univ \ Pub) evs := by
  set Ey := ((run start evs).pres ∩ Pub).filter (fun h => π ((run start evs).row h) ≠ 0)
  have hN' : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → (run start evs).row h = Pi.single h 1 :=
    fun h hP hF hE => hN h hP hF (by by_contra hne; exact hE (by simp [Ey, hF, hP, hne]))
  have hπE : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → π (Pi.single h 1) = 0 :=
    fun h hP hF hE => by
      have hz : π ((run start evs).row h) = 0 := by
        by_contra hne; exact hE (by simp [Ey, hF, hP, hne])
      rwa [hN h hP hF hz] at hz
  have := T4_star π evs hL Pub Ey univ hN' hπE (fun b hb => absurd (mem_univ b) hb)
  have := aS_le_held π Pub evs
  omega

/-- kill the coordinates in `B`. -/
def killB (B : Finset Reg) : (Reg → K) →ₗ[K] (Reg → K) where
  toFun v := fun i => if i ∈ B then 0 else v i
  map_add' v w := by funext i; by_cases h : i ∈ B <;> simp [h]
  map_smul' c v := by funext i; by_cases h : i ∈ B <;> simp [h]

/-- **D1 (card form).** Class N as above, plus:
* `hBorn`: a public register born at c that ends at c ends as its own token (helpers);
* `hArr`: public arrival rows carry no coordinate of a register born at c.
Then `a_S ≤ d + e_S + oa`, with `d` = public registers that arrived and depart, `e_S` = arrived public
enders whose final has π ≠ 0, `oa` = owned entries. Needs `hOnce` (each public register enters c at
most once; [C] on #7623, ExportLaw.md). -/
theorem D1 (π : (Reg → K) →ₗ[K] (Reg → K)) (evs : List (Ev K Reg)) (hL : Legal start evs)
    (Pub : Finset Reg)
    (hN : ∀ h ∈ Pub, h ∈ (run start evs).pres → π ((run start evs).row h) = 0 →
      (run start evs).row h = Pi.single h 1)
    (hBorn : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∈ bornSet evs →
      (run start evs).row h = Pi.single h 1)
    (hArr : ∀ v ∈ arrRows Pub evs, ∀ b ∈ bornSet evs, v b = 0)
    (hOnce : ∀ i ∈ Pub, nEnt {i} evs ≤ 1) :
    aS π Pub evs ≤ ((Pub \ bornSet evs).filter fun i => 0 < nDep {i} evs).card +
      ((((run start evs).pres ∩ Pub) \ bornSet evs).filter (fun h => π ((run start evs).row h) ≠ 0)).card +
      nEnt (univ \ Pub) evs := by
  set B := bornSet evs with hB
  set π' := π ∘ₗ killB B
  set Ey := (((run start evs).pres ∩ Pub) \ B).filter (fun h => π ((run start evs).row h) ≠ 0)
  have hkillTok : ∀ h, h ∉ B → killB B (Pi.single h 1 : Reg → K) = Pi.single h 1 := by
    intro h hh; funext i
    by_cases hi : i ∈ B
    · have : i ≠ h := fun e => hh (e ▸ hi)
      simp [killB, hi, this]
    · simp [killB, hi]
  have hkillB : ∀ h, h ∈ B → killB B (Pi.single h 1 : Reg → K) = 0 := by
    intro h hh; funext i
    by_cases hi : i ∈ B
    · simp [killB, hi]
    · have : i ≠ h := fun e => hi (e ▸ hh)
      simp [killB, hi, this]
  have hnotEy : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey →
      h ∈ B ∨ π ((run start evs).row h) = 0 := by
    intro h hP hF hE
    by_cases hb : h ∈ B
    · exact Or.inl hb
    · right; by_contra hne; exact hE (by simp [Ey, hF, hP, hne, hb])
  have hN' : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → (run start evs).row h = Pi.single h 1 := by
    intro h hP hF hE
    rcases hnotEy h hP hF hE with hb | hz
    · exact hBorn h hP hF hb
    · exact hN h hP hF hz
  have hπE : ∀ h ∈ Pub, h ∈ (run start evs).pres → h ∉ Ey → π' (Pi.single h 1) = 0 := by
    intro h hP hF hE
    by_cases hb : h ∈ B
    · simp [π', hkillB h hb]
    · have hz : π ((run start evs).row h) = 0 := (hnotEy h hP hF hE).resolve_left hb
      rw [hN h hP hF hz] at hz
      simp [π', hkillTok h hb, hz]
  have hπB : ∀ b, b ∉ (univ \ B) → π' (Pi.single b 1) = 0 := by
    intro b hb
    have : b ∈ B := by simpa using hb
    simp [π', hkillB b this]
  have hT := T4_card π' evs hL Pub Ey (univ \ B) hN' hπE hπB hOnce
  have hx : (bornSet evs ∩ (univ \ B)).card = 0 := by
    rw [Finset.card_eq_zero]; ext x; simp [B]
  -- π' agrees with π on the arrival rows
  have hagree : (span K {v | v ∈ arrRows Pub evs}).map π = (span K {v | v ∈ arrRows Pub evs}).map π' := by
    rw [Submodule.map_span, Submodule.map_span]
    congr 1
    ext w; constructor
    · rintro ⟨v, hv, rfl⟩
      refine ⟨v, hv, ?_⟩
      have : killB B v = v := by
        funext i; by_cases hi : i ∈ B
        · simp [killB, hi, hArr v hv i hi]
        · simp [killB, hi]
      simp [π', this]
    · rintro ⟨v, hv, rfl⟩
      refine ⟨v, hv, ?_⟩
      have : killB B v = v := by
        funext i; by_cases hi : i ∈ B
        · simp [killB, hi, hArr v hv i hi]
        · simp [killB, hi]
      simp [π', this]
  have hle : aS π Pub evs ≤ finrank K ((span K (held start evs)).map π') := by
    unfold aS; rw [hagree]
    exact Submodule.finrank_mono (Submodule.map_mono
      (Submodule.span_mono fun v hv => arr_held Pub start evs v hv))
  rw [← hB] at hT
  have hx' : (B ∩ (univ \ B)).card = 0 := by simp
  omega

/-! ## Scope: the card form is false without `hArr` -/

/-- **D1 card form FALSE without hArr.** Chart c, three registers over ℚ: x = 0 (public, S register,
born at c), h = 1 (public helper), owned 2 unused. x is born; h arrives with row e_h + e_x (the x
coordinate brought down by an owned descent elsewhere); h -= x; x departs. h ends as its token.
a_S = dim π_S(e_h + e_x) = 1, but d = 0 (no ARRIVED register departs), e_S = 0 (π_S(e_h) = 0),
oa = 0. Every hypothesis of `D1` except `hArr` holds. -/
theorem D1_false :
    let π : (Fin 3 → ℚ) →ₗ[ℚ] (Fin 3 → ℚ) := LinearMap.single ℚ (fun _ => ℚ) 0 ∘ₗ LinearMap.proj 0
    let Pub : Finset (Fin 3) := {0, 1}
    let evs : List (Ev ℚ (Fin 3)) :=
      [.born 0, .arrive 1 (Pi.single 1 1 + Pi.single 0 1), .add 1 0 (-1), .depart 0]
    Legal start evs ∧
    (∀ h ∈ Pub, h ∈ (run start evs).pres → π ((run start evs).row h) = 0 →
      (run start evs).row h = Pi.single h 1) ∧
    (∀ h ∈ Pub, h ∈ (run start evs).pres → h ∈ bornSet evs → (run start evs).row h = Pi.single h 1) ∧
    (∀ i ∈ Pub, nEnt {i} evs ≤ 1) ∧
    aS π Pub evs = 1 ∧
    ((Pub \ bornSet evs).filter fun i => 0 < nDep {i} evs).card = 0 ∧
    ((((run start evs).pres ∩ Pub) \ bornSet evs).filter (fun h => π ((run start evs).row h) ≠ 0)).card = 0 ∧
    nEnt (univ \ Pub) evs = 0 := by
  intro π Pub evs
  have hrun : run start evs = ⟨Function.update (Function.update (fun _ => 0) 0 (Pi.single 0 1)) 1
      (Pi.single 1 1 + Pi.single 0 1 + (-1 : ℚ) • Pi.single 0 1), {1}⟩ := by
    simp only [evs, run, step, start]
    congr 1
    funext r; fin_cases r <;> simp [Function.update]
  have hpres : (run start evs).pres = {1} := by rw [hrun]
  have hrow1 : (run start evs).row 1 = Pi.single 1 1 := by
    rw [hrun]; simp
  have hborn : bornSet evs = {0} := by simp [evs, bornSet]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · simp [evs, Legal, LegalEv, step, start]
  · intro h hP hF _
    rw [hpres] at hF; rw [Finset.mem_singleton] at hF; subst hF; exact hrow1
  · intro h hP hF hb
    rw [hpres] at hF; rw [hborn] at hb
    rw [Finset.mem_singleton] at hF hb; subst hF; exact absurd hb (by decide)
  · intro i hi; fin_cases i <;> simp [evs, nEnt]
  · have hA : arrRows Pub evs = [Pi.single 1 1 + Pi.single 0 1] := by
      simp [evs, arrRows, Pub]
    unfold aS; rw [hA]
    have hset : {v : Fin 3 → ℚ | v ∈ [Pi.single 1 1 + Pi.single 0 1]} = {Pi.single 1 1 + Pi.single 0 1} := by
      ext v; simp
    rw [hset, Submodule.map_span, Set.image_singleton]
    have hv : π (Pi.single 1 1 + Pi.single 0 1) ≠ 0 := by
      intro h
      have := congrFun h 0
      simp [π] at this
    exact finrank_span_singleton hv
  · rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
    intro i hi
    rw [hborn] at hi
    have : i = 1 := by
      have := (Finset.mem_sdiff.mp hi)
      fin_cases i <;> simp_all [Pub]
    subst this
    simp [evs, nDep]
  · rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
    intro i hi
    rw [hpres] at hi
    have : i = 1 := by
      have := Finset.mem_inter.mp (Finset.mem_sdiff.mp hi).1
      simpa using this.1
    subst this
    rw [hrow1]; simp [π]
  · simp [evs, nEnt, Pub]

end DepartD1
