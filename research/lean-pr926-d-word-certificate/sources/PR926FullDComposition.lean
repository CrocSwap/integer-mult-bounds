import PR926InjectionJoinSupport
import PR926FullInjectionRow000Normalized
import PR926FullInjectionRow001Normalized
import PR926FullInjectionRow002Normalized
import PR926FullInjectionRow003Normalized
import PR926FullInjectionRow004Normalized
import PR926FullInjectionRow005Normalized
import PR926FullInjectionRow006Normalized
import PR926FullInjectionRow007Normalized
import PR926FullInjectionRow008Normalized
import PR926FullInjectionRow009Normalized
import PR926FullInjectionRow010Normalized
import PR926FullInjectionRow011Normalized
import PR926FullInjectionRow012Normalized
import PR926FullInjectionRow013Normalized
import PR926FullInjectionRow014Normalized
import PR926FullInjectionRow015Normalized
import PR926FullInjectionRow016Normalized
import PR926FullInjectionRow017Normalized
import PR926FullInjectionRow018Normalized
import PR926FullInjectionRow019Normalized
import PR926FullInjectionRow020Normalized
import PR926FullInjectionRow021Normalized
import PR926FullInjectionRow022Normalized
import PR926FullInjectionRow023Normalized
import PR926FullInjectionRow024Normalized
import PR926FullInjectionRow025Normalized
import PR926FullInjectionRow026Normalized
import PR926FullInjectionRow027Normalized
import PR926FullInjectionRow028Normalized
import PR926FullInjectionRow029Normalized
import PR926FullInjectionRow030Normalized
import PR926FullInjectionRow031Normalized
import PR926FullInjectionRow032Normalized
import PR926FullInjectionRow033Normalized
import PR926FullInjectionRow034Normalized
import PR926FullInjectionRow035Normalized
import PR926FullInjectionRow036Normalized
import PR926FullInjectionRow037Normalized
import PR926FullInjectionRow038Normalized
import PR926FullInjectionRow039Normalized
import PR926FullInjectionRow040Normalized
import PR926FullInjectionRow041Normalized
import PR926FullInjectionRow042Normalized
import PR926FullInjectionRow043Normalized
import PR926FullInjectionRow044Normalized
import PR926FullInjectionRow045Normalized
import PR926FullInjectionRow046Normalized
import PR926FullInjectionRow047Normalized
import PR926FullInjectionRow048Normalized
import PR926FullInjectionRow049Normalized
import PR926FullInjectionRow050Normalized
import PR926FullInjectionRow051Normalized
import PR926FullInjectionRow052Normalized
import PR926FullInjectionRow053Normalized
import PR926FullInjectionRow054Normalized
import PR926FullInjectionRow055Normalized
import PR926FullInjectionRow056Normalized
import PR926FullInjectionRow057Normalized
import PR926FullInjectionRow058Normalized
import PR926FullInjectionRow059Normalized
import PR926FullInjectionRow060Normalized
import PR926FullInjectionRow061Normalized
import PR926FullInjectionRow062Normalized
import PR926FullInjectionRow063Normalized
import PR926FullInjectionRow064Normalized
import PR926FullInjectionRow065Normalized
import PR926FullInjectionRow066Normalized
import PR926FullInjectionRow067Normalized
import PR926FullInjectionRow068Normalized
import PR926FullInjectionRow069Normalized
import PR926FullInjectionRow070Normalized
import PR926FullInjectionRow071Normalized
import PR926FullInjectionRow072Normalized
import PR926FullInjectionRow073Normalized
import PR926FullInjectionRow074Normalized
import PR926FullInjectionRow075Normalized
import PR926FullInjectionRow076Normalized
import PR926FullInjectionRow077Normalized
import PR926FullInjectionRow078Normalized
import PR926FullInjectionRow079Normalized
import PR926FullInjectionRow080Normalized
import PR926FullInjectionRow081Normalized
import PR926FullInjectionRow082Normalized
import PR926FullInjectionRow083Normalized
import PR926FullInjectionRow084Normalized
import PR926FullInjectionRow085Normalized
import PR926FullInjectionRow086Normalized
import PR926FullInjectionRow087Normalized
import PR926FullInjectionRow088Normalized
import PR926FullInjectionRow089Normalized
import PR926FullInjectionRow090Normalized
import PR926FullInjectionRow091Normalized
import PR926FullInjectionRow092Normalized
import PR926FullInjectionRow093Normalized
import PR926FullInjectionRow094Normalized
import PR926FullInjectionRow095Normalized
import PR926FullInjectionRow096Normalized
import PR926FullInjectionRow097Normalized
import PR926FullInjectionRow098Normalized
import PR926FullInjectionRow099Normalized
import PR926FullInjectionRow100Normalized
import PR926FullInjectionRow101Normalized
import PR926FullInjectionRow102Normalized
import PR926FullInjectionRow103Normalized
import PR926FullInjectionRow104Normalized
import PR926FullInjectionRow105Normalized
import PR926FullInjectionRow106Normalized
import PR926FullInjectionRow107Normalized
import PR926FullInjectionRow108Normalized
import PR926FullInjectionRow109Normalized
import PR926FullInjectionRow110Normalized

/-!
Proposed exhaustive source-bound row join for historical PR9260f216a34 and
its PR915e9daefe3 parent. Every one of111 actual target rows is imported once.
Nested Fin.cases covers all target indices without a new literal decision.
The complete Fin661 basis coverage and arbitrary dirty-state lifting reuse the
accepted generic theorem through the concrete join-support interface.

This file is uncompiled and depends on every listed row certificate; missing
objects or unaccepted rows cannot be treated as completed coverage. It supplies
only the ordered Boolean D-word equality and off-target restoration. Physical
frame operators, integer lift, precision, selected-current adoption and the
whole multiplication theorem remain separate. Gareth Davidson/bitplane
PR915/926, PR733, PR590/597 and PR774 attribution is retained by imports.
Apache-2.0; OpenAI assistance.
-/
namespace CurrentMain.PR926FullDComposition
open BitXor BitXorFiniteBasis BitXorInjectionAdapter PR926PreparationSupport
open PR926FullInjectionRows PR926InjectionJoinSupport
set_option Elab.async false

/-- Every one of111 actual target coordinates, for every input singleton. -/
theorem all_rows (i : Fin 111) (r : Reg) :
    injectionVector target encoded (run helpers (basisState r))
        (⟨111 + i.val, by have := i.isLt; omega⟩ : Reg) =
      injectionVector target original (basisState r)
        (⟨111 + i.val, by have := i.isLt; omega⟩ : Reg) := by
  exact (Fin.cases (motive := fun j : Fin 111 => ∀ x : Reg,
      injectionVector target encoded (run helpers (basisState x))
          (⟨111 + j.val, by have := j.isLt; omega⟩ : Reg) =
        injectionVector target original (basisState x)
          (⟨111 + j.val, by have := j.isLt; omega⟩ : Reg))
    PR926FullInjectionRow000Normalized.row000_basis
    (Fin.cases PR926FullInjectionRow001Normalized.row001_basis
    (Fin.cases PR926FullInjectionRow002Normalized.row002_basis
    (Fin.cases PR926FullInjectionRow003Normalized.row003_basis
    (Fin.cases PR926FullInjectionRow004Normalized.row004_basis
    (Fin.cases PR926FullInjectionRow005Normalized.row005_basis
    (Fin.cases PR926FullInjectionRow006Normalized.row006_basis
    (Fin.cases PR926FullInjectionRow007Normalized.row007_basis
    (Fin.cases PR926FullInjectionRow008Normalized.row008_basis
    (Fin.cases PR926FullInjectionRow009Normalized.row009_basis
    (Fin.cases PR926FullInjectionRow010Normalized.row010_basis
    (Fin.cases PR926FullInjectionRow011Normalized.row011_basis
    (Fin.cases PR926FullInjectionRow012Normalized.row012_basis
    (Fin.cases PR926FullInjectionRow013Normalized.row013_basis
    (Fin.cases PR926FullInjectionRow014Normalized.row014_basis
    (Fin.cases PR926FullInjectionRow015Normalized.row015_basis
    (Fin.cases PR926FullInjectionRow016Normalized.row016_basis
    (Fin.cases PR926FullInjectionRow017Normalized.row017_basis
    (Fin.cases PR926FullInjectionRow018Normalized.row018_basis
    (Fin.cases PR926FullInjectionRow019Normalized.row019_basis
    (Fin.cases PR926FullInjectionRow020Normalized.row020_basis
    (Fin.cases PR926FullInjectionRow021Normalized.row021_basis
    (Fin.cases PR926FullInjectionRow022Normalized.row022_basis
    (Fin.cases PR926FullInjectionRow023Normalized.row023_basis
    (Fin.cases PR926FullInjectionRow024Normalized.row024_basis
    (Fin.cases PR926FullInjectionRow025Normalized.row025_basis
    (Fin.cases PR926FullInjectionRow026Normalized.row026_basis
    (Fin.cases PR926FullInjectionRow027Normalized.row027_basis
    (Fin.cases PR926FullInjectionRow028Normalized.row028_basis
    (Fin.cases PR926FullInjectionRow029Normalized.row029_basis
    (Fin.cases PR926FullInjectionRow030Normalized.row030_basis
    (Fin.cases PR926FullInjectionRow031Normalized.row031_basis
    (Fin.cases PR926FullInjectionRow032Normalized.row032_basis
    (Fin.cases PR926FullInjectionRow033Normalized.row033_basis
    (Fin.cases PR926FullInjectionRow034Normalized.row034_basis
    (Fin.cases PR926FullInjectionRow035Normalized.row035_basis
    (Fin.cases PR926FullInjectionRow036Normalized.row036_basis
    (Fin.cases PR926FullInjectionRow037Normalized.row037_basis
    (Fin.cases PR926FullInjectionRow038Normalized.row038_basis
    (Fin.cases PR926FullInjectionRow039Normalized.row039_basis
    (Fin.cases PR926FullInjectionRow040Normalized.row040_basis
    (Fin.cases PR926FullInjectionRow041Normalized.row041_basis
    (Fin.cases PR926FullInjectionRow042Normalized.row042_basis
    (Fin.cases PR926FullInjectionRow043Normalized.row043_basis
    (Fin.cases PR926FullInjectionRow044Normalized.row044_basis
    (Fin.cases PR926FullInjectionRow045Normalized.row045_basis
    (Fin.cases PR926FullInjectionRow046Normalized.row046_basis
    (Fin.cases PR926FullInjectionRow047Normalized.row047_basis
    (Fin.cases PR926FullInjectionRow048Normalized.row048_basis
    (Fin.cases PR926FullInjectionRow049Normalized.row049_basis
    (Fin.cases PR926FullInjectionRow050Normalized.row050_basis
    (Fin.cases PR926FullInjectionRow051Normalized.row051_basis
    (Fin.cases PR926FullInjectionRow052Normalized.row052_basis
    (Fin.cases PR926FullInjectionRow053Normalized.row053_basis
    (Fin.cases PR926FullInjectionRow054Normalized.row054_basis
    (Fin.cases PR926FullInjectionRow055Normalized.row055_basis
    (Fin.cases PR926FullInjectionRow056Normalized.row056_basis
    (Fin.cases PR926FullInjectionRow057Normalized.row057_basis
    (Fin.cases PR926FullInjectionRow058Normalized.row058_basis
    (Fin.cases PR926FullInjectionRow059Normalized.row059_basis
    (Fin.cases PR926FullInjectionRow060Normalized.row060_basis
    (Fin.cases PR926FullInjectionRow061Normalized.row061_basis
    (Fin.cases PR926FullInjectionRow062Normalized.row062_basis
    (Fin.cases PR926FullInjectionRow063Normalized.row063_basis
    (Fin.cases PR926FullInjectionRow064Normalized.row064_basis
    (Fin.cases PR926FullInjectionRow065Normalized.row065_basis
    (Fin.cases PR926FullInjectionRow066Normalized.row066_basis
    (Fin.cases PR926FullInjectionRow067Normalized.row067_basis
    (Fin.cases PR926FullInjectionRow068Normalized.row068_basis
    (Fin.cases PR926FullInjectionRow069Normalized.row069_basis
    (Fin.cases PR926FullInjectionRow070Normalized.row070_basis
    (Fin.cases PR926FullInjectionRow071Normalized.row071_basis
    (Fin.cases PR926FullInjectionRow072Normalized.row072_basis
    (Fin.cases PR926FullInjectionRow073Normalized.row073_basis
    (Fin.cases PR926FullInjectionRow074Normalized.row074_basis
    (Fin.cases PR926FullInjectionRow075Normalized.row075_basis
    (Fin.cases PR926FullInjectionRow076Normalized.row076_basis
    (Fin.cases PR926FullInjectionRow077Normalized.row077_basis
    (Fin.cases PR926FullInjectionRow078Normalized.row078_basis
    (Fin.cases PR926FullInjectionRow079Normalized.row079_basis
    (Fin.cases PR926FullInjectionRow080Normalized.row080_basis
    (Fin.cases PR926FullInjectionRow081Normalized.row081_basis
    (Fin.cases PR926FullInjectionRow082Normalized.row082_basis
    (Fin.cases PR926FullInjectionRow083Normalized.row083_basis
    (Fin.cases PR926FullInjectionRow084Normalized.row084_basis
    (Fin.cases PR926FullInjectionRow085Normalized.row085_basis
    (Fin.cases PR926FullInjectionRow086Normalized.row086_basis
    (Fin.cases PR926FullInjectionRow087Normalized.row087_basis
    (Fin.cases PR926FullInjectionRow088Normalized.row088_basis
    (Fin.cases PR926FullInjectionRow089Normalized.row089_basis
    (Fin.cases PR926FullInjectionRow090Normalized.row090_basis
    (Fin.cases PR926FullInjectionRow091Normalized.row091_basis
    (Fin.cases PR926FullInjectionRow092Normalized.row092_basis
    (Fin.cases PR926FullInjectionRow093Normalized.row093_basis
    (Fin.cases PR926FullInjectionRow094Normalized.row094_basis
    (Fin.cases PR926FullInjectionRow095Normalized.row095_basis
    (Fin.cases PR926FullInjectionRow096Normalized.row096_basis
    (Fin.cases PR926FullInjectionRow097Normalized.row097_basis
    (Fin.cases PR926FullInjectionRow098Normalized.row098_basis
    (Fin.cases PR926FullInjectionRow099Normalized.row099_basis
    (Fin.cases PR926FullInjectionRow100Normalized.row100_basis
    (Fin.cases PR926FullInjectionRow101Normalized.row101_basis
    (Fin.cases PR926FullInjectionRow102Normalized.row102_basis
    (Fin.cases PR926FullInjectionRow103Normalized.row103_basis
    (Fin.cases PR926FullInjectionRow104Normalized.row104_basis
    (Fin.cases PR926FullInjectionRow105Normalized.row105_basis
    (Fin.cases PR926FullInjectionRow106Normalized.row106_basis
    (Fin.cases PR926FullInjectionRow107Normalized.row107_basis
    (Fin.cases PR926FullInjectionRow108Normalized.row108_basis
    (Fin.cases PR926FullInjectionRow109Normalized.row109_basis
    (Fin.cases PR926FullInjectionRow110Normalized.row110_basis
    (fun z => Fin.elim0 z)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))) i r

/-- Exact scalar full D composition on arbitrary661 incoming bits. -/
theorem full_D (s : State Reg) :
    run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s =
      run (preparation ++ original ++ preparation.reverse) s ∧
    ∀ r, ¬ target r →
      run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s r =
        s r :=
  full_D_of_rows all_rows s

end CurrentMain.PR926FullDComposition
#print axioms CurrentMain.PR926FullDComposition.all_rows
#print axioms CurrentMain.PR926FullDComposition.full_D
