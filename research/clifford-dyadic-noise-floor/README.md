# Which odd divisions attain the optimal Clifford noise norm?

At tensor width 13 the smallest possible worst-case Euclidean noise amplification for the full four-qubit Clifford decoder is $\sqrt{2^{32}/470624175}$. Among exact Gaussian-rational left inverses that attain this value, the **least common odd denominator is exactly 470,624,175**. Every exact Gaussian-dyadic decoder has strictly larger norm. With coefficient precision $s$, the best excess in **squared** norm is of order $4^{-s}$. At **every integer width $f\ge13$**, the least Gram eigenvalue determines the required odd denominator and the sharp rate remains $4^{-s}$ for fixed $f$. The results concern arbitrary additive errors in the ambient observation space. [Proof and precision model](PROOF.md)

Write the least Gram eigenvalue as $\lambda_f=m_f/2^{e_f}$ in lowest terms. The sharp odd budget is $m_f$. One correction using $1/\lambda_f$ makes the inverse exact on the worst noise eigenspace; further dyadic corrections strictly inside the available spectral gap suffice to attain the optimum. This constructs a potentially noncanonical minimizer. The rank, splitting and neighboring odd and Bell spectra enter through the credited predecessor proofs. [Construction and necessity](PROOF.md#1-a-split-finite-matrix) · [Pinned sources](SOURCE-PINS.json)

| Width | Least Gram eigenvalue | Sharp odd denominator for optimal decoding |
|---:|---:|---:|
| 13 | 470624175 / 2³² | 470,624,175 |
| 14 | 5741614935 / 2³⁵ | 5,741,614,935 |
| 15 and 16 | 75707742285 / 2³⁸ | 75,707,742,285 |
| 17 | 37674563331825 / 2⁴⁶ | 37,674,563,331,825 |

The argument also identifies sharp conditioning endpoints at every width divisible by four from width 16 onward. The Pauli-invariant part contains every eigenvalue from the preceding odd width; a positive unit-diagonal Schur multiplier traps the rest of the spectrum between those same endpoints. Extending the previous sharp constants to this neutral sector avoids a new character-table computation for the remaining blocks. [Endpoint proof](PROOF.md#3-four-qubit-least-eigenvalues-at-every-full-rank-width)

## Reproduce

From the repository root, use CPython 3.12 and the standard library.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-dyadic-noise-floor
```

The primary checker reconstructs all 81 width-13 levels from Nick Petalas's projected character data and compares them to Ali Romman's threshold receipt. It separately sums the actual nonzero Pauli lifts for the 81 inflated blocks at 21 neutral widths from 16 through 96, yielding 1,701 exact block equalities with their preceding odd widths. It tests the phase convention, certifies a toy optimum with odd denominator 5 whose canonical matrix needs 65, enumerates eight complex coefficient grids, and verifies exact rounding followed by recovery repair on 16 grids. A separate one-qubit checker evaluates the neutral-sector claim on full dense Gram matrices. The written proof supplies the infinite-width and asymptotic assertions. [Registered replay](VERIFY.json)

## Scope, credit and coordination

This package builds on Ali Romman's odd and Bell spectra, threshold conditioning, canonical odd-division obstruction and neutral width-twelve analysis, Nick Petalas's character projections, alephnan's Pauli-sector work, and apoursh's sharp dyadic width and stabilization results. The projection credits the ATLAS and Thomas Breuer's CTblLib. The proof uses classical finite-group orthogonality, Schur positivity and generalized-inverse identities. Two unmodified numerical inputs are retained for offline replay. Prepared by **apoursh** with substantial OpenAI Codex and separate agent assistance under Apache-2.0. [Source attributions and immutable versions](SOURCE-PINS.json) · [Investigation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19754148)

The least odd denominator is optimized over norm-attaining inverses. The result does not identify the least denominator of the entire canonical matrix, computational work at the denominator limit, or a physical multiplier. No change to the selected conditional multiplication exponent follows.

## Open next questions

1. What is the least odd denominator of the canonical width-13 matrix? Use all 52 spectral levels and the dyadic splitting to derive simultaneous denominators; denominators from the bottom eigenspace alone give only a lower bound.
2. How much coefficient precision is required for a practical noise margin? At width 13, the explicit lower bound scales as $4^{-s}/(12{,}128{,}668{,}876{,}800\cdot470{,}624{,}175^2)$. First bound the two-sided constants for a specified compact input/output interface; the general upper bound uses the full ambient matrix.
