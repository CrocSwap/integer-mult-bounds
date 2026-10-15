import BitXorInjectionAdapter

/-!
State-dependent restored-basis injection adapter.
Unlike the one-sided interface, the entrance may change helper registers.
The encoded contribution is evaluated at the actual post-entrance state.
The source-specific equality in hencoded is explicit and must be proved for
any concrete matrix/word. No precision or physical hosting claim is made.

Motivation: PR915 at e9daefe320a0043000bd9746664ed02c3287d056 and
the two-sided PR926 candidate at 0f216a345c37bc71cc0e22030ef11ec31b26a69e,
including its credit to Scott Woolsey Biggart's PR733 two-sided method.
Reuses the PR590 ordered interpreter, PR597 reversal and the accepted
BitXorConjugacy/BitXorInjectionAdapter APIs. The underlying conjugacy
algebra also appears in Anthony (@anthonylei)'s PR774 unary interpreter.
Apache-2.0; prepared with OpenAI assistance. Uncompiled source proposal.
-/
namespace CurrentMain.BitXorTwoSidedInjectionAdapter
open BitXor BitXorConjugacy BitXorInjectionAdapter
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]
variable (target : Reg → Prop) [DecidablePred target]

/-- Restore any reversible entrance after an actual encoded injection.
The entrance may write helpers. Arbitrary incoming target/helper values are
allowed; the substantive encoded-vector identity is evaluated after entrance.
Only the original injection's target support supplies final helper preservation. -/
theorem conjugated_word_injection
    (entrance original encoded : List (Gate Reg))
    (hself : ∀ g ∈ entrance, g.dst ∉ g.sources)
    (horiginal_writes : ∀ g ∈ original, target g.dst)
    (horiginal_reads : ∀ g ∈ original, ∀ r ∈ g.sources, ¬ target r)
    (hencoded_writes : ∀ g ∈ encoded, target g.dst)
    (hencoded_reads : ∀ g ∈ encoded, ∀ r ∈ g.sources, ¬ target r)
    (hencoded : ∀ s,
      injectionVector target encoded (run entrance s) =
        run entrance (injectionVector target original s))
    (s : State Reg) :
    run (entrance ++ encoded ++ entrance.reverse) s = run original s ∧
      ∀ r, ¬ target r →
        run (entrance ++ encoded ++ entrance.reverse) s r = s r := by
  have hword : run (entrance ++ encoded ++ entrance.reverse) s =
      run entrance.reverse
        (xorState (run entrance s)
          (injectionVector target encoded (run entrance s))) := by
    rw [BitXorReversal.run_append, BitXorReversal.run_append]
    rw [injection_execution target encoded hencoded_writes hencoded_reads]
  have hc := BitXorConjugacy.conjugated_target_injection target entrance hself
    (injectionVector target original)
    (fun t => injectionVector target encoded (run entrance t)) hencoded
    (fun t r hr => by simp only [injectionVector, if_neg hr]) s s
  constructor
  · calc
      run (entrance ++ encoded ++ entrance.reverse) s =
          run entrance.reverse
            (xorState (run entrance s)
              (injectionVector target encoded (run entrance s))) := hword
      _ = xorState s (injectionVector target original s) := hc.1
      _ = run original s :=
        (injection_execution target original horiginal_writes horiginal_reads s).symm
  · intro r hr
    rw [hword]
    exact hc.2 r hr

end CurrentMain.BitXorTwoSidedInjectionAdapter
#print axioms CurrentMain.BitXorTwoSidedInjectionAdapter.conjugated_word_injection
