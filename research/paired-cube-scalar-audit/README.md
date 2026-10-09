# Exact scalar audits of the pinned paired-cube schedules

These independent standard-library checkers verify the finite complex and bit
scalar maps at PR178 commit `2c4a380126640abfcdce398ced255d1dd5d1d007`,
which retains PR168's graph, signed word, bit witness, reuse pairs and sinks.
They complement the [precision refinement](../precision-certificate/README.md).
The audit implementations import no upstream producer or upstream checker.
The separate upstream producer supplies a raw complex witness; frozen bit
witnesses are read directly. `SOURCE.json` binds the upstream dependency
closure, audit source bytes and canonical regenerated complex witness hashes.

For the complex schedule, sparse integer numerator vectors with adaptive
denominators cover 1,320 source variables, 1,320 initial target variables and
11,015 independent retained dirty variables. The forward map must be
`(X,Y,Z) -> (X,Y+X,Z)`, and the literally reflected scalar schedule must be
`(X,Y,Z) -> (X-Y,Y,Z)`. Both maps are checked coefficient by coefficient.
The 47 sink substitutions include their pre-shears, redirected writes and
post-shears. Center scatter completes before targets become controls.
The response matrices are rebuilt independently in both original operation
order and phase-first execution order. Four mathematical corruptions must fail.

For the bit schedule, integer bitsets encode all 1,760 source and 18,028
physical dirty columns. Every source and dirty register must restore, and
every target increment must equal its source. Initial target values remain
arbitrary: targets are additive destinations throughout and never controls.
All 3,960 gauge reads are included, comprising 2,200 unpaired reads and 1,760
late paired reads. Read times are execution positions; partner-K injections
follow the corresponding side-root deliveries. Six corruptions must fail.

From the repository root, using Python 3.12 or later:

```sh
python -B scripts/paired_cube_producer.py --work-dir /tmp/paired-cube-audit --output /tmp/paired-cube-audit-report.json
python -B research/paired-cube-scalar-audit/verify.py --complex-work-dir /tmp/paired-cube-audit
python -O -B research/paired-cube-scalar-audit/verify.py --complex-work-dir /tmp/paired-cube-audit
python -B research/paired-cube-scalar-audit/test_bit.py
python -B research/paired-cube-scalar-audit/test_sinks.py
```

On Windows, substitute a writable scratch directory for the `/tmp` paths.
`--bit-only` runs the bit audit without reconstructing a complex witness.
The complex producer must run without optimized Python; the independent
audits and their tests keep all mathematical guards active under `-O`.
Each checker has a 300-second wall limit. Run the full audit with an external
4 GiB memory limit; the complex checker declares that requirement and does
not claim to enforce it internally.

The upstream native gates separately check the actual frame chains and paid
ledger. This package additionally checks sink eligibility and exact scalar
identities. It does not establish general Gaussian/Pauli phases, completed-core
sharing, the literal charge theorem, the uniform weighted compiler or all-size
analytic/precision/fixed-tape interfaces. Those hypotheses remain explicit in
the upstream notes and the precision package's proof document. Finite checks
and AI agent reviews do not constitute a complete theorem proof.

Prepared with substantial OpenAI Codex assistance. Preserve the construction
credits and Apache-2.0 notices in [NOTICE](NOTICE) and [LICENSE](LICENSE).

The complex audit uses PR178's selected physical frames, retaining PR168's
raw DAG, signed word, reuse pairs and all 47 sinks. The source closure also
binds every PR178 addition, including its independently reproduced profile.
