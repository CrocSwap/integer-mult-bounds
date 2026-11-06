import BitXorTwoSidedInjectionAdapter

/-!
Finite singleton-state supplier for the ordered XOR injection interface.
This derives the universal post-entrance encoded-vector equation from one
basis equation per register in a complete finite enumeration. Enumeration
order is arbitrary and duplicate entries are harmless: the induction clears
each peeled coordinate before continuing. Incoming target/helper bits stay
arbitrary. No selected matrix, frame, physical store or precision is supplied.

The algebra is standard finite Boolean linearity. This source reuses the
PR590 ordered interpreter, PR597 reversal, and the checked run_xor and
state-dependent injection adapter. Anthony (@anthonylei)'s PR774 already
proves compensation algebra for a separate unary interpreter. The concrete
motivation is Gareth Davidson/bitplane PR915 at e9daefe320a0043000bd9746664ed02c3287d056
and PR926 at 0f216a345c37bc71cc0e22030ef11ec31b26a69e, with the latter's
credit to Scott Woolsey Biggart's PR733 two-sided method.
Apache-2.0; prepared with OpenAI assistance. Uncompiled source proposal.
-/
namespace CurrentMain.BitXorFiniteBasis
open BitXor BitXorConjugacy BitXorInjectionAdapter
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]

/-- A singleton true bit; every other coordinate is false. -/
def basisState (r : Reg) : State Reg := fun q => if q = r then true else false

private def zeroState : State Reg := fun _ => false
private def atom (r : Reg) (b : Bool) : State Reg :=
  fun q => if q = r then b else false
private def clear (r : Reg) (s : State Reg) : State Reg :=
  fun q => if q = r then false else s q

private theorem split_state (r : Reg) (s : State Reg) :
    s = xorState (atom r (s r)) (clear r s) := by
  funext q
  by_cases h : q = r
  · subst q
    cases hs : s r <;> simp only [atom, clear, xorState, if_pos rfl, hs, if_true, Bool.xor_false]
  · simp only [atom, clear, xorState, if_neg h, Bool.false_xor]

private theorem additive_zero (F : State Reg → State Reg)
    (hF : ∀ s t, F (xorState s t) = xorState (F s) (F t)) :
    F zeroState = zeroState := by
  funext r
  have h := congrFun (hF zeroState zeroState) r
  change F zeroState r = (F zeroState r ^^ F zeroState r) at h
  simpa only [Bool.xor_self] using h

private theorem atom_eq (F G : State Reg → State Reg)
    (hF0 : F zeroState = zeroState) (hG0 : G zeroState = zeroState)
    (hb : ∀ r, F (basisState r) = G (basisState r)) (r : Reg) (b : Bool) :
    F (atom r b) = G (atom r b) := by
  cases b with
  | false =>
    have hz : atom r false = (zeroState : State Reg) := by
      funext q
      simp only [atom, zeroState, ite_self]
    rw [hz, hF0, hG0]
  | true => exact hb r

private theorem maps_eq_of_supported
    (F G : State Reg → State Reg)
    (hF : ∀ s t, F (xorState s t) = xorState (F s) (F t))
    (hG : ∀ s t, G (xorState s t) = xorState (G s) (G t))
    (hb : ∀ r, F (basisState r) = G (basisState r))
    (registers : List Reg) (s : State Reg)
    (hsupport : ∀ r, r ∉ registers → s r = false) : F s = G s := by
  have hF0 := additive_zero F hF
  have hG0 := additive_zero G hG
  induction registers generalizing s with
  | nil =>
    have hz : s = zeroState := by
      funext r
      exact hsupport r (by simp)
    rw [hz, hF0, hG0]
  | cons r rest ih =>
    have ht : ∀ q, q ∉ rest → clear r s q = false := by
      intro q hq
      by_cases hqr : q = r
      · simp only [clear, if_pos hqr]
      · simp only [clear, if_neg hqr]
        apply hsupport q
        intro hm
        rcases List.mem_cons.mp hm with heq | hmem
        · exact hqr heq
        · exact hq hmem
    have hrest := ih (clear r s) ht
    calc
      F s = F (xorState (atom r (s r)) (clear r s)) :=
        congrArg F (split_state r s)
      _ = xorState (F (atom r (s r))) (F (clear r s)) := hF _ _
      _ = xorState (G (atom r (s r))) (G (clear r s)) := by
        rw [atom_eq F G hF0 hG0 hb r (s r), hrest]
      _ = G (xorState (atom r (s r)) (clear r s)) := (hG _ _).symm
      _ = G s := congrArg G (split_state r s).symm

private theorem maps_eq_of_basis
    (registers : List Reg) (hcover : ∀ r, r ∈ registers)
    (F G : State Reg → State Reg)
    (hF : ∀ s t, F (xorState s t) = xorState (F s) (F t))
    (hG : ∀ s t, G (xorState s t) = xorState (G s) (G t))
    (hb : ∀ r ∈ registers, F (basisState r) = G (basisState r))
    (s : State Reg) : F s = G s :=
  maps_eq_of_supported F G hF hG (fun r => hb r (hcover r)) registers s
    (fun r hr => False.elim (hr (hcover r)))

private theorem injectionVector_xor
    (target : Reg → Prop) [DecidablePred target]
    (words : List (Gate Reg)) (s t : State Reg) :
    injectionVector target words (xorState s t) =
      xorState (injectionVector target words s) (injectionVector target words t) := by
  have herase : eraseTargets target (xorState s t) =
      xorState (eraseTargets target s) (eraseTargets target t) := by
    funext r
    by_cases hr : target r <;> simp only [eraseTargets, xorState, hr, if_true, if_false, Bool.xor_self]
  funext r
  by_cases hr : target r
  · simp only [injectionVector, xorState, if_pos hr]
    change run words (eraseTargets target (xorState s t)) r =
      (run words (eraseTargets target s) r ^^ run words (eraseTargets target t) r)
    rw [herase]
    exact congrFun (run_xor words (eraseTargets target s) (eraseTargets target t)) r
  · simp only [injectionVector, if_neg hr, xorState, Bool.xor_self]

/-- Finite basis equations supply the substantive universal encoding premise.
No entrance read/write restrictions are required for linearity. In particular,
self reads and repeated operands retain their actual ordered interpretation. -/
theorem encoded_vector_of_basis
    (target : Reg → Prop) [DecidablePred target]
    (registers : List Reg) (hcover : ∀ r, r ∈ registers)
    (entrance original encoded : List (Gate Reg))
    (hbasis : ∀ r ∈ registers,
      injectionVector target encoded (run entrance (basisState r)) =
        run entrance (injectionVector target original (basisState r)))
    (s : State Reg) :
    injectionVector target encoded (run entrance s) =
      run entrance (injectionVector target original s) := by
  let F : State Reg → State Reg :=
    fun t => injectionVector target encoded (run entrance t)
  let G : State Reg → State Reg :=
    fun t => run entrance (injectionVector target original t)
  have hF : ∀ u v, F (xorState u v) = xorState (F u) (F v) := by
    intro u v
    dsimp only [F]
    rw [run_xor, injectionVector_xor]
  have hG : ∀ u v, G (xorState u v) = xorState (G u) (G v) := by
    intro u v
    dsimp only [G]
    rw [injectionVector_xor, run_xor]
  exact maps_eq_of_basis registers hcover F G hF hG hbasis s

/-- Plug finite source-bound equations into the accepted actual-word adapter.
No target/helper cleanliness, selected instance, or physical precision follows
from merely supplying an enumeration; every basis equation is still required. -/
theorem conjugated_word_injection_of_basis
    (target : Reg → Prop) [DecidablePred target]
    (registers : List Reg) (hcover : ∀ r, r ∈ registers)
    (entrance original encoded : List (Gate Reg))
    (hself : ∀ g ∈ entrance, g.dst ∉ g.sources)
    (horiginal_writes : ∀ g ∈ original, target g.dst)
    (horiginal_reads : ∀ g ∈ original, ∀ r ∈ g.sources, ¬ target r)
    (hencoded_writes : ∀ g ∈ encoded, target g.dst)
    (hencoded_reads : ∀ g ∈ encoded, ∀ r ∈ g.sources, ¬ target r)
    (hbasis : ∀ r ∈ registers,
      injectionVector target encoded (run entrance (basisState r)) =
        run entrance (injectionVector target original (basisState r)))
    (s : State Reg) :
    run (entrance ++ encoded ++ entrance.reverse) s = run original s ∧
      ∀ r, ¬ target r →
        run (entrance ++ encoded ++ entrance.reverse) s r = s r :=
  BitXorTwoSidedInjectionAdapter.conjugated_word_injection target entrance original encoded
    hself horiginal_writes horiginal_reads hencoded_writes hencoded_reads
    (encoded_vector_of_basis target registers hcover entrance original encoded hbasis) s

end CurrentMain.BitXorFiniteBasis
#print axioms CurrentMain.BitXorFiniteBasis.encoded_vector_of_basis
#print axioms CurrentMain.BitXorFiniteBasis.conjugated_word_injection_of_basis
