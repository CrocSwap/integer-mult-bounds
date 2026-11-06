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

## Additional all-height upper-proof audit

On 2026-11-06, the fresh reviewer `/root/final_interval_audit` independently
audited the all-height upper argument. This review binds the same four
scientific SHA256 hashes in the table above, including PROOF.md
`eeb46c387e9a3965c9e15a8d75f750796fa1d8d8f1b32a6808bd4feaa799a53a`.
No scientific file changed for this documentation update.

The fresh derivation checked inverse-positive-prefix source nonadjacency,
especially the phase-2 pattern `(1-f,f,v)`, unequal-height zero padding,
and the scratch-row bound `H(k)=floor((k+1)^2/2)`. It verified that the
argument assumes no correlation between source occupancy and scratch
support. The reviewer also checked the rightmost-factor cross-child
estimates, all six phase pairs, reverse and complementary cuts, the
phase-0-to-3 source cancellation or filling `AB-efAB`, and the height-one
and leaf bases. No gap was found in the scoped upper proof.

The reviewer verified the imported source pins. A separate delegated audit
rederived #1085's eight signed prefix cases and corroborated them with 32
abstract free-ring cases and 16 outer inverse identities. These checks do
not assume `e=f`. They support the stated prefix argument; they are not a
comprehensive reproof of every imported predecessor theorem.

This was an author-side AI written-proof audit. It did not rerun the
author's interval census or independently reprove #1374's all-height lower
family, and it supplies neither formal verification nor human acceptance.
The historical #628 proposal is closed and unmerged; that provenance does
not invalidate a theorem about its precisely specified ideal word and does
not provide caller admission. No rounded execution, precision invoice,
selected-framework assumption or new kappa follows from this audit.
