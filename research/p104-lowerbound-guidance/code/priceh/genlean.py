# emit Nov15/PriceHInst.lean data+instances from mol_h{h}.json (verified first by verify.py)
import json, sys
outf=sys.argv[1]; hs=[int(x) for x in sys.argv[2:]]
out=["""/-
%s (lane PRICEH, Nov 20).  Molecule certificates (cards/WILD/NOVEL/priceh/mol_h*.json, gen.py; Fractions-verified by verify.py)
as MolData h for label ranks h in %s, each field checked by decide+kernel; `md<h>` : MolData h (instances of PriceHRung.rung_port_h).
Kernel only.
-/
import Nov15.PriceH
import Mathlib.Tactic.IntervalCases

set_option maxRecDepth 100000
set_option linter.unusedVariables false

namespace PriceH
open BankNC0
""" % (outf, hs)]
for h in hs:
    d=json.load(open(f'mol_h{h}.json'))
    mol=d['mol']
    Ds=[0]+[mol[str(L)]['D'] for L in range(1,h)]
    Es=[0]+[mol[str(L)]['E'] for L in range(1,h)]
    Ws=[[]]+[[tuple(x) for x in mol[str(L)]['W']] for L in range(1,h)]
    out.append(f"def molD{h} : ℕ → ℕ := fun L => ({Ds}:List ℕ).getD L 0")
    out.append(f"def molE{h} : ℕ → ℕ := fun L => ({Es}:List ℕ).getD L 0")
    wl='['+', '.join('['+', '.join('(%d, %d)'%(a,b) for a,b in W)+']' for W in Ws)+']'
    out.append(f"def molW{h} : ℕ → List (ℕ × ℕ) := fun L => ({wl} : List (List (ℕ × ℕ))).getD L []")
    per=[]
    for L in range(1,h):
        per.append(f"theorem hdec{h}_{L} : ∀ i, i ≤ {h} → ∀ j, j ≤ {h} →\n    decVal (molW{h} {L}) i j = molD{h} {L} * min {L} (dh i j) + molE{h} {L} * min 1 (dh i j) := by decide +kernel")
    out.append("\n".join(per))
    alts=", ".join(f"hdec{h}_{L}" for L in range(1,h))
    out.append(f"""theorem hD{h} : ∀ L, L ≤ {h} - 1 → 1 ≤ L → 0 < molD{h} L := by decide +kernel
theorem hdec{h} : ∀ L, L ≤ {h} - 1 → 1 ≤ L → ∀ i, i ≤ {h} → ∀ j, j ≤ {h} →
    decVal (molW{h} L) i j = molD{h} L * min L (dh i j) + molE{h} L * min 1 (dh i j) := by
  intro L h2 h1
  have h2' : L ≤ {h-1} := h2
  interval_cases L
  exacts [{alts}]
theorem hsep{h} : ∀ L, L ≤ {h} - 2 → 1 ≤ L → molD{h} L + molE{h} L ≤ 2 * sepValH {h} (molW{h} L) := by decide +kernel
/-- the molecule certificate at label rank {h} -/
def md{h} : MolData {h} :=
  ⟨molD{h}, molE{h}, molW{h}, hD{h}, hdec{h}, hsep{h}, by decide +kernel, by decide +kernel⟩
""")
out.append("end PriceH\n")
open('<research-tree>/lean/decoder-duality/Nov15/'+outf+'.lean','w').write("\n".join(out))
