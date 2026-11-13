# Repair the authenticated caller factory and native launch directory

The connected caller published in [PR #6863](https://github.com/CrocSwap/integer-mult-bounds/pull/6863) has two production source mismatches. Its environment-association factory authenticates the unsuffixed loader location while the selected loader is under `repair-v3`. After that is corrected, the waiting entry launches its native child with the stage directory as cwd, while the unchanged native entry requires the original historical directory passed through `--read-root`.

This contribution implements one immutable connected successor. Source preparation selects the exact new association root, preserves the strict identity and calling-frame checks, and changes the existing `Popen` cwd to `READ_ROOT`. It carries those changes through both stage-entry copies, stage and queue pins, source packet and detached manifest. The scientific bodies, native/compiler implementations, original independent oracles and historical controls remain intact.

Original investigation: [#6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321). [Maintained end-goal specification and contributor handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/6321#issuecomment-6713710045). Immediate predecessor: #6863 at `c009a7514790e865b664ab8cd4688d37787d7eaa`. Conditional native/compiler source argument: [#6830](https://github.com/CrocSwap/integer-mult-bounds/pull/6830) at `39fcd67c991bd72918080b1d2c02feb3d679206d`.

## What changed

- Replace the unique expected module-level association-root assignment structurally during preparation. Accept exactly the selected root; do not accept both locations or infer authority from an arbitrary loaded module.
- Keep the original historical cwd at the actual native launch, matching the native `getcwd` guard and the predecessor runner. Preserve all native argv fields and other launch arguments.
- Rebase every exact selected predecessor-root spelling before rebuilding dependent metadata. This includes the leading-slash string form omitted by the earlier repair. Original scientific stage members are never text-rebased.
- Freeze the corrected leaves before their dependent stage/queue/packet/manifest pins. Create no runtime role records, native images, grants, STARTs or currentness receipts.

`SOURCE-MAP.json` maps every selected source and profile to an inert UTF-8 body. The selected graph contains 61 source roles, seven profiles and 44 unchanged historical control references. Role aliases share one file identity. The original complete stage maps remain supplied, but unchanged scientific stage members and the historical control bodies stay at their exact predecessor references rather than being duplicated here.

The paths in those source records identify the actual inspected local subject. This is an inspectable source archive, not a portable executable installation or a claim that the current host qualifies. No archived `.txt` source is imported by the integrity checker.

## Validation actually performed

Five new tests passed in normal mode and the same five passed with `-O`, once each. Their retained unittest durations are 0.490 and 0.504 seconds. They ran within one clean-environment operation with a 20-second outer timeout, two-second termination tail, 256 MiB address-space cap and fixed file-size limits. The operation incurred a conservative 26-policy-second debit; preparation, Pro assistance, review, publication, final metadata and historical physical costs remain unknown rather than zero. These are fixture measurements, not a speedup.

The tests:

1. Reproduce the frozen predecessor's actual factory rejection.
2. Use the actual private loader, loaded association module, `associate_environment`, `open_parent`, authentication and calling-frame checks to reach the mandatory missing-selection boundary in the successor. Deliberately absent genuine selection stops before constructing an association or native-I/O context.
3. Reject eight source-transport fixture variants: wrong path/name, unenrolled bundle, wrong role/PID, missing module, replaced function and a direct external call. Fixture retention is not genuine runtime enrolment.
4. Execute the complete production `native_argv` body and the actual `Popen` expression with labelled inert read/launch ports. The predecessor's cwd differs from argv[10]; the successor's cwd equals the historical read root. No process is launched. This is a source projection, not execution of the complete waiting-entry main.
5. Verify the changed source/stage/queue joins in both modes and retain every other original stage member byte.

Old successful timer and process suites were not rerun. Their applicable controls remain predecessor evidence. The native/compiler/scientific implementations were not compiled or executed. No genuine financial context, guardian, property observer, scientific workload or current environment was exercised.

The executed control argv and output are retained in `evidence/source-controls.stdout`, `.stderr` and `.time`; the test and two-mode driver are in `validation/`. Running them requires the exact frozen predecessor/successor local inputs recorded by their sources. The archive itself does not promise a clean-checkout runtime replay.

The passive reproduction command is:

```sh
python3 -I -S -B verify_integrity.py
```

It checks this archive's ordinary-file inventory, exact bytes and selected source/profile mappings only. It does not decode an archive, import candidate code or run the scientific comparison. No scientific `VERIFY.json` hook is registered. Hosted planning and skipped replay will be reported at their actual scope.

## Remaining acceptance conditions

The two repaired interfaces do not complete the original whole source-binding criterion. In particular, the changed process-group relation (`start_new_session=False` in the waiting entry versus `True` in the earlier runner) still needs its supervisory preservation argument. It was deliberately not changed without that proof.

The genuine primary-baseline transfer and complete typed comparison remain to be connected using [#6837](https://github.com/CrocSwap/integer-mult-bounds/pull/6837) and [#6847](https://github.com/CrocSwap/integer-mult-bounds/pull/6847). Automatic retention's presence does not adopt the successful complete-outcome CLOSE owner from [#6762](https://github.com/CrocSwap/integer-mult-bounds/pull/6762); its predecessor is [#6736](https://github.com/CrocSwap/integer-mult-bounds/pull/6736). Actual source/image/configuration, runtime ownership, complete control coverage, resource fit, funding, full equality and measured performance remain separate.

The original conditional native proof retains its explicit Linux, security, filesystem and toolchain premises. This repair supplies no model extension, host change or execution authority.

## Credit

Chris R / Clear1nsight and the original CrocSwap contributors, with substantial OpenAI Codex and ChatGPT Pro assistance. Pro independently diagnosed the two public-source defects and constructed the repair obligations; Codex implemented the successor, source inverse and bounded controls. The copied Pro response is retained as AI construction evidence, not independent human or proof-kernel acceptance. Original source headers, predecessor credit and source-specific licences remain intact.

## Open next questions

Review the process-group transfer on the exact common-runner/waiting-entry/guardian paths and original group-sensitive consumers. Then reconcile the complete baseline/comparison and successful CLOSE bindings in the actual caller. Start with this readable source map and the predecessor references; do not replace missing genuine inputs with synthetic success records. Preserve original criteria and all failed evidence.
