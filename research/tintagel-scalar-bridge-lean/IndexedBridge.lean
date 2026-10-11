import BridgeChain

namespace Tintagel.Abelian
variable {A : Type u} (G : Abelian A)

/-- Every stage may use a different implementation. Helpers are passed through
the actual invocation calls, including calls in recursive tails. -/
def indexedBorrow {H : Type v} (I : Nat → Invocation G H) (t : Nat)
    (p : Pair A) (qs : List (Pair A)) (h : H) : Pair A × List (Pair A) × H :=
  match qs with
  | [] =>
    let f := (I t).fwd (p, h)
    (f.1, [], f.2)
  | q :: tail =>
    let a := G.gateA p q
    let f := (I t).fwd (a.1, h)
    let b := G.gateB f.1 a.2
    let d := (I (t + 1)).bwd (b.2, f.2)
    let r := indexedBorrow I (t + 2) d.1 tail d.2
    let c := G.gateC b.1 r.1
    (c.1, c.2 :: r.2.1, r.2.2)

theorem indexed_borrow_all_inputs {H : Type v} (I : Nat → Invocation G H)
    (t : Nat) (p : Pair A) (qs : List (Pair A)) (h : H) :
    indexedBorrow G I t p qs h = (G.forward p, qs.map G.quarter, h) := by
  induction qs generalizing t p h with
  | nil => simp only [indexedBorrow, (I t).fwd_spec, List.map_nil]
  | cons q qs ih =>
    simp only [indexedBorrow, (I t).fwd_spec, (I (t + 1)).bwd_spec, ih, List.map_cons]
    change ((G.borrowOne p q).1, (G.borrowOne p q).2 :: qs.map G.quarter, h) = _
    rw [borrow_one]

def indexedChain {H : Type v} (I : Nat → Invocation G H)
    (p : Pair A) (qs : List (Pair A)) (h : H) : List (Pair A) × H :=
  let f := (I 0).fwd (p, h)
  let b := (I 1).bwd f
  let r := indexedBorrow G I 2 b.1 qs b.2
  (r.1 :: r.2.1, r.2.2)

theorem indexed_chain_all_inputs {H : Type v} (I : Nat → Invocation G H)
    (p : Pair A) (qs : List (Pair A)) (h : H) :
    indexedChain G I p qs h = ((p :: qs).map G.quarter, h) := by
  simp only [indexedChain, (I 0).fwd_spec, (I 1).bwd_spec,
    indexed_borrow_all_inputs, fbf, List.map_cons]

theorem indexed_chain_correlated_signed_endpoint {H : Type v} {Ω : Type w}
    (I : Nat → Invocation G H) (p : Ω → Pair A)
    (qs : Ω → List (Pair A)) (h : Ω → H) (ω : Ω) :
    let r := indexedChain G I (p ω) (qs ω) (h ω)
    (r.1.map G.signedExchange, r.2) = (p ω :: qs ω, h ω) := by
  simp only [indexed_chain_all_inputs, List.map_map, Function.comp_def, signed_exchange_quarter]
  exact congrArg (fun xs => (xs, h ω)) (List.map_id _)

end Tintagel.Abelian

#print axioms Tintagel.Abelian.indexed_borrow_all_inputs
#print axioms Tintagel.Abelian.indexed_chain_all_inputs
#print axioms Tintagel.Abelian.indexed_chain_correlated_signed_endpoint
