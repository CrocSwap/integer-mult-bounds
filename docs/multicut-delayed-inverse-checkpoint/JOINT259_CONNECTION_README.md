# JOINT259 operation connection inventory

Start with JOINT259_CONNECTION_SUMMARY.json, SCHEMA.json, and MANIFEST.json.
The system overview is a separate descriptive graph. Its edges must never be
presented as the complete operation inventory.

## Exact scope

The selected final local word has 859,771 operations: 760,383 ADD, 99,340 MOVE,
24 COPY and 24 ERASE. The generator emits every original six-int row plus
20 connection fields: source/destination IDs, semantic value versions, frame
IDs and state versions, and producer events. Four typed producer columns
define 3,439,036 read links; consumer lists are their exact transpose.
Initial producer IDs are -(register+2), and -1 means absent.

MOVE preserves semantic payload while advancing its frame state. ADD reads
both old operands before writing its destination. COPY creates a fresh
temporary generation, preserves the retained source and expands into COPY
plus MOVE in global lowering. ERASE checks that source and lifetime before
removing the temporary. All 24 copied-source lifetimes have 220 reads each.

The complete word is freshly scanned, with frame-state/read-before-write,
scalar/tagged digest, paid/category count, and copied-source immutability
checks. This is a structural connection check, not a new scalar all-column,
geometric-containment or arbitrary-size compiler proof.

The BankPlan map includes 16,587 actual helper roles, residual rank families,
gauge-frame IDs, packing segments/patterns and phase schedule.
iter_global_connections(inputs, stage, replica, cover='d') maps every local
operation for any of 200 stage/replica pairs. All five logical stage streams
match the admitted Lowerer exactly at 859,795 rows each. Each of 24 local COPY
macros contributes an additional lowered MOVE. The 4,021,600-address check
tests distinct syntactic (family, route-word) keys. Algebraic rational/mod-q
nonaliasing remains inherited from the separately admitted bank proof.

Unexpanded: finite-cover enumeration, recursive child programs and stopping
policy, q-local fallback, complex supplier internals and arbitrary-size tape
movements. COMPLETE is rejected by the mapper; bank completion is inherited.

## Portable rebuild

Extractor requirements: Python 3.11+, standard library only. Its shared
source adapter and binding JSON must be beside the extractor:
joint259_system_docs_sources.py and joint259_system_docs_source_binding.json.

Use an admitted source directory or ZIP with the original scientific manifest
9f6d8637b9a119cfe4566a02ab2d704f23c502e5e4357b40c28ef85a3fd4de89
or approved public manifest
0af10dcca505cbd913cf1b9220a08b6a62687650ace4e3d1efd093e828e3990e.
The adapter validates the complete closure and 117 retained numerical pins.

Existing fresh verifier output can be reused; no expensive verification is
rerun by the extractor. To produce inputs when none exist, run the selected
source package's documented verifier using its own requirements (Python 3.11+
and SymPy 1.14.0); OUTPUT must be new and outside the source package:

    python SOURCE/verify.py --output OUTPUT

The final input directory is OUTPUT/hybrid, not OUTPUT itself. Then:

    python JOINT259_CONNECTION_EXTRACT.py --package SOURCE --inputs OUTPUT/hybrid --summary
    python JOINT259_CONNECTION_EXTRACT.py --package SOURCE --inputs OUTPUT/hybrid --map
    python JOINT259_CONNECTION_TESTS.py --package SOURCE --inputs OUTPUT/hybrid --full --writer

SOURCE can also be the admitted source ZIP for extraction/testing, without
extracting it. The verifier itself should be run from its documented source
directory. Input binding uses the decompressed raw SHA and canonical invariant
metadata digests. Gzip compression/header, JSON formatting, and runtime/timing
receipt differences are allowed; raw/frame/category/census changes are not.

Generate the complete portable gzip JSONL in an authorized writable location:

    python JOINT259_CONNECTION_EXTRACT.py --package SOURCE --inputs OUTPUT/hybrid --inventory DEST/JOINT259_CONNECTION_EVENTS.jsonl.gz

The destination must be a new file outside a directory-valued source package.
The output is self-describing: metadata first, all 859,771 operation rows,
validation last. Public delivery is the tested complete generator and source
binding manifest, not a multi-megabyte generated trace. Four experimental
base64 shards 000-003 are partial, private, excluded from publication and every
completeness claim. --saved is an optional developer facility requiring a
separate complete shard index; it is not part of the delivered workflow.

Expected packed 20-int-per-event connection SHA:
14d13b5b4e851a66c20af1850d77a71fe21cbe3fda35c72000709f767275222e.

## Reuse and change boundaries

Automatic within the documented six-int MOVE/ADD/COPY/ERASE IR: enumerate all
events, rebuild producer/consumer links and value/frame versions, check
lifetimes, expand the selected five-stage lowering, and evaluate BankPlan
addresses. Changed event order, coefficients or frames can be re-extracted
only after an explicit reviewed source/config update.

Manual configuration: approved package closure/source binding, RAW_SHA,
GENERATED_PINS invariant projections, CONNECTION_SHA regression value and
expected operation/category/census controls. These currently live in the
extractor and source-binding JSON, not a generic architecture parser config.

Manual adapter work is required for different role-selection files or role
counts, initial state layout, new opcode/field conventions, new COPY semantics,
different stages/replicas, or a new bank API. The selected N,V and ownership
census assertions deliberately fail loudly on incompatible systems. A new
system requires renewed tests and review. Do not update labels/counts alone
to make a stale artifact pass. Supplier and historical generator files are
unchanged.
