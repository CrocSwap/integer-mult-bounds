# Conditional κ ≥ 0.0037194530062 with jointly changed P104 charts

The new word improves the conservative [PR #7660](https://github.com/CrocSwap/integer-mult-bounds/pull/7660) bound by **0.0000023694495 (0.06374%)**. It gives an application **2.46263% above the selected 0.00363005817** under the five retained assumptions. Most of that second difference is predecessor work. Joint changes at 33 scalar contacts remove four native paid positions per invocation. A complete signed caller uses the changed word 17 times. A separate exact-arithmetic and full-extent construction supplies the scalar and private reset actions with new finite physical costs.

| | Selected record | Open parent | This package |
| --- | ---: | ---: | ---: |
| Conditional κ | 0.00363005817 | 0.0037170835567 | **0.0037194530062** |
| Complete paid positions | 117,612 | 108,581 | **108,513** |
| Complete productive fields | 23,392 | 22,461 | 22,461 |

The [proof](PROOF.md) identifies the hypothesis and physical cost of each step. The [literal edit](EDIT.json) reconstructs the candidate from the pinned parent. The [result](RESULT.json) contains the complete paid and target histograms, two independent price signs, compiler and outer bounds, chart verification digests, storage counts and numerical guards. The [input inventory](SOURCE-PINS.json) and [notice](NOTICE) identify the consumed sources. The [coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19697298) tracks this investigation.

## Verification

From the repository root, use Python 3.12 with the standard library.

```sh
python3.12 -B scripts/research_package.py --package research/p104-joint-chart-banks
```

The decisive output includes the following markers. Each of the six disjoint catalogue commands prints its own shard number and coverage.

```text
PASS_JOINT_NATIVE 1501 234 [100502, 187, True]
PASS_JOINT_APPLICATION 0.0037194530062 108513 22461
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-joint-chart-banks outcome=completed
```

The exact arbitrary-input replay checks the 96 A ports, eight B ports, 1,101 helper identities, 234 live-donor erasure witnesses, changed private chart and signed half-ADD. The complete catalogue checks 3,023 operators and 104 main boundary pairs. On the 18 new pairs, the checker also compares all 512 forward and all 512 adjoint columns. Tests reject a phase-only error, a legal scalar sign change with the same invoice, an aliased caller stage, a self-referential witness, a shortened reset extent and an odd last-tick exact division.

The directed raw crossing is between 0.00371945300635 and 0.00371945300636. At the interior probe the compiler passes all 54 strict and four functional outer predicates. Native all-column and adapter realization, owned allocation, compiler closure, fixed-tape movement and storage, and analytic recovery remain conditional. The full multiplier, the historical rounded supplier's fixed tariff and independent human review remain open.

## Open next questions

1. Can a reviewer instantiate the retained allocator and view selector at one materialized compiled parent/child boundary using these immutable guides, including suspended-parent backing and charged movement?
2. Can a different native communication program improve the signed rank surplus of 1,424? A proposed extra saving should retain every independent input, price all new children, and pass the full caller. The fixed word reaches its raw crossing within 1.6 × 10⁻¹³ of the stated claim.
