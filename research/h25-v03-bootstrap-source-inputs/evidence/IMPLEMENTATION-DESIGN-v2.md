# Unit06 versioned design supplement

This supplements, and never rewrites, IMPLEMENTATION-DESIGN-v1.md (13,674 bytes; SHA256400f1533fd08dcad2633d477f9d388cd65b888b0c0e74c08c20e7fbef33c0bae). Both are source design only. No implementation source has been drafted or executed, and parent input-gate approval remains required.

## Terminal partial-initialisation ownership

A new bootstrap-owned state object, outside every captured project namespace, is retained by the T0 caller/entry before its first acquisition or module publication. Its one-attempt slot is consumed before any selected project object is published or any project body executes. This state owns the retained independently pinned source buffers, exact constructed ModuleType objects, publication/execution order, current phase, primary raw exception, secondary cleanup exceptions, and uncertain acquisition flags.

All selected source bytes are authenticated and retained before the first project body executes. A failure during compilation, sys.modules publication, module initialisation, gate installation, identity checking, make_prefix_owner, run_prefix, result verification or receipt writing terminally burns this attempt. The first delivered exception is retained by identity before formatting or optional reporting; cleanup exceptions remain separate raw objects. Partial retained bytes, module objects, published-name map and phase observations remain available to the actual enclosing failure owner. No new owner/capture is created to clear an earlier failure.

Removing sys.modules entries is not rollback of module-body effects and cannot authorize a retry. This design performs no alleged rollback. The process remains terminal and the genuine enclosing guard must observe its exit/cleanup. Failure data is not an original capability. Pre-handler/native acquisition uncertainty retains the original bounded-guarantee caveats; no universal first-error or hostile-host theorem is claimed.

Project modules use actual real builtins, their actual constructed namespace dictionaries and exact retained bytes. Only the explicitly permitted authentic six supervisor and three COPY gate globals are installed before the one actual capture/owner-construction call. No post-capture extra globals, wrappers or diagnostic state are added to captured project namespaces. Bootstrap mutable state remains in its separately owned entry/caller object. Existing original mutable registries change only through their actual original source paths.

## Exact original identity schema correction

The v1 prose listed the operating-system term nlink. The actual schema.IDENTITY_KEYS field is **links**, not nlink:

    device, inode, mode, links, uid, gid, size, mtime_ns, ctime_ns

The preparation/read primitive maps observed stat.st_nlink to identity['links']. It must emit the exact original schema.blob fields path,sha256,bytes,identity, require a regular single-link file and identity.size==bytes, and preserve exact typed integer/range checks. No observed identity is fabricated from a content hash.

## Caller and receipt boundary clarification

The actual queue science/receipt.json bridge is an explicit NEW case DATA contract. A fixed PREFIX_OBSERVATION_DATA receipt is written only after the actual one owner-construction/run_prefix sequence and actual verification of its returned observation file. Its production_completion/full_c05/full_v03/runtime_qualified/enclosing_parent_exit_observed fields are false. It creates no new source, financial, native, process or completion authority. The unchanged queue's generic acceptance is not original C05/V03 qualification.

Actual canonical root history, runner budget/locks, outer real subreaper/domain/RootProxy and receipt custody remain the original operations. The existing outer source has inherited str(error) formatting and PermissionError/process-census caveats; preserving it does not strengthen those into a universal opaque-failure guarantee. The new retained-byte loader's own first-error handling uses raw objects and makes only its scoped caught-error claim.

Q's complete nine-category current source/compile/oracle/stage inventory remains a future genuine independent input. The actual preparation operation must read/check each real selected row, enforce exact original row shape/categories/limits and refuse absent or mismatching inputs. It may not substitute policy-only rows, invented categories, dummy files or a completeness boolean. Complete original C05/C07/native/source/funding/runtime admissions remain unestablished separately; no image, native policy or paused prior unit is implemented here.

Sb and Sc remain separate. The runner excludes every basename STAGE.json. Preparation rejects unexpected nested STAGE.json or accounts for it through an explicit independently pinned outer custody input; it never infers that ordinary stage inventory covered excluded bytes. M uses its ordinary inventoried fixed name. Every excluded outer file/read/identity and both parent lifetimes remain in the bill.
