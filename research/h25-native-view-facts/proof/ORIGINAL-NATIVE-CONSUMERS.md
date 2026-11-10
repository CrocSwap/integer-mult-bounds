# Native-entry invariants at the actual original consumers

This construction reuses the existing 31-function map, `outputs/caller-observation-closure-20261106T2252Z/review/original-cases/FUNCTION-PINS-v1.json`, SHA256 `a85400c0261568a7bbdf14ddd0083d9754c7b27446f20c8f7fa3f2d24d290fe4`, and its finite case map, SHA256 `23677e5924e72e9d76a16c1d6026120ee90ab6780911847bc2f8b96d0983cdc0`. No original case census is repeated or context count changed. The original 52 body / 65 context map remains the exact predecessor record at `be1b2fd75556f2f4bbe73cfa63ef0fcd7a9e3dcd4bbd7166ebf5dd68cf2a7653`.

All stage paths below are relative to the predecessor's `implementation/bindings/stages/joined-full-candidate-v1`. Its immutable scientific bodies are read only. The entry subject is the actual C hash `60af72915efea62f46ea376e2ba7ed0c616f99b09ca1beec0f4b0d8173609410`. The source invariants N1–N9 are in `NATIVE-ENTRY-INVARIANTS-v1.md`.

## C1. Namespace UID/GID representation does not falsify these stat consumers

**Hypotheses.** A selected original read path still resolves to its same backing regular inode through the copied view; no relevant source bytes, inode attributes or original custody interval has changed. The selected native reader executes the same captured primitive. This is a concrete file/path relation, not an assumption that its original predicate returns true.

**Conclusion.** A change limited to the user-namespace representation of inode UID/GID cannot change the following consumers' stat predicate, hash value or first stat/hash refusal. Their actual source never reads the affected UID/GID fields.

**Derivation.** Define the projections exactly as the source defines them:

- Root `integration/full_driver.py`, `_fingerprint` at line 476 and `_hash_regular` at lines 480–507, uses `(dev, ino, size, mtime, ctime)`, separately requires regular-file type and bounds, hashes the actual bytes and verifies the same projected tuple after reading.
- Provider `integration/probe_binding_v3.py`, `_fingerprint` at line 242 and `_hash_regular` at lines 246–273, uses that same projection and separate type/size/hash checks. Its `_audit_files` at lines 290–294 compares actual byte hash and count for the runtime/header/binary triples; it does not compare an expected root UID.
- `areas/cache-validity/probe-native/native_tcb_v1.py`, `_fingerprint` at line 125 and `_hash_file` at lines 129–154, adds mode to the projection and returns the actual device/inode/mode/times/hash/size record. It has no UID/GID field in this fingerprint or returned file record.
- `integration/native_packet.py`, `_file` around lines 137–155, compares device/inode/mode/size/times and returns hash, bytes and permission mode; `_dependencies`, existing function-map row 1, then compares the declared hash and size.
- `integration/cold_build_evidence.py`, `_fingerprint` at line 33 and `_snapshot`, existing map row 11, use device/inode/mode/size/times. The reader/writer equality test uses the actual device/inode and regular-file type, not a UID representation.

The copied mounts retain the same backing objects; read-only/nosuid are mount attributes and do not rewrite the inode's mode or contents. Therefore each displayed projection is unchanged by UID/GID representation alone. Applying the same byte reader then gives the same byte sequence and digest or the same original content/bound/stability refusal. This proves the stated local implication directly from the fields actually used. It does not assert that every copied ACL or every native security effect is harmless.

The supplementary exact source pins read back for these reached callees are:

| Source | SHA256 |
|---|---|
| Root `integration/full_driver.py` | `f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0` |
| Provider `integration/probe_binding_v3.py` | `9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2` |
| `native_tcb_v1.py` | `865943df5cfdbf9383362d7fb2b76c6d0fd895cf0a0e20d550a26b579606b5d7` |
| `native_tcb_controls_v1.py` | `63b1804caa7f89915662a1424f788c3becad13520e1f63212a338fb45aaa2c5a` |

These callee pins are already literal authenticated dependencies of map row 16, `_initial_native_tcb`. Recording the concrete field use does not create additional original contexts or replace its original source checks.

## C2. Actual native mapping/header checks remain genuine within each invocation

**Hypotheses.** The same selected Python/native image and startup loader closure are executed through the final view; the actual source/native qualification supplies their factual association. File-backed executable mappings are not changed during the original audit interval. The read relation in C1 holds for the declared files and headers.

**Conclusion.** The initial-TCB helper's mapping/current-file consistency proof and provider's runtime/header checks use genuine current objects after the entry, rather than a declaration from the entry or a historical inode constant.

**Proof.** The helper reads `/proc/self/maps`, parses actual executable file-backed mappings, requires their exact path set to equal the declared inventory, reads each actual file and compares its actual device/inode to the corresponding mapping rows, then reads mappings again and requires before/after equality. N1's successful exec removes the entry's old address space; N2 leaves no native image FD behind. N4 establishes the protected task-root reference. Nothing in the entry injects a Python module or supplies a substitute mapping record. The provider's `/proc/self/exe` is the actual executed Python object, and `_audit_files` calls the same original readers on its literal runtime/header triples.

ASLR addresses, module IDs, timing samples and actual PID fields are preserved as genuine raw observations of their own invocation. This proof does **not** rewrite those receipts, assume historical cross-invocation addresses are equal or replace the original observation relation with universal byte equality of unrelated runtime diagnostics. The main theorem must apply the original consumer projection; this lemma establishes the exact source/current-object checks that projection reaches.

The same interpreter pathname, image bytes, source/stdlib selection, argv and environment also preserve the inputs to original `sysconfig` suffix/include evaluation. The entry changes no Python configuration source, PATH, locale, TMPDIR or argv element of the original trailing command. The original suffix/header equality test is still performed by `native_packet.prepare` (map row 2); it is reused, not replaced by a second implementation. Actual exec/security success and each compiler command's resolution are separate derived steps, not consequences of the suffix check alone.

## C3. All five early initial-TCB controls retain their actual boundaries

**Hypotheses.** C1–C2 and the ordinary artifact read/write/create/close/unlink relation hold for the original exclusively created `output/initial-tcb-controls` directory. The original pristine Root primitive identity relation holds. These hypotheses identify the exact operation and ownership relations; they do not assert the expected control result.

**Conclusion and proof by the unchanged control branches.** The source-pinned `native_tcb_controls_v1.run_controls` performs:

1. **Positive native closure.** Its unchanged helper obtains the actual mapping/file agreement proved in C2, so the original status/count/private-ABI assertions observe that genuine agreement.
2. **Wrong file digest.** The control flips one expected digest character without changing the actual bytes. C1 gives the same actual digest, hence the unchanged digest comparison raises the original `file digest differs` refusal.
3. **Missing declared map.** The control removes one declared file while C2's actual mapped-path set still contains it. The set comparison therefore fails at the original `mapped file closure differs` boundary, before file hashing.
4. **Root hash alias.** The control substitutes the original forbidden Python function into Root's hash alias. The unchanged pristine-Root identity check rejects that changed alias before the forbidden function executes, then the control restores the actual old reference. No native UID or mount flag enters this identity predicate.
5. **Isolated reader drift.** The control creates its own fixture inside that directory, reads a chunk, truncates the same fixture to one byte through another writable descriptor and then checks the original fingerprint/count. The changed size makes the unchanged reader reject `file changed during hashing`; its finally block unlinks the fixture. N6 grants write/truncate/unlink inside the artifact tree and N7 admits those syscalls. The control does not mutate a system native file or its mapping.

This is a source derivation of these five existing cases, not a control execution. It also explains why the optimized full entry must retain early output creation: `_initial_native_tcb` (map row 16) and these controls run before `_epoch_sc4_full_entry` rejects optimization. N3 keeps the science leaf absent for that original exclusive mkdir. No entry-side optimized refusal is added.

## C4. Genuine task census and the original live-thread refusal

**Hypotheses.** The original branch starts with the selected single Python task, and ordinary selected glibc/Python thread creation has its stated native behavior and resources. N1–N7 hold.

**Conclusion.** `cold_build_evidence._one_thread` (map row 8) still observes genuine task identities: it accepts exactly the original one-task state and rejects the original actual worker-thread fixture before Popen. No inevitable UID/PID mismatch is introduced by the entry.

**Proof.** That function lists `/proc/self/task`, rejects on a second entry, and compares the remaining name with `str(os.getpid())`. It does not inspect UID/GID, parent namespaces or the host process census. The entry creates neither a PID namespace nor an extra task. Its final exec replaces the already launched process. Its exact clone policy allows the selected ordinary thread fallback, rather than denying all clone. Consequently a real second worker remains a second actual proc task, and the original `len(tasks) <= 1` guard remains the first helper refusal. The original control still owns setting and joining that worker in its finally block. This argument is separate from the private-user-namespace representation of an unrelated inode owner.

`Phases.memory` at scientific-driver lines 349–362 reads `/proc/self/status` but consumes only the `VmRSS` row, its kB unit and the actual self `getrusage` high-water value. It does not compare proc Uid/Gid/Groups text. The entry leaves this genuine proc filesystem and PID namespace in place. The diagnostic values need not be numerically identical to an unrelated fresh run; their cost/fit and original comparison role remain unchanged and paid.

## C5. The helper's child-only FSIZE and group relation is constructive

**Hypotheses.** The actual inherited FSIZE tuple satisfies the original helper's `>= 16 MiB` precondition. The original preexec closure and pristine resource builtins retain their identities. The selected process primitives have their ordinary semantics. N1–N7 hold.

**Conclusion.** The helper can install its exact `(16 MiB, 16 MiB)` tuple in the child while its original parent tuple and process group remain unchanged; the native entry does not replace this with a different compiler contract.

**Proof.** `_limit_callback` and `_check_limit_callback` (map rows 9–10) capture resource ID 1 and the immutable tuple before launch, then validate actual closure/default/code/builtin identities. The new seccomp resource filter admits every self `setrlimit` whose resource is not CORE, including resource 1, and admits self prlimit queries/mutations for that resource. The entry itself changes no FSIZE tuple. The child callback is used by the original `Popen(..., start_new_session=False)`, so it does not create a new group/session. The entry also creates neither, and no PID namespace is introduced. The source's original child-limit/group control therefore keeps both its actual child readback and actual unchanged-parent assertions.

This does not give the GF2 or trace producers a 16 MiB child contract: neither calls this helper. Their separate PIPE/text/90-second contracts remain exactly as the existing map states.

## C6. Original evidence contracts and negative operation classes remain distinct

The following is a source composition rule, not an assertion that every possible compiler succeeds. Given a proved relation for the concrete exec/loader/security/creation operations of one row, use that row's actual consumer. Never replace it with another producer's evidence behavior.

| Original source owner and map rows | Existing evidence order that the native proof preserves | Actual negative consequence |
|---|---|---|
| Metadata `native_packet.prepare -> cold_build_evidence.run`, rows 1–4 and 8–12 | Intent, journal and exclusive regular raw files precede Popen; actual poll/wait and bounded snapshots; original primary rethrow plus ordered secondary close/evidence notices | Nonzero is original CalledProcessError; startup retains spawn entered/returned distinction; timeout/overflow prefixes stay non-final until the original outer owner retires the forest |
| GF2 `native_backend.build_native`, row 5 | Separately evaluates sysconfig CC/shlex, uses PIPE/text/timeout 90; writes build.json only after subprocess.run returns | Startup/timeout/decode exceptions occur before build.json; nonzero writes it first then raises the original native compilation requirement |
| Trace guarded authority -> `adapters.build_encoder`, rows 6–7 | Independently evaluates its own sysconfig CC/shlex; preserves PIPE/text/timeout 90 and source checks | Keeps its distinct first check and RuntimeError; does not acquire the GF2 producer's explicit empty-compiler check or metadata helper's raw-file journal |
| Separate toy `command_for/run_case/closure_identity_case`, rows 13–15 | Original explicit Python child constructor, actual raw bytes including NUL/non-UTF8, separate queue/context placement | Normal, nonzero 7, timeout, oversized log, missing executable, live thread, child limit/group and closure-identity outcomes retain their original consumers and multiplicities |
| Final original/outer consumers, rows 18–20 and 25–27 | Original main finally/STOP/late-last checks precede genuine terminal validation; actual wait and complete EOF/retirement remain required | No early receipt or new native setup failure can stand in for final original disposition; N8 proves the native exit-78 exclusion |

For the toy startup case specifically, the command is the absent absolute path beneath its fresh output. The selected kernel's path lookup returns ENOENT before any format handler receives file bytes. The new filter permits execve and the relevant ancestors are in the declared artifact view, so this case needs the ordinary lookup/permission relation, not a fictional invalid-format handler comparison. The exact binary-format equivalence proof remains necessary for real executable/helper paths.

## Scope of these constructed consequences

C1–C6 discharge useful local steps: the actually observed stat fields, genuine proc task relation, five early TCB controls, child-only FSIZE/group behavior, distinct evidence owners and setup-error classifier. They do not add an absence-of-ACL preflight, strip metadata, normalize raw receipts, assume every compiler path equals the absolute metadata GCC path, or claim the two outer commands run all 65 separate original contexts.

The exact executable/helper/spec/interpreter and security/creation/fault/topology relations are inputs from the parent/Pro finite model, interpreted at the original native qualifier and genuine owner. Source construction is active; no current environment, kernel feature, runtime fit, control/science execution, whole S10.03 acceptance or original credit is claimed here. No actual failed native proof step in these consumers currently demands a C change. The prospective simpler kernel model being discussed by Pro is evaluated separately and has not been applied to the frozen C subject.
