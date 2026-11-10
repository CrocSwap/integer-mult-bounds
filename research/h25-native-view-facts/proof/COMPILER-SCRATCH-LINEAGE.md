# The selected full caller installs its compiler scratch environment

This lemma concerns the immutable full scientific driver already identified by row 17 of the existing 31-function map. No case census, compiler, import, probe or runtime observation has been performed. It corrects the proposed inference from the runner's initial six-key environment to the environment actually inherited by the compiler children.

## Source facts and conclusion

The runner starts the original command with `env = dict(LAUNCH_ENV)` and no TMPDIR key. That fact is correct. It does not imply that a compiler invoked later by the Python program has the same unmodified mapping: the selected original program changes its own `os.environ` before invoking any of the three compiler families.

In `integration/scientific_driver.py`, `main_epoch` performs the following ordered original operations:

- Line 951 selects `compiler_tmp = output / 'compiler-tmp'`.
- Line 952 exclusively creates that directory with the original `mkdir`.
- Line 953 sets `os.environ['TMPDIR'] = str(compiler_tmp)`.
- Line 1027 invokes `native_packet.prepare` for the three metadata builds.
- Line 1030 invokes `backend.build_native` for the GF2 build.
- Line 1052 invokes the authenticated guarded-adapter preparation which reaches the original `adapters.build_encoder` for the trace build.

The older function retained in the same immutable file has the same ordering at lines 453–455 and 543/548/574. The selected original `main_epoch` is not inferred from that older function: its own body contains the concrete operations above.

Neither `cold_build_evidence.run`, `native_backend.build_native` nor `adapters.build_encoder` supplies an alternate `env` to its subprocess call. The metadata helper's `Popen` and the two separate PIPE/text producers' `subprocess.run` therefore inherit the **then-current** process environment, which contains the original program's TMPDIR assignment. This proves that the caller supplies the same scratch directory to all three selected compiler families. It preserves their different commands, evidence and timeout contracts; it does not route them through a new common compiler wrapper.

The early optimized full refusal does not enter `main_epoch` and does not execute these compilers. Its initial native-TCB controls create only their own fixture, as shown in `ORIGINAL-NATIVE-CONSUMERS-v1.md`. The separate eight cold-build toy cases use explicit Python children, not these GCC compilation paths. The unchanged source/context map still determines which other original contexts pass through the view; this lemma does not make two outer invocations execute every separate context.

## Relation to the actual native view

The `output` leaf is beneath the declared artifact parent. The compiler-tmp directory is consequently beneath that same writable clone. The entry's artifact Landlock rule grants the needed directory/file create/read/write/remove rights and its syscall policy admits those operations. The same-ID mapping keeps the underlying creator UID and permission checks; source/hash/header inputs elsewhere remain readable through the copied root.

For a selected ordinary local-filesystem/security model in which this original mkdir yields the intended caller-owned searchable/writable scratch directory, the new mount boundary does not itself make that directory read-only. No `/tmp` writable clone or new environment mutation is required merely because the **initial launcher** environment lacks TMPDIR.

The remaining actual compiler consequence is precise: derive from each selected GCC/helper/interpreter implementation that its temporary-file choice uses the provided usable TMPDIR, or enumerate any independent fixed scratch path it actually reaches. A wrapper that ignores TMPDIR is not certified by the caller assignment, and an unusable TMPDIR can have an original fallback whose preservation needs its own argument. These are concrete compiler/permission cases in the existing finite model, not evidence that the current caller inevitably uses `/tmp`.

No broader host write exception should be introduced on the incorrect premise that the original full driver never sets TMPDIR. The constructive starting point is the existing original assignment, its artifact-path lineage and the actual selected compiler's temporary-path algorithm. The scientific source and original environment semantics remain unchanged.
