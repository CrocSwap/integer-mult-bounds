# Validation and limits

Prepared for @CubeJerry with substantial OpenAI Codex assistance, 2026-11-06.
Author-side AI checks are not independent human or proof-kernel acceptance.

## Environment and actually executed commands

CPython 3.12.14, Linux 6.18.57 x86_64, glibc 2.39. Interpreter:
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
Standard library only. Commands ran from the repository root:

```sh
python3 -I -W error -B research/sharp-net-splitting-tax/verify.py
python3 -I -O -W error -B research/sharp-net-splitting-tax/verify.py
python3 -I -W error -B research/sharp-net-splitting-tax/independent_family.py
python3 -I -O -W error -B research/sharp-net-splitting-tax/independent_family.py
python3 -B scripts/research_package.py --package research/sharp-net-splitting-tax --check-only
python3 -B scripts/research_package.py --package research/sharp-net-splitting-tax
```

All pass. Primary checks took 1.946 seconds normally and 1.925 seconds with
optimization; the separate check took 0.097 and 0.130 seconds. The registered
four-command replay took 4.961 seconds. These are replay budget observations,
not compiler or multiplication runtime claims.

The primary receipt reports 16 parameter pairs, 4,608 literal integer splits,
109 optimized noncandidate comparisons, 16 near-maximizing integer witnesses,
16 exact families, 64 integer attainers, 35 rational-power enclosure checks,
and 13 controls. Six controls reject invalid parameters; seven exhibit exact
counterexamples to undercharges or accounting/quotient mistakes. Its complete
histogram fixture has final gap 34 and sufficient normalized charge 75/98.
The separate checker reports 4,844 rational-radical fixtures and 50 exact
attainers of 8/27, plus its omitted-raw-charge counterexample.

An AST parse of each new Python file passes; every function has fewer than
60 physical lines. Checks use explicit exceptions and remain active under -O.
The all-real proof and its retained completion accounting were separately read
by the lead agent. The lead's completing-square argument and fixture checker
were developed separately from the primary verifier. No human independence or
formal proof-kernel verification is asserted.

## Actual corruption and portability checks

Copies of the package, not publication files, were changed in four ways.
Each rejects under both normal and optimized isolated Python:

| Corruption | Observed rejection |
| --- | --- |
| Force the exact family to use q=1 | `noncandidate optimized quotient` |
| Replace the net numerator with the full split numerator | `noncandidate optimized quotient` |
| Omit the paid completion cost | `literal complete inventory` |
| Alter the frozen #6390 proof text | `frozen source hash mismatch` |

A separate Git-free temporary copy passed both verifier programs in both
modes with empty PATH. All input files were read-only; before/after SHA256
inventories were identical. The direct verifiers use no Git, network, third-party
libraries, subprocesses, or predecessor executables. Five frozen source exports
match both their source Git-blob names and SHA256 pins.

The source-history ancestry preflight is unavailable in this shallow checkout.
It is not claimed as passing. Pending-source documents are retained as complete
byte-checked exports inside this package; no foreign pending commit is needed
for direct replay. The base catalogue and selected record are historical
provenance, with their exact canonical Git pins.

## Scope and unrun obligations

Finite checks corroborate a scoped analytic theorem; they are not a universal
exhaustive search or a formal proof. The test helper rejects unsupported
parameter denominators, unresolved signs, or an exhausted finite bracket.
Python's dynamic integers/Fractions/JSON and reviewed local files are trusted
runtime inputs; no fixed-memory or hostile-filesystem contract is claimed.

No raw native word, source-bound supplier invoice, selected cold replay,
physical caller, new tensor power, outer-ledger application, Lean, or Docker
suite was run. Native all-column correctness, owned erasure, uniform compiler
closure, precision/tape, analytic recovery, stock, and complete physical costs
remain inherited. The selected kappa and all five framework assumptions remain.
