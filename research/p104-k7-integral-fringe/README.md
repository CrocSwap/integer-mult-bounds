# Charge the integral interior fringe at the #8095 profile

The complete staged local signed replay passed on the exact source. The rate uses the five stated premises.

The installed price supports conditional κ **0.003900857312674** and recurring `log₂ C = 85945126846` under the five premises of the comparator. The price replaces the Gaussian matched interior fringe bound of `10k` by `10k−5` for a funded recipient of grade k. It books a conservative two-tick decrease in the Gaussian debit, from `1039701/2^23` to `1039699/2^23`. The same five-stage resource profile then binds on its ordinary price. [Proof and complete accounting](PROOF.md) · [Installed price](RESULT.json)

| Comparison | Exact comparator κ | Exact Δκ | Percentage gain |
| --- | ---: | ---: | ---: |
| Strongest independently reproduced, [#8095 at 490cd470](https://github.com/CrocSwap/integer-mult-bounds/commit/490cd470f86157d29c9d3f8da9f96d6e2c3c04e5) | 0.003900857312000 | `337/500000000000000` = 0.000000000000674 | `337/19504286560` percent ≈ **+0.0000000172782531%** |
| Latest relevant external peer, [#8094 at c20a08dc](https://github.com/CrocSwap/integer-mult-bounds/commit/c20a08dc0a79a989e3515068560d5da371c0a2a8) | 0.003900857267786 | `5611/125000000000000` = 0.000000000044888 | `2244400/1950428633893` percent ≈ **+0.000001150721416%** |

The exact #8095 timeout-only repair passed its registered local suite. Its hosted retry is separate from this candidate. #8094’s original local 100-second product cap expired, and its unchanged product later passed at 220 seconds alongside the other six exact scopes. [#8095 hosted retry](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45294927135) · [#8094 local continuation](https://github.com/ToikY/integer-mult-bounds/blob/616be5669b7e21e338bba164e5307b020e9f8005/paired-768/r423/REPLAY.md)

## Replay from a clean checkout

Use Git and CPython 3.12 with assertions enabled. Run from the repository root. Use fresh temporary storage outside the checkout, with at least 8 GiB available on both the temporary and checkout volumes.

```sh
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB scripts/research_package.py --package research/p104-k7-integral-fringe
```

The package authenticates its source inputs and constructs the runtime from them. The [literal overlay and observed price](https://github.com/ToikY/integer-mult-bounds/blob/4c3ff9f606991a60834d46a9e9fd50c44a6995e7/paired-768/r428/REPLAY.md) and [independent source proof](https://github.com/ToikY/integer-mult-bounds/blob/4c3ff9f606991a60834d46a9e9fd50c44a6995e7/paired-768/r427/INDEPENDENT.md) can also be replayed separately. See [registered scopes](VERIFY.json) for the full suite.

## Open next questions

Can the exact K7 ordinary finite factor support one lower debit tick on the same caller and heights? Compare the current guarded ordinary ceiling with the new Gaussian ceiling before modifying the profile. The remaining Gaussian headroom above the ordinary crossing is about `4.69e-13`, so a larger increase would require a combined price. The earlier phase-averaged fringe is a candidate for that repricing after the ordinary bound moves.

## Credit

Clear1nsight’s [#8083](https://github.com/CrocSwap/integer-mult-bounds/pull/8083) and the [Round 409 referee proof](https://github.com/ToikY/integer-mult-bounds/blob/8e7738d0cd3cd37d1aa9815c6ea129bf21e5e1ef/paired-768/r409/price/PEER-INTEGRAL.md) establish the stronger lattice and integrated bounds. Ali Romman supplied the [#8057 typed allocator and signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) and its underlying [#8042 quotient receiver](https://github.com/CrocSwap/integer-mult-bounds/pull/8042). SYLforge supplied the [#8052 K7 word](https://github.com/CrocSwap/integer-mult-bounds/pull/8052). floration supplied [#8094’s five-shortcut word and resource profile](https://github.com/CrocSwap/integer-mult-bounds/pull/8094). [#8085](https://github.com/CrocSwap/integer-mult-bounds/pull/8085) supplied the four-aligned exterior period proof, and [#8095](https://github.com/CrocSwap/integer-mult-bounds/pull/8095) supplied its exact #8094 instantiation and sharper ordinary tariff. This package applies the sufficient integral fringe bound to that literal combined profile and regenerates its signed invoice. OpenAI Codex materially assisted proof, implementation and verification.
