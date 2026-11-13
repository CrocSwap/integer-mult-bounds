## Decision

**The published tuple is not ready for complete source-binding acceptance. I found two concrete source mismatches, and the shortest correction is one immutable successor that repairs both and tests the actual factory-to-launch boundary.** Neither correction requires changing the scientific bodies, relaxing authentication, or extending the selected native/compiler model.

This is a constructive result for S07.04, whose original completion test requires reconciliation of the complete stage’s source, helper, driver, and native bindings. It is not a claim that two repaired lines complete that activity. The existing conditional native proof remains reusable, but the changed supervisory connections and remaining campaign bindings still need their own joined review. The original activity definitions are in [ACTIVITY-BREAKDOWN-v16.json](https://github.com/CrocSwap/integer-mult-bounds/blob/1ac58a84b725bd6f17eec66727edc877c49c7e66/research/h25-full-caller-readable-inputs/ACTIVITY-BREAKDOWN-v16.json).

I inspected the immutable published source bodies and relevant preparation, freeze, and control code. No public file I attempted to retrieve was inaccessible. I did not execute, import, compile, or initialise any project owner.

## 1. The first production obstruction is an inconsistent authenticated loader path

The actual chain is `controller_entry.main → PrivateBundle.associate_environment → environment_association.open_parent → _authenticate`.

The bootstrap and private loader select the `/repair-v3` version. However, `environment_association.py` lines 29–33 still construct `LOADER_PATH` from the unsuffixed assembly root. Its `_authenticate` at lines 221–223 requires exact equality with the actual loader module’s `__file__`. Consequently, the genuine production call raises `AssociationError("actual fixed private loader module")` before constructing the environment association. This does not depend on missing current qualification records. The two selected source strings disagree. See the [bootstrap](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/readable/implementation/bootstrap/controller_entry.py.txt), [loader factory](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/readable/implementation/bindings/private_loader.py.txt#L390-L397), and [association authentication](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/readable/implementation/bindings/environment_association.py.txt#L220-L253).

The preparation defect is also identifiable. `prepare_retirement_repair_v3.py` replaces absolute predecessor paths and one quoted `outputs/...` spelling, but the association uses `W + '/outputs/...'`. That leading-slash form escapes the replacement. The published source controls authenticate selected file bytes and exercise the supervisor’s `_COMMON` binding, but they do not call the actual association factory. Their success therefore does not contradict this failure. See the [preparation script](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/prepare_retirement_repair_v3.py#L8-L18) and [source-assembly controls](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/validation/test_source_assembly.py).

**The correction belongs in source preparation, not in the authentication predicate.** Select the new version’s exact root in the association’s owning `R` assignment. Preserve the exact loader name/path, enrolled `PrivateBundle`, same-PID/controller role, module identity, code/globals, and authentic calling-frame checks. Allowing either path, deriving authority from whichever module happened to load, or patching its globals after loading would weaken the contract.

## 2. A second obstruction would remain after the factory repair

The waiting entry builds native arguments containing:

```python
'--read-root', str(READ_ROOT)
```

Here `READ_ROOT` is the original historical working directory. But its actual `Popen` at line 350 launches that native entry with `cwd=stage`.

The unchanged native entry takes `argv[10]` as the required original working directory. `validate_owned_paths` compares it with `getcwd()` and refuses with `original-cwd-is-preserved` when they differ. Thus, assuming earlier native setup succeeds, the current launch reaches a deterministic refusal before GNU time and science. This is an envelope failure, not the original optimized scientific refusal. See [candidate_entry.native_argv and main](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/readable/implementation/source/candidate_entry.py.txt#L283-L351) and [native validate_owned_paths](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/readable/implementation/native/science_view_entry.c.txt#L458-L469).

The earlier #6830 runner supplied the historical directory both through `--read-root` and through `Popen(cwd=HERE)`. Restore that established interface by changing the waiting entry’s launch to `cwd=READ_ROOT`. Do not redefine the historical directory as the stage or remove the native check. The predecessor is readable in [#6830 fresh_runner.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/39fcd67c991bd72918080b1d2c02feb3d679206d/research/h25-caller-proof-completion/readable/implementation/source/fresh_runner.py.txt).

## 3. One connected correction and freeze

For a newly selected immutable version, such as `repair-v4`, the two substantive runtime-source changes are the following. This is a proposed delta, not a generated or tested artifact.

```diff
--- implementation/bindings/environment_association.py
+++ implementation/bindings/environment_association.py
@@
-R = W + '/outputs/connected-caller-assembly-20261107T2053Z'
+R = W + '/outputs/connected-caller-assembly-20261107T2053Z/repair-v4'

--- implementation/source/candidate_entry.py
+++ implementation/source/candidate_entry.py
@@
-            child=subprocess.Popen(native,cwd=stage,env=dict(ENV),stdin=stdin['object'],stdout=out,stderr=err,
+            child=subprocess.Popen(native,cwd=READ_ROOT,env=dict(ENV),stdin=stdin['object'],stdout=out,stderr=err,
                                    close_fds=True,start_new_session=False,preexec_fn=limits)
```

The preparation correction must accompany these edits. Authenticate the exact predecessor bytes, locate the single expected module-level `R` assignment structurally, and replace that assignment with the selected successor root. Reject an unexpected assignment or multiple matches. Before freezing, establish the following equality from the actual bodies and manifest:

```text
controller_entry.LOADER
= private_loader.R / implementation/bindings/private_loader.py
= environment_association.LOADER_PATH
= manifest.source_pins.private_loader.path
```

This is a consistency assertion between independently selected source locations, not permission to accept an arbitrary location.

Reuse the existing freeze order. Freeze the changed owner leaves, copy the changed waiting entry into **both** selected stages, rebuild `JOBS.json` and `STAGE.json`, update queue stage pins and command profiles, then rebuild the selected packet and detached manifest. Finally derive new role/configuration DATA through the genuine existing constructor. The current [freeze script](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/freeze_source_assembly.py#L10-L94) already contains most of this dependency order, including both stage-entry copies. Add the missing semantic consistency checks before it emits the final manifest.

No new digest should be invented in advance. Do not issue role records, STARTs, currentness receipts, or grants as part of this source freeze.

### Why these changes preserve the intended source boundary

The loader correction makes the selected expected path agree with the authentic bootstrap’s actual path. It removes no identity check and grants no additional caller access. The calling-frame checks in `open_parent` still require the real `PrivateBundle.associate_environment` method.

The working-directory correction restores the native input relation already used by the predecessor. It leaves the original stage arguments, Root/provider commands, artifact and usage identities, clean environment, compiler limits, and scientific images unchanged. It does not manufacture success when another native precondition fails.

These are proofs of the two corrected interfaces. They are not proofs that all later native or scientific operations succeed.

## 4. Bounded regressions that distinguish this subject from its correction

The decisive controls should exercise the owning boundaries, while explicitly stopping before genuine qualification or owner creation.

| Control | Published subject | Corrected subject and required assertions |
|---|---|---|
| Authentic association call chain | Fails at `_authenticate` because the loader path differs. | Use the actual loader class, source-loaded association, exact module registration, and retained source-transport fixture. Call actual `associate_environment` with deliberately missing required selection DATA. It must pass authentication and the authentic caller-frame check, then stop at the required selection lookup. No association or native-I/O context may be created. |
| Strict factory negatives | Must reject substituted paths and identities. | Wrong loader root/name, unenrolled bundle, wrong role/PID, replaced module/function/globals, and an external direct call must still fail. Do not patch `LOADER_PATH` inside the loaded module. |
| Native launch boundary | Captured `Popen` cwd differs from `native_argv[10]`. | With labelled inert read/launch ports and distinct stage/history paths, the actual command construction and launch call must satisfy `cwd == argv[10] == ORIGINAL_CWD`. The unchanged C guard is the independent source predicate. No subprocess is launched. |
| Frozen stage join | A changed source copy alone is insufficient. | Both installed stage-entry bytes, both stage manifests, the waiting-entry pin, queue stage pins, and command/profile selections must agree. Every scientific member outside the declared entry/JOBS delta must retain its predecessor identity. |

The first positive is deliberately **factory reachability to the mandatory input boundary**, not a fabricated admitted association. This avoids restoring an original Context from DATA or claiming that inert ports qualify a real owner.

Retain the earlier strict-path, once-only common binding, waiting-release, timer-unwind, and retirement controls. In particular, the timer correction must continue to preserve an existing working primary before ordered cancellation/restoration errors, with uncertain retirement preventing successful closure. Neither proposed edit touches those finaliser bodies. The published [timer controls](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/validation/test_timer_retirement.py) remain relevant retained evidence; I did not rerun them.

## 5. Reuse the earlier proof, but transfer the changed interfaces explicitly

I compared the published current and predecessor native entry, compiler policy, property-query observer/receiver, and selected native/OS/filesystem/CPython profiles. Those subjects are unchanged. The earlier conditional proof can therefore be reused for its exact subject and premises. It must not be promoted into a proof of a different incoming command or process topology. The governing argument and stated limits are in [PRESERVATION-v1.md](https://github.com/Clear1nsight/integer-mult-bounds/blob/39fcd67c991bd72918080b1d2c02feb3d679206d/research/h25-caller-proof-completion/proof/PRESERVATION-v1.md) and [CANDIDATE-SOURCE-REVIEW.json](https://github.com/Clear1nsight/integer-mult-bounds/blob/39fcd67c991bd72918080b1d2c02feb3d679206d/research/h25-caller-proof-completion/evidence/CANDIDATE-SOURCE-REVIEW.json).

| Boundary | Reusable result | Remaining transfer obligation |
|---|---|---|
| Native/compiler semantic subject | Existing finite Linux 6.12 and compiler consequence argument. | Preserve every selected configuration, source/image, filesystem, security, and interval premise. Current factual association remains unissued. |
| Bootstrap and association | Existing strict source-private factory design. | Prove the corrected version/path map and actual factory reachability, rather than only manifest membership. |
| Native launch | Existing command interpretation and original-cwd check. | Apply the cwd repair above and verify the complete argv/environment/FD relation. |
| Common runner and waiting entry | Existing bounded ownership, release, and timer work. | Join protected generations, query retirement, registered writers, EOF, deadlines, and one-use release to the actual production caller. |
| Scientific and terminal relation | Unchanged scientific bodies and original oracles. | Preserve normal positive validation, original optimized startup artifacts and refusal, and separation of envelope exit 125 from original refusal exit 1. |

One consequential topology change remains specifically unproved by this review. The predecessor launched the native entry with `start_new_session=True`; the waiting entry uses `False`. That may be appropriate for the common runner, but native-byte identity does not establish preservation of group-sensitive controls, monitoring, or retirement. The joined review must trace the selected original consumers and establish the required group relationships. Blindly restoring `True` could instead break the new monitoring boundary. This is a finite source-delta obligation, not a demand for a universal Linux proof or an unqualified scientific run.

The original 52 bodies and 65 contexts remain the coverage domain. Two enclosing modes do not replace that mapping.

## 6. Remaining complete bindings and the implementation exit

Three larger connections must remain explicit.

First, the current controller still drives its candidate normal/optimized sequence and expressly records that fresh independent baseline transfer/comparison is not completed there. The receiver’s retained `full:baseline` source route names the instrumented `9bbafe3f…` subject, not the genuine primary `5b963a5f…` predecessor. Do not make that source record into a fresh baseline observation. Inspect the actual [controller](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/readable/implementation/controller/composed_controller.py.txt) and [receiver](https://github.com/Clear1nsight/integer-mult-bounds/blob/c009a7514790e865b664ab8cd4688d37787d7eaa/research/h25-connected-caller-assembly/readable/implementation/source/full_result_receiver.py.txt#L213-L225). The genuine baseline owner’s opaque, process-local ownership and receiver interface should be adopted from [#6837’s interface](https://github.com/Clear1nsight/integer-mult-bounds/blob/92bd2213be787cc4451a3b61b00793dad26bebdd/research/h25-primary-baseline-readable-inputs/baseline/INTERFACE.json), with #6847’s inherited-limit repair, rather than reconstructed from command DATA.

Second, automatic retention is present in the current controller’s completed-boundary, parent-readback, and release sequence. Its presence does not establish successful formal financial CLOSE. The selected `active_current.publish_reviewed_close` still has the legacy STOP/unknown restriction. The existing [#6762 complete-close successor](https://github.com/Clear1nsight/integer-mult-bounds/blob/3bcf99910a95248452e955d382c59bd23792a39b/research/h25-complete-outcome-close/implementation/active_complete_close_v1.py) needs actual caller, role/bootstrap, evidence, and source-pin adoption. Its inert fixture results do not qualify the real publisher.

Third, the unchanged conditional native model requires a genuinely associated instance. The [dated environment hold](https://github.com/Clear1nsight/integer-mult-bounds/blob/39fcd67c991bd72918080b1d2c02feb3d679206d/research/h25-caller-proof-completion/evidence/CURRENT-ENVIRONMENT-HOLD.json) is neither a current complete certificate nor permission to extend the proof to another kernel. No new model extension is needed to fix the two source defects identified here.

**The implementation sequence should be one connected revision.**

1. Preserve the published subject and failures, apply both owning-source corrections, and repair preparation’s exact root selection.
2. Add the actual factory-boundary and native-launch discriminators, then rebuild both stages and all dependent pins through the existing freeze.
3. Complete the supervisory delta argument, especially process-group semantics, and reconcile every changed actual call with its selected source, role, and profile.
4. Independently review the resulting complete binding graph, recording the genuine baseline/comparison and CLOSE adoption boundaries explicitly. Accept S07.04 only when its complete selected scope is reconciled, not when these two regressions pass.

I inspected the bootstrap, loader, association, role constructor, manifest, supervisor, common runner, waiting entry, receiver, controller, relevant preparation/freeze controls, and the cited native/proof subjects. I did **not** re-certify every external scientific/helper dependency, the complete baseline module DAG, or all retention/native premises. Accordingly, the present result is **two verified production defects, a minimal connected correction, and bounded discriminating checks**. It supplies no complete activity credit, current admission, numerical fit, baseline equality, or measured improvement.