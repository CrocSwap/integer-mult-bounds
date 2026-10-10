/-!
# (key: gx-data) Raw Lean form of a `gcert/1` file (EXTENDED-CERT-SPEC section 1)

Core Lean only (no Mathlib): the generated data modules import nothing else, so they elaborate
cheaply.  Field order and meaning are those of the JSON; `pairs` and `cuts` are DERIVED by the
generator (`checks/wht26/gx-data/py/gxgen.py`) and must be tested by the label check.

Registers: `x_t = t`, `y_t = v + t`, slot `k = 2 v + k`.  Vectors are bit masks.
-/

namespace GXD

/-- the rational `(-1)^neg * num / den` (`den > 0`) -/
structure Co where
  neg : Bool
  num : Nat
  den : Nat
  deriving DecidableEq, Repr

/-- a gate: every register named (extras too) first moves to `frame`; then the adds happen in order -/
inductive Gate where
  /-- `tgt += co * src` for each `(tgt, co)` -/
  | out (frame src : Nat) (tgts : List (Nat × Co)) (extra : List Nat)
  /-- `tgt += co * src` for each `(src, co)` -/
  | inn (frame tgt : Nat) (srcs : List (Nat × Co))
  deriving Repr

/-- the scatter `y_t += sum over k of coef(t, k) * total k` -/
inductive Scat where
  /-- star rule: `inside` if coordinate `k` is in port `t`, else `outside` -/
  | star (inside outside : Co)
  /-- explicit rows: row `t` = `[(total k, coef)]` -/
  | table (rows : List (List (Nat × Co)))
  deriving Repr

/-- a `gcert/1` file -/
structure Raw where
  h : Nat
  v : Nat
  R : Nat
  N : Nat
  cst : Nat
  /-- `v` masks: the unit vectors of the ports -/
  ports : List Nat
  /-- CHUNKED frame table (`flatten` = the table); an entry is a reduced echelon basis, leading bits descending -/
  frames : List (List (List Nat))
  /-- frame id per register at the start -/
  start : List Nat
  /-- frame id per register at the end -/
  final : List Nat
  /-- position `k` = retained total `k`: (slot REGISTER, frame id) -/
  ret : List (Nat × Nat)
  scat : Scat
  /-- CHUNKED gates before the scatter -/
  A : List (List Gate)
  /-- CHUNKED gates after the scatter -/
  B : List (List Gate)
  /-- CHUNKED, derived: the distinct climbs `(a, b)`, `a ≠ b`, in order of first use -/
  pairs : List (List (Nat × Nat))
  /-- derived: replay cut points `(gates of A ++ B before the cut, frame id per register there)` -/
  cuts : List (Nat × List Nat)
  /-- slots that start off the zero frame `(slot REGISTER, frame id)` (rule 2); EMPTY on the path -/
  ext : List (Nat × Nat)
  /-- derived (questions.md Q1): per port `h` masks, the first is the port, pairwise dots = delta
  (an orthonormal basis of `F_2^h` through the port) -/
  obase : List (List Nat)

/-- registers of a gate, in the order they are moved -/
def Gate.regs : Gate → List Nat
  | .out _ s ts ex => s :: (ts.map Prod.fst ++ ex)
  | .inn _ t ss => t :: ss.map Prod.fst

/-- frame of a gate -/
def Gate.frame : Gate → Nat
  | .out f _ _ _ => f
  | .inn f _ _ => f

/-- single adds `(tgt, src, co)` of a gate, in order -/
def Gate.adds : Gate → List (Nat × Nat × Co)
  | .out _ s ts _ => ts.map fun p => (p.1, s, p.2)
  | .inn _ t ss => ss.map fun p => (t, p.1, p.2)

/-- the frame table -/
def Raw.frameTab (c : Raw) : List (List Nat) := c.frames.flatten

/-- all gates of phase A / phase B -/
def Raw.gatesA (c : Raw) : List Gate := c.A.flatten
def Raw.gatesB (c : Raw) : List Gate := c.B.flatten

/-- number of registers -/
def Raw.nreg (c : Raw) : Nat := 2 * c.v + c.R

end GXD
