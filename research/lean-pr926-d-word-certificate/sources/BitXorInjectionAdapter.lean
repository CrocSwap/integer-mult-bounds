import BitXorConjugacy

/-!
Actual ordered-word adapter for restored-basis Boolean injections.
The input to an injection is the complete arbitrary off-target state, retained
by eraseTargets. Target-only writes in the entrance preserve that context.
The encoded-vector identity remains an explicit premise: no selected matrix,
word, frame geometry, signed-positive bound or hosted invoice is certified.
Motivated by Gareth Davidson/bitplane PR915 at mathematical head
7d5ef1dcf994d0542f2d302110b33780f5504ab7 and publication head
e9daefe320a0043000bd9746664ed02c3287d056, with its credited restored-basis
PR794/713/716/686 lineage. Reuses the PR590 interpreter and PR597 reversal API.
Apache-2.0; prepared with OpenAI assistance. Uncompiled source proposal.
-/
namespace CurrentMain.BitXorInjectionAdapter
open BitXor BitXorConjugacy
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]
variable (target : Reg → Prop) [DecidablePred target]

def injectionVector (words : List (Gate Reg)) (s : State Reg) : State Reg :=
  fun r => if target r then run words (eraseTargets target s) r else false

private theorem injection_vector_support (words : List (Gate Reg))
    (s : State Reg) (r : Reg) (hr : ¬ target r) :
    injectionVector target words s r = false := by
  simp only [injectionVector, if_neg hr]

/-- The actual injection word adds its target-supported contribution to an
arbitrary state. Its donors may be any off-target registers. -/
theorem injection_execution (words : List (Gate Reg))
    (hwrites : ∀ g ∈ words, target g.dst)
    (hreads : ∀ g ∈ words, ∀ r ∈ g.sources, ¬ target r)
    (s : State Reg) :
    run words s = xorState s (injectionVector target words s) := by
  funext r
  by_cases hr : target r
  · simpa only [xorState, injectionVector, if_pos hr] using
      (target_identity target words hreads s r hr)
  · simpa only [xorState, injectionVector, if_neg hr, Bool.xor_false] using
      (run_off_target target words hwrites s r hr)

private theorem erase_targets_preserved (entrance : List (Gate Reg))
    (hwrites : ∀ g ∈ entrance, target g.dst) (s : State Reg) :
    eraseTargets target (run entrance s) = eraseTargets target s :=
  erased_eq_of_agree_off_target target (run entrance s) s
    (fun r hr => run_off_target target entrance hwrites s r hr)

private theorem injection_vector_preserved
    (words entrance : List (Gate Reg))
    (hwrites : ∀ g ∈ entrance, target g.dst) (s : State Reg) :
    injectionVector target words (run entrance s) =
      injectionVector target words s := by
  funext r
  unfold injectionVector
  rw [erase_targets_preserved target entrance hwrites s]

/-- Complete restored-basis word equals the original injection word.
No cleanliness is assumed. Final source/helper preservation follows for every
coordinate outside target. Literal matrix and source binding remain premises. -/
theorem conjugated_word_injection
    (entrance original encoded : List (Gate Reg))
    (hself : ∀ g ∈ entrance, g.dst ∉ g.sources)
    (hentrance : ∀ g ∈ entrance, target g.dst)
    (horiginal_writes : ∀ g ∈ original, target g.dst)
    (horiginal_reads : ∀ g ∈ original, ∀ r ∈ g.sources, ¬ target r)
    (hencoded_writes : ∀ g ∈ encoded, target g.dst)
    (hencoded_reads : ∀ g ∈ encoded, ∀ r ∈ g.sources, ¬ target r)
    (hencoded : ∀ s, injectionVector target encoded s =
      run entrance (injectionVector target original s))
    (s : State Reg) :
    run (entrance ++ encoded ++ entrance.reverse) s = run original s ∧
      ∀ r, ¬ target r →
        run (entrance ++ encoded ++ entrance.reverse) s r = s r := by
  have hword : run (entrance ++ encoded ++ entrance.reverse) s =
      run entrance.reverse
        (xorState (run entrance s) (injectionVector target encoded s)) := by
    rw [BitXorReversal.run_append, BitXorReversal.run_append]
    rw [injection_execution target encoded hencoded_writes hencoded_reads]
    rw [injection_vector_preserved target encoded entrance hentrance s]
  have hc := BitXorConjugacy.conjugated_target_injection target entrance hself
    (injectionVector target original) (injectionVector target encoded) hencoded
    (fun t r hr => injection_vector_support target original t r hr) s s
  constructor
  · calc
      run (entrance ++ encoded ++ entrance.reverse) s =
          run entrance.reverse
            (xorState (run entrance s) (injectionVector target encoded s)) := hword
      _ = xorState s (injectionVector target original s) := hc.1
      _ = run original s :=
        (injection_execution target original horiginal_writes horiginal_reads s).symm
  · intro r hr
    rw [hword]
    exact hc.2 r hr

end CurrentMain.BitXorInjectionAdapter
#print axioms CurrentMain.BitXorInjectionAdapter.injection_execution
#print axioms CurrentMain.BitXorInjectionAdapter.conjugated_word_injection
