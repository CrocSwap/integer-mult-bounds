# Executed validation and remaining obligations

Executed on 2026-10-13 with CPython 3.14.5 (Windows x64), MSVC 19.51 and
Boost 1.88.0. `NATIVE-ENVIRONMENT.json` records compiler/header hashes and the
literal native commands. Regenerated gzip headers are excluded from
mathematical equality; exact hashes still bind immutable input archives.

| Check | Observed result |
|---|---|
| Complete finite verifier, final witness | PASS, 66.010 seconds |
| Exact transfer minimum | 11; independent BFS 798,401 states |
| Exact reverse-compatible minimum | 12; independent exclusion 949,377 states |
| Whole PR589-based local word | 661 columns; H1-H5 and all interface conclusions pass |
| Literal exported instructions | ADDs 24,305 -> 24,283; 2,911 MOVEs; 9 COPY/ERASE pairs |
| Paid profile | Unchanged; rank mass 5,129 |
| Mathematical mutations | All 9 rejected |
| Package tests | 11 passed in 122.432 seconds |
| Fresh C++ legality | Both words pass source-owner, geometry and lifecycle checks |
| Fresh C++ 5/9/11-stage checks | Both words pass 883/1,327/1,549 formal columns |
| Omitted-bridge controls | All 96 rejected across both words |
| Selected-record integrity | `scripts/verify_selected_result.py` passes at recorded base |

The package tests include a minimal offline copy with only four execution
inputs, in a path with spaces, under `python -I -O -B`; altered certificate and
source rejection; stale cleanup that is scalar-valid but violates H4; malformed
gate/wire and overlap-window rejection; incorrect minima and exhausted budgets;
and preservation of an existing output directory. Independent search receipts
are embedded in `CERTIFICATE.json`; the two small `INDEPENDENT-*.json` files
retain the same separately obtained lower-bound receipts.

Initial nomination found an 11-gate word with a larger reverse map. It was not
presented as admitted. An exhaustive guarded search established the 12-gate
floor, and the final 12-gate ordering also meets the tighter PR936 reverse cap.
Both final verifier and native replay use that final source-bound ordering.
The earlier 12-gate ordering was checked during development but is not the
packaged witness. No failed receipt was edited into a pass.

The submitted changes are confined to `research/r439-frame272-seed06/`.
`upstream/`, all consumed suppliers, the selected certificate and global
generators are unchanged. The repository-wide `make verify` and selected cold
replay were not run: this standalone research package does not replace their
inputs, GNU make was not available in the local Windows shell, and their
historical suites regenerate unrelated artifacts. The affected finite and
native checks above were run directly. Hosted Linux CI, a full hosted invoice,
outer assembly and the full Lean multiplication theorem are not claimed.

All-size/compiler, physical realization, common-label/mutable-source,
whole-call hosting, precision/tape and analytic assumptions remain inherited.
The exact finite minima and executable evidence do not remove those obligations
or produce a new kappa.
