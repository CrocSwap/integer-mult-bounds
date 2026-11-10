# Descriptor-relative C05 namespace observations

This implements a bounded namespace-classification primitive using real Linux filesystem operations. It replaces supplied object-kind/absence facts with the observer's own no-follow component lookups and held descriptors. The two Pro-authored files are unchanged from the completed consultation; independent Codex controls add descriptor-closure probes, a real lookup-error/quarantine control, the exact component-bound positive and two temporal counterexamples.

This is a **partial C05 prerequisite**. It emits no ordinary `source_files` row, reads no regular payload, and neither resolves the compiler's search chain nor proves that a later compilation used the observed namespace. `full_c05`, `full_v03` and `runtime_qualified` remain false in this package's disposition. The observer's diagnostic projection has its own explicit false flags. Original admission selections and source contracts are untouched.

## Exact contract and argument

Construct and retain `NamespaceObservation(path)` before calling `observe()`. The path must be an exact canonical absolute ASCII string, at most 4,096 characters and 64 components. These are local restrictions of this partial interface; unsupported original C05 spellings remain open. `observe()` returns `None`; raw stat/exception/ownership state stays on the pre-existing owner. After a successful observation, `project()` produces diagnostic data rather than a capability, durable artifact, content certificate or original Root acceptance.

The walk starts from a real process-root descriptor. Every subsequent operation receives one basename and an actually held parent descriptor. No intermediate symlink is hidden in a multi-component lookup. A reached symlink is classified without following it; an unresolved suffix receives no invented observations. Missing means that the particular no-follow stat call delivered exact `FileNotFoundError`/`ENOENT` under the held parent. Other errors retain their identity and terminate the operation. An `O_PATH` reference is used instead of an ordinary read-open, so classification of a FIFO does not wait for a writer.

For present objects, raw lookup and descriptor metadata are retained before the local equality guard. Equality is an acquisition-consistency check, not a proof against ABA or inode reuse. Late metadata is another observation of the held object, not another absolute path walk. Under the stated dispatch, delivery and noninterference premises, a successfully completed absence observation establishes a genuine single-component ENOENT observation and successful close returns for all known delivered descriptors. It establishes neither complete witness selection nor compile-interval stability.

The component distinguishes regular-content-unread, directory-membership-unenumerated, unresolved symlink, unsupported special file, nondirectory prefix, and absence-at-pinned-parent outcomes. `DONE` means that the observation operation completed; it does not mean C05 accepts the route. The original integer range used by `_vplain` is preserved in the metadata projection, but that alone does not establish complete parent encoding/record fit.

## Ownership, failure and explicit premises

Every raw result, error and FD slot is allocated before acquisition. A delivered FD first enters its ownership slot. Known ownership is consumed before one reverse-order close attempt; no possibly recycled descriptor is retried after a close error. Body, open, close and projection failures root their primary and relevant raw errors. An admitted-operation/projection failure poisons future acquisition in this module; precondition refusals before admission do not constitute a completed native failure.

The module-local active-owner check is **not a thread lock**. This partial contract requires serialized, nonreentrant ordinary calls, authenticated unchanged native dispatch, protected singleton state and no interfering audit hooks, signals, tracing or private-state mutation. These are explicit caller obligations, not newly accepted original C05 premises. Reloading or modifying private module state is not an authenticated reset. Original Root/owner propagation, audit behavior and import/dispatch authenticity remain unqualified.

An open error leaves `pending_open=True`. An undelivered descriptor cannot be recovered or declared released merely from that state; the enclosing process/owner disposition remains open. Raw retention is in memory. It does not satisfy durable raw-before-oracle acceptance. Adverse open-return boxing, EACCES, close-failure combinations, asynchronous delivery and concurrent calls have not been executed as original or new native qualification controls here. No blanket allocation-equivalence or financial-accounting theorem is added.

The [Linux open manual](https://man7.org/linux/man-pages/man2/open.2.html) supports the documented O_PATH/no-follow mechanism; the [close manual](https://man7.org/linux/man-pages/man2/close.2.html) explains the recycled-descriptor retry hazard. The [stat manual](https://man7.org/linux/man-pages/man2/stat.2.html) also cautions that returned fields need not form an atomic concurrent snapshot. These are mechanism references, not source correspondence for an admitted interpreter/kernel/toolchain build.

## Controls and reproduction

Python 3.12 on Linux with O_PATH support:

```sh
python3 -B scripts/research_package.py --package research/h25-c05-namespace-observer --check-only
python3 -B scripts/research_package.py --package research/h25-c05-namespace-observer
python3 -B scripts/check_research_commit.py --package research/h25-c05-namespace-observer
```

The registered normal/optimized commands run only this new module and fresh owned `/tmp` fixtures. `run_controls.py` supplies the isolated import path and checks exact returned-source hashes. No archived module, original Root/provider/helper/producer, compiler, subprocess or historical scientific workload is launched by either suite. Fixtures are retained on success and failure; the harness prints their roots. See `VALIDATION.json` for actual execution status; the commands above are not themselves evidence of success.

Actual local registered execution passed in both profiles on Python 3.12.3. Each profile completed the two Pro-proposed test methods and the independent suite's 18 observation scenarios, 14 input refusals, 133 closed-descriptor EBADF probes, one real ENAMETOOLONG/quarantine control and two temporal counterexamples. The independent suite made 526 internal checks; these are not 526 independent control families or original activities. No functional source repair was needed. Adverse close/open-return delivery, concurrent callers and original Root/runtime integration remain unexecuted.

Pro's proposed suite checks regular/empty files, absent components, nondirectory prefixes, final/intermediate/dangling symlinks, FIFO, directory/regular PCH possibilities, hardlinks, input refusals and outcome ABA. Independent controls use fixture metadata captured before candidate observation, verify actual EBADF for every known closed descriptor, reach exactly 64 components/65 held descriptors, and exercise a real ENAMETOOLONG lookup. That error must not become absence; later acquisition/projection must rethrow the identical retained primary without acquisition or a private reset. A separate real-OS ancestor-rename counterexample shows that a held directory can differ from its old absolute spelling. This does not inject a race into an original Root or simulate a native failure.

Outcome ABA compares absence/presence/absence; it does not claim equality of all metadata endpoints. The ancestor counterexample and the source argument expressly prevent promotion to an absolute snapshot or interval lease. Requested paths remain separate obligations even for hardlinks with matching inode/device observations.

## Resources and scope

For k <= 64 components, source loop bounds are <= k+1 open invocations, k no-follow stat invocations, 2(k+1) fstat invocations and k+1 close attempts: <= 5k+4 = 324 Python-level primitive invocations, <= 65 simultaneously held descriptors, and <= 3k+2 = 194 successful metadata objects. Regular payload bytes read are zero. These are local invocation/retention bounds, **not kernel syscall, wall-time or complete-cost bounds**; metadata operations can block. Total queries, projection/serialization, genuine custody and original source authentication still need accounting.

Original C05 remains the complete independently approved project/system-header/include-search/macro/compiler/specs/linker/library witness closure, with 1..512 source rows, <=64 MiB/file and <=256 MiB per capture. Absence is not a zero-byte file; a proposed canonical witness artifact would still need genuine construction, exact command/role/profile/context binding, currentness, custody and complete charged representation. No such representation is silently adopted here.

## Provenance and overlap

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Immediate predecessor [PR6354](https://github.com/CrocSwap/integer-mult-bounds/pull/6354), head `b3771dbc5f713ba3e90170c1dc3321e653222c65`, constructs roots and a conditional certificate over supplied lookup facts. This package adds actual namespace operations; it neither copies nor executes the predecessor. [PR6352](https://github.com/CrocSwap/integer-mult-bounds/pull/6352) supplies prior V03 source findings; [PR6351](https://github.com/CrocSwap/integer-mult-bounds/pull/6351) clarifies G12 scope. Their unmerged code is not an executable dependency. The newly available cold-helper source remains at its exact public predecessor pin; no helper body is imported or run here.

`SOURCE-ORIGIN.json` records the exact delivered code identities. Pro reported grammar/source review, with no execution; Codex independently assessed and controls the actual checks. Original 43.5% weighted activity completion, stage 2/10, milestone 1/10 and the 24-component denominator remain unchanged. Whole C05/V03/O03, source adoption, performance and kappa are not claimed. Physical, preparation, review, reporting, publication and final metadata costs remain OPEN_NOT_ZERO.

## Open next questions

Bind installed configured compiler/toolchain rules and actual inherited caller context, derive the complete search/expansion domain, and implement alias/content/PCH handling with genuine original Root, writer and compile-interval currentness integration. Prove whole-domain witness representation and fit under the unchanged limits. The first useful step is an exact source-bound rule/context adapter for the pinned original executable; its source/build correspondence is still missing. The original stopped V03 round remains closed. See `TASK.json` for structured questions.

Chris R / Clear1nsight with substantial ChatGPT Pro construction/reported AI source-review and OpenAI Codex independent assessment/control/publication assistance. Retain PR6321/6029/5864 source/reviewer lineage, unpaidmoon/Cursor Grok PR6339, and Douglas R. Colkitt's circuit/network/native/verification attribution. New code/analysis is Apache-2.0. AI review and finite checks are not human or proof-kernel acceptance.
