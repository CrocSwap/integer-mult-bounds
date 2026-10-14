import BitXorDisjointComposition

/-!
Exact row pullback for the accepted ordered XOR interpreter. This is a symbolic
list certificate, not a second execution semantics or an assumed matrix law.
An operand is expanded at each actual single update; both repeated operands
and self reads are retained. The source list may contain duplicates, so its
meaning is parity rather than set membership.

The intended finite client is all111 complete PR926 injection rows at immutable
0f216a345c37bc71cc0e22030ef11ec31b26a69e, retaining its PR915 parent and all192
helper shears. Concrete row data/checks and exhaustive target coverage are
separate. This generic source does not supply any selected singleton equation.
Credits: PR590/597 ordered interpreter, PR774 earlier compensation algebra,
Gareth Davidson/bitplane PR915/926 and PR926's Scott Woolsey Biggart PR733 credit.
Apache-2.0; OpenAI assistance. Uncompiled source proposal.
-/
namespace CurrentMain.BitXorRowPullback
open BitXor BitXorConjugacy BitXorInjectionAdapter BitXorDisjointComposition
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]

/-- Ordered donor parity; duplicate occurrences cancel by Boolean XOR. -/
def donorXor : List Reg → State Reg → Bool
  | [], _ => false
  | r :: rs, s => s r ^^ donorXor rs s

/-- Pull a row through one literal single-donor update. -/
def pullSingle (dst src : Reg) : List Reg → List Reg
  | [] => []
  | r :: rs =>
      if r = dst then r :: src :: pullSingle dst src rs
      else r :: pullSingle dst src rs

theorem pullSingle_sound (dst src : Reg) (row : List Reg) (s : State Reg) :
    donorXor (pullSingle dst src row) s = donorXor row (single dst src s) := by
  induction row with
  | nil => rfl
  | cons r rs ih =>
    by_cases hr : r = dst
    · subst r
      simp only [pullSingle, if_pos rfl, donorXor, ih, single, if_pos rfl, if_true]
      exact (Bool.xor_assoc _ _ _).symm
    · simp only [pullSingle, if_neg hr, donorXor, ih, single, if_neg hr]

/-- Pullbacks are composed in reverse chronological order. -/
def pullSources (dst : Reg) : List Reg → List Reg → List Reg
  | [], row => row
  | src :: rest, row => pullSingle dst src (pullSources dst rest row)

theorem pullSources_sound (dst : Reg) (sources row : List Reg) (s : State Reg) :
    donorXor (pullSources dst sources row) s =
      donorXor row (sourcesRun dst sources s) := by
  induction sources generalizing s with
  | nil => rfl
  | cons src rest ih =>
    rw [pullSources, pullSingle_sound, ih]
    rfl

def pullWord : List (Gate Reg) → List Reg → List Reg
  | [], row => row
  | g :: rest, row => pullSources g.dst g.sources (pullWord rest row)

theorem pullWord_sound (word : List (Gate Reg)) (row : List Reg) (s : State Reg) :
    donorXor (pullWord word row) s = donorXor row (run word s) := by
  induction word generalizing s with
  | nil => rfl
  | cons g rest ih =>
    rw [pullWord, pullSources_sound, ih]
    rfl

def offTarget (target : Reg → Prop) [DecidablePred target] : List Reg → List Reg
  | [] => []
  | r :: rs => if target r then offTarget target rs else r :: offTarget target rs

theorem offTarget_sound (target : Reg → Prop) [DecidablePred target]
    (row : List Reg) (s : State Reg) :
    donorXor (offTarget target row) s = donorXor row (eraseTargets target s) := by
  induction row with
  | nil => rfl
  | cons r rs ih =>
    by_cases hr : target r
    · simp only [offTarget, if_pos hr, donorXor, eraseTargets, if_pos hr,
        Bool.false_xor, ih]
    · simp only [offTarget, if_neg hr, donorXor, eraseTargets, if_neg hr, ih]

/-- An actual injection coordinate is represented by its pulled donor list.
No write/read restriction is needed for this identity: it follows directly
from the ordered interpreter and the actual eraseTargets definition. -/
theorem injection_coordinate (target : Reg → Prop) [DecidablePred target]
    (word : List (Gate Reg)) (s : State Reg) (q : Reg) (hq : target q) :
    injectionVector target word s q =
      donorXor (offTarget target (pullWord word [q])) s := by
  rw [offTarget_sound, pullWord_sound]
  simp only [injectionVector, if_pos hq, donorXor, Bool.xor_false]

/-- The same coordinate after an actual preparation has a second literal
pullback. Finite clients check the resulting donor parity on every basis bit. -/
theorem prepared_injection_coordinate (target : Reg → Prop) [DecidablePred target]
    (word entrance : List (Gate Reg)) (s : State Reg) (q : Reg) (hq : target q) :
    injectionVector target word (run entrance s) q =
      donorXor (pullWord entrance (offTarget target (pullWord word [q]))) s := by
  rw [pullWord_sound]
  exact injection_coordinate target word (run entrance s) q hq

end CurrentMain.BitXorRowPullback
#print axioms CurrentMain.BitXorRowPullback.pullWord_sound
#print axioms CurrentMain.BitXorRowPullback.injection_coordinate
#print axioms CurrentMain.BitXorRowPullback.prepared_injection_coordinate
