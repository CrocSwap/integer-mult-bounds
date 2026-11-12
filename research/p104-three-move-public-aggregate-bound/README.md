# Public donor aggregates for P104 role 532

**NO VERIFIED GAIN.** Conditional κ remains `0.00364665195644`,
with exact Δκ = 0 relative to independently reproduced
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace` and signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

This follow-up releases the original-partner restriction of
[#7383](https://github.com/CrocSwap/integer-mult-bounds/pull/7383)
for one fixed #7334 role-532 window. Two incoming ADDs must be
replaced by their exact aggregate at one of the two fixed endpoints
of a direct paid MOVE. The forward and backward engines agree on
all 26 aggregate coordinates and both full public inventories.
Coordinate 27 is zero on every eligible donor row and +1 on the
required aggregate, excluding both banks.
[Agreement](receipts/AGREEMENT.json) · [Proof and price](PROOF.md).

## Replay

Use POSIX CPython 3.12 with assertions enabled from a clean checkout.

```sh
python3.12 -I -B research/p104-three-move-public-aggregate-bound/replay.py
```

The standard-library replay verifies the exact #7383 public
manifest, source price and native word. It regenerates the
one-window quote, both exact bank checks and their agreement.
Two changed-input controls reject. Use `--out fresh-directory`
to retain the four receipts. No network, Git metadata, external
dependency root or prior temporary state is needed.
[Provenance](PROVENANCE.json) · [Path-keyed pins](LOCAL-PINS.json) ·
[Receipt hashes](receipts/SHA256.json).

## Open next questions

The fixed chart-207 cut also has one old live owned value, role
1567. A separate scoped test can check its coordinate 27 and
whether an exact read-only use fits the same lifetime, restoration
and price. The separate role-198 aggregate uses an owned source
and remains open. This package tests only original public donors
at the two stated endpoints of role 532.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the native word and signed caller.
[#7383](https://github.com/CrocSwap/integer-mult-bounds/pull/7383)
at `7289aef67c67bda19b7cb15e3e8b427c27edb556` supplies the exact
triple, signed directed price and original-partner exclusion.
[#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355)
at `403e0d388c35e83b15eab5bba67be563b33d5a8a` supplies the
forward rational row engine.
[#7378](https://github.com/CrocSwap/integer-mult-bounds/pull/7378)
supplies a two-write aggregate precedent on a different owned role.
[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338),
[#7368](https://github.com/CrocSwap/integer-mult-bounds/pull/7368)
and [#7369](https://github.com/CrocSwap/integer-mult-bounds/pull/7369)
cover nearby role-532 subwindows or chart-746 scalar contacts
under different route constraints.
[#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
supplies the directed tariff inherited through #7383.
OpenAI Codex and subagents materially assisted proof,
implementation, independent verification and packaging.
