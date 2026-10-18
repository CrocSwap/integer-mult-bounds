# Frozen stride-depth validation

Complete macOS arm64 / Python 3.11.15 and Linux aarch64 / Python 3.14.8
replays passed with isolation, optimization and bytecode disabled. Their
full mathematical receipts are byte-identical to each other and to the
decompressed `../cyclic-stride-effective-depth/EXPECTED.json.gz`.

Frozen package manifest SHA256:
`0b40eccb5d47d2ac152ed7fe47c259eb71bc17d3c818a71c63e2bc026e9377e3`.
Complete mathematical receipt SHA256:
`f30ad0e119c9928f30e2fc97e1911e053fe347bc4fe3f2b328b295141bda1552`.

Each platform recomputed the full mathematics three times: default replay,
rejection of an altered expected receipt, and a read-only relocated replay
in a path containing spaces. Eleven package rejection controls passed on
each platform. Linux also began with the supplied package read-only, outside
a Git checkout, under a durable supervisor that recorded exit status zero.

The full `*-MATH.json.gz` receipts, package controls, platform information,
terminal records and logs are retained here. Compare decompressed receipt
bytes; container compression identity is not required. `VALIDATION.json`
records their hashes. All 12 retained source files match their pinned Git
objects and SHA256 hashes, as recorded in `SOURCE-GIT-CHECK.json`.

Evidence includes 423 array cases, 90 scalar coefficient paths, all 300
original PR846 kernel cases, 64 actual cubic-width kernel executions,
216 integer budgets, three exact nonnegative polynomial identities,
54 admission checks, 1,545 logarithm boundaries, 12 new mathematical
controls and four inherited controls, 12 zero-base checks and 33 traffic
cases through length 131,072. Scalar paths are not huge-array executions.
Original and early-exit outputs agree exactly; the two traffic bills are
40L and 44L respectively, with the additional head returns charged.

The source record preserves preparation base
`007664306fff84fbb1c9a1b4053b69f439764034`. Before publication the branch was
fast-forwarded to `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`, without changing
any frozen package byte. Selected-record consistency passed there at
`1661960547713947/1000000000000000000`; staged whitespace and byte checks
also passed. Only two new research directories and their workflow are added.
The full repository suite and hosted CI are separate from these local
prepublication records. The scoped workflow repeats both Python versions.

Finite exact checks support the written universal argument; they are not
independent human review or proof-assistant verification. Clean scratch,
phase access and remaining transform obligations remain explicit. No new
kappa or bit-reversible/borrowed-array implementation is claimed.
