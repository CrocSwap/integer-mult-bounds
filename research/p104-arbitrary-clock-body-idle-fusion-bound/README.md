# Bound arbitrary-clock fusion of Type A body idles

On the exact [#7334 benchmark](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) with the [#7113 signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), replace two Type A body idles with disjoint stage masks by one whole union-mask body on one field. Allow that body at any clock and keep the surrounding scalar, body, signed and paid itinerary fixed.

One physically realizable joint negative body specialization gives a different exact transported projector at every one of the 224 disjoint-mask pairs. All are excluded. The best quoted pair at clocks 1448 and 1763 also fails literal omission at output row 1 and input column 0, where 0 becomes −4. The optimistic combined saving of any disjoint matching is below 238.182 raw before ancillary work. No complete construction or exponent change follows.

From a clean POSIX checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B research/p104-arbitrary-clock-body-idle-fusion-bound/replay.py
```

The standard-library replay authenticates bundled inputs by path and runs two independent exact engines. It compares all case keys, projector witnesses and the literal control, and rejects a corrupted caller. Expected marker `PASS_TYPE_A_BODY_IDLE_FUSION`. No previous temporary files, Git history or network is required for the standalone command.

## Open next questions

Could a different body supplier realize a two-field action at a single priced occurrence? Specify its physical axes, exact scalar action on two independent dirty inputs, routing and restoration before repricing. The one-field union-mask operator considered here becomes the identity at the joint negative specialization. Operators that do not have that specialization and changes to the fixed surrounding itinerary require separate tests.

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supply the exact comparator and caller. [#7305](https://github.com/CrocSwap/integer-mult-bounds/pull/7305) supplies a related fixed-slot BIT exclusion method and [#7357](https://github.com/CrocSwap/integer-mult-bounds/pull/7357) addresses a distinct Type B odd/even idle family. [#7435](https://github.com/CrocSwap/integer-mult-bounds/pull/7435) supplies the source-pinned caller export and retained scalar walk. [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) supplies directed pricing. OpenAI Codex and subagents materially assisted the proof, implementation, independent replay and packaging.
