# P112 diagonal support audit for the fixed PR #1347 cover

This package exhausts all maximum-hit rank-six support triples in the ten distinct 1,120-hit frame-mask classes used by PR #1347's `COVERING.json`.

## Result

The complete 967,232 parent/cut domain contains 40 triples in those ten fixed classes: four triples per class, with two distinct diagonal-support masks per class. The union of all 40 masks covers 102 of the 112 live root lines. It misses line IDs `18, 47, 53, 62, 88, 92, 96, 100, 112, 117`.

Therefore no choice of one maximum-hit support representative from each of these ten frame classes can cover every live diagonal. The exact root representatives, frame masks, all 40 support triples, diagonal masks, and replay receipts are in `RESULT.json`.

This is a negative result for this one fixed ten-mask cover. It does not rule out a different cover, a different cost/domain, or an arbitrary P112 decoder. It is only a support necessary-condition audit; it does not solve the coefficient equations or claim a physical circuit or a new κ.

## Reproduce

From the repository root, run:

```sh
python3 -I -O -B research/p112-fixed-frame-diagonal-seed52/verify.py
```

Expected output:

```text
PASS_EXACT_FIXED_FRAME_PATTERN_DIAGONAL_OBSTRUCTION patterns=10 support_triples=40 diagonal_union=102/112 uncovered=10
```

The verifier uses only the Python standard library. It rebuilds the E8/P112 frame geometry, checks the predecessor's exact positive control, enumerates all rank-seven parent pairs and their nonzero code words, and compares the full candidate census and its digest to `RESULT.json`. It uses exact integer bit masks; no MILP or floating-point solver is involved. To regenerate the result after an intentional input or algorithm change, run the same command with `--write-result` and review the full JSON diff.

The repository's opt-in package checks are:

```sh
python3 scripts/research_package.py --package research/p112-fixed-frame-diagonal-seed52 --check-only
python3.12 scripts/research_package.py --package research/p112-fixed-frame-diagonal-seed52
```

## Provenance and credit

Base commit: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Assignment seed 52 selected this fixed-mask audit from three scoped candidates; see `CLAIM.md` and the claim on [coordination discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911792).

This work extends PR #1347's bounded diagonal search in a different way: that search kept only the first enumerated representative for each frame mask and timed out at 120 seconds. Here all support representatives in the ten masks of its committed `COVERING.json` are enumerated exactly, and the conclusion follows from their complete diagonal-support union. The finite rank-six geometry and witness derive from Navinor's PR #1226 and the ordered P112 model/certificate in PR #1323. The inherited nine-root frame obstruction is credited in PR #1347 to David Arias's PR #1236 and Hanson's independent PR #1242; this package does not need or extend that lemma. Exact source and license pins are in `SOURCES.json`; the original Apache-2.0 license and predecessor notice are retained.

New code and analysis by Cinna Davis with substantial OpenAI Codex assistance in scope selection, proof analysis, code, verification, and writing. No selected certificate or frontier is modified.

## Open next questions

- **Could a different set of ten maximum-hit frame masks pass this support test?** That would preserve a possible support-level route beyond the fixed PR #1347 witness, while still leaving coefficient and physical-cost gates. First step: enumerate all 5,376 maximum-hit masks with their full representative sets, then solve an exact dominance-compressed frame-plus-diagonal cover. The broader cross-pattern dictionary is outside this fixed-cover certificate.
