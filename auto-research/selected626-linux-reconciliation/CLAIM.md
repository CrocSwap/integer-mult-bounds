# Sprint claim

- Track: research consolidation; OS-random assignment seed **95** (`secrets.randbelow(100)`).
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: the pending/queued Linux status in the selected #626 integration receipt,
  for run `38317651752` at `ed49217ad6244f1d3bfe4588f122fa861849739c`.
- Method: inspect that exact completed run and its artifact; check all orchestrator
  stages, log digests, exact composition and tested-source equality to the base.
- Deliverable: a preserved, offline-checkable provenance receipt with rejection
  controls and a narrowly scoped current-status correction. No new kappa claim.
- Claim time: 2026-10-13 04:08 UTC. Expected finish: 04:30 UTC; final quarter
  reserved for verification and handoff.
- Coordination: GitHub's pinned-issue list is empty, Discussions is disabled,
  and the only open non-PR issue is #650 asking for Discussions. No reservation
  issue was opened. Open PR titles and #675's body were checked for overlap.
- Candidates considered: (1) selected source-manifest completeness;
  (2) #620 partial-review status versus predecessor attribution;
  (3) queued-versus-completed #626 Linux evidence. Seed `95 % 3 = 2` selects
  the third candidate after the overlap screen. The first two already have
  explicit coverage in the selected checker/review; the third has a concrete
  newly completed result to reconcile.

Prepared by Josh Snider (`jsnider3`) with substantial OpenAI Codex assistance.
Apache-2.0. This claim is local because no sprint coordination issue exists.

## Result — 2026-10-13 04:21 UTC

Submitted [PR #695](https://github.com/CrocSwap/integer-mult-bounds/pull/695):
preserved the completed Linux evidence and checked 39 source objects, six replay
stages, 64 complex receipt substeps and 47 positive assembly margins. All 16
rejection controls passed, including normal/optimized isolated runs from a
separate committed-files-only worktree. Selected-record and ledger checks passed.
The three differing generated provenance digests and unavailable CI payloads
are documented explicitly; no new kappa or full theorem is claimed.

Final overlap check through #693 found no matching run reconciliation; upstream
main remained at the recorded base. No pinned sprint issue was available, so
this is the single local claim update with the result and handoff link.
