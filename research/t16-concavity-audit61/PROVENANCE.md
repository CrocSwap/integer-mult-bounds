# Scope selection and source provenance

Track: seed61 adversarial mathematical audit, round24. Fixed repository base
`ba82555c64e1879e4b7decce28186f208fcb8262`. Read the selected-result record,
community-batch1047 review, selected T16 sources and inherited hosting proof.

Three candidates considered: (1) exact all-concave comparison of the four
admitted T16 maps; (2) single-call capacity-greedy fixed-point audit; (3)
physical-stock/symplectic-row formula audit. Candidate1 was claimed before
the main experiment and completed. Candidates2/3 were not pursued.

Inputs are the four immutable `community-batch1047-audit/variants/pr*/...`
PLAN/OWNERS pairs, the selected PLAN/OWNERS for equality binding, the existing
hosting proof, and the maintainer's review. SOURCES.json pins the exact
required inventory: text after CRLF-to-LF normalization and gzip bytes
exactly. BASE-SELECTED.json is a separately hash-bound frozen context record;
the moving selected-result pointer is not a replay dependency.

Curiosity Bot live overlap checks on 2026-10-13:

- [PR1042](https://github.com/CrocSwap/integer-mult-bounds/pull/1042): actual
  selected packing claim. This audit compares its whole residual vector with
  all three reviewed T16 predecessors; no new packing is proposed.
- [PR1049](https://github.com/CrocSwap/integer-mult-bounds/pull/1049), Sagar
  Thakrar: independent mutable-leaver semantics/profile audit, including the
  raw per-cell delta correction. That scope is explicitly excluded here.
- GitHub provider searches `is:pr "majorization" "1042"` and
  `is:pr "coordinate" "T16"` returned PR1042 and the distinct fixed-family
  PR890. A broader T16 owner search found PR1050/1053/1055/1061/1065/1068/
  1074/1087 and rank-seven variants1104/1107. Those later optimization claims
  are outside the four-map domain; none is treated as admitted or audited.

The result differs from the earlier batch's native-gate omission atlases,
round20 H1/H3 target-feedback cleanup criterion and round18 probe optimum:
it gives a counterexample inside the actual concave power-cost family and
complete exact relations among four already admitted owner maps. It also
does not repeat the valid upstream admission or allege a missing proof.
