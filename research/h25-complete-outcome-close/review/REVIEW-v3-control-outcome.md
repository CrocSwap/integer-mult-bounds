# Independent finite-control outcome addendum

At 2026-11-06 05:14 UTC, the reviewer read the two parent-produced bounded control outputs, GNU time records, empty stderr files, and selected `execution/LEDGER-002.json`. The reviewer did not execute either command. This addendum preserves and supplements `REVIEW-v2-final-source.md` and the earlier rejected evidence.

**Verdict: ACCEPT_SOURCE_COMPONENT_AND_FINITE_CONTROLS_ONLY.** The owning successor remains SHA256 `9b4ddb537e46e0f7f5f09cab10e32cc9f8d1a6472b8612757b1da04a7155b380`; the reviewed harness remains SHA256 `81ef02f0f8cb2b45fb03f6cbf2fee462a8b021602b2031699d3a31116cc5b25f`. Current bytes were rehashed after execution and remain unchanged from source review. Both output records identify the same selected successor and unchanged funding source hashes.

The normal and optimized reports each list the same **41 distinct defined checks: 40 finite behavioral controls and one static compatibility check**. Both report all 41 passed. This is 41 checks exercised in two modes, not 82 independent checks. The checks use the whole extracted validator and changed method/helper bodies, actual unchanged `advance`, and inert ports as detailed in the source report. The parent reports one execution per mode and no retry; the two supplied command records correspond to the normal invocation and its `-O` variant.

| Supplied record | Normal | Optimized |
|---|---:|---:|
| Passed checks | 41 | 41 |
| Exit status | 0 | 0 |
| Stderr bytes | 0 | 0 |
| GNU time wall interval | 0.50 s | 0.40 s |
| GNU time user / system | 0.45 / 0.02 s | 0.39 / 0.01 s |
| GNU time maximum resident set | 29340 kB | 29356 kB |

These observations concern only the two bounded finite-control invocations. They are not measurements of a full scientific invocation, original command/profile fit, aggregate target RSS, native ownership, or complete physical costs.

Reviewed output SHA256 values:

- `execution/normal-v1.stdout.json`: `36f05c75b1a82e1a6518b99ad72fd69c72a3dca52f72d2f316f285facc83fa52`
- `execution/optimized-v1.stdout.json`: `8b528424889c825e1e5622907e7363059b3c002e6cb055a2a1b1d087d8cc06ba`
- `execution/normal-v1.time.txt`: `33746e69d269b74fc342722aa573d52f20003710e34330b57cdc20ba896e8a7f`
- `execution/optimized-v1.time.txt`: `51c07b73033912f7c49ba679ad9fd910c5f8e38f52dc3b0795bd3f79274fe2eb`
- `execution/LEDGER-002.json`: `6224f7078f7b1eaa24c0db226fe380e0d67bdacc77e1766e9381fac38e731410`

The selected ledger's arithmetic is consistent: reported prior recorded scope `1354.890533479` seconds plus the new conservative policy debit `54` seconds equals `1408.890533479` seconds; subtracting that from `2400` gives `991.109466521` seconds. The record states two completed attempts, no active batch, no outstanding reservation, no refunds, no new budget, and original-activity credit delta zero. This review checks that selected record and its arithmetic; it does not re-audit the prior ledger's complete custody or historical baseline. Physical costs and preparation, Pro, review, reporting, publication, final metadata, and historical costs remain `OPEN_NOT_ZERO` exactly as retained by the supplied record.

No remaining blocking defect was found in the bounded reviewed extension after repairs and these finite controls. Coverage remains limited: the harness does not execute complete bind/acquisition validation, real `active_view`, native EX, authentic whole-body/custody evidence, current runtime/profile admission, or complete downstream funding eligibility. Its publication fault injection covers the exposed receipt/registry/history/HEAD/readback boundaries of actual `advance`; it does not execute internal filesystem writes, links, fsyncs, descriptor cleanup, or crash behavior inside actual `publish`.

**Connected caller/source adoption remains unaccepted.** Genuine authenticated bootstrap selection, owner/loader and detached source-manifest bindings for the new closer hash, authentic target evidence production/acceptance, full original workload receiver/schedule, closer accounting and later original admission checks remain outstanding. This is a completed bounded source component plus finite-control assessment, with original activity credit zero. It is not S04.03/S04.04/S04.05 completion, scientific acceptance, native/runtime qualification, or publication approval. No further research execution or unchanged rerun is requested by this addendum.
