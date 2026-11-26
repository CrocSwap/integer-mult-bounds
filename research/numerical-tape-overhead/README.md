# Numerical overhead for full-product multiplication on tapes

One specified deterministic multitape machine multiplies every pair of unsigned, possibly zero-padded, $n$-bit words and writes their full $2n$-bit product. Put $L=1+\log_2 n$, $x=\log_2 L$ and $\Phi(x)=(x^2\log_2(x+2))^{1/3}$. The written construction gives

$$
T(n)\le n\sqrt L\,2^{63\Phi(x)}\quad(n\ge2),\qquad
T(1)\le4096,\qquad S(n)\le 2^{32}n\quad(n\ge1).
$$

$T$ counts transitions in the worst case. $S$ counts distinct tape/address pairs touched at any time, including erased cells and the starting positions of idle heads. The remaining human review concerns the physical cost of the full program. [Construction and derivation](CONSTRUCTION.md) · [Exact scope of the Lean proofs](REVIEW.md)

## Relation to #8102

OpenAI's November 24 tape theorem gives one exact multiplier with a logarithmic exponent tending to $1/2$. In #8102, @zxv applies it to each **fixed** $\varepsilon>0$, obtaining $O_\varepsilon(n(\log n)^{1/2+\varepsilon})$. Its example $\kappa=0.4999$ gives exponent $0.5001$, already closer to $1/2$ than $0.501$. Hans Brende had also drawn attention to the published theorem in #8100. [PR #8102 and its discussion](https://github.com/CrocSwap/integer-mult-bounds/pull/8102) · [Issue #8100](https://github.com/CrocSwap/integer-mult-bounds/issues/8100)

We derive $\log_2(T/(n\sqrt L))\le O(\Phi(x))$ by charging the address swaps and selected Walsh transforms used to compute the full product. We then fix the machine parameters and bound those costs explicitly, obtaining $63\Phi(x)$ for every $n\ge2$. This gives a computable sufficient input length for each exponent $1/2+1/q$ (integer $q\ge2$) and a sharper coefficient-one cutoff for $0.501$. [Adaptive-interchange derivation](proof/adaptive-rate.md)

It uses the paper's interchange, finite Fourier and full-product constructions with a width-dependent choice of arity. It imports the original tape semantics directly from OpenAI. There is no build or source dependency on #8102. [Sources, attribution and upstream overlap](SOURCES.md)

## From an exponent to a bit length

Let $t=\log_2\log_2 n$. For each integer $q\ge2$, set $D=(60q)^3$, take the first integer $j\ge2$ with $2^j\ge jD+2$, and set $t_q=\max(1{,}572{,}864{,}480,jD)$. For every $n\ge2^{2^{t_q}}$, the same machine satisfies $T(n)\le n(\ln n)^{1/2+1/q}$. The program is independent of $q$. [Proof and examples](proof/all-exponents.md)

| Exponent | Sufficient $t$ | Calculation |
|---|---:|---|
| $0.5001$ | 13,824,000,000,000,000,000 | General formula, $q=10{,}000$ |
| $0.501$ | 11,664,000,000,000,000 | General formula, $q=1{,}000$ |
| $0.501$ | **7,519,517,465,920,988** | Piecewise estimate for the occupied Walsh calls |

The last row means $T(n)\le n(\ln n)^{501/1000}$ **for every larger input length as well**. The immediately preceding integer value of $t$ fails the same charged estimate. The actual machine could meet the time bound sooner. [Endpoint proof](proof/routing-label-walsh.md) · [Exact checks](VERIFICATION.md)

## Replay

From the repository root, with Git, Python 3.10+, the pinned Lean 4.34.1 toolchain (including Lake and leanchecker), a C++17 compiler named `c++`, and GMP 6.3.0 C++ development headers and libraries installed, run

```sh
python3 -I -B research/numerical-tape-overhead/verify.py
```

The command obtains pinned Mathlib dependencies, compiles the local Lean modules in an empty build directory, audits declaration axioms, runs a fresh kernel, and checks both cutoff signs and four complete product fixtures. A pre-existing Mathlib checkout can be supplied via `TAPE_MATHLIB_DIR`. The command checks its revision and its transitive Git pins. [Dependencies](dependencies.json) · [Verification record](VERIFICATION.md) · [PR title and description](PR.md)

## Open next questions

Does the full Walsh controller generate exactly the counted occupied calls, charge each parent scan, and reuse the same physical head intervals across every return? The first check is one free-rectangle source role and one charged-rectangle destination role, from mask preparation through the last restored bit. The key blocker for an end-to-end Lean theorem is the correspondence between that controller and the physical call traces. [Precise obligations and written arguments](REVIEW.md)

Jerry Chen (@CubeJerry) directed this work with substantial ChatGPT research and verification assistance. OpenAI supplied the published constructions and original tape model. OpenAI Codex prepared the extraction and additional physical trace proofs. [Source and contributor credits](SOURCES.md)
