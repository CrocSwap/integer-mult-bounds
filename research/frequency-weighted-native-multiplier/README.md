# Frequency-weighted Gaussian calls in a signed multiplier

One signed binary multiplier attains conditional $\kappa=0.00389821$. Its largest native rank is $2^{524288}$, against $2^{20000000}$ for the previous highest-rate peer and $2^{680000}$ for the previous compact high-rate machine. The portable fixed setup costs fewer than $2^{113}$ individual tape transitions, and the complete all-input recurring coefficient is at most $2^{318259431}$. The exact gain over the rounded-packet peer is $83863/10^{13}$. The new complete rate also exceeds that peer's raw trial $4286126377/2^{40}$. [Written construction](PROOF.md) · [Numerical finite cost](FINITE-LOSS.md) · [Exact receipt](RESULT.json) · [Source bindings](SOURCES.json)

| Complete claim | κ | Terminal ordinary heights | Gaussian height | First full A | Terminal A | Ceiling for log₂ S | Ceiling for log₂ C |
|---|---:|---|---:|---:|---:|---:|---:|
| Rounded quarter packets in PR #8056 | .0038982016137 | 60,000 and 960,000 | 20,000,000 | 21,020,646 | 21,020,646 | 513 | 21,111,681,659 |
| Physical dilation 79 in PR #8055 | .0038982 | 35,327 and 559,005 | 680,000 | 7,437 | 1,274,851 | 228 | 339,787,971 |
| Frequency-weighted jobs | **.00389821** | **8,192, 129,414 and 524,288** | **483,871** | **7,437** | **1,146,239** | **113** | **318,259,431** |

Each height $H$ denotes an actual native rank $2^H$. The sufficient input length for exponent $A$ is $2^{\lceil2^A/6\rceil-1}+1$ significant bits. Compared with the rounded-packet machine, the maximum rank exponent falls 38.15-fold and the terminal threshold exponent falls 18.34-fold. The inexpensive complete tier enters 2,826-fold earlier in $A$. Its local rate is .00345. The all-length bill pays the full 514-bit cost to use it at the global rate. The earlier one-stage, lower-rate machine enters at $A=6913$ with maximum $H=5610$ at $\kappa=.00363005817$. A two-stage compact machine uses heights 9,100, 144,000 and 8,500 at $A=161992$ and $\kappa=.00387992803556$. The first tier here still requires $2^{7412}$ true outer axes. [Highest-rate peer](https://github.com/CrocSwap/integer-mult-bounds/pull/8056) · [Compact high-rate predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) · [Other K7 configurations](https://github.com/CrocSwap/integer-mult-bounds/pull/8052)

An earlier working configuration of this same research is a useful scale comparison. It reached .00389820002 with maximum $H=559011$, terminal $A=1137207$ and $\log_2 C\le309506891$. The final form lowers its maximum $H$ by 34,723 and raises the complete rate above the rounded-packet peer. It adds 9,032 to that working configuration's terminal $A$ and 8,752,540 to its $\log_2 C$ ceiling. The comparison with PR #8055 in the table uses the smaller published high-rate predecessor. [Earlier weighted receipt](https://github.com/aliromman/integer-mult-bounds/blob/776d432ddaaf9edd8f11f1b8e6933abfd82a63b7/research/frequency-weighted-native-multiplier/RESULT.json)

The producer runs physical jobs at $f$ and $2f$ columns with relative birth weights 1 and 90. Each opening has 52,608 true productive owners. Both types issue and return their own loans. At frequency 91 the total signed moment still has slack, yet the compulsory flows to grades above two exceed the available capacity. The new finite price uses all 51 installed shares and permits the calendar to begin at 2,048 columns. At execution the calendar constructs 88 typed shares and the real chronological lists. A third terminal ordinary stage lowers the maximum required rank. It also adds an intermediate rank and a suspended call. Both appear in the clock and stock. At the same raw K7 trial and finite debit, any number of ordinary stages requires some height of at least 517,430. The installed maximum is within 1.33% of that floor. [Calendar and stage proof](PROOF.md) · [Exact fringe and depth accounting](FINITE-LOSS.md)

The portable installer generates a typed directory of 36,094,602 bytes and a cold receiver connects its seven recipe objects to the signed caller. Its sequential clock pays for the entire interpreter, generated sources, transfer, both runs, every live tape and cleanup. The explicit setup bound uses a separate head for each data stack and charges discarded data as the interpreter pops it. The terminal private control envelope is $2^{536870915}$ bits. The active Gaussian cohort alone has $2^{44516132}$ independent rows. The measured installation and finite physical tests have a different scale from the full active machine. [Portable setup and reproducible receipts](portable/README.md) · [Sequential locality proof](portable/STACK-LOCALITY.md) · [Signed execution and limits](VERIFICATION.md)

Five inherited premises cover all-column native action, owned erasure, uniform compiler closure, fixed-tape movement and precision, and analytic decomposition and recovery. The complete theorem has the same research contract as the two peers. Lean checks the weighted per-owner capacities, physical placement, finite price conversion, rate gain and rank floors. [Weighted funding in Lean](WeightedNumerical.lean) · [Finite Gaussian loss in Lean](GaussianFiniteLoss.lean) · [Canonical assumption record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

## Reproduce

Use Git and CPython 3.12 with assertions. The declared inputs include the exact preceding multiplier on this branch.

```sh
python3.12 -IB scripts/research_package.py --package research/frequency-weighted-native-multiplier
python3.12 -IB research/frequency-weighted-native-multiplier/bootstrap.py /tmp/frequency-machine
python3.12 -B /tmp/frequency-machine/band_product.py -741503 466013
```

The last command returns −345550037539 through the public small-input base. The registered suite exercises the complete Fourier product at a supplied finite geometry and the weighted physical production bodies separately. [Evidence and limitations](VERIFICATION.md) · [Attribution](NOTICE.md)

## Open next questions

- Can a different ordinary graph or a cheaper quotient exchange reduce the 517,430 floor for the present ordinary price?
- Can a different Gaussian word or transfer rule pass the upper-capacity cut that rejects a second-type frequency of 91 in this source at its funded trial?
- Can the outer controller and its true reserves run at tractable bit lengths? No crossover against a practical multiplier has been measured.
