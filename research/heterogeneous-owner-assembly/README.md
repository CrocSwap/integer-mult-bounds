# A bound for mixed providers in one owner pool

No mixture of the **71 provider records, with 25 distinct cost interfaces,**
in the pinned catalogue can improve the U8/T37 complex moment. This holds
for every positive replica count. Calls can use different providers and can
share the entire owner pool. The bound allows real call counts and removes
all time and matching restrictions. It also allows idle remainders to split.
Helpers must stay whole, and the data capacity inventory must stay fixed.

The new result is the common dual for **different helper inventories**. A
provider changes both the local paid profile and the width and signed price
of the helpers in the shared pool. Comparing separately packed providers
does not prove this result. The signed bin prices and the U8/T37 witness
come from earlier work. See [PROOF.md](PROOF.md) and [NOTICE.md](NOTICE.md).

For `0 < b <= 1/500`, each call outside the U8 cost interface has a strict
penalty greater than `1.9*b`. For the 22 interfaces with a different helper
inventory, the penalty is greater than `336*b`. At the U8/T37 root, the
respective certified floors are `27/4000` and `113/200`.

The complete catalogue is defined by all
`research/*/data/SPEC*.json` files at base
`8bddbee377e2f3ce1f1247196c4b290d55767d20`. There are 35 files. The
[registry](CATALOGUE.json) retains every source record and exact source hash.
Equal cost interfaces share an ID; no record is removed. This is a bound
for this catalogue, not for all possible factories.

The existing seven-step outer recipe gives the same grid ceiling,
`0.001661960547713947`. This package does not improve kappa. The selected
frontier is unchanged. No new supplier, physical owner map, finite invoice,
or cold replay is claimed. The theorem takes each recorded paid profile
and helper inventory as its call contract. It allows even combinations
whose physical compatibility has not been established.

## Reproduce

Use Python 3.11 or later and the standard library. Run from the repository
root with a fresh output filename:

```sh
python3 -B research/heterogeneous-owner-assembly/verify.py \
  --audit-base-tree --out /tmp/heterogeneous-owner-bound.json
```

Expected result:

```text
PASS_HETEROGENEOUS_OWNER_CATALOGUE_BOUND records=71 interfaces=25 kappa_grid_upper=0.001661960547713947
```

The default check replays the frozen source list. It needs no network or Git
history. `--audit-base-tree` also checks the complete pinned Git tree, using
`git ls-tree` and `git show`. Omit this option in a source export that lacks
the base object. `--audit-current-tree` reports later records as outside the
bound. Adding an unrelated provider does not change the default proof.
Changing a registered source causes failure.

The separate integer-form check and the controls are:

```sh
python3 -I -O -B research/heterogeneous-owner-assembly/independent_check.py \
  --out /tmp/heterogeneous-owner-independent.json
python3 -B research/heterogeneous-owner-assembly/controls.py \
  --out /tmp/heterogeneous-owner-controls.json
```

The expected statuses are `PASS_INDEPENDENT_INTEGER_MIXTURE_DUAL` and
`PASS_HETEROGENEOUS_OWNER_CONTROLS`, with 14 controls. The independent check
does not import the primary checker. It uses an integer form of the dual
and a fill recurrence. It remains active with `python -O`. The primary
checker rejects that mode because the retained outer engine uses assertions.

[evidence/EXACT.json](evidence/EXACT.json) records two exact rational interval
engines, all 1,163 bin patterns, 92 maximum-price cases, all 25 provider
penalties, the root signs, the PR589 surcharge, and all 47 outer constraints.
[evidence/INDEPENDENT.json](evidence/INDEPENDENT.json) records the separate
check. [evidence/CONTROLS.json](evidence/CONTROLS.json) records source drift,
missing records, wrong aliases, a mass-preserving profile change, excessive
bin credit, later source growth, optimized execution, and output preservation.

The controls also reject three favorable profiles outside the catalogue:
the U10 delta from PR987 and the R489 and R480 interfaces from PR1004/1005.
The last two change the helper inventory. Their reduced costs are negative.
Thus this bound does not exclude those new constructions. The controls
check their cost vectors only; they do not repeat their native admission.

Changes to the data capacity inventory, helper migration across data
boundaries, split helpers, deferred restoration that changes the paid
contract, new local profiles, or a different outer recipe are outside this proof.
All inherited all-size, compiler, common-label, mutable-source, hosting,
precision, tape, analytic-transfer and bit H1-H5 assumptions remain.

Prepared for Ali Romman (@aliromman) with substantial OpenAI Codex assistance.
There is no claim of independent human review or full formal verification.
