# Sharp polynomial pass counts for the four-qubit Clifford decoder

At tensor width 13, **52 applications of the Gram matrix suffice for a Gaussian-dyadic left inverse within $2^{-73}$ of the canonical decoder** in operator norm. The previous explicit construction used 8,192 applications of a fixed step and also covered larger widths. The 52-step schedule uses the exact discrete width-13 spectrum. Every prefix recovers noiseless inputs exactly and amplifies the initial error relative to the canonical decoder by at most one. [Derivation, lower certificates and coefficient bounds](PROOF.md) · [Complete scalar schedules](SCHEDULE.json) · [Previous uniform construction, PR 7799 §5](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md)

| Goal at width 13 | Exact scalar arithmetic | Gram applications | Lower certificate |
|---|---|---:|---|
| Contract the initial error uniformly by at least $2^{-128}$ | All 52 steps dyadic, actual residual below $2^{-129}$ | **52** | Every normalized polynomial of degree at most 51 has residual above $2^{-61}$. |
| Attain the optimal squared noise norm $2^{32}/470624175$ | 50 dyadic steps on a 192-bit grid, then one multiplication by $2^{32}/470624175$ | **51** | Every fixed normalized polynomial of degree at most 50 fails for some exact dyadic initial inverse within the stated error bound. |

For observation $y$, initialize $d=By$ with the Bell inverse and precompute $t=A^*y$. Each listed scalar $h$ prescribes the update $d\gets d+h(t-Kd)$ with $K=A^*A$. Only the second schedule uses odd division, and its denominator realizes the previously proved sharp minimum among all optimal-norm decoders. The scalar precisions of the first schedule range from 69 to 266 fractional bits. The proof gives a sufficient grid for writing out every coefficient of that decoder. [Sharp arithmetic necessity, PR 7802](https://github.com/apoursh/integer-mult-bounds/blob/ebe2c019e398d73444e4f33f2d71bd5775795a01/research/clifford-dyadic-noise-floor/PROOF.md)

Both lower bounds concern fixed residual polynomials $p$ with $p(0)=1$. The second uses only the hypothesis $\|B-J\|<2^{56}$ about the initial error and allows other exact dyadic starting inverses besides the Bell inverse. The 52-level program counts exact Gram applications. Producing the input, pricing an individual application and realizing a multiplication supplier remain open. No change to the selected multiplication exponent is claimed.

## Reproduce

From the repository root, use CPython 3.12 and the standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-accelerated-dyadic-decoder
~~~

The primary verifier regenerates the shifts from Ali Romman's spectrum using rational interpolation, integer root comparisons and explicit rounding. It checks both schedules and both degree lower bounds. The second verifier recovers the levels from Nick Petalas's fixed-space character projections. It checks integer prefix products, computes the lower certificates using divided differences and applies the actual updates to a rectangular dyadic test with a nondiagonal Gram matrix. Reversing the 52 shifts gives an intermediate amplification above $2^{138}$, which the prescribed order avoids. The generator supports writing a fresh copy of SCHEDULE.json via its `--emit-schedule` option. [Source pins](SOURCE-PINS.json) · [Registered checks](VERIFY.json)

## Credit

Ali Romman supplied the four-qubit spectrum and conditioning. Nick Petalas supplied the projected quotient character data from the ATLAS and Thomas Breuer's GAP Character Table Library. The four-qubit Clifford conventions also build on alephnan's Pauli-sector work. The starting dyadic splitting, the sharp optimal-noise denominator, and the separate larger arithmetic cost of the canonical inverse are earlier contributions of apoursh. The present results use classical Lagrange interpolation, alternation and spectral polynomial iteration. Prepared by **apoursh** with substantial OpenAI Codex assistance. Apache-2.0. [Source files and predecessor credits](SOURCE-PINS.json) · [Canonical denominator, PR 7805](https://github.com/apoursh/integer-mult-bounds/blob/d3df403a13bee082a8cef62f190024aaf0cd08dd/research/clifford-canonical-denominator/PROOF.md) · [Investigation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19755740)

## Open next questions

1. Can one Gram application be evaluated on a compact acquisition interface? Start with one specified observation layout and count data movement, arithmetic, and intermediate precision for $K d$. The pass counts leave those costs open.
2. Does the particular Bell inverse already have zero error on any of the 52 levels? Project its error onto the smallest block first. Extra exact zeros could reduce the required polynomial degree for this specific starting matrix.
