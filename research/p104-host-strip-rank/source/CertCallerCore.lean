/-
CertCallerCore (lane CK-CALLER, Nov 19).  Generic caller-facts machinery: the caller block of a P104 invoice
(Theorem K's Dc = cdat T - cdat P) DERIVED from a caller file (schema mixed-root-caller/1), not taken as a constant.
Rules (= the repo verifier's caller_invoice, research/p104-flipped-helper-combination/pricing.py, plus the #7113
package's IDLE_ODD rule, 7113 emit_odd_type_ab.py l.127-132; = PRICEKIT README "Who pays what"):
  every caller event of type t is charged once per port of t (ports t = len(types[t].ports));
  QUERY -> P[1];  IDLE_ONE s -> P[8|s|];  IDLE_ODD s -> P[8|s|+1];  ADD/SCALE/SWAP/LAMBDA -> nothing;  J -> one call;
  diagonal row (exponent, zero, mask) of type t -> T[(exponent mod 2) + 8 * |mask|] per port of t.
Data encoding (generator toolkit/certkit/callerfacts.py, round-trip checked there):
  events: one Nat, 32-bit slots; slot = op (bits 0-3: 0 J, 1 ADD, 2 SCALE, 3 SWAP, 4 LAMBDA, 5 QUERY, 6 IDLE_ONE,
          7 IDLE_ODD) + 16 * type index (bits 4-5) + 64 * stage mask (bit k of the mask = stage k in the set).
  diagonal rows of each type: one Nat, 64-bit slots; slot = (exponent + 2^15) (bits 0-15) + 2^16 * mask bits.
`hist` merges a (rank, count) item list into the rank-sorted histogram; cdat_hist: it preserves cdat for every s.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.SafeRungsPrice

namespace CertCaller
open SafeRungsPrice

/-- slot i of width w of a packed Nat. -/
def slot (w c i : ℕ) : ℕ := c / 2 ^ (w * i) % 2 ^ w

/-- number of set bits among the first k bits. -/
def popc : ℕ → ℕ → ℕ
  | _, 0 => 0
  | x, k + 1 => x % 2 + popc (x / 2) k

structure CType where
  ports : ℕ
  nrow : ℕ
  rows : ℕ

structure CData where
  types : List CType
  nev : ℕ
  evs : ℕ

def evOp (x : ℕ) : ℕ := x % 16
def evTy (x : ℕ) : ℕ := x / 16 % 4
def evSt (x : ℕ) : ℕ := x / 64

def portsOf (C : CData) (t : ℕ) : ℕ := (C.types.getD t ⟨0, 0, 0⟩).ports

def ev (C : CData) (i : ℕ) : ℕ := slot 32 C.evs i

/-- the paid items of one caller event: (rank, ports of its type). -/
def evItem (C : CData) (x : ℕ) : List (ℕ × ℕ) :=
  if evOp x = 5 then [(1, portsOf C (evTy x))]
  else if evOp x = 6 then [(8 * popc (evSt x) 26, portsOf C (evTy x))]
  else if evOp x = 7 then [(8 * popc (evSt x) 26 + 1, portsOf C (evTy x))]
  else []

/-- the caller's paid items P (raw, one per invoiced event). -/
def pRaw (C : CData) : List (ℕ × ℕ) := (List.range C.nev).flatMap fun i => evItem C (ev C i)

/-- diagonal row rank: (exponent mod 2) + 8 * degree. -/
def rowRank (x : ℕ) : ℕ := ((((x % 2 ^ 16 : ℕ) : ℤ) - 2 ^ 15) % 2).toNat + 8 * popc (x / 2 ^ 16) 40

/-- the caller's target items T (raw, one per diagonal row and type). -/
def tRaw (C : CData) : List (ℕ × ℕ) :=
  C.types.flatMap fun t => (List.range t.nrow).map fun i => (rowRank (slot 64 t.rows i), t.ports)

/-- number of calls (J events). -/
def calls (C : CData) : ℕ := ((List.range C.nev).filter fun i => evOp (ev C i) = 0).length

/-- every event has a known opcode (0..7). -/
def known (C : CData) : Bool := (List.range C.nev).all fun i => evOp (ev C i) ≤ 7

/-- merge one (rank, count) item into a rank-sorted histogram. -/
def ins (p : ℕ × ℕ) : List (ℕ × ℕ) → List (ℕ × ℕ)
  | [] => [p]
  | q :: l => if p.1 < q.1 then p :: q :: l else if p.1 = q.1 then (q.1, q.2 + p.2) :: l else q :: ins p l

def hist (l : List (ℕ × ℕ)) : List (ℕ × ℕ) := l.foldr ins []

theorem cdat_cons (s : ℝ) (p : ℕ × ℕ) (l : List (ℕ × ℕ)) :
    cdat s (p :: l) = (p.2 : ℝ) * (p.1 : ℝ) ^ s + cdat s l := by
  simp [cdat]

theorem cdat_ins (s : ℝ) (p : ℕ × ℕ) (l : List (ℕ × ℕ)) :
    cdat s (ins p l) = (p.2 : ℝ) * (p.1 : ℝ) ^ s + cdat s l := by
  induction l with
  | nil => simp [ins, cdat]
  | cons q l ih =>
    simp only [ins]
    split_ifs with h1 h2
    · rw [cdat_cons, cdat_cons]
    · rw [cdat_cons, cdat_cons]
      simp only
      rw [h2]; push_cast; ring
    · rw [cdat_cons, ih, cdat_cons]; ring

/-- the histogram has the same invoice as the raw item list, for every exponent s. -/
theorem cdat_hist (s : ℝ) (l : List (ℕ × ℕ)) : cdat s (hist l) = cdat s l := by
  induction l with
  | nil => rfl
  | cons p l ih =>
    show cdat s (ins p (hist l)) = _
    rw [cdat_ins, ih, cdat_cons]

end CertCaller

#print axioms CertCaller.cdat_hist
