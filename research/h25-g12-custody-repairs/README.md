# H25 G12 custody repairs and retained allocation counterexamples

**Bounded source repair. Full P07/N22 integration remains open. No H25 execution or gain.**

This is the explicitly assigned source follow-up to [PR6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321) and unpaidmoon's [PR6339](https://github.com/CrocSwap/integer-mult-bounds/pull/6339), frozen at `608ad23adc6c01264c8195daf7f18e29c17464a7`. It implements the three narrow repairs proposed by a ChatGPT Pro source consultation, adds executable source-function failure controls, and preserves the counterexamples that prevent a full-source acceptance claim.

## Result and exact scope

The corrected parent and consumer are new **unselected** successors. Their bytes are the consultation's reviewed proposal, now under v3 filenames. The predecessor's internal v2 description remains unchanged so the proposal hashes are preserved. Frozen H25 sources and PR6339 are not edited.

- Seven raw-error ledgers are allocated before their function acquires new resources. A failure of that initial allocation therefore cannot strand those subsequently acquired resources or replace a previously caught local body error.
- P09 has an independent final release phase for recorded pidfds after its last process-disposal attempt. Persistent observation denial no longer bypasses the known release loop when snapshotting and error recording succeed. Numeric ownership is removed before close to avoid a blind retry after an ambiguous outcome. Failed or unknown cleanup stays unknown.
- The consumer requires an exact nonnegative integer `publication_size`, rejecting equal-valued floats, booleans and foreign integer subclasses.

These are **conditional local repairs**, not a complete allocation-failure solution. `_close_known_descriptors` still allocates its ledger and snapshot while a primary can be pending; recording a close error can also fail. The verifier deliberately reproduces all three retained counterexamples. Acquisition-to-registration gaps and later raw-journal allocation remain open. Hoisting a ledger adds successful-path allocation and memory cost; no improvement or unchanged allocation availability is claimed.

The tuple-to-dictionary conversion inherited from PR6339 remains intact. Both original exports, source/oracle checks and original producer are retained. Launch/handoff remain `None`. The old candidate authority/transport/mount graph is not silently selected or claimed adopted.

## Reproduce

Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/h25-g12-custody-repairs --check-only
python3 scripts/research_package.py --package research/h25-g12-custody-repairs
```

The registered hook runs normal and optimized modes. Direct commands:

```sh
python3 -I -W error -B research/h25-g12-custody-repairs/verify.py
python3 -I -O -W error -B research/h25-g12-custody-repairs/verify.py
```

Expected final line:

```text
PASS_G12_BOUNDED_SOURCE_REPAIRS source_cases=41 metadata_checks=94 unresolved_preflight_allocation=3 no_integrated_acceptance
```

There are 41 source-function/window cases, including **three expected refutations of the stronger cleanup contract**, and 94 separate byte/AST/diff checks. These counts do not replace the original 52 helper bodies, add accepted N22/P07 body credit or certify all18 G12 branches.

The verifier executes explicitly named **AST-extracted source functions/windows** with synthetic descriptor/process tokens. It does not import the full parent/consumer modules, invoke the H25 parent or original scientific CLI, call real close/signal/process operations, acquire a provider, compile native code or replay the author's old verifier. The original guarded/scientific budget is not used.

## Evidence and source availability

- [SOURCE-IDENTITIES.json](SOURCE-IDENTITIES.json): exact retained PR6339 bytes and corrected-source hashes, external commit and proposal provenance.
- [repairs-from-pr6339.patch](repairs-from-pr6339.patch): the complete146-line proposal diff. Verification applies it **in memory** to the retained v2 texts and compares every byte with v3.
- [verify.py](verify.py): normal/optimized source-function controls, negative predecessors, exact source deltas, closed selections and preserved unresolved witnesses.
- [review/PRO-SOURCE-REVIEW.txt](review/PRO-SOURCE-REVIEW.txt): the detailed prior AI source review, all18 branch categories, CP01-CP15 reasoning, source pins, counterexamples and unreviewed obligations.
- [review/PRO-COMPOSED-REVIEW.json](review/PRO-COMPOSED-REVIEW.json): a distinct consultation agent's bounded review of the exact composed draft. This is agent evidence, not human or proof-kernel acceptance.
- [VALIDATION.json](VALIDATION.json): actual local execution record and limits.

The two PR6339 source inputs are retained as inert text because that commit is not an ancestor of canonical main. No private Git object cache or fetch of an unmerged commit is needed by the verifier. The external head is explicit provenance, not an ancestry claim. [SOURCES.json](SOURCES.json) and [VERIFY.json](VERIFY.json) declare all84 consulted archive files as live byte-bound inputs for CI invalidation, plus the fixed canonical catalogue/selected-result provenance. Hashing those inputs is not re-execution or semantic acceptance of them.

The common frozen baseline remains PR6029. PR6316/6317 are independent usable log/archive packages, not dependencies. P02 is a separate lane. Source counts, complete adoption, actual execution, full-caller qualification, measured wall/CPU costs and kappa/frontier changes remain distinct.

## Why this does not close P07/G12

A successful one-yield P07 local continuation checks the observed remainder after the same original CLI and validates its final `StopIteration.value`. Its intentional completion marker bypasses the normal driver's later full-native/full-anchor/late-last completion. Do not remove that marker as an assumed repair or count the local control as full caller qualification.

The remaining source gate needs exception-safe acquisition/registration, a raw first-primary/secondary journal robust under the original failure model, complete nested-schema/alias review and an explicit parent/consumer/authority/driver pin-and-mount derivation. The source review's category matrix is coverage of questions, not acceptance of every predicate.

Original C01-C15 costs, including added recorder allocation, retained traceback graphs, both exports, failed cleanup and final tails, remain required. Unknown physical/final costs are **OPEN_NOT_ZERO**; historical allowances are nontransferable. The original scope clarification does not require building a new generic enclosing accounting API.

## Open next questions

Structured questions and blockers are in [TASK.json](TASK.json).

1. Can a finite preallocated ownership/raw-error journal meet the original allocation-failure contract without an additional interpreter or atomic-acquisition guarantee? First prove the exact failure boundary and acquisition-to-registration rule. A generic Python impossibility claim is not established by the current counterexamples.
2. After that gate, freeze and independently review the complete corrected source/mount/pin derivation for both N22 and P07. Genuine runtime/custody/admission remains a separate blocker, not a fabricated fixture.
3. Under separate future authorization, qualify the actual full caller and all original controls/costs. Nothing in this package authorizes an H25 replay or transfers historical budget.

## Credit and license

Chris R / Clear1nsight, with substantial OpenAI Codex implementation/verification assistance and ChatGPT Pro consultation assistance. The exact predecessor repairs and their attribution are retained from unpaidmoon with substantial Cursor Grok assistance (PR6339). Credit PR6321, PR6029, retained source/review contributors, Douglas R. Colkitt and the original circuit/network/native/verification lineage. Apache-2.0.

The consultation's AI reviewers and the present checks do not establish independent human or formal proof-kernel acceptance.
