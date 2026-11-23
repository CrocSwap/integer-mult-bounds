# Sharper K7 tariff and Gaussian period at the #8094 profile

The exact installed price and all scoped local scientific checks passed under the five stated premises.

The installed price supports conditional κ **0.003900857312000**. Against [exact #8094 at c20a08dc](https://github.com/CrocSwap/integer-mult-bounds/pull/8094), κ **0.003900857267786**, the exact difference is `22107/500000000000000` (0.000000000044214). The relative gain is `2210700/1950428633893` percent, displayed as **+0.000001133443163%**. The bound uses the same five conditional premises and the same recurring coefficient `log₂ C = 85945126846`.

The K7 ordinary price uses a sharper bound on the number of same-stage children per unit volume. It lowers the debit from `1420718/2^20` to `1414404/2^20`. This transfers the binding inequality to the Gaussian supplier. Applying #8085’s exterior-period proof at #8094’s five-shortcut word then lowers the Gaussian debit from `1039776/2^23` to `1039701/2^23`. Both changes are needed to reach this rate at these heights. [Complete conditional argument](PROOF.md) · [Installed price](RESULT.json)

## Replay from a clean checkout

Use Git and CPython 3.12 with assertions enabled. Run from the repository root with at least 8 GiB free on the checkout and temporary volumes. Use fresh temporary storage outside the checkout. The verifier authenticates its bundled source inputs and builds the runtime from them.

```sh
scratch="$(mktemp -d)"
TMPDIR="$scratch" python3.12 -IB scripts/research_package.py --package research/p104-k7-sharper-period
```

The original seven #8094 scopes reproduced on the exact head across separate local runs. The original 100-second product cap expired. The unchanged product passed under the inherited 220-second cap. The peer’s hosted attempt had zero jobs. [Peer continuation and receipts](https://github.com/ToikY/integer-mult-bounds/blob/616be5669b7e21e338bba164e5307b020e9f8005/paired-768/r423/REPLAY.md) · [Peer hosted attempt](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45143810893)

The candidate price reproduced the directed margins and expanded setup bound. The dense relay exercised 2,048 values in each direction at node 104493, rejected an incorrect Fourier action and restored the original owner. The first typed fixture invocation stopped before entering the signed stream due to a verifier name collision. The corrected two- and four-column cases each preserved 52,608 owners and retired relay scratch. The nine-recipe census emitted 2,492,277 records. The price, calendar, raw, exterior, nested, and signed product checks passed. See the [registered scopes](VERIFY.json).

## Open next questions

The next fixed-profile question is whether the directed Gaussian finite factor can be tightened beyond the adjacent failed `1039700/2^23` debit without changing ownership, phase or tape obligations. Ordinary headroom at the current rate is about `6.74e-13`. Reprice both sides before testing further sites.

## Credit

floration supplied #8094’s literal five-shortcut word and five-stage profile. Ali Romman supplied the [#8042 exact quotient receiver](https://github.com/CrocSwap/integer-mult-bounds/pull/8042), [#8055 serial setup proof](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) and [#8057 signed caller, compiler and replay](https://github.com/CrocSwap/integer-mult-bounds/pull/8057). SYLforge supplied the [#8052 K7 word](https://github.com/CrocSwap/integer-mult-bounds/pull/8052). The ordinary predecessor stack includes [#8076’s tariff and summation](https://github.com/CrocSwap/integer-mult-bounds/pull/8076), [#8082’s reserve removal](https://github.com/CrocSwap/integer-mult-bounds/pull/8082) and [#8086’s combined price](https://github.com/CrocSwap/integer-mult-bounds/pull/8086). [#8085](https://github.com/CrocSwap/integer-mult-bounds/pull/8085) and [#8087](https://github.com/CrocSwap/integer-mult-bounds/pull/8087) supply the Gaussian period lemma and prior replay. Clear1nsight supplied the [#8089 hosted control](https://github.com/CrocSwap/integer-mult-bounds/pull/8089). [#8091](https://github.com/CrocSwap/integer-mult-bounds/pull/8091) independently examines overlapping packet conservation and ownership in the retained receiver.

This package instantiates the sharper ordinary child mean and the existing Gaussian period lemma together at #8094’s profile. It reuses the campaign’s [direct and quotient trace](https://github.com/ToikY/integer-mult-bounds/blob/a5d5fd437a3bb3d0a78f3fb4f6412db8a04bb42a/paired-768/r414/proof-first/README.md), [setup correction](https://github.com/ToikY/integer-mult-bounds/tree/a5d5fd437a3bb3d0a78f3fb4f6412db8a04bb42a/paired-768/r417/setup-receipt), and [fixed-profile composition](https://github.com/ToikY/integer-mult-bounds/blob/a5d5fd437a3bb3d0a78f3fb4f6412db8a04bb42a/paired-768/r420/RESTART.md). OpenAI Codex materially assisted source tracing, proof, implementation and checking.
