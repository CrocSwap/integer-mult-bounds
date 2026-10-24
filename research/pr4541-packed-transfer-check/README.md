# Independent check of #4541: packed Word RAM transfer, §1–§3

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Dugongue's #4541 (head `46ca24a8`) proves an informal bounded-word RAM bound `O((T+n+m)/log(n+2) + (n+2)^(1/16) log(n+2))` for a fixed TM. It uses generated tables of r-step local transitions over packed tape words. With a conditional TM multiplication bound, it gives `O(n/(log n)^κ)` RAM operations. This package checks the parameter arithmetic of §1 and the macro-step invariant and halting semantics of §§2–3. The verifier was written from #4541's `PROOF.md` text alone, vendored here as `PR4541-PROOF.md` with blob `43a6afbe` and its SHA256 pinned. Nothing is imported from #4541's code.

## Results

All checked claims are confirmed.

**A. §1 parameters.** These are exact integer checks over 720,240 cases: `k ≤ 8`, `c ∈ {2, 4, 8}`, `s ≤ 10`, `0 ≤ λ ≤ 3000`.
- `16b ≤ λ` whenever `λ ≥ max(64Kc, 64s)`. So all `2^b` table rows number at most `(n+2)^(1/16)`, and setup `r·2^b` fits the startup term.
- `128Kc·r ≥ λ` for `λ ≥ 1`, so `r = Θ(log n)`.
- `L = 2r+1 ≤ B = 4r`, so a window spans at most two words.
- The codec exponent satisfies `cr < b`.

The origin `H = 2^(a+dℓ)` satisfies `H ≥ 2^a (n+2)^d > 2·2^(a−4)(n+2)^d` for `a = 8`, `d ≤ 3` and all `n < 2^12` (12,288 cases). So every coordinate `H+z` with `|z| ≤ T+r` stays positive without truncating subtraction.

**B. §§2–3 by an independent packed simulator.** The simulator follows the proof's description:
- `B = 4r` c-bit fields per word, with random dirty bits above the fields;
- tapes interleaved at `dataBase + J·u + i`;
- signed positions at origin H;
- `L`-cell windows read across at most two words, with all reads done before any write;
- a lazily generated local table of up to r literal steps, with invalid patterns treated as halt;
- the update `newHead = oldHead + localHead − r`.

It ran 486 random k-tape machines (`k ≤ 3`, `Q ≤ 5`, alphabet ≤ 4, `r ∈ {1, 2, 4}`) against direct execution:

| Case | Count | Compared against direct execution |
|------|------:|-----------------------------------|
| Halting runs | 263 | Exact state, transition count, heads and every tape cell |
| Nonhalting runs | 223 | Exact state, count and heads at every macro boundary |
| Halts found at an epoch boundary with elapsed zero (r > 1) | 46 | |
| Runs that visit negative coordinates | 323 | |
| Windows that cross a block boundary | 11,090 | |

- **Dirty high bits.** These are preserved in every word.
- **Rejection control.** Writing windows back one cell off is caught in 19 of 20 runs.

**C. Binding.** The verifier checks that the vendored `PROOF.md` states the formulas it tests verbatim (9 statements).

I also replayed #4541's registered package at its head: `PASS_REGISTERED_RESEARCH_PACKAGE research/packed-ram-speedup outcome=partial` in 4.3 s.

## Verify

```text
python3 -B research/pr4541-packed-transfer-check/verify.py
```

This runs in about 2 s with the standard library only.

## Limitations

- **Not covered:** the packed IO codec (`PACKED-IO.md`, §4), the corollary's reliance on a TM multiplier with the stated envelope, and the RamStd lowering. The table here is generated lazily, for the keys actually used. #4541 generates every row and charges `r·2^b`; part A checks only that this charge fits.
- **Finite and random.** The simulator checks a finite random family. The universal statement rests on #4541's written argument, which these runs corroborate but do not replace.

## Open next questions

- An independent check of the packed IO codec of §4 (reservoir continuity across operands, first-blank output decoding and partial chunks). First step: a separate codec over random operand lists, compared against direct binary encoding.

Credit: Dugongue (#4541), Hopcroft, Paul and Valiant (1975) for the classical method. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
