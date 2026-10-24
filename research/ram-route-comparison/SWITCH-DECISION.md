# A fair decision about the Word RAM backend

**Recommendation:** develop the native Word RAM implementation while retaining the packed TM-derived backend as a correctness and cost reference. Current evidence supports the new backend as a constructive alternative; it does not yet establish a superior native exponent against the best eligible packed transfer, a practical speedup, or a reason to discard the reference backend.

Prepared for Dugongue with substantial OpenAI Codex assistance, 2026-10-22. This note distinguishes proved upper bounds, measured performance and lower bounds.

## Compare the same task and instructions

Use packed binary operands of at most n bits and return their exact product in at most 2n bits. Both backends run on one bounded-word RAM with w = C log(n+2), where C is a fixed sufficiently large constant. Charge all input conversion, preparation, allocation, routing, arithmetic, restoration, recovery and output. A word instruction multiplies only bounded-size words. It does not multiply arbitrary n-bit integers or operate exactly on unrestricted complex numbers.

| Backend or theorem | Charged complexity | Meaning |
|---|---|---|
| Conditional multitape theorem | O(n (log n)^(1−κ)) tape steps | A different cost model; not the fair direct RAM competitor. |
| Packed transfer, PR #4541 | O(n / (log n)^κ) RAM operations | Preserves the supplied TM κ, including packed input/output and fresh table setup. |
| Native Gaussian assembly, PR #4635 and successors | O(n / (log n)^κ) RAM operations | Uses native arithmetic, routing and analytic recovery; no TM simulation in its execution. |
| Classical complex FFT on Fürer’s log-RAM | O(n) RAM operations | Published baseline; ordinary word packing alone is not a new κ mechanism. |
| GMP on an actual fixed-word computer | Runtime depends on input size, thresholds and machine | Appropriate for empirical claims over stated sizes, not a substitute for a growing-word asymptotic proof. |

PR #4541’s public statement pays O((T(n)+n+m)/log(n+2) + (n+2)^(1/16) log(n+2)) for a fixed finite machine with a known polynomial envelope and output cap m. For T(n) = O(n (log n)^(1−κ)), m ≤ 2n and 0 < κ < 1, this yields O(n / (log n)^κ). Its core does not require word MUL/DIV, so it remains an available competitor in the stronger RAM that permits them. Comparing native arithmetic to an unoptimized one-tape-step-per-RAM-instruction simulator would therefore omit an existing relevant competitor. Source: [PR #4541](https://github.com/CrocSwap/integer-mult-bounds/pull/4541), whose published construction credits Hopcroft–Paul–Valiant’s logarithmic simulation and explicitly handles packed IO.

For a shared admitted supplier exponent κ, the packed transfer and native assembly presently have the **same stated asymptotic class**. A stronger κ available to one route must first be checked for transfer eligibility on the other. A small reserve tightening in a source supplier must not be counted twice as an architectural advantage. Native execution can remove TM-specific obligations or avoid a BIT supplier, but that is a scope benefit until it changes the complete complexity guarantee under comparable assumptions.

## A positive sufficient criterion for a stronger guarantee

Suppose one actual native algorithm has a proved complete cost upper bound A(n) = a n / (log n)^κ_N and an eligible packed reference has a proved complete cost upper bound B(n) = b n / (log n)^κ_P, with positive fixed a,b and κ_N > κ_P. Include setup and IO in these bounds, or prove they are absorbed by the same bounds. Then

    A(n) / B(n) = (a/b) (log n)^−(κ_N−κ_P) → 0.

This proves a strictly stronger asymptotic **upper-bound guarantee** for the native construction. It is already a sound complexity-based reason to prefer that proved guarantee. It does not prove actual running-time ratio T_native(n)/T_reference(n) → 0: two upper bounds do not determine that ratio, and the reference might run faster than its stated bound. An actual ratio conclusion additionally needs a suitable reference lower bound, a tight cost characterization, or a direct algorithm-specific comparison.

The proof of the displayed limit is elementary: put Δ = κ_N−κ_P > 0; log n tends to infinity and x^−Δ tends to zero. For any desired envelope ratio 0 < ρ < 1, the explicit sufficient condition is log n ≥ (a/(ρ b))^(1/Δ). Without proved numerical constants and valid cutoffs, this is not a usable practical crossover. None is claimed here.

A sufficient research deliverable for this criterion identifies the actual native program or constructive family, exact changed paid mechanism, complete cost invoice, common instruction model, exact predecessor comparison, coefficient/prefix precision bounds and inherited assumptions. It then verifies the strict exponent gap. The criterion is positive and constructive; it does not assert that no other algorithm can do better.

## What would justify a practical replacement

Produce two complete exact-product implementations and compare them on the same input representation, compiler settings, hardware and thread budget. Include one-shot setup in the one-shot measurement; if a persistent context reuses tables, report its preparation separately and state the batch size used to amortize it. Check every computed product against an independent exact oracle outside the timed region. Use repeated paired trials, report distributions and retain raw observations, rather than timing only a favorable primitive.

Use geometrically spaced sizes plus dense samples around algorithm thresholds; include zero, sparse, random, maximal-digit, unbalanced and carry-heavy inputs. Record peak memory and failure/cutoff behavior. Avoid source-path, hostname or user-account metadata in public benchmark artifacts. A local Gaussian kernel improvement or certificate-replay speedup is not a complete multiplier benchmark.

These choices are motivated by actual implementation behavior: GMP selects among seven multiplication families using size thresholds, and its documentation identifies allocation and call overhead for small operands. Its FFT implementation has size rounding and parameter transitions that produce step-like timings. See the primary [GMP multiplication documentation](https://gmplib.org/manual/Multiplication-Algorithms), [FFT documentation](https://gmplib.org/manual/FFT-Multiplication), and [efficiency discussion](https://gmplib.org/manual/Efficiency). The protocol above is our proposed fair comparison; the GMP documentation is not being cited as an endorsement of this project’s algorithms.

At present there is no complete practical native multiplier, validated usable crossover or end-to-end comparative benchmark in the inspected deliverable. Reporting those absences is a limit on the recommendation, not a standalone research result.

## Why native work remains useful

The native construction offers a direct implementation route on the machine the user wants to target. It permits experiments with bounded-word arithmetic, matrix-boundary kernels, explicit coefficient reuse and practical memory layouts without simulating tape transitions. Its complex-only supplier interface may admit progress that a currently available TM assembly cannot yet use. Retaining both backends lets future work exploit those opportunities while preserving a runnable comparison once complete implementations exist. This is a recommendation to pursue and compare the native backend, with a concrete stronger-guarantee criterion, not a claim that the existing equal-κ bound already compels an exclusive switch.

## Predecessor credit and search limits

Credit Dugongue’s PR #4541 packed transfer and PR #4554/#4630/#4635 native adapters and assembly; Cao Yifan’s #4610 word; Cinna Davis and the #4470 supplier/controller lineage; the retained Problem 1.8 Word RAM sources; Hopcroft, Paul and Valiant; Fürer; Harvey and van der Hoeven; and all source-specific credited contributors. Independent checks #4552 and #4553 concern parts of #4541 and do not replace a universal proof audit.

Fürer’s primary [2014 log-RAM paper](https://arxiv.org/abs/1402.1811) separates O(log n)-bit unit-cost arithmetic from refined depth costs and proves the classical O(n) multiplication baseline. It does not show that this conditional native construction is faster in practice. The companion literature search covered 43 recorded queries and selected primary papers/Lean sources; neither this note nor that search establishes exhaustive worldwide priority or an optimal RAM lower bound.
