# Cold replay evidence

The frozen package manifest is
`aa569a51a741db43c80cb29815c1736d668db17593048974015daf14857c41bb`.

| Environment | Full cold time | Top-level stages | Result |
|---|---:|---:|---|
| macOS arm64, Python 3.14.8, zlib 1.2.12 | 399.922 s | 18 | PASS |
| Linux aarch64, Python 3.12.3, zlib 1.3 | 425.950 s | 18 | PASS |

Each run starts from an absent output directory and includes the complete
pinned PR568 replay. There is no retained-provider reuse in these final runs.
The final result is `kappa=0.001600535778621932`. Its byte-identical
`RESULT.json` SHA-256 is
`0bbdaef6b06b415910079cac6bc4a4e7e4bee569f0ec510f74f6b127c336b0af`.

`CROSS-PLATFORM.json` compares all seven proof-relevant identities for each
provider and every numerical/semantic invoice field. It names the raw-reference
fields omitted from the invoice comparison. Those references were validated
against actual files in each independent cold run; their derived raw hashes
need not agree across environments. Timings and absolute command paths in
receipts are environment-specific.

Each environment includes its command/exit/timing/log-hash receipts, root logs,
local construction/omission checks, exact assembly, owner/invoice audits and
admission/portability controls. `SOURCE-VALIDATION.json` records 229 original
Git-blob comparisons. GitHub CI is a separate execution and is not implied by
these local and remote receipts.

## Preliminary work and corrections

An initial aggregate ownership search could satisfy width totals but fail
literal expansion because a call could repeat an owner. It was rejected.
The accepted search uses explicit per-pattern/per-call flows and a checked
matching expansion; all 36,288 actual helper roles pass the independent audit.
A pilot control-count expectation of 89 was corrected to the actual 93
rejections after adding composed-provider controls. No admission check was
removed.

Preliminary v1 source passed cold on both platforms (407.928 s and 427.327 s),
but retained generated gzip byte pins inherited from PR569. V2 adopts the
pinned PR567 content-identity helper and adds actual recompression and rebound
mutation controls. Both final cold runs above were restarted from empty output
directories against v2. The mathematical construction and rate are unchanged.
V1 success is not used as evidence of final-source execution.

## Repository baseline

All 18 top-level groups in `make verify` passed across the initial and resumed
runs on the unchanged base commit `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`.
The first aggregate run passed twelve groups, including `gen4-bank-verify` and
`frontier531-verify`, then failed in `verify-strips` because Apple clang rejected
`-fopenmp`. An installed `libomp` runtime and a run-owned compiler wrapper were
validated with a four-worker probe. The failed group and five remaining groups
then passed sequentially. No source or test assertion was changed.

`baseline/RESULT.json` records the commands, environment, separate outcomes
and log hashes. The first aggregate invocation exited 2 and is not described
as a successful single invocation.

The release diff retains nine inherited trailing blank-line warnings, including
one in adapted audit code. Frozen and vendored source bytes were preserved.
