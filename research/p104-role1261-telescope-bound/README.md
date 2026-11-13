# Fixed chart-246 correction for role 1261

**NO VERIFIED GAIN.** On exact #7481, test fusing the rank-three MOVEs 38490 and 39433 of public role 1261 into a rank-six MOVE. Omit its two old ADDs into role 1191 and reconstruct their historical net increment at chart 246 immediately before ADD39469. The fixed repair grants seven other chart-246 rows and preserves the old recipient's self coefficient of one.

The original input `x894=2` with all other entries zero annihilates all seven rows, but the required increment is 1. Independent normalized forward replay verifies both prefixes, including the preserved role 964 source, chart and ownership guards, and the old and unrepaired role 1191 responses of 0 and −1. The same probe also rules out an invertible scalar repair acting only on role 1191 with the seven donor rows fixed. Such a repair would require a zero self coefficient.

The hypothetical fusion would gross about 0.25649690069 raw across 17 signed calls before repairs. One fixed case exhausted with no unresolved case in that scope. No saving was realized. See [proof and price](PROOF.md), [path pins](PINS.json) and [verification](VERIFICATION.md).

## Replay

From a clean POSIX checkout using CPython 3.12 and its standard library:

```sh
python3.12 -I -B research/p104-role1261-telescope-bound/replay.py
```

Expect `PASS_ROLE1261_TELESCOPE_BOUND`. Both scientific processes have a 30-second cap. The replay requires no Git metadata, network or prior temporary state.

## Open next questions

Can a different already-paid path carry the historical increment, or can a joint repair change the available donor rows? Start by naming the sender, receiver and deadline, then check its exact response on the separator before pricing the full edit. Joint writable-bank changes, altered routes and other deadlines remain open.

## Credit

[#7494](https://github.com/CrocSwap/integer-mult-bounds/pull/7494) supplies the same-word, same-MOVE-pair result on fixed-peer relocation of the original outward ADD38491. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) supplies the earlier single-contact MOVE fusion method. [#7526](https://github.com/CrocSwap/integer-mult-bounds/pull/7526) supplies the previous exact inverse-contact component, and the [Round 276 handoff](https://github.com/ToikY/integer-mult-bounds/tree/4beae3493b0d3596e9a09b9b5d59f110c0a4881e/handoffs/round276) supplies this bounded telescope test. [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) supplies the exact word and invoice, with [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) in its lineage. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller, [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) exact cut covectors, [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) directed tariffs, and [#7508](https://github.com/CrocSwap/integer-mult-bounds/pull/7508) prior public copies of pinned bytes. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.
