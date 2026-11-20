# When two product returns can share a carry

A parent receives four words and an incoming carry. It needs the low $m$ bits of $x_1y_1+x_2y_2+c$. Suppose the two left words agree on $a$ low bits, and the two right words agree on $b$ low bits. This package proves exactly when a single ordinary multiplication of separately encoded operands, with arbitrary one-sided additive corrections, can supply that return.

The threshold is **$a+b\ge m+1$**. Below it, multiply the two half sums and add a correction from the low $d=\max(0,m+1-a-b)$ bits of each divided difference. At $a+b=m$ the correction is one AND of two parities, applied to the high bit. For example, with four-bit words, take both sibling pairs to be $(0,4)$. The half-sum product would give 8 after doubling. The correction toggles its top bit, giving the correct $16\bmod16=0$. The proof allows arbitrary incoming carries and hidden differences of either sign. [Theorem 1 and the residual information bound](PROOF.md)

If all four words are independently odd and the parent asks for just the high bit, a different bound applies. Every fixed list of binary polynomial products with separate encoders and no other operand messages needs **$2m-2$ input coordinates on each side**. Unrestricted decoding attains that width. At six bits there are 512 distinct, nonconstant rows among the 1,024 left pairs. The earlier single-product result has a different input and output contract. [Theorem 2](PROOF.md) · [Single-product predecessor, #7838](https://github.com/CrocSwap/integer-mult-bounds/pull/7838)

## Two circuits on the same inputs

Both circuits read four distinct operand ports and one incoming carry, preserve all five words, and write the same low word. The control computes two truncated schoolbook products and adds them. The candidate computes the half sums, a truncated product, the correction and the carry. Both are compiled with the same XOR/AND primitives, zero constant, wire reuse, ripple addition and gate sharing.

| Word and low-bit promise | Two-product control | Shared-carry circuit | Inputs checked by the primary circuit verifier |
|---|---:|---:|---:|
| $m=4,\ a=b=2$ | 38 AND, 38 XOR | 21 AND, 29 XOR | All 65,536 input and carry combinations |
| $m=8,\ a=b=4$ | 170 AND, 170 XOR | 91 AND, 107 XOR | 4,096 repeatable cases |

On the eight-bit case, reversible compute, copy and uncompute costs **182 Toffoli and 436 CNOT**, using 198 initially clean scratch bits. The same translation of the control costs **340 Toffoli and 688 CNOT**, using 340 scratch bits. These totals include copying the eight-bit output and restoring every scratch wire. Wires and fan-out are free in the Boolean count. The reversible count assumes unrestricted gate connectivity and charges the forward and inverse gates explicitly. Neither circuit uses a lookup table. [Circuit generators](circuits.py) · [Frozen counts](RESULT.json) · [Independent verification](REVIEW.md)

## What this buys the integer multiplier

The Gaussian multiplier in #7834 contains actual sum-only joins. A source-bound control there can reduce ordinary word-product dispatches in a complete finite multiplication while preserving the integer output and the checked intermediate coefficients. The charged P104 and BIT caller in #7830 has a different obligation. Its named child fields may be observed separately. The congruence theorem supplies no signed credit on that caller. The verified conditional reference is $\kappa\ge0.00387992803556$; its fixed-profile directed upper endpoint is $0.003879928046155$. The target in this study is $0.003884928046155$. The reference still needs at least 4.880391089954707 rational and 1.925615290709237 binary price units there. [Source sites and qualifications](CALLERS.md) · [Full reference histograms](reference-price.json) · [Reference PR](https://github.com/CrocSwap/integer-mult-bounds/pull/7830)

## Reproduction

From a checkout with Python 3.12, run the two commands below. The first checks the congruence identity on 1,044,944 admissible cases through five bits, large signed representatives, literal odd-dot row classes, the circuits and the independent replay. The second also checks package registration and provenance. The Gaussian source replay has its own pinned checkout instructions. [Caller reproduction](CALLERS.md)

~~~sh
python3 -I -B research/recursive-dot-carry/verify.py
python3 -B scripts/research_package.py --package research/recursive-dot-carry
~~~

## Open next questions

Can a charged parent accept an invertible representation that exposes a dot-product sum while keeping any independently observed child difference available? Start by pinning the two child activations, the first consumer of each return, the correlation on all legal inputs, and the cost of retaining or restoring the difference. A candidate must move the applicable signed invoice after all of those charges. The explicit ordinary gate savings make a control for that test. [Literal caller witnesses](CALLERS.md)

## Credit

Clear1nsight prepared this package with substantial OpenAI Codex assistance. Separate workers traced the Gaussian and mixed-rank callers, tested asymmetric and phase-diagonal corrections, and reviewed the proofs and circuits with a separately implemented verifier. The arithmetic factorization uses the classical difference-of-products identity, and the Gaussian control uses the classical three-product complex multiplication identity. The contribution here is the sharp threshold for arbitrary separate encoders in the stated model, the exact residual and channel bounds, and the source-bound circuit and caller evidence. The Gaussian and mixed-rank implementations and their reported bounds belong to their cited contributors. [Task card and attribution](TASK.json) · [Frozen base sources](SOURCES.json) · [Gaussian implementation by aliromman](https://github.com/CrocSwap/integer-mult-bounds/pull/7834)
