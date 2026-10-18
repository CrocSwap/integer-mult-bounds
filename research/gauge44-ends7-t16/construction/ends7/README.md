# Rank-seven helper ends on the seven-slot k8 word

Credit: the mechanism is PR1030's (helpers 588/589 of PR869's U8 end in dimension seven; eight B frames and two
early-cleanup frames change with them). PR1049's leaver-cell audit supplies the leaver-premise check (`premise/`,
its `verify.py` unchanged as `verify_1049.py`, Apache-2.0).

On the seven-slot k8 word `c2b29430…` (R = 480), PR1030's helpers 588/589 are helpers **574/575**. The
recipe `RECIPE-ENDS7-k8.json` is PR1030's twelve annotations, shifted to that numbering:

- ends of 574 and 575: `[256,128,96,16,8,4,2,1]` → `U = [256,128,96,17,9,5,3]`;
- B frames 994, 995, 1026, 1027 (needed: the row cone of 574/575 is {412, 574} and {414, 575}) and
  1106, 1107, 1138, 1139 (profile lowerings), each to the same codimension-one subspaces as PR1030;
- early-cleanup tails 93/94 → `U`.

Local profile `{1:2412,2:418,3:432}` → `{1:2406,2:432,3:424}` (Δ `{1:-6,2:+14,3:-8}`, rank mass −2), helper
widths `{7:30,8:122}` → `{7:32,8:120}`.

Search over all helpers: the only helpers with a low end are the 46 dimension-eight ends and 32 dimension-four ends.
Each dimension-eight end has exactly one legal codimension-one subspace (the cone forces it), no dimension-four end
has one, and no lowered end drops again to six. With gopt2-optimal frames only 574, 575, 580 and 581 lower the local
cost by more than the idle price of the freed coordinate (−1.0013 vs −0.9884…−0.9990 for the others).

## Verify

```
python -B construction/ends7/verify_ends7.py --main <repo> --pr635 <pr635 checkout> \
    --baseline <completed verify_slots[_fast].py --work dir> --work <new dir> [--phases reference]
```

Steps: baseline pins (SLOT-PINS-k8) → `build_ends7.py` (output pinned) → `end7_controls.py` (positive control plus
`end_restored`, `wrong_frame`, `cone_violation`, each rejected by both audit_local and the native hpe auditor:
6 rejections) → native locals (phases through PR1029's sparse evaluator by default) pinned in `ENDS7-PINS-k8.json`
→ audit_local → PR1049 leaver premise on the new word → strict `verify_global.py` with this package's data, κ pinned.
