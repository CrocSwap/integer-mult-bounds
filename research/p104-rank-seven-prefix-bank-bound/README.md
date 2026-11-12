# Fixed-paid rank-seven prefix exclusions on chart 602→127

**NO VERIFIED GAIN.** Exact Δκ = 0, a 0% change from conditional
κ = `0.00364665195644` on independently reproduced
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
head `aaeec8c0acf01e99a5f331ef363a698d9c084ace), with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
head `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

The proposed fixed-paid change splits one of five rank-seven productive
targets into 3+4 or 4+3 at an existing intermediate chart. Exhaustive
geometry finds 65 occupied rank-six bank keys on five charts and zero
eligible rank-five keys. Two exact prime-field engines agree on 32
direct exterior-prefix exclusions. Independent literal continuity
replay transfers those exclusions to 20 additional keys, for **52
excluded and 13 unresolved**. All unresolved keys are singletons in
the proved equivalence partition. [Exact key receipt](receipts/RECONCILED.json).

The fixed paid bill has 110,519 positions across 17 signed caller
copies. The relaxed directed upper is 0.294636248924991 raw units
per edit, or 1.473181244624955 across five distinct targets if all
can coexist. One new paid rank-one position defeats a single edit.
[Proof and price](PROOF.md).

## Replay

From a clean checkout, use CPython 3.12 with assertions enabled:

```sh
python3.12 -I -B research/p104-rank-seven-prefix-bank-bound/replay.py
```

The replay authenticates the native word and the inherited helper
census, rebuilds the directed price and full geometry, checks both
primes for the two frozen 16-key sets, and reconstructs all 60 adjacent
links in both directions. It rejects altered price and word inputs
and reproduces the exact 65-key disposition. Use `--out fresh-directory`
to retain all ten receipts. The standard-library replay needs no Git
metadata, network, external root or prior temporary state.
[Source provenance](PROVENANCE.json) · [Path-keyed pins](LOCAL-PINS.json) ·
[Receipt hashes](receipts/SHA256.json) · [Cohort preflight](COHORT.md).

## Open next questions

Test exactly the 13 unresolved keys from the reconciliation in one
25-second two-sided modular pass. If both sides drop rank, choose at
most four exact rational pairing tests under a 35-second cap and
preserve any remaining keys. A pair that survives still requires
signed arbitrary-input forward and adjoint action, ownership,
restoration, compiler, precision and tape checks, complete repricing
and independent caller and outer replay. The package tested the
fixed public bank and the existing chart catalogue on the pinned
word.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
supplies the exact current word and comparable result, and
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
the signed caller. [#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314)
supplies the parent native word. [#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319)
supplies the independent helper census. [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
supplies the independently admitted price inputs and
[#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
the directed tariff. [#5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718)
uses chart 602 as a productive insertion in an older rank-nine
construction, and [#6040](https://github.com/CrocSwap/integer-mult-bounds/pull/6040)
reproduces that calibration and tests a later older-word domain.
[#7363](https://github.com/CrocSwap/integer-mult-bounds/pull/7363)
supplies the exact-word modular exterior method for a distinct
rank-eight cohort. OpenAI Codex and subagents materially assisted
proof, implementation, independent verification and packaging.
