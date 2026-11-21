# A near-crossing 320-factor single-band multiplier

The paired literal integer multiplier certifies **conditional κ ≥ 0.00389011528633** in a new profile of [#8030’s single-band construction](https://github.com/CrocSwap/integer-mult-bounds/pull/8030). This is **0.00000000000273** above [#8031](https://github.com/CrocSwap/integer-mult-bounds/pull/8031). The fixed histogram’s directed raw BIT upper endpoint is **0.003890115286595**, leaving **0.000000000000265**. That endpoint is a bound for this strictly priced raw word.

| Quantity | #8030 price-match profile | This profile |
| --- | ---: | ---: |
| Binary tensor power | 228 | 320 |
| Source trial C | 17108907955/2⁴² | 17519521755133/2⁵² |
| Complete binary band debit, including five ordinary bits | 19 | 24 |
| Largest binary rank exponent H | 1,568,000,000,000 | 114,688,000,000,000 |
| Sufficient public-precision exponent | 1,870,297,303,584 | 136,798,773,006,437 |
| Ordinary BIT cap | 0.003890115271496 | 0.003890115286380239 |
| Complete conditional κ | 0.00389011527141 | **0.00389011528633** |

The new carrier exponent is about 2.61× smaller than the 299,610,000,000,000 exponent used by #8031. The older #8030 price-match installation achieves its earlier rate with a smaller carrier, setup and activation. Under its five-bit ordinary tariff and four signed ticks, matching even #8031 at the unchanged raw BIT upper requires a binary rank exponent of at least 1,692,047,377,327. The exact price and applicability proof are in [PROOF.md](PROOF.md).

## Replay

From a CPython 3.12 checkout run

```sh
python3.12 -IB scripts/research_package.py --package research/p104-single-band-near-crossing
```

The package authenticates 91 files of [#8030 at 6285dd829114705862e8d91facaedc1f31d3cfcb](https://github.com/aliromman/integer-mult-bounds/tree/6285dd829114705862e8d91facaedc1f31d3cfcb/research/single-band-native-carriers), applies the five small module updates in [OVERLAY.json](OVERLAY.json) to a private copy, and regenerates the complete profile from the actual entry points. The registered cases cover two strict source price calculations, finite band flow, dense spectral results, exact BIT charts, paid Gaussian grid and atlas, the rational physical caller, and the signed product on the candidate profile. The product checks all recovered digits, 157,248 numerical H calls, 138 rank-two shuttles, retained input bytes and pointers, and an admitted small-stage body.

[RESULT.json](RESULT.json) retains the literal invoice and stage prices, complete resource and activation data, and rejected price controls. It rejects an additional paid rank-one call, the 288-factor sufficient test at the selected offsets and price, the exact conservative 23-bit band test, and equality at the required signed ordinary gate. No assertion is made about other 288-factor proofs or the optimal 320-factor tariff.

The complete conditional application inherits all-column native action, owned erasure and restoration, compiler transfer, precision and tape services, and analytic recovery. The written installation and cost proof covers production sizes through its parameters. The executed operator, tape and product controls use finite dimensions. Production-dimensional execution and a practical crossover remain open.

## Open next questions

Can a changed literal BIT invoice give a strictly higher raw crossing? The first decisive check is a positive signed moment at 0.003890115286595 with a legal paid or productive change. Any such change requires a fresh operator, erasure, precision and outer application replay.

Ali Romman supplied the single-band compiler, paired native circuits and all-column implementation. Clear1nsight supplied the prior compiler and refined application comparison, with earlier source and complement bounds by ToikY, Jacob Alan Sussman, DreamingOfClouds and zxv. New contributions are the directed 320-factor choice, staged proof extension, exact price controls and replay. OpenAI Codex materially assisted. The archived sources retain their original notices and licenses. The new material is Apache-2.0.
