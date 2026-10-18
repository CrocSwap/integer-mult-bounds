# Implementation and verification limits

The package owns only its new directory. It changes no selected record,
frozen input, shared verifier or supplier. The unchanged geometry.py is
byte-identical to its pinned main-branch origin. Its unused flat_capacity
function is retained for byte identity and is not executed by this package.
No binary-flat census is a dependency of the new support theorem.

The primary checker authenticates that copy, checks all finite inputs needed
by the written Weyl-chamber argument, covers A4 stars through four complete
reflection orbits, and verifies the literal witness with rational elimination.
The independent checker reconstructs roots by lattice membership, enumerates
all orthogonal frames and uses separate modular elimination plus exact codeword
relations. It shares the literal witness and written mathematical definitions,
not either primary reconstruction or primary rank implementation.

All new control flow is iterative and bounded. Root inventories have 120
projective and 240 signed roots; every prefix orbit has at most 240 states,
with at most 120 reflecting normals. There are four prefixes, 126 scalar
patterns and 45 frame signatures. Lattice enumeration has exactly 390,625
candidates. The frame worklist has a hard one-million-state budget and fails
closed on exhaustion; a successful complete traversal checks 352,876 states
and exactly 2,025 frames. Indices increase along every extension, so no cycle
or recursion is possible. Witness matrices have at most 17 rows and 112
columns, with bounded integer inputs. Rational elimination has at most 17
pivots. Binary elimination has at most 112 labels and nine bit positions.

Every JSON input is a regular nonlinked file of at most 100,000 bytes. The
retained geometry file is capped at 20,000 bytes. Witness entries and sparse
indices are checked before primary construction. All important checks use
explicit ValueError failures and remain enabled under -O. Mathematical
identities, inventories, Gram matrices and exact inclusion relations are
executable contracts. Output files are external, opened exclusively and
closed by a context manager. Source, coefficient, index, Gram, inventory,
receipt and modular-zero failure controls exercise acceptance boundaries.

The longest new function is the cohesive witness support/rank certificate,
about sixty lines after formatting. It keeps the exact relations, ranks and
support conclusion together. Other new functions fit within sixty lines.
There is no network, subprocess, code generation or dynamic module selection
in either mathematical checker. Counter selectors use bounded five-value
built-in key callbacks; their only targets are the displayed equality counts.

Rule 3 deviation, managed-runtime allocation: CPython Fraction, tuples, sets
and dictionaries allocate during checking. The scope is this bounded finite
research replay. Input sizes, explicit loop/worklist caps and fixed matrix
shapes bound live data. Exact input-entry bounds also bound integer bit lengths
through finite rational elimination. Context managers release files and test
scratch on success and failure. Both CPython versions and the read-only export
checks exercise this path. A fixed-storage native checker would be needed
before deployment in an allocation-free runtime; none is claimed here.

Rule 9 deviation, runtime/library calls: Python built-ins perform bounded
iteration, equality counting and fixed key callbacks. Their targets and input
sizes are explicit above. No unsafe pointer operations are exposed. The replay
and behavioral controls cover all application-defined dispatch targets.

Rule 10 diagnostics: verification uses warnings as errors, optimized failure
controls, compilation of all sources to an external bytecode directory, and
Ruff's E,F,B,UP checks. These are the applicable correctness and Python-version
checks for this standard-library package; no static type checker is configured
by this repository. VERIFY.json runs the mathematical checks and controls in
the registered package workflow. It does not add a repository-wide lint policy
or claim to inspect allocation inside CPython libraries. CHECKS.json records
the exact commands, interpreter versions and local review limits.
