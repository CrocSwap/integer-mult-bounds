# Mutation isolation for the exact retained R2 caller

This package changes the construction of mutable fault-injection fixtures in
24kHandsome1201's PR3202 audit, as retained by Tekalign's PR3218 comparator
adapter. It does not change a mathematical predicate, native operator or
mutation function. Path copying and structural sharing are established
programming techniques; their discovery is not claimed here.

## Precise domain

The source pins are PR3218 `a93c4f0bfcac21bf9c62c79728c8936e35ebbc3b`
and its retained PR3202 `259043321323717b7e816d6be38ad5e1f0b69b4c`.
Every retained file and live dependency is authenticated before execution in a
private snapshot. The original strict JSON parser constructs the fixtures.
Lists and dictionaries therefore form trees: there are no cycles or repeated
mutable container references. Immutable numbers, strings and keys may repeat.
This is a contract of these actual fixtures, not of arbitrary Python objects.

The original `reject` helper copies the complete word and data, calls one of
sixteen mutation functions, requires a nonvacuous change, and runs its original
predicate. It accepts the control only when that predicate raises the exact
specified `ValueError` message. Both providers execute all sixteen controls.

## Write-footprint table

`adapter.plan` selects the same first matching record as each literal original
mutation. Actual selected indices and keys are recorded for both providers in
RESULT.json. No optimizer-selected replacement mutation is substituted.

| Original mutation | Isolated object | Required copy at that object |
|---|---|---|
| forward fan-in sign | first matching forward scalar event | entire event subtree |
| dual fan-in sign | first matching backward scalar event | entire event subtree |
| rank-two child undercharge | first matching forward cleanup climb | entire event subtree |
| tail phase substitution | forward cleanup-tail phase event | entire event subtree |
| wrapper side | first forward post-wrapper event | entire event subtree |
| dual wrapper owner | first backward pre-wrapper event | entire event subtree |
| post wrappers before cleanup | forward event list | outer list only |
| source exit frame | forward source-40 exit adapter event | entire event subtree |
| missing dirty restoration | word's restore list | outer list only |
| extra fan-in observer | restore gate 180 | entire gate subtree |
| prefix wrong source frame | first forward climb with nonzero old frame | entire event subtree |
| native global phase | selected W-to-FULL child record | entire record subtree |
| native translation | same child record | entire record subtree |
| native child rank | same child record | entire record subtree |
| residual global phase | first sorted residual recipe | entire record subtree |
| residual translation | same residual recipe | entire record subtree |

The post-wrapper mutation extracts a slice, deletes that slice and inserts it
earlier in the same list. It never edits the event cells. The missing-restore
mutation only pops the outer list. Both may therefore share their untouched
children with the original fixture. All other selected subtrees are fully
deep-copied, including the nested scalar operands or monomial fields.

## Path-copy lemma

Let T be a finite tree of plain lists, dictionaries and immutable scalars.
Choose one container at path p. Copy each ancestor container shallowly and
replace its selected child with the recursively copied child. At p, either
deep-copy the entire subtree, or shallow-copy only that container when the
mutation changes its slots without changing any descendant.

Before mutation, the resulting value equals T. Every container the mutation
can write is fresh, and all shared containers are outside the write footprint.
Applying the same mutation to this value and to a complete deepcopy produces
equal complete values and leaves T unchanged. This follows by induction along
p: the selected child is replaced in a fresh ancestor, and every other child
retains its original value. At the leaf, deep isolation or the restricted
outer-container write contract gives the required disjointness.

This lemma does not hold for arbitrary aliased object graphs. An alias outside
p could refer to the modified leaf, and a general deepcopy would preserve that
alias inside its copy. This package does not expose a general deepcopy adapter.
Unknown mutation names fail; extending the sixteen-source-function contract
requires new pins, write-footprint review and complete differential checks.

## Why the original decisions are preserved

The pinned predicates use the fixtures' values and builtin types, not container
identity. `frame_boundaries`, `bind_events` and `expected_tail` build their own
state, cursors, sections and outputs. `restore_control` retains its own original
small deepcopy before reconstructing the old gate sequence. Native checking
constructs circuits and uses the unchanged PR3218 exact comparator; it does not
write the input records. These are source-specific read-only obligations, not a
claim about all future audit functions.

Consequently the path-copy lemma supplies the same nonvacuity comparison and
the same predicate input values as full deepcopy. The exact original predicate
and named-error check still execute. All 32 actual optimized mutant payloads
are additionally compared with the original mutation applied to a complete
deepcopy. This comparison examines the entire word and data with Python value
equality, not just the changed field or a receipt digest. The differential mode
is intentionally slower and is part of the registered verification command.

Every complete execution also serializes each original fixture before its
audit and after all its controls, comparing the complete bytes exactly. This
uses pickle protocol 5 only on trusted in-memory JSON trees; no pickle is loaded.
The comparison is within one process, not a cross-version certificate or hash
acceptance test. A persistent unplanned write into a shared original cell fails
this guard. The written footprint argument supplies isolation; the guard is a
second failure detector, not a proof for arbitrary future mutation code.

## Source-bound integration and measurements

The new wrapper retains PR3218 byte-for-byte and installs four unique hooks in
its private PR3202 verifier: replace the two whole-fixture copies; observe the
mutated payload; begin an original-fixture guard; end that guard. It also adds
the callback bindings in a private copy of PR3218's wrapper. Mutation bodies,
predicates, complete receipt comparison, native comparator and source bindings
are unchanged. Each hook must occur exactly once. Executed source hashes are
recorded separately from the retained originals.

All three timing modes execute these same hooks and guards. The only copy
choice is original deepcopy, jackmgaller/#1939's unchanged checked-marshal
function, or the new path copier. The credited function is extracted by AST
from its authenticated source; its CLI monkeypatch and assertion requirement
are not invoked. No process-global `copy.deepcopy` replacement occurs.

BENCHMARK.json compares complete results, original-fixture return, every
mutation name/write footprint, and all actual circuit-pair decisions. It uses
nine fresh serial processes in alternating order. Peak RSS covers each whole
process. Timings are local observations without a CI threshold. All modes
exclude native artifact generation and include source authentication, snapshots
and the added fixture guards. They do not measure integer multiplication.

Full deepcopy visits every mutable fixture descendant for each mutation. Path
copying visits ancestor containers and the selected leaf, plus the original
record-selection scan. It still copies an event list's outer pointer array;
this is not a constant-time persistent-array implementation. All original
event/frame calculations remain. No predicate result or acceptance is cached.

## Verification boundary

The executable controls cover 100 deterministic generated tree/path cases
(seed 21), whole-list splicing, the credited full copier's alias preservation,
shallow nested-write leakage, an out-of-footprint write, a wrong complete mutant,
an unknown mutation, invalid leaf type and three corrupted hook locations.
Separate source-corruption tests change the retained checker, exact comparator
and live packed kernel. Optimized Git-free exports exercise the complete audit.

The tree lemma is a written argument; the complete 32-case differential replay
is finite evidence for this source integration. Neither is a proof-kernel
verification of the multiplication theorem. PR3202/3218's full native-prefix,
physical-owner, precision/tape, recursive implementation and supplier/outer
obligations remain outside this package. Concurrent PR3208 separately audits
R2 cleanup; no coverage or speedup for that caller is claimed here.

Tekalign (@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
