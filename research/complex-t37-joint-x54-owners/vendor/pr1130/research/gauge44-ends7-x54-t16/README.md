# Eight-slot k8 word with rank-seven helper ends and T16 packing

Conditional κ = **0.001673006105142741**, conservative κ = **0.00167300610229067600**. The upstream conditional assumptions and PR589 bit supplier remain unchanged.

This package adds the eighth triangle-hybrid slot **X54/E589** after the rank-seven ends of helpers574/575, then binds the strongest checked ends7-X54-E7G4d4 T16 owner map. The final local word is NOT the seven-slot baseline and NOT the ends7-only intermediate word.

## Binding artifacts

- Final FULL-WORD content SHA256: `9fca1fc6f1fa0a9469fc10e3b90dc2c9802bf391b45f84d52ce5e7f6706c9674`.
- Canonical content SHA256: `4577d75e58f128340ce49dbdeeb6f034ed7e77dfbea973614c85676654864838`.
- R480, residual width3728; widths {4:56,5:32,7:32,8:120,9:240}.
- Local paid profile {1:2406,2:432,3:426,4:138,5:84,8:8}.
- Frozen T16 owners SHA256: `d275e6c0ef501fdc9cb6fba883d65666d10391ad35ed5e66b2f4d7689ec75d4b`.
- Frozen T16 PLAN SHA256: `d64d0314634805d9a919a0251935a91f84146281cbc9a97d8de6a2b62d3cabe7`.
- Frozen T8 κ =0.001671160051689084; its data is in `data/T8` and `data/SPEC-T8.json`.

## Complete construction verification

First obtain a completed seven-slot k8 replay using `research/gauge44-slots/construction/slots/verify_slots.py` (or its exact sparse-phase equivalent). The completed baseline's word, locals and full successful step list are checked against `construction/slots/SLOT-PINS-k8.json`; no unchecked word is accepted.

```sh
python -B research/gauge44-ends7-x54-t16/construction/ends7/verify_ends7.py \
  --main . --pr635 /tmp/gauge44-pr635 --baseline /tmp/slots \
  --work /tmp/ends7-x54 --phase-jobs 2
```

This single command rebuilds and verifies the entire changed construction:

1. Hash-check the completed seven-slot baseline.
2. Apply `construction/ends7/RECIPE-ENDS7-k8.json` using its literal old-value and output pins. Run the existing ends7 controls on THIS intermediate word: six rejections by both independent and native auditors.
3. Apply `construction/ends7/x54/RECIPE-X54-ends7.json` with the unchanged triangle builder. It has five B deletes and five inserts, one FULL holder335 restoration and one rank-eight early holder367 restoration. Both restorations at FULL are NOT legal.
4. Run all ten X54 identity/recipe/global/per-X controls with pinned exact-audit rejection reasons.
5. Rebuild native canonical/program locals, ledgers, replay, wrappers and exact phases against the composite pins in `x54/X54-PINS.json`.
6. Check the final word with the independent exact forward/dual endpoint/frame/entrance/cone auditor and PR1049's complete leaver-premise check.
7. Run fresh strict T8 AND strict T16, including actual owner-window reconstruction, exact invoice, assembly and independent T16 negative controls.

Final marker: **PASS_RANK7_ENDS_AND_X54_ON_CHECKED_SLOT_BASELINE**. An ends7-only marker is not sufficient for this package. `verify_t16.py` remains available to replay T16 alone on already checked COMPOSITE locals; it does not substitute for the construction command.

## Mechanism and attribution

Rank-seven ends transfer PR1030's codimension-one end-frame mechanism to helpers574/575. X54 is an additional S-source instance of PR987's triangle-hybrid mechanism, missed by a search filter that admitted only packet sources with register index≥224. Its width-neutral profile change is {3:+2,4:-4,5:+2}. Donations feed holders367 and335 before their target reads. The eighth slot gives a strict same-map gain of about3.977e-8, not merely an estimated gain. The ends7-X54-E7G4d4 map was produced by exact T16 pattern-flow packing; every frozen role is checked against actual windows.

The local mechanism, width supply and frozen owner assignment are independently checked. Prefix397 agrees between independent and invoice checks; physical row coefficient16469. Apache-2.0 notices, vendored source provenance and conditional proof scope remain in the existing notice/proof files. Other proof notes describe inherited intermediate stages, not alternative final locals.
