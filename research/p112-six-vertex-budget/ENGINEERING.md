# Implementation and verification bounds

Build the Lever changed the deliverable from a numerical observation to a
retained exact replay and a separate finite algorithm. Prove It Works required
checking the actual profile, every eligible simplex and the publication bytes.
Laziness Protocol kept the change inside one new package and reused pinned
geometry rather than changing shared verification code.

The three new Python programs use direct calls and structured control flow.
Their functions stay below sixty physical lines after formatting. Runtime
`require` checks remain enabled under optimization. They validate the source
and data inventories, graph sizes, exact ranks, cost histograms, quotient
budgets and arithmetic capacity. Mutants and invalid dimensions exercise
the relevant failure paths.

Loop bounds are fixed by the finite instance. The alphabet has 248 lines,
so intersections test 30,628 pairs. The graph has 58 vertices and 595 edges.
The independent pair join tests at most `binom(595,2)=176715` edge pairs.
Primary clique traversal uses the retained 40,000-state bound and a stack
capacity of 407. Rank matrices have at most five rows and eight columns;
integer elimination enforces a 128-bit magnitude bound. Cost vectors have
112 or 120 entries. The six-flat enumeration covers exactly 788,035 spaces.
The profile filter has sizes five through eleven and six permitted weights;
each size has at most `binom(16,5)=4368` multisets. The old-cover comparison
uses at most 462 selections and 729 assignments each. Source files are
limited to 2 MB. The only child process is the pinned BK filter, with a
120-second timeout and checked exit status. Registered commands have
180/120/120-second limits.

Power of Ten deviations are bounded as follows.

- Rule 3, fixed allocation. CPython allocates tuples, arbitrary integers,
  fractions and small containers during the census. All dimensions above
  are fixed; no input can enlarge the mathematical search. Source parsing
  is capped at 2 MB per file. The finite inventory checks and complete
  replays exercise these capacities. A native fixed-storage implementation
  would be needed if this module were reused in a constrained runtime.
- Rules 8 and 9, runtime dispatch. `argparse`, `Counter`, `unittest` and
  temporary mock dispatch are ordinary Python library mechanisms. There
  is no generated code or `eval`. Mock targets are local read functions
  in the controls; production mathematics uses direct calls. A change to
  a framework or serialization boundary requires revisiting that scope.
- Rule 10, diagnostics. A full Ruff diagnostic scan was inspected.
  Repository-wide annotation, copyright-header, docstring and package-layout
  conventions are outside this isolated mathematical replay. Security
  heuristics flag the fixed, authenticated child script; its arguments are
  an array, shell execution is disabled and exit/timeout are checked.
  Numerical constants deliberately stay beside the exact mathematical
  invariants. No warning suppressions were added. New code passes Ruff
  `E,F,I,B,UP,PLE,PLW,RUF` and warnings-as-errors Python checks. Retained
  source files remain byte-identical; broader changes to their style or
  annotations require a separately reviewed source revision.

These are implementation controls, not a proof-kernel verification or a
claim that Python internals have fixed allocation. Baseline provenance uses
Git; standalone mathematical replay uses retained byte hashes. The generic
runner isolates imported bytecode. Direct standalone `-B` invocations assume
a source export without stale caches. A future hostile-code loading claim
would need a stronger loader boundary.
