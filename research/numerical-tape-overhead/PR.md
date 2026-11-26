# An explicit all-input overhead bound for integer multiplication on tapes

For one specified full-product multiplier, the written construction gives $T(n)\le n\sqrt L\,2^{63\Phi(x)}$ for every $n\ge2$ and at most $2^{32}n$ distinct visited tape cells. Here $L=1+\log_2 n$, $x=\log_2 L$ and $\Phi(x)=(x^2\log_2(x+2))^{1/3}$. At $n=1$ the direct branch takes at most 4096 transitions. Both operands may have leading zeros.

## Relation to #8102

@zxv's #8102 applies OpenAI's published theorem to get $O_\varepsilon(n(\log n)^{1/2+\varepsilon})$ for each fixed $\varepsilon>0$. Its $\kappa=0.4999$ example already gives exponent $0.5001$, closer to $1/2$ than $0.501$.

We derive $\log_2(T/(n\sqrt L))\le O(\Phi(x))$ by charging the address swaps and selected Walsh transforms used to compute the full product. We then fix the machine parameters and bound those costs explicitly, obtaining $63\Phi(x)$ for every $n\ge2$. This gives a computable sufficient input length for each exponent $1/2+1/q$ (integer $q\ge2$) and a sharper coefficient-one cutoff for $0.501$. [Adaptive-interchange derivation](https://github.com/CubeJerry/integer-mult-bounds/blob/research/numerical-tape-overhead/research/numerical-tape-overhead/proof/adaptive-rate.md)

Its adaptive interchange and Fourier implementation draw directly on the November 24 papers. The code uses OpenAI's tape semantics independently of #8102. [Prior work and attribution](https://github.com/CubeJerry/integer-mult-bounds/blob/research/numerical-tape-overhead/research/numerical-tape-overhead/SOURCES.md)

For the same multiplier, the written proof gives $T(n)\le n(\ln n)^p$ with leading coefficient one whenever $\log_2\log_2 n\ge t$.

| Exponent $p$ | Sufficient threshold $t$ | Estimate |
| --- | ---: | --- |
| 0.501 | 7,519,517,465,920,988 | Refined cutoff |
| 0.5001 | 13,824,000,000,000,000,000 | General formula, $q=10{,}000$ |
| 0.50001 | 15,984,000,000,000,000,000,000 | General formula, $q=100{,}000$ |

For $p=0.501$, the preceding integer $t-1$ fails the refined estimate. Lean verifies the adjacent signs, the all-later implication, and the physical gather–child–scatter rule with its repeated-call space bound. The complete time, output and space argument for the multiplier remains a written proof. [Package README](https://github.com/CubeJerry/integer-mult-bounds/blob/research/numerical-tape-overhead/research/numerical-tape-overhead/README.md)

From the repository root, run

```sh
python3 -I -B research/numerical-tape-overhead/verify.py
```

## Review and next steps

**Review question.** Does the full Walsh controller generate exactly the stated occupied calls, pay for every scan and child once, and keep the same head intervals across returns? The package states the missing Lean hypotheses and links the written cost for each. [Proof boundary](https://github.com/CubeJerry/integer-mult-bounds/blob/research/numerical-tape-overhead/research/numerical-tape-overhead/REVIEW.md)

For exponent $0.5$, the open problem is to bound $G=\log_2(T/(n\sqrt L))$ above by a constant. Equivalently, the goal is an excess exponent of order $1/\log\log n$ or smaller: if $T(n)\le nL^{1/2+C/x}$ for a fixed $C$, then $L^{C/x}=2^C$ since $x=\log_2 L\sim\log_2\log_2 n$. The present estimate gives $G\le63\Phi(x)$. An intermediate target is $G=O(\log(x+2))$. This requires deriving a tighter cumulative cost for the recursive swaps and Walsh calls. Reaching constant overhead also requires absorbing the outer permutation and transform costs. The [package README](https://github.com/CubeJerry/integer-mult-bounds/blob/research/numerical-tape-overhead/research/numerical-tape-overhead/README.md#open-next-questions) separates these research targets from the Lean obligations for the present bound.

Jerry Chen (@CubeJerry) directed this work with substantial ChatGPT research and verification assistance. OpenAI supplied the published constructions and tape model. OpenAI Codex prepared the extraction and additional Lean proofs.
