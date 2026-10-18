Run the final export gate with NumPy-capable Python:

```sh
python3 -I -O -B research/h6-compensation-network/gate/replay.py
```

`--preflight` performs source, syntax and corruption checks before the final
unified verifier is available. It records `PREFLIGHT.json`; it does not claim
the complete package has replayed.

The gate creates a fresh minimal file export under the platform's default
temporary directory and runs
from an unrelated directory. Its `PINS.json` includes the declared predecessor
inventory, every tracked file in the immutable prior independent audit, and
the new `e8_sections.py`, retained exact Clifford compiler and frame notes.
Every inherited file is compared byte-for-byte with its Git blob at the
task's pinned base before export. Bindings are checked again in both the
export and source checkout after replay. The final script inventory and every
script's SHA-256 must match the tested export. Core checks use explicit
exceptions; no new script contains an optimization-sensitive `assert`.
Task, inherited source inventory, bucket schema and relevant proof specifications
must also match the tested snapshot.
The frozen lowerer's legacy asserts are inactive under `-O`; the new explicit
rank, signed-tableau and complete exact state/phase guards remain active.

Git provenance stays enabled through `GIT_DIR` pointing to the exact source
object database. Source files and execution are relocated; a standalone Git
object database is not bundled.

The unified verifier, independent corruption controls, exact polynomial
coefficient mutation and new transitive-source mutation all run under
`-I -O -B`. Semantic controls cover dirty-prefix/cleanup omission, changed
compensation coefficients, wrong actual bucket labels, illegal descent and
unequal current frames, private copy rank, stock/pad/private C invoices,
duplicated scalar charges, explicit Horner coefficient/lifetime errors,
omitted movement charges, physical global phase and Fourier rank.

Every signed coefficient used by the word is checked against its explicit
Horner opcode stream and an independent primitive-count formula. Physical
phase controls preserve every signed Pauli generator and still fail the
complete exact Gaussian-dyadic state comparison.

`RESULT.json` records final script hashes, inherited pin count, logs and
mutation outcomes. The prior exhaustive billion-entry audit is retained
immutable evidence. This gate makes no billion-event full-word execution,
hosted CI, selected-supplier cold replay, admission or new kappa claim.
