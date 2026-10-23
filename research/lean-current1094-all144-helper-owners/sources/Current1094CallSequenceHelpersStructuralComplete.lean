import Current1094HelperRowsBlock000
import Current1094HelperRowsBlock001
import Current1094HelperRowsBlock002
import Current1094HelperRowsBlock003
import Current1094HelperRowsBlock004
import Current1094HelperRowsBlock005
import Current1094HelperRowsBlock006
import Current1094HelperRowsBlock007
import Current1094HelperRowsBlock008
import Current1094HelperRowsBlock009
import Current1094HelperRowsBlock010
import Current1094HelperRowsBlock011
import Current1094HelperRowsBlock012
import Current1094HelperRowsBlock013
import Current1094HelperRowsBlock014
import Current1094HelperRowsBlock015
import Current1094HelperRowsBlock016
import Current1094HelperRowsBlock017
import Current1094HelperRowsBlock018
import Current1094HelperRowsBlock019
import Current1094HelperRowsBlock020
import Current1094HelperRowsBlock021
import Current1094HelperRowsBlock022
import Current1094HelperRowsBlock023
import Current1094HelperRowsBlock024
import Current1094HelperRowsBlock025
import Current1094HelperRowsBlock026
import Current1094HelperRowsBlock027
import Current1094HelperRowsBlock028
import Current1094HelperRowsBlock029
import Current1094HelperRowsBlock030
import Current1094HelperRowsBlock031
import Current1094HelperRowsBlock032
import Current1094HelperRowsBlock033
import Current1094HelperRowsBlock034
import Current1094HelperRowsBlock035

/-!
Exhaustive selected PR1094 owner certificate from all36 exact four-row blocks.
Every imported block theorem is required. Fin.cases closes every Fin36 branch,
and the accepted div/mod interface covers all Fin144 calls. No placeholder,
default theorem, skipped row, whole-array decision or external oracle is used.
The original-order RowOK/injection/exclusion/Hosting consequence below is copied
byte-for-byte from the preserved monolithic structural candidate.

Selected source context kappa=836330098538459/500000000000000000.
Physical address/chart projection, actual execution and precision stay separate.
Preserve Rohan Arun PR1094, Jeremy Kothe T16, Hao Yan PR514/484/507,
columbia-git PR1553, DreamingOfClouds realization and Lean library credits.
Apache-2.0; OpenAI assistance. Source preparation; missing compiled blocks are
prerequisites, not assumed successful by this final source.
-/
set_option Elab.async false
namespace CurrentMain.Current1094CallSequenceHelpersStructural
open Current1094CallSequenceRouting

private theorem all_blocks_checked : ∀ block : Fin 36, ∀ offset : Fin 4,
    SortedRowOK (blockRow block offset) :=
  (Fin.cases block000_checked (Fin.cases block001_checked (Fin.cases block002_checked (Fin.cases block003_checked (Fin.cases block004_checked (Fin.cases block005_checked (Fin.cases block006_checked (Fin.cases block007_checked (Fin.cases block008_checked (Fin.cases block009_checked (Fin.cases block010_checked (Fin.cases block011_checked (Fin.cases block012_checked (Fin.cases block013_checked (Fin.cases block014_checked (Fin.cases block015_checked (Fin.cases block016_checked (Fin.cases block017_checked (Fin.cases block018_checked (Fin.cases block019_checked (Fin.cases block020_checked (Fin.cases block021_checked (Fin.cases block022_checked (Fin.cases block023_checked (Fin.cases block024_checked (Fin.cases block025_checked (Fin.cases block026_checked (Fin.cases block027_checked (Fin.cases block028_checked (Fin.cases block029_checked (Fin.cases block030_checked (Fin.cases block031_checked (Fin.cases block032_checked (Fin.cases block033_checked (Fin.cases block034_checked (Fin.cases block035_checked (fun z => Fin.elim0 z)))))))))))))))))))))))))))))))))))))

private theorem sorted_rows_checked : ∀ c : Fin 144, SortedRowOK c :=
  sorted_all_of_blocks all_blocks_checked

/-- Recover exactly the original RowOK contract without its quadratic decision.
The structural permutation theorem returns Nodup in original register order. -/
theorem all_rows_certified (c : Fin 144) : RowOK c := by
  obtain ⟨hlen, hrange, hsorted, houtside⟩ := sorted_rows_checked c
  exact ⟨hlen, hrange,
    StructuralOwnerCertificate.nodup_of_structural_scan (helperNats c) hsorted, houtside⟩

theorem helper_length (c : Fin 144) : (helperNats c).length = 480 :=
  (all_rows_certified c).1

/-- Bounds are carried by a proof, so no Fin numeral coercion can wrap an owner. -/
def borrowedOwner (c : Fin 144) (h : Fin 480) : Fin 14336 :=
  ⟨(helperNats c)[h.val]'(by simpa only [helper_length] using h.isLt),
    (all_rows_certified c).2.1 _ (List.getElem_mem _)⟩

theorem borrowedOwner_injective (c : Fin 144) : Function.Injective (borrowedOwner c) := by
  intro i j hij
  apply Fin.ext
  apply List.getElem?_inj (xs := helperNats c)
    (by simpa only [helper_length] using i.isLt) (all_rows_certified c).2.2.1
  rw [List.getElem?_eq_getElem (by simpa only [helper_length] using i.isLt),
    List.getElem?_eq_getElem (by simpa only [helper_length] using j.isLt)]
  exact congrArg some (congrArg Fin.val hij)

theorem borrowedOwner_outside (c : Fin 144) (h : Fin 480) :
    (borrowedOwner c h).val < dataBase c ∨
      dataBase c + 224 ≤ (borrowedOwner c h).val :=
  (all_rows_certified c).2.2.2 _ (List.getElem_mem _)

def selectedOrdinaryOwner (c : Fin 144) : Fin 704 → Fin 14336 :=
  ordinaryOwner c (borrowedOwner c)

theorem selectedOrdinaryOwner_injective (c : Fin 144) :
    Function.Injective (selectedOrdinaryOwner c) :=
  ordinaryOwner_injective c (borrowedOwner c) (borrowedOwner_injective c)
    (borrowedOwner_outside c)

theorem selectedDeclaredFamily_injective (c : Fin 144) :
    Function.Injective
      (Current1094PrivateCentreHosting.declaredFamily (selectedOrdinaryOwner c)) :=
  declared_family_injective c (borrowedOwner c) (borrowedOwner_injective c)
    (borrowedOwner_outside c)

end CurrentMain.Current1094CallSequenceHelpersStructural

#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.all_rows_certified
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.borrowedOwner_injective
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.borrowedOwner_outside
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.selectedOrdinaryOwner_injective
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.selectedDeclaredFamily_injective
