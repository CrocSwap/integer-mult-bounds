# Review of the lifted-target negative-control fixture

A separate OpenAI Codex agent checked the fixture change on both exact late8 providers. This is an independent computational check, not independent human review. The production auditor and candidate words were not edited.

The original control swaps destinations of prelude events 9 and 10 (zero-based):

```text
add 126 <- -1/2 * source 83, frame [45]
add 153 <- -1/2 * source 83, frame [45]
```

The swap merely exchanges the order of two commuting additions. The unchanged auditor correctly accepts the resulting circuit in both orientations. It is therefore not a valid negative control on these words. The original failed receipts are preserved as `ORIGINAL-FAILED-BASE-CONTROLS.json` and `ORIGINAL-FAILED-EXTRA-CONTROLS.json`; each had only this non-rejection among its 24 proposed mutants.

The replacement keeps event 9 and selects the first later addition with a distinct destination, a different `(source, numerator, denominator)` payload, and the same frame. This chooses event 16:

```text
add 153 <- -1/2 * source 98, frame [45]
```

Swapping the destinations of events 9 and 16 creates an actual semantic mutant. Re-derived cleanup is identical to the original cleanup because the prelude's target corrections do not belong to non-target cleanup. Both mutant words pass the unchanged auditor's static warp and frame/profile checks, then fail at `target map failed 14` (register 126).

A separate free-operator replay confirms the exact final residual at register 126:

```text
+ 1/2 * K_52 * x_83 - 1/2 * K_53 * x_98.
```

It is nonzero because `x_83` and `x_98` are independent inputs and the chart operators are invertible. Register 164 has the same residual; registers 153 and 218 have its negative. All other target residuals vanish. These residuals occur in both providers.

The scratch copy of the control suite, with only this fixture selector changed, accepts each unmutated word and rejects all 24 negative controls on both base and extra. No acceptance condition, auditor, profile, frame, source word, or cleanup rule was weakened.

Evidence: `SWAP-REVIEW.json`, `INDEPENDENT-MUTANT-RESIDUAL.json`, `BASE-CONTROLS.json`, and `EXTRA-CONTROLS.json`. The scratch `lowfour_controls.py` contains the reviewed selector. The original failed receipts remain separate from the successful reruns.
