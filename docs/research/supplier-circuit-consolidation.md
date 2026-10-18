# Proposed supplier-circuit integration batch

This is a reviewable integration candidate for PR681, based on
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. It is not a publication receipt or a
change to the selected frontier. See the [executable package](../../research/supplier-circuit-consolidation/README.md),
[proof](../../research/supplier-circuit-consolidation/PROOF.md),
[exact-head dispositions](../../research/supplier-circuit-consolidation/DISPOSITIONS.json),
and [validation](../../research/supplier-circuit-consolidation/VALIDATION.md).

| Complete measured bill | Before | After |
|---|---:|---:|
| R420 local XOR additions | 26,916 | 18,378 (31.72% fewer) |
| R420 hosted instructions | 8,603,712 | 6,144,768 (28.58% fewer) |
| Selected CK forward scalar real primitives | 224,938 | 169,618 (24.59% fewer) |
| Selected JP8 forward scalar real primitives | 257,232 | 200,380 (22.10% fewer) |
| Raw complex factory forward primitives | 170,488 | 123,768 (27.40% fewer) |

The bit hosted prefix allocation increases from 192 to 256 bits and is fully
repriced. Its two-level allocation remains 512 bits. κ remains
`0.001635527380375392`; instruction savings are not an exponent or runtime claim.

The batch retains six complete research packages: Ali Romman's #688, mtpsl's
#691, Greer Guthrie's #694, Sagar Thakrar's #696/#708, and Scott Woolsey
Biggart's #713. yongjae321's #670 and x0hu's #674 circuits are retained through
#688's vendored certificates. Alluri's #681 factory changes are composed with
#696 on the raw complex word. Credit remains with the circuit authors.

Integration required two compatibility changes: target-row factoring is rerun
on the helper-transformed compensation matrix, and 23 of #708's 27 decoder
pairs are selected under the unchanged local precision cap. The original
packages and their complete recipes are also preserved and separately replayed.
The semantic D-prefix extension is explicit; old literal H2 checkers are not
weakened. Actual native and hosted programs are checked independently.

The central ledger's historical dispositions are unchanged. After this batch
is merged, maintainers can compare the six imported PRs' current heads with
the retained heads and resolve fully covered research contributions with a link
to this evidence. The #670/#674 subset does not establish complete-PR coverage.
No automatic merge or closure is performed. Later commits and unreviewed
higher-κ proposals remain separate work.

Prepared for Alluri with substantial OpenAI Codex assistance, Apache-2.0.
No independent human review, full theorem formalization or practical speedup
is claimed. Inherited compiler, physical, hosting, tape and analytic assumptions
remain as stated in the selected review.
