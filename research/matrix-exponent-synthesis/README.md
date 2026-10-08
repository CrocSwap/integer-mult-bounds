# Strict parameter refinement of PR #62's stacked witness

`kappa = 25508460085039/500000000000000000 = 5.1016920170078e-5`, above `5101691/100000000000`
by `1.0170078e-11`, and also above its old scoped limit `39859/781289859`.
Bit saving is `102039046058023/2000000000000000000`; positive backoff is `h=1e-18`. This uses the same
interval-strip/core-aware-pair graph with PR #57's joint frame compiler.
It is a parameter refinement; no matrix arithmetic count is substituted for
a physical wire profile. New concrete Lean proofs and fresh exact arithmetic
checks accompany the witness; PR #62's reported finite construction validation
is inherited and was not rerun. All-size analytic/compiler/tape hypotheses remain.

## Reproduce

See `candidate/README.md` for the external immutable upstream checkout and
fresh rational replay. `lake build` checks the 171 standalone theorem endpoints,
including 11 concrete frontier theorems; no Mathlib or project axioms are needed.
The original matrix source's separate Mathlib proofs retain historical CI scope.
`python run_checks.py --work work/recheck` replays the matrix/search background.
The matrix and matching receipts are historical checks, not a fresh PR #62
physical network replay. The paper is supplied as LaTeX source without a new PDF.
Earlier PR #58/#60 parameter witnesses are retained in the repository's `history/`.

## Concrete interfaces

`gaussian_matrix.multiply16` evaluates the pinned flat certificate on 256-entry
canonical Gaussian matrices. `hierarchical_gaussian_matrix.multiply16_hierarchical`
retains the actual 48-by-46 DAG sharing. Both align inputs to Pi tag E and return
canonical values on the mathematically necessary product tag 2E. All final
coordinate numerators divide by eight exactly. The shared reference schedule
uses 57,696 component additions rather than the flat interpreter's 193,568;
alignment, normalization and physical tape costs remain separately charged.

`LateQuotient.lean` proves exact recovery modulo 2^p from a denominator-cleared
numerator computed modulo 2^(p+3). `SharpQuotient.lean` proves the numerator-only
precision boundary. `CommutingPhases.lean` proves raw XOR-phase commutation
with equal charged denominator tags and a gauge incompatibility witness.
Exact operator tests also show that mixed linear forms can leave the eligible
phase-child class despite staying inside a commutative operator algebra.

## Search certificates and formal boundaries

The typed catalogue rejects unsupported coefficient domains, mixed leaves
used as block-stable outers, false rank claims and unpaid lifted arithmetic.
Its minima are minima in the supplied finite catalogue, not global records.

`catalogue/MATCHING_SEARCH.md` documents two exact certificate objectives.
The original objective has a maximum-cardinality penalty. The new complete
fixed-target feasibility slack includes external roles and changes in wire
normalization, uses zero-cost private unmatched columns, and permits every
cardinality. Integer primal/dual equality proves the recorded quantized
fixed-DAG optimum; rational intervals bound remaining true-cost regret.
Neither assertion proves global network or exponent optimality.

`MatchingDual.lean` proves generic exact weak duality and optimality from
explicit edge, row and column-partition contracts. `FeasibilityNormalForm.lean`
proves the all-cardinality bookkeeping identity. The finite graph/source binding
is independently checked by Python. `RefinedFrontierCertificate.lean` derives the
current rounded moment envelope and checks the 47 slacks and strict benchmark
comparisons. `FiniteRationalChecks.lean` states the enclosure contracts; the full
transcendental and physical interface scope is stated in the paper and candidate
receipts. `AuditAll.lean` prints dependencies for every standalone theorem.

There are no omitted proofs, new project axioms or native decision shortcuts.
The full multiplication theorem remains conditional on inherited analytic,
ordered-affine compiler, fixed-tape, setup, recovery and eventual-threshold
arguments. Neither finite replay nor the new Lean modules implies peer review
or measured hardware speed.

## Provenance

Alejandro Zarzuelo Urdiales is the author and human developer. His earlier
Archivara exploration and July matrix generalization were developed personally
with multiple AI tools, most recently GPT-6.1 as recorded by the author. The
current synthesis, proofs, implementations and search involved substantial
OpenAI Codex assistance. The actual matrix source and 45-endpoint proof evidence
are pinned at `alejandrozu/openmath-2026-judging`, commit
`7203497dc990e47c2391bff1b9863408d817faeb`, with proof edition
`9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd`.

Community credit and source/license notices are retained in the candidate
README and source manifests. New material follows the destination's Apache-2.0
license; copied original source/evidence retains its attribution and scope.
