# Frozen additive cyclic inverse validation

Both complete replays passed on macOS arm64 / Python 3.11.15 and Linux
aarch64 / Python 3.14.8, with isolation, optimization and bytecode disabled.
The complete mathematical receipts are byte-identical to each other and to
the decompressed `../additive-cyclic-no-connector/EXPECTED.json.gz`.

Frozen source manifest SHA256:
`4c595fa0731cd62064e560bc2ac48957ee073054f21d739e2ea2e4648436c14f`.
Mathematical receipt SHA256:
`eec23b09b1b3d15e1d41ad7efa3879ccff5fe2a34573bed6f628ee84cc2d5902`.

Each platform passed 11 package rejection controls and a full replay from a
read-only relocated copy in a path containing spaces. Linux additionally
ran the supplied source package read-only, outside a repository checkout,
under a durable supervisor with recorded exit status zero. Each platform
computed the full mathematical result three times: default verification,
rejection of an altered expected receipt, and read-only relocation.

The per-platform `*-MATH.json.gz` files contain the complete results. Compare
their decompressed bytes; compressed container identity is not required.
The package controls, environment, terminal marker and full logs are retained
alongside them. `VALIDATION.json` records their hashes and cross-platform
comparison. All 19 retained sources match their original Git bytes, as
recorded in `SOURCE-GIT-CHECK.json`.

Mathematical evidence covers 140 bounded complex cases, 48 original-kernel
cases from all ten pinned fixtures through radix 16, 16 actual uniform-budget
executions and 12 additional edge cases. It also includes 2,322 integer
budget checks, eight exact nonnegative polynomial identities, 3,005 width
boundary checks, 18 additional rejection controls and three defect families.
Original-kernel execution and coefficient preparation meet the 128-bit target.
Every case restores its source and reverses its target exactly.

Selected-record consistency and staged whitespace checks passed. Only this
validation directory, the new construction package and its scoped workflow
are added. The complete repository suite and hosted CI are separate from
these prepublication records; CI repeats Python 3.11/3.14 full replays.

The written all-length argument is distinct from finite computational checks.
Zero borrowed length-L arrays does not mean zero clean scalar workspace.
No new kappa, bit-reversible arithmetic compiler, arbitrary-stride tape
routing, common-label/Clifford realization, full multiplication theorem or
independent human review is claimed.
