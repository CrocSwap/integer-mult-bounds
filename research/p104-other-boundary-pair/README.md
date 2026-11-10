# Other rank-2 boundary carriers on the #5718 cut

**Outcome:** negative result. On the pinned PR5713 word, the only legal rank-2 coframed main-partner carriers are three carriers of helper 708 on frame 602. They leave the same terminal output defect. The published partner 154 is the unique ordinary-prefix minimum, at scalar cost 1118 against 1142 and 1612.

Prepared by unpaidmoon with substantial Cursor Grok assistance.

## Scope

This package answers one question left by `research/p104-two-boundary-helper-split`: whether another legal boundary pair at an actual coframed cut improves the complete native, helper and ordinary bill. The question is refined to a classification of rank-2 carriers. A search for a new split, a new kappa, or a change to the selected frontier is outside it.

The source word, carrier rule, spans and defect identity are in [PROOF.md](PROOF.md). `verify.py` recomputes the census and the three terminal defects from the pinned tar.

## Evidence

- Source hash `32adce6656e49aa020d3e6317f1c45c11fccadeeb67a8d506172d101703d2138`.
- Carriers: `(708, 154, +1/2)` on events 13657–14336, `(708, 127, -1/2)` on 13653–14139, and `(708, 119, +1/4)` at 13658 only.
- The published cut 14330 is inside the partner-154 span, and its nuisance is constant there.
- All three suffix columns are `{126: -2, 188: 2, 708: 1}`.
- Terminal defects agree on rows 126, 188 and 743. No prefix move is inserted.
- Ordinary prefix scalars are 1118, 1142 and 1612.

## Reproduction

From the repository root:

```bash
python3 -B scripts/research_package.py --package research/p104-other-boundary-pair --check-only
python3 -B scripts/research_package.py --package research/p104-other-boundary-pair
```

The registered commands also run the verifier under `python3 -I -B` and `python3 -I -O -B`. Both print `PASS_P104_OTHER_BOUNDARY_PAIR`.

## Open next questions

1. Do any rank-1 main-partner carriers on this same word beat the published bill once their wider cleanup is charged? The first concrete step is to restrict the census to frames of length 1, record each suffix column, and build the terminal program for the narrowest columns. The rank-2 cleanup order does not settle that wider repair, which is why this package leaves the family open.
2. Does the same three-carrier list persist on the already-split candidate word in `research/p104-two-boundary-helper-split/WORD.json.gz`? The first step is to rerun this census there. That word already contains the partner-154 split, so the comparison has to say whether a second carrier is still present after the split rather than treating the source word as the only object.
