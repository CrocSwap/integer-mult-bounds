## Result

In the exact two-role formal `F2[D8]` model with paid reflection labels `s,t` only and arbitrary free `GL2(F2)` mixing, the noncentral rotation/inverse target `diag([r],[r^-1])`, `r=st`, has exact paid-call minimum **four**. The direct four-call word passes; exhaustive full-coefficient enumeration rules out every word of length zero through three.

The regular representation gives only the lower bound three (target difference rank 12; each paid factor has rank 4). The exact word enumeration rules out that remaining three-call possibility.

## Scope and relation to predecessors

This is a target-class extension of merged [PR #1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443), which uses the same group, two reflection labels, two roles and free scalar mixing but proves an eight-call minimum for the central target `diag([r^2],[r^2])`. This PR concerns the noncentral order-four inverse pair and its four-call bill. It does not restate the central-target result. Other nearby work includes the open quaternion central-pair result in PR #1822 and the D8 third-role central-pair claim in Discussion #1738.

## Reproduction

```sh
python3 -I -B research/d8-rotation-pair-seedff568/search.py
python3 -I -B research/d8-rotation-pair-seedff568/verify.py
python3 scripts/research_package.py --package research/d8-rotation-pair-seedff568 --check-only
```

The search covers `1, 12, 144, 1728` words at lengths `0,1,2,3`. The independent verifier checks the direct word, complete group-algebra boundary, altered and truncated controls, and the rank screen. The registered package replay requests Python 3.12; direct checks in this environment use Python 3.14.7 because Python 3.12 is unavailable.

This is a scoped abstract address-model result only. The selected supplier and selected moment are unchanged; there is no new `kappa` or physical/compiler admission. Substantial OpenAI Codex assistance; no independent human review is claimed.
