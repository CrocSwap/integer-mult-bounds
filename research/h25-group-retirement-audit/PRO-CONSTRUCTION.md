## Decision

**Keep `start_new_session=False`, but repair the common runner’s retirement order. The published process-group invariant is false because the runner can signal a recycled process-group number after reaping its original group leader.**

This is an admissible counterexample involving the actual selected runner and an original completed or optimized-refusal case. It requires neither a new scientific API call nor compiler misbehaviour. The smallest correction is to observe the direct child’s terminal state without reaping it, perform the final group signal while that child still reserves its numeric identity, and then consume its wait once.

The correction needs a declared common supervisory successor and updated bindings. It does **not** require changing either scientific image, the factory/cwd repairs, the native isolation model, or the original scientific refusal. It also does not complete the whole source-binding activity.

### Input and coverage audit

I inspected the current README, source map, interface argument, common runner, waiting entry, supervisor, guardian, native view, receiver, registry, relevant carrier sources, and the earlier runner. I also inspected the original cold-build owner and its group-sensitive controls, and the relevant Linux v6.12 PID, signal, and wait implementations. No project code, control, native operation, or workload was executed.

The directly readable sources were sufficient to establish the counterexample. They were not sufficient for a fresh, complete no-group-change proof over all 52 bodies and 65 contexts. In particular, the [#6830 source map](https://github.com/Clear1nsight/integer-mult-bounds/blob/39fcd67c991bd72918080b1d2c02feb3d679206d/research/h25-caller-proof-completion/SOURCE-MAP.json) identifies, but does not expose as readable bodies, the exact selected `cache_contract_v8.py` and `cold_authority_v7.py` variants. Their normal hashes are `06911ec0…fa64ac` and `b32155cd…abee5`; the optimized variants are `d317c986…01a2` and `f279ab86…aec10`. I have not inferred their behaviour from those hashes or decoded their archive.

## 1. What the topology actually changes

Let `R` denote the runner, `T₀` the new outer GNU-time process, `E` the waiting entry, and `T₁` the native-entry process that subsequently execs inner GNU time. Each recorded generation is the actual PID plus start ticks, corroborated where required by a held pidfd.

| Birth or boundary | Earlier #6830 | Current #6864 | Actual ownership |
|---|---|---|---|
| G → M → K → P/C2 | Fresh cgroup D; M, K, and P establish the selected sessions. P execs C2 without changing its PID. | Unchanged. | G owns D and native lifecycle records; each carrier owns its immediate wait and captures. |
| C2 → R | R starts a new session/group. | Same. | C2 registry, `OwnedDomain`, actual R pidfd, and G Root registration. C2 owns R’s consuming wait. |
| R → immediate native/observer child | Native entry starts a new session, then execs GNU time. | R starts `T₀` in a new session, with SID = PGID = PID `q`. | R owns the immediate `Popen` and wait. C2 also holds observed generation pidfds. |
| `T₀` → E | Absent. | E inherits group `q`, publishes ARRIVED, and stops before inner birth. | GNU time waits for E; the authenticated C2 parent owns the one-use pidfd release after qualification and known intent closure. |
| E → native entry → `T₁` | The equivalent native/time process was R’s separately grouped child. | `start_new_session=False` preserves group `q`; native setup and exec do not change it. | E owns the immediate pidfd, wait, inner relay, and local closure record. |
| `T₁` → scientific Root and compiler children | Ordinary children inherit the inner time group. | Ordinary children inherit `q`. | GNU time, original scientific wrappers, and compiler owners retain their distinct waits and failure protocols. |
| C2 → property query | Separate query session/group, before scientific launch. | Separate query session/group while R/T₀/E are protected and E is stopped. | Query `OwnedDomain` borrows the exact protected-generation exclusion; it does not own their pidfds or release. |
| Seal and final retirement | Source registry plus genuine G closure. | Same responsibilities. | Local waits and EOF precede registry closure; G’s frozen D census and final retirement remain mandatory. |

The relevant births and ownership checks are in [fresh_supervisor.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/source/fresh_supervisor.py.txt#L547-L788), [candidate_entry.py](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/source/candidate_entry.py.txt#L296-L402), and [retention_guardian.c](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/native/retention_guardian.c.txt#L373-L426).

Blindly restoring `True` in E would place science outside the group sampled and killed by common R. The outer domain could still observe or retire it, but that would not preserve the common runner’s declared group measurement and control boundary.

## 2. The concrete failure trace

The current common runner does the following.

1. Line 354 launches `T₀` with `start_new_session=True`.
2. Line 356 calls consuming `process.poll()`.
3. Line 368 calls `process.wait()`.
4. Its `finally` then unconditionally calls `killpg(process.pid, SIGKILL)` at line 371, followed by another wait.

See [the actual monitoring block](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/source/run_guarded_v3.py.txt#L350-L374).

A permitted trace is therefore:

- The original optimized case produces its genuine refusal, E completes its local retirement, and `T₀` exits.
- R’s `poll()` reaps `T₀`. Its session/group has no remaining members.
- R is descheduled before the final group signal.
- An unrelated same-UID host process receives recycled number `q` and establishes a new session/group.
- R resumes and sends `SIGKILL` to that unrelated group.

The existing premises do not grant a host-wide exclusion over PID allocation. This example changes no scientific body and introduces no scientific group operation.

**The held pidfd does not prevent this.** Linux v6.12 removes the numeric PID from the namespace lookup in `free_pid`, independently of the later destruction of the reference-counted PID object. Numeric group signalling subsequently resolves the number through `find_vpid`. A pidfd remains a reference to the old identity, but `killpg(q)` does not use that reference. See [`pid.c` allocation retirement](https://github.com/torvalds/linux/blob/v6.12/kernel/pid.c#L133-L163), [`__change_pid`](https://github.com/torvalds/linux/blob/v6.12/kernel/pid.c#L346-L367), and [numeric signal lookup](https://github.com/torvalds/linux/blob/v6.12/kernel/signal.c#L1603-L1617).

The earlier #6830 runner avoided this particular final signal after a committed wait. Its final group kill was conditional on `READY` or `SAFE_NONTERMINAL`. See [the predecessor retirement block](https://github.com/Clear1nsight/integer-mult-bounds/blob/39fcd67c991bd72918080b1d2c02feb3d679206d/research/h25-caller-proof-completion/readable/implementation/source/fresh_runner.py.txt#L683-L728).

G cannot repair the erroneous signal afterwards. Its cgroup ownership protects retirement of D; it does not undo harm to a process outside D.

## 3. Preservation results that can be established

### The original group observation is relational

The inspected cold-build controls capture `original_group = os.getpgrp()`, require the parent group to remain unchanged, and compare the child’s JSON against that captured group. They do not require a particular numeric PGID or PID = PGID. The cold builder launches with `start_new_session=False`, and its limit callback changes FSIZE rather than group membership. Therefore the inherited-group predicate is preserved in the current topology, provided the original operation follows that selected path. The actual numeric observations must remain in the retained evidence without rewriting. See the [cold-build owner](https://github.com/CrocSwap/integer-mult-bounds/blob/ff7df8391c3bb3f5518ce43682ba4c1e41380e3e/research/h25-fresh-sc-constructor/successor-v26/implementation/payload/body-pool/aa0a315110e031e19291970c9611fe5e0f91465fa20eaec51e81186099563f78.blob#L169-L240) and [original controls](https://github.com/CrocSwap/integer-mult-bounds/blob/ff7df8391c3bb3f5518ce43682ba4c1e41380e3e/research/h25-fresh-sc-constructor/successor-v26/implementation/payload/body-pool/37db9881193f0ecf111f8ce94b6ef84cd3b22d1123b3266ced25390aa48d5a52.blob#L93-L179).

Those same controls expressly leave failed-build finality to the outer owner’s whole-group termination and join. The inheritance lemma does not discharge retirement.

### Session changes do not escape the genuine cgroup

G creates D before M’s `CLONE_INTO_CGROUP` birth. Under the unchanged finite effect premises, descendants inherit D and have no migration/export channel. `setsid` and `setpgid` do not change cgroup membership. Indeed, the selected science policy permits those calls, so it would be incorrect to derive group invariance merely from seccomp.

G’s seal freezes D and rejects live producers or unregistered descendants. Failure retirement separately requires `cgroup.kill`, recursive population emptiness, native reaping, and final wait reconciliation. Short-lived children, changed groups, and reparenting do not make these obligations disappear. G loss itself still has no automatic-success theorem. These implications follow from [the native view](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/native/science_view_entry.c.txt#L698-L820) and [guardian retirement](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/native/retention_guardian.c.txt#L537-L597).

This is a conditional cgroup/lifetime result, not proof that group sampling captures every instantaneous memory peak or every permitted group-changing path.

### Local closure remains distinct from domain closure

E deliberately reports `process_group_empty=False`. The receiver separately requires completed outer cleanup, no remaining or adopted-after-root processes, complete relay EOF, and known descriptor closure. If a cap kill also kills E before its relay drains, missing or incomplete closure remains failure/uncertainty. It must not become “complete retained output”. See [entry closure](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/source/candidate_entry.py.txt#L372-L402) and [terminal validation](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/source/full_result_receiver.py.txt#L272-L338).

## 4. Proposed owning correction

### The retained-child lemma

Replace consuming monitoring polls with `waitid(P_PID, pid, WEXITED | WNOHANG | WNOWAIT)`. Linux’s `WNOWAIT` path obtains terminal information without moving the zombie into the consumed state. Perform the last numeric group signal before the sole consuming wait. See [`wait_task_zombie`](https://github.com/torvalds/linux/blob/v6.12/kernel/exit.c#L1143-L1169).

The no-auto-reap premise has a source derivation for the inspected candidate chain. Actual M entry requires default SIGCHLD; the selected intervening carrier/controller sources do not replace it; fresh exec clears signal-action flags, including `SA_NOCLDWAIT`. Thus R retains its direct child until its own consuming wait. This uses the existing authentic-entry and selected-native semantics, not a new global exclusion. See [M’s actual launch checks](https://github.com/Clear1nsight/integer-mult-bounds/blob/c8f7bd582ffc1301b851dde2364c60f1636aac8b/research/h25-caller-binding-repairs/readable/implementation/carrier/inner_meter.py.txt#L222-L231) and [Linux signal-action reset](https://github.com/torvalds/linux/blob/v6.12/kernel/signal.c#L533-L545).

Consequently, while numeric group signalling is possible, `q` still belongs to the original live or unreaped child. Once the consuming wait is entered, this function performs no further numeric signal. A failed or unrecognised observation does not license a guessed cleanup target.

### Patch-ready implementation

Add the following owner to `run_guarded_v3.py`. It also replaces the surrounding capture `with` statement, because a later file-close exception must not mask the working primary. This is proposed source, not executed or independently accepted code.

```python
_GROUP_CUSTODY = [None]


def run_group_capture(timed, stage, env, folder, runner_start, cap, spent):
    if _GROUP_CUSTODY[0] is not None:
        raise RuntimeError('one common-runner group owner')

    state = {
        'process': None, 'spawn': 'NOT_ENTERED',
        'peek': 'NOT_ENTERED', 'raw_peek': None,
        'owns_unreaped_child': False,
        'signal': 'NOT_ENTERED', 'signal_absent': None,
        'wait': 'NOT_ENTERED', 'raw_wait': None,
        'streams': [[None, 'RESERVED'], [None, 'RESERVED']],
        # Body, signal, wait, stderr-close, stdout-close.
        'errors': [[None, None] for _ in range(5)],
        'unknown': False,
    }
    _GROUP_CUSTODY[0] = state
    peak, stop, code = 0, None, None

    try:
        for index, name in enumerate(('stdout.txt', 'stderr.txt')):
            row = state['streams'][index]
            row[1] = 'OPEN_ENTERED'
            row[0] = (folder / name).open('wb')
            row[1] = 'OWNED'

        state['spawn'] = 'ENTERED'
        process = subprocess.Popen(
            timed, cwd=stage, env=env,
            stdout=state['streams'][0][0],
            stderr=state['streams'][1][0],
            start_new_session=True)
        state['process'] = process
        state['spawn'] = 'RETURNED'

        while True:
            state['owns_unreaped_child'] = False
            state['peek'] = 'ENTERED'
            observed = os.waitid(
                os.P_PID, process.pid,
                os.WEXITED | os.WNOHANG | os.WNOWAIT)
            state['raw_peek'] = observed
            if observed is not None:
                if (type(observed) is not os.waitid_result or
                        observed.si_pid != process.pid or
                        observed.si_code not in
                        (os.CLD_EXITED, os.CLD_KILLED, os.CLD_DUMPED)):
                    raise RuntimeError('actual owned terminal observation')
            state['peek'] = 'KNOWN'
            state['owns_unreaped_child'] = True
            if observed is not None:
                break

            peak = max(peak, group_rss(process.pid))
            if peak > RSS_CAP:
                stop = 'sampled_group_rss_cap'
            elif time.monotonic() - runner_start > min(TIMEOUT, cap - spent):
                stop = 'wall_or_aggregate_cap'
            elif max((folder / 'stdout.txt').stat().st_size,
                     (folder / 'stderr.txt').stat().st_size) > OUTPUT_CAP:
                stop = 'output_cap'
            if stop:
                break
            time.sleep(0.05)

    except BaseException as error:
        state['errors'][0][0] = error
        state['errors'][0][1] = (
            BaseException.__dict__['__traceback__'].__get__(
                error, BaseException))
        if state['spawn'] == 'ENTERED':
            state['spawn'] = 'UNKNOWN'
            state['unknown'] = True

    finally:
        process = state['process']
        if process is not None:
            if state['owns_unreaped_child']:
                state['signal'] = 'ENTERED'
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                    state['signal'] = 'KNOWN'
                except ProcessLookupError as error:
                    state['signal_absent'] = error
                    state['signal'] = 'KNOWN_ABSENT'
                except BaseException as error:
                    state['errors'][1][0] = error
                    state['errors'][1][1] = (
                        BaseException.__dict__['__traceback__'].__get__(
                            error, BaseException))
                    state['signal'] = 'UNKNOWN'
                    state['unknown'] = True

                state['wait'] = 'ENTERED'
                try:
                    code = process.wait()
                    state['raw_wait'] = code
                    if type(code) is not int:
                        raise RuntimeError('actual terminal wait result')
                    state['wait'] = 'COMMITTED'
                except BaseException as error:
                    state['errors'][2][0] = error
                    state['errors'][2][1] = (
                        BaseException.__dict__['__traceback__'].__get__(
                            error, BaseException))
                    state['wait'] = 'UNKNOWN'
                    state['unknown'] = True
            else:
                state['unknown'] = True

        for error_slot, stream_index in ((3, 1), (4, 0)):
            row = state['streams'][stream_index]
            if row[1] == 'OPEN_ENTERED':
                row[1] = 'UNKNOWN'
                state['unknown'] = True
            if row[1] != 'OWNED':
                continue
            row[1] = 'CLOSE_ENTERED'
            try:
                row[0].close()
            except BaseException as error:
                state['errors'][error_slot][0] = error
                state['errors'][error_slot][1] = (
                    BaseException.__dict__['__traceback__'].__get__(
                        error, BaseException))
                row[1] = 'UNKNOWN'
                state['unknown'] = True
            else:
                row[1] = 'CLOSED'

    for error, traceback in state['errors']:
        if error is not None:
            raise BaseException.with_traceback(error, traceback)
    if state['unknown'] or state['wait'] != 'COMMITTED':
        raise RuntimeError('common-runner retirement remains unknown')
    return code, peak, stop
```

Replace the entire original capture/launch/monitor block at lines 353–374 with:

```python
        code, peak, stop = run_group_capture(
            timed, stage, env, folder, runner_start, cap, spent)
```

Keep the preceding `start = time.monotonic()` and subsequent elapsed-time, log finalisation, usage, source-currentness, and receipt code in their existing order.

This retains the original threshold order, sampling function, 50 ms delay, stop labels, and return-code interpretation. The primary error occupies the first fixed slot before retirement. Signal, wait, and capture-close errors retain their actual objects and tracebacks in operation order. Uncertain acquisition or retirement cannot return a success tuple. There is no numerical fallback signal after lost ownership, no retry after an uncertain wait, and no new artifact or service.

“Once” here means one explicit entry into the existing `Popen.wait()` or file-close interface. It does not invent a guarantee about the number of internal kernel calls in the selected CPython implementation.

### Binding and protocol consequences

This is a declared retirement-order change under the authorised common supervisory amendment. It is **not** covered by the ancestor’s two entry/path substitutions alone.

Freeze the changed common R, update the supervisor’s immutable runner pin, both stage manifests, command/profile and packet bindings, and the common-runner inverse description. Preserve the current waiting-entry bytes, factory/cwd repair, native/compiler subjects, and scientific member identities. When the genuine primary baseline is adopted, it must select the same common R and establish the same actual wait-ownership launch condition at its real parent.

The parent-command wall and CPU-through-validation endpoints remain unchanged. The new observation work and retained custody are charged inside that interval. Nested GNU-time fields remain diagnostics and are not added again to enclosing totals. Group RSS remains a sampled metric, not a proof of instantaneous peak or complete numerical fit.

## 5. Decisive changed controls

These should use the actual new function with clearly labelled inert filesystem, process, wait, signal, and clock ports. None requires a genuine owner or child launch.

| Control | Required discriminator |
|---|---|
| Recycled PGID | In a deterministic kernel-state model, the published consuming poll frees `q`, allowing unrelated U to acquire it before final `killpg`. The corrected function must signal before its consuming wait and never signal after reuse. |
| Normal and original refusal | Terminal cases returning 0 and 1 retain those codes and unchanged stop labels. The real receiver still distinguishes original optimized refusal from envelope failure. |
| Working P, signal E, wait S, and close failures | Raise distinct objects at each boundary. P remains raised; E, S, stderr-close, and stdout-close remain in that order with their traceback objects. Each retirement interface is entered once. |
| Lost wait ownership | `ChildProcessError`, a mismatched PID, or an invalid terminal observation causes no numeric signal or consuming wait and yields no successful result. |
| Partial opening or uncertain launch | Failure opening stderr closes known stdout once. Uncertain `Popen` return produces no reconstructed PID. Earlier errors survive later close errors. |
| Cancellation and binding | The original cap decision leads to one group signal before wait. Both selected stages and the authentic caller select the exact changed R; scientific members, factory/cwd, timer, and release bindings remain unchanged. |

The counterexample is established by source reasoning now. These are proposed regressions, not reported passes.

## 6. Whole-activity disposition and next exit

The process-group question has a concrete answer. **Inherited membership is compatible with the inspected original relational control, but the selected common runner’s post-reap numeric signal is unsafe. Repair that owner rather than toggling the native launch flag.**

The next implementation should contain this retirement correction, its caller integration, its exact binding updates, and the discriminating controls in one immutable revision. Independent review should then accept or reject the retained-child signalling lemma against the actual changed functions. No unchanged timer suite needs to be rerun simply to add evidence counts.

The following boundaries remain separate and cannot be credited by this repair.

- **Complete original coverage.** Reconcile the remaining exact helper/context bodies, including the identified unread cache/authority variants, against their actual selected callers. The inspected relational group control is not a universal 52-body/65-context theorem.
- **Native and compiler qualification.** Reuse the unchanged conditional proof only for its selected Linux, security, filesystem, compiler, and interval subject. Actual image/configuration association remains unissued.
- **Genuine primary baseline and comparison.** Adopt #6837/#6847 through the real common parent, preserving the genuine PR #6029 baseline, typed independent transfer, original anchors, and complete comparison protocol.
- **Retention and successful CLOSE.** Preserve the existing genuine registry/G seal and retention path. Adopt #6762 through the actual caller/role/source tuple before claiming successful formal CLOSE.
- **Funding, fit, and execution.** Complete current cost coverage and admission remain S10.04/S10.05 gates. This source argument supplies neither a current balance nor a wall/CPU/RSS bound.

**The current published subject remains NO-GO for the required signalling invariant. The connected correction above is a source-construction route, with a falsifiable acceptance check. Neither it nor this consultation completes S07.04, qualifies execution, or demonstrates an optimisation.**