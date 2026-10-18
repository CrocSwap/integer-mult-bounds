# NOTICE

Prepared by **Aaron Wang**, with help from opencode (substantial AI assistance; no
independent human review or proof-assistant formalization is claimed). New material
is Apache-2.0 under the repository license.

Pinned predecessor material (byte copies under `inputs/`, hashes in `SOURCES.json`):

- PR #1391 (Cinna Davis / 1337isnot1337), head
  `6ce8017e4c27c8b220b6c3a27a53bb18f138212a`: the order-four child family and its
  basis replay, via `inputs/PR1391/CERTIFICATE.json` and `inputs/PR1391/verify.py`
  (snapshots as retained by `research/z4-distinct-source-seed55/inputs/PR1391/`).
- PR #1410 (Cinna Davis), head `5b1c00b9f2770aabaa0085539405757f7818a14a`: the
  same-source persistent boundary, via `inputs/PR1410-README.md`.
- `research/z4-distinct-source-seed55` (Cinna Davis): the phase-indexed typed child
  contract `C_(i,t)`, the exact boundary recurrence, the two-bank wrapper/handoff
  accounting and the 5|5 construction this package reproduces as its positive
  control. The model loader and word machinery in `verify.py` follow that package's
  `verify.py` with attribution.
- `research/z4-heterogeneous-pair-seed3x7` (PR #1768, 1337isnot1337): the
  heterogeneous 3+7 reader schedules `[0,1,2]` and `[2,1,0,2,1,0,2]`.
- `research/z4-persistent-pair-seed57` (PR #1410 package, Cinna Davis): the paired
  order-four boundary lineage, credited through the pinned README snapshot.

Selected-result context: Rohan Arun's PR #1094 on Jeremy Kothe's #1087 construction,
resolved through `certificates/selected-result.json`; nothing in this package
changes it. No κ, supplier, moment or frontier claim is made.
