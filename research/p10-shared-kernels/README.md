κ = 7.68257328708259e-4

# Shared-donor kernels after the frozen p10 composition

This conditional finite construction certifies

`κ = 768257328708259 / 1000000000000000000`.

It improves on [PR317](https://github.com/CrocSwap/integer-mult-bounds/pull/317)'s `7.6817007781759e-4` by `8.7250890669e-8` (about **0.01136%**). The bit supplier still binds; the freshly regenerated PR315 complex supplier remains at `772714351296671/10^18`, including its full bad-class fallback. These are asymptotic exponent savings, not measured multiplication speeds.

PR317 is frozen at `0a0b61a7f4601a96036af8bb6a6338c58f035d2e` and vendored unchanged. This package runs its complete verifier fresh, then appends **90 additional rank-one kernel entries** to its final scalar word. The entries share **106 distinct donors**, with pivot and donor sets disjoint. Their exact target-prefix response identities and both reflected frame ledgers are checked on that literal word. The original 540 entries remain in place, giving 630 in total.

Shared donors amortize the setup-frame cost of several kernel pivots. Selection used common-frame kernel groups, alternate response bases, maximum-weight closure and compatible-group packing. Admission requires no claim that the search was optimal: every chosen relation, cut, source span, frame path, scalar column and final cost is recomputed.

## Reproduce

Python 3.11+ with SymPy 1.14.0, a C++17 compiler, and Boost headers:

```sh
python3 -m pip install -r research/p10-shared-kernels/requirements.txt
python3 -B research/p10-shared-kernels/verify.py --output /tmp/p10-shared-kernel-proof --cxx g++ --boost-include /usr/include
```

Use a fresh output directory outside the package. The run is entirely offline. The manifest pins all source files, selections and the unchanged predecessor manifest; its integrity is checked before and after replay. The new stage uses the native binaries compiled during that fresh predecessor run, then reruns complete admission on the changed word.

## Final accounting

| Quantity | Frozen PR317 | This construction |
| --- | ---: | ---: |
| Rank-one kernel entries | 540 | 630 |
| Scalar records | 384,471 | 384,591 |
| ADDs | 335,240 | 335,264 |
| Unit-expanded ADDs | 337,160 | 337,184 |
| Local positive-rank calls | 48,042 | 48,138 |
| Local paid rank mass | 180,270 | 180,180 |
| Literal stock | 660,690 | 660,420 |
| Normalized stock | 132,138 | 132,084 |
| Banks per stage | 86,058 | 86,004 |
| Changed projector charts | 3,752 | 3,937 |
| Computed payload bits | 90 | 94 |

The final word SHA256 is `668fab1ae01c69181cd7b182c0b66ca106aa3dd57f756b31d661bc7822b4cb05`. Both local directions replay all 10,150 formal columns, checking the required target map and restoring every source and dirty helper, and the complete five-stage replay checks all **12,070 global columns**, including **8,230 independent dirty helpers**. The source-span audit checks 376,244 operand incidences exactly.

The residual census is `{3:310,4:960,19:630,20:6330}`. All **2,469,000** helper/replica/stage assignments are enumerated at width 100 with 60 replicas. The 90 new entrances reuse existing frames, so the complete construction still has **390 new exact frames** relative to PR315. Its **3,937 changed projector charts** use at most 139 factors; the inherited source has a 150-factor bound and the invoice retains the conservative 787-factor normalizer.

The full literal paid profile has **14,902,200 children**, rank mass **65,919,600**, and deficit **122,400**. Two independent exact moment engines include the entire `10^-16` fallback and admit bit coarse saving `38442400107729/50000000000000000`. Three completed ordinary levels feed all **47 strict outer assembly constraints**, and the adjacent grid points are rejected.

The finite invoice pays **389,016,851,400 selector calls** and counted primitive coefficient **25,380,271,118,580,401**, below `2^80`. The actual cancellation-free signed prefix bound is 94 bits, below the retained 104-bit allowance. The full paid histogram and unit expansion are read from the final binary, not supplied by the selection.

## Scope and attribution

This is a source-bound conditional construction under the inherited all-size compiler, weighted-chart, restored-row, selector, routing, prime-supply, complex-lifting, precision/recovery and analytic-transfer interfaces. The kernel stage preserves the F₂ target map; it does not claim signed-integer endpoint equivalence. Actual signed coefficients and prefix bounds are separately recomputed. No unconditional multiplication theorem, new Lean build or runtime benchmark is claimed.

Prepared for eumemic with substantial OpenAI Codex assistance. See `PROOF.md`, `NOTICE.md`, and all preserved predecessor notices.
