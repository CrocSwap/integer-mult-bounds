# Deferred six-recipient repair for owned 1551

**NO VERIFIED GAIN.** On exact #7481 at `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b` and signed #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, two exact separating inputs exclude the tested chart-127 repair interfaces after deferring six owned1551 ADDs. The earlier input kills four named carriers and edited recipient 873. The later 20-coordinate input kills all 644 edited chart-127 rows at the first outward deadline. The strongest independently reproduced comparable κ remains 0.003647081039689.

## Reproduction

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-owned1551-fanout-banks/replay.py
```

The replay authenticates inputs and runners and regenerates the exact separators, chronology and price. See [proof](PROOF.md), [verification](VERIFICATION.md) and [source credit](PROVENANCE.json).

## Open next questions

Both named cases are exhausted. Earlier corrections, altered source histories, different banks and changed paid itineraries remain open. Price one named new route and require exact source support and all six old recipient and ownership returns before a build.
