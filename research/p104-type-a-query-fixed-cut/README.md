# Fixed-cut Type A QUERY pair correction

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On independently replayed [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ `0.00364665195644`, test two of the four Type A QUERYs at clocks 1516, 1580, 1659 and 1721 in exact [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Replace two QUERYs by ordinary ADDs and insert one proposed same-volume rank-two correction before the first replacement. All 17 J blocks and other paid calls stay fixed. The scoped provider uses two commuting, mutually annihilating rank-one axes.

Two exact unit-body implementations agree on all six pairs. At q=+1 the correction is identity. At q=−1 each defect has rank two. Four pairs have nonzero squared defect and fail the scoped shape. Pairs (1516,1721) and (1580,1659) provisionally pass. The one-pair formal cap selects (1580,1659). Two exact reconstructions verify its correction with all 17 body variables formal, including 36 columns at each of four Gaussian characters, 144 total. Pair (1516,1721) remains unresolved. No physical provider or modified multiplication bound is verified. See [PROOF.md](PROOF.md).

One same-volume edit would change the complete 96-port paid bill by `P1−192,P2+96`, leaving productive targets fixed. The optimistic gross upper is about 0.484699135287 raw at the incumbent crossing. The hypothetical two-disjoint upper is about 0.969398270574. Both are below one extra paid rank-one position. The directed derivative certificate proves that with this debit both edited bills stay negative from the incumbent lower crossing through the retained BIT cap. The two-disjoint grant leaves more than 138.70 raw units of deficit at fixed κ `0.0040075385047236`. No compatible physical saving is certified. The [physical admission note](PHYSICAL.md) derives a rank obstruction for the retained serial one-return interface and identifies the mandatory body in the existing J.

## Replay

Use CPython 3.12 with assertions and the standard library. From a clean checkout:

```sh
python3.12 -I -B research/p104-type-a-query-fixed-cut/replay.py
python3.12 -B scripts/research_package.py --package research/p104-type-a-query-fixed-cut
```

Use `--out` with a fresh path to retain the eight regenerated receipts. See [VERIFICATION.md](VERIFICATION.md) for pins and controls.

## Open next questions

Can a retained physical service supply both inverse-q axes at one rank-two field volume? Start with the directions in PROOF.md and the signed phase compiler. A mixed-sign service with q-even wrappers and no separate ordinary correction cannot implement it directly. A separately priced q-even correction may change this result. A physical candidate still needs all-width forward and adjoint, exact phase, coframes, ownership, restoration, paid and ordinary routing, compiler, precision, tape, caller and outer verification. The other provisional pair remains open.

Credit #7334 for the admitted invoice, #7113 for the signed caller, #7298 for the directed tariff, #7309 for the four-query census and q-even obstruction, and #7310 for the distinct one-removal changed-J obstruction. OpenAI Codex and subagents materially assisted.
