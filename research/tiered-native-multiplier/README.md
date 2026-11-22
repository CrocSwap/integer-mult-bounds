# A tiered signed multiplier with smaller native ranks

One signed multitape multiplier attains conditional κ = 0.0038982 for arbitrary binary inputs. It uses the K7 ordinary word, a Gaussian word with physical dilations 1 and 79, and two complete sets of native ranks. The public input header selects the set. Both sets run the same CRT, signed Fourier, product and recovery algorithm. The largest rank is $2^{680000}$. The complete recurring coefficient is at most $2^{339787971}$ tape transitions in the normalization below. [Machine quantities](RESULT.json) · [Sources and exact hashes](SOURCES.json)

| Complete construction | κ | Ordinary log₂ ranks | Gaussian log₂ rank | Sufficient connected A | Ceiling for log₂ C |
|---|---:|---:|---:|---:|---:|
| Fixed-carrier K7, PR #8053 | .0038981721342 | 60,000 and 960,000 | 20,000,000 | 21,020,646 | 21,111,681,659 |
| Entry branch | .00345 local | 3,000 and 3,080 | 1,024 | 7,437 | 125,660,241 at its local rate |
| Terminal branch | .0038982 | 35,327 and 559,005 | 680,000 | 1,274,851 | 339,787,970 |
| Single machine | **.0038982** | both sets above | at most 680,000 | **7,437** for a complete native path, **1,274,851** for the terminal path | **339,787,971 at all lengths** |

For each A the sufficient input length is $2^{\lceil 2^A/6\rceil-1}+1$ significant bits. Here $N_i=2^{H_i}$ and $M=2^{H_M}$ are internal ranks. The price pays for arbitrary inputs, numeric recovery, the smaller branch, every parked bank and every cell traversed. Complete fixed installation falls from a published ceiling of $2^{513}$ to $2^{228}$ tape transitions. Two matched fresh-process observations per version took 82.62 and 5.09 seconds on average. Input-dependent preparations have their own charge. [Fixed setup and measurements](SETUP.md) [Numerical source, precision and movement](NUMERICAL.md) · [Complete product, clocks and activation](CLOCK.md)

The complete gain over ToikY’s fixed-carrier repricing is exactly 139329/5000000000000. The two unchanged numerical copies at scales 1 and 8 have a raw crossing below .0038981803447950341293615589, which is already below the new complete rate. [Leading comparison](https://github.com/CrocSwap/integer-mult-bounds/pull/8053) · [Independent interval proof](independent_price.py)

A lower-rate one-stage configuration in the same source family activates at A = 6,913 with H = 5,610 and numerical H = 1,024. The lower-rate two-stage compact configuration uses 9,100 and 144,000, with numerical H = 8,500 and A = 161,992. At κ = .003893947 the K7 configuration has A = 1,056,618 and numerical H = 36,000. These are smaller in one or more dimensions than the terminal branch above. The 7,437 threshold is for both actual ordinary stages and the numerical supplier. The finite price conversion also applies when an earlier machine has a suitable smaller connected profile. The independently significant terminal comparison is the 29.41-fold reduction in the largest rank exponent and the 16.49-fold reduction in the terminal threshold exponent against K7 extended. [K7 configurations](https://github.com/CrocSwap/integer-mult-bounds/pull/8052)

## Reproduce

Use Git and CPython 3.12 with assertions enabled.

```sh
python3.12 -IB scripts/research_package.py --package research/tiered-native-multiplier
python3.12 -IB research/tiered-native-multiplier/bootstrap.py /tmp/tier-install
python3.12 -B /tmp/tier-install/band_product.py -741503 466013
```

The last command prints `-345550037539` at the ordinary small-input base. The registered replay also runs an explicit physical Fourier geometry, the changed Gaussian source and the K7 interpreter. Open both Lean files with Mathlib and Lean 4.34.1, or run `check_lean.py LEAN_ROOT MATHLIB_ROOT`. [Verification scope](VERIFICATION.md) · [Attribution](NOTICE.md)

## Open next questions

- Can a different numerical word or weighted ordinary exchange reduce the terminal exponents by another order of magnitude? The old Gaussian source fails the strict raw moment before finite costs at the new complete rate.
- Can the outer controller generate and serve its enormous sides on physical inputs at an attainable scale? The first full execution proved here still requires at least $2^{7412}$ axes at the certified entry geometry. A production-scale timing comparison remains open.
