import IndexedBridge

namespace Tintagel.Abelian
variable {A : Type u} (G : Abelian A)

/-- Literal source operations after hash-locked selected-AST recognition. Stage-indexed
invocations permit distinct implementations; all share the same live helpers. -/
def sourceB3With {H : Type v} (I : Nat → Invocation G H)
    (p1 p2 p3 : Pair A) (h : H) : List (Pair A) × H :=
  let r0 := (I 0).fwd (p1, h) -- stage 0
  let p1 := r0.1
  let h := r0.2
  let r1 := (I 1).bwd (p1, h) -- stage 1
  let p1 := r1.1
  let h := r1.2
  let p1 := (G.add p1.1 p2.1, p1.2) -- source operation 3: ('G', ('X', 1), ('X', 2), 1)
  let p2 := (p2.1, G.sub p2.2 p1.2) -- source operation 4: ('G', ('Y', 2), ('Y', 1), -1)
  let r4 := (I 2).fwd (p1, h) -- stage 2
  let p1 := r4.1
  let h := r4.2
  let p2 := (p2.1, G.add p2.2 p1.2) -- source operation 6: ('G', ('Y', 2), ('Y', 1), 1)
  let p1 := (G.sub p1.1 p2.1, p1.2) -- source operation 7: ('G', ('X', 1), ('X', 2), -1)
  let r7 := (I 3).bwd (p2, h) -- stage 3
  let p2 := r7.1
  let h := r7.2
  let p2 := (G.add p2.1 p3.1, p2.2) -- source operation 9: ('G', ('X', 2), ('X', 3), 1)
  let p3 := (p3.1, G.sub p3.2 p2.2) -- source operation 10: ('G', ('Y', 3), ('Y', 2), -1)
  let r10 := (I 4).fwd (p2, h) -- stage 4
  let p2 := r10.1
  let h := r10.2
  let p3 := (p3.1, G.add p3.2 p2.2) -- source operation 12: ('G', ('Y', 3), ('Y', 2), 1)
  let p2 := (G.sub p2.1 p3.1, p2.2) -- source operation 13: ('G', ('X', 2), ('X', 3), -1)
  let r13 := (I 5).bwd (p3, h) -- stage 5
  let p3 := r13.1
  let h := r13.2
  let r14 := (I 6).fwd (p3, h) -- stage 6
  let p3 := r14.1
  let h := r14.2
  let p2 := (p2.1, G.sub p2.2 p3.2) -- source operation 16: ('G', ('Y', 2), ('Y', 3), -1)
  let p3 := (G.add p3.1 p2.1, p3.2) -- source operation 17: ('G', ('X', 3), ('X', 2), 1)
  let p1 := (p1.1, G.sub p1.2 p2.2) -- source operation 18: ('G', ('Y', 1), ('Y', 2), -1)
  let p2 := (G.add p2.1 p1.1, p2.2) -- source operation 19: ('G', ('X', 2), ('X', 1), 1)
  ([p1, p2, p3], h)

theorem sourceB3_is_indexed_chain {H : Type v} (I : Nat → Invocation G H)
    (p q r : Pair A) (h : H) :
    sourceB3With G I p q r h = indexedChain G I p [q,r] h := rfl

theorem sourceB3_reduces_to_canonical {H : Type v} (I : Nat → Invocation G H)
    (p q r : Pair A) (h : H) :
    sourceB3With G I p q r h = (G.correct3 p q r, h) := by
  simp only [sourceB3With, (I 0).fwd_spec, (I 1).bwd_spec, (I 2).fwd_spec, (I 3).bwd_spec, (I 4).fwd_spec, (I 5).bwd_spec, (I 6).fwd_spec]
  rfl

theorem sourceB3_all_inputs {H : Type v} (I : Nat → Invocation G H)
    (p q r : Pair A) (h : H) :
    sourceB3With G I p q r h = ([G.quarter p, G.quarter q, G.quarter r], h) := by
  rw [sourceB3_reduces_to_canonical, b3_identity]

theorem sourceB3_correlated_signed_endpoint {H : Type v} {Ω : Type w}
    (I : Nat → Invocation G H) (p q r : Ω → Pair A) (h : Ω → H) (ω : Ω) :
    let z := sourceB3With G I (p ω) (q ω) (r ω) (h ω)
    (z.1.map G.signedExchange, z.2) = ([p ω, q ω, r ω], h ω) := by
  simp only [sourceB3_all_inputs, List.map_cons, List.map_nil, signed_exchange_quarter]

end Tintagel.Abelian

#print axioms Tintagel.Abelian.sourceB3_is_indexed_chain
#print axioms Tintagel.Abelian.sourceB3_reduces_to_canonical
#print axioms Tintagel.Abelian.sourceB3_all_inputs
#print axioms Tintagel.Abelian.sourceB3_correlated_signed_endpoint
