# Selected scatter lists and record-export parity

Appending `[0,0]` to row 0 of the selected PR589 bit word passes the complete
symbolic checker but changes the exported F2 operator. Native record legality
also accepts it. The native formal-column checker rejects the exported word.
This is a counterexample to a cross-stage implication, with a two-entry fixture
and an exact dirty-input witness. It does not invalidate the selected result.

The selected generator produces distinct row entries, its tuned word satisfies
that condition, and its complete replay binds the original bytes. No production
source, frozen input or selected-frontier record is changed here.

## Exact result and proof

The pinned tuned word has `v=111`, `R=439`, nine retained totals and 661 local
input columns. Its first scatter row is `[4,5,6,7,8]`, and retained index 0 names
helper register 472. Change only that row to `[4,5,6,7,8,0,0]`.

The complete [symbolic checker](../e8-bit-p111-tuned/code/xcheck_p.py) XORs a
copied total once per list occurrence in `Word.replay`. The
[record exporter](../e8-bit-carrier-skeleton/code/bit/export_records.py) emits
one ADD if `k in row`. If an index occurs `m` times, their coefficients over F2
are respectively `m mod 2` and `[m>0]`. For independent abstract copied values,
the two scatter operators agree exactly when every positive multiplicity is
odd. Distinct entries are a sufficient boundary condition. Repeated odd
multiplicities can also agree, so uniqueness is not asserted necessary.

Two added occurrences cancel in the symbolic word. All label/lattice checks,
all 661 dirty-state columns, H1-H5 and all four conclusion flags still pass.
The scatter occurrence count rises from 527 to 529. The exporter instead emits
one extra ADD, raising its stream from 27,234 to 27,235 records. The record
legality check still accepts rank mass 5,129 and nine COPY/ERASE pairs.

Set only input register 472 to one. The original export leaves target 111 at
zero; the mutant leaves it at one. Helper 472 remains one in both. The exact
full-column oracle finds that only output register 111 differs, and records
its complete difference support in [RESULT.json](RESULT.json). The actual
native checker fails at `local defining-decoder full formal column`.

Appending a single `[0]` is rejected by the symbolic checker with
`targets not y + x: [0]`, yet exports byte-identically to the paired mutant.
Thus two is minimal among append-only repetitions of this initially absent
index that retain this symbolic endpoint. This is not a minimum over arbitrary
word edits. Removing even multiplicities from this specific row recovers the
original word and its exact record bytes. No general signed-ring normalization
or compiler repair is claimed.

The package's `validate_scatter` is a tested sufficient guard requiring simple
support lists. It rejects repeated, noninteger and out-of-range indices before
export. It is an opt-in repair candidate, not an installed production change.

## Source boundary and existing protection

[gen_p3.decoder_rows](../e8-bit-p111-tuned/code/gen_p3.py) searches
`itertools.combinations`, so its rows contain no duplicates.
[pwordl.build](../e8-bit-p111-tuned/code/pwordl.py) serializes those rows, and
[tune/apply.py](../e8-bit-p111-tuned/tune/apply.py) changes only A/C after copying
the base. The pinned [tune/verify.sh](../e8-bit-p111-tuned/tune/verify.sh) binds
the rebuilt word before its checker/export/native stages. The synthetic mutant
is outside that selected producer, and the later column check independently
rejects its endpoint. Symbolic checking or record legality alone does not
replace that later check.

These source observations are pinned and inspected, not a fresh execution of
the generator, tuner or complete supplier chain. The original source bytes
match the selected PR1094 source manifest. [SOURCES.json](SOURCES.json) also
pins the exact native sources and the checked arithmetic stand-in.

## Reproduce

The registered hook requires Python 3.12. The direct audit also runs on newer
Python versions. Both use only the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/scatter-export-parity-audit
python3 -I -O -Werror -B research/scatter-export-parity-audit/verify.py
```

The first command runs the primary audit and eight behavioral test groups.
Normal replay is read-only. `verify.py --emit` prints a reconstructed receipt.
The oracle directly interprets the unchanged exporter's packed records, with
661 independent F2 basis bits. MOVE is ignored only in this scalar projection;
COPY creates a fresh temporary and ERASE closes it. This is not an independent
frame, hosting, precision or native compilation proof.

Optional native replay, with a C++17 compiler:

```sh
python3 -I -Werror -B research/scatter-export-parity-audit/native.py
```

It compiles the actual unchanged legality and five-stage column checkers with
`HDIM=8, NCOPY=9, VPORTS=111, RHELP=439`, using the authenticated
[checked cpp_int stand-in](../bit589-checked-cpp-int-seed92/README.md).
That backend is checked 128-bit arithmetic which refuses overflow. This is not
a fresh system-Boost build. The three native fixtures and complete deterministic
receipts are in [NATIVE.json](NATIVE.json). Only elapsed times and the temporary
stream path are normalized after checking their format. Native replay is
optional because the generic hook does not provision a compiler.

## Open next questions

Choose the scatter schema for a separately versioned successor checker and
exporter. If rows are simple supports, enforce uniqueness at both boundaries;
if multiplicity is meaningful, define its coefficient semantics and test that
lowering. Start by adding this two-entry fixture to the successor's full
symbolic/export/native sequence. Adoption requires new manifests and reviewed
source bindings; frozen packages should stay unchanged. No additional search
or new supplier construction follows from this audit.

## Scope, credit and verification limits

Base main `d878e1f048823de10e57e3dc58522d345a5fcd8d`, priority revision 5.
[TASK.json](TASK.json) records the refined `supplier-boundary-audit` card,
overlap coverage, freshness and remaining obligations. The canonical
[Discussion2976](https://github.com/CrocSwap/integer-mult-bounds/discussions/2976)
contains the claim and artifact handoff. Existing scatter-lifecycle, record
mutation and owner-binding work is credited there; none is replaced here.

Credit eumemic for the punctured generator, word checker and PR543/PR555/PR589
lineage; DreamingOfClouds for the punctured-star and retained bit-supplier
construction lineage; Dylan Crow for the exporter and native checkers; and
Douglas Colkitt for the selected source bindings and review. Existing source
notices and licenses remain unchanged. This contribution adds the paired-list
counterexample, exact source-to-record witness, guard and replay controls.

Nick Petalas. Apache-2.0. Substantial automated assistance in research,
implementation, checking and writing. Separate internal source inspection and
review do not constitute independent human or proof-assistant review. Full
selected cold replay, all-size transfer and hosted CI are not claimed.

## Engineering constraints

Build the Lever led to the retained record interpreter and native replay;
Prove It Works required the actual full symbolic checker, exporter and native
rejection. Power-of-Ten checks keep the new functions below 60 lines, bound
inputs to 24 pinned files of at most 5 MiB and streams to 30,000 records, and
use explicit checks under `-O`. Registered commands have finite timeouts.

Rules 3, 8 and 9 require managed-runtime and authenticated-code deviations:
Python allocates bounded fixture objects and dispatches pinned modules and
subprocesses. The source hashes, fixed 661-column/three-fixture domain,
subprocess deadlines, explicit closure and corruption controls bound their
scope. Frozen source loops are audit subjects, unchanged here. Reassess these
controls before enlarging the domain or adopting a production compiler change.
