## Produce both low digits and exact carries for generated binary routes

This sequential follow-up to #8092 supplies a local interface left open by its generated-word ledger: produce the canonical new low digits and fused dyadic carry from the actual elementary alphabet, with explicit access, temporary data and integer widths. **No new kappa or complete canonical assumption removal.**

### Exact contribution

For every finite emitted right word S, odd q>=3 and supplied canonical low matrix g0, the producer returns `h0=g0 S mod q` and `C=(g0 S-h0)/q`. Source #8092 is pinned at `6a3437d1cd94dc4e1792f4052511af6160120bf9`; canonical base remains `e54523517d0f03e58352e647c403a5af3e525a57`.

The two-pass finite-control specification emits both outputs for all 94 addition coefficients and 15 scales. First-pass state has a sufficient 388-bit logical encoding per fixed column type (plus a fixed finite tag for a shared dispatcher), with carry numerators in [-54,54]. A second bounded-state pass emits every canonical padded low bit, including the final denominator flush. These are specification bounds, not Python memory figures or measured literal-graph execution.

For m nonswap operations, the fused denominator exponent is at most 5m and signed arithmetic work fits 6m+5 bits. Conservative sequential bit work is `O_source(N^2(ell+1)[B+W+log(2N)]^2)` for total length ell and radix width B. Source reads, extraction, local output, numerator arithmetic, temporary retirement and descriptor access are charged. The exact inverse gets a separate execution/width ledger and uses committed low digits.

A complementary theorem proves that for every odd q>=5 of bit length B, one-pass synchronized LSB input with append-only LSB output of canonical x+y modulo q requires at least B-2 bits of retained state. The construction exhibits 2^(B-2) unreadable-first-output prefixes distinguished by a common continuation. This is an access/output-model bound, not a route impossibility theorem.

### Novelty and credit

Ali Romman's #5841 already gives the low/high formula, cocycle, inverse and table-free whole-word evaluation. #6474/#6503 already produce bounded carry packets from interleaved bits. The additions here are the actual second output stream, source-alphabet construction and generated-word width/access bill. Nick Petalas's serialized-carry cut supplies the state-distinguishability method, under a different carry-only serialized contract. Classical finite-state arithmetic is credited, not claimed as a new method.

### Reproduction

```sh
python3 -B research/generated-route-two-output/check.py
python3 -O -B research/generated-route-two-output/check.py
```

Expected marker: `PASS_GENERATED_TWO_OUTPUT_CARRY`. Eight source files have Git-blob and SHA-256 pins. Author checks cover 17,411 local cases, all 109 types, 40 streams through 4,097 bits, 300 generated rows, 900 full-width reconstructions and 300 inverse checks. The complete 134-coordinate stage covers 268 rows/35,912 coordinates. The one-pass cut checks 5,460 prefixes at all 126 odd radices from 5 through 255. Thirteen controls cover flush, signed-floor, denominator-growth, chronology, stale-input and domain failures. Independent review and registered integration receipts must be included before publication.

### Remaining obligations

The producer accepts supplied low rows. It does not construct the global payload permutation, enumerate GL, move high/spectator fibres, restore recursive owners or reprice the native service. Scratch reset is destructive overwrite. No full physical multiplier, hosted CI success, human review or proof-kernel acceptance is claimed. Selected kappa remains conditional at 0.00363005817.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. Credit Ali Romman (#5841, #6474, #6503, #7828), Nick Petalas, #7840's selected native work, #8092's dyadic/generated-route contributors and the retained ordered-affine/full-GL lineage. Source notices and Apache-2.0 attribution are preserved.
