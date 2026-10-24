# Independent check of #4586: quasipolynomial growth of chronological batch widths

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

mihir-s-05's #4586 (head `aadb7bc5`) proves that #4507's chronological batch widths satisfy `log B_N = O((1+log N)^(d+2))`, where `d` is the number of primes dividing the rank alphabet. That is `exp(O((1+log N)^9))` for raw p7, replacing the inherited `exp(O(N log N))`. #4586 checks its lemmas on an authenticated copy of #4507's own generator. This package checks them with **separately written code**, `flow_widths.py`:
- my default-height flow, written for my #4456 checks of #4436;
- my chronological width recurrence, written when checking #4507.

The raw p7 rule is bound to main's `research/higher-moment-strictification/RESULT.json` (SHA256-pinned).

## Results

All checked claims are confirmed through rank `N = 4000`: 3,880 ranks and 611,342 batch constraints.

- **`B_1000`.** It has **2,524 bits**, as #4586 and #4507 report. `B_4000` has 5,834 bits.
- **Rank descent.** Every recursive rank in `J_n`, both source complements `n−s` and actual exits `e`, is at most `⌊(m−1)n/m⌋` with `m = 121`.
- **(4).** `B_n | L_N^D(n)` holds for every `n ≤ 4000`. This is checked by `D(n)` rounds of gcd stripping, with no factoring. Here `L_N` has 309 bits and `D(4000) = 373`.
- **(2).** The depth bound `D(n) ≤ 1 + ⌊log(n/m)/log(m/(m−1))⌋` holds.
- **Source-state lemma.** The flow's height and complete source census at `n` equal those at `m·t`, where `t` is the largest `Π`-smooth integer at most `⌊n/m⌋` and `Π = {2,3,5,7,11,19,41}` (`d = 7`). This holds for every `n ∈ [121, 4000]`, and every rank in the rule is `Π`-smooth.
- **(5).** `|H(M)| = 27` against the bound 576 at `M = 33`.
- **Explicit exponent.** At `N = 1000`, `D(N)·K_N·⌈log₂ C_N⌉ = 211·32·45 = 303,840`, exactly #4586's stated value.

## Verify

```text
python3 -B research/pr4586-width-growth-check/verify.py
```

This runs in about 25 s with the standard library only.

## Limitations

- **Scope.** The written induction and counting argument are #4586's. This package checks every finite consequence above on a separate implementation, but it does not formalise the proof.
- **Physical contracts.** These are #4507's and #4436's premises, and are out of scope.

## Open next questions

- A lower bound on the actual width growth, to see how loose the quasipolynomial bound is. The bound gives 303,840 bits at `N = 1000`, against 2,524 actual. First step: fit `log B_N` against `log N` over `N ≤ 4000` with the sequence computed here.

Credit: mihir-s-05 (#4586), #4507's width construction and #4436's flow lineage (zxv, Jacob Alan Sussman). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
