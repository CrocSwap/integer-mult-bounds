# Sprint claim and handoff

- Assignment seed: **67** (Python OS-backed `secrets.randbelow(100)`, obtained 2026-10-13).
- Assigned track: 60–74, adversarial mathematical audit.
- Repository base pinned: `ba82555c64e1879e4b7decce28186f208fcb8262` (main at beginning of investigation).
- Investigated predecessor: PR #1125 at `9f7c0679d64bab954b7161d8586dc626a59b92ee`; source certificate blob `9a2cd574df48361579167e39aa6198f39059f70c`.
- Three candidates: (1) independently replicate 0/1-survivor-loss widths; (2) classify two-erasure widths; (3) complete all-survivor width spectrum with automorphism and dual witnesses. Selected (3), encompassing (1) and (2) in a new finite statement.
- Claim: exact widths of the 255 nonempty projections of the frozen 104-mask cube support family; no claims outside term-preserving carrier interface.
- Method: induced-tree enumeration; exact bipartite matching to construct chain partitions; alternating-path antichains; independently verified dual witnesses; cube symmetry under 48 explicitly checked automorphisms.
- Expected deliverable: self-contained Python 3.10+ standard-library package, 21-orbit certificate, proof, negative controls and review notes.
- Coordination: no pinned sprint issue was found in available issue search. This claim was recorded locally, not posted to GitHub.
- Status: ready for focused review; PR not submitted because the connected GitHub account has no push rights to this repository and no supported fork action was available.
- All inherited assumptions and explicit provenance are recorded in PROOF.md and SOURCES.json.
