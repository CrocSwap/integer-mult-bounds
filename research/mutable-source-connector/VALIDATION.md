# Execution record and limits

Base and refreshed upstream main:
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Host: Windows 11, bundled CPython **3.12.14**, standard library; Git.
This is local execution, with no independent human or proof-assistant review.

The following commands pass from the repository root:

```sh
python3 -I -O -B research/universal-connector-boundary/verify.py
python3 -B scripts/research_package.py --package research/mutable-source-connector --check-only
python3 -B scripts/research_package.py --package research/mutable-source-connector
python3 -B scripts/verify_selected_result.py
git diff --cached --check
```

The first command returns the inherited positive control:

```text
PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182
```

The registered replay checks metadata/source pins and executes all three new
commands, including their isolated optimized subprocesses. Its key results are:

```text
PASS_MUTABLE_SOURCE_CONNECTOR B=10 A=62 XOR=12 census=2600 primitives=2028_vs_2072 controls=9 no_new_kappa
PASS_MUTABLE_SOURCE_ORACLE census=2600 dense_cases=3024 dirty_probes=24 complete_tariff=2760_vs_2812
Ran 4 tests
OK
PASS_REGISTERED_RESEARCH_PACKAGE research/mutable-source-connector outcome=completed
```

The primitive counts combine arbitrary-map calls and identity-row XORs only
under the explicitly stated unit macro tariff. PROOF.md separates these types
and includes internal nodes, root instruction charges and the general price
inequality. No scalar-runtime conclusion follows from those count strings.

Coverage:

- Exact free noncommutative linear maps for all 40 arbitrary incoming rows,
  forward and inverse, for the candidate and both literal predecessor repairs.
- All 2,600 normalized nine-point sets; independent integer Walsh
  autocorrelations reproduce the complete six-bin coverage histogram.
- Independent iterative emission reproduces both complete word digests and
  counts all 648 internal candidate nodes and 666 comparator nodes.
- Six dense F2 matrix banks, dimensions 1,2,3, all 480 basis inputs and 24 mixed
  dirty inputs, in both directions for three words: 3,024 executions.
- Nine primary mathematical/admission rejection controls; separate concrete
  common-B failure and noncommuting-factor controls in the dense oracle.
- Four package test groups: optimized source-export relocation and default
  no-write replay; byte-identical certificate regeneration; occupied output
  preservation; five semantic certificate corruptions; changed/missing source;
  and omitted source pin. Rejection cases invoke the actual CLI.
- The selected-record integrity checker passes with the existing exact kappa
  and source inventory. The selected source-bound research baseline also passes,
  identifying the complex side as binding.

The first package test attempt failed before mathematical execution in its
relocated subprocesses: the desktop's redirected Windows system temp directory
allowed creation of a temporary directory but denied its children/cleanup.
The tests now use a fresh sibling scratch directory, check its resolved parent,
and clean only that generated directory. The complete registered replay passes
after this portability fix. An earlier draft metadata check rejected a prose
`outcome`; it was corrected to the required `completed` enum with the prose
retained separately. These development failures are not mathematical passes.

The bounded 500,000-candidate nested-four-shear pilot found maximum coverage 31.
It was **not** exhaustive. The final proof instead normalizes the complete
nine-point problem and gives a ten-point attaining construction. No complete
search or lower bound for the source-XOR count is asserted.

Final overlap refresh: **821 open PRs**, including drafts, complete public REST
pagination at **2026-10-13 23:03:34 UTC**. The repository helper searched those
titles/bodies and local top-level notes/ledger at 23:04:19 UTC. It reported 57
broad matches, many containing the generic phrase "mutable source". Relevant
predecessor/parallel heads are recorded in TASK.json. Public discussion listing,
handoffs and mechanism-proposal pages were re-read; complete Discussion
pagination and a connected Discussion-write tool were unavailable. No evidence
from pending PRs is imported. Overlap checks do not prove novelty.

Not run or established: the selected supplier cold replay, native supplier
emitters, complete repository suites, Lean, hosted CI, a physical supplier
instance of the changed interface, source ownership/frame admission, fixed
precision/tape realization or analytic transfer. The word and proof are exact
F2-linear interface results, not a complete multiplication theorem. The
selected frontier, upstream and frozen predecessor inputs are unchanged.
