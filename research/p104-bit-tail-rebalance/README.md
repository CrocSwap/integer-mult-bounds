# Conditional κ ≥ 0.00387992802506 from rebalancing the P104 BIT tensor schedule

This continuation raises the exact-head finite conditional lower bound from 0.00387990740712 to **0.00387992802506**, a gain of **0.00000002061794**. It inherits the 48-call rational and 36-call BIT words and recompiles the BIT tensor schedule. The admitted ordinary BIT saving is **0.003879928025145**. [PR #7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830)

The conditional conclusion is $T(n)=O(n(\log n)^{1-\kappa})$ under the five inherited premises: native_all_columns, owned_erasure, compiler, precision_tape and analytic_recovery. Two implementations passed the complete finite application. Lean 4.33.0 checked the rational tail certificate and cutoff comparison. The strict-separation theorem uses propext, Classical.choice and Quot.sound. The cutoff comparison has an empty axiom list.

## Tensor certificate

Set $C=0.003879928045154$, $t=1-C$, and $M_H(s)=\sum_r H_r r^s$. Let $P,T$ be the complete paid and productive histograms. Use tensor power $v=416$, paid cutoff $J=10^v$, and productive floor $B=16^v$. Specialize the lower complete targets to owned zero and retain all intermediate queries. Split every paid tuple into rank-$J$ calls and at most one residual call on disjoint axes. The tuple using paid grade 14 in all 416 factors needs one call at cutoff $15^{416}$ and several at cutoff $10^{416}$.

For a paid rank $R>J$, its split moment is at most $2R J^{t-1}\le 2R^{t+u}J^{-u}$ when $u\ge C$. A discarded target of rank $R<B$ costs at most $R^{t-w}B^w$ when $w>0$. The tensor product factors the moments, so the fraction spent on paid work and discarded targets is at most

$$
\alpha^v + 2\gamma^v + \lambda^v,\qquad
\alpha=\frac{M_P(t)}{M_T(t)},\quad
\gamma=\frac{M_P(t+u)}{10^u M_T(t)},\quad
\lambda=\frac{16^w M_T(t-w)}{M_T(t)}.
$$

Use $u=11/50$ and $w=3/10$. The outward rational upper bounds are $999999999998669/10^{15}$, $473009043448109/(5\cdot10^{14})$, and $94357873737351/10^{14}$. Bernoulli's inequality gives $\alpha^v\le 1/(1+v(1-\alpha))$. The resulting normalized surplus exceeds 0.000000000333056567.

On the full working ambient $134^{416}$, the shifted logarithm factor is $5/6$, the logarithm power is 44, and $\log_2 N=209400000000000$. The predecessor independent schedule uses tensor power 768 and logarithm power 621. Uniform and delayed-cover losses are each $10^{-11}$, with $2^{45}10^{-11}>256$ and the inherited prime condition. Four strict stock stages start at 0.00385248 and use stock exponent $1/250$. Each admits a price below $(1-1/250)(C-2\cdot10^{-11})$ plus $1/250$ times the previous price.

The rational raw crossing lies in $[0.00388013644474, 0.00388013644475]$. The BIT raw crossing lies in $[0.003879928046154, 0.003879928046155]$ and limits the gain from this fixed BIT profile under the signed-moment criterion. The rational invoice and full ordinary bill match the pinned #7830 receipt.

## Reproduction

From the package directory, use CPython 3.12 or 3.13 and a fresh output directory.

    python -IB verify.py --work p104-source-cache --out p104-replay --fetch
    lean BitTailCertificate.lean

The verifier authenticates 12 explicit predecessor inputs and 127 locked dependencies. It checks both 680-input BIT orientations and both 38-dimensional caller orientations, complete charges and retirement. It independently replays both 1,289-input rational orientations, the expanded scalar plans, complete invoice, width and depth guards, and all 54 strict plus four functional outer conditions. Omit the fetch flag to replay with a prepared source cache.

## Open next questions

A material gain requires a new BIT profile. One next experiment is multi-coordinate projection on helpers sharing an endpoint pair, with a rooted reconnection and exact forward and adjoint tape replay. The cost includes every bridge, cleanup step and changed ordinary charge.

## Credit

PRs #7786 and #7830 supplied the BIT word, the rational contractions and the two bounded-scalar checks. Ali Romman supplied the dual-supplier caller and tariff lineage, the independent BIT literal and price code, and related ordinary interchange work. The chronological product and separated compiler build on work by Cinna Davis, Jacob Alan Sussman and the compiler contributors credited in the predecessor notice. Jerry Chen and the other contributors to the physical supplier are credited in the pinned sources. Dugongue prepared this continuation with substantial OpenAI Codex assistance, under Apache-2.0. [PR #7786](https://github.com/CrocSwap/integer-mult-bounds/pull/7786) · [PR #7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) · [PR #7776](https://github.com/CrocSwap/integer-mult-bounds/pull/7776) · [PR #7826](https://github.com/CrocSwap/integer-mult-bounds/pull/7826) · [PR #7828](https://github.com/CrocSwap/integer-mult-bounds/pull/7828) · [Predecessor notice](https://github.com/CrocSwap/integer-mult-bounds/blob/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/NOTICE)
