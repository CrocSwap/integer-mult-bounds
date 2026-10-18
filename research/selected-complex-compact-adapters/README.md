# Sequential compact adapters for the selected complex supplier

We implement the retained compact dirty-control operation on sequential
record streams, including exceptional-record extraction, inverse keys,
stable binary radix passes, reinsertion and cleanup. We also compile the
actual selected Gaussian monomial catalogue into columnwise controls and
unit phases, with forward and inverse execution.

Given a completed ordinary binary interchange with cost `O(V b^tau)`, we
prove the adapter bound `O(V((f log p)^tau+1))` on the retained spaced-axis,
long-record domain. [PROOF.md](PROOF.md) keeps the preparation and repair
charges explicit before absorption. We reuse the existing algebra and
sufficient guard. We claim no new guard, supplier budget or selected kappa.

## Evidence

We bind the actual selected R480/T16 word through the PR1094 archive,
including both 24,767-event local programs. The checks cover:

* 3,474 distinct monomials and 1,778,688 exact local-column cases, including
  affine endpoints, inverse chronology and the retained phase convention.
* Complete small payload executions for earlier/later sources, constant
  toggles and full Gaussian records, with omitted-repair, inverse-key and
  tensor-phase controls.
* A complete 8,388,608-record repair: 6,291,456 exceptional records,
  2,097,152 good records and 23 sequential radix passes.

The selected tensor lift needs a typed distinction. Residual recipe
`0:1000.right` sends two zero columns to `(245,245)` with phase zero. Its
Clifford constant phase repeats once per column. The first role-level SCALE
coefficient remains `-1/2`. Section markers named `phase` do not apply a
Gaussian phase. We test these source-bound distinctions.

[RESULT.json](RESULT.json) records the bounded checks and
[LARGE-RESULT.json](LARGE-RESULT.json) the full repair experiment. In the
large experiment, address oracles prepare the raw input and expected output;
the new interpreter performs the repair. The tests use completed elementary
digit interchanges for compact swaps and record their widths and volumes.
The faster asymptotic contract can use the pending written construction in
[PR2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234).

## Reproduce

Use Python 3.12, the standard library, and repository history containing
commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`:

```sh
python3.12 scripts/research_package.py --package research/selected-complex-compact-adapters
```

The manifest runs normal and optimized bounded checks, with a 300-second
limit for each. To replay the larger experiment and compare its saved receipt:

```sh
python3.12 -I -B research/selected-complex-compact-adapters/verify.py --large
```

That experiment simulates over seven billion bit reads and writes. We keep
it outside the default CI replay. To print fresh receipts without reading
saved results:

```sh
python3 -I -B research/selected-complex-compact-adapters/verify.py --emit
python3 -I -B research/selected-complex-compact-adapters/verify.py --large --emit
```

We authenticate retained code and archives before imports. We change no
selected artifact and do not rerun the full supplier cold replay.

## Open next questions

The complete complex caller still needs its all-size child, ownership,
work and numerical precision composition. [TASK.json](TASK.json) names
concrete next steps. Independent review should also assess the written
fixed-tape argument and the fast ordinary-callee dependency. We do not claim
a full multiplier, transition-table formalization or independent human review.

Jose Manuel ([jmbarrancoml](https://github.com/jmbarrancoml)) prepared this
contribution with substantial OpenAI Codex assistance. [NOTICE.md](NOTICE.md)
preserves predecessor credit. We coordinated through
[Discussion2238](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238).
