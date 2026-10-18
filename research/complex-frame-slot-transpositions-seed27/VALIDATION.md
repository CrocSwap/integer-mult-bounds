# Reproduction and validation

Executed on Windows with CPython 3.14 on 2026-10-13, at base ba82555c64e1879e4b7decce28186f208fcb8262.

| Command | Result |
|---|---|
| `python -I -B research/complex-frame-slot-transpositions-seed27/verify.py` | PASS, complete saved receipt reproduced |
| `python -I -O -B research/complex-frame-slot-transpositions-seed27/verify.py` | PASS, same complete receipt with Python assertions disabled |
| `python -I -B scripts/verify_selected_result.py` | PASS selected-at-base PR1042 record, exact kappa, original source inventory and proof supplement |
| `make verify` | Unavailable: `make` is not recognized in this environment |
| `git diff --cached --check` | Required and passed before commit |

The initial adjacent census covers all 5,295 within-stage adjacent positions. The stronger exposure census covers all 11,848 endpoint-exposable pairs across 1,666 unequal-frame boundaries, including 11,811 commuting pairs. Every commuting crossing fails subspace containment; all affected-register results agree with complete reconstructed-stage results. No rejection relies solely on the fixed exit check. No random search or early state/depth cap is used.

Eleven controls check dependent ADD maps, equal-dimensional but different subspaces, duplicate JSON keys, nonfinite JSON, floating seed 27.0, required-pin deletion, a legal synthetic crossing, a later frame decrease, an altered stage exit, non-ADD barriers, and a legal crossing exposed only by moving a previously nonadjacent ADD. All pass. The source-name set is fixed exactly, so deleting a pin cannot silently reduce validation.

The input profile is recounted from A/B, center routes, early cleanup and terminal promotions. It is exactly {1:2412,2:418,3:432,4:142,5:82,8:8}, with rank mass 5586. The word is read directly from the selected archive's R480 member; no retained R492 intermediate is substituted.

These checks establish the relative scalar-map invariance and label-frame obstruction. They do not independently establish native/Clifford/physical legality, global owner admission, precision bounds or the full multiplication theorem. No baseline code, selected certificate, or supplier artifact is modified.
