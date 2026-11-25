import Current1094PrivateCentreHosting
import Lean.Elab.Tactic.Omega

/-!
Source-only routing projection for all 144 ordered selected PR1094 calls.
The exact archive has 224 consecutive data/target owners in each call:
896 * replica + 224 * pair + local register. The compact table below preserves
call-array order. Its source binding retains every complete call and owner hash.

This is a new uncompiled source. The only closed finite decision is the table
length. No finite helper uniqueness/exclusion decision or event replay is added.
The 480 borrowed owners remain arbitrary, with injection and exclusion of the
active data interval supplied explicitly. Those premises are not kernel results
of PR1553's source audit. A repeated family in different calls is allowed.

Only the existing tagged private-centre injection interface is reused. Numeric
address interpretation, actual route/chart projection, executor equality, dirty
input bounds, atomicity, chronological legality and precision remain separate.

Apache-2.0; prepared with OpenAI assistance. Selected artifact lineage: Rohan
Arun's PR1094 on Jeremy Kothe's T16, retaining Hao Yan and PR514/484/507 credits.
The all-call structural source binding reuses columbia-git's PR1553 audit with
OpenAI Codex assistance. Inherited realization is DreamingOfClouds with Claude
Opus 5.5 (Anthropic), via Claude Code. No new mechanism-priority claim is made.
-/
set_option Elab.async false

namespace CurrentMain.Current1094CallSequenceRouting

/-- Each pair is (replica, pair), in the exact emitted calls-array order. -/
def callPositions : List (Fin 16 × Fin 4) :=
  [
    (0, 0), (8, 0), (1, 0), (9, 0), (0, 0), (8, 0), (2, 0), (10, 0),
    (1, 0), (9, 0), (0, 0), (8, 0), (3, 0), (11, 0), (2, 0), (10, 0),
    (1, 0), (9, 0), (0, 1), (8, 1), (4, 0), (12, 0), (3, 0), (11, 0),
    (2, 0), (10, 0), (1, 1), (9, 1), (0, 1), (8, 1), (5, 0), (13, 0),
    (4, 0), (12, 0), (3, 0), (11, 0), (2, 1), (10, 1), (1, 1), (9, 1),
    (0, 2), (8, 2), (6, 0), (14, 0), (5, 0), (13, 0), (4, 0), (12, 0),
    (3, 1), (11, 1), (2, 1), (10, 1), (1, 2), (9, 2), (7, 0), (15, 0),
    (0, 2), (8, 2), (6, 0), (14, 0), (5, 0), (13, 0), (4, 1), (12, 1),
    (3, 1), (11, 1), (2, 2), (10, 2), (1, 2), (9, 2), (7, 0), (15, 0),
    (0, 3), (8, 3), (6, 0), (14, 0), (5, 1), (13, 1), (4, 1), (12, 1),
    (3, 2), (11, 2), (2, 2), (10, 2), (1, 3), (9, 3), (7, 0), (15, 0),
    (0, 3), (8, 3), (6, 1), (14, 1), (5, 1), (13, 1), (4, 2), (12, 2),
    (3, 2), (11, 2), (2, 3), (10, 3), (1, 3), (9, 3), (7, 1), (15, 1),
    (6, 1), (14, 1), (5, 2), (13, 2), (4, 2), (12, 2), (3, 3), (11, 3),
    (2, 3), (10, 3), (7, 1), (15, 1), (6, 2), (14, 2), (5, 2), (13, 2),
    (4, 3), (12, 3), (3, 3), (11, 3), (7, 2), (15, 2), (6, 2), (14, 2),
    (5, 3), (13, 3), (4, 3), (12, 3), (7, 2), (15, 2), (6, 3), (14, 3),
    (5, 3), (13, 3), (7, 3), (15, 3), (6, 3), (14, 3), (7, 3), (15, 3)
  ]

/-- Proposed finite length check; not yet run by a Lean kernel. -/
theorem callPositions_length : callPositions.length = 144 := by decide +kernel

def callPosition (c : Fin 144) : Fin 16 × Fin 4 :=
  callPositions[c.val]'(by simpa only [callPositions_length] using c.isLt)

def dataBase (c : Fin 144) : Nat :=
  896 * (callPosition c).1.val + 224 * (callPosition c).2.val

/-- No default lookup and no modulo reduction of family numbers. -/
def dataOwner (c : Fin 144) (i : Fin 224) : Fin 14336 :=
  ⟨dataBase c + i.val, by
    have hr := (callPosition c).1.isLt
    have hp := (callPosition c).2.isLt
    have hi := i.isLt
    dsimp only [dataBase]
    omega⟩

theorem dataOwner_range (c : Fin 144) (i : Fin 224) :
    dataBase c ≤ (dataOwner c i).val ∧
      (dataOwner c i).val < dataBase c + 224 := by
  have hi := i.isLt
  change dataBase c ≤ dataBase c + i.val ∧ dataBase c + i.val < dataBase c + 224
  omega

theorem dataOwner_injective (c : Fin 144) : Function.Injective (dataOwner c) := by
  intro i j hij
  apply Fin.ext
  have hv := congrArg Fin.val hij
  simp only [dataOwner] at hv
  omega

/-- The local register order is the 224 data/target roles followed by 480 helpers.
No claim is made that an arbitrary supplied borrowed map is the emitted map. -/
def ordinaryOwner (c : Fin 144) (borrowed : Fin 480 → Fin 14336)
    (i : Fin 704) : Fin 14336 :=
  if hi : i.val < 224 then dataOwner c ⟨i.val, hi⟩
  else borrowed ⟨i.val - 224, by have h := i.isLt; omega⟩

/-- Per-call helper injection and data-interval exclusion suffice. These are
explicit supplier obligations, not conclusions inferred from Python evidence. -/
theorem ordinaryOwner_injective (c : Fin 144) (borrowed : Fin 480 → Fin 14336)
    (hborrowed : Function.Injective borrowed)
    (houtside : ∀ h, (borrowed h).val < dataBase c ∨
      dataBase c + 224 ≤ (borrowed h).val) :
    Function.Injective (ordinaryOwner c borrowed) := by
  intro i j hij
  apply Fin.ext
  have hiBound := i.isLt
  have hjBound := j.isLt
  by_cases hi : i.val < 224
  · by_cases hj : j.val < 224
    · have hv := congrArg Fin.val hij
      simp only [ordinaryOwner, dif_pos hi, dif_pos hj, dataOwner] at hv
      omega
    · have ho := houtside ⟨j.val - 224, by omega⟩
      have hv := congrArg Fin.val hij
      simp only [ordinaryOwner, dif_pos hi, dif_neg hj, dataOwner] at hv
      omega
  · by_cases hj : j.val < 224
    · have ho := houtside ⟨i.val - 224, by omega⟩
      have hv := congrArg Fin.val hij
      simp only [ordinaryOwner, dif_neg hi, dif_pos hj, dataOwner] at hv
      omega
    · have hb : borrowed ⟨i.val - 224, by omega⟩ =
          borrowed ⟨j.val - 224, by omega⟩ := by
        simpa only [ordinaryOwner, dif_neg hi, dif_neg hj] using hij
      have hv := congrArg Fin.val (hborrowed hb)
      change i.val - 224 = j.val - 224 at hv
      omega

/-- Reuse the existing ordinary/private namespace join; no global family
disjointness between separate calls or interpretation of all scratch is claimed. -/
theorem declared_family_injective (c : Fin 144) (borrowed : Fin 480 → Fin 14336)
    (hborrowed : Function.Injective borrowed)
    (houtside : ∀ h, (borrowed h).val < dataBase c ∨
      dataBase c + 224 ≤ (borrowed h).val) :
    Function.Injective
      (Current1094PrivateCentreHosting.declaredFamily (ordinaryOwner c borrowed)) :=
  Current1094PrivateCentreHosting.declaredFamily_injective (ordinaryOwner c borrowed)
    (ordinaryOwner_injective c borrowed hborrowed houtside)

end CurrentMain.Current1094CallSequenceRouting

#print axioms CurrentMain.Current1094CallSequenceRouting.callPositions_length
#print axioms CurrentMain.Current1094CallSequenceRouting.dataOwner_range
#print axioms CurrentMain.Current1094CallSequenceRouting.dataOwner_injective
#print axioms CurrentMain.Current1094CallSequenceRouting.ordinaryOwner_injective
#print axioms CurrentMain.Current1094CallSequenceRouting.declared_family_injective
