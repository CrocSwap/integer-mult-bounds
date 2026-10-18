# Independent arithmetic audit of PR #1407's complex profile

**Status: completed, scoped independent verification. No new construction or κ claim.**

PR #1407 proposes a neutral whole-helper hosting construction for the selected
PR1094 owner map. I do not repeat its search or replay its owner paths. This
package independently checks the resulting profile arithmetic with a third,
code-disjoint exact interval engine: the primary and conservative complex root
brackets, the unchanged bit ceiling, and the published κ grid. The upstream PR
reports two exact moment engines; this audit adds a separate rational
atanh/Taylor implementation while leaving its construction proof and native
admission as inherited claims.

## Frozen data and exact result

The research/source base is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Before publication, `main`
advanced to `410026dc5513b87db92ae98571d1d5984c69a983` through three
reconciliation commits. The selected certificate and the seven other pinned repository
inputs/provenance files have identical Git blobs at both commits; the audit
branch is based on the refreshed `main`, while `TASK.json` and `SOURCES.json`
retain the exact research base. The selected record binds at
`κ = 836330098538459/500000000000000000`, with complex endpoint
`67018507072324140917/40000000000000000000000` and bit endpoint
`1733427039589844234749/10^24`. The source construction and maintainer review
are pinned by `SOURCES.json`.

The external candidate snapshot is PR #1407 at exact head
`d8640f5b7ae99b43f5d56146cb94ca62b8b3835d`. `REFERENCE.json` contains the
candidate profile, endpoint receipts and the original SHA256 and Git blob
identifiers for PR #1407's `PROFILE.json`, `RESULT.json` and `ASSEMBLY.json`.
I fetched that exact PR commit through the upstream pull ref and independently
recomputed all three Git blob IDs and content SHA256 values; all six matched
the recorded pins. Its snapshot hash is also pinned in `SOURCES.json`.

The candidate profile changes from the selected
`{1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152, 48:4866}`
to
`{1:349605, 2:60192, 3:62585, 4:20448, 5:11808, 8:1152, 16:3, 48:4866}`.
The exact delta is `+e1 - 7e7 + 3e16`: rank mass and deficit stay fixed,
while the positive-rank call count drops by three. The priced parameters are
`m=73`, `W=14336`; the primary complex moment has no added surcharge. The
conservative check includes the inherited term
`32*m*N/(10^16*W) * m^a`.

| profile and moment | lower endpoint (`M(a)-1` scaled by `10^32`) | upper endpoint (`M(a)-1` scaled by `10^32`) |
|---|---:|---:|
| selected primary | `[-130421533, -130421532]` accepted | `[162472375, 162472376]` rejected |
| PR #1407 primary | `[-159548291, -159548290]` accepted | `[133342011, 133342012]` rejected |
| selected conservative | `[-281245180, -281245179]` accepted | `[11648729, 11648730]` rejected |
| PR #1407 conservative | `[-171561767, -171561766]` accepted | `[121328535, 121328536]` rejected |

Each displayed integer interval is divided by `10^32`. The exact brackets
reproduce the receipts. The candidate's primary and conservative complex
brackets both move above the selected brackets, and both remain below the
unchanged bit endpoint. Exact flooring of `a/(1+a)` to the repository's
`10^-18` κ grid reproduces the candidate and conservative κ values. The
primary κ difference is exactly `161104813/7812500000000000`.

## Independent interval method

`verify.py` uses only Python's standard library and `Fraction` arithmetic. It
computes logarithms after binary range reduction with 48 positive atanh terms
and the explicit geometric tail
`2*z^(2N+1)/((2N+1)*(1-z^2))`, where `0 <= z <= 1/3`. It encloses each
positive exponential with 32 Taylor terms and a geometric bound on the
remaining tail. The verifier does not import either moment engine used by
PR #1407 or the selected assembly.

Failure controls mutate one rank-16 count, swap accepted and rejected endpoint
labels, change κ by one grid unit, and omit the conservative surcharge. Every
mutation is rejected. The saved exact replay is [RESULT.json](RESULT.json).

Reproduce from the repository root with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/pr1407-complex-moment-audit-seed39
```

Expected: `PASS_REGISTERED_RESEARCH_PACKAGE research/pr1407-complex-moment-audit-seed39 outcome=completed`.

## Scope and limits

This confirms the finite arithmetic receipts derived from the two histograms.
It does not verify PR #1407's 24 owner moves, its all-input dirty-state
argument, strict source-event windows, native T16 execution, controller,
invoice, all 47 outer inequalities, or full ancestry. The audit does not
establish that the published reassignment realizes the candidate histogram.
PR review and hosted-workflow status are mutable. This package pins the
candidate content at the exact head above and makes no claim that its
construction, CI or review gates are approved.

## Open next questions

The next useful step is a fresh, independent replay of PR #1407's native path
and a role-by-role check of its eleven neutral-then-concentrating paths. That
matters because profile arithmetic alone cannot establish physical admission.
The open blocker is the draft PR's pending review and workflow approval.

## Credit

PAI (@pai-scaffolde) supplies PR #1407's candidate profile and receipts. Rohan
Arun's PR #1094 supplies the selected owner map; Jeremy Kothe and Hao Yan / FanPUYen
supply the retained packing and controller lineage. The selected construction
and its maintainer review remain the pinned baseline. Prepared by Cinna Davis
(@1337isnot1337) with substantial OpenAI Codex assistance in review, exact
arithmetic design, implementation and writing. This is a code-disjoint audit,
not independent human review. New material is Apache-2.0.
