# Validation and handoff

Executed on 2026-10-13, Linux 6.18.44 x86_64, Python 3.13.15.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Audited PR387 head: `d9fb9410b1ae6f6ada376a1e7fd12bc176e476ea`.
The source head was refreshed before submission and had not changed.
The final pre-submission queue snapshot contained 586 open PRs through #767.
The 19 arrivals after the initial snapshot concern other objects; no matching
five-level bootstrap audit was identified. The pinned-issue list remained
empty. Ahrazzle's two PR387 reviews were read and credited; their reported
three-level arithmetic is distinct from the new variable-savings ceiling.

## Completed checks

```sh
python3 -I -B -O research/bootstrap-depth-audit/verify.py --check research/bootstrap-depth-audit/EXPECTED.json
python3 -I -B -O research/bootstrap-depth-audit/test_audit.py
python3 -B scripts/verify_selected_result.py
git diff --check
git diff --exit-code -- upstream certificates/selected-result.json
```

- Exact deterministic receipt matched. Depths 0 through 5 are excluded;
  the pinned six-round compact margin is admitted; nine controls are rejected.
- All seven tests passed. These include all 1,536 four-level schedules over
  two upper endpoints, three initial savings and four per-level choices;
  every intermediate depth is checked directly against the original three
  cost exponents. They also cover 2,400 strict-grid cases, 42 closed-form
  comparisons through depth 20, the failure of the monotonicity claim outside
  its domain, and process-level source/receipt tampering with Python `-I -O`.
- All ten retained source files were compared byte-for-byte with
  `git show <audited-head>:<upstream-path>`, in addition to the reproducible
  SHA256 and Git-blob checks in the verifier. No predecessor code was imported.
- The repository's selected-record checker passed with
  `51110230636731/31250000000000000`.
- `upstream/`, the selected record and all pre-existing tracked files remain
  unchanged. No global artifacts were regenerated.

The first development run rejected an overly narrow display enclosure for
the sixth-level slack. Exact evaluation gives approximately
`0.4061096846138577 * 10^-18`; the final asserted enclosure is
`(0.406, 0.407) * 10^-18`. This was a new audit-display error, not a failure
of the predecessor witness. The five-level exclusion was unaffected.

## Checks not claimed

`make selected-record-check` could not start because `make` is absent in this
environment; its exact Python recipe was run successfully as shown above.
The repository-wide `make verify`, the expensive selected-supplier cold replay,
PR387's full supplier suite, its two moment engines and the other assembly
constraints were not rerun. This addition changes none of their inputs.
No remote CI pass, alternate-interpreter execution, formal proof-assistant
check, separate agent review or human review is claimed.

The source-pinned moment bracket and completed ordinary-supplier interfaces
remain assumptions of this audit. The new evidence is the written uniform
recurrence envelope and its exact evaluation, not a replay of those assumptions.

## Reviewer entry point

Read the identity in PROOF.md section 2, the necessary compact-margin inequality
in section 3 and the source-bracket limitation. The exact exclusion is one
positive integer cross-product in EXPECTED.json. The stronger-initial-supplier
control demonstrates why the starting saving is part of the claim. Reproduce
with the first command above; no network or third-party dependencies are needed.

The result is a scoped negative result within PR387's certificate accounting.
It supplies no new κ and makes no change to the selected frontier.
