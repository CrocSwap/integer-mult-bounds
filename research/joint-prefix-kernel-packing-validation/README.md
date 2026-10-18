# Full cold replay evidence

Source manifest: `410ddcb9c59b51bed4176062f5a6fb1f7922fbed84f32a7e984592c43c91164b`.

| Environment | Full cold time | Result |
|---|---:|---|
| macOS arm64, Python 3.14.8, zlib 1.2.12 | 395.026 s | PASS |
| Linux aarch64, Python 3.12.3, zlib 1.3 | 477.666 s | PASS |

Each run starts from an absent output directory. The nine root stages contain
the complete 39-stage PR575 cold replay and the new added-kernel provider,
followed by eight fresh global admission stages. No retained provider proof
outputs are reused in either final run. All source files remain unchanged.

Both final results are byte-identical with SHA-256
`22ad457a63b220e7aff8e5224346559544d2b37d5b04aad3745ec4b04ce87c31` and admit `kappa=0.001601260169988325`.
`CROSS-PLATFORM.json` compares all fourteen provider proof-content identities
and every numerical/semantic invoice field. Raw-reference fields omitted from
the invoice comparison are explicitly listed; each is validated against actual
files during its own run. Raw compressed containers, timings, absolute paths
and derived receipt hashes can differ across environments.

The complete nested receipt chains, named proof artifacts and logs are
retained. Both runs include 48 new kernel omission controls, all columns,
wrappers and phases, 23 owner mutations, 106 assembly mutations, two timing
accept/reject pairs, two actual recompressions, 18 proof mutations and 18
reference/metadata mutations. The unchanged PR543 bit circuit is cited and
repriced; it is not freshly rebuilt here. `SOURCE-VALIDATION.json` records all
271 original Git-blob matches. `OPTIMIZED-REJECTION.json` proves the root refuses
optimized Python before creating any output. GitHub CI is a separate execution.

## Nomination and preliminary checks

The five-family search stopped with a feasible solution after its 180-second
limit. `nomination/` retains the exact integer/matching verifier, selected
allocation receipt and search log. It selected 48 added-kernel joint-prefix and
24 plain joint-prefix calls. Floating-point optimization nominated choices;
every integer row, literal owner assignment, physical chart, coefficient and
admission inequality was subsequently checked independently and exactly.
Neither solver nor packing optimality is claimed.

The first portable pilot reached its final control stage, then failed on an
inherited package path in the recompression test launcher. The path was fixed
before freezing the source; the second portable pilot passed all eight stages.
The two final full cold runs above use only the corrected frozen source. Their
results are not inferred from the pilots. Preliminary logs are retained.

`REPORT-NORMALIZATION.json` compares the freshly built added-kernel word to
PR576's independently rebuilt word. Every scalar operation, frame, entrance,
port and cleanup entry is identical. Only two stale descriptive report fields
are recomputed: final rank mass 5956 and actual width inventory. No gate or
frame change is concealed by this correction.

## Unchanged repository baseline

`BASELINE-REUSE.json` binds the unchanged base commit
`db0e57bc7f36b5ac0fc844ad7ce1396165ee6647` and the twelve byte-identical evidence
files published by PR572 at `0c3a7d1b0d99dbc6a1cc5ec1675ddd74aa959586`.
All 18 top-level `make verify` groups passed across the initial and resumed
runs, including `gen4-bank-verify`. The initial invocation passed twelve groups
then exited 2 on Apple clang's unsupported `-fopenmp`. After a run-owned libomp
wrapper passed a four-worker probe, the failed group and five remaining groups
passed. No source or assertion changed. This is explicitly reused evidence,
not a new successful aggregate invocation.

These receipts prove the described finite conditional admission. The
all-size/interface and analytic obligations in the source PROOF remain open.

The diff retains twelve whitespace warnings: nine in pinned vendor files, two
on unchanged inherited lines in adapted audit/binding code, and one in a
verbatim preliminary failure log. Frozen source and evidence bytes are preserved.
