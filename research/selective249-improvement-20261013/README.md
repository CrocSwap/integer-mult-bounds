# Selective helper-249 dispatch

Conditional **κ = 0.001636472098484378**. This exceeds
[PR639](https://github.com/CrocSwap/integer-mult-bounds/pull/639) by
`0.000000010505707262` and [PR640](https://github.com/CrocSwap/integer-mult-bounds/pull/640)
by `0.000000007408721083`.

A new cold-basis cancellation lets JP8 helper 249 end at dimension 8. The native
paid-profile delta is `{1:+2,2:-1,4:+1,5:-1}`, and its width drops from 9 to 8.
Using this supplier at 12 selected calls, alongside 59 original JP8 calls and
one original CK call, admits an owner map with idle profile `{48:2230}`.
The exporter records 235 changed rows relative to pinned PR639.

The selection matters: using the new supplier at every JP8 call cannot beat
PR639 within the fixed geometry and moment model, even with ideal packing.
The [exact exclusion](ALL71-EXCLUSION.json) is reproducible with
`python3 check_all71_exclusion.py --package witness --out /tmp/all71.json`.
The twelve-call choice matches unused capacity to multiples of 48. This is a
construction and dispatch improvement with an exactly validated literal map.

The [portable witness](witness/README.md) includes the new supplier constructor,
independent mathematical check, all pinned sources and exact owner reproduction.
The [packing supplement](../selective249-packing-20261013/README.md) records the
literal assignment. [Fixed-dispatch packing proof](PACKING-SCOPE.md) explains why
its idle moment is optimal for these fixed inputs; no universal optimality or
all-dispatch-count optimum is claimed.

Before publication, exact bindings, physical owner admission and 31 mutations,
the invoice, both moment engines and 155 assembly controls passed. Independent
native/owner/rational checks and five mutations also passed. The full fresh
replay passed **82/82 stages**, without reuse, in 425.33 seconds. All 63 artifact
and 82 log hashes were independently checked. Every supplemental proof,
mutation check, owner reconstruction and recipe reconstruction passed. Complete
evidence is in [validation/](validation/). Execution was on macOS; no Linux
replay is claimed.

```sh
PYTHON=python3 sh research/selective249-improvement-20261013/witness/verify.sh /tmp/selective249-fresh
```

Use Python 3.10+, a C++ compiler, Boost headers, and a new output directory.
The inherited all-size, compiler, realization, analytic-transfer and bit H1–H5
premises remain. Prepared by Chi Zhao with substantial OpenAI Codex assistance;
upstream contribution and license notices remain in the witness.

The fresh replay used commit `12b98ab8f76a3ae9bc26191b7812889dafd4d3ae`. After success,
only the witness README and its manifest entry changed. The
[documentation update record](DOCUMENTATION-UPDATE.json) confirms that all
319 other manifested files are unchanged.
