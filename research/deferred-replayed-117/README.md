# Deferred readouts on PR117's 28,705-role complex producer

Conditional κ = 6783925373/(6.25·10^13) = **1.085428059680 × 10^-4** — **+3.875% over PR #117**
(1044939/10^10) and +9.97% over PR #116.

PR #117 (eumemic) found an h = 24 all-disjoint complex DAG with only 28,705 roles, but charged its
complex side with PR #104's plain profile (no deferral): a_c = 26129/(2.5·10^8) binds.
PR #110 (and #114/#116) showed deferred readouts pay on the complex network under PR #104's
one-child rule. This witness runs the same deferral algorithm, with its producer adapter, expected graph counts and pair-star order updated on PR #117's DAG.

| h = 24 complex | PR #117 | this |
|---|---:|---:|
| additions / matched / roles | 91,770 / 71,185 / 28,705 | same DAG, same 28,705 roles |
| deferred roles | — | 3,020 |
| complex saving (binding) | 26129/2.5·10^8 = 1.045160e-4 | **108566486/10^12 = 1.085665e-4** |
| κ | 1.044939e-4 | **1.085428e-4** |

Bit side: Swapnil Jain's round-seven deferred word under PR #104's one-child rule — the same bit word
as PR #117 and PR #110/#116 (`bit-profile.json`, coarse 620523/(5·10^9), stopped 1.2402e-4).

## Files and checks

```sh
python3 research/deferred-replayed-117/complex_deferred.py   # ~2 min; DAG replay, matching, lifted frames,
                                                              # deferral, arbitrary-scratch replay, exact F2 checks
python3 research/deferred-replayed-117/certificate.py         # exact moments, next-grid rejections,
                                                              # expanded scalar charge, 47 constraints, 7 margins
```

- `replayed.py`, `complex-dag.json.gz`: copied unchanged from PR #117; every support, label, rank,
  root identity, ÷21 decoder/scatter identity, nesting and nondegeneracy is recomputed from operand pairs.
- `producer.py`: adapter exposing `build` and the pair-star order (ascending) to the deferral compiler.
- `complex_deferred.py`, `certificate.py`: PR #116's deferral compiler and certificate with only paths, the
  pinned graph size (91,770 / 8,120 / 71,185 / 28,705) and the complex constant changed; the certificate
  also requires κ above PR #117 and PR #116. The unit-shear correction below additionally increases the scalar guard.

Scope: finite conditional witness under PR #104's written interfaces and PR #110's stated deferral argument
(see the PROOF.md files of PR #110/#116 and PR #117). No optimality or practical-speed claim.

Credit: eumemic (PR #117 DAG and PR #114), Avi Eisenberg (PR #110 deferral), Swapnil Jain (deferred
readouts, round-seven word), icekylinx (PR #104/#115), PR #116, and all predecessors in PR #104's
NOTICE/SOURCES. Composition by Rohan Arun with Anthropic Claude assistance. Apache-2.0.

## Unit-shear audit correction

Independent exact expansion found a largest old-readout coefficient of 55/42, so the inherited PR116 audit's bound of one was insufficient. The corrected implementation splits each coefficient into at most two unit-magnitude shears at the same frame (55/42 = 1 + 13/42). The exact audit checks every decomposition, charges every piece in both directions and preserves the full child histogram. The certificate doubles the previous conservative local scalar-work bound and recomputes all guards; kappa remains unchanged. Eight new controls cover unpaid pieces, incorrect signs, dropped terms and exact dirty-value shear/inverse action. See [PROOF.md](PROOF.md).

```sh
python3 research/deferred-replayed-117/test_unit_readouts.py
python3 research/deferred-replayed-117/audit.py --source research/deferred-replayed-117/complex_deferred.py
```

The original failed audit log is preserved in the local build evidence. The corrected independent audit passed: all 11,862,912 nonzero old readout coefficients are covered by 11,862,944 unit shears (32 extra scalar additions), and the forward/reflected child histogram is unchanged. The doubled conservative scalar guard still supports the same exact kappa. `python3 research/deferred-replayed-117/verify.py --full` reproduces source pins, profiles, assembly, controls and this audit. Combined verification passed. The original full invocation on `ec862a5af51537495c745d9f2323e8a5736ee265` passed `make -j1 verify`, producer, bit and certificate commands, then failed the inherited unit-coefficient audit; its sixth planned equality command did not run. The corrected `verify.py --full` passed on `6ec868e8568ca9a74b7245494de1b187c7be78fe` in 303.50 seconds, including exact regenerated artifacts, pins, eight controls and the paid unit-shear reflected audit. The broad sources and physical producer/DAG/profiles are byte-identical across these commits, and both runs had no source drift. All 42 corrected-head GitHub checks passed. This is combined coverage, not a monolithic full-make run on the corrected commit. See [validation.json](validation.json).
