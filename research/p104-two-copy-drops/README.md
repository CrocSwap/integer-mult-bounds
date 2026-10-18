# Two COPY terms can drop at the first P104 puncture boundary

For the **single exact eight-term decoder** in PR1187's published witness, 22 additional punctures can lower **two** COPY ranks simultaneously. The resulting profile costs **54 copies on82ports**, improving that source's displayed55/82witness. All16original frame lines remain punctured.

The complete first-boundary census has **360** distinct22port sets that cause any COPY drop: **24give cost54**, and336give55. Every other22port deletion has cost56. Therefore54is the sharp minimum at this boundary for this fixed decoder. Fewer than22added punctures leave all eight terms at rank7. This is an exact deeper-puncture decoder result, not a physical supplier or new kappa;54/82=27/41 remains worse than the original56/104=7/13copy ratio.

A separate complete1,792,252cut-pair union census gives the exact minimum for each of28pairs of distinct terms; the minimum two-term threshold is also22. Every deleted port in the displayed two-drop witness is necessary: restoring any one makes both drops disappear. All6724remaining all-pairs coefficient equations are checked exactly with integer denominator clearing.

## Completeness proof

For each original term, its P104 binary pairing matrix has rank7. Factor it as XY with inner dimension7and both factors full rank. If puncturing rows and columns lowers its rank, at least one restricted factor loses rank. Otherwise left and right inverses certify product rank7. A rank-deficient row factor lies in the kernel of a nonzero functional, so the removed ports must contain the support of a nonzero word in the full parent column code. The column case is transposed.

Each side has127nonzero codewords. After deduplication there are253distinct port cuts per term. Every cut is checked to lower that term, and every cut has size at least22. Hence any improving puncture of size22must equal one of the enumerated22point cuts exactly. Their union over all eight terms has360sets, each explicitly repriced. This proves the sharp54boundary claim for **all**22port subsets, not only a heuristic search.

For two distinct terms i,j, any common improving puncture must contain one cut from dictionary i and one from dictionary j. Conversely their union suffices. Thus minimizing the union size over all253x253pairs gives the exact pair threshold. This is repeated for all28term pairs. The fixed original real root-pair dual basis is unchanged; its identity therefore holds on every restricted live set. The witness also receives a full entrywise check.

## Reproduce

Python3.12+, standard library, from the repository root:

```
python -I -B research/p104-two-copy-drops/two_drops.py
python -I -O -B research/p104-two-copy-drops/two_drops.py
python scripts/research_package.py --package research/p104-two-copy-drops
```

Expected: `PASS_P104_TWO_TERM_DROP extra=22 copy=54 ports=82 cutpairs=1792252`.
The complete receipt, pair table, boundary histogram and full boundary-profile digest are compared. Controls reproduce the unchanged rank7baseline and the source's one-drop witness, verify every cut, restore each of22ports and check the exact coefficient identity.

Only the published fixed decoder is covered. The result does not optimize other P104 decoders, arbitrary deeper punctures, total cost beyond22deletions, additional term counts or physical endpoints. Source accesses, frames, restoration, hosting and recursive implementation are unpriced. A better COPY witness is not a complete moment or exponent result. The selected frontier remains unchanged.

## Open next questions

Do the other frame-pair decoder orbits share this54minimum at their first boundary? Identify an exact symmetry partition before repeating the360set boundary check; counting all7168decoders as independent would waste work. Global deeper-puncture optimization and physical realization remain separate blockers, especially because this boundary's ratio is already worse than unpunctured P104.

## Sources and credit

PR1187, Cinna Davis (@1337isnot1337), establishes the first-drop threshold22over all7168frame-pair decoders. Its full certificate is copied byte-for-byte at15bee4c8ea0f54fea575a48441c6acc8bad263cd, with Git blob/SHA256 in DEPENDENCY.json. It explicitly excludes aggregate COPY optimization at that boundary. This contribution supplies that optimization for its one published decoder and retains predecessor credit: themilkman216 PR968, DreamingOfClouds PR717, woklerx PR1020/1077and Joel Pulikkan PR620. New proof and independently written checker prepared for woklerx with substantial OpenAI Codex assistance; Apache-2.0. No independent human review claimed.
