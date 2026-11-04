# Validation and trust boundary

The source certificate contains 19,002 events in 96 chronological chunks:
4,291 scalar-identity frame moves, 14,693 parity-sensitive additions,
nine copies, and nine erases. Lean verifies two complete trajectories:
zero and `1 << 243`. The full final integer bitset is unchanged in each
case, and the cumulative numeric-bound/copy-cleanliness/erase-equality
guard is true. Each checkpoint is checked by `decide`; none uses native
evaluation as a proof oracle.

The fresh offline runner compiles seven modules with official Lean 4.33.0,
compiler commit `d8b18978322de05a8f3dba51ef03cf5461676c17`, trust level zero.
It uses only installed Std and freshly built pinned dependencies. The
manifest and replay receipt record all sources, imports, timings, and
transitive axiom closures. There are 422 named declarations including
generated checkpoint/composition theorems and inherited dependencies.
Only `propext` and `Quot.sound` are allowed. There are no project axioms,
`sorry`, `native_decide`, or reused project proof binaries.

The three negative controls require mathematical rejection by Lean:

1. Disable actual event 218, the XOR `126 ← 126 + 243`, and assert its
   containing chunk still has the original checkpoint endpoint. This false
   claim is rejected. Python replay of the whole mutated word independently
   finds final support `{126,243}` with clean-operation guards still valid.
2. Assert that the actual helper-basis input instead exits as zero.
3. Assert that ignoring the second retained coordinate residual preserves
   the concrete observation. This small coordinate demonstration uses Fin 3;
   it makes no assertion that that field is admitted by the physical supplier.

The separate source checker verifies four pinned source files, both raw
template hashes, the original binary records, all frame/state metadata, the
two selected owner rows, and every projected Lean event. An independent
Python all-column replay checks the full normalized scalar endpoint over
987 inputs, equal-frame ADD annotations, frame ranks, and private-center
lifetimes. These Python results are in source-check-result.json; they are
distinct from the two kernel-checked trajectories. Generator output also
matches the checked SourceWord.lean byte for byte.

The independent review used a separate fresh build of the six proof/dependency
modules before the final Audit module was added. Its results and exact
snapshots are in REVIEW.md and independent-build.json. The final replay
checks the exact package snapshot, including the complete axiom inventory.

These validations do not derive the physical observation hypotheses in
SourceWitness, establish arbitrary dirty-input behavior in Lean, or implement
numeric owner isometries. The result is a failed direct instantiation under
the source's declared geometry, together with a checked actual-source
trajectory. It does not certify a physical failure of PR442 or any κ bound.

The prior PR442 full replay and required baseline checks remain documented in
the sibling whole-residual package. No inherited implementation changed.
The full repository `make verify` remains incomplete because the preceding
session reproduced `joint-dual-verify`'s `AssertionError: Makefile` on clean
pinned main; this additive audit does not claim a passing broad suite.
