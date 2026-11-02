# Raw pilot capture failure accounting and finite fake-only controls

This prerequisite package retains a frozen controller repair that keeps the first capture error through later cleanup and accounting failures, together with independent source reviews and the actual NEW synthetic-control receipts. The 24-method fake-only suite passed once normally and once with optimized Python. The contribution is the synchronous failure-accounting repair and finite evidence; original C05/V03 qualification remains open.

The exact retained source base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, tree `e6898c8ba7a27b71587c32ba3f639259ceeeed91`. The local publication repository preserves that full parent index/tree and adds only this directory. Its Git objects come from a local alternate cache with the known unrelated missing base PDF blob `f0d42d430159f3f46dcf447ecb5df8aa9355e208`; this is not a complete scientific-history claim, clone repair or requalification.

## Concrete source change and retained rejection

The initial v2 controller was independently rejected for three connected defects. Its exact source, protocol, source freeze, harness and rejected review remain inert under `archive/rejected-v2/` and `reviews/source/`. The sole bounded successor v3 is retained byte-for-byte under `source/v3/`; no code or path translation was applied.

| Defect retained in the initial review | Frozen v3 mechanism | Finite evidence boundary |
|---|---|---|
| Secondary selector/pipe/raw-fd failures could replace the first capture error, skip later closes and omit terminal accounting. | Keep primary and secondary failures, guard each owned finalizer, record exhausted-tail unknowns, and attempt bounded parent fallback after terminal append failure. | Fake cap+fsync, multiple close failures and terminal-ledger failure combinations. |
| Ledger fsync could skip fd close; main removed its timer before final accounting and recorded apparent success too early. | Attempt close despite fsync failure, quarantine failed writers, retain the timer through final accounting and decide final success afterward. | Fake fsync/close and final-accounting helper cases, including apparent success followed by accounting failure. |
| A fallible post-spawn ledger append occurred before both returned pipe handles entered the ownership set. | Acquire both returned pipes before logging/selector setup. | Fake post-spawn append failure verifies both acquired pipe closes are attempted. |

The v3 core is 30,821 bytes, SHA256 `24ec8b0100e57523151bf132aa92d2674591e82d3866ca09d51cdd22c74074b0`; its adjacent harness is 20,128 bytes, SHA256 `8a1ddf2f47a985c36461422ad7b573bc186a0846513cd24f9e3fc904ad7b3f4d`. `SOURCE-MAP.json` binds every retained origin path to exact package bytes. `MANIFEST.json` covers all package files except itself, including the source map and new verifier. Root and copied upstream license/notices remain intact.

## What was independently checked

The repaired source delta/schema review is retained at `reviews/source/repair-v3-review/DELTA-REVIEW-v1.json` (SHA256 `174eda2c6fc9444e8bd51b12d55b12a991785c9b64ca41154abf239af543832f`). It approved a separate NEW synthetic-control grant at source level and withheld native work. The actual grant, all raw stdout/stderr/time bytes, metadata-readback failure and both immutable ledgers are under `evidence/synthetic-controls/`. The exact independent execution-evidence review is under `reviews/execution/`; its JSON SHA256 is `d474810cd421e518c0b17c2b1e780552a4064f7f16e97bb88537cdaffd958f31`, accepted by the parent at 2026-11-02 21:55:03 UTC. That review approves the finite controls and does not approve an unseen publication export.

| Original-location fake-only run | Tests | GNU wall/user/system | Individual maxrss | Supplemental policy debit |
|---|---:|---|---:|---:|
| Normal, attempt 1 | 24/24 | 0.18 / 0.10 / 0.01 seconds | 27,992 KiB | 0.19 seconds |
| Optimized, attempt 1 | 24/24 | 0.54 / 0.44 / 0.02 seconds | 31,012 KiB | 0.55 seconds |

The ordinary test assertions and explicit controller guards remain active under `-O`. The suite imports only the NEW adjacent controller, replaces Popen/proc/selector/group/resource effects with fakes or leaves them uninvoked, and uses owned temporary data/descriptors. The two final-accounting cases exercise a helper, not a positive end-to-end main queue. It is finite coverage, not all 29 independently predeclared cases. No native compiler, original module, Root/native-TCB, shell calibration, intact original baseline or original V03 case was run by these controls.

A bookkeeping readback failed after the normal run because raw decimal spelling was compared with float reserialization. Its exact diagnostics and time/output bytes are retained. Domain/field parsing corrected that bookkeeping without rerunning tests or changing raw files. Attempt-1/no-rerun records are scoped retained evidence, not a universal process-history audit.

## Execution and portability contract

The controller contains hardcoded original `P`, command/context, digest, admission and queue-authority assumptions. Its archive is not a portable native collector. No actual final ADMISSION, native command, queue authority, funding or known-group/unknown-spawn cleanup disposition has been granted. Do not run `pilot_controller_v3.py` main.

`VERIFY.json` opts in only to the following Python 3.12 commands, each with a 10-second timeout, total at most 30 seconds. The generic runner provides its private bytecode-cache namespace and process-group cleanup. It stops after a failing command. There are no non-standard dependencies or external executable inputs. All package-local transitive controller/harness bytes are declared by the package inventory. `SOURCES.json` pins upstream catalogue/guidance/license provenance, while newly retained files are authenticated by `SOURCE-MAP.json` and `MANIFEST.json`; they are not falsely pinned as files already present in the base commit.

```text
{python} -I -B {package}/verify_integrity.py
{python} -I -B {package}/source/v3/test_pilot_controller_v3.py -v
{python} -I -B -O {package}/source/v3/test_pilot_controller_v3.py -v
```

From an authorized committed checkout, the registered entry point is:

```sh
python3.12 -B scripts/research_package.py --package research/h25-raw-pilot-failure-accounting --check-only
python3.12 -B scripts/research_package.py --package research/h25-raw-pilot-failure-accounting
```

The first new verifier reads retained bytes/JSON and creates only owned synthetic temporary fixtures. It imports no controller or test harness, launches no subprocess, and exercises seven archive failure controls: altered same-size payload, truncation, missing file, extra file, duplicate manifest path, traversal path and duplicate JSON key. Archive integrity, fake-suite execution and source-history availability are distinct results. The original-location actual run evidence above does not by itself establish execution of a later publication copy; any publication validation must bind the exact exported bytes and be separately granted and receipted.

## Qualifications, costs and source lineage

Every qualification flag in `SCOPE.json` remains false: query/native authority, intended complete emission, reporter fidelity, consumer bridge, full C05, full V03 and full runtime. Original progress remains 43.5%, 22/49 activities, stage 2/10, overall 1/10, 24 components and 52 helpers, with zero added original activity credit. This package provides no κ, paid-profile improvement, measured complete caller speedup or selected-frontier adoption.

The canonical guarded ledger stays `94.550533479` seconds. Immutable supplemental fake-control ledgers add `0.74`, giving `95.290533479/2400` recorded policy seconds; initial cap 600 and command cap 180 are unchanged, with no new budget. The controller's proposed native whole-job limit of 150 seconds is a separate ungranted contract. All setup, observer, approval, failure, cleanup, publication and outside costs remain `OPEN_NOT_ZERO`; a complete physical total is unknown. GNU-time individual maxrss is not an aggregate or hard peak claim.

A failed raw write can leave a prefix on disk before the controller advances its completed-block count/hash. Those fields must be called completed-block telemetry. Actual retained-file bytes require independent readback where possible; otherwise count/hash/identity must remain unknown. No third controller repair or native attempt is authorized here.

The exact 37-node bounded graph in `lineage/PR-COVERAGE-NEXT-v4.json` (SHA256 `189c0745bffdbea74478826cd6088b3b2b20a3716a796dfffe829d5a5c8bca09`) retains known predecessor/dependency heads and related PRs. Its older metadata observations are historical, not a fresh global overlap audit. In particular, [PR6397](https://github.com/CrocSwap/integer-mult-bounds/pull/6397) at `0b3b5d923a54808a13c3102657fc51ef2ec5ba3e` supplies the criterion/direct-consumer contract; this package adds raw-controller failure accounting and fake evidence, without claiming that criterion is discharged. [PR6351](https://github.com/CrocSwap/integer-mult-bounds/pull/6351) is related caught-primary/accounting boundary work; that source lineage does not become universal pre-delivery-error coverage.

The exact Pro19 prompt, answer, send/verification/completion receipts, links and parent's critical assessment are retained under `consultation/` for context. Pro inspected public criterion/original-source material and explicitly did not inspect the unpublished local controller/case. The first complete observation, 21:44:18.762 UTC, was after the fixed 21:41:18.975 deadline; completion-before-deadline remains UNKNOWN. No resend, extension or timely-completion claim is inferred.

`context/driver-root-spec-preflight/` retains passive report/bill context, not a new runnable source package or a whole C05 no-go. The earliest missing concrete driver-root binding was `STANDARD_LIBEXEC_PREFIX` at gcc.cc:1618/4697; Makefile:2331 is a template, not the installed authoritative binding. The literal 29+6=35 and 46,764,649-byte bill is passive arithmetic, not complete closure, wire fit or qualification. No new source search or scientific gate was opened by this archive.

## Open next questions

Structured questions and blockers are recorded in `TASK.json`. The smallest useful next work is to bind an actual final admission/context/funding/one-queue and genuine outer cleanup/unknown-spawn disposition before considering any separately authorized raw native DATA run. A later failure must independently identify retained-file bytes or preserve unknown/completed-block telemetry. These are prerequisites, not an automatic continuation.

Original C05/V03 still requires one concrete instance, independent closure/consumer binding, fit, C07 lifetime, complete costs and intact baseline plus every named original V03 case in both modes. The missing installed driver-root record is an explicit finite blocker for the examined route; resource refusal or absent records do not establish that no adequate construction can exist.

## Credit

Prepared for Clear1nsight with substantial OpenAI Codex assistance, retaining ChrisR's original research/source credit, predecessor and parallel contributions, and all CrocSwap/upstream source notices. See `NOTICE.md`, the unmodified `notices/` files and the retained lineage graph. AI review and finite unittest success are not human review, proof-kernel acceptance, merge or scientific adoption. Apache-2.0; source-specific notices remain in force.
