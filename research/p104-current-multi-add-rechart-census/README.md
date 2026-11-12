# Current-word multi-ADD public rechart census

**NO VERIFIED GAIN.** On exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), change one common interior chart of a closed public-helper component with at least two literal ADDs. Keep all outside charts, initial and final charts, chronological scalar operations and incident paid MOVE clocks fixed. Each MOVE must retain positive rank. Both literal walks exhaust 1,301 multi-ADD components. Of these, 824 touch main or owned segments and another 43 touch fixed endpoints. Among the 434 closed pure interiors, 420 are nonpositive even before geometry and all 14 remaining relaxations fail exact span geometry.

The 14 potentially positive stock keys are precisely the 13 inherited keys from [#7361](https://github.com/CrocSwap/integer-mult-bounds/pull/7361) and the chart-746 key from [#7369](https://github.com/CrocSwap/integer-mult-bounds/pull/7369). This census starts from the full current literal word and certifies that the combined prior list has no missing current-word price-positive case. It adds the stock exclusion for the other 420 closed pure interiors. There are zero new positive keys and zero unresolved cases in scope. The optimistic one-edit upper is below 0.106305391209185 raw. The sum of the 14 relaxed uppers is below 0.993184112588 raw before compatibility. Actual compatible saving is zero.

From a clean POSIX checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B research/p104-current-multi-add-rechart-census/replay.py
```

The runner replays independent forward disjoint-set and reverse breadth-first chronology engines, verifies both directed invoices and every exact geometric row, rebinds public predecessor receipts, and rejects a damaged word and changed chart-746 control. See [proof](PROOF.md) and [verification](VERIFICATION.md).

## Open next questions

Simultaneously promoting multiple adjacent components may relax the outside-chart barriers. Start with one fixed vector and propagate a forced successor closure through the unchanged paid nesting DAG, then fully price that joint edit. Allowing an incident MOVE to disappear or changing a fixed endpoint is also outside this census.
