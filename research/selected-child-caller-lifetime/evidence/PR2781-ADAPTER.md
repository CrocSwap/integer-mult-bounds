# Complete numerical lifetime of a selected BIT adapter coefficient

For unchanged PR2697 `numeric.selected_coefficient`, the **adapter branch** needs
at most **37,672 additional residue Words and 22 additional index Words** above
every numerical Word live on entry. This covers Callback initialization, current
projector preparation, form construction, evaluation and cleanup. A complete
literal rank-42 call attains the residue bound. The index bound is conservative;
no index sharpness claim is made.

PR2770 bounds an initialized evaluator and PR2778 bounds isolated constructors.
This joins them at the actual closed entry point, including the projector and
callback residents that coexist with construction. Other node/route residents
remain explicit entry charges. This does not establish a whole-node reserve,
physical tape implementation, supplier admission or new kappa.

## Contract and sources

Fix m=64, good rank 1 through 42 or a valid fallback branch, an initialized Ring
and two arenas. The modulus is an admitted odd prime power with the source
arithmetic margin. Program, fields, fixed source specifications, plan and request
satisfy the source's chronological, branch, pivot, encoded-word and address
contracts. `request.kind` is `adapter`. The early delegated child branch is
outside this result. Execution is sequential, successful and has sufficient
arena capacity. Borrowed numerical Words, input tapes and permanent templates
enter with their heads at cell 1.

Let L_R and L_I count **all** live numerical arena slots before entry, including
the Ring modulus and one, request coordinate, suspended callers, unrelated
matrices and retained bank numerators. The live slot counts obey

```text
residues <= L_R + 37672
indices  <= L_I + 22.
```

Successful return preserves entry slots, bytes and heads, restores program/field
tapes, and leaves exactly one additional owned residue result. Freeing the result
restores the entry live sets. With b_R and b_I bits per Word, the permanent arena
templates give this bound on occupied non-LEFT numerical symbols:

```text
(L_R + 37673)(b_R + 1) + (L_I + 23)(b_I + 1).
```

Serialized inputs and continuations, LEFT markers, erased backing capacity,
Python heap objects, physical banks and movement costs are separate charges.

Jose Manuel/jmbarrancoml's [PR2697 at a53fdf4](https://github.com/CrocSwap/integer-mult-bounds/tree/a53fdf4bcbe33c6732f0bec1badc8c023380f9d1/research/selected-bit-node)
supplies six unchanged runtime modules. [SNAPSHOT.json](SNAPSHOT.json) records
original paths, Git blobs and SHA256 hashes. The complete [notice](vendor/NOTICE.md)
is unchanged. Every export authenticates before any executes; compilation uses
authenticated bytes and bypasses bytecode caches. [SOURCES.json](SOURCES.json)
pins the historical catalogue and selected record. Runtime dependencies are the
package-local authenticated exports, so a later selected-record change alone
does not invalidate this frozen-source result. This audits a pending source and
does not assert selected admission.

## Lifetime proof

Nick Petalas's [PR2759](https://github.com/CrocSwap/integer-mult-bounds/pull/2759)
supplies ten additional Words for primitive inversion.
[PR2770](https://github.com/CrocSwap/integer-mult-bounds/blob/687372b807f5ec635f6a748c2585fc0090a7dc2a/research/selected-callback-word-liveness/README.md)
supplies `Callback.weight` excess bounds `5m²+10` residues and ten indices, and
retained form inventories.
[PR2778](https://github.com/CrocSwap/integer-mult-bounds/blob/6dfdbaa004540f5d89f390a9a78fa38c46d225d6/research/selected-form-construction-storage/README.md)
supplies these constructor excess bounds above all their entry residents:

```text
G(r) = 6m² + 4mr - r² + 10
F    = 8m² - 2m + 5, for m=64.
```

The unchanged implementations are exported here. Composing their actual
allocation/free order gives this table, always above the closed call's entry.

| Phase | Residue excess | Index excess |
| --- | ---: | ---: |
| Callback construction and validation | 12 | 15 |
| Current projector preparation | `4m²+12` = 16,396 | 11 |
| Good form, projector retained | `m²+G(r)+2`, at most 37,672 | 7 |
| Fallback form, projector retained | `m²+F+2` = 36,743 | 7 |
| Initialized adapter evaluation, worst fallback | `9m²+13` = 36,877 | 22 |

`Callback` owns two residue Words, `high_cap` and `root_unit`, and six index
Words, `root_size`, `depth`, `final_size`, one, two and 64. Ring Words already
belong to L_R. Prime-power validation needs at most seven additional residues:
qword, high_cap and the current test can coexist with four division Words.
Root-unit inversion coexists with high_cap and root_unit, giving twelve.
Chronological validation frees each previous step's addresses before continuing.
Its largest index case fits fifteen: three constants, root size/depth, current
and count, level, parent and child, f, and four half-division temporaries.
Seeks and field-code checks fit within this allowance.

`selected_page` constructs columns using at most four division Words, then a
temporary scope. `Callback.prepare` includes the high matrix, header, constants
and inverse. Its existing excess bound is `4m²+10` residues; adding the callback's
two gives 16,396. Only the m² projector survives. The scope is freed before form
construction. Seven index residents remain; preparation's seek needs at most
three more, so eleven is conservative.

Both constructors retain that projector. Adding its m² Words and the callback's
two residues to G or F gives the construction rows. `7m²+4mr-r²+12` increases over
ranks 1 through 42 and equals 37,672 at 42. Fallback reaches only 36,743.
Neither constructor allocates index Words.

The projector is freed before Page construction. Page owns three geometry
indices and borrows columns, bringing the callback/Page index total to ten.
The retained good form has `m²+2mr-r²` residue Words; fallback has `4m²`.
An adapter can retain the first bank result during the second weight evaluation,
so its residue bound is

```text
stored_form + 2 callback residents + 1 retained numerator + 5m² + 10.
```

Fallback gives 36,877; good ranks at most 42 give at most 28,201. Ratio arithmetic
and optional negation are smaller. A bank retains base and position during the
ten-index weight evaluation, giving `10+2+10=22` indices. Tail and zero
coefficients need less. Numerical Words do not accumulate with chronological
depth. Serialized continuations remain separate.

Successful cleanup closes the form, frees columns and closes the callback.
Weight stacks are empty. The returned result is the only new numerical Word.
The outer `selected_coefficient` ValueError handler also rolls back to its entry
sets and rewinds input tapes, including failures before `selected_page` returns
its tuple. Controls check that behavior before external fixture cleanup. This
does not establish arbitrary Python exception safety or constant-size stacks.

### Literal attainment

Over F3, start with the identity raw header and change its block on coordinates
0 and 42 to `[[1,1],[1,2]]`. With rank 42 and identity fixed preparation,
`H E_42 H^-1` has the all-two rank-one block on those coordinates and diagonal
ones on coordinates 1 through 41. This is exactly PR2778's sharp good projector.
Here the source constructs it from serialized fields, so its m² Words and the
two callback residues actually coexist with G(42). The complete closed call
attains **37,672 additional residue Words**, returns coefficient two, preserves
borrowed state and erases its temporaries. The fixture does not establish
selected-catalogue membership or the outer large-prime coupling. The universal
bound rests on the source lifetime proof.

## Replay and controls

Python 3.12, standard library only, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -Werror -B \
  scripts/research_package.py --package research/selected-adapter-numerical-lifecycle
```

Git-free direct replay uses `verify.py` and optimized `test_verify.py` here.
`verify.py --emit` prints a receipt without writing. [RESULT.json](RESULT.json)
is compared as complete typed JSON on ordinary replay. Fixtures execute literal
64-dimensional source over F3 and Z/9, ranks 1 and 42, depths zero through four,
serialized unit/Pair ancestors, head/tail/shear and zero coefficients, reversed
adapters and unrelated borrowed residents. An independent integer oracle supplies
fallback itineraries and expected results without source binary arithmetic or
matrix routines.

Every source allocation checks its budget. Separate scans compare live sets
with literal occupied cells, including retained erased slots and templates.
Successful calls check results, exact owned output, entry bytes/heads and input
tapes. Controls reject a one-Word-underbudget good call, insufficient fallback
and index budgets, wrong Page binding, wrong expected scalar, borrowed corruption,
entry-head violations, source corruption and typed-receipt changes. They check
repeated calls and source rollback before fixture teardown.

Finite replay supports implementation and residue attainment. It does not
exhaust adapter branches or chronological programs, execute the selected GL64
Boolean payload, or formally verify the proof. No selected cold replay,
independent human review or hosted CI pass is claimed.

## Scope and engineering

[TASK.json](TASK.json) records the changed picker scope, exact dependency heads,
overlap and freshness. The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18959295)
follows PR2778's released numerical-overlap handoff. David Arias's PR2753 already
supplies a coarser all-size logical inventory. Active physical Frame/bank and
compatible-row-padding tasks are separate. Metadata searches exclude arbitrary
diffs and do not establish novelty.

Build the Lever led to an authenticated closed-call census. Prove It Works
required the actual entry point, occupied cells and cleanup before external
rollback. A separate internal source review derived 37,672 and tightened the
initial index allowance from 24 to 22.

Power of Ten bounds new fixtures to dimension 64, residual dimension 128, depth
four, two repeats and arena capacities 65,536/256. New functions fit 60 physical
lines; runtime checks remain active under optimized Python. Managed-runtime
deviations to rules 3, 8 and 9 cover Python heap allocation, compilation of six
authenticated modules and temporary instrumentation of one allocation method.
Fixture sizes bound live data, the manifest bounds process runtime, and the
method is restored on every exit. This is numerical-content evidence, not a
fixed-heap or physical compiler claim. Replace the measurement arrangement when
the physical allocator is admitted. The loader's specific S102 annotation records
the same authenticated-compilation deviation; source bytes are not arbitrary
runtime code. Frozen source implementation is unchanged.

The expansion decision is narrow and finish this audit. The allowance cannot
replace L_R/L_I with zero or justify further supplier construction without the
complete caller and physical ledger.

## Open next questions

1. What numerical entry residents coexist at complete caller/route coefficient
   sites? Trace actual constants, high matrices and suspended state before
   substituting this allowance. Missing simultaneous inventory blocks a
   whole-node reserve claim.
2. Can that combined inventory use physical shared banks within the required
   cost? Bind the active Frame/bank role map, then charge templates, markers,
   backing slots, erasure, movement and child grants. Logical content alone
   does not establish physical placement or the stronger time recurrence.

## Credit

Nick Petalas, Apache-2.0. Jose Manuel/jmbarrancoml supplies the unchanged PR2697
algorithms and retained source/control/normal-form/hosting lineage; its complete
notice is preserved. Nick Petalas's PR2759/2770/2778 supply the primitive,
evaluator and constructor components. The authenticated loader and census
pattern are adapted from those components. David Arias's earlier PR2753 logical
inventory retains separate credit. This contribution adds the closed-lifecycle
composition, actual-entry attainment, independent expectations and rollback controls.
