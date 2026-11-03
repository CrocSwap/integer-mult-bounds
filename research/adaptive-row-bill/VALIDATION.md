# Validation record

Local interpreter: CPython 3.12.13, macOS arm64, standard library only.
The exact executable was
`/Users/aliromman/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`.

The registered ordinary and optimized commands passed. Both emitted the same
receipt: 2538 families, 12200 policies, 181 safe, 2357 unsafe, 1629 prefix checks,
and 18 rejecting controls. A separate direct ordinary run also passed.
The independent oracle uses permutation determinants and Cramer's rule; it
imports neither the producer's elimination nor its policy decisions.

At scientific commit `76447bc104e91e731ff1ddb663dcf867d7a52f86`, committed-byte
and owner-execute-mode checks passed for all eight package files. The official
export and its declared-input integrity check passed. Both scientific commands
passed from the exported files with empty PATH, no Git checkout and read-only
files/directories. All nine file hashes and modes, including export metadata,
remained unchanged. Ordinary and optimized stdout were identical.

The checkout is shallow. Full-history source preflight was not claimed. The
package is a direct descendant of the declared canonical base; all provenance
pins resolve at that base. There are no external runtime inputs or side-branch
Git dependencies. This removes the missing-predecessor clean-checkout issue.

Canonical main was fetched again before submission. Its base, priority and
selected-record files were unchanged. The initial complete overlap cache covered
409 open PRs and 6362 Discussion records. Submission checks read later Discussion
claims and new open PR bodies through PR6466. No matching row-menu certificate
was found. Sparse local notes and unpublished work remain coverage limits.

Hosted CI is recorded in the PR after the published head is available.
No independent human review, formal proof-kernel acceptance, selected-supplier
replay or new kappa is claimed. No fragile workaround is used.
