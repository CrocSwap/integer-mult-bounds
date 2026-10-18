# T185: exact parameter refinement and independent reproduction

This package investigates Dugongue's [PR2863](https://github.com/CrocSwap/integer-mult-bounds/pull/2863)
at `34328b1d5e5bebac62d5cabec993dfbfd7b2123f`. It independently audits its
fixed-inventory optimum, records a failed structural search, and refines the
rational parameters of the **same construction**. Complete baseline and candidate releases passed. The exact gain below is a
precision-only improvement to the explicit certified rational.

The comparison is the conditional integer-multiplication exponent in
`T(n) = O(n (log n)^(1-kappa))`, not a Fourier saving or runtime benchmark.
The reviewed selected record remains separate from this pending lineage.

## Exact comparison and scope

| Quantity | Value |
| --- | --- |
| Pinned baseline | `0.001720100805416885927944 - 10^-46 - 10^-70` |
| Proposed refined rational | `0.0017201008054168859279440070756063355312 - 10^-62 - 10^-86` |
| Exact proposed difference | `7.07560633553120000009999999999999999000000009999999999999999e-27` |
| Construction change | None: same words, allocation, inventory, widths and paid profile |

The independent dual checks all 1,163 permitted patterns and 11 symbolic ties.
T185 already attains that fixed model's fractional optimum. More accurate
rational endpoints approach the same root; they do not improve the optimum.
The refinement method is established prior art. This very small gain is not a
new circuit or evidence of practical acceleration.

The structural pivot screened 216 additional nonzero compensation columns per
provider and 47 entry/frame cases per provider. All 94 frame cases failed
retained interface constraints. See [experiments](experiments/README.md) for
commands and the precise domain. This is a bounded negative result, not a
universal obstruction. Rank 12/nullity 4 was already established in PR2857.

## Reproduction

The bounded registered verifier uses Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/t185-precision-replay --check-only
python3.12 -B scripts/research_package.py --package research/t185-precision-replay
```

It authenticates inputs and complete-release bindings, regenerates both exact
endpoints, reruns independent rational and LP audits, reconstructs the admission
driver, and checks the unchanged outer ledger's 63 strict inequalities and 17
rejecting controls. It does **not** rerun the full native/chronological pipeline.
Full cold reproduction is separate and was developed for POSIX with LF source
bytes. Windows requires the predecessor's documented LF runtime adapter:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git refs/pull/2863/head
git cat-file -e 34328b1d5e5bebac62d5cabec993dfbfd7b2123f^{commit}
git fetch https://github.com/CrocSwap/integer-mult-bounds.git refs/pull/2833/head
git cat-file -e e9307b48d7d1b690939935ecef0f8e524e6d92f4^{commit}
python3.12 -m venv /tmp/t185-precision-venv
/tmp/t185-precision-venv/bin/python -m pip install -r research/t185-precision-replay/requirements-full.txt
/tmp/t185-precision-venv/bin/python -B research/t185-precision-replay/reproduce_all.py \
  --repo "$(pwd)" --work /tmp/t185-precision-cold --jobs 2
```

Use fresh environment and work paths. If a PR head moves, fetch the exact SHA;
the scripts require the pins above. The wrapper performs no fetch and changes
no repository files. It uses at most two native chains and one fine-engine
worker. It exports pinned sources, recovers two manifest-bound files in a
separate copy, reruns portable finite checks, cold-replays the baseline, then
performs complete precision admission using only that fresh native cache.
Logs, commands, exit codes, timings and hashes stay under `--work`.

This session executed the complete baseline and candidate stages separately
(1364.56s and926.09s). The combined orchestration script received syntax/help
and source-export preflight; an additional combined cold run is not claimed.

`inputs/pr2863` is an explicitly labelled scientific subset for bounded checks,
not a complete export. The cold command obtains full source from Git objects.
`DEPENDENCIES.json` pins the source manifests.

## Baseline portability findings

The original published wrapper fails: its manifest lists two absent
`.gitattributes` files. Their exact bytes, `* -text\n`, were recovered in a
separate copy and match the original manifest. That copy's finite wrapper then
fails a regenerated gzip comparison: only byte 9 differs, while all 14,452,025
decompressed bytes agree. Immutable container hashes remain enforced. A
separate adapter checks exact regenerated payloads, as CONTRIBUTING.md
requires; neither original checker nor manifest is edited. Mutation controls
reject changed payloads, truncation and changed immutable containers. See
[the audit](notes/PORTABILITY.md).

The original wrapper is **not reported as passing unchanged**. Complete
admissions are independently recorded. The derivative driver keeps the original
coarse/fine moment-checking block; the refiner only generates parameters.

## Evidence and limitations

`PROOF.md` gives the argument and inherited assumptions. `evidence/` records
source-bound receipts and commands. Early screens and agent notes are historical
screening evidence, not complete releases. `inputs/admitted-outer` contains
the actual released parameters.

Both requested repository gates were run on clean pinned main
`1cdd4bf6507eeb2d045335e5f6216152ac28aaad` before this package was added.
`make verify` failed a historical singleton-target unpacking; selected
`make frontier1094-verify` failed a historical source/supplement hash check.
Original exit codes and logs are retained. No expected result was changed.

Finite releases remain conditional on inherited compiler/all-size, hosting,
common-label/mutable-source, precision/tape, exact-recovery, ordinary recursion,
BIT H1-H5 and analytic-transfer interfaces. Finite certificate success is not a
formal proof of the complete asymptotic theorem.

## Open next questions

1. Can a changed native or consumer contract reduce the paid profile beyond
   the fixed-inventory optimum? Apply the dual marginal screen to a specified
   interface change or relation using at least two helpers outside the known
   quartets. Charge conversion, cleanup, ownership and precision costs. The
   one-helper frame attempts here failed retained interfaces.
2. Can one retained all-size compiler or precision/tape implication be proved
   for the actual words? Pin one statement and operational model; additional
   finite matrix tests alone cannot establish uniform all-size behavior.

Structured questions and the bounded budget are in `TASK.json`.

## Credit

Prepared for digitalis-p with substantial OpenAI Codex assistance, including
four delegated agents. No independent human review is claimed. The construction
is Dugongue's T185 allocation using Yiyang/Lyy-iiis's shared-kernel words and the
retained vacancy-relay/replica lineage. The parameter-refinement method follows
credited prior work. See `NOTICE`, predecessor `CREDITS.md`, and `LICENSE`.
