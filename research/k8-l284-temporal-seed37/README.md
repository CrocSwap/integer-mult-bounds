# Seed 37: exact temporal gauge on helper L284

**Status: finite scalar construction; no new κ or hosted-supplier claim.** This package applies the established one-coordinate temporal-gauge method to a new boundary helper: L284, the first eligible helper after PR1259's exact seed-37 slice `[37,53)`. The full sorted eligibility list has 237 helpers; the prior slice's 16 helpers end at L283. PR1369's census covers the complementary zero-static class, while L284 has static exponents -2 forward and +2 backward.

| Orientation | Incident ADDs | Exact exponent domain per ADD | Real primitives | Complex primitives | Saving | SCALE transitions / work | Formal columns |
|---|---:|---:|---:|---:|---:|---:|---:|
| Forward | 86 | [-3,4] | 68,001 → 67,923 | 136,002 → 135,846 | 78 / 156 | 16 / 22 | 712 |
| Backward | 86 | [-4,3] | 68,009 → 67,931 | 136,018 → 135,862 | 78 / 156 | 16 / 22 | 712 |

The exact DP covers all 8 exponents at each of the 86 chronological ADDs in each direction (5,448 transition evaluations per orientation). It charges the zero-entry gauge, every change, and restoration to exponent zero. The best constant additional exponent is zero in both directions and saves nothing. The resulting complex primitive invoices are 135,846 forward and 135,862 backward; the paid profile remains identical. Payload remains 192 bits, with 52-bit and 68-bit prefix envelopes respectively.

## Scope and provenance

The fixed source word and lowerer are pinned to PR1263 head `5fbaca13028846bddbb001e8e07addc2ab8e5816`. PR1259's exact seed-37 interval `[37,53)` ends before L284; its certificate is vendored and SHA-256 / Git-blob pinned, and the verifier checks the slice against PR1263's reconstructed eligible-helper list. The temporal-gauge method and implementation are credited to PR1259 and PR1385 (L259). This result changes the helper parameter to L284; it does not rerun either predecessor's helper range or claim a better global schedule. It does not combine L284 with L248, L253, L259, L276, or any other schedule.

No full hosted supplier admission, native emission, runtime benchmark, theorem-level multiplication proof, or new κ is claimed. The selected PR1094 result and PR589 bit supplier remain unchanged at the pinned base.

## Reproduce

With Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/k8-l284-temporal-seed37
```

The package verifier rebuilds the pinned PR1263 source and checks both exact schedules, complete invoices, precision receipts, unchanged paid profiles, and equality on all 712 formal input columns. A three-ADD exhaustive enumeration is a small independent DP control. Expected final line: `PASS_REGISTERED_RESEARCH_PACKAGE research/k8-l284-temporal-seed37 outcome=completed`.

## Attribution and next question

Contributor: **Cinna Davis / @1337isnot1337**. Substantial **OpenAI Codex** assistance was used for research, implementation, verification, and writing. Credit Sagar Thakrar / @thakrarsagar (PR1259) for the single-helper temporal gauge method and its exact clamping argument; credit Cinna Davis / @1337isnot1337 (PR1385) for the adjacent L259 application; credit Philipp / @mightyOil (PR1263) for the frozen k8 word; and credit @woklerx / PR1161 for the pinned exact lowerer engine. No independent human review is claimed.

## Open next questions

Can this exact L284 schedule be admitted by the native hosted supplier with the same precision and operation charges? This package does not establish that admission. Joint L284 schedules also require their own complete interaction and invoice analysis.
