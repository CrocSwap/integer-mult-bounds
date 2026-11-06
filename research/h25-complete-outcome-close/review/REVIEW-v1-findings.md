# Independent source review, first findings

This is a source-only review. No reviewed module was imported or executed, no native owner was acquired, and no tests, compiler, science job, network operation, or publication was run by this reviewer. The reviewer owns only this review directory and has not edited implementation files.

Reviewed source snapshot: `active_complete_close.reviewed-v1.py.txt`, SHA256 `4f299555d97828b791540176311639803b58ca12061e3097e5aecc73737f7a2b`. The implementation was changing during initial reads, so this copied snapshot fixes the findings below. The originally supplied `68a410ec31ab47b7ae57dc6c675a8a59675c65f85714790d1aac8d3fa5f19778` was also observed by SHA256 before the snapshot was copied; this report's line references concern the fixed `4f299...` snapshot.

Reference owner: `outputs/s04-resource-fit-20261106T0200Z/inputs/exact/selected_owner.py.txt`, SHA256 `e94ee23f4f66b16f9d5a0b7f1cc510952d1769247283062d9124737d7838ce3c`.

Reference funding: `outputs/s04-resource-fit-20261106T0200Z/inputs/exact/selected_funding.py.txt`, SHA256 `164468176d2094fbd496eecfd0d0adf3b6ceaf89b2573456509157cc26256677`.

Completed advice: `outputs/s04-complete-close-20261106T0438Z/consultation/RESPONSE-v1-complete.md`, SHA256 `81b702ad20ac0dfcdac0a098b994748c897ffd09c5eafc1997de5b96329d0ea2`.

## Blocking findings at this snapshot

1. **The new complete validator lacks request-to-actual-START correlations.** Lines 176-188 correlate admission with the selected request and independently bind an admission registration pin to START provenance. They never require the request command, policy, reservation, round, and label to equal the actual START fields. The unchanged `active_view` checks the actual snapshot START equals the selected `start`, then assesses the proposed `request` against the predecessor prefix separately. In a registry with another valid adopted policy/command, same-label request B and actual START A can therefore satisfy those two checks independently. A receipt/evidence package can be internally bound to B while carrying A's START hash. Before publication, require exact shared request/START values, correct schemas/round, and `validate_pre_entry_provenance` for that same request. A mutation control must use an otherwise valid alternative request/policy so a generic malformed-request failure does not mask this gap.

2. **The new protected primary slot ignores an established original primary when the private first slot is empty.** Lines 727-732 choose private `record['first']` or the newly caught exception, before consulting the original `first_state[0]`. If original error A already exists and initial `verify` rejects continuation with error B, B is promoted as private primary, whereas unchanged `fail` would preserve authenticated A. Preserve the established original primary under the captured error-container integrity contract before any optional recorder call. Do not claim universal allocation-safe capture; the review is limited to new bookkeeping after catch.

3. **Release can miss complete-branch error custody when first verification fails before consumption.** At lines 750-753, `verify` may fail before `complete_used=True`; `complete_failure` still records the exception. Lines 1063-1068 then route a later cleanup error through protected handling only if `complete_used` is true. Otherwise an existing private primary causes that cleanup secondary to be discarded by the legacy branch. Select complete release handling from the privately selected complete branch, or from that branch's protected-error state, while preserving legacy behavior when no complete closure is selected. Preserve the once-only lease-close boundary if helper bookkeeping changes the `CLOSE_UNKNOWN` phase.

These findings were sent immediately to the implementation owner. They require review of a new exact source hash before source-only acceptance.

## Supported source properties and boundaries

- The optional branch preserves the legacy six-field STOP/UNKNOWN method body and the ten-method `Context` set. `exact` and `digest` are included in captured funding function identities at this snapshot.
- The branch keeps the closer's original manual request/provenance separately, uses the closer's reservation for its local protocol-window check, and checks a selected clock lineage for target-terminal-before-closer ordering. That local sample does not measure startup, release, or final exit.
- Evidence acceptance remains an explicit authenticated source-private parent premise. Pinned JSON, a review decision, hashes, and raw-manifest entries are consistency data and do not authenticate native outcomes. The source does not reread large raw inventories; complete custody and genuine independent acceptance remain external obligations.
- The receipt projection omits only `independent_outcome_review_sha256`, avoiding a receipt/review digest cycle. The original final receipt bytes are passed unchanged to publication.
- The complete validator constructs receipt, registry, and next-HEAD images and checks registry/append semantics, generation capacity, and metadata limits before the first receipt publication. It reuses the selected original publication and advancement functions, and compares durable readback against precomputed bytes. Post-write IO or allocation failures remain uncertain evidence; there is no rollback or repair.
- Resource-invalid PASS and known STOP must retain their actual observed cost and RSS values. This snapshot correctly leaves them recordable without a fit grant; unchanged funding assessment adds reservation/RSS blockers on later admission. Rejecting all such PASS receipts would prevent truthful accounting.
- There is no G clearing or grant. Successful return keeps costs unsettled and native/execution capabilities false. Closing the target does not settle the closer's enclosing operation.
- No genuine bootstrap/caller adoption was supplied or reviewed. The copied owner extension is not proof that an authenticated caller loads it, that owner/loader/detached manifests name the new source, or that authentic accepted target evidence exists. Those bindings must be explicit before connected runtime adoption can be accepted.

## Test-plan assessment

The owner's proposed AST extraction of the whole actual pure validator, new complete method/helper, and actual dispatch/release methods into inert ports is appropriate for source-only behavioral evidence. No native execution is needed for those checks. Required additions are the three findings' exact counterexamples, including original A with private first empty, initial verification failure before consumption, cleanup B, and optional recorder C. Both smaller and larger own-versus-target reservation controls are needed.

To claim failures at each registry publication, HEAD-history publication, HEAD replacement, and durable readback phase, run the actual unchanged `advance` source with inert ports; similarly use actual `publish` with inert native ports if claiming its individual internal write/link/readback phases. A single failing stub for `advance` or `publish` supports only failure at that exposed call boundary. Preserve that distinction in result labels.

Current verdict: **CHANGES REQUIRED for the exact reviewed source; GO to build a bounded inert source harness after repairs.** No native ownership, complete original activity, resource fit, scientific acceptance, S04 completion, publication, or runtime adoption is accepted by this report.
