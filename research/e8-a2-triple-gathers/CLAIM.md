# Local research claim and completion record

- Date: 2026-10-13
- Seed: **44**, generated from OS randomness (`secrets.randbelow(100)`)
- Track: structural decoder, seed range 40–49
- Public source pin for preparation: `66849e1475c930fd7732b1a0067ffee7e1e95f60` (from PR #703; remote clone unavailable)
- Candidates reviewed:
  1. Closed-neighborhood overlap in three-port E8 A2 batching (**selected**): characterize exact minimum distinct read sources, all triples, with positive and negative controls.
  2. Four-port A2 batching: larger and not investigated.
  3. A partial K/M face carrier bypass: already under #683; declined to avoid overlap.
- Specific object: 120 antipodal E8 root lines, their 57-member closed gather sets; all 280,840 triples.
- Method: root-coordinate exact enumeration, Gram-rank classification, independent intersection/union counts, algebraic A2 edge-closure argument.
- Deliverable: `verify.py`, independently implemented `crosscheck.py`, frozen `RESULT.json`, `PROOF.md` and `README.md`; no existing files changed.
- Result: 1,120 A2 triangles attain minimum union **84**, all other triples union ≥100. Optimistic 16-occurrence triple-batching advantage relative to generic triangles; physically unpriced, no κ claim.
- Baseline comparison: #446 copy-rank obstruction, #620 E8 decoder floors, #703 Hurwitz copy floor, #697 direct-source E8. None is described as superseded.
- Execution: Python 3 standard library, `python3 -B research/e8-a2-triple-gathers/verify.py` from repository root.
- Checks: passed all 280,840 triple consistency checks in two independent implementations and 7 intentional negative controls in this environment. Whole selected cold replay was not run (independent self-contained research note only).
- Coordination: no open pinned issue visible from public GitHub issue listing; no authenticated GitHub posting access; claim kept local. This is not a posted/accepted pull request.
- Assistance and credits: substantial GPT-6 assistance. Mathematical root-system and community context credited in `README.md`; no prior program copied. User identity/attribution to be supplied before submission.
