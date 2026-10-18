# A sound all-source P104 memory relaxation

The repaired PR3182 subspace-memory recurrence contains every source-to-target
support path of a finite linear correction program under its stated monotone
common-frame contract. This package proves that implication in both memory
modes and checks its binding to the pinned routine.

PR3214 found that the original output loop retained only the first eligible
source and explicitly left the repaired recurrence's soundness open. The new
result is the written support-inclusion theorem in [PROOF.md](PROOF.md).
It gives missing-pair exclusions a precise valid scope. It does not construct
a correction, improve kappa, or update the selected result.

## Exact scope

Sources are immutable, targets are unread, and independent helper dirt has no
source dependence. Every helper follows one nested full flag without a descent
or a change of frame at fixed dimension. Transfers occur only at equal actual
frames; there is no additional source-dependent storage. Source and target
snapshots are complete but untimed in the relaxation. The full assumptions,
including excluded layers zero and nine, are stated with the theorem.

The key argument compresses a path's same-dimension relays to a single
permitted contact because all those relays use one actual frame. A freshly read
source can be read directly by the final receiving helper in the complete
untimed snapshot relation. A remembered subspace remains inside the actual
frame along the path, and replacing it with a smaller representative preserves
all future tests. Unioning every eligible output source then proves inclusion.

The recurrence can admit paths whose flags, times or coefficients cannot coexist.
Passing it does not establish a correction program. Reading Y, mutable X,
helper descents, correlated auxiliary inputs and unequal-frame operations
change the theorem's contract.

## Evidence and reproduction

From the repository root, Python 3.12 and the standard library are sufficient:

```sh
python3.12 -B scripts/research_package.py --package research/p104-memory-relaxation-soundness
```

The registered commands are also usable directly:

```sh
python3.12 -O -Werror -B research/p104-memory-relaxation-soundness/verify.py
python3.12 -O -Werror -B research/p104-memory-relaxation-soundness/controls.py
python3.12 -O -Werror -B research/p104-memory-relaxation-soundness/test_cli.py
```

The primary replay authenticates five inputs and compiles only nine named pure
functions from PR3182's authenticated source, with exactly the output-loop
break removed for the repaired comparator. It does not import that package or
its consumer-budget dependencies. Frozen predecessor files remain unchanged.

A separate point-set implementation agrees with the repaired bitmap routine on
all 104 PR3019 output supports in both modes. It preserves PR3214's required
`X1 -> H201 -> Y98` path at source cut 594 and target cut 4058, checks its full
nested flag, and independently reconstructs `C[98,1]=-1/2` from the root fixture.
[RESULT.json](RESULT.json) retains the complete output masks and path evidence.
The path does not restore arbitrary helper dirt; it calibrates a relaxation
that already drops restoration.

The small exhaustive check uses all 21 flags in `F_2^3`, all 441 ordered pairs
of helper flags, and all 16 revelations of their intermediate frames. All 14
nontrivial subspaces are source and target snapshots. Each of the 7,056 interval
fixtures retains every path in a separately built actual-frame BFS, in both
memory modes. When every frame is fixed, the results equal that BFS. The
archived repaired core agrees on every fixture. This is not a P104 matching
census. [CONTROLS.json](CONTROLS.json) records the domain and behavioral controls.

Other checks cover immediate read/relay, all-source output union, a restored
six-ADD dirty shear, an incompatible retained history, subset-minimal pruning,
read-only Git-free optimized replay and four rejection groups. Source-byte
drift, typed receipt changes, duplicate JSON keys and memory exhaustion reject.
Default replay reads committed receipts; `verify.py --emit` prints a candidate
receipt without writing files.

The proof and checks are internally reviewed research evidence. They are not
independent human or formal-kernel verification. The implementation checks share
a model contract; the literal BFS and separate point-set recurrence do not
prove the universal theorem by enumeration. No complete native, hosting,
precision, recursive-consumer or selected cold replay is included.

## Sources and credit

Scientific base is canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`,
priority revision 6. [SOURCES.json](SOURCES.json) pins the five live inputs and
historical task/selected-record provenance. The live PR3182 routine is retained
from `ad848966cd62e13de5ad8d4b5169c221d74d2fcd`. PR3214's exact handoff head is
`faa6323371db1c5fbb43ab04c6e00715d2328bc6`; its text is context, not a runtime
input. [TASK.json](TASK.json) records the scoped task and overlap coverage.

Credit dcharb78/PR3182 for the memory mechanism; commdata2338/PR3214 for the
output repair, literal path and released soundness handoff; Nick Petalas's
PR2981/2996/3013/3019 endpoint and support work; Ross Richardson's PR3032
flag-consistency proof; Cinna Davis's PR3124 cycle work; Arham Tahir's fixed-flag
checks; and the retained Rohan Arun, Chafik Boukhalfa, Adam Gall, Josie Elliston,
Ali Romman and geometry/native/compiler lineage. The earlier output repair,
path witness, endpoint covers and matching are not claimed as new.

New proof and checks by Nick Petalas. Apache-2.0. Substantial automated assistance
was used in analysis, implementation, verification and writing. No independent
human review is claimed.

## Open next questions

Can one changed, named collection pass this necessary test and then supply
simultaneous full flags, chronological coefficients and restored dirty state?
Start by binding its compatible endpoints and exact source/target snapshots,
then attach times before coefficient synthesis. Its complete physical consumer
invoice remains a blocker. A passing support relation alone does not justify
another construction round. The family decision here is to finish the
recurrence implication and stop.

## Engineering limits

Separate Before Serializing Shared State kept the work in its own package,
branch and cache directory; only Git metadata operations use the common OS
lock. Build the Lever made the support proof replayable. Prove It Works required
literal geometric checks, archived-code correspondence and the public command.
Unslop guided the scope statements.

Power of Ten inspection covers the four new Python files. New functions are
below 60 physical lines, loops have fixed geometric or input-cap bounds, checks
use exceptions that survive `-O`, and warning/lint checks cover new code.
Receipt comparisons preserve JSON value types.

Rule 3 deviation: Python's managed sets, dictionaries and integers allocate
during replay. The test is a finite batch, bounded by eight layers, 208 helpers,
104 sources/targets, ten snapshots, 512 frame points, and 16 memories per
helper/source; capacity exhaustion fails. Files are capped at 2 MB. The actual
source-bound receipt records the maximum retained antichain. A resident or
variable-size service would require a fixed arena and a separate memory budget.

Rules 8 and 9 deviation: the comparator compiles nine explicitly named functions
from SHA256-authenticated source and removes one structurally checked `break`.
It bypasses import caches and executes no predecessor module top level. Small
fixtures replace only its interval accessor with one bounded local function.
The generic registered runner supplies a private cache namespace for ordinary
package imports; direct commands retain Python's normal local-import semantics.
A production library adoption should expose a static support API instead.
The retained routine's 79-line function is frozen predecessor code; the separate
implementation splits acquisition, relay and delivery into bounded functions.
