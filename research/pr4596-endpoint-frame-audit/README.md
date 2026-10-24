# Endpoint-frame audit of #4596 (quotient of PR4470's word by span{511})

**Task:** independent-moment (adversarial audit). **Base:** canonical main `f626db5c`. **No κ is claimed here.**

DaysSky's #4596 (head `406aae34`) applies the linear map `φ(v) = (v & 0xFF) ^ (0xFF if v & 0x100 else 0)`, whose kernel is `span{511}`, to every frame of PR4470's word. It then extends one helper's final frame by the ninth axis (`pad_ambient`) and prices the result as a block-8 supplier. The claimed complex supplier is 0.0121, giving an outer κ of 0.0034, up from 0.00302015. Its evidence is that the shipped literal replay returns all 632 endpoints exactly.

This audit compares the submitted word's **main-field output frames** with PR4470's. PR4470's frames come from main's pinned constructor (`joint-helper-lattice/native_joint.py`, 7 pinned inputs). #4596's `QUOTIENT-WORD.json.gz` is vendored (blob `5bc2bdaf`, SHA256-pinned).

## Findings

| | PR4470 | #4596 quotient word |
|---|---|---|
| main roles 0–111 | end in the full frame `F₂⁹` | end in `F₂⁸` (low 8 bits) |
| main roles 112–223 | end in **112 distinct hyperplanes**, none containing 511 | end in the **same** `F₂⁸` |
| roles ending in `F₂⁹` | the 112 mains above | **only helper 224**, the `pad_ambient` extension |

- **Every main output frame changed.** All 224 main fields now end in **one and the same frame**. This is forced by the map: `φ` sends `F₂⁹`, and every dimension-8 subspace avoiding 511, onto `F₂⁸`. So all 224 distinct output charts collapse into one.
- **Why the replay still passes.** The pinned `verify_buffers.py` compares a replay's final frames with the submitted word's **own** `canonical["final"]`, at its line 207. Its `expected()` rows take no frame input; they are logical scalar endpoints. A word that changes every main field's output chart, together with its own declared finals, is therefore accepted. "632/632 endpoints exact" certifies the logical linear map, not the output charts.

## Consequence

PR4470's word supplies its kernel by delivering each main field in its required chart. That means `C_{F₂⁹}` for mains 0–111 and the chart of a specific hyperplane for mains 112–223. The paid profile prices those transports, and the downstream ladder and consumer charges assume them.

**If the supplier contract is PR4470's endpoint, the quotient word does not meet it.** Its lower paid profile then prices a different operator, one that never performs the full-ambient transforms, so it does not support the claimed κ. The `pad_ambient` step, which makes the frames span nine axes through one helper while no main field reaches them, keeps the block-8 ladder price without the corresponding outputs.

Any route that does change the endpoint contract would need the consumer's, ladder's and controller's charges re-derived for the new output charts, with an operator-level, not logical-only, endpoint check.

## Verify

```text
python3 -B research/pr4596-endpoint-frame-audit/verify.py
```

This runs in about 2 s with the standard library only.

## Limitations

- **What is decided here.** This audit establishes the frame facts and the replay's frame-blindness. Whether a supplier may change its output charts is a contract question for the maintainers. The consequence above is stated conditionally.
- **What is not re-checked.** #4596's pricing arithmetic. The objection concerns what is priced, not the arithmetic.

## Open next questions

- An operator-level endpoint check for literal replays: compare each field's final frame with the certificate's required frame, not only with the word's own list. First step: add the PR4470 certificate's final frames as an independent input to `replay`.

Credit: DaysSky (#4596), Cinna Davis (#4470) and the frame/replay lineage of `verify_buffers.py`. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
