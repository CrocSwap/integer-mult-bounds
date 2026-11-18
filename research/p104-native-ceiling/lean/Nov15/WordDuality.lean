/-
WordDuality .  See WordDuality.md.  Source: internal notes

D = sigma . perp . time-reversal . transpose.
Model: charts `C` with an involution `perp` (dim (perp c) = N - dim c, perp z = V), registers `Reg`, a word = initial chart of every
register + a list of events (MOVE a->b, ADD, SCALE, COPY, INIT, CLEAR).  Legality = co-presence + hub rules (no MOVE leaves V,
none enters z) + a move relation R (ascent / owned descent) closed under (a,b) -> (perp b, perp a).
 Part 1  legal words go to legal words, boundaries swap (`dual_run`).
 Part 2  matrices (ADD / SCALE / MOVE): M(D l) = sigma-relabel of (M l)^T (`Mrec_dual`).
 Part 3  invoice: helper (b,e,steps) -> (N-e, N-b, reversed swapped steps); Theorem K invoice (FibreK) unchanged (`dualH_invoice`).
 Part 4  P104 boundary data under sigma: X_p, Y_p exchange (`selfdual_boundary`); 2x2 contract blocks (`hosted_block`, `nonhosted_block`).
 Part 5  caveat: COPY does not dualise to an ADD at matrix level (`copy_not_add`).
Kernel only.
-/
import Nov15.FibreK
import Mathlib.Data.Matrix.Basis
import Mathlib.Data.Matrix.Mul

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace WordDuality
open FibreK CallerCost Matrix

structure Charts (C : Type*) (N : ℕ) where
  perp : C → C
  perp_perp : ∀ c, perp (perp c) = c
  dim : C → ℕ
  dim_le : ∀ c, dim c ≤ N
  dim_perp : ∀ c, dim (perp c) = N - dim c
  z : C
  V : C
  perp_z : perp z = V

namespace Charts
variable {C : Type*} {N : ℕ} (X : Charts C N)
theorem perp_V : X.perp X.V = X.z := by rw [← X.perp_z, X.perp_perp]
theorem ne_V_perp {a : C} (h : a ≠ X.V) : X.perp a ≠ X.z := by
  intro h'; apply h; rw [← X.perp_perp a, h', X.perp_z]
theorem ne_z_perp {b : C} (h : b ≠ X.z) : X.perp b ≠ X.V := by
  intro h'; apply h; rw [← X.perp_perp b, h', X.perp_V]
end Charts

inductive Ev (K Reg C : Type*)
  | move (i : Reg) (a b : C)
  | add (i j : Reg) (q : K) (c : C)
  | scale (i : Reg) (u : K) (c : C)
  | copy (i j : Reg) (c : C)
  | init (i : Reg) (c : C)
  | clear (i : Reg) (c : C)

variable {K Reg C : Type*} {N : ℕ}

section Words
variable [DecidableEq Reg]

def stepL (ℓ : Reg → C) : Ev K Reg C → (Reg → C)
  | .move i _ b => Function.update ℓ i b
  | _ => ℓ

def runL (ℓ : Reg → C) : List (Ev K Reg C) → (Reg → C)
  | [] => ℓ
  | e :: es => runL (stepL ℓ e) es

theorem runL_append (ℓ : Reg → C) (l1 l2 : List (Ev K Reg C)) :
    runL ℓ (l1 ++ l2) = runL (runL ℓ l1) l2 := by
  induction l1 generalizing ℓ with
  | nil => rfl
  | cons e es ih => simp [runL, ih]

def LegalEv (X : Charts C N) (R : C → C → Prop) (ℓ : Reg → C) : Ev K Reg C → Prop
  | .move i a b => ℓ i = a ∧ a ≠ X.V ∧ b ≠ X.z ∧ R a b
  | .add i j _ c => i ≠ j ∧ ℓ i = c ∧ ℓ j = c
  | .scale i _ c => ℓ i = c
  | .copy i j c => i ≠ j ∧ ℓ i = c ∧ ℓ j = c
  | .init i c => ℓ i = c
  | .clear i c => ℓ i = c

def LegalL (X : Charts C N) (R : C → C → Prop) : (Reg → C) → List (Ev K Reg C) → Prop
  | _, [] => True
  | ℓ, e :: es => LegalEv X R ℓ e ∧ LegalL X R (stepL ℓ e) es

theorem LegalL_append (X : Charts C N) (R : C → C → Prop) (ℓ : Reg → C) (l1 l2 : List (Ev K Reg C)) :
    LegalL X R ℓ (l1 ++ l2) ↔ LegalL X R ℓ l1 ∧ LegalL X R (runL ℓ l1) l2 := by
  induction l1 generalizing ℓ with
  | nil => simp [LegalL, runL]
  | cons e es ih => simp [LegalL, runL, ih, and_assoc]

variable [One K]

/-- the dual of one event. COPY becomes ADD (valid on a clean target only; see `copy_not_add`). -/
def dualEv (X : Charts C N) (σ : Reg ≃ Reg) : Ev K Reg C → Ev K Reg C
  | .move i a b => .move (σ i) (X.perp b) (X.perp a)
  | .add i j q c => .add (σ j) (σ i) q (X.perp c)
  | .scale i u c => .scale (σ i) u (X.perp c)
  | .copy i j c => .add (σ j) (σ i) 1 (X.perp c)
  | .init i c => .clear (σ i) (X.perp c)
  | .clear i c => .init (σ i) (X.perp c)

/-- time reversal of the dualised events. -/
def dualList (X : Charts C N) (σ : Reg ≃ Reg) (l : List (Ev K Reg C)) : List (Ev K Reg C) :=
  (l.map (dualEv X σ)).reverse

theorem dualList_cons (X : Charts C N) (σ : Reg ≃ Reg) (e : Ev K Reg C) (l : List (Ev K Reg C)) :
    dualList X σ (e :: l) = dualList X σ l ++ [dualEv X σ e] := by
  simp [dualList]

/-- PART 1.  A legal word dualises to a legal word; the dual starts at perp of the final charts and ends at perp of the initial
charts (births and ends exchange). -/
theorem dual_run (X : Charts C N) (R : C → C → Prop) (hR : ∀ a b, R a b → R (X.perp b) (X.perp a))
    (σ : Reg ≃ Reg) :
    ∀ (l : List (Ev K Reg C)) (ℓ : Reg → C), LegalL X R ℓ l →
      runL (fun r => X.perp (runL ℓ l (σ.symm r))) (dualList X σ l) = (fun r => X.perp (ℓ (σ.symm r))) ∧
      LegalL X R (fun r => X.perp (runL ℓ l (σ.symm r))) (dualList X σ l) := by
  intro l
  induction l with
  | nil => intro ℓ _; exact ⟨rfl, trivial⟩
  | cons e es ih =>
    intro ℓ h
    obtain ⟨he, hes⟩ := h
    obtain ⟨A, B⟩ := ih (stepL ℓ e) hes
    have hS : (fun r => X.perp (runL ℓ (e :: es) (σ.symm r))) =
        (fun r => X.perp (runL (stepL ℓ e) es (σ.symm r))) := rfl
    rw [hS, dualList_cons, runL_append, LegalL_append, A]
    -- the last event
    cases e with
    | move i a b =>
      obtain ⟨h1, h2, h3, h4⟩ := he
      subst h1
      refine ⟨?_, B, ?_⟩
      · simp only [runL, dualEv, stepL]
        funext r
        by_cases hr : r = σ i
        · subst hr; simp
        · have : σ.symm r ≠ i := by
            intro h; apply hr; rw [← h]; simp
          simp [Function.update_of_ne hr, Function.update_of_ne this]
      · exact ⟨⟨by simp [stepL], X.ne_z_perp h3, X.ne_V_perp h2, hR _ _ h4⟩, trivial⟩
    | add i j q c =>
      obtain ⟨h1, h2, h3⟩ := he
      refine ⟨?_, B, ?_⟩
      · simp [runL, dualEv, stepL]
      · simp [LegalL, LegalEv, runL, dualEv, stepL, A, h2, h3]
        exact fun h => h1 h.symm
    | scale i u c =>
      refine ⟨?_, B, ?_⟩
      · simp [runL, dualEv, stepL]
      · simp [LegalL, LegalEv, runL, dualEv, stepL, A]; simp [LegalEv] at he; simp [he]
    | copy i j c =>
      obtain ⟨h1, h2, h3⟩ := he
      refine ⟨?_, B, ?_⟩
      · simp [runL, dualEv, stepL]
      · simp [LegalL, LegalEv, runL, dualEv, stepL, A, h2, h3]
        exact fun h => h1 h.symm
    | init i c =>
      refine ⟨?_, B, ?_⟩
      · simp [runL, dualEv, stepL]
      · simp [LegalL, LegalEv, runL, dualEv, stepL, A]; simp [LegalEv] at he; simp [he]
    | clear i c =>
      refine ⟨?_, B, ?_⟩
      · simp [runL, dualEv, stepL]
      · simp [LegalL, LegalEv, runL, dualEv, stepL, A]; simp [LegalEv] at he; simp [he]

/-- ascent and descent both survive: (a,b) ascending (dim a ≤ dim b) gives (perp b, perp a) ascending. -/
theorem ascent_dual (X : Charts C N) : ∀ a b, X.dim a ≤ X.dim b → X.dim (X.perp b) ≤ X.dim (X.perp a) := by
  intro a b h; rw [X.dim_perp, X.dim_perp]; have := X.dim_le a; have := X.dim_le b; omega

theorem descent_dual (X : Charts C N) : ∀ a b, X.dim b ≤ X.dim a → X.dim (X.perp b) ≥ X.dim (X.perp a) := by
  intro a b h; rw [X.dim_perp, X.dim_perp]; have := X.dim_le a; have := X.dim_le b; omega

/-! ### words, boundaries -/

structure Word (K Reg C : Type*) where
  init0 : Reg → C
  evs : List (Ev K Reg C)

def Word.fin (w : Word K Reg C) : Reg → C := runL w.init0 w.evs

def dualWord (X : Charts C N) (σ : Reg ≃ Reg) (w : Word K Reg C) : Word K Reg C :=
  ⟨fun r => X.perp (w.fin (σ.symm r)), dualList X σ w.evs⟩

theorem dual_legal (X : Charts C N) (R : C → C → Prop) (hR : ∀ a b, R a b → R (X.perp b) (X.perp a))
    (σ : Reg ≃ Reg) (w : Word K Reg C) (h : LegalL X R w.init0 w.evs) :
    LegalL X R (dualWord X σ w).init0 (dualWord X σ w).evs := (dual_run X R hR σ w.evs w.init0 h).2

/-- births of the dual are perp of the ends; ends of the dual are perp of the births. -/
theorem dual_boundary (X : Charts C N) (R : C → C → Prop) (hR : ∀ a b, R a b → R (X.perp b) (X.perp a))
    (σ : Reg ≃ Reg) (w : Word K Reg C) (h : LegalL X R w.init0 w.evs) (r : Reg) :
    (dualWord X σ w).init0 (σ r) = X.perp (w.fin r) ∧ (dualWord X σ w).fin (σ r) = X.perp (w.init0 r) := by
  constructor
  · simp [dualWord]
  · have := congrFun (dual_run X R hR σ w.evs w.init0 h).1 (σ r)
    simpa [Word.fin, dualWord] using this

theorem dual_dim_boundary (X : Charts C N) (R : C → C → Prop) (hR : ∀ a b, R a b → R (X.perp b) (X.perp a))
    (σ : Reg ≃ Reg) (w : Word K Reg C) (h : LegalL X R w.init0 w.evs) (r : Reg) :
    X.dim ((dualWord X σ w).init0 (σ r)) = N - X.dim (w.fin r) ∧
    X.dim ((dualWord X σ w).fin (σ r)) = N - X.dim (w.init0 r) := by
  obtain ⟨a, b⟩ := dual_boundary X R hR σ w h r
  rw [a, b, X.dim_perp, X.dim_perp]; exact ⟨rfl, rfl⟩

end Words

/-! ### Part 2: matrices -/
section Mat
variable [Fintype Reg] [DecidableEq Reg] [CommRing K]

def evMat : Ev K Reg C → Matrix Reg Reg K
  | .add i j q _ => 1 + Matrix.single i j q
  | .scale i u _ => Matrix.diagonal (Function.update (1 : Reg → K) i u)
  | _ => 1

/-- events with a matrix semantics (MOVE only changes location). -/
def Lin : Ev K Reg C → Prop
  | .move .. => True
  | .add .. => True
  | .scale .. => True
  | _ => False

/-- total matrix of a word in initial-row coordinates: later events multiply on the left. -/
def Mrec : List (Ev K Reg C) → Matrix Reg Reg K
  | [] => 1
  | e :: es => Mrec es * evMat e

theorem Mrec_append (l1 l2 : List (Ev K Reg C)) : Mrec (l1 ++ l2) = Mrec l2 * Mrec l1 := by
  induction l1 with
  | nil => simp [Mrec]
  | cons e es ih => simp [Mrec, ih, Matrix.mul_assoc]

theorem evMat_dual (X : Charts C N) (σ : Reg ≃ Reg) (e : Ev K Reg C) (he : Lin e) :
    evMat (dualEv X σ e) = (evMat e)ᵀ.submatrix σ.symm σ.symm := by
  cases e with
  | move i a b => simp [evMat, dualEv]
  | add i j q c =>
    ext a b
    simp [evMat, dualEv, Matrix.single_apply, Matrix.one_apply, Matrix.transpose_apply, Matrix.submatrix_apply, Equiv.eq_symm_apply]
  | scale i u c =>
    ext a b
    simp [evMat, dualEv, Matrix.diagonal_apply, Function.update_apply, Equiv.symm_apply_eq]
  | copy _ _ _ => exact absurd he (by simp [Lin])
  | init _ _ => exact absurd he (by simp [Lin])
  | clear _ _ => exact absurd he (by simp [Lin])

/-- PART 2.  M(D l) is the sigma-relabel of the transpose of M(l). -/
theorem Mrec_dual (X : Charts C N) (σ : Reg ≃ Reg) :
    ∀ l : List (Ev K Reg C), (∀ e ∈ l, Lin e) → Mrec (dualList X σ l) = (Mrec l)ᵀ.submatrix σ.symm σ.symm := by
  intro l
  induction l with
  | nil => intro _; simp [dualList, Mrec]
  | cons e es ih =>
    intro h
    have he := h e (by simp)
    have hes := ih (fun x hx => h x (by simp [hx]))
    rw [dualList_cons, Mrec_append, hes]
    simp only [Mrec, Matrix.one_mul, Matrix.transpose_mul]
    rw [evMat_dual X σ e he, Matrix.submatrix_mul_equiv]

end Mat

/-! ### Part 3: the Theorem-K invoice is unchanged -/
section Invoice
variable [DecidableEq Reg]

/-- the MOVE steps (source dim, target dim) of register `r`. -/
def regSteps (X : Charts C N) (r : Reg) (l : List (Ev K Reg C)) : List (ℕ × ℕ) :=
  l.filterMap fun e => match e with
    | .move i a b => if i = r then some (X.dim a, X.dim b) else none
    | _ => none

def swapN (N : ℕ) (s : ℕ × ℕ) : ℕ × ℕ := (N - s.2, N - s.1)

/-- register `r` as a FibreK helper: birth dim, end dim, steps. -/
def helperOf (X : Charts C N) (w : Word K Reg C) (r : Reg) : Helper :=
  ⟨X.dim (w.init0 r), X.dim (w.fin r), regSteps X r w.evs⟩

/-- a helper b -> e becomes (N-e) -> (N-b), with reversed swapped steps. -/
def dualH (N : ℕ) (h : Helper) : Helper := ⟨N - h.e, N - h.b, (h.steps.map (swapN N)).reverse⟩

variable [One K]

theorem regSteps_dual (X : Charts C N) (σ : Reg ≃ Reg) (r : Reg) :
    ∀ l : List (Ev K Reg C), regSteps X (σ r) (dualList X σ l) = ((regSteps X r l).map (swapN N)).reverse := by
  intro l
  induction l with
  | nil => simp [dualList, regSteps]
  | cons e es ih =>
    rw [dualList_cons]
    have : regSteps X (σ r) (dualList X σ es ++ [dualEv X σ e]) =
        regSteps X (σ r) (dualList X σ es) ++ regSteps X (σ r) [dualEv X σ e] := by
      simp [regSteps, List.filterMap_append]
    rw [this, ih]
    cases e with
    | move i a b =>
      by_cases h : i = r
      · subst h; simp [regSteps, dualEv, swapN, X.dim_perp]
      · simp [regSteps, dualEv, h]
    | add i j q c => simp [regSteps, dualEv]
    | scale i u c => simp [regSteps, dualEv]
    | copy i j c => simp [regSteps, dualEv]
    | init i c => simp [regSteps, dualEv]
    | clear i c => simp [regSteps, dualEv]

/-- PART 3a.  The dual word's register `sigma r` is the dual helper of `r` (b,e) -> (N-e, N-b). -/
theorem helperOf_dual (X : Charts C N) (R : C → C → Prop) (hR : ∀ a b, R a b → R (X.perp b) (X.perp a))
    (σ : Reg ≃ Reg) (w : Word K Reg C) (h : LegalL X R w.init0 w.evs) (r : Reg) :
    helperOf X (dualWord X σ w) (σ r) = dualH N (helperOf X w r) := by
  obtain ⟨b1, b2⟩ := dual_dim_boundary X R hR σ w h r
  simp only [helperOf, dualH, dualWord, b1, b2]
  simp only [dualWord] at b1 b2
  rw [b1, b2]
  simp [regSteps_dual X σ r]

theorem gap_swapN (N : ℕ) (s : ℕ × ℕ) (h1 : s.1 ≤ N) (h2 : s.2 ≤ N) : gap (swapN N s) = gap s := by
  simp only [gap, swapN]; omega

/-- PART 3b.  Dualising a helper list leaves FibreK's invoice (Theorem K) unchanged:
births/ends (b,e) -> (N-e,N-b) keep the climb, every MOVE keeps its |Δdim|. -/
theorem dualH_invoice (E : Inv) (tb : Table) (H : List Helper)
    (hN : ∀ h ∈ H, h.b ≤ h.e ∧ h.e ≤ N ∧ ∀ s ∈ h.steps, s.1 ≤ N ∧ s.2 ≤ N) (t : ℝ) :
    Fi (nativeInv E tb (H.map (dualH N))) t = Fi (nativeInv E tb H) t := by
  rw [K_word, K_word]
  unfold FK
  have hP : PiW (H.map (dualH N)) = PiW H := by
    unfold PiW
    congr 1
    rw [List.map_map]
    apply List.map_congr_left
    intro h hh
    obtain ⟨a, b, _⟩ := hN h hh
    simp only [Function.comp, dualH]; omega
  have hS : (((Ssum (H.map (dualH N))).map fun s => Fh (tb.tP (gap s)) t).sum) =
      ((Ssum H).map fun s => Fh (tb.tP (gap s)) t).sum := by
    simp only [Ssum, Multiset.map_coe, Multiset.sum_coe]
    rw [sum_flatMap_map, sum_flatMap_map, List.map_map]
    congr 1
    apply List.map_congr_left
    intro h hh
    obtain ⟨_, _, c⟩ := hN h hh
    simp only [Function.comp, dualH, List.map_reverse, List.sum_reverse, List.map_map]
    congr 1
    apply List.map_congr_left
    intro s hs
    obtain ⟨c1, c2⟩ := c s hs
    simp only [Function.comp, gap_swapN N s c1 c2]
  rw [hP, hS]

theorem dualH_root (c E : Inv) (tb : Table) (H : List Helper) (L : ℕ)
    (hN : ∀ h ∈ H, h.b ≤ h.e ∧ h.e ≤ N ∧ ∀ s ∈ h.steps, s.1 ≤ N ∧ s.2 ≤ N) (κ : ℝ) :
    IsRoot (Fi (invoice c (nativeInv E tb (H.map (dualH N))) L)) κ ↔
      IsRoot (Fi (invoice c (nativeInv E tb H) L)) κ := by
  unfold IsRoot
  rw [Fi_invoice, Fi_invoice, dualH_invoice E tb H hN κ]

/-- PART 3c, word level: the helpers of `D w` (registers `sigma r`) have the same invoice as those of `w`.
Hypothesis: the listed registers climb (birth dim <= end dim), as helpers do. -/
theorem word_invoice (X : Charts C N) (R : C → C → Prop) (hR : ∀ a b, R a b → R (X.perp b) (X.perp a))
    (σ : Reg ≃ Reg) (w : Word K Reg C) (h : LegalL X R w.init0 w.evs) (rs : List Reg)
    (hc : ∀ r ∈ rs, X.dim (w.init0 r) ≤ X.dim (w.fin r)) (E : Inv) (tb : Table) (t : ℝ) :
    Fi (nativeInv E tb ((rs.map σ).map (helperOf X (dualWord X σ w)))) t =
      Fi (nativeInv E tb (rs.map (helperOf X w))) t := by
  have : (rs.map σ).map (helperOf X (dualWord X σ w)) = (rs.map (helperOf X w)).map (dualH N) := by
    rw [List.map_map, List.map_map]
    apply List.map_congr_left
    intro r _
    exact helperOf_dual X R hR σ w h r
  rw [this]
  apply dualH_invoice
  intro h' hh'
  obtain ⟨r, hr, rfl⟩ := List.mem_map.mp hh'
  refine ⟨hc r hr, X.dim_le _, ?_⟩
  intro s hs
  simp only [helperOf, regSteps, List.mem_filterMap] at hs
  obtain ⟨e, _, he⟩ := hs
  cases e <;> simp at he
  obtain ⟨_, rfl⟩ := he
  exact ⟨X.dim_le _, X.dim_le _⟩

end Invoice

/-! ### Part 4: P104 boundary data -/
section P104
variable [DecidableEq Reg] [One K] {ι : Type*}

/-- hypotheses (from DU1 section 1): X_p runs <p> -> V, Y_p runs {0} -> p^perp, sigma swaps X_p, Y_p, perp <p> = p^perp.
The dual word has the same register boundaries (g = id): the problem is self-dual. -/
theorem selfdual_boundary (X : Charts C N) (R : C → C → Prop) (hR : ∀ a b, R a b → R (X.perp b) (X.perp a))
    (σ : Reg ≃ Reg) (w : Word K Reg C) (h : LegalL X R w.init0 w.evs)
    (Xr Yr : ι → Reg) (line hyp : ι → C)
    (hσX : ∀ p, σ (Xr p) = Yr p) (hσY : ∀ p, σ (Yr p) = Xr p) (hperp : ∀ p, X.perp (line p) = hyp p)
    (hX : ∀ p, w.init0 (Xr p) = line p ∧ w.fin (Xr p) = X.V)
    (hY : ∀ p, w.init0 (Yr p) = X.z ∧ w.fin (Yr p) = hyp p) (p : ι) :
    ((dualWord X σ w).init0 (Xr p) = line p ∧ (dualWord X σ w).fin (Xr p) = X.V) ∧
    ((dualWord X σ w).init0 (Yr p) = X.z ∧ (dualWord X σ w).fin (Yr p) = hyp p) := by
  have hl : ∀ p, X.perp (hyp p) = line p := fun p => by rw [← hperp, X.perp_perp]
  obtain ⟨a1, a2⟩ := dual_boundary X R hR σ w h (Yr p)
  obtain ⟨b1, b2⟩ := dual_boundary X R hR σ w h (Xr p)
  rw [hσY] at a1 a2
  rw [hσX] at b1 b2
  refine ⟨⟨?_, ?_⟩, ⟨?_, ?_⟩⟩
  · rw [a1, (hY p).2, hl]
  · rw [a2, (hY p).1, X.perp_z]
  · rw [b1, (hX p).2, X.perp_V]
  · rw [b2, (hX p).1, hperp]

end P104

/-! ### contract blocks (from DU1.md; the non-hosted block is reconstructed from the card's dual [[1/2,-1],[1/2,1]]) -/
section Blocks
def sw : Equiv.Perm (Fin 2) := Equiv.swap 0 1

/-- hosted block [[1,0],[1,1]] is invariant under transpose + sigma. -/
theorem hosted_block :
    (!![1, 0; 1, 1] : Matrix (Fin 2) (Fin 2) ℚ)ᵀ.submatrix sw.symm sw.symm = !![1, 0; 1, 1] := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [sw, Equiv.swap_apply_def]

/-- non-hosted block F = [[1,-1],[1/2,1/2]]: D(F) = [[1/2,-1],[1/2,1]] and diag(1,1/2) D(F) diag(2,1) = F
(one SCALE 2 and one SCALE 1/2, unpriced). -/
theorem nonhosted_block :
    (!![1, -1; 1/2, 1/2] : Matrix (Fin 2) (Fin 2) ℚ)ᵀ.submatrix sw.symm sw.symm = !![1/2, -1; 1/2, 1] ∧
    Matrix.diagonal ![1, 1/2] * (!![1/2, -1; 1/2, 1] : Matrix (Fin 2) (Fin 2) ℚ) * Matrix.diagonal ![2, 1] =
      !![1, -1; 1/2, 1/2] := by
  constructor
  · ext i j; fin_cases i <;> fin_cases j <;> simp [sw, Equiv.swap_apply_def]
  · ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Fin.sum_univ_two] <;> norm_num

end Blocks

/-! ### Part 5: caveat, COPY does not dualise to an ADD at matrix level -/
section Caveat
/-- COPY 0 <- 1 on two registers has matrix [[0,1],[0,1]]; its transpose is [[0,0],[1,1]], which is not an ADD matrix
1 + q e_ab (a != b: every ADD matrix has diagonal 1).  DU1's "COPY becomes ADD" holds only for a clean target. -/
theorem copy_not_add (a b : Fin 2) (hab : a ≠ b) (q : ℚ) :
    (!![0, 1; 0, 1] : Matrix (Fin 2) (Fin 2) ℚ)ᵀ ≠ 1 + Matrix.single a b q := by
  intro h
  have := congrFun (congrFun h 0) 0
  simp [Matrix.single_apply] at this
  by_cases h0 : a = 0 ∧ b = 0
  · exact hab (h0.1.trans h0.2.symm)
  · simp [h0] at this

end Caveat

end WordDuality

#print axioms WordDuality.dual_run
#print axioms WordDuality.Mrec_dual
#print axioms WordDuality.dualH_invoice
#print axioms WordDuality.word_invoice
#print axioms WordDuality.selfdual_boundary
#print axioms WordDuality.nonhosted_block
#print axioms WordDuality.copy_not_add
