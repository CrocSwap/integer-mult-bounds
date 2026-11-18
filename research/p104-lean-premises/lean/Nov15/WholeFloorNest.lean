/-
WholeFloorNest : the NESTING rule of the verifier added to the WHOLEFLOOR model, and
the unconditional-in-lat versions of R3's floor.
LAT.md (internal notes) settled from primary sources that lateral MOVEs are ILLEGAL:
  local.py:66  need(frames[b] < frames[a] if private else frames[a] < frames[b], 'Nested chronological transport')
  (frames are frozensets, `<` is PROPER subset), owned-ascent relaxation = `or frames[a] < frames[b]`
  (pr6902-OWNED-ASCENT.md), SPEC 03-motifs.tex "On every edge one label will contain the other",
  local.py:67 paid[abs(len(frames[b]) - len(frames[a]))] += 1.
Here: `Geo` = chart dims + proper nesting; `StepL`/`RunL` = WholeFloorModel.Step with the guard (public MOVE: c < d AND
c nested in d; owned MOVE: nested either way) and a log of the owned MOVE chart pairs; `nest_lat_zero`; then
`d0_whole_floor_nested` and `kappa_whole_floor_nested`.
-/
import Nov15.WholeFloorModel
import Nov15.WholeFloorEnd
import Nov15.WholeFloorCover

set_option linter.unusedSectionVars false

namespace WholeFloorNest
open WholeFloor Finset

/-- chart geometry: dimension and PROPER nesting (`sub a b` = frames[a] < frames[b], a proper subset). -/
structure Geo (C : Type*) where
  dim : C → ℕ
  sub : C → C → Prop
  sub_dim : ∀ {a b}, sub a b → dim a < dim b

variable {K Reg C : Type*}

/-- paid rank of a MOVE a -> b (local.py:67, pricekit rk): |dim b - dim a|. -/
def rank (G : Geo C) (a b : C) : ℕ := Int.natAbs ((G.dim b : ℤ) - G.dim a)

/-- the verifier's nesting rule for an OWNED MOVE (A6 relaxation: either direction, never sideways). -/
def NestOwn (G : Geo C) (a b : C) : Prop := G.sub a b ∨ G.sub b a

/-- number of lateral (rank 0) MOVEs in a log. -/
def latCount (G : Geo C) (ms : List (C × C)) : ℕ := (ms.filter fun m => rank G m.1 m.2 = 0).length

/-- a legal MOVE changes the dimension, so its paid rank is >= 1. -/
theorem nest_rank_pos (G : Geo C) {a b : C} (h : NestOwn G a b) : 1 ≤ rank G a b := by
  unfold rank
  rcases h with h | h <;> have := G.sub_dim h <;> omega

/-- **nest_lat_zero**: under the nesting rule there is no lateral MOVE: lat = 0. -/
theorem nest_lat_zero (G : Geo C) (ms : List (C × C)) (h : ∀ m ∈ ms, NestOwn G m.1 m.2) :
    latCount G ms = 0 := by
  unfold latCount
  rw [List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro m hm
  have := nest_rank_pos G (h m hm)
  simp; omega

section Model
variable [Field K] [Fintype Reg] [DecidableEq Reg] [DecidableEq C] [PartialOrder C] (pub : Reg → Prop)

open Classical in
/-- WholeFloorModel.Step with the NESTING guard; the label is the chart pair of an owned MOVE. -/
inductive StepL (G : Geo C) : St K Reg C → Option (C × C) → St K Reg C → Prop
  | birthPub (s : St K Reg C) (r : Reg) (c : C) : s.loc r = .unborn → pub r →
      StepL G s Option.none
        { s with loc := Function.update s.loc r (.sit c),
                      row := Function.update s.row r (Pi.single r 1),
                      B := Function.update s.B c (insert r (s.B c)) }
  | birthOwn (s : St K Reg C) (r : Reg) (c : C) : s.loc r = .unborn → ¬ pub r →
      StepL G s Option.none
        { s with loc := Function.update s.loc r (.sit c),
                      row := Function.update s.row r 0 }
  | gate (s : St K Reg C) (r : Reg) (c : C) (coef : Reg → K) : s.loc r = .sit c →
      StepL G s Option.none
        { s with row := Function.update s.row r (∑ t ∈ Finset.univ.filter (fun t => s.loc t = .sit c), coef t • s.row t) }
  | movePub (s : St K Reg C) (r : Reg) (c d : C) : s.loc r = .sit c → pub r → c < d → G.sub c d →
      StepL G s Option.none
        { s with loc := Function.update s.loc r (.sit d),
                      A := Function.update s.A d (insert r (s.A d)),
                      eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c' }
  | moveOwn (s : St K Reg C) (r : Reg) (c d : C) : s.loc r = .sit c → ¬ pub r → NestOwn G c d →
      StepL G s (Option.some (c, d))
        { s with loc := Function.update s.loc r (.sit d),
                      O := Function.update s.O d (s.row r :: s.O d) }
  | clearOwn (s : St K Reg C) (r : Reg) (c : C) : s.loc r = .sit c → ¬ pub r →
      StepL G s Option.none
        { s with loc := Function.update s.loc r .cleared,
                      row := Function.update s.row r 0 }

/-- every nested step is a model step. -/
theorem StepL.toStep {G : Geo C} {s s' : St K Reg C} {o : Option (C × C)} (h : StepL pub G s o s') :
    Step pub s s' := by
  cases h with
  | birthPub r c h1 h2 => exact Step.birthPub s r c h1 h2
  | birthOwn r c h1 h2 => exact Step.birthOwn s r c h1 h2
  | gate r c coef h1 => exact Step.gate s r c coef h1
  | movePub r c d h1 h2 h3 _ => exact Step.movePub s r c d h1 h2 h3
  | moveOwn r c d h1 h2 _ => exact Step.moveOwn s r c d h1 h2
  | clearOwn r c h1 h2 => exact Step.clearOwn s r c h1 h2

/-- a run with the log of its owned MOVE chart pairs. -/
inductive RunL (G : Geo C) : St K Reg C → List (C × C) → St K Reg C → Prop
  | refl (s : St K Reg C) : RunL G s [] s
  | none {s s' s'' : St K Reg C} {l : List (C × C)} : StepL pub G s none s' → RunL G s' l s'' → RunL G s l s''
  | some {s s' s'' : St K Reg C} {l : List (C × C)} (m : C × C) :
      StepL pub G s (some m) s' → RunL G s' l s'' → RunL G s (m :: l) s''

theorem RunL.toRun {G : Geo C} {s s' : St K Reg C} {l : List (C × C)} (h : RunL pub G s l s') :
    Relation.ReflTransGen (Step pub) s s' := by
  induction h with
  | refl => exact Relation.ReflTransGen.refl
  | none h _ ih => exact Relation.ReflTransGen.head h.toStep ih
  | some m h _ ih => exact Relation.ReflTransGen.head h.toStep ih

/-- every owned MOVE in the log of a nested run is nested. -/
theorem RunL.nested {G : Geo C} {s s' : St K Reg C} {l : List (C × C)} (h : RunL pub G s l s') :
    ∀ m ∈ l, NestOwn G m.1 m.2 := by
  induction h with
  | refl => simp
  | none _ _ ih => exact ih
  | some m h _ ih =>
    intro x hx
    rcases List.mem_cons.mp hx with rfl | hx
    · cases h with | moveOwn r c d _ _ hn => exact hn
    · exact ih x hx

/-- a nested run from `init` is reachable, so `reach_inv`, `cs_final` etc. apply, and its lateral count is 0. -/
theorem runL_reach_lat {G : Geo C} {s : St K Reg C} {l : List (C × C)} (h : RunL pub G init l s) :
    Reach pub s ∧ latCount G l = 0 :=
  ⟨h.toRun, nest_lat_zero G l (h.nested pub)⟩

end Model

/-! ### the floors, unconditional in lat -/

open WholeFloorPrice WholeFloorEnd CallerCost JointCeiling

/-- the pricing summary `w` is that of a nested run: its lateral count is the number of rank-0 owned MOVEs of
the log, and all owned MOVEs of the log are nested (the verifier rule). -/
structure NestedWord {C : Type*} (G : Geo C) (w : Word) (log : List (C × C)) : Prop where
  lat_def : w.lat = latCount G log
  nested : ∀ m ∈ log, NestOwn G m.1 m.2

theorem NestedWord.lat_zero {C : Type*} {G : Geo C} {w : Word} {log : List (C × C)}
    (h : NestedWord G w log) : w.lat = 0 := by
  rw [h.lat_def]; exact nest_lat_zero G log h.nested

/-- **R3's all-words D0 floor, nested words**: every priced word obeying the nesting rule has the 17-call invoice
D0 >= 155,730.9 (R3: 155,730.99). No lat hypothesis: lat = 0 is a consequence. -/
theorem d0_whole_floor_nested {C : Type*} (G : Geo C) (w : Word) (hP : Priced w) (log : List (C × C))
    (hw : NestedWord G w log) (n : Inv) (hn : Dinv n = w.hD0 + w.mD0 + w.oD0) :
    (155730.9 : ℝ) ≤ Dinv (invoice (caller 6 7) n 17) :=
  d0_whole_floor w hP hw.lat_zero n hn

/-- the native floor `F <= -Nfl` (JointCeiling's hN), DERIVED for nested words. -/
theorem hN_nested {C : Type*} (G : Geo C) (w : Word) (hP : Priced w) (log : List (C × C))
    (hw : NestedWord G w log) (n : Inv)
    (hF : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - (2 - (2 : ℝ) ^ s) * ((w.sH + w.sM : ℕ) : ℝ)
        - (w.ow.length : ℕ)) :
    ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s := by
  intro s h0 h1
  have h := F_floor s h0 h1 (w.sH + w.sM) w.ow.length w.lat (Finv s n) (hF s h0 h1) hP.h_m16
    (by have := hP.h_Y; omega)
  rwa [hw.lat_zero, NflL_zero] at h

/-- **kappa <= .0204110965 for nested words, NO numeric hypothesis** (R3 §3). The interval cover (F < 0 on [t0, 1] for the
floor-native invoice of the #7113 caller C(8|9), 17 calls) is `WholeFloorCover.cover`, kernel-checked with NumCertK
. t0 = .0204110965 is R3's .0204110964 rounded UP in the 10th digit: the exact root is
.02041109645 (F at s = .9795889036 is +6.7e-6), so the 10-digit .0204110964 itself is 5e-11 below the root.
Remaining hypotheses: `Priced w` (includes h_Y and the named upstream pricing facts) and the F-currency pricing `hF`. -/
theorem kappa_whole_floor_nested {C : Type*} (G : Geo C) (w : Word) (hP : Priced w) (log : List (C × C))
    (hw : NestedWord G w log) (n : Inv)
    (hF : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - (2 - (2 : ℝ) ^ s) * ((w.sH + w.sM : ℕ) : ℝ)
        - (w.ow.length : ℕ)) :
    ∀ t : ℝ, (204110965 : ℝ) / 10 ^ 10 ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  intro t ht ht1
  have hN := hN_nested G w hP log hw n hF
  have hs0 : (0 : ℝ) ≤ 1 - t := by linarith
  have hs1 : 1 - t ≤ 1 := by
    have : (0 : ℝ) ≤ (204110965 : ℝ) / 10 ^ 10 := by norm_num
    linarith
  have h1 := hN _ hs0 hs1
  have h2 := invoice_F (1 - t) (caller 6 7) n 17
  have h3 := invoice_F (1 - t) (caller 6 7) natFloor 17
  have h4 := natFloor_F (1 - t)
  have h5 := WholeFloorCover.cover t ht ht1
  push_cast at h2 h3
  nlinarith

end WholeFloorNest

#print axioms WholeFloorNest.nest_lat_zero
#print axioms WholeFloorNest.StepL.toStep
#print axioms WholeFloorNest.runL_reach_lat
#print axioms WholeFloorNest.d0_whole_floor_nested
#print axioms WholeFloorNest.hN_nested
#print axioms WholeFloorNest.kappa_whole_floor_nested
