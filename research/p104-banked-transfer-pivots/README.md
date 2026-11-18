# Fifteen fewer paid transfers per native call

The construction gives **conditional κ ≥ 0.0037260455556** under the five assumptions in the selected multiplication framework. It starts with SYLforge’s 16-call construction. At fifteen places a sender can supply a linear combination that the receiver needs from a different chart. Each change saves one recursive call. The complete construction saves 240 calls and retains all 21,152 productive fields. [Parent PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669) · [Construction and application proof](PROOF.md)

| Quantity | Published parent | This construction |
| --- | ---: | ---: |
| Paid transfers per native call | 6,157 | 6,142 |
| Paid calls in the complete construction | 102,064 | 101,824 |
| Productive fields | 21,152 | 21,152 |
| Target minus paid rank mass | 1,328 | 1,328 |
| Directed bracket for the raw crossing | (0.0037218793483, 0.0037218793484) | (0.00372604555571, 0.00372604555572) |

The claimed saving exceeds the parent’s **upper** endpoint by 0.0000041662072, or 0.11194%. That increment is 1.758 times the 0.0000023694495 increment in PR #7663. The comparison with the selected conditional κ of 0.00363005817 is 2.64424% and includes the work of the predecessor authors. The new implementation reserves 15,290 private full-field homes per native call. The two constructions have different finite resource budgets. [Previous step](https://github.com/CrocSwap/integer-mult-bounds/pull/7663) · [Selected record at the base commit](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

## Review and reproduce

1. Read the first entry in [PIVOTS.json](PIVOTS.json) with the identity in [section 1](PROOF.md#1-replace-one-incoming-transfer). All fifteen entries use event indices from the same pinned parent. A negative input token `~r` denotes public role `r`.
2. Inspect the paid and productive histograms, two directed price checks, compiler margins and physical charges in [RESULT.json](RESULT.json). The physical and precision argument is in [sections 3 and 4](PROOF.md#3-retain-the-complete-root-grid).
3. Run the package from the repository root with Python 3.12 and its standard library.

```sh
python3.12 -B scripts/research_package.py --package research/p104-banked-transfer-pivots --check-only
python3.12 -B scripts/research_package.py --package research/p104-banked-transfer-pivots
```

The eight registered commands reconstruct the source word, check the fifteen exact identities, verify every public endpoint and price the complete signed caller. The six catalogue slices check phase and rank for 3,024 physical pairs. They compare all forward and adjoint columns on the ten distinct rerouted pairs. They also check all 104 main ports. The replay rejects a wrong sender sign, a wrong phase, a nonlocal donor, a causal cycle and an inexact division. [Replay manifest](VERIFY.json) · [Repository input pins](SOURCES.json) · [Open-source head and file pins](SOURCE-PINS.json)

The finite certificates cover the stated circuits. The application still requires native all-column realization, owned allocation and erasure, compiler closure, fixed-tape precision and movement, and analytic recovery. The exact-grid argument applies to the common root format. The separately rounded finite-tariff implementation described in the parent needs its own error proof. Independent scientific review and a materialized full multiplier remain open. [Application proof](PROOF.md) · [Parent scope](https://github.com/CrocSwap/integer-mult-bounds/blob/eaef5d1580e5761feaed09262b964871f3e5f553/research/ee251f60-composition/README.md)

## Open next questions

- Can some of the 15,290 private snapshots share backing? Compute the last read of each snapshot in the published schedule. A smaller bound needs a proof of allocation, resets and selection across child returns.
- Can a pivot increase the target minus paid rank mass? Check candidate sender relations against arbitrary independent inputs, their legal receiver dependencies and the full 16-call invoice. The present changes preserve the rank mass exactly.

## Credit

Ali Romman, with substantial OpenAI Codex assistance. The fifteen rational pivots, the resulting bank program and the application to the 16-call construction are new here. SYLforge supplied the source word and caller bytes. DreamingOfClouds, Clear1nsight, Rohan Arun, Jerry Chen (CubeJerry), Douglas Colkitt and the contributors recorded in the source notices supplied predecessor constructions, operator and compiler methods, and the selected framework. [Attribution](NOTICE) · [Parent provenance](source/7669-CREDITS.md) · [Coordination discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19700346)
