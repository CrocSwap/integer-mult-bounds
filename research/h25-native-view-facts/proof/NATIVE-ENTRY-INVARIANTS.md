# Constructed invariants of the actual native entry

The subject is `outputs/native-dispatch-closure-20261106T2206Z/implementation/native/science_view_entry.c`, SHA256 `60af72915efea62f46ea376e2ba7ed0c616f99b09ca1beec0f4b0d8173609410`. Its hash was read back in this round. The predecessor remains closed. No C source change, import of a project module, control, compiler, native operation, kernel/host/policy/namespace probe or protected runtime read is performed by this proof construction.

These are reusable source lemmas, not an assertion that the complete theorem already follows from a profile. They give the entry's actual transition relation and positive consequences for specific original consumers. The independent kernel lemmas supply the indicated primitive semantics; the parent/Pro construction composes the finite dispatch, security, filesystem and original-observation theorem. No compiler receives an exemption or an assumption that its arbitrary effects are harmless.

## Subjects and interpretation

Let `t` be the authentic freshly launched entry task. Let `A` be the actual artifact-parent inode, `U` the actual usage inode, and `C` the actual cwd path and inode passed by its genuine runner. Let `M` be the copied mount namespace and `N` the new one-ID user namespace. Let `S` be the native FD registry. A registry slot records a custody operation, so the initial FD0 adoption is counted even though it is not a newly allocated kernel FD.

For a trace of the C source, define `Ready` to be the program point immediately before its final `execve` at line 714, reached with `okay == true`. Define `SetupError` to be its non-exec exit path. A killed, interrupted or unobserved process is not assigned `Ready` or completed cleanup by this definition. Actual process exit, relay EOF, forest retirement and owner release remain observations of the original outer owners.

The native primitive hypotheses used below are the precise selected Linux v6.12 syscall semantics, actual entry/native-image association, and the original trusted setup interval. For the partial-correctness lemmas, a successful syscall means that specific native call actually returned successfully, not an externally supplied success flag. A whole proof of admission/success for an environment must derive those outcomes from its concrete native/resource/security facts. It cannot insert the desired observation equality as a premise.

## N1. Success is dominated by every mandatory setup owner

**Hypotheses.** The actual code executes with ordinary C short-circuit semantics and the selected native primitives; execution reaches `Ready`.

**Conclusion.** Native start, exact argv validation, CORE installation, entry/time authentication, namespace entry, private dispatch creation/close, view construction, capability removal, Landlock installation, known closure, final FD census, final time reauthentication and seccomp installation all completed successfully in that order.

**Proof.** In `main` at lines 686–714, every producer of a later phase is guarded by `okay`. Every mandatory function result is conjoined into it; no assignment later changes a false `okay` back to true. At the three `close_all` boundaries, either an error or uncertainty forces false. The final `execve` is inside the last `if (okay)`. Consequently no failed setup branch can skip its failure and enter science through another call site. The C source contains no task creation call and no other successful exec path. The successful process replacing this entry is the exact GNU time path and argv prefix checked by `argv_shape` at lines 672–684, with the original trailing command passed unchanged and `environ` passed through rather than rewritten.

This is a useful dominance result even when setup can fail: the failure is an actual paid setup error, not a scientific refusal invented by the entry.

## N2. Descriptor ownership is monotone and unknown close cannot become success

**Hypotheses.** The actual source begins with its statically initialized registry and executes its explicit native FD operations. A negative acquisition has the selected syscall's negative-result/no-returned-FD semantics.

**Conclusion.** Every setup FD is reserved before acquisition and recorded immediately on return. The only descriptor state transitions are `PENDING -> FAILED` or `PENDING -> OPEN -> RETIRED -> CLOSED/UNCERTAIN`. A numeric FD is never closed twice by this registry while ownership is uncertain. At `Ready`, the actual descriptors are precisely the reestablished FD0 and original two pipe writers.

**Proof.** `reserve`, `acquired` and `close_once` at lines 117–137 define those transitions directly. Before the native close, `close_once` changes `OPEN` to `RETIRED`; an error changes it to `UNCERTAIN`, records the actual errno and sets the global uncertainty bit. `close_all` at lines 138–142 selects only `OPEN` setup FDs above 2. It therefore cannot retry an uncertain integer, including one the kernel might already have closed. A close failure causes the owning function to return false or is caught by the subsequent mandatory error/uncertainty barrier. There is no later native acquisition on such a failed setup route.

The initial census in `native_start` rejects every inherited FD above 2 except its own registered census descriptor. FD1 and FD2 must be distinct blocking FIFO write ends. FD0 must be the exact major/minor `1:3` character sink opened read-only. No source function closes FD1 or FD2. During stdin replacement the fresh sink is opened while old FD0 is still occupied; old FD0 is then explicitly retired and once-closed before the successful `dup3` to 0. Hence an unrelated setup acquisition cannot silently occupy a standard slot. All other known setup holders are closed before the final census, and the one later time-image FD is also once-closed before `Ready`.

The two pipe writers are genuine runner-created capabilities by the original launch owner, not authority inferred from inode type alone. The C source independently validates their native shape and excludes a regular capture or control socket. Failure records preserve raw errno sites and custody states; they cannot establish final exit or release.

## N3. Exact object authority and backing identities survive the view

**Hypotheses.** The authentic runner has created `A` and `U` and supplied their actual native device/inode observations. Execution reaches `Ready`.

**Conclusion.** `A` was an empty, caller-owned `0700` directory, `U` an empty, caller-owned `0600` single-link regular file, and the science leaf was absent. The view's writable clones expose those same actual backing objects at those exact paths. The final cwd has the original pathname and backing identity. FD0 names the same genuine devnull backing object through the final view; its original open file description has been replaced and closed with explicit custody.

**Proof.** `validate_owned_paths` at lines 438–464 uses canonical absolute paths and no-symlink/no-magic-link `openat2` resolution, compares actual descriptor observations with the supplied device/inode values, checks modes/types/ownership/emptiness and requires `ENOENT` for the absent leaf. No caller-supplied FD is admitted. `make_view` at lines 466–493 opens the clone sources only after namespace copying, creates exactly the two detached clones and installs each on its actual opened target. Its final stat comparisons retain device, inode, mode, ownership, link, size and modification/change time fields. It reopens cwd through the final paths and restores its exact string.

`reestablish_stdin` at lines 412–436 retains the actual device/inode/rdev/type/mode relation while accounting for UID/GID representation across the namespace. It preserves O_RDONLY, NONBLOCK status and CLOEXEC clear. Its new FD0 avoids the old devnull mount reference without pretending to preserve an arbitrary stdin OFD. The selected genuine devnull producer has no shared-position or OFD-identity consumer. This restriction is a fixed launch contract, not a new scientific-input test.

The cross-user-namespace object comparison at lines 183–187 treats only UID/GID representation specially. Each native image hash separately checks full stable owner fields in its own context. Device/inode/mode/link/size/timestamps and complete image bytes are still compared, so this does not normalize a raw original receipt or waive original owner association.

## N4. The root reference is itself protected, including self proc links

**Hypotheses.** The selected kernel implements the successful unshare and mount-attribute operations used by this entry; `Ready` is reached.

**Conclusion.** The task's own filesystem root is a copied mount whose attributes were changed in place to read-only and nosuid. Its own `/proc/self/root`, including O_PATH/openat aliases, does not reintroduce the parent's writable root mount.

**Proof.** This is proved in `ROOT-REFERENCE-LEMMA-v1.md`, including the exact `ksys_unshare -> unshare_nsproxy_namespaces -> create_new_namespaces -> copy_mnt_ns` filesystem-structure argument. The current C implementation does not overmount a full new root; only `A` and `U` are attached as writable exceptions. A chroot correction is therefore not demanded by this proof step. This self-reference argument is separate from the ancestor-task ptrace/capability argument.

## N5. The private dispatch owner prevents ancestor-handler recovery

**Hypotheses.** The selected built-in registered Linux v6.12 binfmt_misc implementation is genuinely associated; the entry reaches `Ready` without an external entrant or export during trusted setup.

**Conclusion.** Its current user namespace owns an empty binfmt_misc instance; ancestor registrations, including preopened F interpreters, are not selected by its later misc-format lookup. No visible mount or surviving fs-context FD was created. Science cannot reconfigure or import another registry through an admitted interface.

**Proof.** N1 establishes successful `create_private_binfmt_dispatch` at lines 371–397 after namespace creation and before view/drop/descendants. That helper owns one actual `fsopen`/CREATE/once-close sequence. Under the selected primitive lemma, the first successful CREATE publishes an empty namespace-local instance which survives context close until namespace destruction. Final default-deny seccomp does not admit fsopen, fsconfig, fsmount, fspick, setns, unshare, mount APIs or descriptor-transfer interfaces. No registry mount is attached. Existing copied registry paths are read-only and receive no Landlock write permission.

This conclusion is confinement, not automatic exec preservation. The original environment's finite ordinary/misc dispatch outcomes still need to be related to this empty lookup. No claim that every compiler or every Linux format is unaffected is used. If CREATE fails after partial publication, N1 prevents `Ready`; the helper records its actual error before the one close and leaves actual namespace retirement to the existing outer owner. It does not label that setup error an optimized scientific refusal.

## N6. Post-exec rights are explicit and inherited

**Hypotheses.** `Ready` is reached; subsequent primitives have the selected cap/NNP/Landlock/seccomp inheritance semantics.

**Conclusion.** The branch has empty effective/permitted/inheritable capability sets, cleared ambient and recognized bounding sets, locked NOROOT/NO_SETUID_FIXUP securebits and NNP. It has explicit global read/execute rights, artifact write rights, exact usage write/truncate rights, the exact devnull sink exception and the two inherited pipe writers. It has no ordinary content-write or metadata-mutation authority over source, captures or administration through the copied mounts. Later process creation cannot select another user/mount/cgroup namespace through an admitted clone tuple or syscall.

**Proof.** `drop_privilege` at lines 495–514 installs and reads back the capability/NNP state. `install_landlock` at lines 520–542 handles the complete selected ABI6 filesystem rights, both TCP rights and both scopes. Its four actual inode/path rules are: root READ/READ_DIR/EXECUTE; `A` ordinary file/directory/symlink/FIFO write/create/remove/REFER/truncate; `U` read/write/truncate; devnull read/write/ioctl subject to the final six-request filter. No network or broader write rule is added. Mount attributes enforce metadata writes outside the two clones; Landlock is not falsely credited with confining chmod/xattr/timestamps by itself.

`install_seccomp` at lines 563–644 rejects alternate architectures and x32, gives clone3 ENOSYS and allows exactly the normalized low32 legacy tuples `003d0f00`, `00004111` and `01200011`. Ordinary fork/vfork retain their original argument treatment. The complete tuple tests do not admit a new-namespace/cgroup flag union. The remaining syscall allowlist and argument filters are literal source data, not an approval callback. Namespace/mount/context operations, sockets/SCM_RIGHTS, ptrace/process_vm, pidfd_getfd and unreviewed async interfaces are not on that list.

By induction on allowed task creation and exec, descendants retain the namespace and mandatory restrictions. A later executable has no compiler exemption. Session/group operations that the original subprocess paths may need remain allowed, but do not change cgroup membership or the inherited policy. The original guardian, rather than a process-group-only assumption, still owns whole-domain retirement.

## N7. Required local operation classes remain admitted by the filter

This lemma is deliberately about the filter's exact allowance. It does not assume that an LSM, filesystem, executable or decoder subsequently succeeds. The complete model derives those effects separately.

| Original operation class | Actual admitted native interfaces | Constructed consequence |
|---|---|---|
| File/source/header/native-image reads and stat fingerprints | open/openat/openat2, read/pread/readv, fstat/stat/newfstatat/statx, close, readlink, getdents/getdents64 | The new filter does not itself replace the selected reader's original error, content or fingerprint check |
| Artifact and evidence production | mkdir/mkdirat, open/create, write/pwrite/writev, fsync/fdatasync, rename/renameat/renameat2, unlink/rmdir, truncate/ftruncate, chmod/fchmod/fchmodat/fchmodat2, timestamps and xattr calls | The original calls can run inside `A`; copied mounts rather than a pointer-string seccomp test constrain other targets |
| Metadata helper's child-only FSIZE | setrlimit with resource != CORE; prlimit64 for self pid 0 and non-CORE resources | Its resource 1 callback and readback are admitted, while CORE changes remain denied |
| Process/thread creation and teardown | exact clone fallback tuples, ordinary fork/vfork, execve/execveat, wait4/waitid, exit/exit_group, set_tid_address, set_robust_list, rseq, futex, signal and memory primitives | The original live-thread control is not intentionally replaced by a clone3 or ordinary-thread denial |
| PIPE/text producer I/O and timeout | pipe/pipe2, dup variants, poll/select/pselect/ppoll/epoll, read/write, waits, nanosleep/clock_nanosleep, clocks and signal operations | The two PIPE/text producers keep their original communicate/timeout/decoding owner instead of being converted to raw-file helpers |
| Process identity/group observations | getpid/gettid/getppid/getpgrp/getpgid/getsid and genuine proc reads | No new PID namespace or new entry-created process is introduced to falsify the original role/group relation |

The metadata raw-file producer remains distinct from both sysconfig/shlex/PATH PIPE/text producers. Admission of these syscall classes does not prove their separate compiler/helper/spec/interpreter resolution closures equal; no such identification is made here.

## N8. New setup errors cannot satisfy the original terminal classifier

**Hypotheses.** An entry setup error reaches its ordinary non-exec exit; the genuine runner/receiver source in the existing 31-function map performs the final check.

**Conclusion.** That failure cannot be accepted as either complete normal science or the original optimized full-entry refusal.

**Proof.** The native failure branch emits only its failure evidence and exits 78, with no scientific exec or successful receipt. `fresh_runner._poll_child` records the actual wait tuple before decoding and commits the actual exit. `full_result_receiver.validate_terminal` requires exit 0 for normal science or exit 1 for optimized refusal, plus complete cleanup/EOF/closure. Optimized refusal additionally requires the exact original traceback boundary and suffix. Exit 78 fails the common terminal test before either success branch. A signal or unresolved native wait also fails rather than being normalized to the original refusal. These are existing function-map rows 25 and 27, not new failure consumers.

This result preserves the distinction between setup failure and original negative observations; it does not prove that every supported environment will have successful setup. Numerical native/resource/security admission remains an owned later edge in the complete construction.

## N9. Error order, capacity and actual release remain explicit

The native error array appends the saved errno at the point of failure. A CREATE primary is appended before a close can change errno; later close errors append in order. A full array marks uncertainty. No status flag is used as evidence that a partially published kernel object is absent. Actual release of namespaces, mounts, FD0 and pipe writers is never established by the native failure projection itself.

The success path consumes 27 registry slots, including initial stdin adoption. Its peak is 13 registered live FDs, or 15 including the two pipe writers. The context closes before view handles, so the dispatch repair adds one lifetime slot without increasing the peak. The 96-slot and 48-error caps are unchanged; the previous exact birth/close calculation remains applicable. All source setup, failure, closure and kernel-retirement tails remain in the original enclosing attempt/cost union with physical cost `OPEN_NOT_ZERO`.

## Composition boundary

N1–N9 give concrete facts and a proved transition structure for the actual entry. Together with the consumer lemmas in `ORIGINAL-NATIVE-CONSUMERS-v1.md`, they close specific possible representation, self-root, first-refusal and process-control contradictions. They do not replace the full finite dispatch/security/filesystem/fault construction or the original parent/native association cut. No new C correction follows from these source facts as of this version. If the parent/Pro theorem identifies an actual failed primitive or operation consequence, the correction must be made at that exact existing owner and the affected lemma updated.
