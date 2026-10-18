# Sprint claim: frames after scalar resynthesis

- Track: bit supplier. OS assignment seed **10**, drawn once with Python
  `secrets.randbelow(100)` at 2026-10-13 15:58:17 UTC.
- Exact base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
- Accepted selection: PR942/T37, kappa `1661960547713947/10^18`, retaining
  PR589 bit word. Followed `selected-result.json` to its source manifest,
  construction, all-T proof, assembly and batch952 maintainer review.
- Three narrow candidates: (1) exact frame reassignment after PR904 four-wire
  resynthesis; (2) after PR936 five-wire resynthesis; (3) after PR952 full
  six-wire resynthesis. Choose the full six-wire case because it changes entire frame-local operators,
  while the prior selected-word optimum does not cover its changed gates.
- Exact object: committed `research/r439-six-wire-boolean/candidate.json.gz`.
  Freeze gate order/operands, start/final frames and nine retained COPY frames.
  Test all legal closed-root-span frame assignments via component enumeration.
  This changes the word underlying PR886's closed frame-only search, rather
  than adding computation to that old domain. No new gate-order search.
- Hypothesis: scalar resynthesis opens frame/profile headroom. Price rank
  moments at the retained exact PR589 bit endpoint before constructing a new
  hosted supplier. Stop after this one fixed-word domain; if no improvement,
  preserve an independently checked scoped negative result. Any improvement
  still needs unchanged H1-H5, complete precision and hosted cost checks.
- Seed use: bit-track assignment and a rotation of independent boundary-control
  nominations by 10; exhaustive coverage is deterministic. Distinctness comes
  from the changed scalar word, not from a different seed.
- Method: source-pinned PR886 nomination, independently checked geometry and
  component costs; exact rational comparisons; meaningful degraded and invalid
  controls. No full multiplication proof or new kappa inferred.
- Expected deliverable: one scoped construction or negative-result package
  with pinned sources, certificate, reproducible checker and clear boundaries.
- Finish: 2026-10-13 16:58 UTC. First 12 minutes reserved for orientation;
  final 15 minutes for verification and handoff.
- Coordination: public paginated metadata checked immediately before this
  local claim. No sprint coordination issue found. PR886 fixes PR589/555;
  PR933 excludes changed words; PR952 and PR980 preserve frame paths rather
  than optimizing them. Local concurrent workers' directories are untouched.
- Contributors: Eva Ayala / GitHub ToikY, with substantial OpenAI Codex
  assistance; predecessor attribution will accompany the result. Apache-2.0.

## Result update

Completed the one-word domain. Independent enumeration confirms 314 free
gates, 137 components and 13,730 component assignments. All 934 strict
alternatives have larger paid moment for every 0 < c < 1, using 933 concavity
certificates and one exact exception lemma. No new kappa. The source checker,
reference replay, independent certificate and six admission tests pass.
The reviewable result, commands and limits are in [README.md](README.md),
with exact evidence in [CERTIFICATE.json](CERTIFICATE.json) and
[VALIDATION.json](VALIDATION.json). Final overlap checked through 16:25:44 UTC;
no duplicate found in the inspected PR bodies. Publication URL is recorded in
the sprint handoff. No coordination issue was available to update.
