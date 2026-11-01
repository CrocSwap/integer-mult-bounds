# H25 O03 source repair: W1-W4 review archive

This package preserves a completed, independently source-reviewed W1-W4 round. It is a source and review archive, with byte-exact drafts, conditional arguments, proposed controls, failure history, and the sole W4 repair. The review accepted the exact declared local source scopes. No source was installed or adopted; all target executions are **0**, W5 remains **unadmitted**, O03 remains **not qualified**, there is **no measured gain**, and complete physical cost remains **OPEN_NOT_ZERO**.

| Order | Delivered source scope | Start here |
| --- | --- | --- |
| W1 | Conditional byte/framing correctness and provider-dependent auxiliary-space analysis; 50 unexecuted boundary proposals | [Bound/framing argument](archive/w1-bounds/BOUND-FRAMING-REVIEW.md) |
| W2 | Four-region primary-exception hardening draft, failure-state table, exact inverse/preservation evidence, 14 unexecuted proposed controls per normal/-O mode | [Failure-state table](archive/w2-failure/FAILURE-STATE-TABLE.md), [draft source](archive/w2-failure/source-v1/bounded_serialization.py) |
| W3 | Conditional source-route plan, 23-row provider dependency matrix, bounded acquisition proposal and timing interface | [Closure plan](archive/w3-runtime/RUNTIME-CLOSURE-PLAN.md) |
| W4 | Bounded tagged/legacy timing parser/readback v2, grammar, independent literal expectations, T01-T30 with 59 unexecuted variants | [Accepted v2 source](archive/w4-timing/v2/parent_readback_v3_DRAFT_v2.py), [original handoff](archive/w4-timing/HANDOFF.md) |

The [final independent source review](archive/review/FINAL-REVIEW-v1.json) has SHA-256 `a8ecfc1d805e30dff1031f51dc371ea567de962cf4115077dfa55e3e6da8a420`; its [external source-review freeze](archive/review/FINAL-FREEZE-v1.json) has SHA-256 `cee7e0a6891761fe8c1d76f148cf5d78f43f6d0260cb3c0ae9a951fd8b748970`. This is independent AI source review, with no human or proof-kernel acceptance implied.

## W4 rejection and single repair

The [v1 rejection](archive/review/W4-REVIEW-v1.json) and original v1 source/47 variants remain intact. The admitted wall literal `179.990000000000000000000000001` plus `.01` is exactly `180.000000000000000000000000001`, greater than 180. Ambient Decimal precision could round that violation to 180. The [accepted v2 review](archive/review/W4-REVIEW-v2.json) covers the sole repair: an explicit isolated precision-128 context and a conservative 60-aligned-digit arithmetic argument. All 330 v1 payloads and 47 original variant/oracle entries are conserved; 12 new variants yield 59 total. This paragraph describes the reviewed source argument; the parser and variants were never run.

## Reading and checking this archive

`archive/` contains every file in the closed local round, unchanged, including control, review, cost, failed checker, rejected v1 and repaired v2 records. `dependencies/` contains only named source/text inputs needed to inspect that review. [SOURCES.json](SOURCES.json) records public commit provenance and [RELOCATION-MAP-v1.json](RELOCATION-MAP-v1.json) resolves the exact historical absolute/project paths to these copies. The source package needs neither network access nor Git to inspect. It does not include the approximately 17 MB authentic transports or full predecessor packages. Those execution dependencies remain named public pinned references in SOURCES.json; no hidden live workspace access is required to read the supplied source.

The retained JSON, proofs, fixtures, code and absolute paths are historical bytes. Their original commands are not portable replay instructions, and this export makes no claim of fully standalone execution, source-history ancestry, runtime qualification or relocation of executable imports. Normal exported Git modes are 100644. Original modes are recorded; no original payload mode was changed. A source content freeze is not immutable runtime custody.

The sole optional metadata command is:

```sh
python3 -I -S -B research/h25-o03-source-repair-20261101/check_archive.py
```

It parses its own manifest and hashes regular package files only. It never imports, parses, compiles, decodes, launches or tests candidate code or fixtures. [SOURCE-EXPORT-MANIFEST-v1.json](SOURCE-EXPORT-MANIFEST-v1.json) covers all package files except itself; the external publication export freeze anchors the manifest and full transfer tree. No VERIFY.json replay hook is registered, in accordance with the guide's archive-format option. Prior passive-source receipts remain historical evidence, not new executed validation.

## Remaining obligations

W1's 50 bounds controls, W2's 14 controls per mode, and W4's 30 labels/59 variants are proposals, all unexecuted. The original 70 serializer, 39 loader, and 15 consumer cases retain their predecessor status; this source round ran none of them. No current runtime seal, new admission/launcher/termination/controller-completion producer, concrete adopted source profile, or W5 admission exists. Trusted request hashes require an authenticated controller. Timing validity, workload success, termination coverage, resource compliance and complete physical accounting remain separate obligations. [OUTCOME.json](OUTCOME.json) and [ordered next dependencies](archive/integration/NEXT-DEPENDENCIES-v1.json) retain the exact boundaries.

## Open next questions

The structured questions in [TASK.json](TASK.json) identify why each next step matters, its smallest useful first step and its blockers: concrete source/control selection, separately authorized actual-host/provider sealing, then current producer/control integration and fresh W5 admission. This publication grants none of those actions and does not resume the original goal or automations.

## Credit and license

Chris / Clear1nsight; Douglas R. Colkitt and CrocSwap; and the circuit, verification, and source lineage in PRs [6029](https://github.com/CrocSwap/integer-mult-bounds/pull/6029), [6326](https://github.com/CrocSwap/integer-mult-bounds/pull/6326), [6332](https://github.com/CrocSwap/integer-mult-bounds/pull/6332), [6328](https://github.com/CrocSwap/integer-mult-bounds/pull/6328), and [5864](https://github.com/CrocSwap/integer-mult-bounds/pull/5864) retain their credit. The inventory work has a separate scope and supplies no serializer speedup credit. Substantial OpenAI Codex GPT-6.1-sol assistance at max reasoning produced source, analysis, independent AI review, and this export. This is not independent human review or proof-kernel certification. Contributions are Apache-2.0; retained source notices remain unchanged. See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).
