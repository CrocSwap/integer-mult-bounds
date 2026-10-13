# Review of PR681 circuit consolidation

**Finite circuit integration; no new κ and no measured runtime claim.** Alluri's
`e536f6fc8aad65adef8ac4682d13625598a5c3f9` composes six retained research
packages and two vendored circuit subsets. Source-pinned local and full hosted
maintainer replays passed, followed by minimal-source relocation and five
package rejection/output-preservation controls.

| Measured bill | Before | After |
|---|---:|---:|
| R420 local XOR additions | 26,916 | 18,378 |
| R420 hosted instructions | 8,603,712 | 6,144,768 |
| Historical CK forward real primitives | 224,938 | 169,618 |
| Historical JP8 forward real primitives | 257,232 | 200,380 |
| Raw complex factory forward primitives | 170,488 | 123,768 |

The composition correctly recomputes target factoring after helper factoring:
for involutions H and P it implements H, P, PKH, P, H, preserving arbitrary
helper and target inputs. Its frame-zero D operator equals the old complete
operator; it does not falsely claim the new syntax satisfies literal H2.
The canonical D with the changed A/B/C passes H1–H5, and semantic substitution
is valid at this uninterrupted common-frame boundary. Actual native and hosted
checkers separately consume the changed word.

All 27 decoder pairs would need 105 bits and are rejected. The retained 23
pairs pass the strict local 104-bit cap. Global prefix allocation increases
from **192 to 256 bits**; the two-level allocation remains 512 bits. Both are
recomputed, not inherited for free. The 120,960 whole helper invocations,
recursive profile and exponent stay unchanged. C++ checks cover 5/9/11 stages,
96 bridge omissions across the two words, and each word's 17 parent and 16
hosted mutations. Exact results equal the submitted HOSTED.json.

Complex lowering checks all rational columns and per-register containment in
the old macro's prefix envelope, including cleanup of its private work register.
Raw factory resynthesis and selected-provider lowering are distinct bills;
the raw changes have not been transported into either the old selected recipes
or the new #741 supplier. Original finite/tape/all-size assumptions remain.

Credit: **Alluri** for composition and raw factory circuits; **Ali Romman** for
#688's two-block and hosted infrastructure; **mtpsl** for #691's quad;
**Greer Guthrie** for #694's helper basis; **Sagar Thakrar** for #696 lowering
and #708 decoder sharing; **Scott Woolsey Biggart** for #713 target factoring;
**yongjae321** and **x0hu** for #670/#674 blocks. #686's earlier compensation
idea and semantic D contract retain attribution. The six imported package
source files match their cited Git objects. Their pending branch-level
closures remain separate; #670/#674 have only subset coverage.

## Reproduce on current main

These packages pin the historical #626 selected-record bytes. To preserve their
sources while allowing the frontier to advance, the integration wrapper makes
an isolated minimal source closure and supplies the immutable #626 checkpoint
at that closure's original selected-record path. It never overwrites the live
selected record or relaxes any source hash.

```sh
python3 -B scripts/verify_supplier_consolidation.py --hosted --out /new/external/directory
# Add --package-tests for the relocation and rejection suite.
```

The original package entry point remains useful in its original pinned checkout.
The new CI wrapper uses the historical closure. Contributor validation is kept
separate from our fresh [RESULT.json](../../research/community-circuits681-audit/RESULT.json).
