# Validation and implementation constraints

## Scope and commands

Registered replay passed on macOS 27.0.1 arm64 with CPython 3.12.15:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python -Werror -B scripts/research_package.py --package research/selected-add-counter-backing
```

The absolute interpreter is the local Python 3.12 environment. The portable
command in README.md uses any Python 3.12 interpreter. The registered commands
run the primary native census, separate write-observed census, and five tests.
The primary result has 63 ordinary fixtures, nine embedded controls and an
additional successful callback-escape fixture. The separate census has 162
fixtures, including modulus four. All source executes from authenticated bytes.

A relocated copy with no Git checkout, network or third-party modules passed all
three direct commands on CPython 3.14.8 with `-I -O -Werror -B`. Its package files
were read-only, and a complete before/after SHA256 inventory was unchanged.
Warnings are errors and verifier contracts remain active under optimization.
The Python source was also compiled in memory to check syntax without bytecode
writes. Hosted Linux CI is not claimed as a local result.

## Separate derivation and review

A separate internal reviewer derived the constructor-overlap formula directly
from the pinned native source and ran 162 native fixtures using a write-observed
weak-set census. The parent inspected that check, adapted its observer into the
registered [independent.py](independent.py), and reran it. It shares source
authentication with the primary checker, but does not call the primary formula,
fixture or constructor-return census. Both procedures observe the same native
implementation, rather than constituting independent compiler implementations.

Review identified the need to prohibit callback capture of native frames as
well as its own Counter objects. The proof retains both conditions. The primary
check supplies the concrete 82-cell retained-Counter counterexample; the
no-frame-capture premise is justified by the written lifetime argument. No
independent human or proof-assistant review is claimed.

## Engineering choices and constraints

Build the Lever changed the deliverable from a prose estimate to a source-bound,
rerunnable census and literal rejection controls. Prove It Works required actual
native ADD endpoints, an independent address oracle, and a relocated replay.
The ten Power of Ten inspections are scoped to the new checker and its five
immutable source exports, without rewriting frozen predecessor implementations.

- New control flow is structured and nonrecursive. The callback targets are the
  local fixture constructor, coefficient provider and write observer. Original
  methods/module bindings are restored in `finally` blocks.
- The primary fixture list has exactly 63 entries. Each primary fibre is at most
  40,000 bits, its residue width at most 64, and callback backing at most 60 cells.
  The independent census is exactly 162 entries, with fibres at most 1,296 bits.
  The source's binary countdown loops consume these finite fixture extents.
  The metadata runner separately enforces 120-second command timeouts.
- Weak census metadata retains at most eight live Counter references, each weak;
  the independent observer permits six. Dead entries are removed on sampling.
  The receipt stores scalar lengths and source-site names, with no Counter or
  frame roots. Ordinary return checks verify the disappearance of Counter roots.
- Each new function is at most 60 physical lines. Contracts reject invalid
  numeric domains, source mutations, unexpected inventory, wrong endpoints,
  incorrect peaks and typed receipt substitutions. They use ordinary exceptions,
  so optimization cannot disable them.
- Every proof-relevant native result is consumed. The deliberately uncounted
  numerical arena, source extents and payload arrays are explicitly separate
  cohorts. Numerical live slots are checked against the complete entry baseline;
  that check does not assert numerical backing reclamation.

The managed Python runtime requires dynamic allocation. This is a deviation
from fixed steady-state allocation, confined to the verifier and native fixture
execution. Finite fixture sizes, weak-reference inventories and command timeouts
bound the work. It is not a fixed physical-tape implementation. Replacing these
fixtures with an actual physical compiler requires a separate memory contract.

Authenticated source execution uses `compile`/`exec` for exactly five modules,
with fixed order and checked source digests/Git blobs. This constrained dynamic
loading avoids unauthenticated bytecode-cache reads. Instrumentation replaces
one known constructor or one known module Tape binding, then restores it. Those
are bounded deviations from static dispatch needed to observe unchanged source;
new production dispatch behavior is not introduced. Future native-source changes
require new source pins, reinspection of allocation sites and regenerated
receipts. Existing source functions/loops remain byte-identical and are covered
only within the enforced finite fixture bounds.

## Unrun obligations

No complete selected GL64 payload execution, cold frontier replay, all-size
caller proof, total private-A bound, numerical backing bound, field/program
storage, exception cleanup, physical placement/reuse/movement or multiplication
transfer was run or established. Supplier admission and the selected frontier
remain separate maintainer decisions.
