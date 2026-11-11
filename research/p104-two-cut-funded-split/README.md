# Conditional κ 0.003645372367832 from two funded cuts

Two paid rank-one exits and two guarded helper retirements raise the complete
conditional saving by **0.000000482299892** over exact [#7161](https://github.com/CrocSwap/integer-mult-bounds/pull/7161)
at `e3f8d39c43b07063dfc5b800f71c5d21015259e6`. The original event order
is retained. The emitted word has 76,444 events, 1,501 public fields,
67 owned labels and 70 explicit owned lifetimes. Its canonical SHA256 is
`56e1a5e60cecf14991b3169b4575f0b7388d48fa39f261d7a20c7627a8d9e540`.

The rank-four cut uses a symmetric response on donors 988 and 991.
Their later difference at the rank-eight cut is independent of that
earlier response. [PROOF.md](PROOF.md) gives the arbitrary-input
construction. [WITNESS.json](WITNESS.json) pins both cuts, pivots and
scalar coefficients. The exact guard check includes the actual COPY
destination before overwrite.

Each invocation adds two paid rank-one MOVEs and changes the target
counts by `T1 +1, T4 +1, T5 +1, T8 −1`. Across the unchanged signed
17-stage [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113),
the complete invoice has 22,461 productive fields and 110,553 paid
positions. Rank surplus remains 1,424. The raw root is bracketed near
0.003645372367832704847. With the exact target profile and 17 native
words fixed, the ambient-145 fractional remainder ceiling lies between
0.00580691389950 and 0.00580691389996. The claim realizes about 62.78%
of that fixed-profile ceiling. Both comparisons are reproduced from
the literal inventory in [EARLY-RESULT.json](EARLY-RESULT.json).

## Replay

Use CPython 3.12 with assertions enabled.

```sh
python3.12 -B scripts/research_package.py --package research/p104-two-cut-funded-split
```

The runner authenticates the exact retained #7156 archive and #7161
reference files and applies counted adapters only to temporary copies.
It compares the complete frozen early, native and signed-caller receipts.
The proposed claim uses the exact outer application and retains the
selected admitted BIT provider. [REFERENCE.json](REFERENCE.json) and
[INPUTS.json](INPUTS.json) describe the source custody.

## Open next questions

A maintainer can replay the submitted head, review the complete application
against exact #7161 and record a disposition on [PROPOSED-CLAIM.json](PROPOSED-CLAIM.json).
The candidate retains the five conditional framework assumptions. A
materialized whole multiplier and independent human or formal acceptance
remain open. [NOTICE](NOTICE) records predecessor credit and AI assistance.
