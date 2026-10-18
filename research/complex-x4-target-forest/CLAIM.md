# Sprint claim

- Track: complex supplier; OS-random assignment seed **34**.
- Base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
- Claim recorded: 2026-10-14 Australia/Melbourne.
- Expected finish: 2026-10-14 00:45 Australia/Melbourne (2026-10-13 13:45 UTC).
- Object: the selected PR799 X4 zero-frame arbitrary-helper compensation matrix.
- Method: restored signed target forests, extending the disjoint pair class of
  PR901. Exact binary-Horner prices include both basis boundaries. Test whether
  a minimum-spanning-tree formulation yields a cheaper complete circuit.
  Seed 34 determines deterministic tie ordering, not mathematical coverage.
- Deliverable: one source-pinned finite construction or scoped negative result,
  exact reproduction, arbitrary-input replay and corruption controls.
- Three candidates considered: X4 overlapping target forests (chosen); nonunit
  target pairs (closed by PR909); JP8 coefficient-work sharing (substantial
  existing coverage in PR722/739/751/755/811/830/839/882).
- Overlap: PR901 disjoint X4 pairs; PR909 excludes nonunit disjoint pairs;
  PR816 and PR917 use target forests in historical CK compensation. This
  contribution will credit the mechanism and check a complete selected-X4
  circuit, including the minimum-cost forest claim if justified.
- Coordination: live pinnedIssues query returned no pinned issues; sprint issue
  search returned none. Local claim used. Open PR metadata inspected through
  PR925 immediately before this claim. No other issue opened.
- Timing: orientation bounded to first 8 minutes of a 40-minute session;
  final 10 minutes reserved for verification and handoff.

## Completion

Submitted one contribution: [PR932](https://github.com/CrocSwap/integer-mult-bounds/pull/932).
The selected-X4 forest has 6 roots and 106 edges, reduces compensation from
6,320 to 2,324 additions, and saves 47,690 real primitives per orientation.
Its exact scoped floor is 10,883 primitives per real component. Full scalar
replay, independent Prim/cycle/operator checks, nine package tests and selected
record checks pass; VALIDATION.md records remaining integration obligations.
No new kappa is claimed. Final overlap refresh reached #931, with #901/#816
heads unchanged and no competing selected-X4 forest found. No pinned issue
was available, so this is the single local claim update with the result link.
