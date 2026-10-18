# Scope and implementation checks

Build the Lever changed the deliverable from a frame observation to a
retained exact replay. Prove It Works required the literal attaining witness,
source authentication and committed-byte checks. Power of Ten kept iteration
bounded and runtime invariants active under Python optimization.

The initial target was support thirty instead of twenty-nine, with endpoint
allowance 120. The arbitrary-puncture attempt gave only 120; the orthogonal
frame argument gave 122. A final publication refresh found concurrent PR3205
already proved that shortening theorem by a complete frame census. The final
contribution is therefore the distinct analytic Parseval proof, replacing
that census as a mathematical dependency. No new shortening range or exponent
is claimed. The append-only [decision log](decisions.tsv) retains the original
attempts and the scope change. The calculations are exact, with no numerical
noise or runtime-performance claim.

New code is confined to `verify.py` and `test_verify.py`. There is no new
shared API or dependency. Predecessor source remains unchanged. Functions
are below sixty physical lines after formatting. State stays in local values,
apart from immutable source paths and the literal eight-root witness.
Failures raise exceptions and produce nonzero exits. Output is opened
exclusively only after successful verification and must be outside the checkout.

The verifier has no frame search. Root construction uses 56 signed coordinate
pairs and 256 sign vectors. Cost vectors have 120 entries and six evaluations
per entry. Scalar checks enumerate 210 sorted integer six-tuples, with fifteen
pairs each. Formal frame costs have 165 sorted eight-tuples. The Gram matrix
has 25 entries; the witness Parseval matrix has 64, with eight terms each.
Only one literal frame is checked. Thirteen authenticated input files are
each capped at 2 MB, and the workspace/export must remain stable during checking.

Runtime checks enforce the source inventory, complete E8 root set, exact
spectrum, variance identities, symbolic lower bound, orthogonality, matrix
normalization and literal costs. Twelve behavioral groups include incomplete
geometry, a nonorthogonal frame, impossible costs, source and mixed-premise
mutations, and the support-thirty-one equality boundary. The registered replay
also reruns both inherited mixed-edge implementations for the known shortening
corollary; direct checks authenticate those inputs without executing them.

The following Power of Ten deviations are limited to the new Python code.

- Rule 3, fixed allocation. CPython allocates tuples, integers and containers
  during verification. The fixed capacities above bound live mathematical
  data; input parsing is separately bounded. A fixed-storage native program
  would be needed for a constrained runtime. Full replay and invalid-domain
  controls exercise the current bounds.
- Rules 8 and 9, runtime dispatch. Standard-library JSON, argparse, Counter
  and unittest use runtime dispatch. Mathematical calls have explicit targets
  and no generated code, recursion or dynamic evaluation. Test mocks have
  two local read targets and restore them on exit. JSON's runtime parsing
  internals are inherited platform behavior; parse failures propagate before
  output is opened. Revisit this scope for a different runtime or a hostile
  concurrent-file-mutation requirement.
- Rule 10, diagnostics. The full Ruff diagnostic inventory was inspected.
  Remaining reports concern annotation/docstring and package/header policies,
  magic numbers, unittest-versus-pytest style, comma style and the intentional
  success print. Adopting those repository-wide conventions is outside this
  isolated proof contribution; no diagnostic is suppressed in code. The
  selected `E,F,I,B,UP,PLE,PLW,RUF` rules, formatter, compilation and
  warnings-as-errors replay pass. Reassess broader style diagnostics when
  the repository adopts a common Python policy.

No code-owned control-flow cycle, unbounded retry, external subprocess,
mutable shared state or unchecked status return was introduced. The registered
runner starts inherited and new commands serially with bounded timeouts.
Its private bytecode caches and the commands' `-S` option avoid installed-site
module collisions. Source integrity and finite checks do not settle the whole
decoder or supplier theorem.
