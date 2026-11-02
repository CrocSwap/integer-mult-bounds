# G12 acquisition and raw-error delivery boundary

**Conditional source finding; original P07/N22 qualification remains open.**

This package follows the explicitly assigned [PR6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321) P07/G12 investigation, unpaidmoon's [PR6339](https://github.com/CrocSwap/integer-mult-bounds/pull/6339), and the independent partial repairs in [PR6346](https://github.com/CrocSwap/integer-mult-bounds/pull/6346). A completed ChatGPT Pro consultation proposed bounded preallocation and identified acquisition and interpreter-delivery gaps. The current contribution independently checks the decisive upstream CPython 3.12.3 source paths and preserves three finite witnesses.

[CLAIM.md](CLAIM.md) gives the complete argument, assumptions, counterexamples and explicit next gate. It distinguishes complete resource registration, delivery of raw errors, retention in a journal, and outward primary identity. An acquisition conversion failure is not a generic Python impossibility result; losing an undelivered raw error also requires an explicit contract interpretation. Preallocated capacity alone does not establish these distinct guarantees.

## Evidence and reproduction

- [SOURCE-EXCERPTS.json](SOURCE-EXCERPTS.json) contains 19 unchanged source windows from 11 immutable external files, with exact full-file and window hashes, line ranges and direct URLs. Ten files are from CPython `f6650f9ad73359051f3e558c2431a109bc016664`; the other is the fixed PR6339 parent. Complete external texts were fetched and inspected locally. CI verifies the retained window bytes, not an external download or the target executable's provenance.
- [verify.py](verify.py) checks the excerpt records, fixed canonical contract inputs and **13 finite transition cases**. The cases are a small explicit abstraction of the cited C paths. They are not C execution, interpreter fault injection, a proof kernel, target regression results, or an exhaustive interpreter audit. A passing witness check confirms the stated failure remains represented; it does not make the stronger contract pass.
- [SOURCES.json](SOURCES.json) and [VERIFY.json](VERIFY.json) preserve the current catalogue/selection provenance and declare all three used canonical contract inputs for invalidation.
- [VALIDATION.json](VALIDATION.json) records the actual local normal/optimized results.

Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/h25-g12-interpreter-boundary --check-only
python3 scripts/research_package.py --package research/h25-g12-interpreter-boundary
```

Expected per-mode line:

```text
PASS_G12_INTERPRETER_BOUNDARY transition_cases=13 source_windows=19 target_runtime_qualified=false original_acceptance=false
```

There is no target import, real descriptor/process operation, native build, original H25 run, provider acquisition, historical budget transfer or performance measurement. The selected source, launch/handoff `None`, original 52 helper IDs, original 49 activities and 24 components, CP01-CP15 and all18 branch obligations are unchanged. Unknown costs remain OPEN_NOT_ZERO. This finding does not award original helper credit or close O03.

## Open next questions

Structured questions are in [TASK.json](TASK.json).

1. Establish the actual pinned target implementation and the precise original raw-error observer boundary. Then enumerate and discharge the remaining frame/traceback/handler/call-entry sites. The current source argument is conditional on implementation correspondence and the stated fault model.
2. Prove a faithful acquisition-owner primitive or private-descriptor-table recovery alternative. Treat failed return conversion and failed post-return registration separately. No new acquisition protocol is implemented here.
3. Only after those gates, compose a bounded journal into the original exceptional contexts and the full parent/consumer/authority/driver graph. A new runtime assurance or weaker outward-error contract must be explicit, independently reviewed and cannot be labelled ORIGINAL acceptance.

## Credit and licenses

Chris R / Clear1nsight, with substantial OpenAI Codex source analysis/verification and ChatGPT Pro consultation assistance. Preserve unpaidmoon's PR6339 credit with substantial Cursor Grok assistance, PR6321/6029 contributors, Douglas R. Colkitt and the retained circuit/network/native/verification lineage. AI agreement is not independent human or proof-kernel acceptance.

New analysis and finite model: Apache-2.0. CPython excerpts are unchanged and retain the Python Software Foundation and predecessor notices in [LICENSE-CPYTHON.txt](LICENSE-CPYTHON.txt), copied exactly from the pinned CPython LICENSE. CPython is not relicensed under Apache-2.0. PR6339 source excerpts retain the repository's existing Apache-2.0 attribution.
