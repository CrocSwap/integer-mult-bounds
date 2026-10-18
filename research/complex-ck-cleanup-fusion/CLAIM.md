# Sprint claim

- Track: complex supplier. OS assignment seed: 20.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Start: 2026-10-13 04:26:40 UTC. Expected finish: 05:16:40 UTC.
- Object: the selected #626 CK provider's full-frame scalar cleanup.
- Hypothesis: same-source, same-target additions separated only by commuting
  operations can be combined at their later position without changing the
  complete dirty-input map or increasing the absolute prefix envelope.
- Method: exhaust the pair domain in this one cleanup word, then apply a
  deterministic fixed-point fusion pass and exactly replay both orientations.
  Seed 20 selects CK by parity. Full-frame cleanup is selected after excluding
  the already-claimed factory and B-frame tasks.
- Deliverable: exact local circuit evidence, a reproducible checker, source pins,
  negative controls, and a scoped result. No new kappa is assumed.
- Candidates considered: raw factory resynthesis, selected B-frame reassignment,
  and cleanup fusion. #681 and #698 cover the first two. #696 lowers individual
  unchanged macros; this experiment changes the cleanup macro word. #687 changes
  a raw K-triangle read order. No pending result is a dependency.
- Coordination: GitHub's pinned-issue query returned an empty list. No separate
  issue was opened. Open PRs were inspected through #700 before this local claim.
- Scope: only this research package. Keep upstream, accepted supplier sources,
  selected certificates, ownership, frame paths, and recursive profiles unchanged.
- Substantial OpenAI Codex assistance is used for research, code, and writing.

Status: completed, 2026-10-13 04:44 UTC. The initial commuting search found no
candidate among all 78 pairs. One refinement computed the complete conjugated
shear: every pair has a certified rank-two defect in both orientations. No
single rank-one replacement can work anywhere among the unchanged middle gates
on arbitrary register inputs. This is a scoped negative result, with no kappa
claim and no fixed-point optimization run.

Result: [research note](README.md), [exact certificate](CERTIFICATE.json), and
[review branch](https://github.com/thakrarsagar/integer-mult-bounds/tree/research/complex-ck-cleanup-fusion/research/complex-ck-cleanup-fusion).
Reproduce with `python3 -B research/complex-ck-cleanup-fusion/verify.py`.
Expected: `PASS_CK_CLEANUP_RANK_TWO pairs=78 rank=2 columns=312 controls=8`.
The final verification and overlap record is in [VALIDATION.md](VALIDATION.md).
