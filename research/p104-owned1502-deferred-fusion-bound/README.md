# Deferred chart-905 repair for the owned role 1502 fusion

**NO VERIFIED GAIN.** On exact #7481, a proposed fusion replaces owned role 1502's rank-one MOVEs 33140 and 33142 by one rank-two MOVE from chart 541 to 117 and omits the intervening ADD33141. The fixed repair deadline is immediately before ADD43317, the observer's first outward read after it arrives at chart 905. Grant the repair the entire edited bank, including the arriving role 152 and the edited observer 1489.

The exact public input with coordinate 2 equal to −4 and all other coordinates zero makes both edited bank rows zero. The old observer is 4, and the original outward ADD produces −2 in role 152. Any homogeneous linear correction using the edited bank gives zero. A sparse reverse solver derives the separator and an independent normalized forward replay checks both literal prefixes and the active bank. This exhausts one route at one cut with zero unresolved cases.

The hypothetical paid change has directed gross between 0.08584222521755123 and 0.08584222521755124 raw across all 17 signed calls, before any corrections. An added rank-one paid child per edited native call costs 17 raw. No saving was realized. See [proof and price](PROOF.md), [path pins](PINS.json) and [receipts](VERIFICATION.md).

## Replay

From a clean POSIX checkout with CPython 3.12 and its standard library:

```sh
python3.12 -I -B research/p104-owned1502-deferred-fusion-bound/replay.py
```

Expect `PASS_OWNED1502_DEFERRED_FUSION_BOUND`. Each scientific process is capped at 30 seconds. The package needs no network, Git objects or prior temporary state for direct replay.

## Open next questions

Can an earlier encoding or a different already-paid operation transport the missing observer direction before its first outward read? The complete chart-905 bank at the tested cut cannot supply it. Name the candidate operation, sender, receiver and deadline, then check signed support before pricing the full repair. Earlier correction, different paid routing and changes to the downstream interface remain open.

## Credit

[#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) supplies the literal native word and price, with [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) in its native lineage. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller. [#7003](https://github.com/CrocSwap/integer-mult-bounds/pull/7003) and [#7494](https://github.com/CrocSwap/integer-mult-bounds/pull/7494) supply outward timing precedents, [#7482](https://github.com/CrocSwap/integer-mult-bounds/pull/7482) exact covectors, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) directed tariffs. [#7491](https://github.com/CrocSwap/integer-mult-bounds/pull/7491) checks terminal receiver banks, [#7492](https://github.com/CrocSwap/integer-mult-bounds/pull/7492) checks a distinct owned fusion, and [#7495](https://github.com/CrocSwap/integer-mult-bounds/pull/7495) and [#7500](https://github.com/CrocSwap/integer-mult-bounds/pull/7500) check different deferred repairs. [#7508](https://github.com/CrocSwap/integer-mult-bounds/pull/7508) supplies prior public byte copies. OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.
