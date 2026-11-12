# Changed-public MOVE contraction bound

**NO VERIFIED GAIN.** The verified gain is Δκ = 0, exactly 0% relative to conditional κ = 0.00364665195644 on exact #7334 `aaeec8c0acf01e99a5f331ef363a698d9c084ace` and signed #7113 `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Two exact screens rule out a paid MOVE contraction on the declared public roles under their tested contact contracts.

The literal full-word census covers all 37 consecutive paid ascending MOVE windows on the 14 changed-block public roles. Every interval has an ADD contact, including reads of the mover. The two engines agree on all 67 signed contacts. The contact-free and SCALE-only scopes each have zero candidates and zero unresolved windows.

The narrower donor relaxation keeps the old ADD clock in six windows where it is the mover's only intervening contact, the mover is its destination, and the middle chart differs from 207. At each of the two endpoint charts, the source row has a nonzero public input coordinate absent from every eligible donor row. The exact [12 separators](receipts/SEPARATORS.json) rule out arbitrary rational public-donor combinations at those fixed clocks. Both engines agree on all bank membership, source support sizes, donor ranks and dispositions. Three endpoint banks at chart 207 are empty. The one owned occupant at a chart-120 bank remains outside the donor basis.

## Reproduce

Use CPython 3.12 with assertions and the standard library. From this package in a clean checkout or Git-free export:

```sh
python3.12 -I -B replay.py
```

Use `--output replayed` to retain the [eight regenerated receipts](receipts/SHA256.json), including literal contact bytes and exact sparse source and donor rows. [Proof and price](PROOF.md) · [Verification](VERIFICATION.md) · [Pinned provenance](PROVENANCE.json)

## Open next questions

Start from a [separating coordinate](receipts/SEPARATORS.json) and specify what new source mechanism could supply it. Price all compatible edits before changing the bank or clock. The donor relaxation covers six of the 37 current windows. The other 31, middles on chart 207, roles outside the frozen 14, owned replacement donors, multiple binary contacts, source-side edits and different ADD clocks remain outside its scope. A signed native and complete caller replay would still be required for any candidate.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supply the exact comparator and signed caller. [#7339](https://github.com/CrocSwap/integer-mult-bounds/pull/7339) supplies the changed-block role record. [#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312) supplies the #7277 contact census and predecessor fusion gates. [#7336](https://github.com/CrocSwap/integer-mult-bounds/pull/7336) and [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338) supply related compensated fusion evidence. [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355) supplies the exact two-engine donor method for owned movers. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) and [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) supply directed price and the pinned rank-stock receipt. OpenAI Codex and subagents materially assisted proof, implementation, independent verification and packaging.
