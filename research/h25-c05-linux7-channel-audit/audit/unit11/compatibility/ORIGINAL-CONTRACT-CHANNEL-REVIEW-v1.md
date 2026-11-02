# Unit11 original-contract and channel compatibility review

Reviewed at 2026-11-02T16:48:27.295796+00:00. **STOP before any installer. Whole P2, P3 and P4 are not established.** This is a bounded source comparison; it does not adopt a copied instance or native policy.

Actual Ubuntu kernel sources at commit `88cb661f6b53f472167d39a72241b5396e34ab2a` are available. The findings below use those retained bytes, not the Pro12 Linux6.8 examples. Config/registered-LSM observations and source availability do not prove source/binary reproducibility or active policy coverage. Exact package/parser overlay review is separately owned by the kernel reviewer.

## Original contract and the 215-header question

CONDITIONS C05 requires the complete independently approved current project/system-header/search/macro/compiler/specs/link/dependent-library closure in bounded child source_files. INTERFACE keeps that at512 occurrences,64MiB/file and256MiB/capture; parent source/stage limits are8192/16384. C01/C03/C07 preserve original Root/provider/helper/native startup, immutable ancestor ownership and independent full-stage/receiver custody. C02/C13 permit assessing a separately admitted fresh installed stage; they do not admit this particular private copy.

Provider `probe_binding_v3.py` (40799B, SHA256 `9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2`) has216 immutable runtime rows:214 `/usr/include/python3.12/` headers,1 multiarch `pyconfig.h`, and `/proc/self/exe`. Header expected bytes total1256818. `_profile_files`276–287 adds the provider-adjacent profile, so `_audit_files`290–293 and `preflight_runtime`452–458 check217 files. This is static source counting, not observed current custody. Variant722 invokes the original packet/Root/provider chain before either build and788–789 invokes it again after.

Variant `_vcheck_literal_sources`660–688 explicitly binds the six role C/header files and fixed include path. It has no all215 runtime-header membership loop. Provider preflight therefore covers those original header/profile obligations separately. That fact does not establish compiler exclusion and does not justify subtracting215 rows from a C05 selection: unchanged gcc uses `-I/usr/include/python3.12`; all actual relevant compiler inputs still need complete approved F/child witness treatment or a valid effective exclusion/relevance argument. No fitting count is established.

## Concrete compatibility constraints

Original cold helper `aa0a315110e031e19291970c9611fe5e0f91465fa20eaec51e81186099563f78` opens raw logs at189/208–209 with `O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW`, without `O_APPEND`. Popen220–221 runs the exact command directly, inherits current cwd/env, uses DEVNULL stdin, closes other FDs and does not create a session. The callback92–107 sets the child file-size limit before exec. Append-only permission would change required behavior; ordinary write permission alone does not prove evidence integrity.

Exact7 AppArmor `lsm.c`1151–1166 revalidates inherited files, clears pdeath_signal and transitions resource limits on confined profile change. `file.c`920–943 may replace denied inherited FDs with null. `file.c`768–771/839–849 retains unconfined-object delegation. Hence directed lowercase px is a plausible mechanism, not a preservation proof: correct parent confinement must precede sensitive FD opens, the original FD identities/limits must survive, and actual prior pdeath state must make its change harmless or be preserved by an original-compatible route. No actual pdeath mismatch is asserted here.

Parent source uses real `/proc` census, actual Popen generation and same-process subreaper GET/SET/GET with retained genuine native keeper (`h25_parent_supervisor.py`108–175,392–399). Parent domain188–190 permits only four domains. Fresh exec into copied inodes requires fresh genuine native/mapping/receiver reconstruction; serialized old tokens are not authority. The native checker158–189 compares mapped device/inode identities, so content-identical copied paths alone do not satisfy it.

## Channel matrix

| ID | Route | Remaining obligation |
| --- | --- | --- |
| M01 | ordinary F reads, executable/library mappings and mprotect | No installed/admitted profile or bound BPF program, concrete complete F, alias closure or actual full-read reachability proof. |
| M02 | metadata stat/getattr | Select exact ABI/emitted policy and represent or exclude relevant metadata, including failures, without assuming every stat is a file-byte read. |
| M03 | readlink, pathname-component search, negative lookups, alias resolution | A complete effective exclusion or original-compatible namespace/relevance witness is absent. This alone blocks AppArmor-only complete P2 as specified. |
| M04 | automatic gcc transition, descendants, argv/env/PID | Package patches/emitted ABI/loaded attachment plus no envscrub/no wrapper/no executable alias escape/no unconfined fallback must be proved; no current policy or instance is approved. |
| M05 | inherited descriptors and SCM_RIGHTS/file_receive | Parent must already be correctly confined when sensitive descriptors are opened; inherited set, rawlog descriptors and delegated objects must be closed/approved with no substitution. close_fds=True alone is not proof for all lifetime channels. |
| M06 | pipes, Unix sockets, network, asynchronous/delegated I/O | No complete IPC/network/SCM_RIGHTS/async policy, actor confinement or justified irrelevance proof is supplied; do not infer exclusion from PATH or absent ordinary files. |
| M07 | System V shared memory/messages/semaphores and inherited shared state | No explicit IPC namespace/admitted isolation policy or complete BPF construction and prior authority. An IPC namespace alone also requires its genuine operation and relevant inherited-state disposition. |
| M08 | ptrace, proc memory, signals and mutable external peers | No whole actor/signal/ptrace policy or actual preservation of original parent cleanup rights is proved. No blanket noninterference axiom follows from MAC source availability. |
| M09 | real proc parent census and process generations | New PID namespace, synthetic proc or hidden descendants could invalidate ownership. Preserve one real census view, actual Popen PID/start ticks/PGID/SID, four domains, 128 generations and all cleanup tails. |
| M10 | fresh parent/subreaper/native/receiver capture after copy | No copied instance is admitted. Fresh exec requires real reconstruction of Root/native keepers/current module captures in prescribed order, not transferring old Python tokens or reusing old mappings. |
| M11 | pdeathsig and resource limits across exec | Prove actual legitimate prior pdeath state (zero would make clearing harmless), chosen limits and exact transition effects. Source fact is a preservation obligation, not proof an actual launch already fails. |
| M12 | F/P immutability: writers, writable mappings, mount aliases and old roots | No actual exclusive construction, surviving-fd/writable-map census, remount authority exclusion, private propagation/old-root detachment or lifecycle/cleanup evidence exists. |
| M13 | P bootstrap/parent/Root/provider/config partition | Need complete P inventory and every compiler-relevant P occurrence either in F or effectively excluded/proved irrelevant. No hash cycle: outer manifest finalized last, externally pinned before execution. |
| M14 | A compiler scratch/intermediates/output products and generated provenance | Need deterministic ownership of all scratch/temp/device/linker paths, source-to-generated provenance and per-artifact bounds. W_read may include A; prehashing outputs or claiming W_read subset F is invalid. |
| M15 | E rawlog write rights and retention without readback-as-input | Must prove E is not compiler input and cannot corrupt previous evidence while original writes succeed. Raw-log preservation, fsync, errors, close uncertainty and primary-error order need unchanged handling. |
| M16 | namespace/launch K: cwd/env/argv/auxv/credentials/umask/mount/proc | Need exact approved N/L/K values and actual lifetime interval. Do not strengthen C01 into a blanket arbitrary-kernel-data premise or treat selected namespace observations as universal source closure. |
| M17 | vDSO/vvar/auxv/CPU features/time/randomness/nonfile facts | No source-supported proof or original-admitted K model covers all relevant such channels; do not assert gcc uses __DATE__/__TIME__ in these exact builds or assert they are irrelevant without evidence. |
| M18 | 215 Python headers and profile coexist with compiler policy | Literal validator does not require all215 child rows automatically. Separate provider custody is not compiler exclusion. No215drop from C05/compiler F, no double counting, and no claimed fitting count without complete actual selection. |
| M19 | immutable metadata/negative witnesses and K witness encoding | No complete original-compatible encoding of dynamic/nonfile/search witness and no independent admission of that witness is supplied. |
| M20 | wire and physical-resource fit | No complete actual selection with row/byte/codec/alias/path/custody/native/memory/CPU/wall/cost bill. Pro12 broad858/literal531 reported candidates fail512 but do not prove no smaller valid candidate exists. |
| M21 | failure/cleanup/source-lifetime boundaries and current authority | No current enclosing parent/runtime/funding interval exists. Source-only feasibility cannot supply actual privilege, C05/C07 admission, reservations or scientific activity credit. |

The JSON contains original anchors, separate AppArmor/BPF source mechanisms and unresolved predicates for every row. No row claims actual runtime policy enforcement.

Exact7 registered AppArmor hooks2159–2275 include getattr and file_receive but omit inode_readlink, inode_permission and SystemV IPC families. `security_add_hooks`3068 registers that array. `domain.c`1053–1056 also leaves shared-state mediation as FIXME. A BPF hook family is available in source, subject to disabled-hook/verifier checks (`bpf_lsm.c`39–59,119–139), but no complete bound program/maps/attachment/caller/lifetime proof was supplied. Missing relevant channels can be closed by an original-compatible mechanism or sufficient independent relevance/observer argument; source-hook absence is not a general impossibility proof for all alternatives.

## Scope and decision

For the finite enclosure, actual ordinary reads may lie in F or generated A; only exogenous ordinary-file origins must lie in F. Relevant nonfile N/L/K inputs require their own explicit approved treatment. AppArmor or BPF does not mediate arbitrary vDSO/vvar userspace instructions by being installed. The original contract does not demand general GCC correctness or universal deterministic output, but omitted relevant facts cannot be declared trusted kernel data without a sufficient original-compatible argument.

No exact complete F/P/A/E/K/witness selection fits the child codec/row/byte/resource/custody bounds in current evidence. Reported broad858/literal531 candidates in Pro12 are diagnostic failures of those candidates, not proof that no smaller complete selection exists. Parent/provider-only custody is not consumer exclusion, policy/witness files are not free, and generated outputs must not be prehashed into self-referential input manifests.

The next concrete gate is the complete source/policy/ABI/candidate proof plus original-preservation and fit, followed by genuine admissions and funding before any privileged work. A user decision to adopt a privileged copied-instance MAC route changes the trusted native mechanism being proposed; granting arbitrary K inputs, dropping actual compiler inputs, changing flags/PID/proc/rawlog behavior or raising caps would change assurance or the experiment. This review does not infer any such decision from Pro12.

All original C05/full V03/runtime flags remain false; original activity credit added0, completion43.5%, costs OPEN_NOT_ZERO. No original code, target/compiler/native operation, namespace or policy installation, tests or host-process inspection occurred in this review. Only the owned report pair is written.

## Pinned sources

- `plan`: `outputs/c05-v03-completion-20261102T055710Z/unit11/PLAN.json`; 2981B; SHA256 `53eae6fa7489e12420c855f4b11dd87ed03c7f36890f4a33d723e89d45ced9c2`.
- `pro12`: `outputs/c05-v03-completion-20261102T055710Z/consultation/RESPONSE-v12.txt`; 12183B; SHA256 `cb0bf3dfb999515db32dcbcf7f79cb3c58905a8139063d28f8ca09622e72bc8a`.
- `assessment`: `outputs/c05-v03-completion-20261102T055710Z/consultation/ASSESSMENT-v12.md`; 1245B; SHA256 `56aaf3bd5913e76e78aed193a9cdd2bff4bb155f343be22c5ab6302c8526678e`.
- `host_config`: `outputs/c05-v03-completion-20261102T055710Z/consultation/HOST-POLICY-CONFIG-REASSESSMENT-v12.json`; 1323B; SHA256 `6a86df2870574d4c4625b5627bdde9971212945bfb78d905eafe273044e9e69d`.
- `host_packages`: `outputs/c05-v03-completion-20261102T055710Z/consultation/HOST-POLICY-SOURCE-AVAILABILITY-v12.json`; 1949B; SHA256 `0d25cd594190ebc2972c1a49799ca1ba2ca3ea287cb5982bca6c919674277bc5`.
- `conditions`: `outputs/resolved-questions-publication-20261102T025112Z/v03-publication/research/h25-v03-source-prerequisites/snapshot/areas/field-variant-producer-v2/CONDITIONS.json`; 6940B; SHA256 `70e237d6ee4ac2ccaadf01615e8106999718eb1fbb3cf7644c9fc6d3fd4463fe`.
- `interface`: `outputs/resolved-questions-publication-20261102T025112Z/v03-publication/research/h25-v03-source-prerequisites/snapshot/areas/field-variant-producer-v2/INTERFACE.json`; 6956B; SHA256 `30820f1f2d27d4d4306d8ba63db5329f89182912f7f915aede35b9ce62359491`.
- `variant`: `outputs/c05-v03-completion-20261102T055710Z/publication-prefix-derivation-v1/research/h25-v03-configured-prefix-derivation/snapshot/variant_driver_v1.py.txt`; 41337B; SHA256 `cdb1479253358508088f8aa0e1e92e6c75ffcc127e54552698598a02de061254`.
- `provider`: `outputs/h25-data-handling-20261028/stages/combined-finite-v8/integration/probe_binding_v3.py`; 40799B; SHA256 `9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2`.
- `root`: `outputs/h25-data-handling-20261028/stages/combined-finite-v8/integration/full_driver.py`; 38851B; SHA256 `f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0`.
- `packet`: `outputs/h25-data-handling-20261028/stages/combined-finite-v8/integration/native_packet.py`; 21478B; SHA256 `6adbcd1dfeb77fb6da7ee8f725796b1bfdbf0a4f397ef23f3a266a6b89d55892`.
- `cold_helper`: `outputs/c05-v03-completion-20261102T055710Z/unit03/binding/cold_build_evidence.py.txt`; 16463B; SHA256 `aa0a315110e031e19291970c9611fe5e0f91465fa20eaec51e81186099563f78`.
- `supervisor`: `outputs/c05-v03-completion-20261102T055710Z/unit05/implementation/h25_parent_supervisor.py`; 23047B; SHA256 `cfb09a18dd10b597cc6d5a8139ee769bef679bc44ae029329755e3d97b055075`.
- `domain`: `outputs/c05-v03-completion-20261102T055710Z/unit05/implementation/parent_domain_v1.py`; 23942B; SHA256 `a51264289803b4b17bb262f2460ddd4ed72500aaa21e5eb80fa2db4583689361`.
- `parent_completion`: `outputs/c05-v03-completion-20261102T055710Z/unit05/implementation/parent_completion_v1.py`; 54168B; SHA256 `d4ee1b7ce4a42b73261984ffb1b9ceb5bb0165223e04a253588f83b99f6981a5`.
- `closure`: `outputs/c05-v03-completion-20261102T055710Z/unit05/implementation/parent_closure_v1.py`; 13463B; SHA256 `a15424f14baa3d484fe04bfbe7e449c32561c866dbaca2c1b5f646dfb377ed1f`.
- `native_tcb`: `outputs/c05-v03-completion-20261102T055710Z/prerequisite-source/native_tcb_v1.py.txt`; 11353B; SHA256 `865943df5cfdbf9383362d7fb2b76c6d0fd895cf0a0e20d550a26b579606b5d7`.
- `tcb_profile`: `outputs/c05-v03-completion-20261102T055710Z/unit06/prerequisites/NATIVE-INITIAL-TCB-v1.json`; 4935B; SHA256 `610492b3fc06baa0560175edc3ba27057de00d00b8fd3d58dbe55e5a371c042a`.
- `prior_copy_review`: `outputs/c05-v03-completion-20261102T055710Z/unit04/compatibility-review-v1.json`; 8664B; SHA256 `9dfa9168d69cba7adcd98bec567ee61db1ad98de90adc1c603195458f2164a49`.
- `kernel_acquisition`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/EXACT-SOURCE-ACQUISITION-v1.json`; 24517B; SHA256 `da7ad90b4e0e0c428d10aafd547768d194deb2cc5eb6bbf43daaa9bbfed040da`.
- `aa_lsm`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/exact-source/security/apparmor/lsm.c`; 85116B; SHA256 `2ca0d185cb272958c4a8ae7c2da0c923db9648765411187f940443f34c228021`.
- `aa_file`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/exact-source/security/apparmor/file.c`; 27463B; SHA256 `4e32fb7dcaaef6f5e4f41f638257d2aa462cd68827d6a4a0e9af6db1ad12a5c4`.
- `aa_domain`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/exact-source/security/apparmor/domain.c`; 46410B; SHA256 `87bee91898fdf119b8c7b58ad5b2078df83db68c5dca397d4e1a49e62d090a9b`.
- `aa_compat`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/exact-source/security/apparmor/policy_compat.c`; 9514B; SHA256 `2934dd788f1536ed3c1d201b27fb3179fb69296985975db81b78c6c0d73b3e39`.
- `bpf_lsm`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/exact-source/kernel/bpf/bpf_lsm.c`; 13968B; SHA256 `2d952607f3a280deef7bd67273c61b1bfa37c2ccc80b3438a417d1246143aa38`.
- `lsm_hooks`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/exact-source/include/linux/lsm_hook_defs.h`; 25085B; SHA256 `c57d584e9bd85686e599dbad10351bc61f0ee9e49a382a7fc8470c6ce461864a`.
- `exec`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/exact-source/fs/exec.c`; 50792B; SHA256 `4eb89b8d5d23050d9a9741f73979fe95fc083b897b2744f08fd395da62f4a698`.
- `aa_parser_manifest`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/APPARMOR-SELECTED-SOURCE-v2.json`; 29047B; SHA256 `39d681f7523ea818a8ea636058eb713f99239c93f0920e989968eb8c22c49156`.
- `aa_parser_misc`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/apparmor-selected/parser/parser_misc.c`; 38361B; SHA256 `f07777cf10320341bab677b0ffc10f54ddcf95afc24a8bdbaed21593465611dd`.
- `aa_parser_h`: `outputs/c05-v03-completion-20261102T055710Z/unit11/kernel/apparmor-selected/parser/parser.h`; 15420B; SHA256 `a9b76f6bcc527dd23b5cf61dd623c52e88e97d7bd58ed0f274277beec38e94cc`.
