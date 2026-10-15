# Notice

This package accelerates the historical ternary invocation-frame checker in
`scripts/experiments/ternary_side.py:verify_invocation_frames` while preserving
the ternary-side mathematical certificate payload (aside from the single
`ternary_side.py` source pin).

Predecessor credit:

- Douglas R. Colkitt — ternary five-subset DAG, invocation scalar/frame checkers
  and the historical `certificates/ternary-side.json` witness.
- Zhihao Chen / [CrocSwap/integer-mult-bounds#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7)
  — five-subset motif and common-pair geometry.
- Hanson Sun / [CrocSwap/integer-mult-bounds#1217](https://github.com/CrocSwap/integer-mult-bounds/pull/1217)
  (`research/ternary-frame-cache/`) — opt-in exact ordered frame-pair memoization;
  this package puts an equivalent invocation-local memo on the default path and
  does not edit that adapter.
- [CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922)
  — cleared-denominator `product` on `audit_joint_frames.py` and the open
  question inviting the same pattern for ternary-frame inverse work; this package
  answers that ternary stream without editing `audit_joint_frames.py`.

Closest tooling priors on different objects:
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994).

Prepared by Wentao Li with substantial AI assistance under Apache-2.0.
This is not independent human peer review and is not a formal proof of the
multiplication theorem.
