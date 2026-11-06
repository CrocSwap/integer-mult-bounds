# Private binary-format dispatch ownership

The proposed native entry now creates an empty `binfmt_misc` instance in its fresh user namespace before building its filesystem view, dropping privileges or starting a descendant. This shadows inherited miscellaneous binary handlers, including handlers that retain an interpreter file opened before the new filesystem view existed.

The entry reserves a descriptor slot before `fsopen`, records the actual descriptor immediately, calls `fsconfig(FSCONFIG_CMD_CREATE)`, and retires the context exactly once. A create error remains primary if close also fails. An uncertain close stops setup and is never retried. No visible registry mount is created. Existing descriptor, error and report caps remain unchanged. The final syscall allowlist continues to deny filesystem-context creation, mount changes, namespace creation, registration writes and descriptor import.

This is a proposed source repair with independently reviewed source and eight passing mock-control groups. The actual entry source was compiled inside a harness whose main reaches only the new owner and its real descriptor/error machinery. Syscall and close boundaries were mocked. The production entry main, namespaces, handler operations and scientific caller were not executed. Complete caller acceptance and any measured optimization remain open.

## Selected source premises

The source profile selects the Linux v6.12 semantics and `CONFIG_BINFMT_MISC=y` with successful filesystem registration. This avoids module-request delegation during `fsopen`. It is a prospective selection, not an observation about the current host. The empty namespace instance is published during filesystem creation and survives disposal of its unattached superblock until user-namespace destruction. A create operation can have partially published state before a later security-hook error; such a failure terminates setup and cannot be called an original scientific refusal.

Primary sources: [miscellaneous binary loading and instance creation](https://github.com/torvalds/linux/blob/v6.12/fs/binfmt_misc.c), [filesystem-context operations](https://github.com/torvalds/linux/blob/v6.12/fs/fsopen.c), [context release](https://github.com/torvalds/linux/blob/v6.12/fs/fs_context.c), [filesystem lookup and module request](https://github.com/torvalds/linux/blob/v6.12/fs/filesystems.c), and [namespace disposal](https://github.com/torvalds/linux/blob/v6.12/kernel/user_namespace.c).

## Lineage and exact scope

Original investigation: [PR #6321](https://github.com/CrocSwap/integer-mult-bounds/pull/6321). Original full caller and criteria: [PR #6744](https://github.com/CrocSwap/integer-mult-bounds/pull/6744) at `1ac58a84b725bd6f17eec66727edc877c49c7e66`. Direct predecessor: [PR #6818](https://github.com/CrocSwap/integer-mult-bounds/pull/6818) at `1479ccf2ec0bc29b7bf741a2d613d79e1f9ec19e`.

The predecessor owns the corrected original optimized-refusal classification and connected caller sources. This package changes its existing native entry; it does not add another caller or replace original scientific bodies. The exact native delta is included. The original fixed helper and context coverage, resource limits, normal output oracle and optimized refusal oracle are preserved. The predecessor's accepted refusal controls were retained and were not rerun for this repair.

Related work is reused at its exact recorded scope: [native selection #6715](https://github.com/CrocSwap/integer-mult-bounds/pull/6715), [parent ownership #6736](https://github.com/CrocSwap/integer-mult-bounds/pull/6736), [metadata consequence audit #6780](https://github.com/CrocSwap/integer-mult-bounds/pull/6780), and [later close component #6762](https://github.com/CrocSwap/integer-mult-bounds/pull/6762). The provenance record lists inspected commits and concrete reuse decisions. Bounded all-author, all-state PR title/body searches found no `binfmt_misc` or `FSCONFIG_CMD_CREATE` counterpart; this does not prove global code novelty.

## Reproduction and evidence boundaries

`source/science_view_entry.c.txt` is an inert exact source snapshot. The contract and profile describe its selected semantics. The original authoring-status file preserves the controls' initially unexecuted state. The later actual evidence records the sole admitted compile and mock run: both returned zero; the mock run had empty stdout and stderr. All eight fixed control groups passed. Compilation retained three pre-existing `-Wmisleading-indentation` warnings (3,252 bytes), not a warning-free result. The command used `-Wall -Wextra -Werror=implicit-function-declaration`. `review/` records independent source findings and their exact inputs. The guard, exact compiler/source identities, raw captures and results are retained under `evidence/`. The conservative policy charge was 24 seconds, including compile and mock-run allowances; full physical costs remain open. No replay registration is supplied for this unqualified production native source.

After obtaining this package, run `python3 -B research/h25-private-binary-dispatch/verify_integrity.py` to check package membership and hashes only. This command neither imports the native caller nor executes its controls. Full caller dependencies remain in the exact predecessor package and its explicit external-input map; this contribution does not claim a self-contained cold science replay.

## Open next questions

1. **Required execution behavior.** Prove that removing inherited miscellaneous handlers preserves each original GNU-time, Python, compiler/helper, script and failed-exec observation. Exact executable bytes do not establish which handler would have run. The smallest next check is a finite source-selected dispatch map joined to the genuine parent association; it is blocked by the absent consequence owner.
2. **Fault results.** Establish the affected original fault observations under the entry's existing `CORE(1,1)` profile, including GNU-time diagnostics and compiler-child wait status. A Python signal return code alone omits core-status consequences. This requires the actual consumer chain, not an assumed current host setting.
3. **Creation and filesystem effects.** Join exact topology, permission and LSM creation/exec consequences to the same original caller. Subject hashes and metadata equality alone do not prove the new confinement preserves those consequences. Current kernel/images, actual association, numerical fit, funding and execution follow only after complete source acceptance.

A helper or a delivered PR does not satisfy these complete-caller obligations. No performance claim, original full-data equality, supplier qualification or complete physical cost account is made. Preparation, consultation, agent review, reporting, publication and historical timing gaps remain `OPEN_NOT_ZERO`.

## Credit

Prepared for Clear1nsight with substantial OpenAI Codex and ChatGPT Pro assistance. Retains the predecessor native entry and its ownership, error and confinement machinery. Contributions are under the repository's Apache-2.0 license. Independent AI source review is distinct from human review, executed controls and runtime qualification.

To reproduce just the mocked owner check, restore the two inert sources into a temporary directory with their original relative layout: `implementation/native/science_view_entry.c` and `controls/native-dispatch/dispatch_control.c`. Compile the control file using the recorded GCC command and then run that control executable under appropriate local limits. Its include must resolve to the exact supplied entry bytes. Do not run the production entry as this control. Current-host kernel behavior and complete caller qualification are outside this command.
