# Bound Type B stage-17 idle retirement at J17

**Outcome** — Scoped exclusion. The complete bound is unchanged.

At the two legal stage-17 body signs, the exact Type B endpoint changes on four independent roles. Deleting either paid singleton idle leaves at most three directions of body-sign change with an arbitrary replacement at the original two-role J17 contact. Deleting both leaves at most two. An independent forced-map replay also shows that each deletion needs J17 to act on both global roles 52 and 53 in addition to its original roles 36 and 37.

The optimistic paid saving before any host changes is about 63.5165 raw per retired idle across eight ports, or 127.0330 for both. The signed obstruction excludes all three retirements at the retained host. [Proof](PROOF.md)

## Replay

From a clean checkout on a POSIX host, use CPython 3.12 with assertions and its standard library.

```sh
python3.12 -I -B research/p104-stage17-idle-retirement-bound/replay.py
```

The replay authenticates bundled inputs, regenerates the forward and reverse receipts, and compares the exact capacities, outside-host entries and directed quotes. It rejects a changed caller. Expected final line is `PASS_P104_STAGE17_IDLE_RETIREMENT_BOUND`. [Verification](VERIFICATION.md)

## Open next questions

- Can one enlarged or moved host realize the four-coordinate action on arbitrary input while charging less than the original invoice? Start with one exact contact and its ownership and restoration schedule, then price all routing, precision and tape changes before building it.
- Can a different mechanism move or share body-dependent work while preserving the productive endpoints? Pin which paid and productive occurrences change and compare the complete invoice before testing a new signed lowering.

## Predecessors

- Clear1nsight’s #7334 `aaeec8c0acf01e99a5f331ef363a698d9c084ace` supplies the complete comparator, κ = 0.00364665195644. Rohan Arun’s #7113 `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the literal signed caller and its physical body model. [Comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/7334), [signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
- Exact #7402 `ac7a4b1ebaa300408511470db8fcbe054f843348` supplies the stage-17 clock inventory, a forward event evaluator and the prior fixed-J derivative scope. Exact #7406 `a5fa7b464a773afb47eb8b9725b94f660c407528` supplies the two-idle rank-two pair and physical stage-17 Walsh sectors. [Fixed-host transfer proof](https://github.com/CrocSwap/integer-mult-bounds/pull/7402), [two-return proof](https://github.com/CrocSwap/integer-mult-bounds/pull/7406)
- #7362 and #7298 supply the directed-price receipt and rational tariff lineage. Exact retained files and source hashes are in `PROVENANCE.json`. [Price receipt](https://github.com/CrocSwap/integer-mult-bounds/pull/7362), [tariff precedent](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)

OpenAI Codex and subagents materially assisted the proof, implementation and independent replay.
