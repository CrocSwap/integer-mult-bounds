# Exact-commit cross-review

Reviewed on 2026-11-06 by a separate OpenAI Codex worker in the @CubeJerry
research session. This is an independent AI derivation/code review within
the author-side workflow, not independent human or proof-kernel acceptance.

The reviewed commit is `485c8174677bfef24472d4cdf46e83574cfc3b44`.
The reviewer checked a clean working tree and these exact SHA256 hashes:

| File | SHA256 |
| --- | --- |
| PROOF.md | `eeb46c387e9a3965c9e15a8d75f750796fa1d8d8f1b32a6808bd4feaa799a53a` |
| verify.py | `5687a7fbec81378d66f514a006cd327dd9cb6156cab19089b0f8f42ca141e48e` |
| scalar_oracle.py | `9213efcd7dafd9a171c0b6d60c9badf6307c945e6d031702ce19a584767b4ac9` |
| CERTIFICATE.json | `ea0061f56cfdc39fee148e401b9d88cfddaea0760c6d2daa7d0926a68bb3afb7` |

The reviewer independently checked the scratch-pair restriction, inverse
source-column nonadjacency (including phase 2 and unequal-child padding),
both cross-child product orders, all six phase identities and their reverse
directions, the first-to-last phase endpoint cancellation, induction height
inequalities and the negative-word reduction. No unresolved scientific gap
was found under the explicitly imported #1085/#1278/#1374 premises.

Implementation inspection confirmed that the formal verifier retains
noncommuting and repeated factors, uses the correct leaf and inverse-prefix
updates, and maps complementary cuts correctly. Its controls distinguish
the inverse direction, factor order and a changed leaf sign. The compressed
scalar route is meaningfully distinct from the literal polynomial engine.
The registered commands correctly omit `-I`, since the verifier imports its
sibling scalar module by name.

The reviewer did not rerun the author's already-passed scientific suite and
did not independently audit the imported predecessor theorems. The original
normal/optimized runs, provenance-pin check and committed-byte check remain
author-side evidence, with the shallow-history limitation described in the
README. This review supplies no rounded-caller admission, selected-framework
assumption, precision invoice or new kappa.

This follow-up adds only the review record; the four scientific files above
remain unchanged from the reviewed commit.
