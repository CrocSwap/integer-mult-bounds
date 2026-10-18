# Claim: portable native-byte binding for the PR626 owner check

- Track: verification engineering; OS assignment seed **88** (`secrets.randbelow(100)`).
- Upstream base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Claim recorded: 2026-10-13 04:43 UTC; expected finish: 05:10 UTC.
- Exact object: the four regenerated native gzip hash checks in
  `research/complex-k492-owner-repair/extras/check_owner_map.py`.
- Hypothesis: changing gzip representation alone rejects an unchanged native
  word/program; full decompressed-byte binding can remove that false rejection
  while preserving all existing owner/profile/moment computations.
- Method: source-pinned opt-in adapter, same-input original/adapted subprocess
  comparisons, all four native inputs, metadata and compression variants,
  proof-relevant payload mutations and source-drift controls.
- Deliverable: one isolated tooling package, reproducible command, exact source
  pins, equal original receipts, failure controls, timings and scope statement.
  No supplier or exponent change.

## Selection and overlap

Three candidates were inspected:
1. Exact frame algebra reuse: already covered by open #367.
2. Parallel isolated test execution: overlaps open #154.
3. Native gzip binding in the independent PR626 owner checker: selected.

Seed 88 selects verification engineering and is reused to select the scalar
mutation site, header timestamp and alternating benchmark order. The bit-side
geometry/determinant candidates are already addressed by #709/#707. This is a
representation-reproducibility experiment, not another numerical search.

Read CONTRIBUTING.md, selected-result.json, current-status.md, pr-ledger.md,
the selected K492 review, both construction proof notes and the actual owner
checker. Selected conditional kappa is 51110230636731/31250000000000000.
Open issue search found only #650 (discussion request), no pinned sprint
coordination issue. Claim therefore remains local. Open tooling and gzip PRs
were inspected through #710. #695 reconciles Linux execution evidence and does
not repair this check. #220 (Maxime Fleury, following Antoine Olivier) supplies
the accepted container/payload convention; this work applies it to a different,
currently selected independent checker. #675 audits owner boundaries, not this
representation boundary. No prior failed search is being reopened.

## Access and provenance

Shell GitHub DNS is unavailable. The necessary upstream source subset was
fetched through the GitHub connector at the exact base above; the 12 execution
inputs were checked against their Git blob IDs. The local branch is
`seed88-native-payload-binding`. Its initial snapshot commit is local transport
bookkeeping, not the upstream base. Existing files and upstream/ stay unchanged.

Prepared for @MrPink604 with substantial OpenAI Codex assistance. Apache-2.0.

## Result update (completed 2026-10-13 04:51 UTC; publication resumed 05:00 UTC)

Completed: the original checker rejects all 16 representation-only variants;
the opt-in adapter produces byte-identical complete receipts. All 16 malformed
container or changed-payload cases are rejected, including four seeded scalar
changes that preserve the recounted widths/profiles. Six additional override,
relocation and source-drift controls pass. Both exact moments, 72 calls, 35,424
roles and rank mass 520,704 remain identical. No new kappa.

Final source refresh still gives base 66849e1475c930fd7732b1a0067ffee7e1e95f60.
The publication refresh covered the latest open PRs through #734 and a targeted
gzip/payload search without a matching native-owner gzip-binding fix. #695 and
#675 remain distinct as above. New #727 (Agastya Sondhi / TMM2009, head
71ba94c981477b3527ef21dd0f8140e795a7664d) optimizes the same checker's footprint
sets using bit masks; it does not replace this native-container comparison.
Neither adapter is imported or composed here.

Open-issue refresh still finds only #650, so there is no coordination comment
to update. The first handoff was a clean patch because upstream branch creation
returned HTTP 403. The user subsequently created a writable fork. Publication
uses the exact upstream base, with only the seven files in this directory:
[contribution branch](https://github.com/MrPink604/integer-mult-bounds/tree/seed88-pr626-native-payload-binding/research/pr626-native-payload-binding).
The API-fetched local snapshot commit is not part of the submitted ancestry.

Reproduce with:

```sh
python3 -I -B research/pr626-native-payload-binding/verify.py
```

See README.md, SOURCES.json, EVIDENCE.json and EXPECTED-OWNER-CHECK.json for
provenance, complete local evidence, inheritance and limits.
