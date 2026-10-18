# Validation record

Validation used Python 3.14.7 on macOS 26.6.1, arm64. The final mathematical
sources, compiler pin, and expected receipt stayed fixed throughout each run.
Only documentation was completed afterward. The package uses the standard
library and one CPU. Peak child resident memory was 102875136 bytes, below
99 MiB. This is checker memory, not a supplier workspace bound.

| Check | Result | Wall time |
|---|---|---:|
| `python3 -I -B research/shared-carrier-decoder/verify.py --out /new/directory` | exit 0; all final markers | 210.337 s |
| `python3 -I -B research/shared-carrier-decoder/test_controls.py` | exit 0; 14 controls | 2.068 s |
| Same package copied outside the repository to a path with spaces; `python3 -I -O -B verify.py --out /new/directory` | exit 0; all final markers | 170.133 s |
| Control suite in that relocated, optimized environment | exit 0; 14 controls | 1.936 s |
| Changed compiler source in the relocated package | exit 1; `Clifford source pin` | 0.091 s |
| `make selected-record-check` | exit 0; selected record intact | 0.492 s |

The source-pin control restored the copied compiler before the successful
relocated run. Both generated CERTIFICATE.json files are byte-identical to
EXPECTED.json. The two word hashes and native lowering hash agree as well.
Timing is recorded for reproduction; it is not a performance comparison.

## Coverage

Each primary run checks both modules on all 674 independent logical columns.
The exact sparse row and separate integer column interpreters use different
state representations. The native audit checks 234 exact frame operators and
913 distinct ordered transitions. Each transition uses the retained compiler,
with its assertions enabled even under an optimized parent process.

The separate physical interpreter executes both forward words and both inverse
transposes. Each execution checks 345088 complex output values, from 674 roles
and 512 addresses. All 512 matrix columns of the nonzero-endpoint rank-seven
COPY also pass. These execution checks support, but do not replace, the written
composition proof for arbitrary physical inputs.

The coordinator, in a separate Codex review, ran all 14 controls and chose a
second dense input (`trial=1`) for the candidate's forward and inverse-transpose
physical executions. Both passed. [REVIEW-SECOND-INPUT.json](REVIEW-SECOND-INPUT.json)
binds that result to the four Python source hashes. This was a separate AI
replay with the same interpreter, not an independent human or formal review.

## Failure controls and their contracts

| Change | Contract that rejects it |
|---|---|
| Omit one old-value compensation, centre restoration, source restoration, or source read | Exact map on all independent dirty inputs |
| Change one scatter coefficient | Complete normalized Gram identity |
| Process the nonzero endpoint first | Common exact frame at every later COPY read |
| Copy to a line outside the query hyperplane | Legal source/endpoint inclusion |
| Omit one inactive helper tail | Every advertised physical output frame |
| Dispose of a copy before its first read | Temporary stream lifetime |
| Add a global phase to the compiled COPY | Exact complex operator, beyond its binary frame |
| Omit one C factor | Actual paid recursive operator |
| Replace integer 1 in the receipt with Boolean true or floating 1.0 | Canonical JSON value and type agreement |
| Remove EXPECTED.json from a copied package | Required receipt at the ordinary CLI boundary |

The last three cases repair a review finding. The prior parsed-object equality
accepted `true == 1` and `1.0 == 1`. The verifier now compares canonical JSON
after it normalizes integer histogram keys. The missing-file control invokes
the real CLI on a copied package and fails before native work starts.

The tests use the existing construction and verification entry points. They do
not add an alternate execution mode or alter a native primitive for testing.

## Earlier failure and checks outside scope

An earlier `/usr/bin/time -l` wrapper returned 1 because macOS denied its
`kern.clockrate` query after the verifier had completed. That wrapper result is
not counted as an exit-zero validation. The final runner records each Python
child's own return code and uses the permitted resource counter.

The full repository `make verify`, historical supplier cold suites, hosted CI,
an all-size compiler, rounding code, and a linear tape implementation were not
run or built. This patch adds one isolated finite research package and changes
no selected construction or upstream source. The full theorem and runtime
claims stay outside its scope.
