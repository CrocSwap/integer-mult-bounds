# Fixed-clock source synthesis for two P104 donor banks

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to the independently
reproduced conditional κ = `0.00364665195644` on
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

Contract one public helper's two paid MOVEs to a direct rank-two
MOVE. Keep both original signed ADD clocks and the original peer
path. Each ADD must replace its old source with unchanged public
donors in the recipient's chart, even allowing the arbitrary dirty
destination as an extra span vector.

Two exact engines agree on all eight banks from the four frozen
windows. Seven have a coordinate missing from the entire bank.
The eighth has a two-coordinate rational separator. All eight
exclude the target even under unrestricted rational coefficients.
There are no surviving or unresolved banks.
[Exact agreement](receipts/AGREEMENT.json) · [Proof and complete price](PROOF.md).

## Replay

From a clean checkout, use CPython 3.12 with assertions:

```sh
python3.12 -I -B research/p104-fixed-clock-two-bank-bound/replay.py
```

The standard-library replay authenticates the #7334 word, its
signed cost receipt and the predecessor interval receipts.
It rebuilds the complete price and compares every frozen key,
donor, signed coordinate and exact elimination residual. It
rejects altered price and word inputs. Use `--out fresh-directory`
to retain all four receipts. No Git metadata, network or previous
temporary state is needed.
[Provenance](PROVENANCE.json) · [Path-keyed hashes](LOCAL-PINS.json).

## Open next questions

Switch to productive target cost while keeping paid paths fixed.
The [#7370 catalogue](https://github.com/CrocSwap/integer-mult-bounds/pull/7370)
has 18 untested bank representatives for chart 3→238 and roles
325 and 1087. Freeze that group and its complete rank-five 2+3
price before testing exact two-sided public-bank support. Its
productive change spends a different part of the invoice.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the exact native word and signed caller. [#7371](https://github.com/CrocSwap/integer-mult-bounds/pull/7371)
at exact head `3080de88bea994b03ea2494ddb51e22720562014` supplies
the four frozen windows and directed price. [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
inventoried the same four paid pairs under a different virtual-owned
fusion contract. [#7365](https://github.com/CrocSwap/integer-mult-bounds/pull/7365)
and [#7366](https://github.com/CrocSwap/integer-mult-bounds/pull/7366)
supply the adjacent sole-ADD donor and chronology methods.
[#7336](https://github.com/CrocSwap/integer-mult-bounds/pull/7336)
supplies the earlier public source-span precedent, and
[#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355)
supplies the reused exact donor engines. OpenAI Codex and subagents
materially assisted proof, implementation, independent checks
and packaging.
