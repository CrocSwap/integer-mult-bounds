import Std

/-!
Independent scalar component of the B_K bridge, based on the pinned B_2
Work/Bridge/Net.lean and Work/Bridge/Cert.lean headers. No repository imports.
This does not assert a geometry, route, finite bill, or analytic transfer.
-/
namespace Tintagel

/-- Ordinary abelian-group operations; redundant inverse laws simplify the
standalone proof without a dependency on Mathlib. No field or division assumed. -/
structure Abelian (A : Type u) where
  zero : A
  add : A → A → A
  neg : A → A
  assoc : ∀ a b c, add (add a b) c = add a (add b c)
  comm : ∀ a b, add a b = add b a
  add_zero : ∀ a, add a zero = a
  add_neg : ∀ a, add a (neg a) = zero
  neg_add : ∀ a b, neg (add a b) = add (neg a) (neg b)
  neg_neg : ∀ a, neg (neg a) = a

namespace Abelian

variable {A : Type u} (G : Abelian A)

def sub (a b : A) := G.add a (G.neg b)

theorem zero_add (a : A) : G.add G.zero a = a := by
  rw [G.comm, G.add_zero]
theorem neg_add_cancel (a : A) : G.add (G.neg a) a = G.zero := by
  rw [G.comm, G.add_neg]
theorem left_comm (a b c : A) : G.add a (G.add b c) = G.add b (G.add a c) := by
  rw [← G.assoc, G.comm a b, G.assoc]
theorem add_cancel_left (a b : A) : G.add a (G.add (G.neg a) b) = b := by
  rw [← G.assoc, G.add_neg, zero_add]
theorem neg_cancel_left (a b : A) : G.add (G.neg a) (G.add a b) = b := by
  rw [← G.assoc, neg_add_cancel, zero_add]

abbrev Pair (A : Type u) := A × A

def forward (p : Pair A) : Pair A := (p.1, G.add p.2 p.1)
def backward (p : Pair A) : Pair A := (G.sub p.1 p.2, p.2)
def quarter (p : Pair A) : Pair A := (G.neg p.2, p.1)
def signedExchange (p : Pair A) : Pair A := (p.2, G.neg p.1)

/-- The two assignments in each layer have distinct targets and unchanged sources. -/
def gateA (p q : Pair A) : Pair A × Pair A :=
  ((G.add p.1 q.1, p.2), (q.1, G.sub q.2 p.2))
def gateB (p q : Pair A) : Pair A × Pair A :=
  ((G.sub p.1 q.1, p.2), (q.1, G.add q.2 p.2))
def gateC (p q : Pair A) : Pair A × Pair A :=
  ((p.1, G.sub p.2 q.2), (G.add q.1 p.1, q.2))

/-- A; F on the old pair; B; backward on the new pair; F on the new
pair; C. This replaces F on the old pair and rotates the new pair. -/
def borrowOne (p q : Pair A) : Pair A × Pair A :=
  let a := G.gateA p q
  let b := G.gateB (G.forward a.1) a.2
  G.gateC b.1 (G.forward (G.backward b.2))

theorem borrow_one (p q : Pair A) :
    G.borrowOne p q = (G.forward p, G.quarter q) := by
  rcases p with ⟨x, y⟩
  rcases q with ⟨z, w⟩
  simp only [borrowOne, gateA, gateB, gateC, forward, backward, quarter, sub,
    G.neg_add, G.neg_neg, G.assoc, G.comm, left_comm,
    G.add_zero, G.add_neg, add_cancel_left]

  congr 2
  calc
    _ = G.add (G.add x (G.neg x)) (G.add (G.add y (G.neg y))
          (G.add (G.add z (G.neg z)) (G.add (G.add w (G.neg w)) z))) := by
      simp only [G.assoc, G.comm, left_comm]
    _ = z := by simp only [G.add_neg, zero_add]

theorem fbf (p : Pair A) :
    G.forward (G.backward (G.forward p)) = G.quarter p := by
  rcases p with ⟨x, y⟩
  simp only [forward, backward, quarter, sub, G.neg_add,
    G.assoc, G.comm, G.add_zero, G.add_neg, add_cancel_left]

/-- Recursive replacement of the final F. Its C layers execute in reverse
chain order, after the recursive tail has finished. -/
def borrow (G : Abelian A) (p : Pair A) : List (Pair A) → Pair A × List (Pair A)
  | [] => (G.forward p, [])
  | q :: qs =>
    let a := G.gateA p q
    let b := G.gateB (G.forward a.1) a.2
    let r := G.borrow (G.backward b.2) qs
    let c := G.gateC b.1 r.1
    (c.1, c.2 :: r.2)

/-- Universal borrowing interface, with no assumptions on the input values. -/
theorem borrow_identity (p : Pair A) (qs : List (Pair A)) :
    G.borrow p qs = (G.forward p, qs.map G.quarter) := by
  induction qs generalizing p with
  | nil => rfl
  | cons q qs ih =>
    simp only [borrow, ih, List.map_cons]
    change ((G.borrowOne p q).1, (G.borrowOne p q).2 :: qs.map G.quarter) = _
    rw [borrow_one]

/-- The full nonempty chain, with exactly 2K+1 invocations for K pairs. -/
def chain (p : Pair A) (qs : List (Pair A)) : List (Pair A) :=
  let r := G.borrow (G.backward (G.forward p)) qs
  r.1 :: r.2

theorem chain_identity (p : Pair A) (qs : List (Pair A)) :
    G.chain p qs = (p :: qs).map G.quarter := by
  simp only [chain, borrow_identity, fbf, List.map_cons]

theorem signed_exchange_quarter (p : Pair A) :
    G.signedExchange (G.quarter p) = p := by
  rcases p with ⟨x,y⟩
  simp only [signedExchange, quarter, G.neg_neg]

theorem chain_restored (p : Pair A) (qs : List (Pair A)) :
    (G.chain p qs).map G.signedExchange = p :: qs := by
  rw [chain_identity, List.map_map]
  simp only [Function.comp_def, signed_exchange_quarter]
  exact List.map_id _

/-- Arbitrary common parameter, allowing any correlations between all banks. -/
theorem correlated_inputs {Ω : Type v} (p : Ω → Pair A)
    (qs : Ω → List (Pair A)) (ω : Ω) :
    (G.chain (p ω) (qs ω)).map G.signedExchange = p ω :: qs ω :=
  G.chain_restored (p ω) (qs ω)

/-- Helpers are arbitrary live inputs, not extra independent dirt variables. -/
def withHelpers {H : Type v} (p : Pair A) (qs : List (Pair A)) (h : H) :=
  (G.chain p qs, h)

theorem helpers_unchanged {H : Type v} (p : Pair A) (qs : List (Pair A)) (h : H) :
    (G.withHelpers p qs h).2 = h := rfl

/-- The hypothesis required of each physically completed invocation, expressed
in its incoming/outgoing normalized frames. `H` contains ALL live helpers.
These are universal identities, even when helpers depend on bank inputs. -/
structure Invocation (G : Abelian A) (H : Type v) where
  fwd : Pair A × H → Pair A × H
  bwd : Pair A × H → Pair A × H
  fwd_spec : ∀ p h, fwd (p, h) = (G.forward p, h)
  bwd_spec : ∀ p h, bwd (p, h) = (G.backward p, h)

/-- Execute with the same helper state threaded through all invocations.
Twin gates act only on the bank pairs. -/
def borrowWith {H : Type v} (I : Invocation G H)
    (p : Pair A) (qs : List (Pair A)) (h : H) :
    Pair A × List (Pair A) × H :=
  match qs with
  | [] =>
    let r := I.fwd (p, h)
    (r.1, [], r.2)
  | q :: tail =>
    let a := G.gateA p q
    let f := I.fwd (a.1, h)
    let b := G.gateB f.1 a.2
    let d := I.bwd (b.2, f.2)
    let r := borrowWith I d.1 tail d.2
    let c := G.gateC b.1 r.1
    (c.1, c.2 :: r.2.1, r.2.2)

theorem borrow_with_helpers {H : Type v} (I : Invocation G H)
    (p : Pair A) (qs : List (Pair A)) (h : H) :
    borrowWith G I p qs h = (G.forward p, qs.map G.quarter, h) := by
  induction qs generalizing p h with
  | nil => simp only [borrowWith, I.fwd_spec, List.map_nil]
  | cons q qs ih =>
    simp only [borrowWith, I.fwd_spec, I.bwd_spec, ih, List.map_cons]
    change ((G.borrowOne p q).1, (G.borrowOne p q).2 :: qs.map G.quarter, h) = _
    rw [borrow_one]

def chainWith {H : Type v} (I : Invocation G H)
    (p : Pair A) (qs : List (Pair A)) (h : H) : List (Pair A) × H :=
  let f := I.fwd (p, h)
  let b := I.bwd f
  let r := borrowWith G I b.1 qs b.2
  (r.1 :: r.2.1, r.2.2)

/-- Reusable supplier scalar interface, including arbitrary shared live helpers. -/
theorem chain_with_helpers {H : Type v} (I : Invocation G H)
    (p : Pair A) (qs : List (Pair A)) (h : H) :
    chainWith G I p qs h = ((p :: qs).map G.quarter, h) := by
  simp only [chainWith, I.fwd_spec, I.bwd_spec, borrow_with_helpers, fbf, List.map_cons]

/-- Simultaneous restoration for any correlated input assignment. -/
theorem correlated_helpers {H : Type v} {Ω : Type w} (I : Invocation G H)
    (p : Ω → Pair A) (qs : Ω → List (Pair A)) (h : Ω → H) (ω : Ω) :
    let r := chainWith G I (p ω) (qs ω) (h ω)
    (r.1.map G.signedExchange, r.2) = (p ω :: qs ω, h ω) := by
  simp only [chain_with_helpers, List.map_map, Function.comp_def, signed_exchange_quarter]
  exact congrArg (fun xs => (xs, h ω)) (List.map_id _)

/-- In the recursive borrow word: one base F; each added pair adds B and F. -/
def borrowInvocations : Nat → Nat
  | 0 => 1
  | n + 1 => borrowInvocations n + 2

def twinAdditions : Nat → Nat
  | 0 => 0
  | n + 1 => twinAdditions n + 6

theorem invocation_count (n : Nat) : borrowInvocations n + 2 = 2 * (n + 1) + 1 := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [borrowInvocations]; omega

theorem twin_addition_count (n : Nat) : twinAdditions n = 6 * n := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [twinAdditions]; omega

/-- Explicit seven-invocation prefix, before terminal cleanup. -/
def prefix3 (p q r : Pair A) : Pair A × Pair A × Pair A :=
  let p0 := G.backward (G.forward p)
  let a12 := G.gateA p0 q
  let d12 := G.gateB (G.forward a12.1) a12.2
  let q0 := G.backward d12.2
  let a23 := G.gateA q0 r
  let d23 := G.gateB (G.forward a23.1) a23.2
  let r0 := G.forward (G.backward d23.2)
  (d12.1, d23.1, r0)

def correct3 (p q r : Pair A) : List (Pair A) :=
  let z := G.prefix3 p q r
  let c23 := G.gateC z.2.1 z.2.2
  let c12 := G.gateC z.1 c23.1
  [c12.1, c12.2, c23.2]

/-- The explicit seven-stage word is the generic K=3 program by reduction. -/
theorem correct3_is_chain (p q r : Pair A) :
    G.correct3 p q r = G.chain p [q,r] := rfl

theorem b3_identity (p q r : Pair A) :
    G.correct3 p q r = [G.quarter p, G.quarter q, G.quarter r] := by
  rw [correct3_is_chain, chain_identity]
  rfl

/-- Deliberately wrong ascending terminal cleanup order. -/
def wrong3 (p q r : Pair A) : List (Pair A) :=
  let z := G.prefix3 p q r
  let c12 := G.gateC z.1 z.2.1
  let c23 := G.gateC c12.2 z.2.2
  [c12.1, c23.1, c23.2]

end Abelian

def intAbelian : Abelian Int where
  zero := 0
  add := Int.add
  neg := Int.neg
  assoc := Int.add_assoc
  comm := Int.add_comm
  add_zero := Int.add_zero
  add_neg := Int.add_right_neg
  neg_add := fun _ _ => Int.neg_add
  neg_neg := Int.neg_neg

/-- Kernel-reduced exact counterexample to order-insensitive cleanup. -/
theorem wrong_order_counterexample :
    (intAbelian.wrong3 (0,1) (0,0) (0,0)).map intAbelian.signedExchange =
      [(0,1), (0,0), (0,1)] := by decide

theorem wrong_order_not_identity :
    (intAbelian.wrong3 (0,1) (0,0) (0,0)).map intAbelian.signedExchange ≠
      [(0,1), (0,0), (0,0)] := by decide

/-- Over integers, unsigned exchange cannot replace the signed endpoint. -/
theorem unsigned_endpoint_counterexample :
    let z := intAbelian.quarter (0,1)
    (z.2, z.1) = (0,-1) ∧ (z.2,z.1) ≠ ((0,1) : Int × Int) := by decide

end Tintagel

#print axioms Tintagel.Abelian.borrow_one
#print axioms Tintagel.Abelian.borrow_identity
#print axioms Tintagel.Abelian.chain_identity
#print axioms Tintagel.Abelian.chain_restored
#print axioms Tintagel.Abelian.correlated_inputs
#print axioms Tintagel.Abelian.invocation_count
#print axioms Tintagel.Abelian.twin_addition_count

#print axioms Tintagel.Abelian.borrow_with_helpers
#print axioms Tintagel.Abelian.chain_with_helpers
#print axioms Tintagel.Abelian.correlated_helpers

#print axioms Tintagel.Abelian.correct3_is_chain
#print axioms Tintagel.Abelian.b3_identity
#print axioms Tintagel.wrong_order_counterexample
#print axioms Tintagel.wrong_order_not_identity
#print axioms Tintagel.unsigned_endpoint_counterexample
