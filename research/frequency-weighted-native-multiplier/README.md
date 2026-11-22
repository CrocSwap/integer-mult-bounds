# Frequency-weighted Gaussian calls in a signed multiplier

Two Gaussian job types can operate at distinct, paid frequencies in the same chronological calendar. The first type uses $f$ physical columns, the second $2f$. The second has 90 times the ideal birth density. Both types issue their own loans, have their own deadlines, and can consume real fields from the other type. This removes the need for the 79-fold column dilation in the preceding construction. The same signed multiplier now attains conditional $\kappa=0.00389820002$ with maximum native rank $2^{559011}$ and an all-input recurring coefficient at most $2^{309506891}$. [Construction and complete bills](PROOF.md) · [Exact receipt](RESULT.json) · [Source and image hashes](SOURCES.json)

| Complete claim | κ | Terminal ordinary heights | Terminal Gaussian height | First complete A | Terminal A | Ceiling for log₂ C |
|---|---:|---|---:|---:|---:|---:|
| Two unsplit returns in PR #8054 | .0038981730255 | 60,000 and 960,000 | 20,000,000 | 21,020,646 | 21,020,646 | 21,111,681,659 |
| Physical dilation 79 in PR #8055 | .0038982 | 35,327 and 559,005 | 680,000 | 7,437 | 1,274,851 | 339,787,971 |
| Two weighted types | **.00389820002** | **35,327 and 559,011** | **542,350** | **7,437** | **1,137,207** | **309,506,891** |

Each height $H$ denotes an actual internal rank $2^H$. The input length corresponding to $A$ is $2^{\lceil2^A/6\rceil-1}+1$ significant bits. The increase over PR #8055 is exactly $1/50{,}000{,}000{,}000$. It is $53989/2000000000000$ above PR #8054. The second ordinary stage needs six more height bits than in PR #8055. The maximum height over both suppliers decreases from 680,000 to 559,011. Compared with the earlier 20,000,000 benchmark the reduction is 35.78-fold in the exponent itself. The terminal threshold exponent decreases 18.48-fold against that benchmark. The earlier one-stage lower-rate machine still enters at $A=6913$ and $\kappa=.00363005817$. The previous two-stage compact machine enters at $A=161992$ and $\kappa=.00387992803556$. [Two unsplit returns](https://github.com/CrocSwap/integer-mult-bounds/pull/8054) · [Predecessor signed machine](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) · [Compact K7 comparisons](https://github.com/CrocSwap/integer-mult-bounds/pull/8052)

The fixed compiler uses one shared Gaussian atlas and 51 installed grade shares. At active entry it expands 88 type-specific shares and the actual physical owner lists. The complete portable setup costs fewer than $2^{142}$ tape transitions for the pinned fixed inputs. Its first run generates 106 source files and a 36,094,504-byte directory. Its second run loads that directory and connects the ordinary and Gaussian suppliers to the signed caller. The earlier serial arithmetic invoice gives an alternative ceiling of $2^{228}$. [Setup construction and replay](portable/README.md) · [Sequential tape price](portable/TRACE-CLOCK.md) The terminal maximum private control ceiling is $2^{572427266}$ bits. The Gaussian productive cohort alone has $2^{49896200}$ independent rows. With the same raw trials and finite debit rules, any number of ordinary stages still requires an ordinary height of at least 515,494. The Gaussian debit requires at least 542,294. [Scope of the two height floors](PROOF.md)

The first complete tier still requires $2^{7412}$ outer axes. None of these native ranks is a measured operating point. [Setup and executable evidence](VERIFICATION.md)

The five inherited premises cover all-column native action, owned erasure, uniform compiler closure, fixed-tape movement and precision, and analytic decomposition and recovery. They have the same scope as the preceding signed multiplier. The implementation uses two job types. The weighted row and owner-capacity implications hold for arbitrary finite sets and are kernel checked. [Weighted funding and placement in Lean](WeightedNumerical.lean) · [Upstream assumptions](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

## Reproduce

Use Git and CPython 3.12 with assertions. The declared inputs include the exact preceding multiplier on this branch.

```sh
python3.12 -IB scripts/research_package.py --package research/frequency-weighted-native-multiplier
python3.12 -IB research/frequency-weighted-native-multiplier/bootstrap.py /tmp/frequency-machine
python3.12 -B /tmp/frequency-machine/band_product.py -741503 466013
```

The last command returns −345550037539 through the public small-input base. The registered suite exercises the complete Fourier product at a supplied finite geometry and the weighted physical production bodies separately. [Evidence and limitations](VERIFICATION.md) · [Attribution](NOTICE.md)

## Open next questions

- Can a different ordinary graph or a cheaper quotient exchange reduce the remaining maximum height, 559,011?
- Can a different Gaussian word or transfer rule pass the upper-capacity cut that rejects a second-type frequency of 91 in this source at its funded trial?
- Can the outer controller and its true reserves run at tractable bit lengths? No crossover against a practical multiplier has been measured.
