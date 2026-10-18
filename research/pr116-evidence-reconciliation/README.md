# PR116: source-identical scientific head, distinct evidence head

**Research consolidation; no new kappa.** PR116's later head changes only a
README status paragraph, that README's SHA-256 in `SOURCE.json`, and a new
author validation receipt. Its producer, proof, scientific certificate,
workflows and all other tracked files are unchanged. This independently
corroborates the [round-eight review](../../docs/research/community-round8-review.md)
by resolving its historical source-identification question. It does **not** turn
the earlier triage into mathematical acceptance.

**Current integration, 2026-10-16:** PR116 has since been reviewed, incorporated
and closed in the [92-contribution review](../../docs/research/community-reconciliation92-review.md).
That later decision remains authoritative. `PARENT-EVIDENCE.json` lets
`scripts/reconcile_pr_queue.py` append this independent source/evidence pointer
without changing any disposition, closure, review-completion field, remaining
question or earlier evidence. Regenerate both ledger files with that generator;
do not restore the submission-time `changed_since_review` row. This package
does not declare PR1007 itself reviewed or incorporated.

The new evidence is an offline, hash-bound comparison of the **complete Git
trees**, plus recovered GitHub metadata and focused-job log excerpts. The
checker imports no contributor checker and does not trust GitHub's changed-file
list or a `git diff` report. It decodes Git objects itself. No source package is
installed as a supplier.

## Exact provenance and result

| Role | Commit |
|---|---|
| Research base | `8bddbee377e2f3ce1f1247196c4b290d55767d20` |
| PR116 historical scientific head | `97750ec74fc714638c0aa4f31aaa880e56cb8b4d` |
| PR116 current evidence head | `295a48a3b966428896057a98c6b4834c0b4b7416` |
| Actual focused CI checkout | `0db8566d07ae1fd7765d5d98fbb32ad22775ed32` |
| CI merge's main parent | `56b66d58297deca1d7dd130247d720e960f77a37` |

`CERTIFICATE.json` preserves 208 raw commit/tree/blob objects with both Git
object IDs and SHA-256 digests. The parser checks every tree recursively:
1,559 tracked paths become 1,560, with exactly three changed paths. No unchanged
subtree is assumed from a contributor-supplied path list. Git's normal
content-addressing assumptions apply; this is not a Lean proof of Git or a
cryptographic authenticity signature.

The 42 entries in the historical source manifest comprise 18 package inputs
and 24 repository dependencies. **41 retain identical Git blob IDs and modes**;
the remaining entry is the README. The only manifest value changed is its
README hash, and both README hashes are recomputed. The scientific certificate
blob is also supplied, checked against its manifest hash, and retains
`49349675169/500000000000000`. The other unchanged dependency blob contents are
not copied or rehashed to their manifest SHA-256 values in this capsule; their
byte identity between the two anchored trees is the narrower claim checked.
The original `SOURCE.json`, embedded verbatim, retains all predecessor pins,
including PR114 `51cd8934128be37830981ca391d3d6fd28b0fce8`, PR115
`cf60442983c153a3a0f5272ea4713f99eba13c86`, and Swapnil Jain's round-seven source
`741e7aa078392553815df7926ee17ac5e25a8c38`.

The accepted base remains PR942 at `1661960547713947/10^18`, with PR589 on PR555.
PR116's much older exponent is a historical witness only. The selected source,
its review, and its U8/T37 construction were followed before choosing this task.
Neither that selection nor `upstream/` is changed.

## CI attribution and the remaining evidence gap

The author's receipt lists 42 checks. A fresh GitHub API read on 2026-10-13
returns the same 42 unique job URLs, names, timestamps and successful outcomes:
36 research-artifact jobs, three cyclic-deferred jobs and **three cube-deferred
jobs**. This is not 42 independent reviews of the PR116 mechanism.

The [focused run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/37865435177)
used Python 3.11, 3.13 and 3.14. Its recovered job metadata records successful
package verification and `git diff --exit-code` steps. Each log records the
package pass and 14 tests. The complete `gh run view --log` rendering's SHA-256 and explicitly
selected, job-associated excerpts are preserved; the offline checker validates
those excerpts and their metadata, not the authenticity of GitHub's service.

A `pull_request` check's `head_sha` identifies the associated PR head, not
necessarily the checkout. Here the three checkout logs name the synthetic
merge `0db8566…`. Its actual Git tree is **identical** to the historical PR head's
tree (`a644e4d6b08a6851199b12b576383cba980a77be`). The offline checker binds both
commits and the merge's two parents, establishing source identity without
conflating the two commit IDs. This checkout reconciliation is scoped to the
three focused jobs; the other 39 checks have matching metadata, without a
fresh checkout-log audit here.

The author's separate 3,733.46-second local full-suite receipt is internally
consistent, but its named `full-verify-evidence.tar.gz` is not tracked at either
PR head and was not recovered in this run. Its reported archive/log digests
remain author evidence. No fresh full `make verify`, supplier replay, Lean build,
or local-run reproduction is claimed. Earlier maintainer evidence was
`alternative-or-parent` triage, explicitly without standalone full-certificate
validation. At this package's original submission, mathematical mechanism review,
acceptance and PR closure were still maintainer decisions, and the ledger used
`changed_since_review`. The later completed PR116 review and closure now replace
that status; this package adds historical evidence without reopening the question.

## Reproduce and controls

From any working directory, using Python 3.9+ and only its standard library:

```sh
python3 -I -O -B research/pr116-evidence-reconciliation/verify.py
```

When invoked outside the repository, supply the script's absolute path. Expected:

```text
PASS_PR116_EVIDENCE_RECONCILIATION changed_paths=3 unchanged_dependencies=41 checks=42 focused_jobs=3
```

The command needs neither Git, network access, the historical checkout, nor
third-party packages. It compares its complete derived result to `RESULT.json`.

```sh
python3 -I -O -B research/pr116-evidence-reconciliation/test_package.py
```

Expected: **28 tests pass**, including 26 corruptions: incomplete or altered Git
objects, type confusion, extra objects, duplicate JSON/tree names, truncated or
misordered trees, missing/duplicate/wrong-head/failed CI checks, missing matrix
jobs, skipped verifier steps, wrong actual checkout, misassociated logs, and
omitted package/control outcomes. Semantic CI controls run below the immutable
Git digest gate so they exercise the admission logic, not just hash rejection.
Optimization is deliberately supported by this checker; it uses explicit
exceptions rather than Python assertions.

`build_certificate.py` is an optional authoring tool. It reads the three exact
commits from a Git object database and these pre-downloaded public inputs:

```sh
gh api 'repos/CrocSwap/integer-mult-bounds/commits/97750ec74fc714638c0aa4f31aaa880e56cb8b4d/check-runs?per_page=100' > checks.json
gh api repos/CrocSwap/integer-mult-bounds/actions/runs/37865435177 > run.json
gh api repos/CrocSwap/integer-mult-bounds/actions/runs/37865435177/jobs > jobs.json
gh run view 37865435177 --repo CrocSwap/integer-mult-bounds --log > run.log
python3 -I -B research/pr116-evidence-reconciliation/build_certificate.py \
  --repository . --checks checks.json --run run.json --jobs jobs.json \
  --log run.log --observed-on "$(date -u +%F)" --out candidate-certificate.json
python3 -I -O -B research/pr116-evidence-reconciliation/verify.py --certificate candidate-certificate.json
```

The fetched historical commits must be available locally; they can be fetched
by the exact IDs above. Future GitHub retention/reruns may change API/log
availability, so the saved offline capsule is the reproducibility target.
The metadata snapshot is an observation, not a promise of future CI status.

## Credit, scope and sprint coverage

Rohan Arun authored PR116, its validation receipt and predecessor PR111, with
OpenAI Codex/Anthropic Claude assistance as disclosed in the original sources.
Credit remains with icekylinx for PR115/104, eumemic for PR114 and its audit,
Avi Eisenberg for the lifted/deferred compiler, Rohan Gupta for the dual-suffix
identity, Swapnil Jain for the round-seven source, and the other contributors
named in the embedded original README/SOURCE. Douglas Colkitt's round-eight
review and saved comparison first recorded that this increment was evidence
only; this package corroborates that observation using a different parser and
recovers the actual focused CI checkout provenance.

Ross Richardson prepared this reconciliation with **substantial OpenAI Codex
assistance** for analysis, implementation, tests and writing. Apache-2.0;
original notices and attribution are retained. No independent human review is
claimed. Inherited all-size, stopped-product, endpoint, fixed-tape, precision
and analytic obligations remain outside this source/evidence check.

Seed **96**, scope selection and the single overlap-driven pivot are recorded
in `CLAIM.md`. The completed finite domain is the two complete source trees,
the three exact delta paths, all 42 manifest entries, all 42 recorded checks,
and the three focused jobs; no optimization or mathematical search was run.

## Open next questions

- Can the author's historical full-run archive be recovered? Its original
  receipt names the archive and digests, but the bytes are absent from both
  pinned heads. Obtaining and authenticating that exact archive would strengthen
  historical execution evidence; its absence does not undo the later review.
- Can this consolidation be incorporated alongside the later PR116 decision?
  Review the new evidence-only ledger input and the preserved source capsule,
  then retain the existing closure and attribution. PR1007 review remains a
  maintainer decision; no further supplier or theorem claim follows from it.
