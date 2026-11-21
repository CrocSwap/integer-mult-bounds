# Sharper bounds on the same 451-factor multiplier

Under the same premises as #7863, the deterministic fixed-multitape multiplier for every pair of n-bit integers returns the exact product in time O(n (log n)^(1−κ)) with **κ = 0.00387992804505**. The improvement is in the proof of the ordinary BIT rate on the existing physical schedule.

| Comparable complete result | Conditional κ |
|---|---:|
| #7863, independently reproduced against #7973 | 0.00387992804346 |
| Prior #8026 cover proof at 355f3218 | 0.00387992804356 |
| Cover and fractional majorant at 80fcb342 | 0.00387992804359 |
| Cover and normalized majorant at f1649c6d | 0.00387992804406 |
| Complete integer-scale endpoint at 2f82ecc8 | 0.00387992804422 |
| Weighted paid exits at a24daf62 | 0.00387992804459 |
| Minimum integer power for the fixed comparison law at 1ef5792e | 0.00387992804502 |
| Second moment of the actual paid jobs | 0.00387992804505 |

The original 451-factor word bounds the second moment of the completed paid log ranks by 3/5, including the full split surcharge. This admits power 31 at height five and at every other integer height. All 32 coefficient bounds pass. The largest coefficient ratio occurs at index four and is below 0.000058149, against capacity greater than 0.0001888872. The uniform loss falls from 1257/H to 1218/H. The ordinary cap is 0.00387992804513502 and the complete signed consumer tests 0.00387992804512. The exact gain over power 32 is 0.00000000000003, or (50/64665467417)%, approximately 0.000000000773210215548%. The cumulative gain over #7863 is 0.00000000000159, or (2650/64665467391)%, approximately 0.0000000409801414405%. [Proof and source credits](weighted/SECOND.md) · [Independent receipt](weighted/SECOND.json)

## Fixed mean comparison

For the fixed weighted Bernoulli comparison, p=32 is the smallest admissible positive integer power. The actual height G=5 rules out p=31 for this upper estimate and monotonicity excludes every smaller integer power. All 33 coefficients pass at p=32. The resulting uniform loss is 1257/H and ordinary cap is 0.00387992804510259. The exact gain over p=45 is 0.00000000000043, or (4300/387992804459)%, approximately 0.0000000110826797574%. The total gain over #7863 is 0.00000000000156, or (2600/64665467391)%, approximately 0.0000000402069312247%. The exclusion applies to the Bernoulli comparison with these constants. [Minimum-power proof](weighted/MINIMUM.md) · [Independent receipt](weighted/MINIMUM.json)

## Weighted paid exits

The actual paid ranks support a tighter estimate of the leaf count. At p=45 and h=1804, the directed mean including split charges is at most 0.748475924225778. All 46 coefficient bounds hold at every recursion depth. This reduces the uniform charge from 2218/H to 1768/H and gives ordinary cap 0.00387992804467760. The complete consumer tests 0.00387992804466. The incremental gain is 0.00000000000037 over the integer-scale endpoint, exactly (1850/193996402211)% or approximately 0.00000000953625932706%. The cumulative increase over #7863 is 0.00000000000113, exactly (5650/193996402173)% or approximately 0.0000000291242514640%. [Weighted proof and source attribution](weighted/PROOF.md) · [Independent coefficients and receipt](weighted/RESULT.json)

## Fixed integer-scale endpoint

At fixed p=60 and θ=13/15, the shift and base guards admit exactly the positive integer scales 1 through 9012. Scale 9012 attains the minimum integer carrier loss numerator, 2218. It gives the ordinary cap 0.00387992804430335, tested at 0.00387992804429. The complete rate rises by 0.00000000000016 over the normalized proof, exactly (800/193996402203)% or approximately 0.00000000412378781728%. The cumulative increase over #7863 is 0.00000000000076, exactly (3800/193996402173)% or approximately 0.0000000195879921351%. [Endpoint proof](normalized/ENDPOINT.md) · [Exact receipt](normalized/ENDPOINT.json)

## Normalized majorant

The normalized majorant reduces the uniform charge to 2406/H and supports ordinary cap 0.003879928044147. The outer compiler tests 0.00387992804413. This adds 0.00000000000047 over the fractional proof, exactly (4700/387992804359)% or approximately 0.0000000121136267147%. The total over #7863 is 0.00000000000060, exactly (1000/64665467391)% or approximately 0.0000000154642043172%. The complete proof and independent receipt identify the same integer flow at every rank. [Normalized proof](normalized/PROOF.md) · [Receipt](normalized/RESULT.json)

## Fractional majorant

The fractional majorant increases the complete rate by 0.00000000000013 over #7863, exactly (650/193996402173)% or approximately 0.00000000335057760205%. The increment over the prior #8026 head is 0.00000000000003, exactly (75/96998201089)% or approximately 0.000000000773210215839%. The new argument applies the existing real-power leaf-count induction to the same physical schedule. It reduces the uniform loss from 3006/H to 2969/H. The ordinary cap is 0.00387992804367877 and the full outer compiler tests 0.00387992804366. [Fixed-word proof](MAJORANT.md) · [Independent exact receipt](MAJORANT.json)

## Original cover proof

The original uniform carrier has N = 2^H with H = 1202400000000000. The retained delayed-cover theorem charges the full fallback by a factor below 1 + 2^−46. Taking d = 1/(H·2^44) gives N^d > 1 + 2^−45. The complete normalized moment is therefore strictly below one after this smaller loss. Evaluating all seven ordinary stages supports the installed BIT cap 0.00387992804364799. The 48-call rational application tests 0.00387992804363 and certifies its original complete rate of 0.00387992804356. [Proof and strict stage checks](PROOF.md) · [Machine-readable receipt](RESULT.json) · [Delayed-cover theorem, §7](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/p104-shared-native-helper-splits/retained/compiler/bit-audit/retained/DELAYED-COVER-BRIDGE.md#7-moment-and-row-stock-consequences)

The native signed crossing is still enclosed by [0.003879928046154, 0.003879928046155]. Giving the predecessor its upper endpoint and deducting only its two fixed losses yields a ceiling of 0.003879928043555 on the old proof. The new complete claim exceeds even this ceiling by 0.000000000000005. Both proofs use the original paid and productive positions, ordinary word, full fallback work, selected prime and excluded catalogue, stock recursion, restored ownership, 451-factor compiler and precision obligations. Improved asymptotic estimates may require larger fixed proof thresholds. The explicit physical realization of #7863's seven stages and nested seed remains conditional. Main selects #7000 separately.

## Replay

Use CPython 3.12 from a clean repository checkout. The package uses the standard library and authenticates a vendored copy of the public #7863 archive. It writes generated files in a temporary directory.

```sh
python3.12 -IB scripts/research_package.py --package research/bit-451-carrier-cover
```

The first scientific marker is `PASS_ORIGINAL_451_SUPPLIER_AND_ACTUAL_CARRIER_COVER`. It requires byte-identical regeneration of the predecessor's complete BIT receipt, including the native signed census and all 36 caller uses. The original cover marker, `PASS_COMPLETE_SIGNED_APPLICATION`, requires the expanded rational audit, 54 strict conditions, four functional checks and agreement with an independent arithmetic proof and separately regenerated application and audit. Controls cover a missing CLEAR, an extra paid term, an insufficient BIT cap, a non-strict ordinary stage and an insufficient cover bound.

The second registered command emits `PASS_COMPLETE_FRACTIONAL_MAJORANT` after reconstructing the supplier, replaying the full application and checking the independent fractional-majorant certificate. Its application SHA-256 is `2d46b81b9f009ec80a21ae1545f975cdf68abcfe4ea2f3f3a6becaf43e107ebf` and its expanded audit SHA-256 is `df50d7caf1239edaad65ed5394e483e9f5b1e804495435d4386c8068cb0d8d97`.

The h=1024 scientific marker is `PASS_COMPLETE_NORMALIZED_MAJORANT`. The normalized application and expanded audit hashes are `cac0e76c9eb370729f35974088b70a57c48238153f99fca69cb113593bc6163b` and `e68fc5f619a25881fb1d6f064f45a4cf8f161545d63c0dd7f550c1f7d48d3aaa`.

The pointwise endpoint marker is `PASS_COMPLETE_INTEGER_SCALE_ENDPOINT`. The endpoint application SHA-256 is `d8afd25d84dd2721549686ee5a03ce5bddcf2a7957037d700e43e23b04f56f7e` and the expanded audit SHA-256 is `af789e7e42411cfbadf411488de43626e6e23a44ccfb7d2027d488066db3691d`.

The third registered command reproduces all three weighted proofs. Look for `PASS_COMPLETE_WEIGHTED_EXITS`, `PASS_COMPLETE_WEIGHTED_MINIMUM` and `PASS_COMPLETE_SECOND_MOMENT`. The last application SHA-256 is `038a693200287638feae8d6888d4834577e3eb4b2d95cd75ea607605f1c989a0` and the expanded audit SHA-256 is `bf063d3cee7cdde73575265d2e73f430f71dd98abf611bd63cddcbc8ed0e78e1`.

The archived source has SHA-256 `5f9d9c378a1bddccb2e42ac6453716fa950f19bd71f6181a9606f5eb68b022b3`. The verifier checks all 202 entries in its source manifest. The regenerated application and audit hashes are `e0a28d730e5a63070221a170c3e5e10abdf4ed552d67fbd47d1f4ec157b736ad` and `51963b588680e3150b97b156a461c9002368c40752b73bc4a6b03f94aca97c0b`. [Exact predecessor archive](https://github.com/CrocSwap/integer-mult-bounds/blob/b3e4412fe01f07dc58305616fabf96345f49a781/research/p104-bit-451-factor-schedule/replay.tar.gz)

## Credit and overlap

Clear1nsight supplied the exact 451-factor word and schedule, the #7830 compiler lineage and the #7973 consumer audit. Ali Romman supplied the earlier dual-supplier construction and paired caller. The retained delayed-cover and ambient-cap authors supplied the fallback inequality and stock lemma. Dugongue and Rohan Arun supplied the #7831 and #7835 cutoff schedules used in the predecessor lineage. Cinna Davis supplied earlier balanced CRT and outer proof work. The inherited source notices accompany the archived inputs. This contribution specializes the existing multiplier inequality to the actual carrier, proves the improved seven-stage rate on the same algorithm and independently replays the resulting application. OpenAI Codex materially assisted the reasoning, implementation and replay. [#7863](https://github.com/CrocSwap/integer-mult-bounds/pull/7863) · [#7973](https://github.com/CrocSwap/integer-mult-bounds/pull/7973) · [#7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830)

The nearest six-stage threshold calculation assumes a different raw invoice, larger carrier and stronger prime criterion. The 480-factor physical realization and the ternary receiver concern other contracts. [#7975](https://github.com/CrocSwap/integer-mult-bounds/pull/7975) · [#7846](https://github.com/CrocSwap/integer-mult-bounds/pull/7846) · [#7945](https://github.com/CrocSwap/integer-mult-bounds/pull/7945)

## Open next questions

The next test is whether a single rational distribution on the 1/16 grid can dominate the complete tilted paid log ranks and admit a power below 31. Bound the raw 451-fold tail at the 15 interior thresholds, charge every split, then check the all-height inequalities. Lower powers under this new comparison remain open. [Higher paid log moments](https://github.com/CrocSwap/integer-mult-bounds/blob/4cf054a50c5718616594ec4ca2c9114278120a8b/research/net-tax-rank-compiler/LOG-MOMENTS.md)
