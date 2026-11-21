# Conditional κ = 0.00389011519729 (+0.000003105050% over #8027) — normalized uniform bound and same-prime delayed cover

The complete conditional saving increases from **0.00389011507650** on Ali Romman’s #8027 to **0.00389011519729**. The exact gain is 0.00000000012079, or (24158/7780230153)%, approximately 0.00000310504953258804%. Both proofs run on the same signed caller, 768-factor word, finite catalogue, prime condition and restored stock at peer head `fb9b6a7b0d27da1cf98430893a3016bf811e2aa4`. [Exact peer](https://github.com/CrocSwap/integer-mult-bounds/pull/8027)

| Quantity | #8027 | Same-prime delayed cover | Normalized uniform bound plus cover |
|---|---:|---:|---:|
| Complete conditional κ | 0.00389011507650 | 0.00389011517650 | 0.00389011519729 |
| BIT ordinary cap | 0.003890115076583 | 0.003890115176583 | 0.003890115197377 |
| Signed test | 0.00389011507657 | 0.00389011517657 | 0.00389011519736 |
| Uniform debit | 10⁻¹⁰ | 10⁻¹⁰ | 23731/299610000000000 |

The first proof bounds the full fallback at the actual carrier H = 299610000000000 and charges 1/(H · 2³⁸) for delayed cover. It improves κ by 0.00000000010000. The second proof normalizes the paid-leaf potential to (1 + log₂(n)/1024)⁶²³, establishes it for all ranks and certifies the smallest integer debit numerator at that fixed scale, power and H. Combining the two proof changes and repricing all four restored stages adds **0.00000000002079**, or (594/1111461479)% over the first result. The final claim exceeds even the raw upper boundary after charging only the predecessor’s uniform debit by 0.000000000010695. [Cover proof](PROOF.md) · [Normalized proof](normalized/PROOF.md) · [Independent all-size argument](normalized/independent/PROOF.md)

For the first result the independent proof checks the 36-call binary profile, directed raw crossing, both cover estimates and the four restored bootstrap stages. The 48-call rational replay reconstructs the signed application, native action, public outputs, ownership and restoration, ordinary work, precision, tape and common depth. Its 54 strict conditions and four functional tests pass with minimum strict margin 10⁻¹⁵. A separate invoice reconstruction rejects one extra paid rank-one position and a BIT cap set equal to the tested point. The first complete claim exceeds even the old raw upper endpoint less both old debits, with all outer ticks forgiven, by 17981/200000000000000. [Independent proof](independent/PROOF.md) · [Signed result](application/RESULT.json) · [Independent acceptance](independent/ACCEPT.json)

For the combined result a fresh reconstruction verifies the same physical outputs, ordinary costs and compiler guards, rebuilds the signed rank bill from the 48 native calls and their caller, reproduces both earlier admissions, and rejects the cheaper adjacent exponent numerator, a spurious paid rank-one job and a cap equal to the tested point. The fresh full signed result and independent acceptance are separate receipts. [Signed application](normalized/application/RESULT.json) · [Independent acceptance](normalized/independent/ACCEPT.json)

## Clean replay

Use CPython 3.12 and the standard library from the repository root.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-paired-delayed-cover
```

The single command authenticates the 30-file peer package by Git tree and path-keyed SHA-256 and replays both results against the 134-member upstream source closure. It checks the repository’s exact delayed-cover, shifted-log and ambient-cap proofs, regenerates both independent prices for each cap, and rebuilds each complete signed application in sequence. The final scientific marker is `PASS_PAIRED_NORMALIZED_COVER`. The complete registered run took 150.63 seconds locally, including both signed applications and both independent acceptances. The registered time allowance is 540 seconds. Peak memory was unmeasured. [Source pins](SOURCES.json) · [Replay configuration](VERIFY.json)

## Scope and credit

The five inherited conditions cover native action on all columns, owned erasure, compiler transfer, precision and tape accounting, and analytic recovery. The 768-factor BIT word and root rational construction retain their existing interfaces. This package contributes the fixed-carrier estimate, the normalized leaf estimate at h=1024, independently computed prices, and signed applications of both complete caps. Scientific acceptance and selection belong to the maintainers.

Ali Romman supplied #8027’s paired circuits, their composition and application. Clear1nsight supplied the literal compiler, independent readers and audit. The retained bridge and its credited predecessors supplied common-weight cover, fallback pricing and stock. The earlier #8026 proof supplied the actual-carrier comparison. The original LICENSE and PARENT-NOTICE are preserved inside the pinned peer archive. OpenAI Codex materially assisted the proof, implementation and verification. [Predecessor notices](https://github.com/CrocSwap/integer-mult-bounds/blob/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain/PARENT-NOTICE) · [Earlier carrier proof](https://github.com/CrocSwap/integer-mult-bounds/pull/8026) · [Compiler lineage](https://github.com/CrocSwap/integer-mult-bounds/pull/7786)

Jacob Alan Sussman supplied the integer fixed-batch construction, DreamingOfClouds the ambient-cap extension, and zxv the normalized-log proof. Their results supply the source and exit balances, contraction, and shift used here. [Integer ambient-cap flow §6](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/p104-shared-native-helper-splits/retained/compiler/PROOF.md#6-ambient-cap-version-of-the-exact-finite-flow) · [zxv’s normalized induction](https://github.com/CrocSwap/integer-mult-bounds/blob/4cf054a50c5718616594ec4ca2c9114278120a8b/research/net-tax-rank-compiler/SHIFTED-LOG.md)

## Open next questions

Can the actual weighted exit distribution reduce the uniform charge further? First bound its complete paid moment at the existing carrier and word, then price one fixed smaller log power with the same stock and signed obligations. Only the present h=1024, p=623 construction was advanced.
