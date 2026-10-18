# Validation and overlap receipt

Executed 2026-10-13 on macOS 27.0.1 arm64, CPython 3.14.7. All code uses the
Python standard library. The research base and still-current remote main at
the final overlap refresh were
`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.

## Executed checks

| Command from repository root | Result |
|---|---|
| `python3 -I -B research/p112-masked-tangent-audit/verify.py --write` | Generated the full deterministic certificate; rank 1617, nullity 175, 6720 constraints, 2912 odd edges, nine semantic controls. |
| `python3 -I -B research/p112-masked-tangent-audit/test_package.py` | Five tests pass; runs both checkers with `-I -O -B` in a relocated minimal tree and verifies no files change. Rejects a changed rank receipt, changed proof bytes, a missing proof, and an omitted source pin. |
| `python3 -I -O -B research/p112-masked-tangent-audit/independent.py` | Independent F3 split ranks 868/749 and integer kernel dimensions 28/147; six control groups pass. |
| `python3 -I -B research/complex-decoder-field-extension-seed44/verify.py` | `PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44 p=0..24 examples=3 attaining=25 pairing=14400 controls=7`. Replays the predecessor's pinned geometric premises; does not replace its inherited flat-classification premise. |
| `python3 -I -B scripts/verify_selected_result.py` | Selected record, exact kappa, source inventory and proof supplements pass. |
| `python3 -B -m unittest discover -s tests -p 'test_selected_result.py'` | Five selected-record tests pass. This is the named test file, not every selected-result-related test module. |
| `git diff --cached --check` | Passes for the staged package. |

The two separately written rank computations use different equation systems,
primes, pivot orders and arithmetic representations. Exact integer kernel
identities bridge their modular lower bounds to characteristic-zero equality.
The primary certificate also stores an explicitly rechecked square Jacobian
minor and the complete odd-graph spanning tree. Regeneration is byte-identical
to the saved certificate.

The independent checker's additional diagonal-omission experiment drops the
symmetric rank from 868 to 756. The reciprocal-scaling fixture changes 104
unconstrained directed entries while leaving all 6720 masked entries intact.
The primary checker also proves both scaled factors leave the root-coordinate
space. The rank-nine completion is a scope counterexample, not an eight-term
counterexample.

A separate AI reviewer checked the written component proof and actual package.
The review found no mathematical blocker and requested an exact source-inventory
guard. That guard and its omitted-pin regression test are included. The proof
and two implementations remain AI-assisted work, not independent human peer
review or a proof-assistant certificate.

## Live overlap

At entry, 814 open PRs including drafts were retrieved with titles, bodies and
heads. Decoder-related work was inspected semantically alongside local research
and the PR ledger. Discussions 1163, 1166, 1167, 1200 and 1202 were read.
The selected record's review, manifest, certificate and reproduction target
`make frontier1094-verify` were identified; the selected frontier was not changed.

The pre-submission refresh at approximately 20:13 UTC retrieved **820** open PRs
through **#1211**, and all six active discussions including the new **#1210**.
No identical component/rank result was found in this inspected scope. This is
an overlap check, not a priority claim or proof that no earlier work exists.

- PR1191, head `640b43bb13d3d476a2d83b74ef0d33f14d1b5711`: its full proof was
  read. Its one-root-linear-side theorem permits arbitrary term count; this
  result instead permits two unrestricted factors and classifies one eight-term
  component. No pending code is imported.
- PR1180, head `75b408646d558147a4eb250fc407d1fbfcb8df4e`: inspected PR description;
  all-pairs overcomplete root-linear factors, outside the new component question.
- Discussion1210, Navinor's claim updated `2026-10-13T20:12:07Z`: proposed census
  of 240 root-star supports and 57,600 ordered support pairs, with arbitrary
  term count. This is complementary support-alphabet work, not a continuous-path
  classification. It remains a provisional claim; no result is adopted here.

Public coordination messages were not posted. The task card was kept local;
the submission is one focused research contribution. Source and predecessor
credit appear in README, PROOF and SOURCES.

## Hosted workflow

The follow-up workflow `.github/workflows/p112-masked-tangent-audit.yml` runs the
primary certificate, independent certificate, package controls, inherited
complex-floor replay and selected-record checks on Ubuntu 24.04 with Python
3.10 and 3.14. It includes a final tracked-file cleanliness check. The pull
request records hosted run URLs and their exact commit; the initial local
receipt above does not establish hosted success. Upstream fork runs require
maintainer approval, so a fork-hosted run is identified as such.

## Unrun obligations

No selected-supplier cold replay, repository-wide historical regeneration,
physical/native admission, new moment/outer invoice or Lean
proof was run. None is needed to establish this isolated finite rank result;
none is claimed. The differential and topological steps require mathematical
review, and the copy-cost corollary retains the predecessor's geometric premise
and separate-term cost convention. All-size multiplication, exact recovery,
precision/tape, hosting, common-label/mutable-source and analytic obligations
remain inherited.
