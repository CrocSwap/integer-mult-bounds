# Validation and exact coverage

Executed on 2026-10-15 with CPython 3.12.12 and CPython 3.14.6 on macOS arm64,
using only the standard library. These are source and finite-execution checks,
not an independent human review, proof-kernel theorem or supplier admission.

## Registered replay

From the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/selected-validation-numerical-lifetime
make selected-record-check
```

The registered replay passed all four commands in `VERIFY.json`:

| Command | Observed result |
| --- | --- |
| `verify.py` | 82 literal fixtures; Callback bound `(12,15)`, prefix bound `(4096,23)` |
| `test_verify.py` under `-O` | 10 semantic and 4 source/receipt integrity control groups |
| `independent.py` under `-O` | 4229 index histories and 1829 residue cases |
| `compare_models.py` under `-O` | Exact validation-peak agreement for all 82 literal fixtures |

`selected-record-check` passed the existing record/source/proof-supplement
bindings. The selected record was not changed and its complete supplier cold
replay was not run. That check does not certify this prefix theorem or establish
the full selected multiplication theorem.

The fixed `RESULT.json` records each fixture, phase maximum, allocation/boundary
sample count, cell scans and maximum additional occupied numerical symbols.
The literal census instruments allocations and also scans actual source tape
cells at new joint peaks and named boundaries. The runtime's source byte hashes
and Git blobs are authenticated before those exact bytes are compiled.

## Portability and controls

The four scripts also passed with CPython 3.14.6, all under `-I -O -B`, from
`/private/tmp` with an empty `PATH`, using a Git-free package export whose files
were mode 0444 and directories mode 0555. The export's file hashes remained
unchanged. Mutation controls run only in disposable temporary copies. An initial
read-only export trial exposed inherited permissions in those test copies;
the harness now grants write access only to its fresh disposable copies, and
the read-only trial passes. No source runtime change was needed.

Controls reject an undercharge by one Word at each sharp Callback index class,
the inverse residue peak and the composed halving peak. A deliberately added,
correctly restored inverse temporary fails the normal lifetime bound and passes
the relaxed bound, showing that an unchanged endpoint is insufficient. Invalid
program codes, a nonunit root and inconsistent chronology exercise the specific
Callback constructor's rollback. Source-byte or snapshot corruption fails
authentication; a separately demonstrated effective malicious bytecode cache is
ignored by the authenticated-byte loader. Replacing a receipt integer by a
boolean is rejected rather than accepted by Python's numeric equality.

The independent model imports no vendor implementation. Its allocation ledger
and native arithmetic separately derive the event histories. It is an independent
AI implementation, not an independent human review. The cross-model comparison
checks validation peaks, with literal directory/setup maxima checked separately;
it does not compare every source instruction or establish an abstract machine
refinement theorem.

## Coverage boundaries

Literal fixtures cover 70 complete Callback lifecycles and 12 complete caller
prefixes. Callback cases include every good rank 1 through 42, good/pair/unit
and halving branches, depths 0, 1, 4 and 8, moduli 3, 5, 27 and 49, and borrowed
residents. Prefix cases have moduli 3 or 5 (exponent 1), final widths 64 and 127,
neutral good/fallback metadata and depths 0, 1 and 4. They end at the stated
packet-engine seam. Selected vocabulary membership and packet/GL64 execution
are not established by these metadata fixtures.

The independent finite domain is all final widths 64 through 127, depths 0
through 8 with the stated step histories, and every unit for primes
`{2,3,5,7,11}` and exponents 1 through 3. Its inclusion of prime 2 is arithmetic
coverage beyond the README's selected odd-prime contract, not supplier coverage.

The literal whole-prefix weighted-content fixtures are directory-dominated.
The other branch of `max(4096r, 2r+Ki)`, arbitrary valid finite depth and
arbitrary legal prime-power exponent follow from the source-level written
invariants and inequality in `INDEPENDENT.md`. They are not finite exhaustive
execution claims. This contribution leaves non-ADD and child-return lifetimes,
count/control/payload content, physical backing/movement, arbitrary exception
safety, actual selected bindings and the complete multiplication theorem open.
