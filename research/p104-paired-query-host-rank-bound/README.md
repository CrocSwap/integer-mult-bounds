# Paired Type A QUERY demotions into one existing J

**NO VERIFIED GAIN. Conditional κ change 0% relative to #7334.** Demote two of the four original-clock Type A QUERYs at 1516, 1580, 1659 and 1721 to their phase-even ADDs, and allow one of the 17 already paid J hosts to change on the same 36-role port. All 102 exact pair and host combinations fail a rank-two phase-defect capacity. The direct calculation gives a nonzero 3×3 minor for each required host difference at `q = ±1`, with all body values one. An independent endpoint argument gives a required defect rank of at least four for every host. All 102 cases were visited and zero remain unresolved.

## Complete price

The independently reproduced comparator is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, κ = 0.00364665195644. The exact [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json) is shared by all 96 Type A ports.

The one-pair relaxation removes 192 rank-one positions, changes the paid total from 110,519 to 110,327, retains 22,461 productive fields, and changes rank surplus from 1,424 to 1,616. The paid J stock is held fixed. The complete signed invoice grants any extra setup, owned state, routing, restoration, precision and tape for free at this gate. Granting compatibility for two disjoint QUERY pairs gives the optimistic stock bound 384. All tested single-host replacements fail before any extra charge. The disjoint two-pair price is a relaxation and supplies no conclusion about joint replacements with interacting hosts.

## Replay

Use CPython 3.12 with assertions. From a clean repository checkout:

```sh
python3.12 -B scripts/research_package.py --package research/p104-paired-query-host-rank-bound
```

A Git-free export of this directory also runs with `python3.12 -I -B replay.py`. Pass `--out <new-directory>` to retain regenerated receipts. The replay authenticates the exact caller and predecessor endpoint engine and receipt, rebuilds the prior and revised directed prices, replays the signed endpoints and controls, verifies all 102 modular minors, and rejects a changed caller. Path-keyed hashes are in [LOCAL-PINS.json](LOCAL-PINS.json). Exact source links and Git blob IDs are in [PROVENANCE.json](PROVENANCE.json).

See [PROOF.md](PROOF.md) for the rank-four derivation and [VERIFICATION.md](VERIFICATION.md) for check coverage.

## Credit

[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the literal signed caller and Type A J lowering. [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supplies the complete comparator, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies the directed arithmetic. [#7309](https://github.com/CrocSwap/integer-mult-bounds/pull/7309) supplies the exact signed endpoint replay, its controls and the slack lemma. [#7310](https://github.com/CrocSwap/integer-mult-bounds/pull/7310) solves one QUERY demotion into one changed J. [#7342](https://github.com/CrocSwap/integer-mult-bounds/pull/7342) covers a standalone paired correction with the existing J chronology retained. OpenAI Codex and subagents materially assisted.

## Open next questions

A continuation can price one explicit all-width host with phase-defect rank at least four and compare its complete signed bill before replaying a candidate. Changes to multiple hosts, shared odd state or wider ports require their own interface and price. The selected result stays unchanged.
