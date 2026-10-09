## Concurrent construction and exact refinement

[PR #63 by Dominik Scholz](https://github.com/CrocSwap/integer-mult-bounds/pull/63), at [`aa7701b68540b7863d3b66a414e4319915d6282d`](https://github.com/DominikScholz/integer-mult-bounds/tree/aa7701b68540b7863d3b66a414e4319915d6282d), independently publishes the same composition of the PR62 pair graph with PR60's rank-first reclamation. Both decompressed words are byte-identical to the independently generated words used here; both complete axis profiles and the finite bridge also agree. The comparison is recorded in `pr63-comparison.json`. No exclusive discovery or priority claim is made for this construction.

This package adds independent source/scatter/charge binding, exact arithmetic, scoped Lean proofs, and the refined conditional witness

\[
\kappa=\frac{20411033624901463}{400000000000000000000}
=5.10275840622536575\times10^{-5}.
\]

It exceeds PR63's \(5102757/10^{11}\) by exactly \(5624901463/400000000000000000000\), approximately \(1.40622536575\times10^{-11}\). This numerical increment over PR63 changes only the rational characteristic/assembly parameters. The physical construction is identical. The selected bit saving is \(63787735011827529/1250000000000000000000\), with positive assembly backoff \(10^{-18}\).

## A profile comparison valid for every exponent

Relative to [PR62's original stacked profile](https://github.com/ikeboy/integer-mult-bounds/tree/ad0f25ff7b23cff7f08ad237c2254e6ecf74257e/research/pair-assembly/frame), each new-minus-old axis profile \(d_t\) has zero rank mass and nonpositive capped sums \(C_k=\sum_t d_t\min(t,k)\). The first caps are strictly negative: \(-176\) for \(h=23\), and \(-372\) for \(h=25\). For \(f(0)=0\), discrete summation gives

\[
\sum_t d_t f(t)=\sum_{k=1}^{T-1}
\bigl(2f(k)-f(k-1)-f(k+1)\bigr)C_k,
\]

because the linear term vanishes with the rank mass. Taking \(f(t)=t^{1-u}\), \(0<u<1\), makes every curvature positive, so the difference is strictly negative. Positive replication and the unchanged exterior/data terms preserve this comparison. Thus the ranked construction has a strictly smaller full characteristic than PR62's original stacked construction for **every** \(0<u<1\), at the same \(W=137151806\). This does not compare two different constructions between this package and PR63: their words and profiles coincide.

`CappedMass.lean` proves the finite expansion, signed-profile comparison, real-power curvature and the two literal cap certificates. The concrete-profile-to-serialized-word correspondence is checked separately. The other Lean files cover dirty-wrapper semantics, equal-frame reindexing, an assembly-specific ceiling, a scalar rounded recurrence and exact assembly arithmetic. They do not formalize the full compiler, finite-tape machine or multiplication theorem.

## Attribution and limits

The interval strips and core-aware pair graph are [Avi Eisenberg / ikeboy's PR62](https://github.com/CrocSwap/integer-mult-bounds/pull/62), with disclosed Anthropic Claude assistance. The joint-frame compiler and paid reclamation are [eumemic's PR57](https://github.com/CrocSwap/integer-mult-bounds/pull/57), with OpenAI Codex assistance. Descending-current-frame-rank slot priority is [Chafik Boukhalfa's PR60](https://github.com/CrocSwap/integer-mult-bounds/pull/60), with OpenAI Codex assistance. Dominik Scholz's concurrent PR63 discloses substantial OpenAI GPT-6 Astra / Codex assistance. This independent verification and formalization was developed with substantial OpenAI Codex assistance.

The inherited work of Rohan Arun, RaD / hipotures, icekylinx, Zhihao Chen, James Chang, Dominik Scholz, Aurel Prosz / Paureel, Swapnil Jain, Douglas Colkitt and other credited contributors remains attributed in the pinned source notices. The dirty-wrapper argument is inherited mathematics, newly formalized here. Alejandro Zarzuelo Urdiales's Gaussian finite-tensor/precision work and PR61 refinements, and Ryan S's historical Lean certificates, retain their separate credit. The [original OpenAI work](https://github.com/openai/math) and Harvey–van der Hoeven analytic results remain foundational dependencies. Retain all source-specific notices and Apache-2.0 terms.

The displayed multiplication exponent is conditional on the inherited all-size framed/residual compiler, physical routing and finite-alphabet multitape implementation, analytic resampling, precision, prime setup and exact recovery. Finite replay, rational arithmetic and the listed formal statements do not discharge that complete chain. No practical speedup, global optimality or human peer-review claim is made.
