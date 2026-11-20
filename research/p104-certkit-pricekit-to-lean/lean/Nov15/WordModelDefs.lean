/-
WordModelDefs (lane WORDMODEL, coordinator, Nov 18).  SHARED definitions for the WORD MODEL swarm
(WM-Y, WM-R1, WM-R3, WM-SPEC, WM-R2/integration).  Plan + stubs: cards/WILD/LEANSWARM/WORDMODEL.md.
APPEND ONLY: never change an existing definition (sub-lanes build on them).

Sources (tag [src]):  independent.py = imb-c56 research/shared-wire-split-composition/independent.py
  (P104 word checker; line numbers below), SPEC = upstream 04-swap.tex:105-123 (SPECCHECK/ANSWER.md).
Field ℚ (coefficients are dyadic/smooth rationals, l.39-44: any field works; ℚ fixed for simplicity).
Charts = frames = sets of labels (Finset ℕ), the span of the frame basis (l.26-31: labels in 1..511, span
includes 0).  Order = inclusion; `c < d` = proper inclusion (frozenset `<`, l.51).
Rows = linear forms in the public INPUT registers (l.57-66 `adj` is the transpose): row r t = ∂ r / ∂ input t.
Kernel only: no sorry, no native_decide, no axioms.
-/
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.LinearAlgebra.Dimension.Finrank
import Mathlib.LinearAlgebra.Pi
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Fintype.Sum
import Mathlib.Data.Nat.Log
import Nov15.SafeRungsClique

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique Module

/-! ## Charts (frames) -/

/-- a chart = the set of labels of its span [src l.26-31, l.33 `frames=[span(b)...]`]. -/
abbrev Ch := Finset ℕ

/-- V = F2^9, |frame| = 512 [src l.73 `len(frames[final[x]])==512`]. -/
def Vc : Ch := range 512
/-- ⟨q⟩ = {0,q} [src l.73 `frames[initial[x]]==frozenset((0,q))`]. -/
def line (q : ℕ) : Ch := {0, q}
/-- {0} [src l.74]. -/
def zeroCh : Ch := {0}
/-- q^⊥ [src l.75 `frozenset(v for v in range(512) if (v&q).bit_count()%2==0)`]. -/
def Hq (q : ℕ) : Ch := (range 512).filter (fun v => dot v q = 0)

/-- chart is a subspace of F2^9 (labels < 512, 0 ∈ c, closed under xor) [src l.26-31]. Optional clause. -/
def IsSubsp (c : Ch) : Prop := 0 ∈ c ∧ (∀ a ∈ c, a < 512) ∧ ∀ a ∈ c, ∀ b ∈ c, a ^^^ b ∈ c
/-- dim = log2 |frame| [src l.34]. -/
def dim (c : Ch) : ℕ := Nat.log 2 c.card
/-- native MOVE price = |Δdim| [src l.52 `rank=abs(dim[b]-dim[a])`; SPEC price = rank(M_b − M_a) ≥ this]. -/
def mvPrice (c d : Ch) : ℕ := Int.natAbs ((dim d : ℤ) - dim c)

/-! ## Registers and the #7113 caller contract -/

/-- registers by role: live port pair X,Y; hosted pair X2,Y2 (meaningful for D ports only; for non-D ports
they are phantoms, `pub = false`, i.e. treated like owned scratch); helpers h; owned o
[src l.69-83, l.88 `main=set(live)|{r+112}|X2|Y2`]. -/
inductive Reg (Pt Hl Ow : Type) where
  | x (p : Pt) | y (p : Pt) | x2 (p : Pt) | y2 (p : Pt) | h (i : Hl) | o (i : Ow)
  deriving DecidableEq

/-- the fixed caller data (#7113 contract). -/
structure Caller (Pt : Type) [Fintype Pt] where
  lab : Pt → ℕ                 -- port label q   [src l.72 `q=W['ports'][i]`]
  isD : Pt → Bool              -- D port (96 of 104) [src l.69-70]
  lab_lt : ∀ p, lab p < 512
  lab_odd : ∀ p, wt (lab p) % 2 = 1          -- odd weight (caller fact c3)
  lab_inj : Function.Injective lab
  card104 : Fintype.card Pt = 104            -- [src l.70]
  Q_sub : ∀ q ∈ Q, ∃ p, lab p = q            -- clique Q ⊆ ports (caller fact c4, data)

variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- Reg ≃ a sum type, for the Fintype instance. -/
def regEquiv : Reg Pt Hl Ow ≃ Pt ⊕ Pt ⊕ Pt ⊕ Pt ⊕ Hl ⊕ Ow where
  toFun
    | .x p => .inl p | .y p => .inr (.inl p) | .x2 p => .inr (.inr (.inl p))
    | .y2 p => .inr (.inr (.inr (.inl p))) | .h i => .inr (.inr (.inr (.inr (.inl i))))
    | .o i => .inr (.inr (.inr (.inr (.inr i))))
  invFun
    | .inl p => .x p | .inr (.inl p) => .y p | .inr (.inr (.inl p)) => .x2 p
    | .inr (.inr (.inr (.inl p))) => .y2 p | .inr (.inr (.inr (.inr (.inl i)))) => .h i
    | .inr (.inr (.inr (.inr (.inr i)))) => .o i
  left_inv := by intro r; cases r <;> rfl
  right_inv := by
    intro z; rcases z with p | p | p | p | i | i <;> rfl

instance : Fintype (Reg Pt Hl Ow) := Fintype.ofEquiv _ regEquiv.symm

/-- public registers [src l.33 `public==n`; l.50 `owned==(r>=n)`]. -/
def pub (cl : Caller Pt) : Reg Pt Hl Ow → Bool
  | .x _ | .y _ | .h _ => true
  | .x2 p | .y2 p => cl.isD p
  | .o _ => false

/-- unit row e_r. -/
noncomputable def e (r : Reg Pt Hl Ow) : Reg Pt Hl Ow → ℚ := Pi.single r 1

/-- target final row of each register [src l.68, l.79-83 (target[j] = row of output j)]:
D port: X = e_X, Y = e_Y + e_X;  non-D (B) port: X = e_X − e_Y, Y = ½e_X + ½e_Y;
hosted: X2 = e_X2 − e_Y2, Y2 = e_Y2;  helpers e_h;  owned 0 (CLEARed). -/
noncomputable def tgt (cl : Caller Pt) : Reg Pt Hl Ow → Reg Pt Hl Ow → ℚ
  | .x p => if cl.isD p then e (.x p) else e (.x p) - e (.y p)
  | .y p => if cl.isD p then e (.y p) + e (.x p) else (1/2 : ℚ) • e (.x p) + (1/2 : ℚ) • e (.y p)
  | .x2 p => e (.x2 p) - e (.y2 p)
  | .y2 p => e (.y2 p)
  | .h i => e (.h i)
  | .o _ => 0

/-- live-X projection P: v ↦ (v (X_p))_p  (R3 §2). -/
noncomputable def Pproj : (Reg Pt Hl Ow → ℚ) →ₗ[ℚ] (Pt → ℚ) :=
  LinearMap.funLeft ℚ ℚ (fun p => Reg.x p)

/-! ## Run state and events -/

inductive Loc where
  | unborn
  | sit (c : Ch)
  | cleared
  deriving DecidableEq

/-- run state with ghosts.  B c = public born at c; A c = public entrants into c, eRow r c = r's row at
its entry into c; olog = owned MOVEs (source, target, row at the move), newest first; slog = STOPS:
(r, c) logged when public r LEAVES a chart c it had ENTERED (an intermediate chart of its path; the
`nst` of SafeRungsPrice); plog = public MOVEs (r, source, target), newest first. -/
structure St (R : Type) where
  loc : R → Loc
  row : R → R → ℚ
  B : Ch → Finset R
  A : Ch → Finset R
  eRow : R → Ch → R → ℚ
  olog : List (Ch × Ch × (R → ℚ))
  slog : List (R × Ch)
  plog : List (R × Ch × Ch)

section Run
variable {R : Type} [Fintype R] [DecidableEq R] (pb : R → Bool)

/-- the initial state: nothing born (public INPUT registers are born by `birthPub` at their initial frame). -/
def init : St R :=
  ⟨fun _ => .unborn, fun _ => 0, fun _ => ∅, fun _ => ∅, fun _ _ => 0, [], [], []⟩

/-- one event.  Tags:
* birthPub: public register at its initial frame with unit row (input) [src l.33, l.58 `adj=[{r:1}]`].
* birthOwn: owned INIT, row 0 [src l.46, l.61 `adj[r]={}`].
* gate: ADD / COPY / SCALE = row r := Σ coef_t row_t over registers AT THE SAME CHART as r
  [src l.54-55 `cur[r]==cur[e[2]]==e[-1]`; SPEC "common frame at a gate"].
* movePub: public MOVE strictly ascending, c ⊂ d [src l.51 V-asc, a VERIFIER line, not SPEC].
* moveOwn: owned MOVE, ANY target (more general than l.51's nesting; nesting is the separate clause
  `OwnedNested`).  Row unchanged by MOVE [src l.62].
* clearOwn: owned CLEAR [src l.48]. -/
inductive Step : St R → St R → Prop
  | birthPub (s : St R) (r : R) (c : Ch) : s.loc r = .unborn → pb r = true →
      Step s { s with loc := Function.update s.loc r (.sit c),
                      row := Function.update s.row r (Pi.single r 1),
                      B := Function.update s.B c (insert r (s.B c)) }
  | birthOwn (s : St R) (r : R) (c : Ch) : s.loc r = .unborn → pb r = false →
      Step s { s with loc := Function.update s.loc r (.sit c),
                      row := Function.update s.row r 0 }
  | gate (s : St R) (r : R) (c : Ch) (coef : R → ℚ) : s.loc r = .sit c →
      Step s { s with row := Function.update s.row r (∑ t ∈ univ.filter (fun t => s.loc t = .sit c), coef t • s.row t) }
  | movePub (s : St R) (r : R) (c d : Ch) : s.loc r = .sit c → pb r = true → c < d →
      Step s { s with loc := Function.update s.loc r (.sit d),
                      A := Function.update s.A d (insert r (s.A d)),
                      eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c',
                      slog := if r ∈ s.A c then (r, c) :: s.slog else s.slog,
                      plog := (r, c, d) :: s.plog }
  | moveOwn (s : St R) (r : R) (c d : Ch) : s.loc r = .sit c → pb r = false →
      Step s { s with loc := Function.update s.loc r (.sit d),
                      olog := (c, d, s.row r) :: s.olog }
  | clearOwn (s : St R) (r : R) (c : Ch) : s.loc r = .sit c → pb r = false →
      Step s { s with loc := Function.update s.loc r .cleared,
                      row := Function.update s.row r 0 }

/-- reachable states. -/
def Reach (s : St R) : Prop := Relation.ReflTransGen (Step pb) init s

/-- generators of I_C: unit rows of public births at C, entry rows of public entrants, rows of owned
MOVEs into C (R3 §1). -/
def gens (s : St R) (c : Ch) : Set (R → ℚ) :=
  (fun r => (Pi.single r (1 : ℚ) : R → ℚ)) '' ↑(s.B c) ∪ (fun r => s.eRow r c) '' ↑(s.A c)
    ∪ {v | ∃ a, (a, c, v) ∈ s.olog}

/-- I_C. -/
def I (s : St R) (c : Ch) : Submodule ℚ (R → ℚ) := Submodule.span ℚ (gens s c)

/-- final rows of public registers ending at c (F_stay). -/
def Fstay (s : St R) (c : Ch) : Set (R → ℚ) :=
  {v | ∃ r, pb r = true ∧ s.loc r = .sit c ∧ v = s.row r}

/-- unit rows of public registers born at c that end elsewhere (E_BL). -/
def EBL (s : St R) (c : Ch) : Set (R → ℚ) :=
  (fun r => (Pi.single r (1 : ℚ) : R → ℚ)) '' {r | r ∈ s.B c ∧ s.loc r ≠ .sit c}

open Classical in
/-- slack σ_C = (#stops at C) + (#owned MOVEs into C). -/
noncomputable def sigma (s : St R) (c : Ch) : ℕ :=
  s.slog.countP (fun t => decide (t.2 = c)) + s.olog.countP (fun m => decide (m.2.1 = c))

/-- #owned MOVEs (the `no` of SafeRungsPrice). -/
def nOwned (s : St R) : ℕ := s.olog.length
/-- #stops (the `nst` of SafeRungsPrice). -/
def nStops (s : St R) : ℕ := s.slog.length
open Classical in
/-- owned MOVEs whose target lies in a down-set ⇓q^⊥, q ∈ Q (R1 type). -/
noncomputable def nR1 (s : St R) : ℕ := s.olog.countP (fun m => decide (InDown m.2.1))
open Classical in
/-- owned MOVEs whose target meets Q (R2 type, U_Q). -/
noncomputable def nR2 (s : St R) : ℕ := s.olog.countP (fun m => decide (InUp m.2.1))
open Classical in
/-- owned MOVEs into a chart ≠ V. -/
noncomputable def nOwnNonV (s : St R) : ℕ := s.olog.countP (fun m => decide (m.2.1 ≠ Vc))

/-! ### Run-level facts (WM-R3 deliverables, stated here as Props so WM-Y can take them as inputs) -/

/-- CS at the end: every final row of a register sitting at c lies in I_c. -/
def CSFinal (s : St R) : Prop := ∀ r c, s.loc r = .sit c → s.row r ∈ I s c
/-- CS at entry: the row with which r entered d was a row sitting at some chart c ⊂ d, hence in I_c. -/
def CSEntry (s : St R) : Prop := ∀ r d, r ∈ s.A d → ∃ c, c < d ∧ s.eRow r d ∈ I s c
/-- each register is born at most once. -/
def BornUnique (s : St R) : Prop := ∀ r c c', r ∈ s.B c → r ∈ s.B c' → c = c'
/-- slack-rank lemma at every chart ≠ V (R3 §2). -/
def SlackRank (s : St R) : Prop :=
  ∀ c, c ≠ Vc → ∃ K : Submodule ℚ (R → ℚ), finrank ℚ K ≤ sigma s c ∧
    I s c ≤ Submodule.span ℚ (Fstay pb s c ∪ EBL s c) ⊔ K

end Run

/-! ## A legal WORD (end state of a run satisfying the #7113 caller contract) -/

/-- `Word cl s`: s is reachable, public registers all sit at the end and owned ones do not [src l.56],
caller endpoints [src l.71-78], final rows = target [src l.79-87 `bad_inputs` empty]. -/
structure Word (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) : Prop where
  reach : Reach (pub cl) s
  pub_sit : ∀ r, pub cl r = true → ∃ c, s.loc r = .sit c
  own_off : ∀ r c, pub cl r = false → s.loc r ≠ .sit c
  x_birth : ∀ p, Reg.x p ∈ s.B (line (cl.lab p))
  x_final : ∀ p, s.loc (.x p) = .sit Vc
  y_birth : ∀ p, Reg.y p ∈ s.B zeroCh
  y_final : ∀ p, s.loc (.y p) = .sit (Hq (cl.lab p))
  x2_birth : ∀ p, cl.isD p = true → Reg.x2 p ∈ s.B (line (cl.lab p))
  x2_final : ∀ p, cl.isD p = true → s.loc (.x2 p) = .sit Vc
  y2_birth : ∀ p, cl.isD p = true → Reg.y2 p ∈ s.B zeroCh
  y2_final : ∀ p, cl.isD p = true → s.loc (.y2 p) = .sit (Hq (cl.lab p))
  final_row : ∀ r, pub cl r = true → s.row r = tgt cl r

/-! ## Optional legality clauses (WM-SPEC; not in `Word`, used only for prices hO1 / hM) -/

/-- every chart used by a MOVE is a subspace [src l.26-31]. -/
def ChartsSubsp (s : St R) : Prop :=
  (∀ m ∈ s.olog, IsSubsp m.1 ∧ IsSubsp m.2.1) ∧ (∀ m ∈ s.plog, IsSubsp m.2.1 ∧ IsSubsp m.2.2)
/-- owned MOVEs nested (either direction) [src l.51 owned clause; local.py:66]. -/
def OwnedNested (s : St R) : Prop := ∀ m ∈ s.olog, m.1 < m.2.1 ∨ m.2.1 < m.1

/-! ## Theorem stubs (proved in the lane files; listed in WORDMODEL.md)
* WM-R1  (WordModelR1.lean): `R1 : Word cl s → 8 ≤ nR1 s`
* WM-R2  (WordModelR2.lean, coordinator): `R2 : Word cl s → 8 ≤ nR2 s`
* WM-R3  (WordModelR3.lean): `cs_final : Word cl s → CSFinal s`, `cs_entry : Word cl s → CSEntry s`,
          `born_unique : Word cl s → BornUnique s`, `slack_rank : Word cl s → SlackRank (pub cl) s`
* WM-Y   (WordModelY.lean): `theoremY : Word cl s → CSFinal s → CSEntry s → BornUnique s →
          SlackRank (pub cl) s → 104 ≤ nStops s + nOwnNonV s`
* integration (WordModelU0.lean, coordinator): U0 κ < .0204111 for every Word, hR1-hR3 removed. -/

end WordModel
