LOCAL CLAIM AND RESULT — GitHub Discussion posting unavailable

Track `bit-mechanisms`; OS seed `6e5256110feb8b034f6afef8802f497c`; task
`bit-new-register-model`; scope key `74c418ed2b3f8f8a98e2`; priority revision 3;
exact base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Local advisory expiry: `2026-10-14T09:37:35Z`.

Question: in exact `F2[S4]` formal algebra, with three arbitrary dirty scalar
roles, can the target `diag([s1*s2*s3],[s1*s2*s3],[e])` be realized in at most
five calls `I+([s]+[e])N`? Here `s1=(12), s2=(23), s3=(34)` are each paid at
one call, `N` ranges over all 28 rank-one idempotents of `M3(F2)`, arbitrary
free scalar `GL3(F2)` mixing is normalized into the paid factors, and the
third role must be restored. The direct bill is six calls; a candidate saving
would be one call (16.7%). The model optimistically assigns no additional
hosting price to the third role or free scalar mixing and does not claim
physical compilation.

Method/domain: exact `F2[S4]` coefficient matrices and all 84 paid factors.
A complete radius-two ball from identity and radius-three ball from target
covers every word of length at most five because every factor is an
involution. Stop at 110 seconds or 1 GiB RSS; report incomplete coverage if
capped. The actual run completed in 2.29 seconds at 60,576 KiB RSS on Python
3.12.3.

Final overlap check: 405 open PR records were fetched over REST during
07:40–07:43Z; no exact S4/adjacent-transposition/four-cycle match appeared.
Nearest scopes are PR #1478 (UT3 central targets, r=2,3), PR #1705 (four GL2
coordinate-SWAP targets at r=4), and PR #1711 (two AGL2 affine targets at r=2).
The cached complete discussion pagination has 351 records fetched at 07:28Z;
direct reads of #1167 and #1317 reached 07:22Z and 07:31Z and contain no S4
claim. A fresh complete Discussion refresh failed with GitHub's GraphQL rate
limit error; REST GET succeeds, but this installation returns 404 for
Discussion comment create/update, so this claim was kept local.

FINDING: the exact radius-two/radius-three meet has layer counts `[1,84,4697]`
and `[1,84,4697,232692]`, state totals 4,782 and 237,474, and zero meetings.
The direct six-call word passes. Literal convolution confirms all 84 factors
square to identity; six direct-word omissions and a changed-third-role endpoint
are rejected. Thus the declared S4 target has exact minimum six; the tested
one-call saving does not exist. This closes only the specified finite model.
No selected-supplier occurrence, recursive moment change, physical compiler
saving, or new κ is claimed. The selected binding-only baseline currently
reports the complex primitive as binding.

Full package and deterministic receipt: `README.md`, `TASK.json`,
`CERTIFICATE.json`, `SOURCES.json`, `VERIFY.json`, and `verify.py`.

SUBMITTED: [PR #1720](https://github.com/CrocSwap/integer-mult-bounds/pull/1720), head `828a1df15d5f5256f80e61c8d22b822846b76ae7`. It is open; no merge or frontier change is claimed.
