# Retain the group leader until the final numeric signal

This source audit identifies a concrete retirement-order defect in the common runner selected by [PR #6864](https://github.com/CrocSwap/integer-mult-bounds/pull/6864), at `c8f7bd582ffc1301b851dde2364c60f1636aac8b`. The runner can reap its direct child and then call `killpg` with the child's old number. If the number is reused while the runner is descheduled, the final signal can target an unrelated process group.

The result is a source-level counterexample under the selected Linux v6.12 model. No project code, control, kernel probe, native operation or scientific workload was executed. The proposed correction is recorded for implementation; it is not installed or qualified by this package.

- [Counterexample and its precise premises](COUNTEREXAMPLE.md)
- [Connected repair and decisive acceptance checks](REPAIR-PLAN.md)
- [Complete Pro construction, with proposed code clearly unexecuted](PRO-CONSTRUCTION.md)
- [Assessment and claim boundaries](ASSESSMENT.json)
- [Immutable external references and exact source hashes](SOURCES.json)
- [Bounded upstream search and reuse decisions](SEARCH-COVERAGE.json)
- [Exact affected runner snapshot](run_guarded_v3.py.txt)

The original investigation is [PR #6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321); its [maintained plain-English handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/6321#issuecomment-6713710045) explains the wider verification goal. This finding preserves #6864's factory/cwd corrections, #6863's timer/error correction and the original scientific bodies. It does not change the selected mathematical frontier or supply a speedup.

## Source and reproduction boundary

`MANIFEST.json` binds every other package file by raw UTF-8 byte count, SHA256 and Git blob identity. The runner snapshot is inert text and equals the published affected file. External inputs remain at explicit immutable GitHub URLs in `SOURCES.json`; they are intentionally not asserted to be ancestors of this publication. Read the referenced line ranges to audit the argument. No network-free full source history or executable replay is claimed.

This package has no registered replay hook. Hosted planning or onboarding, if successful, verifies repository integration only; skipped replay does not test the proposed correction. No regression passes, environment eligibility, full helper/context coverage, successful comparison, numerical resource fit or final retention result is claimed. Recorded execution allowance is unchanged; complete outside and physical costs remain `OPEN_NOT_ZERO`.

## Open next questions

Implement one connected common-runner successor using non-consuming terminal observation, final signalling before reaping, and explicit first/cleanup-error custody. Update the actual caller's runner pin, both source recipes and detached bindings in that same revision. Adapt the earlier runner's wait-state discipline rather than adding another disconnected helper. Run the new discriminators listed in [REPAIR-PLAN.md](REPAIR-PLAN.md) under an admitted bounded operation and obtain exact-source review. The current implementation round stopped dispatch at its thirty-minute reassessment; no new execution or research window is granted here.

Complete scientific dependency coverage, genuine predecessor-baseline adoption through the same common parent, successful retention/CLOSE, current runtime issuance and complete comparison funding remain separate obligations. Their resolution cannot be inferred from this counterexample or from publication.

Tekalign, with substantial OpenAI Codex and ChatGPT Pro assistance. Apache-2.0 for new contribution text and code; predecessor and external sources retain their notices. See [NOTICE.md](NOTICE.md).
