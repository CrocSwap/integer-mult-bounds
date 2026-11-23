# Two enlarged-budget signed P104 profiles

This source-bound experiment starts from ToikY's [#8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072) at `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`. It keeps the ordinary K7 word, the two-type Gaussian word and their paid finite-factor bookings. It changes the installed three-stage heights and pays the complete resulting recurring invoice. The results are conditional on the same five supplier, ownership, chronological compiler, precision/tape and analytic-recovery premises as #8072.

| Profile | Conditional κ | Ordinary heights | Gaussian height | Complete log₂ C | Terminal entrance A | Entry conversion |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| #8072 | 0.003898214283192 | (8192, 124649, 524288) | 490950 | 318292011 | 1148553 | 515 |
| 300 | 0.0038983 | (8192, 35682, 566698) | 743589 | 358974351 | 1354635 | 608 |
| 340 | 0.00389834 | (8192, 36220, 575705) | 978582 | 413727211 | 1599173 | 717 |

Each height H represents rank `2^H`. These are larger-resource tradeoffs: the two new recurring bounds cost 40,682,340 and 95,435,200 additional bits in the exponent of C. Their maximum native heights also grow. The κ gains over #8072 are exactly 0.000000085716808 and 0.000000125716808. Neither claim applies to #8072's fixed height caps or recurring budget. [Proof and scope](PROOF.md) · [Exact profile 300 invoice](RESULT-300.json) · [Exact profile 340 invoice](RESULT-340.json)

Each target has a minimum charged height sum within the stated three-stage, high-fibre invoice family. The proof relaxes floors and clamps, bounds the reciprocal allocation with an exact rational lower enclosure of `1/sqrt(250)`, and shows one less ordinary height cannot fund the target. The Gaussian height is separately necessary for the stated positive booking. This is an optimum of the stated invoice, not a lower bound on a different machine's true runtime.

From this directory, use CPython 3.12 and Git:

```sh
python3.12 -I -B verify.py 300 all
python3.12 -I -B verify.py 340 all
```

Individual scopes are `price`, `calendar`, `raw`, `exterior`, `nested`, `product` and `setup`. `regenerate` writes the recomputed invoice to standard output. The verifier restores and hashes the archived predecessor, applies the authenticated #8072 changes, checks the new installed-image hash, and runs the signed producer. It checks exact paid prices, the entry prefix, all stated outer inequalities, both direct and compiled stage seams, physical owner returns, signed fixtures, integer cutoffs and the serial setup bound. The economic check rejects a smaller Gaussian height and any smaller total ordinary height; further negative controls reject one-unit height cuts, an unfunded outer margin, an invalid prefix and an understated clock cap.

The physical coefficient fixture is finite and the production-scale terminal input is astronomically large. The executable checks do not run a full terminal-scale multiplication or establish the five inherited premises. They are not a maintainer acceptance, selected-frontier update, or measured speedup. `UPSTREAM-*` files preserve #8072's original proof and exact invoice; [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057), [#8055](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) and [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052) supply the credited source and setup.

## Open next questions

Can a larger Gaussian height raise the rate further while preserving and explicitly repricing the source-level fixed installer, positive carrier generation and all-size signed caller? A separate certificate is needed once the predecessor's 20-bit height guard is exceeded. Independent review can also assess the inherited five premises and the new invoice-to-caller bindings.
