# Inventory-local SHA reuse: source and scoped execution evidence

This source proposal changes one repeated SHA-256 calculation in the original
H25 file inventory. After the original pin lookup, the candidate calculates the
digest of the already-read immutable bytes once and uses that value for both the
pin comparison and returned metadata. Every file read, traversal, pin check,
mode/stat check and inventory completeness check remains in place. The original
`need`, `sha` and `inventory` functions remain as a literal independent reference.

The parent completed the fixed six-process schedule once, and independent
retained-evidence review accepted **54 normal/-O control rows** and the narrow
inventory F7 comparison. All four comparison outputs were byte-identical to the
independently derived 32-entry expected inventory. The two complete candidate
outer observations totaled **2.44 s wall / 2.41 s CPU**, versus **2.77 s wall /
2.74 s CPU** for the two baseline observations: 0.33 s lower in each metric,
about **11.91% wall / 12.04% CPU**, on this fixed host/workload/schedule only.
Two samples per arm do not establish significance or repeatable magnitude.
No memory-saving, whole-caller/H25 or original-goal completion claim follows.

| Fixed order | Wall seconds | User seconds | System seconds | GNU max RSS KiB |
|---|---:|---:|---:|---:|
| normal controls | 0.55 | 0.43 | 0.07 | 22056 |
| optimized controls | 0.64 | 0.57 | 0.07 | 24796 |
| baseline-1 | 1.48 | 1.28 | 0.17 | 21996 |
| candidate-1 | 1.25 | 1.07 | 0.15 | 21756 |
| candidate-2 | 1.19 | 1.02 | 0.17 | 22092 |
| baseline-2 | 1.29 | 1.12 | 0.17 | 22064 |

All first observations and empty stderr files are retained; no admitted operation
failed or was rerolled. BOUNDARY-01 was a rejected source proposal before
execution, preserved with its reviewed additive repair. The six outer times sum
to 6.40 s wall and 6.29 s CPU; the ledger charged an 18.46 s policy increment,
reaching 94.210533479 s including its prior checkpoint. Policy administrative
charges are not physical timing measurements. The candidate's maximum GNU RSS
(22092 KiB) exceeds the baseline maximum (22064 KiB); no RSS saving is inferred.

See [PUBLIC-OUTCOME.json](PUBLIC-OUTCOME.json), the [control review](validation/controls/CONTROL-OUTCOME-REVIEW-v1.json),
the [comparison review](validation/comparison/COMPARISON-OUTCOME-REVIEW-v1.json),
and [EVIDENCE-NOTES.md](EVIDENCE-NOTES.md) for boundaries, raw-record locations and
reproduction requirements. `TREE-SOURCE-v1.json` remains the unchanged historical
source receipt; `TREE-EVIDENCE-v2.json` retains the evidence-authoring snapshot before the
README next-question correction; `TREE-EVIDENCE-v3.json` inventories the current
documentation-consistent revision. The
initial 60-file source commit is `876626e3cacf05b8a6cc3795734b08254b08c4b7`
in [PR6328](https://github.com/CrocSwap/integer-mult-bounds/pull/6328). Final evidence
commit remote/head/CI/handoff verification is a separate parent obligation.

The original source contract and prospective bill below remain applicable. The
publication preparer performed only file copying, text/JSON/AST inspection and
metadata hashing; the parent performed the admitted target execution.

## Retained source and provenance

`component/` contains the accepted 12-file source package, including its original
`SOURCE-PINS.json` unchanged. Its independently supplied SHA-256 is
`159a85d5fd9c06d80c30635a7be27ef102be5943c75cff144cbe05bed85edd7e`.
`workspace/` vendors exactly the 36 external files named by that manifest, at
exact original relative paths. `SOURCES-EXPORT.json` maps every copied path back
to its original workspace path, byte count, SHA-256 and mode. Original manifest
and review paths remain historical provenance; they are not rewritten to imply
that a source review occurred in this export. This is an archive-style source
export, without a generated task card or automatic registered replay hook.

The original driver is retained at
`workspace/outputs/h25-bookkeeping-swarm-20261028/stages/v4/integration/full_driver.py`
(SHA-256 `5b963a5f108b334a627e68001c80b9843fb300c7394693e72f34ce0a6050e6f1`).
It is read as source for literal extraction and is never imported as the caller.
The original 11-case Area6 inventory controls remain byte-identical; the
16 additional cases address exact typed outputs/errors, pin/error ordering,
actual read/hash counts, copy independence, mode drift and fresh-call mutation.
Each planned normal/-O controls process has 27 ordered cases, for 54 total.
`reviews/` retains the preliminary review and F1/F2/F4 source acceptances.

The fixed representative corpus is the 32-file, **453,700-byte** frozen v4
inventory in `component/FIXTURE-v1.json`, with exactly **128 fresh inventory
invocations** in each comparison process. This invocation count is an observation
workload, not a claim about full-driver frequency. The source-derived inner bill
has 4,096 reads and 58,073,600 bytes read per comparison process in either arm;
8,192 SHA calls in the reference and 4,096 in the candidate. These are prospective
source counts, not measurements of timing, I/O savings or complete caller cost.
The list pins' historical 0664 mode entries remain unchanged; the actual frozen
corpus is 0444 and returned actual modes are checked independently.

## Mode restoration and guarded reproduction

Git preserves executable classification, not exact POSIX 0664/0444 permission
modes. A clean checkout must restore the authenticated manifest modes before
source-guard admission or execution. Do not edit the accepted manifest, weaken the
consumer's mode checks, or assume that Git preserved its exact modes.

From repository root, the following trusted, stdlib-only **metadata command**
first authenticates the accepted manifest and all 48 copied component/external
file bytes, then explicitly restores their declared modes. It does not import or
execute any target module. The 12 component files use 0664; 34 external files use
0444; the two external Area6 API/control files use their declared 0664.
Review this helper and authenticate it against the publication commit before use.
It has been authored and AST-inspected only in this source snapshot.

```sh
python3 -I -B research/h25-inventory-digest-reuse-20261031/restore_source_modes.py --apply
```

The parent still needs an independently accepted exact runtime/guard/runner and
operation bill before any target command. The helper is setup, not that approval
or execution evidence. The accepted consumer's `--workspace` points to this
package's `workspace/`, not the repository root. Its command shape, **only after
those gates**, is:

```text
PINNED_PYTHON -B [OPTIONAL -O] PACKAGE/component/component_consumer.py \
  --mode controls|baseline|candidate --workspace PACKAGE/workspace \
  --output ABSOLUTE_FRESH_OUTPUT_OUTSIDE_PACKAGE_AND_SOURCE_CLOSURE
```

`component/BILL-v1.json` fixes six serial fresh processes: normal controls,
optimized controls, baseline-1, candidate-1, candidate-2, baseline-2. There is no
adaptive count, sample reroll, discarded first observation, automatic retry or
best-sample selection. Preserve all failures and charge their costs. Parent
execution must enforce the current shared ledger, 180-second command cap, sampled
1 GiB memory cap and existing initial600/total2400-second budget. This source
package supplies no new allowance.

The prospective outer measurement starts before fixture setup, Python bootstrap,
imports and source/runtime validation. It ends after output equivalence, cleanup,
source/runtime/log/guard checks and the guard receipt. Fixture copying, original
source AST/extraction checks, all reads/hashes/stat/traversal, typed validation,
controls, outputs and cleanup are paid. Consumer post-work custody checks occur
on success; the independent outer guard must perform failure-inclusive custody,
log, runtime and cleanup checks. Report complete per-process elapsed/CPU and
sampled peak memory, two full baseline costs versus two full candidate costs,
and control costs separately. A no-gain result is a valid bounded disposition.
Preparation, review, mode restoration before the guard, publication and final
report serialization outside that boundary remain separately unknown overhead
until measured; they are never assigned zero. The original historical timing and
final metadata-publication gaps remain open.

## Limits, relationship and credit

The domain is trusted supported CPython 3.12 stdlib bindings, ordinary Path roots,
fixed dict/list/string pins, and already-read immutable bytes. The candidate
keeps no digest table or cached PASS across invocations, copies or before/after
boundaries. It supplies no arbitrary callback/monkeypatch semantics or concurrent
filesystem mutation guarantee. No cached arithmetic, native or row observer,
scientific decoder, whole H25/caller speedup, construction admission or kappa
claim follows. This inventory subcomponent does not complete the broader
ordered-observation/digest component or the original six-area/24-checkpoint goal.

Credit belongs to **Clear1nsight/CrocSwap** for the original H25 integration
inventory, frozen sources and retained controls. The exact original files,
embedded attributions and Apache-2.0 license are retained in the export. This
narrow local reuse and package were prepared with substantial OpenAI Codex
assistance. Existing predecessor attribution remains unchanged.

[Serializer PR6326](https://github.com/CrocSwap/integer-mult-bounds/pull/6326)
is context for the separate serializer contribution; this package changes none
of its files or claims. The parent's bounded overlap search identified PR2348 as
instruction-JSON-fragment reuse, a different target from this file inventory.
That search is incomplete evidence, and this package makes no novelty claim.
`provenance/UPSTREAM-BASE.json` retains the observed base, not proof of the final
publication ancestry or current upstream state.

## Open next questions

`OPEN-QUESTIONS.json` preserves the exact historical source-stage questions.
Its first source-stage admission/execution blockers were resolved for this fixed
host/workload by the retained control and comparison reviews. Active next steps
remain separately bounded:

- Does the observed reduction recur under a fresh admitted reproduction, or
  extend to another declared workload? Start with a new independently reviewed
  host/path/runtime/source/resource bill and fixed observation schedule; this
  two-sample-per-arm result establishes no significance or generalization.
- Would contributors review a broader ordered-observation reuse contract? Start
  with one source-pinned observer, its literal reference and invalidation cases;
  contributor agreement and a separate authorization/gate are required. This PR
  contains only inventory-local reuse.
- What completes the original goal's remaining timing/publication and caller
  obligations? Start by mapping this scoped evidence against the original
  checkpoints; the unresolved original invoice and broader source contracts
  remain blockers.

## Retaining execution evidence and future reproduction

Keep `component/`, `workspace/`, `reviews/`, and `SOURCES-EXPORT.json` unchanged
for this accepted source identity. This revision appends separately admitted
runner/runtime/source reviews and exact operation receipts under new
`execution-source/` and `evidence/` paths outside `component/`; the consumer has
an exact component-file census. Retain failures, raw outputs, source/runtime and
guard pins, exact absolute command arrays, all six scheduled observations and
cost accounting. Record relocation/mode-restoration overhead separately. Update
this README's status only from actual evidence, refresh the package tree receipt,
and publish the execution evidence as a separate incremental commit. If any
accepted component/external byte or mode changes, obtain fresh affected source
acceptance and execution evidence instead of rebinding old receipts.

The original source publication and this appended evidence have separate identity
and publication checkpoints. Local package preparation does not verify the final
remote blobs/head or hosted replay. The parent owns final commit publication,
exact-head CI/readbacks and the contributor-facing handoff; these steps do not
establish scientific correctness.
