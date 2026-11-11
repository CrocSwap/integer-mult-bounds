import BitXorReversal

/-!
Literal-free XOR-linearity and restored-basis conjugacy for the existing ordered
Boolean interpreter. All incoming bits are arbitrary. The final preservation
conclusion uses an explicit support premise on the injected vector.

This does not identify a particular D word, helper projection, frame execution,
integer lift, positive bound, hosted invoice or multiplication theorem.
Source motivation: Gareth Davidson/bitplane PR915, tested mathematical head
7d5ef1dcf994d0542f2d302110b33780f5504ab7, publication head
e9daefe320a0043000bd9746664ed02c3287d056. Its attribution credits the
PR794/713/716/686 restored-basis and semantic-boundary lineage.
Reuses the PR590 ordered XOR interpreter and PR597 reversal theorem.
Apache-2.0; prepared with OpenAI assistance. Source proposal, not compiled.
-/
namespace CurrentMain.BitXorConjugacy
open BitXor
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]

def xorState (s t : State Reg) : State Reg :=
  fun r => s r ^^ t r

private theorem xor_interchange (a b c d : Bool) :
    ((a ^^ b) ^^ (c ^^ d)) = ((a ^^ c) ^^ (b ^^ d)) := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

private theorem single_xor (dst src : Reg) (s t : State Reg) :
    single dst src (xorState s t) =
      xorState (single dst src s) (single dst src t) := by
  funext r
  by_cases hr : r = dst
  · subst r
    simp only [single, xorState, if_pos rfl]
    exact xor_interchange (s dst) (t dst) (s src) (t src)
  · simp only [single, xorState, if_neg hr]

private theorem sourcesRun_xor (dst : Reg) (rs : List Reg)
    (s t : State Reg) :
    sourcesRun dst rs (xorState s t) =
      xorState (sourcesRun dst rs s) (sourcesRun dst rs t) := by
  induction rs generalizing s t with
  | nil => rfl
  | cons src rs ih =>
    change sourcesRun dst rs (single dst src (xorState s t)) =
      xorState (sourcesRun dst rs (single dst src s))
        (sourcesRun dst rs (single dst src t))
    rw [single_xor]
    exact ih (single dst src s) (single dst src t)

private theorem step_xor (g : Gate Reg) (s t : State Reg) :
    step g (xorState s t) = xorState (step g s) (step g t) :=
  sourcesRun_xor g.dst g.sources s t

/-- Linearity retains operand order and multiplicity, even with self reads.
No-self-read is needed for reversal, not for this identity. -/
theorem run_xor (gs : List (Gate Reg)) (s t : State Reg) :
    run gs (xorState s t) = xorState (run gs s) (run gs t) := by
  induction gs generalizing s t with
  | nil => rfl
  | cons g gs ih =>
    change run gs (step g (xorState s t)) =
      xorState (run gs (step g s)) (run gs (step g t))
    rw [step_xor]
    exact ih (step g s) (step g t)

/-- Restored-basis injection on arbitrary initial state. The helper parameter
is abstract; interpreting it as the actual incoming helper state requires a
separate source-bound adapter. Only the explicit hsupport premise gives final
preservation outside target. No intermediate preservation is asserted here. -/
theorem conjugated_target_injection {Helper : Type}
    (target : Reg → Prop) (gs : List (Gate Reg))
    (hself : ∀ g ∈ gs, g.dst ∉ g.sources)
    (K R : Helper → State Reg)
    (hencoded : ∀ h, R h = run gs (K h))
    (hsupport : ∀ h r, ¬ target r → K h r = false)
    (s : State Reg) (h : Helper) :
    run gs.reverse (xorState (run gs s) (R h)) = xorState s (K h) ∧
      ∀ r, ¬ target r →
        run gs.reverse (xorState (run gs s) (R h)) r = s r := by
  have heq : run gs.reverse (xorState (run gs s) (R h)) =
      xorState s (K h) := by
    calc
      run gs.reverse (xorState (run gs s) (R h)) =
          run gs.reverse (xorState (run gs s) (run gs (K h))) := by
            rw [hencoded h]
      _ = run gs.reverse (run gs (xorState s (K h))) :=
        congrArg (run gs.reverse) (run_xor gs s (K h)).symm
      _ = xorState s (K h) :=
        BitXorReversal.run_reverse_cancel gs hself (xorState s (K h))
  refine ⟨heq, ?_⟩
  intro r hr
  rw [heq]
  simp only [xorState, hsupport h r hr, Bool.xor_false]

end CurrentMain.BitXorConjugacy
#print axioms CurrentMain.BitXorConjugacy.run_xor
#print axioms CurrentMain.BitXorConjugacy.conjugated_target_injection
