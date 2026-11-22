# Retimed native suppliers for signed integer multiplication

A fixed integer-multiplication machine can generate both native words and their grade couplings before it reads the operand bits. It calls the original binary and Gaussian circuits directly on a timed collection of independent fields, routes each paid operation to a smaller admissible column count, and restores its suspended owner before the next cut. This removes the powered-word ranks from both suppliers. The result also gives an explicit absolute time constant for the complete signed tape algorithm, subject to the predecessor's five research premises. [Transport proof](TRANSFER.md) · [True initialization](INSTALLATION.md) · [Signed clock](CLOCK.md) · [Exact receipts](RESULT.json)

| Machine | Complete κ | Last binary H | Numerical H | log₂ S ≤ | Activation A | log₂ C ≤ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prior compact | 0.00387992803556 | 1,600,000 | 610,000 | 1,638,400,002 | 2,471,428 | 30,535,241,478 |
| Prior small-gap | 0.0038901152865907 | 7,168,000,000,000,000 | 1,600,000 | 7,340,032,000,000,000,003 | 7,645,866,239,991,957 | 125,269,872,000,160,591,302 |
| Small | 0.0038 | 48,000 | 3,000 | 513 | 51,471 | 787,093,646 |
| Compact | 0.00387992803556 | 380,000 | 13,000 | 513 | 426,495 | 6,769,453,650 |
| Balanced | 0.00389 | 36,000,000 | 36,000 | 513 | 37,926,837 | 620,797,681,654 |
| Near | 0.00389011528 | 600,000,000,000 | 36,000 | 513 | 644,320,117,023 | 10,556,538,887,921,661 |
| Matched | 0.0038901152865907 | 1,050,000,000,000,000 | 36,000 | 513 | 1,095,879,152,647,278 | 17,954,883,993,607,921,665 |

All dimensions in the table are exponents. The ranks are $2^H$, setup is bounded by $2^{\log_2 S}$ transitions and the recurring coefficient by $2^{\log_2 C}$. The prior rows use the single-band physical compiler and our explicit repricing of its recurring tape costs. Its submitted bound used an unspecified coefficient. PR #8040 already lowered the corresponding setup exponents to 4,098 and 6,267 with its grade-counted installer. The new fixed bound is 513. The upper bounds do not measure the speed of one product. [Prior setup receipts](https://github.com/aliromman/integer-mult-bounds/blob/1ca6b8111297ac2cc2dcfe5da0027656898f7589/research/counted-native-bands/RESULT.json)

For each A, the first sufficient significant input length in bits is $2^{\lceil 2^A/6\rceil-1}+1$. This entrance supplies the complete numerical raw word, a genuine full-slot ordinary interchange, all earlier services, the private precision and the true high-matrix stock. The public controller can select a cheaper or stopped branch before this point. At Small the largest side at the entrance already has tens of millions of address bits. Every rank-$2^H$ raw cohort actually has $2^{92H}$ independent native rows. Input-dependent preparation, incomplete groups and head movement enter the recurring bound. [Complete activation](ACTIVATION.md) · [Precision and movement](NUMERICAL.md)

## Equal-rate comparison

Retune the old compact, higher-rate, 268-factor and 285-factor prices with one to six ordinary stages at the two supported stop margins. For fixed raw trial c, debit $l$ and stage widths $H_i$, iteration from the cold stage gives
$$
c-b_m \ge c/250^m+(249l/250)\sum_{i=1}^m250^{i-m}/H_i .
$$
Cauchy–Schwarz with $1/16<1/\sqrt{250}$ bounds the last sum below by $(\sum_{j=0}^{m-1}16^{-j})^2/(\sum_i H_i)$. The ordinary width floor implies $A>\sum_i H_i+H_M$. At the most permissive supported positive stop add the strictly necessary numerical debit. The checker also constructs actual alternative installations from those words and runs their complete resource and signed gates. The lower bound applies to these four named tariff formulas and stage rule. Other physical suppliers may do better. [Retunings](equal_rate.py)

- At κ = .00389, a feasible old refit has A = 188,868,731. Every such retuning has A ≥ 188,252,135. The new balanced installation has A = 37,926,837.
- At κ = .00389011528, a feasible old refit has A = 3,615,709,999,957. Every such retuning has A ≥ 3,609,923,786,113. The new near installation has A = 644,320,117,023.
- At κ = .0038901152865907, a feasible old refit has A = 7,420,702,481,833,889. Every such retuning has A ≥ 7,404,411,307,975,972. The new matched installation has A = 1,095,879,152,647,278.

## Reproduction

Use Python 3.12 with assertions enabled and Git on PATH.

~~~sh
python3.12 -IB scripts/research_package.py --package research/retimed-native-multiplier
~~~

The command ends with `PASS_REGISTERED_RESEARCH_PACKAGE research/retimed-native-multiplier outcome=completed`. A clean installation is also available to callers.

~~~sh
python3.12 -IB research/retimed-native-multiplier/bootstrap.py /tmp/retimed-machine
python3.12 -B /tmp/retimed-machine/band_product.py -741503 466013 --profile compact
~~~

The public signed entry prints `-345550037539`; on that input the normal selector uses the scalar stop. A separate true finite Fourier computation visits 157,248 H calls and 138 physical shuttles, verifies all five base-256 coefficients, and restores both inputs. Both original raw emitters, the new timed scheduler with noncommuting finite charts, and real setup at production rank logarithms have separate runs. No test materializes an active production-dimensional field. These results establish neither a measured crossover nor a nonconditional integer-multiplication bound. [Verification details](VERIFICATION.md) · [Credits](NOTICE.md)

## Open next questions

Can the complete ordinary receiver meet its present raw crossing with fewer weighted recursive interchanges on all real low matrices? Can an outer pack force the genuine paid path at a smaller public precision while retaining every high coordinate and the full numerical error budget?
