# Authentic frozen H25 input API

`frozen_h25_inputs.load_frozen_inputs(input_root: pathlib.Path, custody: dict)`
returns a dictionary with exactly `result`, `witness`, `ranks`, `input_receipt`.
The public function always uses the three literal complete-H25 input pins and
59,959 ordered events / 252 distinct rows. It has no fixture-mode argument.
Every invocation reads and authenticates all inputs afresh. Values are exact
built-ins; list order is retained; source tuple positions are restored. Historical
alias/allocation topology and dict insertion order erased by canonical sorting
are not reconstructed. Each arm must run in a fresh process/root with its own
loaded values. No saved PASS exists.

`authenticate_inputs(input_root, custody)` performs fresh complete transport
hashing between custody checks. It returns an additive transport-only receipt;
it does not perform decoding/schema validation or authorize a subsequent load.
The consumer calls this after writing. The independent output validator uses its
own pinned transport/logical stream comparison and result projection.

`InputError(RuntimeError)` reports loader custody/authentication/schema errors.
Underlying gzip and JSON/decimal errors propagate; no failure is converted into
a receipt. No `assert` enforces a condition, so normal and optimized controls
have the same required outcomes. `strict_json` rejects duplicate object keys,
NaN/Infinity constants and numeric floating overflow in every parsed position.
It leaves Python's integer conversion limit untouched, keeps arbitrary-width
integers permitted by that original conversion contract and preserves its
decimal-conversion ValueError. Result exact-int fields reject bool; source bool
fields preserve both True/False; circuit.roles_per_target must remain finite
exact float. No values are cast from bool/float to integer.

Input root is an absolute canonically spelled local Path. The root and three
traversed directories are real directories mode0555. Relative input paths are
`baseline/evidence/canonical/witness.json.gz`,
`baseline/evidence/canonical/rank-trace.json.gz`, and
`baseline/evidence/canonical/complex-network.json`. Each file is regular0444,
has nlink1 and a distinct (device,inode). Every file open uses O_NOFOLLOW and
O_CLOEXEC; fstat checks bind the held fd to the sealed identity. Symlinks,
aliases, unexpected fields and before/after identity/byte changes fail closed.
Input copies and sealing are parent/envelope duties, not work done by loader.

Custody exact keys:

```json
{"schema":"h25-input-custody-v1","root":"ABSOLUTE_PATH",
 "root_identity":{"dev":0,"ino":0,"mode":365,"uid":0,"gid":0,"nlink":0,"mtime_ns":0,"ctime_ns":0},
 "directories":{"baseline":"IDENTITY_OBJECT","baseline/evidence":"IDENTITY_OBJECT","baseline/evidence/canonical":"IDENTITY_OBJECT"},
 "files":{"RELATIVE_PATH":{"dev":0,"ino":0,"mode":292,"uid":0,"gid":0,"nlink":1,"mtime_ns":0,"ctime_ns":0,"size":0,"sha256":"FIXED_PIN"}}}
```

Illustrative numeric zeroes above must be replaced by actual independently sealed
metadata; identity objects have exactly their listed fields. Root/ancestor
ownership and source/runtime closure are admitted separately by the envelope.
The loader establishes fresh before/after immutable bindings, not immunity from
a privileged adversary or historical old-stage custody.

The logical reader authenticates the full transport before opening gzip/plain
logical reads. Each read requests at most1MiB and only remaining-size+1. A size
overrun fails before extending the logical buffer. Logical final size/digest
are checked before JSON parsing. Parsing/restoration is eager: logical bytes,
JSON decoder Unicode and decoded/restored containers can coexist. This is a
bounded-by-pinned-input loader; it is not a streaming object parser or a claim
that the full eager replay fits1GiB/180s. Gzip internal buffering/runtime closure
and actual resource peaks must be reviewed/measured.

The loading bill is two complete transport hash passes (34,045,908 bytes), one
gzip transport reread (17,017,292 bytes), one plain certificate reread (5,662
bytes), logical hash/parse work (60,823,556 bytes), all metadata/fd checks,
restoration/allocation and rank-distinct work. Each subsequent authenticate call
adds one transport hash pass (17,022,954 bytes) and its custody checks. Python
buffer reallocations and temporary conversions are additional paid work.

Run the concrete ordered control source only after independent complete source
and operation admission. A future parent command can invoke Python -B -I on
`frozen_input_controls.py`, normal then -O; the script explicitly adds its sealed
sibling loader directory. Each mode requires the 39 exact names/order in
CONTROL-SPEC-v1.json. Those controls cover prospective families1-19. Consumer
controls supply family20 (literal fallback receives no bounded-path credit),
the complete writer checks and the unchanged original70 cases per mode.
Source readiness is not execution admission or runtime qualification.
