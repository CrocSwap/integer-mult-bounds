import AdmissibleTypedTape
import Init.Data.List.Nat.TakeDrop

/-!
Reusable lifting from actual per-phase instruction prefixes to every prefix of
an indexed tape's concatenated instruction code. Local admissible-domain closure
and an explicit per-operation predicate are propagated in chronological order.
The initial observed predicate and each actual phase-prefix bound are explicit;
no whole lowered-tape endpoint, whole-prefix bound or local inverse is assumed.
Empty codes and arbitrary prefix lengths are included. A client supplies its
actual interpreter append law, phase code and local implementation facts.
James Chang with OpenAI assistance; Apache-2.0. Reuses AdmissibleTypedTape and
Lean's list prefix identities. Pinned conditional context only:
kappa=836330098538459/500000000000000000. Uncompiled candidate.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.TypedCodePrefix
universe u v w x
open AdmissibleTypedTape
variable {Label : Type u} {Op : Label → Label → Type v} {Instruction : Type w}
variable {State : Type x}

def lower (code : ∀ {a b : Label}, Op a b → List Instruction) :
    ∀ {a b : Label}, Tape Op a b → List Instruction
  | _, _, .nil _ => []
  | _, _, .cons op tail => code op ++ lower code tail

/-- Only instructions actually present in the finite typed tape need suppliers. -/
def Every (Allowed : ∀ {a b : Label}, Op a b → Prop) :
    ∀ {a b : Label}, Tape Op a b → Prop
  | _, _, .nil _ => True
  | _, _, .cons op tail => Allowed op ∧ Every Allowed tail

theorem lower_append (code : ∀ {a b : Label}, Op a b → List Instruction)
    {a b : Label} (xs : Tape Op a b) : ∀ {c : Label} (ys : Tape Op b c),
    lower code (append xs ys) = lower code xs ++ lower code ys := by
  induction xs with
  | nil => intro c ys; rfl
  | cons op tail ih =>
      intro c ys
      simp only [append, lower, ih, List.append_assoc]

theorem every_append (Allowed : ∀ {a b : Label}, Op a b → Prop)
    {a b : Label} (xs : Tape Op a b) : ∀ {c : Label} (ys : Tape Op b c),
    Every Allowed (append xs ys) ↔ Every Allowed xs ∧ Every Allowed ys := by
  induction xs with
  | nil => intro c ys; simp only [append, Every, true_and]
  | cons op tail ih => intro c ys; simp only [append, Every, ih, and_assoc]

/-- An actual raw instruction prefix either lies in the head phase, or executes
that complete phase and continues from its proved admissible endpoint. -/
theorem instruction_prefix_lift
    (code : ∀ {a b : Label}, Op a b → List Instruction)
    (eval : List Instruction → State → State)
    (hnil : ∀ s, eval [] s = s)
    (happend : ∀ xs ys s, eval (xs ++ ys) s = eval ys (eval xs s))
    (D : Label → State → Prop) (Allowed : ∀ {a b : Label}, Op a b → Prop)
    (Q : State → Prop)
    (hclosed : ∀ {a b : Label} (op : Op a b), Allowed op →
      ∀ s, D a s → D b (eval (code op) s))
    (hlocal : ∀ {a b : Label} (op : Op a b), Allowed op →
      ∀ s, D a s → ∀ k, Q (eval ((code op).take k) s))
    {a b : Label} (tape : Tape Op a b) :
    ∀ k s, D a s → Q s → Every Allowed tape →
      Q (eval ((lower code tape).take k) s) := by
  induction tape with
  | nil => intro k s _hs hq _hall; simpa only [lower, List.take_nil, hnil] using hq
  | cons op tail ih =>
      intro k s hs hq hall
      change Allowed op ∧ Every Allowed tail at hall
      by_cases hk : k ≤ (code op).length
      · rw [lower, List.take_append_of_le_length hk]
        exact hlocal op hall.1 s hs k
      · have hlen : (code op).length ≤ k := Nat.le_of_lt (Nat.lt_of_not_ge hk)
        rw [lower, List.take_append_eq_append_take, List.take_of_length_le hlen, happend]
        have hq' : Q (eval (code op) s) := by
          simpa only [List.take_length] using hlocal op hall.1 s hs (code op).length
        exact ih (k - (code op).length) (eval (code op) s)
          (hclosed op hall.1 s hs) hq' hall.2

end CurrentMain.TypedCodePrefix
#print axioms CurrentMain.TypedCodePrefix.lower_append
#print axioms CurrentMain.TypedCodePrefix.every_append
#print axioms CurrentMain.TypedCodePrefix.instruction_prefix_lift
#check @CurrentMain.TypedCodePrefix.instruction_prefix_lift
