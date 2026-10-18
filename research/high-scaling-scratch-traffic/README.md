# Exact physical scratch bill for high-field scaling

The unchanged PR2915 doubling/halving call needs exactly seven free scratch
roles when `S=1`, and eight when `S>1`. With the actual `ScratchPool.install`,
its complete successful physical Tape/Word traffic is exactly `T+A<530 BQS`,
where `T` is PR2951's logical invoice and `A=7+3B+2BQ[S>1]` counts leases.
[PROOF.md](PROOF.md) gives the all-parameter lifetime and trace arguments.

This closes PR2951's released local constructor/lease handoff. One blank-marker
read per acquisition is the entire extra tape bill. Pool roles are reused;
only the returned output remains newly owned. The tape metric excludes
installation, finite-control bookkeeping and initial marker provisioning.
No production code, frozen source or selected frontier changes.

## Reproduce

From the repository root, with standard-library Python 3.12 or newer:

```sh
python3.12 -B scripts/research_package.py --package research/high-scaling-scratch-traffic
```

Or run the primary and controls directly:

```sh
python3.12 -I -Werror -B research/high-scaling-scratch-traffic/verify.py
python3.12 -I -O -Werror -B research/high-scaling-scratch-traffic/test_verify.py
```

The checker uses the complete authenticated PR2915 loader and actual installer,
including its retained physical-pool source, without rewriting its loops.
[RESULT.json](RESULT.json) records 390 complete calls and 152,352 checked payload
bits, eight occupied-pool cases including pooled borrowed sources, and four
real one-role-short rejections. Ten behavioral test groups include a cost
mutant that preserves the checked endpoint, alias-meter inflation, stale close,
installer restoration, source corruption and typed receipt rejection. These
finite checks support the written proof; no new independent-column audit is
claimed. PR2951's full-origin checks remain predecessor evidence.

The `Q=5,B=2` fixtures cost exactly 1,499 operations for `S=1` and 3,959 for
`S=3`, including 13 and 33 acquisitions respectively. Both directions agree.
[VERIFY.json](VERIFY.json) declares every external dependency and bounded replay.

Registered normal/optimized CPython 3.12.15 replay, optimized CPython 3.14
replay and controls, and lint/format checks pass locally on macOS 27.0.1 arm64.
A separate internal source/proof review reran the primary and ten controls
without a blocking finding. The repository workflow suite ran 144 tests with
seven Linux-only skips. These are local results; hosted CI is not claimed.

## Open next questions

- Price one complete high route, including encoded setup, ordinary B1 swaps,
  both scaling intervals and teardown. Start with the reached PR2915 route
  and canonical prefix contract. This is the next local time implication;
  the present exact tape bill does not settle all route costs.
- Bind the pool's fixed finite-control selection and marker provisioning to
  a complete machine-step and physical-storage ledger. Begin with `k+p`
  simultaneous roles and charge initialization once, separating returned output
  disposal and failed calls. Physical placement, arbitrary failure cleanup and
  the rest of the caller remain blockers; unknown charges are not zero.

The decision is to finish this scoped audit without expanding the caller
construction. It supplies neither a full bootstrap-stage reserve nor supplier
admission, a complete multiplication theorem or a new kappa.

## Scope, sources and credit

Base canonical main `0614abaef427f123d9b844f85a759e64ee3ab29c`, priority revision
5. The `selected-stock-envelope` card is explicitly changed to the released
local scratch reserve/time handoff, rather than deriving a whole stage
coefficient. [TASK.json](TASK.json) records that change and freshness;
[SOURCES.json](SOURCES.json) pins inputs and provenance. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18975919)
records coordination. Entry overlap had complete pagination for 240 open PRs,
2,413 closed/merged PRs and 1,660 Discussion/comment/reply records. Metadata
search does not cover arbitrary diffs or unpublished work.

Credit Jose Manuel/jmbarrancoml for PR2915's algorithm, physical-pool integration
and PR2809/PR2697 lineage; David Arias for PR2753's logical caller; Arham Tahir
for PR2877's countdown identity; and PR2951 for the logical scaling invoice.
The selected PR589 work remains DreamingOfClouds' on eumemic's base, with all
source-specific attribution retained. This package adds the exact local free
inventory proof, physical tape transfer and actual-installation corroboration.

Nick Petalas. Apache-2.0. Substantial automated assistance. Evidence is
source-checked written argument and local execution, not independent human or
proof-assistant review. Complete selected cold replay and hosted CI are separate.
PR2809's archive status does not close its pending universal-refinement review;
this audit proves only the local pool implication stated above.
