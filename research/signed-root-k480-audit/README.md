# Signed-root K480 execution evidence

This directory records runs of the frozen sibling `signed-root-k480` package.
The complete witness gives conditional κ = **0.001627103256702062**. It is a
structural contribution, below the predecessor and contemporary frontier.

## Fresh finite replay

`fresh/RECEIPT.json` binds the exact package manifest, specification, six source
manifests, 64 successful stage logs and 51 output artifacts. All bound logs and
artifacts are included under `fresh/`; `fresh/RESULT.json` records **519.931 s**
and no reused baseline or local providers. `fresh-replay.log.gz` is the complete
driver output. This replay covers both providers, all 704 arbitrary-dirt columns
per provider, reflected programs, exact wrappers, every phase edge, literal
ownership, the finite invoice and both rational moment engines.

`SCHEDULE-CONTROLS.json` separately records exact reproduction of the signed
schedule and 16 rejected mutations using the unchanged constructor. The fresh
pipeline also runs its inherited controls, including 96 frame controls and 46
cold-ending controls per provider.

`REPOSITORY-CHECKS.json` and `make-verify.log.gz` record the repository-wide
`make verify` run against the stated base commit. That target includes the
required `gen4-bank-verify` and the selected frontier replay. It does not discover
the new research package automatically; the separate fresh replay above covers
the addition. The log hash is over the decompressed bytes, avoiding dependence
on the gzip container.

Check the package and execution evidence with standard-library Python:

```sh
python3 -B research/signed-root-k480-audit/check_receipts.py
```

This command verifies evidence integrity, not the mathematics by re-execution.
For an independent fresh replay, use the sibling package's reproduction guide.
No GitHub CI result is inferred from local execution.

## Discovery evidence and scope

- `PR635-BASE-REPLAY.json` and `PR635-BASE-RECEIPT.json` record our independent
  execution of the pinned predecessor: 64 fresh stages in 441.240 s. Its 51
  artifact hashes and 64 log hashes were checked locally; the predecessor's
  full output tree is not duplicated here.
- `SUBSET-SCREEN.json` records 14 intermediate positive-triangle subsets. Their
  transported endings passed exact row/inverse-column screens. They have not
  received full native/global certification, and no κ is claimed for them.
- `OWNER-SEARCH.json` records a 240-second restricted pattern/flow nomination.
  Its floating solver bound is not an exact certificate or an optimum over all
  owner maps. The admitted literal placement is in the frozen package and was
  checked independently by the fresh exact pipeline.
- `RESEARCH-ENVIRONMENT.json` records versions and resource settings. Discovery
  used at most four parallel subset workers; strict replay used two jobs. Heavy
  processes ran at CPU nice 15 and idle I/O priority.

The package proof note explains the measured tradeoff: fewer helper copies,
but higher terminal frames and worse residual packing for the transported
endings. This does not exclude a better K480 construction. The inherited
all-size and analytic assumptions remain; finite checks do not establish an
unconditional multiplication theorem.

Prepared by Jeremy Diviney with substantial OpenAI Codex assistance.
Apache-2.0; predecessor attribution is retained in the sibling package.
