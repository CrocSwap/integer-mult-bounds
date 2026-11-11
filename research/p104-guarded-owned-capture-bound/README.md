# Guarded owned capture on the funded-return P104 word

**NO VERIFIED GAIN. Conditional κ change 0%.** Two independent walks of
the exact [#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314)
word exhaust all 76,461 events and agree on 72 owned lifetime IDs and
516 ordered operand accesses. The strictly higher-rank read-chart stock
is empty. Six otherwise eligible lifetimes use one strictly lower-rank
chart. A separately priced exact first-read replay excludes every one.
There are zero equal-rank cases, zero unresolved cases and zero
compatible paid saving.

The edit would delete one fresh INIT and immediate nonzero ADD capture,
the owner's paid MOVEs and CLEAR. It would redirect all original source
ADDs, at their original clocks and common exact chart, to a single
already paid public donor. All other events, endpoints and the signed
caller would be retained. See [PROOF.md](PROOF.md).

## Evidence and reproduction

The comparator is exact #7314 head
`9d0119eb12fbd9fa534b48cd37b68e7099757b91` at κ
`0.003646221436446`, with exact
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
head `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The inherited premises
are native all-columns, owned erasure, compiler, precision/tape, and
analytic recovery. The package authenticates the earlier comparator
admission receipts and reproduces this scoped price and exclusion.

From a clean checkout, use CPython 3.12 with assertions enabled.

```sh
python3.12 -I -B research/p104-guarded-owned-capture-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-guarded-owned-capture-bound
```

Use `--out fresh-directory` for the seven exact plaintext receipts.
The standalone command uses only committed files and the Python standard
library. It prices before support, checks both structural walks and the
lower-chart separators, and rejects changed caller bytes and stale price.

## Open next questions

Could a changed route or retimed first read enable a deletion? Pin one
alternative donor route and preprice every added paid, setup and ordinary
operation before testing exact arbitrary-input and adjoint action at all
uses. Restoration, ownership, compiler, precision and tape still need
verification for any survivor.

## Credit

[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) supplies
the exact word and stationary-capture precedent.
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies
the signed caller. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298),
[#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319) and
[#7332](https://github.com/CrocSwap/integer-mult-bounds/pull/7332) supply
the directed tariff and pricing adapters. Round 41 supplies the earlier
47-MOVE stock, independently recounted here. The individual MOVE studies
[#7307](https://github.com/CrocSwap/integer-mult-bounds/pull/7307) and
[#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308)
and the one-recipient study
[#7165](https://github.com/CrocSwap/integer-mult-bounds/pull/7165)
supply related methods. #7308 gives the predecessor separator coordinates,
which are replayed here directly on exact #7314. OpenAI Codex and subagents
materially assisted.
