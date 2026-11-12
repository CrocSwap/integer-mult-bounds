# Retimed paid rank-two splits have empty intermediate banks

**NO VERIFIED GAIN. Conditional κ change 0%.** On exact
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334), a
rank-two public paid MOVE can be priced as two rank-one legs if an
existing rank-four or rank-five chart supports a productive rank-9
split into ranks 4 and 5. This checks whether moving the cut anywhere
inside the original mover's contact-free interval supplies a
pre-existing cochart peer. All other roles, operations and ordering
are fixed.

The two occupancy walks exhaust **29,641 cuts in 31 windows**. The
independent walk partitions them into 62 blocks, one on each side
of the replaced MOVE. Every existing intermediate bank is empty
at every tested cut. There is no eligible mixed bank and zero scoped
cases remain unresolved. Support, signed construction and full
caller re-verification were skipped. [Exact proof and price](PROOF.md).
[Reconciled windows](receipts/R98-AGREEMENT.json).

## Replay

The independently reproduced comparable witness is
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`,
κ = `0.00364665195644`, with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The retained
native all-column, owned-erasure, compiler, precision/tape and
analytic recovery premises stay fixed.

From a clean checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B research/p104-retimed-paid-rank-two-empty-banks/replay.py
```

The standard-library replay rebuilds the directed price, both occupancy
walks, and the agreement receipt, and rejects changed price and word
inputs. It needs no Git metadata, network, external root, or prior
temporary state. Use `--out fresh-directory` to keep the four regenerated
JSON receipts. The package includes one copy of the exact word, the
two compressed predecessor receipts and their published manifest,
[provenance](PROVENANCE.json), and [path-keyed hashes](LOCAL-PINS.json).

## Open next questions

Can one explicitly priced change to another role's itinerary create
an eligible cochart peer without another raw rank-one debit? Start
with the exact windows in the agreement receipt. Freeze one chart,
one peer and its relevant contacts, and compare the complete signed
invoice before attempting support. Other paid ranks, new chart
frames, changed ownership and wider retiming are outside this test.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
supplies the exact native word and comparable witness.
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supplies the signed caller.
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
supplies the original-clock 95 anchors, 285 quotient lines, and
directed price receipts. Its initial pricing uses the directed tariff
from [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298).
[#7148](https://github.com/CrocSwap/integer-mult-bounds/pull/7148)
and [#7117](https://github.com/CrocSwap/integer-mult-bounds/pull/7117)
supply earlier timed paid rank-two subdivisions on different words
and chart ranks. OpenAI Codex and subagents materially assisted
the proof, implementation, independent checks and packaging.
