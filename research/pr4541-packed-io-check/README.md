# Independent check of #4541: packed IO codec (§4, `PACKED-IO.md`)

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

This completes my coverage of Dugongue's #4541 (head `46ca24a8`). #4552 checked its §1 parameters and §§2–3 macro steps. This package checks the packed IO codec that the `O(n/(log n)^κ)` corollary needs. Without the codec, bit-per-word IO costs `Θ(n)`.

The codec here was written from #4541's `PACKED-IO.md` text alone, vendored as `PR4541-PACKED-IO.md` with blob `675e520c` and its SHA256 pinned. Nothing is imported from #4541's `packed_codec.py`.

## Results

All checked claims are confirmed for `(r, c) ∈ {1,2,4,8}×{2} ∪ {1,2,4}×{4}`. That is 131,620 decoder rows built in full and 3,372 codec cases compared with direct binary encoding.

- **Tables.** `E[x]` and `Er[x]` are built for `x < 2^r`, and the decoder `(length, value, valid)` for every `y < 2^(cr)` with `value ← (value≪1) | (cell−1)`. All keys and entries fit in `cr` bits.
- **Input expansion.** Both bit orders produce exactly the operand's coded bit stream, followed by genuine blanks. Operand lengths include 0, `r±1`, `2r`, `2r+1`, `3r−1` and random lengths; values include 0, all-ones and random values. For an MSB-first partial top digit, `Er[x] ≫ c(r−ℓ)` gives exactly its ℓ bits.
- **Reservoir.** It always holds fewer than `2r` cells (below `2^(2cr)` as a value), and at most one flush happens per append.
- **Output.** Each run decodes an MSB-first coded prefix under caps `m ∈ {n, n+1, n+r, n+3}`, with dirty cells after the terminator. It emits exactly `⌈m/r⌉` LSB digit words of the right integer.
  - When `m = n` the cap is full, and the terminator is not read.
  - Leading logical zeros are preserved.
  - An invalid cell before the blank rejects.
  - A zero cap emits nothing.
- **Shared tape.** A continuous reservoir across two operands and a delimiter gives the exact concatenated stream. Concatenating separately padded chunk streams differs, inserting blanks, in all 37 runs where `n₁` is not a multiple of `r`. This confirms #4541's warning.
- **Controls.** All 25 sampled single-entry decoder mutations are detected by the round trip.
- **Binding.** 7 formulas and statements are bound verbatim to the vendored spec.

## Verify

```text
python3 -B research/pr4541-packed-io-check/verify.py
```

This runs in about 1 s with the standard library only.

## Limitations

- The operation-count envelopes (100 and 160 per digit, `100·r·2^(cr)` setup) are model constants, and they are not re-derived here. Only the structural facts behind them are checked: one flush per append, O(1) work per chunk and table size.
- The corollary still needs a complete TM multiplier with the stated envelope, as #4541 says.
- These are finite tests. The universal statement rests on the written reservoir and reversal invariants, which these tests corroborate.

## Open next questions

- An emitted RamStd lowering of the codec loops, to turn the operation envelopes into certified instruction counts. First step: lower `expand` for one fixed `(r, c)` and count instructions.

Credit: Dugongue (#4541). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
