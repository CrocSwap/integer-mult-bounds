# Independent complete-close source review

Review finished at 2026-11-06 05:12 UTC, before the 05:23:11 UTC review checkpoint and 05:38:11 UTC hard source deadline. This reviewer read source and wrote review artifacts only. No reviewed module was imported or executed, and this reviewer ran no tests, native owner, compiler, science job, process inspection, network operation, or publication.

## Exact reviewed inputs

| Input | SHA256 |
|---|---|
| Frozen owning successor `implementation/active_complete_close_v1.py` | `9b4ddb537e46e0f7f5f09cab10e32cc9f8d1a6472b8612757b1da04a7155b380` |
| Frozen inert harness `validation/controls_v1.py` | `81ef02f0f8cb2b45fb03f6cbf2fee462a8b021602b2031699d3a31116cc5b25f` |
| Exact original owner `outputs/s04-resource-fit-20261106T0200Z/inputs/exact/selected_owner.py.txt` | `e94ee23f4f66b16f9d5a0b7f1cc510952d1769247283062d9124737d7838ce3c` |
| Portable copied owner `reference/active_original.py.txt` | `e94ee23f4f66b16f9d5a0b7f1cc510952d1769247283062d9124737d7838ce3c` |
| Exact original and unchanged copied funding | `164468176d2094fbd496eecfd0d0adf3b6ceaf89b2573456509157cc26256677` |
| Completed Pro advice `consultation/RESPONSE-v1-complete.md` | `81b702ad20ac0dfcdac0a098b994748c897ffd09c5eafc1997de5b96329d0ea2` |

Paths without an absolute prefix in the table are relative to `outputs/s04-complete-close-20261106T0438Z/`. The independent frozen successor copy is `review/independent/active_complete_close.reviewed-v2.py.txt`; the final independent harness copy is `review/independent/controls.reviewed-v3.py.txt`.

The earlier rejected source snapshot and `REVIEW-v1-findings.md` remain preserved. This report resolves those findings for the new exact source hash, rather than altering the earlier verdict.

## Source verdict

**GO_SOURCE_COMPONENT_ONLY.** The reviewed optional complete-close branch is source-consistent with the supplied original owner, unchanged funding source, and completed advice at the boundaries below. The three defects reported for the earlier `4f299...` snapshot are repaired:

1. The validator now checks request/START schemas, exact shared round/label/command/reservation/policy values and types, the selected round, and pre-entry provenance against that same request. The actual registered START remains checked by unchanged `active_view`.
2. The complete error helper first protects a caught object, then preserves an established original primary from the captured actual `FIRST` list when the private primary is empty, before optional recorder work. It retains the new caught error as secondary when an earlier primary exists. This is a review of new bookkeeping after catch, not a universal allocation-safe exception theorem or a repair to every inherited pre-handler path.
3. Complete-branch release error handling now follows the privately selected complete branch even when initial verification failed before `complete_used` was set. It restores `CLOSE_UNKNOWN` after protected error recording, retaining the once-only release boundary. The unchanged actual close helper also preserves its native-close entry flag.

No further blocking defect was found in that repaired source during this bounded review. This finding does not state that all required behavioral controls have passed; the parent has not supplied execution results to this reviewer at the time of this report.

## Reviewed contracts and remaining premises

- The optional new argument has a separate seven-field closure shape with a closed versioned binding. It is restricted to CLOSER and excludes the legacy closure argument. Native DATA validation and private copying occur before `open_owner` can acquire a lease. The legacy six-field STOP/UNKNOWN close body and ten-method Context interface remain intact. Funding `exact` and `digest` identities are captured along with the pre-existing selected functions.
- Every actual context still acquires its own selected native EX through the unchanged owner. JSON data, hashes, review decisions, result labels, and the bounded raw-input inventory do not manufacture that ownership or authenticate a native outcome.
- Genuine complete evidence acceptance, original pre-outcome result-contract selection, full raw-evidence custody, and clock lineage remain explicit authenticated source-private parent/reviewer premises. The closer reads pinned bounded metadata, not arbitrary large raw captures. The source cannot establish those external premises from a synthetically consistent packet.
- The closer retains separate original manual request/provenance slots. The continuation sample uses its own reservation; target elapsed time validates the target receipt. Target command and operation identity differ from the closer's, and the selected original clock selector establishes target terminal time no later than the closer's original start. Startup, release, final exit, and complete closer accounting remain responsibilities of the original enclosing meter/admission.
- Review binding is acyclic: the review commits to the canonical receipt projection omitting only the review-digest field and to the complete evidence binding. The final receipt carries the raw review digest. Publication passes the selected original final receipt bytes unchanged.
- Before first receipt publication, the new branch checks current target ownership/view, all selected metadata correlations, prospective receipt pin, exact single CLOSE append, registry and append-only semantics, generation capacity, and metadata size limits for the prospective registry and HEAD. It rechecks HEAD/current registry immediately before writing. It compares publication pins and durable registry/HEAD readback with the precomputed images.
- IO/allocation failures after publication begins remain uncertain evidence. The branch has one-use state and no automatic retry, rollback, deletion, or repair. Known owned cleanup remains available; unknown ownership is not guessed.
- A truthfully observed resource-invalid PASS or known STOP remains recordable with actual duration and sampled RSS unchanged. The extension makes no resource-fit grant. Unchanged funding assessment retains reservation and RSS blockers for later admission. Successful record publication does not supply scientific credit or settle the closer's own operation.
- The branch does not clear G or confer a native or execution capability. Successful return explicitly retains unsettled costs and false capability/permission fields.

## Harness and proposed command source

**GO_COMMAND_SOURCE_ONLY** for the exact final harness hash in the table and unchanged selected source/reference hashes, limited to the parent's two proposed serialized controls: one normal Python invocation, then one optimized invocation with `-O`. The reviewer does not execute these commands.

The proposed command envelope is suitable for this source-only control scope: `/usr/bin/time` records bounded observations; `timeout --signal=TERM --kill-after=2s 20s` encloses `prlimit` with address space 268435456 bytes, CPU 20 seconds, file size 1048576 bytes, and descriptor cap 256. The sanitized environment and `/usr/bin/python3 -S -s -P -B` avoid site loading, user packages, and bytecode writes. Add `-O` only for the second invocation. Preserve the proposed two 25-second body reservations and two 2-second administrative fees, 54 seconds total posted policy amount, while recording actual observations truthfully. No unchanged retry or additional execution is covered by this verdict.

The harness AST-extracts the whole actual complete validator, complete method/helper, dispatch/release methods, and unchanged `advance`, together with selected unchanged funding DATA functions. Publication, HEAD, ownership checks, manual entry, clock, UID, cleanup, and funding IO use inert ports. It does not import the archived owner/controller/funding modules or call their native ports.

The final source includes positive full outcome, selected expected-refusal, and selected known-STOP cases; identity/evidence mutations; resource-invalid STOP and original PASS with actual figures; legacy body/method-set compatibility; replay; role/current-HEAD refusal; metadata and generation limits; primary/secondary custody including initial verification before consumption; and both own-versus-target reservation directions. The negative reservation discriminator is own=5, target=10, local sample=7; the reverse positive is own=2000, target=10, local sample=1000.

Coverage limits must accompany any resulting count. The five staged failures exercise actual `advance` at the receipt, registry, history, HEAD, and final readback call boundaries through an inert publication port. They do not execute the internal write, fsync, link, or close phases of unchanged `publish`. Input binding before acquisition is source-reviewed, not executed by this harness. Real `active_view`, native ownership, independent acceptance, full raw-evidence custody, and live profile/funding state are not qualified by the inert fixture. Controls do not directly execute the downstream funding blocker path, whose retention is established here by comparison to unchanged original funding source.

## Adoption and original-acceptance boundary

**CONNECTED_CALLER_ADOPTION_NOT_ACCEPTED.** No actual source-private bootstrap/caller selection of this successor, updated owner/loader source pin, or detached source-manifest binding was supplied for review. Preserving method names and capturing the new fixed validator internally do not preserve the predecessor source identity automatically. The closer's actual authenticated load chain must explicitly select successor SHA256 `9b4ddb537e46e0f7f5f09cab10e32cc9f8d1a6472b8612757b1da04a7155b380` when adoption is performed. The unchanged funding source remains pinned to its unchanged hash. Historical target source/profile bindings must continue to describe the actual admitted target image; they must not be rewritten as if that target had executed the new closer source.

Accordingly, this review accepts the owning extension only as a bounded source component and accepts the exact proposed inert commands as suitable source controls. It does not accept genuine native evidence, actual full-input execution, resource fit, scientific correctness, complete caller integration, a completed original S04.03/S04.04/S04.05 activity, publication, or S04 completion. The original decisive acceptance checks remain open beyond this component.
