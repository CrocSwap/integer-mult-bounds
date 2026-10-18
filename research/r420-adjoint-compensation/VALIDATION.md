# Validation record

Executed on 2026-10-13, macOS arm64. The checks below passed with the pinned
base and sources listed in `SOURCES.json`.

| Check | Result |
| --- | --- |
| Primary backward verifier, isolated Python 3.9.6 | PASS, 129 rejecting controls |
| Primary backward verifier, isolated optimized Python 3.9.6 | PASS, same certificate |
| Primary backward verifier, Python 3.14.8 | PASS |
| Separate support-set and Boolean verifier, Python 3.9.6 and 3.14.8 | PASS, ten full scalar probes, bounded fault controls, three malformed suites |
| Certificate emission, Python 3.9.6 versus optimized Python 3.14.8 | Byte-identical |
| Both final checkers from a minimal copied tree with spaces, unrelated working directory, Python 3.9.6 | PASS |
| Corrupted compressed source bytes | Rejected by source pin before decompression |
| Zeroed parity probe | Rejected by both checkers |
| Changed test count in committed receipt | Rejected by primary checker |
| Missing certificate and missing pinned source | Both rejected |
| `make selected-record-check` | PASS, exact selected kappa and source inventory |
| Native word Git blob at base versus PR543 source | Identical |

The complete canonical `--emit` output has SHA-256
`e340ed4188ae666b408143195b394686eba26cb266e2ded2fe0a53f6c519b607`.
This hash describes the JSON output, not a regenerated gzip container.

The minimal-tree and external mutation tests used temporary copies of this
package and exactly the seven pinned source/context files. They did not
modify repository inputs. The certificate, source and missing-file tests are
fail-closed execution checks; they are separate from the 129 in-process
mathematical/schema controls in the reproducible primary command.

A separate Codex worker wrote and ran the forward support-set/Boolean checker
and reviewed the adjoint implementation and ten-test optimality proof. No blocking
finding remained. This is disclosed AI review, not independent human review.

The full repository suite, full selected cold replay, remote Linux CI and
Lean were not run. No existing generator, supplier, selected certificate or
`upstream/` file changed. The result has the scalar scope stated in README.md;
it does not verify physical interfaces, restoration, cost or the full theorem.
