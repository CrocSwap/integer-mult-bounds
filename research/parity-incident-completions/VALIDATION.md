# Completed verification

Validated on Windows with CPython **3.14.5**, starting from base
`407d52ff15b2217b6e22bce44728b4c3907b6515`, in an isolated worktree.
The machine-readable commands, results and scope are in
[VALIDATION.json](VALIDATION.json).

| Completed check | Result |
|---|---|
| `python -B research/parity-incident-completions/check.py` | PASS; 692 nodes, 3,096 minimum frames, 2,538 passing frames; node split 560 / 12 / 100 / 20 |
| `python -B research/parity-incident-completions/test_check.py` | 22 tests passed |
| `python -O -B research/parity-incident-completions/test_check.py` | Same 22 tests passed with assertions disabled |
| Fresh `produce.py --out <fresh-output>/certificate.json` | Byte-identical to committed certificate |
| `python -I -O -B research/parity-incident-completions/check.py --certificate <fresh-output>/certificate.json` | PASS in isolated, optimized mode |
| `python -B -m unittest discover -s tests -p test_parity_side.py -v` | All four historical parity tests passed |
| `python -B scripts/verify_selected_result.py` | PASS selected record, exact kappa, source inventory and proof supplements |
| Context-file SHA-256 pins in `SOURCES.json` | All 12 match |

The checker reconstructs all **14,400 signed scalar coefficients** from the
actual DAG arguments. It independently rebuilds source and target reachability,
exhausts every minimum extension coset, checks explicit residual sets, verifies
the 112 larger-frame witnesses, and excludes the missing dimension-eight
frames. It also reproduces the complete **168-frame dimension-four census**
at the 12 nodes requiring one extra dimension.

Controls reject omitted or duplicate records and frames, altered source/DAG
hashes, extra source vectors, changed characteristics or residual decisions,
false impossibility claims, invalid repair vectors, changed summaries, duplicate
JSON keys and an output-sign flip. Small geometric controls cover PR #920's
alternating residual, the accepted zero-residual boundary, a characteristic in
the source span but absent from the actual labels, and a target-only failure.

The row-reduction producer and explicit-vector checker share the pinned DAG
constructor but no frame-algebra implementation. A separate Codex worker also
reviewed the mathematical argument and reproduced the counts independently.
This is not independent human peer review or formal theorem verification.

The initial regeneration attempt in the sandbox-provided Windows temporary
directory failed with a permission error before writing the output. Repeating
that check in the writable workspace succeeded. The Python launcher emitted a
location warning; the completed checks returned zero. Neither issue was bypassed
by weakening a mathematical check.

`make verify` and `make frontier942-verify` were **not run**. This additions-only
research package changes no supplier, generator, selected record or upstream
source; the affected historical tests and new exact checks are reported above.
No full supplier replay, Linux execution, Lean build or complete multiplication
theorem verification is claimed.
