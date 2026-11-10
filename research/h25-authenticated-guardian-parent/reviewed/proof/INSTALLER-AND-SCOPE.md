# Original installer, retirement scope, and successor composition

This document records the original source contracts used in the bounded guardian-retirement repair beginning 2026-11-08T08:04:09.466443Z. The original authenticated-parent and late-input boundary was resolved in the previous supplement and is not reopened here. This is source inspection and proof authoring only. No source module, ctypes call, control, native target, or scientific workload has been executed.

## Exact reusable installer

The selected `fresh_supervisor.py` is the existing #6867 source at `319ea1c5f4097ef87cc0b037327f26374e93e54d`, with 127997 bytes and SHA256 `e5d1e3b834e3ac0c1cec02ca70776ae7a724c42e2b5bbb1661402c824f98affa`. Its public leaf is `research/h25-retained-child-lock-repair/readable/implementation/source/fresh_supervisor.py.txt`. The new outer entry can load this exact source into its own private module and call its actual `install_subreaper` function at lines 372–404 before creating any controlled child. Its docstring expressly identifies this as the future-parent use. It does not require an A context, an existing G channel, or a financial issuer.

The argument must use the actual original root argument `.../outputs/h25-data-handling-20261028`, not the repair implementation directory. The function reads `control/NATIVE-INITIAL-TCB-v1.json` below that root and requires SHA256 `610492b3fc06baa0560175edc3ba27057de00d00b8fd3d58dbe55e5a371c042a`. Its source checks the presence of the selected libc in that record. It then checks the following exact original native/stdlib pins before loading them and checks them again afterwards.

| Original native or stdlib path | SHA256 |
|---|---|
| `/usr/lib/x86_64-linux-gnu/libc.so.6` | `3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf` |
| `/usr/lib/python3.12/lib-dynload/_ctypes.cpython-312-x86_64-linux-gnu.so` | `aad3e24f186e6c0a1c7efa8f16004f951f527db86f6451d30118657384a456c1` |
| `/usr/lib/x86_64-linux-gnu/libffi.so.8.1.4` | `00f593fe192f2851b8ce23b25cec2488d769beb5a8f63e8c9e563071e1075153` |
| `/usr/lib/python3.12/ctypes/__init__.py` | `0782592567ad71097198a3afe985ac3e2ea0b9b5e75452402c9460c89a86318a` |
| `/usr/lib/python3.12/ctypes/_endian.py` | `c5d692bdce10dfee242752620061bab684633bc72445a3def484961ef1bdbf3a` |

The function calls the original `launch_contract` at lines 207–216, requiring the exact CPython executable, no-site/safe-path/fixed-seed flags, closed environment, initial stdlib path, and exactly one parent task. It checks no pre-existing child, resolves the original libffi SONAME, checks actual ctypes module owners, constructs the typed libc `prctl`, and calls GET, SET, and GET of CHILD_SUBREAPER in the same process. It requires final readback 1. It returns the original observation DATA and the actual `(library, call)` keeper pair. The outer owner must strongly retain the pair and the private source/module/function identities through the lifetime of all children and custody work.

These are exact source and ownership edges. The initial TCB body and installed native images are original genuine runtime inputs. Their presence or eligibility on this machine is not asserted by the source pins. No native input was read from a live target while preparing this proof.

The current internal controller already calls this installer at `composed_controller.py` lines 1518–1519, after obtaining its own context and queue binding. Reusing it in a separate fresh outer process does not substitute that process for C2 or move production A before G. The two source calls create distinct actual same-process subreaper owners at their respective places in the process tree.

## Why only the installer is reused

The same supervisor contains `OwnedDomain.cleanup` at lines 756–790. That implementation attempts domain cleanup and then closes its known pidfds even when an error or remaining descendants prevent complete cleanup. Its original inner route has a separately retained G domain owner, which must retire unresolved work. It cannot be adopted as an outer owner of G merely by passing a different root. Doing so would discard the precise custody that the outer repair needs after G fails. The new code must own G and any actual adopted children through its own explicit state transitions and must not infer ownership from a copied registry or a role name.

## Native G failure that the outer owner must cover

The unchanged G source has 69450 bytes and SHA256 `72bf7d0f7e1a4fe7adf909ebd74ae9411b69042ca7740c487b1ba25ba31c9c43`. Its actual `launch_pre_m` calls `setsid` in M before exec. M therefore is not protected by a signal to G's process group. A direct wait for G cannot establish retirement of M or its descendants.

The G source itself retains another consequential distinction. `caught` at line 123 sets `interrupted`. `budget` at lines 103–111 returns false when interrupted. `retire_domain` at lines 569–590 attempts its own cgroup kill write, but its drain/wait loop is guarded by `budget(0)`. A caught SIGTERM can therefore prevent G's own drain loop from establishing complete waits even when the kill write succeeds. A deadline can have the same effect. The outer repair must not claim that TERM alone proves complete retirement.

An actual outer subreaper supplies a different original native ownership relation. It is a surviving ancestor of the freshly created G and its closed descendant tree. If G dies, the kernel reparents eligible orphans to that real owner. Separate sessions do not defeat ancestry-based adoption. Actual pidfds may then identify children for signalling without risking a recycled numeric process identifier. A final exact direct-child census and an actual terminal `wait` result of ECHILD can certify that this original closed descendant tree has no remaining child, provided the source retains sole consuming-wait ownership, has no pre-existing or unrelated child, and creates no later producer. An earlier empty census, G's direct wait, or a DATA `UNKNOWN` marker cannot supply that certificate.

This introduces no second cgroup authority. G remains the only selected owner of its cgroup descriptors and protocol. The outer process uses the original same-user process/child/pidfd/subreaper interfaces and its genuine birth/ancestry relation. It must not open a copied cgroup path or manufacture a second G association.

## Original budgets and failure semantics

The current role constructor requires original `request.body_reservation_ns` to be a positive integer no greater than 180000000000 and original `cleanup_reservation_ns` to be positive and smaller than that body reservation. Native G separately checks its outer-actor body/cleanup values against the actual original grant. Outer-actor and actor-policy records are distinct. A repair must select the actual relevant original reservation and prove its joins rather than assume all identically named fields are equal.

The original clock profile retains the whole 180-second body bound, separate outside 30/queue 390 checks, and positive original cleanup reserve. C's `complete_bill` at lines 1070–1113 checks the nine original positive outside terms, both complete normal/optimised case rows, and their total against the same request reservation. It does not prove numerical fit and does not grant additional time.

The outer owner must stop ordinary working activity early enough to preserve the original cleanup reserve. A grace interval for G, an adoption/wait interval, bounded capture reads, and final holder retirement must be allocations within that same reserve, not newly added allowances. A new whole-wrapper endpoint must include late-input transport, source loading, subreaper installation, derivation/publication, pre-G custody, G execution, and outer terminal work. G's own first timestamp begins later and cannot alone cover those earlier actions. Actual overlapping and exclusive cost scopes must remain distinguished; no new wrapper term may silently vanish into a G-only measurement category.

Native failures do not disappear because a budget expires. Original F explicitly records observed elapsed values which exceed the command/reservation limit as failed/overrun work, does not clip them, and leaves incomplete native/cleanup costs open. Its header says the complete outer body includes nested execution and cleanup. `assess_round` returns DATA eligibility only and explicitly denies native ownership/cleanup authentication and execution permission. Consequently continued real custody after a failed native retirement is not successful within-budget completion, free work, or a new allowance. It must retain the original failed/unpriced operation and block future admission.

No original T1/T2 clause guarantees that every signal, wait, close, read, or acquisition succeeds. A source proof can establish safety and an exact positive retirement certificate. It cannot prove universal bounded physical termination on a trace where all authorised termination/wait mechanisms fail permanently. If actual custody remains unresolved, the owner must remain real and retained, or be genuinely transferred through an already supported owner relation. Emitting `UNKNOWN` and exiting with stranded children is not such a transfer. The distinction between safe blocked custody and completed retirement must remain explicit in the final source verdict, and no parent-death durability claim follows from in-process references.

## Original criterion scope

S07.01 is the original independent review of the exact parent capture/launch source route. S07.02 is the all-six freeze. S07.03 is genuine cache/full-caller and automatic-retention binding. S07.04 is complete current source/helper/driver/native binding reconciliation. S07.05 is independent acceptance of the complete combined stage and installation order. The methodology explicitly permits source tasks to complete their stated source scope and forbids treating their completion as runtime/performance qualification.

S06.05 separately requires genuine terminal cleanup, failed-attempt accounting, and the final timing/publication boundary. The complete normal/optimised control gates and actual comparison/CLOSE remain separate. Source acceptance may prove the normal path and failure ownership without claiming every permitted native-failure execution eventually completes physically. It must nevertheless prove that its own failure branch does not abandon the real owner or misreport retirement. A new whole-stage source verdict requires inspection of the actual repaired code, not merely this contract analysis.

## Successor tuple and installation order

The current complete internal source tuple remains #6867 plus its previously accepted exact S07.02/.03/.04 arguments. The proposed repair is an outer composition delta. It need not modify any of the old 66 leaves, seven profiles,61 roles, or the two197-member recipes. The old manifest must not silently acquire a broader meaning covering new outer code. A separate outer manifest/installation record must bind the new owner, target entry, host template, encoder, and complete proof scope, with exact byte identities after their final freeze.

The acyclic order is original internal sources/recipes/profiles and detached manifest; new outer source and native-interface selection; deterministic fixed shell; candidate document; genuinely issued original inputs; source-authenticated per-operation host invocation; actual late-input delivery; current private derivation; exact exclusive immutable publication; final G argv; genuine actual native entry; and original independent terminal consumers. No candidate-dependent final config, role-contract, CAPTURE grant, or actor-policy digest enters the earlier fixed shell. Later generated host invocation identity is downstream and must not feed back into the earlier candidate.

The new source must call the actual selected installer before G birth and retain its native keeper. It must construct G argv from actual returned-and-published result pins, release any pre-G C EX before P's new EX, preserve the exact native capture paths, `/dev/null` stdin, cwd/environment, and descriptor census, and hold consuming-wait responsibility through both the G and adopted-child branches. Failure readback must distinguish a known working error from uncertain IO custody. Safe complete reads may proceed after a known working error; they may not start new acquisitions after uncertain ownership merely to manufacture a final report.

The four implementation files were frozen at 2026-11-08T08:34:51.793005Z in SOURCE-FREEZE.json. The concrete target/owner composition, actual uncertainty-forwarding edge, and complete acyclic graph are now supplied by TARGET-COMPOSITION.md, SOURCE-ACTIVITY-APPLICABILITY.md, and FINAL-TUPLE-INSTALL-DAG.json. Final independent verdicts are recorded separately in the root decision and certificate. No runtime installation or qualification follows from this source freeze.

## Final integrated uncertainty edge

The frozen target calls the actual owner's retain_external_custody_uncertainty with its retained real error before the one retirement entry whenever its own native acquisition/close bookkeeping is uncertain. The reached method changes only the existing actual owner's uncertainty state. It issues no permission DATA and acquires no handle or authority. This joins the target and owner failure states so that an uncertainty in the parent gate/capture custody cannot be followed by a new metadata reader or child-pidfd acquisition in the owner. Already-owned native handles may still receive safe nonblocking cleanup within the same deadline. Preowned capture readers are used only after actual child-domain emptiness. A working error alone does not disable those full reads.
