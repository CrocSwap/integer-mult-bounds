# CK cleanup diagonal scaling, seed 34

- Track: complex supplier. OS assignment seed: 34, drawn with Python `secrets.randbelow(100)`.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Claimed at 2026-10-13 04:53 UTC; expected finish 05:25 UTC.
- Object: selected #626 CK cleanup scalar word. Seed 34 selects CK from the ordered CK/JP8 pair by parity, and forward-first examination.
- Method: carry exact diagonal factors through cleanup additions, adjust coefficients, settle factors at the cleanup boundary, and price every resulting scalar primitive. Stop if the complete cost fails to improve. Check frame boundaries and exact arithmetic envelopes before making any circuit claim.
- Deliverable: one finite circuit result or scoped negative result with reproducible exact checks and source pins. No kappa claim or frontier edit.
- Candidates considered: coefficient-work sharing, fixed-boundary B-frame reassignment, cleanup diagonal scaling. #722 and #698 already cover the first two classes. #696 and #723 change within-macro lowering; #719 studies rank-one replacements of repeated addition pairs. This task changes coefficients by conjugating diagonal scales through additions.
- Coordination: GitHub reports no pinned issues. The open-PR scan covered 542 entries through #723; body searches found no diagonal scaling-fold claim. The local claim is used as requested when no coordination issue exists.
- Contributor: @thakrarsagar, with substantial OpenAI Codex assistance. New work uses the repository Apache-2.0 license.

## Completed result

The all-to-end hypothesis increased the primitive bill. One pivot to exhaustive
single-scale relocation found a 62-real-primitive saving per orientation, moving
the register-97 doubling across 37 cleanup additions. Both implementations
checked all 1,022,007 placements and both 38-column boundary maps. Complete CK
prefix bounds remain unchanged. No kappa claim.

Result and reproduction: [README](README.md), [exact certificate](CERTIFICATE.json),
[validation](VALIDATION.md). The final overlap scan covered 566 open PRs through
#747; #734 and #739 are distinct and credited in the result. The separate worker
remained within this claim and produced the valuation/integer-matrix check.
