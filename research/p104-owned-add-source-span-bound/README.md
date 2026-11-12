# Same-chart donor spans for three owned ADDs

**NO VERIFIED GAIN. Conditional κ change 0%.** All 33 proposed cuts for three destination-owned, single-ADD windows on exact #7334 fail the arbitrary-input source-span test. Twenty-four cuts have an absent donor coordinate. The other nine have an exact rational covector that annihilates every eligible donor and evaluates to −2 on the required source row. Both exact engines agree on every bank and rank. The 33-cut scope is exhausted with zero survivors and zero unresolved cases.

## Comparator and complete price

The independently reproduced comparator is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ = 0.00364665195644, using the exact [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed 17-copy caller. In a proposed edit the moved owner stays live and fuses its two monotone MOVEs, with the ADD source replaced by a linear combination of other live roles in the chosen outer chart. The literal source's value and itinerary stay intact.

The directed compatible gross relaxation is 0.488271001558 raw at the old crossing across the three distinct windows. It grants extra ordinary ADDs, setup, routing, ownership, restoration, tape and precision costs for free. One extra paid rank-one position defeats even that combined relaxation. The complete productive histogram stays fixed. No cut supports the local source identity, so the verified saving is zero. See [the exact price](receipts/PRICE.json) and [proof](PROOF.md).

## Replay

Use CPython 3.12 with assertions and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-owned-add-source-span-bound
```

From the package directory or a Git-free export, use `python3.12 -I -B replay.py --out fresh-receipts`. The replay authenticates the exact signed caller and native word, reconstructs the complete price before native decoding, regenerates both exact support receipts, rechecks each separating witness against its ordered donor bank, and rejects changed input bytes. Paths, source references and verification coverage are in [PROVENANCE.json](PROVENANCE.json) and [VERIFICATION.md](VERIFICATION.md). The selected record stays unchanged.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supplies the exact word and complete comparator, [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) the signed caller, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed tariff. [#7354](https://github.com/CrocSwap/integer-mult-bounds/pull/7354) at f92b4c999204e0437dc89359f87fc7be3ecdd12e supplies the three frozen windows and their price. [#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308) at 2c777389ec0476e97ab141c645af01ff28a46aa6 tests the moved owner's row in its original destination bank at the original paid MOVE clock. This package tests the original ADD's read-only source row against a new cut and chart while retaining the moved owner. [#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312) provides a related public counterpart retiming scope. OpenAI Codex and subagents materially assisted.

## Open next questions

Four same-lifetime monotone pairs have multiple intervening ADDs. Choose one exact ordered window, extract its joint external response, and price the necessary changed contract before attempting support. Interacting edits, moving a donor, changing the original counterpart's itinerary, and new paid helpers remain open.
