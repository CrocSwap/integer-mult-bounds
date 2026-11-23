# Two-output production for generated binary route words

This source-bound follow-up to #8092 produces canonical new low digits and exact dyadic carries from its actual elementary-word alphabet. The whole-word carry identities are credited to #5841; bounded carry-only state machines to #6474/#6503. Read [the proof](PROOF.md) for the new output construction, generated-word binding and limits.

For supplied canonical g0 and odd q>=3, the producer returns h0=g0 S mod q and C=(g0 S-h0)/q, preserving g0. At the actual 94-addition/15-scale alphabet, the first pass has a sufficient 388-bit logical state encoding per fixed column type (a shared opcode/coefficient dispatcher adds a fixed finite tag) and local carry numerators in [-54,54]. A second bounded-state pass emits the complete padded low word. This is a specified finite controller, not an executed literal tape graph or Python memory measurement.

For m nonswap instructions, fused carry denominators have exponent at most 5m and signed work fits 6m+5 bits. At total word length ell, dimension N and radix width B, conservative sequential bit work is O_source(N^2(ell+1)[B+W+log(2N)]^2). It includes local source access, temporary low words, numerator scans and destructive scratch retirement. Payload-fibre permutation, low-type selection and parent-owner return remain separate services.

A complementary theorem explains the pass choice. For every odd q>=5 with B bits, deterministic single-pass interleaved reading with append-only LSB output of canonical modular addition needs at least B-2 bits of retained state, including control and workspace. It applies already to the coefficient-one shear x <- x+y. It does not exclude rereads, revised output, carry-only production or different output order.

## Reproduce

From this directory:

```sh
python3 -B check.py
python3 -O -B check.py
```

Use `--output /tmp/carry-evidence.json` for a disposable receipt. Expected marker: `PASS_GENERATED_TWO_OUTPUT_CARRY`. Registered replay and independent reviewer evidence are added at integration. [ORIGINS.json](ORIGINS.json) authenticates eight source files by Git blob and SHA-256. The finite counts in [EVIDENCE.json](EVIDENCE.json) corroborate the written universal claims.

## Open next questions

Install these records in one actual recursive owner bank, including high/spectator fibre transport, low-type ordering, original-owner return and cleanup. Then compare complete cost with the retained route tariff. Descriptor production alone does not demonstrate a faster full route or close `owned_erasure` or `precision_tape`.

No new kappa or complete canonical assumption removal is claimed. Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`, selected conditional kappa 0.00363005817. Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. Source authors are credited in the proof and notices. Independent human or formal-kernel acceptance is not claimed.
