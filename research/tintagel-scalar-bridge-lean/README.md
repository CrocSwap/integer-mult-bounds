# Indexed scalar bridge

This packet formalizes the normalized scalar borrowing chain used by the
pinned `bridged.py` source (Git blob
`626a28614b07066528fd5f189d87cffa5015ac60`). Over any abelian group, a
stage-indexed chain on a nonempty finite list of bank pairs maps each `(x,y)`
to `(-y,x)`. Its signed endpoint `(u,v) -> (v,-u)` restores every bank and
the shared helper state, allowing arbitrary correlations among all inputs.

This conclusion **assumes each stage implements its specified complete
normalized forward/backward shear and preserves all live helpers for every
input**. Different stages may use different implementations of those same
external maps. The model does not prove that a physical provider satisfies
the contracts, acts only on the active pair and helpers, or has no aliases.
Physical frames, owners, endpoint operators, scratch lifetimes, costs,
all-size compilation and analytic transfer remain separate obligations.

`BridgeChain.lean` proves the borrowing algebra. `IndexedBridge.lean` proves
composition for arbitrary nonempty finite lists. `SourceBound.lean` contains
the nineteen-operation B3 term, whose equality to the three-pair indexed
chain is proved by `rfl`. Its scalar chronology is
`F1 B1 A12 F1 D12 B2 A23 F2 D23 B3 F3 C23 C12`, with descending cleanup.
Here `A,D,C` each contain two elementary twin additions; Lean calls `D`
`gateB`. The endpoint is signed; an unsigned exchange is not valid in general.

## Source binding and proof boundary

The included source snapshot is never imported or executed. `replay.py`
checks its fixed whole-file SHA-256 and Git blob digest before **hash-locked
selected-AST recognition**, constructs the B3 term, and compares its bytes
to the submitted `SourceBound.lean` before compiling. Recognition covers
selected statements, not all Python semantics. It is not a verified Python
translation. A future source digest requires a renewed full source audit;
merely changing the digest is insufficient.

The B3 term equality and generic list induction are kernel checked. The
general source-loop correspondence is a reviewed mathematical argument,
not a Lean theorem about the Python program. Helper restoration is in
normalized scalar coordinates, not a physical endpoint proof. The explicit
`Invocation` fields remain assumptions even when an axiom report says
“does not depend on any axioms.”

## Offline replay

Requires Python 3.9+ and an **already installed Lean 4.33.0**. No packages,
network access, Mathlib, upstream checkout, or dependency mirror are needed.
Pass the installed toolchain binary, not an `elan` launcher that may download
a missing toolchain. Do not use Python `-O`.

```sh
python3 replay.py --lean /absolute/path/to/installed/lean-4.33.0/bin/lean
```

Optionally add `--receipt /path/to/replay-result.json`. Replay preserves
submitted files, builds the three modules in a fresh temporary directory at
Lean trust level zero, checks all 22 reported transitive axiom closures, and
rejects five mutated candidates: twin sign, cleanup order, unsigned endpoint,
stage index and helper threading. Temporary compiler outputs are removed.
`evidence/replay.json` records the packaged replay; errors there are expected
negative controls, not accepted proofs. `lakefile.toml` describes the same
three-module project with no external dependencies; direct replay avoids
toolchain installation through Lake/elan.

New theorem axiom sets are recorded in `evidence/source-binding.json`:
the two B3 correspondence/reduction results use no axioms; B3 endpoints and
generic scalar composition use `propext`; the generic correlated signed
endpoint additionally uses `Quot.sound`. No reported accepted result uses
`sorryAx` or a project-defined axiom. The Lean compiler, installed standard
library, Python execution and reviewed extraction remain trust boundaries.

## Attribution and contribution

This formalizes an existing construction; it claims no new bridge mechanism,
correlated-helper insight, global novelty, or priority. The source header
credits Jacob Sussman's B2 framework. The general bridge is present in
CrocSwap/integer-mult-bounds PR363/373/375 and inherited by PR377/381/390.
The inspected PR390 snapshot already discusses descending cleanup, signed
exchange and correlated helpers. Its heterogeneous physical provider is
not certified by this packet. See `NOTICE` and `evidence/source-binding.json`
for lineage and exact pins. Credits imply no endorsement.

Only the SourceBound documentation comment was changed from the reviewed
proof packet to use the qualified recognition wording; its definitions and
proofs are unchanged. No compiled objects or larger provider claim is included.
