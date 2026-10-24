# Independent check of #4538: native-layout cost theorems 1–4

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Dugongue's #4538 (head `dffc7939`) states four Word RAM cost theorems for the monomial Clifford layer, in `cost/COST-THEOREMS.md`:
- affine record permutations in at most `8NL + 40N + 8` instructions;
- streaming quadratic Z/4 phases;
- limb negation for Gaussian-unit phases;
- a metadata compiler for X/S/Z/CNOT/SWAP/CZ words that keeps the global phase.

This package checks all four with separately written code. The theorem text is vendored as `PR4538-COST-THEOREMS.md` (blob `a5d940b2`, SHA256-pinned). Nothing is imported from #4538's `streaming_affine.py`, `quadratic_phase.py` or `monomial_metadata.py`.

## Results

All checked claims are confirmed.

- **Theorem 1 (affine permutation).**
  - **Count arithmetic.** Literal increments give the flip count `T = 2N − r − 2` for `r ≤ 8`, and the identity `8NL + 9N + 11T + 3 = 8NL + 31N − 11r − 19 ≤ 8NL + 40N + 8` holds.
  - **My own program.** I wrote a separate fixed program (30 instructions, plus a HALT) on a small additive/Boolean RAM with truncated SUB and no multiplication, division or right shift, using the stated macro costs (XOR 4, MOV 2, JNZ 2, others 1). Over 36 runs (`r ≤ 8`, `L ∈ {1, 2, 3, 5}`, random invertible `A` and offset `b`), it writes `dst[(Ax⊕b)K + j] = src[xK + j]` exactly. It preserves source, table and destination padding cells, and uses at most **0.82×** the bound.
  - **Control.** A mutated program (XOR → ADD in the carry chain) is rejected.

  So the bound is attainable by an independent implementation, not only by #4538's.
- **Theorem 2 (quadratic phases).** The update `d = (a_j + 2g_j) mod 4`, applied with `+d` on a 0→1 flip and `−d` on a 1→0 flip, with `g ^= Bcol_j`, reproduces `q(x)` at all 3,012 visited `x`. Here `r ≤ 8`, there are random `a` and symmetric zero-diagonal `B`, and there are fewer than `2N` flips.
- **Theorem 3 (limb negation).** Digit complement plus carry equals negation modulo `2^(kL)` in 800 random cases (`k ∈ {1, 2, 3, 8, 16}`, `L ≤ 5`), with every temporary `≤ β`. The four Gaussian-unit cases equal multiplication by `i^q`.
- **Theorem 4 (metadata compiler).** My compiler, written from the stated update rules, satisfies `word|x⟩ = i^(c+q(x))|Ax⊕b⟩` for every basis state. This holds on 360 random words (`r ≤ 6`, up to 40 gates of all six types), against a literal Gaussian-integer state-vector interpreter. `B` stays symmetric with zero diagonal. The X-then-S control needs `c = 1`, and dropping `c` is caught.
- **Binding.** 9 formulas are bound verbatim to the vendored text.

I also replayed #4538's registered package at its head: `PASS_REGISTERED_RESEARCH_PACKAGE research/word-ram-transfer outcome=partial` in 9.1 s.

## Verify

```text
python3 -B research/pr4538-cost-theorems-check/verify.py
```

This runs in about 1 s with the standard library only.

## Limitations

- **Out of scope:** #4538's TM emitter, the Lean bridge, and packed tapes. My earlier #4552 and #4553 cover #4541's packed tapes, which follow #4538's model.
- **Macro costs.** The macro expansion costs (XOR 4, MOV 2, JNZ 2) are taken as stated for `Lax13.Ram`, not re-derived from the Lean source.
- **Finite checks.** The universal statements rest on #4538's written inductions, which these finite checks corroborate.

## Open next questions

- An emitted `Lax13.Ram` program for Theorem 1, with resolved labels and an exact instruction count checked against `RamStd.step`. First step: lower my 30-instruction program or #4538's 30-macro program, and count expansions mechanically.

Credit: Dugongue (#4538). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
