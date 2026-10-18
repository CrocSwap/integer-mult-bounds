New implementation and independent verification: Tekalign (tekuuu), with
substantial OpenAI Codex assistance, 2026. Apache License 2.0 (repository LICENSE).

The frozen input is an exact reconstruction of PR699 by jeremykothe2/BRoute,
building on icekylinx's gauge44 work, BlockInvert's promotions, Q6Reviewer's
controls and the source lineage in PR699's SOURCES.json and NOTICE.md.
The unchanged owner assignment descends from chafreaky's PR685 and PR660,
with contributor lineage credited in PR699's README. PR741 by chafreaky
concurrently published the same eight-frame improvement before this submission.

verify_global.py and freeze_spec.py adapt the PR699/PR676 orchestration;
audit_owners.py adapts PR685's literal-owner audit. exact_intervals.py is copied
unchanged from research/complex-k492-owner-repair/extras/exact_intervals.py.
All these sources retain Apache-2.0 provenance. The external pinned packages
are not relicensed; their existing license files and notices apply.
