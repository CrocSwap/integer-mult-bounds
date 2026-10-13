# Selected #626 Linux evidence reconciliation

The published #626 integration receipt records run **38317651752** as queued.
That exact run completed successfully on **2026-10-13 at 02:10:06 UTC**.
This package preserves its artifact and checks the evidence linking that
execution to the selected #543 + #626 composition. Status: **research
consolidation / provenance verification; no new kappa**.

The conditional result remains exactly
`51110230636731/31250000000000000 = 0.001635527380375392`.
The earlier queued receipt remains an unchanged historical snapshot.

## Reproduce

From a clone containing the two commits below, using Python 3.11+ and Git:

```sh
python3 -I -B research/selected626-linux-reconciliation/verify.py
```

Expected:

```text
PASS_PR626_LINUX_RECONCILIATION 6 stages, 64 substeps, 47 strict margins, 16 rejection controls
```

No network, third-party Python package, compilation, or supplier rerun is needed.
`--out /tmp/pr626-linux-report.json` writes the deterministic report.
The same command also works with `-O`; rejection checks use explicit exceptions.
A shallow clone must fetch the pinned commits first. This is an evidence check,
not a fresh execution of the supplier pipeline; that remains `make frontier626-verify`.

## Exact evidence and source scope

| Object | Pin |
|---|---|
| Sprint base | `66849e1475c930fd7732b1a0067ffee7e1e95f60` |
| Tested CI commit | `ed49217ad6244f1d3bfe4588f122fa861849739c` |
| Run, attempt | [38317651752](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38317651752), attempt 1 |
| Job | [115038013572](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38317651752/job/115038013572) |
| Artifact | `11784169747`, `frontier626-linux-python312` |
| Original ZIP SHA-256 | `1f1ad114e311f75d25fd6500db7ef0b8e15a4814aebc5c1edb01ec9288480355` |
| Selected #626 source | `660de893d27bb7abd1d5b01b1640207528a5c851` |
| Retained #543 source | `2065fe4f72a914d907f1046603f5a36f17018535` |

`evidence/` retains the original ZIP, run metadata (selected API fields), full
job/artifact metadata, and losslessly compressed `gh run view --log` output.
`EXPECTED.json` also pins the decompressed log bytes. It pins those evidence
bytes, all workflow step names, all 64 complex receipt substeps, and the three
assembly digest differences. The ZIP hash matches GitHub's artifact metadata;
its bytes are an immutable downloaded input, not a regenerated container.

`SOURCE-PINS.json` records Git object IDs. The checker independently queries
both commits and requires 39 identical objects for every selected package root,
all proof supplements, the complete `scripts/` tree, the workflow, Makefile,
selected record, source manifest, and selected assembly. It derives this coverage
from the selected record rather than accepting an arbitrary shortened list.
It also binds the complex receipt's package/spec and six dependency-manifest
SHA-256 values to the base's bytes. The intervening publication/ledger edits
are outside this source-equivalence claim.

The archived run reports Ubuntu 24.04.5, image `20261004.327.1`, Python 3.12.15,
NumPy 2.5.4, SymPy 1.14.0, SciPy 1.18.1 and mpmath 1.3.0. The workflow installs
dependencies without version pins; these are observed versions from the log,
not a claim that a future installation will reproduce that environment.

## What agrees, and what remains unavailable

All six orchestrator stages have exit code zero and retained logs matching
their SHA-256 values: bit543, declarations, complex626, independent-owner,
helper-interface, and bindings. The complex receipt lists 64 successful
substeps; its result explicitly reports no baseline or local-output reuse.
The composition links to the exact archived complex receipt and assembly.

Every assembly JSON field agrees with the committed certificate except these
three explicitly recorded paths:

- `template_sha256`
- `input_sha256.owner_audit`
- `input_sha256.fresh_invoice`

In particular, the paid profiles, moment intervals, source-engine hashes,
supplier endpoints, bootstrap data, controls, and all 47 strict outer margins
agree exactly. The checker additionally evaluates all 47 rational margins as
positive. The two source-engine/margin mutation controls update receipt links
consistently, so rejection tests mathematical-field comparison rather than
merely noticing a stale file hash.

The workflow did **not** upload the generated template, owner audit, invoice,
all 64 substep logs, or separate `OWNER-CHECK.json`/`INTERFACE.json`. Their
execution is supported by the retained stage logs and receipts, but this package
cannot independently compare those omitted payloads or explain the three byte
digest differences. It does not assert that those differences are only gzip
metadata. The source already includes recompression controls; their recorded
success is evidence of execution, not a replacement for the missing payloads.

Negative controls reject wrong heads/attempts, queued runs, skipped workflow
steps, detached artifacts, missing/failed replay stages, changed logs, broken
receipt links, wrong kappa, changed positive margins, altered engine hashes,
unrecorded provenance differences, and changed tested source objects.

This is an offline consistency check of preserved GitHub evidence, not a signed
attestation or an independent mathematical reimplementation. It confirms one
completed run at a pinned source state. It does not establish other platforms,
newer PRs, optimality, or a full multiplication theorem. The selected review's
all-size compiler, common-label/mutable-basis, pooled hosting, residual,
precision/tape/recovery and analytic assumptions remain.

## Attribution and sprint record

Douglas Colkitt supplied the selected review, replay orchestration and CI.
Chafik Boukhalfa supplied #626's owner repair; Jeremy Kothe supplied #622/#623's
construction; eumemic supplied #543's bit supplier. GamingPuzzled's #620 lead
and the preceding supplier, recurrence and verification contributors retain
the attribution in the selected review and package notices. PR #675's
independent owner-boundary audit is distinct from this CI provenance check.

Consolidation by Josh Snider (`jsnider3`) with substantial OpenAI Codex assistance.
Apache-2.0; this is not independent human peer review. [CLAIM.md](CLAIM.md)
records OS-random seed 95, candidates, scope and coordination checks.

Local validation: normal and optimized isolated Python runs produced identical
reports; all 16 rejection controls passed. `make selected-record-check`,
`python3 -B scripts/verify_pr_reconciliation.py`, and `git diff --check` passed.
The selected suppliers were not rebuilt locally because this change reconciles
the already completed, preserved CI execution and changes no construction.
