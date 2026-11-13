# Fixed-bank repairs for the chart 431 owned transports

**NO VERIFIED GAIN.** On exact #7481 at `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b` and signed #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, three independent exact separating inputs exclude the tested source and receiver interfaces for two chart-431 owned transport proposals. Each proposal has the same optimistic gross around 0.11809207775534 raw before ancillary costs. The complete comparable κ remains 0.003647081039689.

## Reproduction

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-chart431-owned-transport-bounds/replay.py
```

The package authenticates exact inputs and runners, reconstructs all six receipts, and checks directed price and rejecting controls. See [proof](PROOF.md), [verification](VERIFICATION.md) and [source credit](PROVENANCE.json).

## Open next questions

The three named cuts are exhausted. A different earlier encoding, new carrier, changed paid itinerary or a changed receiver bank remains open. Before building, price one named already-paid arrival and require it to carry the exact old operand and restore its independent value by the original deadline.
