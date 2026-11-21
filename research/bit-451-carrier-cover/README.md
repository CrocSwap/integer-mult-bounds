# A sharper cover bound for the 451-factor multiplier

Under the same premises as #7863, the deterministic fixed-multitape multiplier for every pair of n-bit integers returns the exact product in time O(n (log n)^(1−κ)) with **κ = 0.00387992804356**. The improvement is in the proof of the ordinary BIT rate on the existing physical schedule.

| Comparable complete result | Conditional κ |
|---|---:|
| #7863, independently reproduced against #7973 | 0.00387992804346 |
| This proof | 0.00387992804356 |
| Absolute increase | 0.00000000000010 |
| Relative increase | 0.0000000025773673862% rounded; exactly (500/193996402173)% |

The original uniform carrier has N = 2^H with H = 1202400000000000. The retained delayed-cover theorem charges the full fallback by a factor below 1 + 2^−46. Taking d = 1/(H·2^44) gives N^d > 1 + 2^−45. The complete normalized moment is therefore strictly below one after this smaller loss. Evaluating all seven ordinary stages supports the installed BIT cap 0.00387992804364799. The 48-call rational application tests 0.00387992804363 and certifies the complete rate above. [Proof and strict stage checks](PROOF.md) · [Machine-readable receipt](RESULT.json) · [Delayed-cover theorem, §7](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/p104-shared-native-helper-splits/retained/compiler/bit-audit/retained/DELAYED-COVER-BRIDGE.md#7-moment-and-row-stock-consequences)

The native signed crossing is still enclosed by [0.003879928046154, 0.003879928046155]. Giving the predecessor its upper endpoint and deducting only its two fixed losses yields a ceiling of 0.003879928043555 on the old proof. The new complete claim exceeds even this ceiling by 0.000000000000005. Both proofs use the original paid and productive positions, ordinary word, full fallback work, selected prime and excluded catalogue, stock recursion, restored ownership, 451-factor compiler and precision obligations. Improved asymptotic estimates may require larger fixed proof thresholds. The explicit physical realization of #7863's seven stages and nested seed remains conditional. Main selects #7000 separately.

## Replay

Use CPython 3.12 from a clean repository checkout. The package uses the standard library and authenticates a vendored copy of the public #7863 archive. It writes generated files in a temporary directory.

```sh
python3.12 -IB scripts/research_package.py --package research/bit-451-carrier-cover
```

The first scientific marker is `PASS_ORIGINAL_451_SUPPLIER_AND_ACTUAL_CARRIER_COVER`. It requires byte-identical regeneration of the predecessor's complete BIT receipt, including the native signed census and all 36 caller uses. The final marker, `PASS_COMPLETE_SIGNED_APPLICATION`, requires the expanded rational audit, 54 strict conditions, four functional checks and agreement with an independent arithmetic proof and separately regenerated application and audit. Controls cover a missing CLEAR, an extra paid term, an insufficient BIT cap, a non-strict ordinary stage and an insufficient cover bound.

The archived source has SHA-256 `5f9d9c378a1bddccb2e42ac6453716fa950f19bd71f6181a9606f5eb68b022b3`. The verifier checks all 202 entries in its source manifest. The regenerated application and audit hashes are `e0a28d730e5a63070221a170c3e5e10abdf4ed552d67fbd47d1f4ec157b736ad` and `51963b588680e3150b97b156a461c9002368c40752b73bc4a6b03f94aca97c0b`. [Exact predecessor archive](https://github.com/CrocSwap/integer-mult-bounds/blob/b3e4412fe01f07dc58305616fabf96345f49a781/research/p104-bit-451-factor-schedule/replay.tar.gz)

## Credit and overlap

Clear1nsight supplied the exact 451-factor word and schedule, the #7830 compiler lineage and the #7973 consumer audit. Ali Romman supplied the earlier dual-supplier construction and paired caller. The retained delayed-cover and ambient-cap authors supplied the fallback inequality and stock lemma. Dugongue and Rohan Arun supplied the #7831 and #7835 cutoff schedules used in the predecessor lineage. Cinna Davis supplied earlier balanced CRT and outer proof work. The inherited source notices accompany the archived inputs. This contribution specializes the existing multiplier inequality to the actual carrier, proves the improved seven-stage rate on the same algorithm and independently replays the resulting application. OpenAI Codex materially assisted the reasoning, implementation and replay. [#7863](https://github.com/CrocSwap/integer-mult-bounds/pull/7863) · [#7973](https://github.com/CrocSwap/integer-mult-bounds/pull/7973) · [#7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830)

The nearest six-stage threshold calculation assumes a different raw invoice, larger carrier and stronger prime criterion. The 480-factor physical realization and the ternary receiver concern other contracts. [#7975](https://github.com/CrocSwap/integer-mult-bounds/pull/7975) · [#7846](https://github.com/CrocSwap/integer-mult-bounds/pull/7846) · [#7945](https://github.com/CrocSwap/integer-mult-bounds/pull/7945)

## Open next questions

Can the existing uniform compiler prove a smaller log-power loss at the same N? First solve the shifted exit and majorant inequalities with the actual maximal paid rank and minimal productive rank. Keep the same charged template unless its new routes and stock are established independently. Any further improvement must survive the complete consumer and the finite proof-ceiling comparison.
