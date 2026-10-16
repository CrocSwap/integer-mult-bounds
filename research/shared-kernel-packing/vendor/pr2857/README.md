# Four shared dirt kernels and chronological repacking

This package establishes a **conditional finite supplier and modern outer
release** with

```
kappa = 0.001720096628684832600972 - 10^-46 - 10^-70
```

The exact rational is in [CLAIM.json](CLAIM.json). Both changed providers run
fresh native chains; the complete strict supplier and modern outer checks return
`PASS_RELEASE`. Retained provider and parent proofs are reused with exact
full-tree source bindings. This is author-checked, with separate AI-assisted
checkers, not maintainer acceptance or a full theorem formalization. The selected
result remains unchanged.

| Pinned comparison | Headline κ (display rounded) | Exact/approximate gain |
| --- | ---: | ---: |
| [PR2848](https://github.com/CrocSwap/integer-mult-bounds/pull/2848), `c50d12e4720cd1fef2b5a65e337e37de9731879a` | 0.001718658508304930 | exactly `1438120379902596153 / 10^24` |
| [PR2853](https://github.com/CrocSwap/integer-mult-bounds/pull/2853), `d01045dfb67428679618027dff552f1d032fa999` | 0.001719377658697587 | approximately `7.189699872459419e-7` |
| This contribution | 0.001720096628684833 | exact rational comparisons in `CLAIM.json` |

The PR2848 gain is about `1.43812e-6`, exceeding the donor's preferred `1e-6`
target. This is an exponent saving, not a measured runtime speedup.

Fresh overlap found @philippeVV's concurrent PR2853 on the **same four helper
quartets**. That work uses an early-read schedule with local delta
`20 H1 - 12 H2`. Here delayed within-pair mixing and a different compensation
basis give `12 H1 - 8 H2`, followed by a new actual owner fill. This credits the
shared mechanism and helper selection; no priority or exclusive discovery claim
is made. Both comparisons are against frozen heads, not all current work.

## Construction

The scientific baseline is Jeremy Kothe's PR2833, exact head
`e9307b48d7d1b690939935ecef0f8e524e6d92f4`, whose source package has 541
manifest entries. In each of four disjoint helper quartets, the compensation
matrix has rank three with kernel `(1,1,-1,-1)`. A staged reversible change of
raw dirt makes one compensation column zero, permitting a one-line entrance
frame and reducing a helper width from nine to eight.

| Quartet | Helper with smaller width | New entrance line |
| --- | --- | --- |
| 478, 479, 490, 491 | 478 | 25 |
| 460, 461, 468, 469 | 460 | 7 |
| 462, 463, 470, 471 | 462 | 7 |
| 480, 481, 492, 493 | 480 | 25 |

For a quartet ordered `(q0,q1,q2,q3)`, the raw-dirt map is
`q1 += q0; q2 -= q0; q3 += old q2 - q0`. With matrix `S`, the new A map is
`A_old*S` and compensation is `C*S`. Its first column vanishes; its third is
the sum of the old third and fourth columns. Mixing within each pair only after
its first A writes preserves the inherited two-dimensional frames. The producer
regenerates the inverse cleanup; [PROOF.md](PROOF.md) and the independent
`check_four_kernels.py` explain and check the full operator, not only the kernel.

| Child rank | PR2833 per call | New per call |
| --- | ---: | ---: |
| 1 | 2382 | 2394 |
| 2 | 650 | 642 |
| 3 | 266 | 266 |
| 4 | 128 | 128 |
| 5 | 26 | 26 |
| 8 | 8 | 8 |

The helper inventory becomes `{4:26,5:2,7:62,8:84,9:234}` from
`{4:26,5:2,7:62,8:80,9:238}`. The interface still has 408 helpers, 72 private
buffers and 632 live independent inputs. All 20 added A operations, 20 inverse
cleanup operations, compensation and frame changes are charged.

Reusing the old fill loses. The new **T37** construction uses 333 calls
(125 base, 208 extra), assigning every one of 135,864 helper roles under the
actual chronological windows, family and offset guards. `FILL.json.gz`,
`ORDER.json`, `DISPATCH.json` and `PROFILE.json` are the literal witness. Its
complete profile, including idle children, is

```
{1:805860, 2:213786, 3:91775, 4:42624, 5:13098, 8:2664, 9:1, 48:13379}
```

There are 33,152 live and 33,642 physical families; rank mass is 2,408,256.
The independent exact moment audit brackets the complex endpoint between
`17200966286848326009728 / 10^25` and
`17200966286848326009729 / 10^25`. The modern outer wrapper applies the strict
margins displayed above. The inherited supplier bootstrap certificate has the
lower κ `0.001717142976839401`; it is a different layer and is not this headline.

The local coverage-law packing ceiling is in
`[0.001758838083985131367624, 0.001758838083985131367625]`.
The headline realizes **97.797326789%** of its upper bound. The tighter
changed-inventory, fixed-capacity fractional relaxation has upper bound
`0.001720100805416885927945`; this construction realizes **99.71041112% of the
available gain over PR2848**. An independent checker enumerates all 1,163
patterns, proves the primal balances and dual signs (11 tight, 1,152 strict),
and brackets its complete moment. These relaxations are not chronological
witnesses or universal barriers. See `evidence/relaxation/` and
`evidence/full/CEILING-REALIZED.json`.

## Evidence

- `verify.py` regenerates both complete decoded words and runs the separate
  exact 68-check audit per provider, with semantic, cleanup, source-binding and
  optimized-mode rejection controls. It imports only the pinned pure producer.
- `audit_owners.py` independently checks all roles, original template projection,
  windows, dimensions, disjoint offsets, provider-word bindings, idle bill,
  prefixes and exact moment. Four targeted owner/source mutations are rejected.
- `evidence/full/` retains the executed full replay scripts, manifests, logs,
  invoices, cache receipt and modern outer evidence. The release receipt SHA256
  is `c052decb90ceae345b398f111781f567fb787309a528877500cf7fe1cff13b3d`.
  Actual rejected controls include 119 admission, 12 bit, **25 controller**,
  8 owner and 6 geometry mutations; the modern outer ledger checks 63 strict
  inequalities and 17 rejections. `ACTUAL-CONTROLS.json` counts the actual
  serialized arrays; inherited summary metadata saying 15 controller checks
  is stale.
- `check_release_evidence.py` binds all 167 full-release evidence files and
  63 native archive members to the shipped words, owners and exact claim. It
  checks the actual outer margins and rejects 20 targeted corruptions without
  importing packaged Python or extracting the archive.
- `integration-review/` checks the exact admission AST and 11-path source
  overlay (five modified, six added), retaining all previous checks. It rejects
  20 altered-source/control cases, including with Python optimization enabled.

An initial full replay **failed**: the inherited geometry `old_call_count`
mutation set both counts to 333, exactly the correct count for this T37 witness,
so it changed nothing. The corrected derived test subtracts one from each
actual charge and checks that every mutant changes its inputs before calling
the unchanged assembly predicate. All six geometry controls remain required.
The complete replay was then rerun and passed. Failed artifacts and the exact
correction are retained in `evidence/full/experimental-failure/` and
`integration-review/FAILED-V1.json`; this is not a waived test.

## Reproduction

From the repository root, metadata and the bounded, standard-library checks:

```sh
python3 -B scripts/research_package.py --package research/shared-kernel-repacking --check-only
python3.12 -B scripts/research_package.py --package research/shared-kernel-repacking
```

`VERIFY.json` lists every command explicitly. Locally these commands were
executed directly with **Python 3.13.7**, not the generic Python 3.12 runner;
no hosted CI or fresh Lean result is claimed. The fast checks inspect and bind
retained release evidence; they do not substitute for rerunning the full native
and outer pipeline.

For the full reproduction, use a Python environment with the exact pins in
`requirements-reproduction.txt`. Keep bytecode disabled for all frozen inputs.
Fetch the frozen scientific source once, then materialize it from local Git
objects. The exporter verifies its entire 541-file manifest before writing:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git refs/pull/2833/head
pkg="$PWD/research/shared-kernel-repacking"
work=$(mktemp -d)
export PYTHONDONTWRITEBYTECODE=1
unset PYTHONOPTIMIZE
python3 -B "$pkg/materialize_source.py" --repo "$PWD" --out "$work/pr2833"
mkdir "$work/retained-cache"
tar -xzf "$pkg/evidence/retained/NATIVE-CACHE.tar.gz" -C "$work/retained-cache"
python3 -B "$pkg/reproduce.py" \
  --source "$work/pr2833" --words "$pkg/words" \
  --fill "$pkg/FILL.json.gz" --order "$pkg/ORDER.json" --dispatch "$pkg/DISPATCH.json" \
  --retained-cache "$work/retained-cache" \
  --retained-receipt "$pkg/evidence/retained/NATIVE-RECEIPT.json" \
  --comparison-claim "$pkg/sources/PR2848-CLAIM.json" \
  --comparison-latest-claim "$pkg/sources/PR2853-OUTER-CLAIM.json" \
  --work "$work/release" --jobs 4
```

The executed wrapper completed in about 259 seconds locally. It freshly runs
**both changed current native chains** and authenticates the exact retained
cache, receipt and source trees for **two retained native chains and the
16-stage retained parent proof**. This is explicit source-bound reuse, not a
fresh cold replay of every predecessor. Paths and timing make replay receipts
run-specific; regenerated compressed words are compared by complete decoded
content. Committed source containers retain exact byte pins.

The allocation can be reconstructed without a solver or network, from the
committed exact flow and original source template:

```sh
python3 -B "$pkg/allocation/replay_allocation.py" \
  --source "$work/pr2833" \
  --owner-engine "$pkg/vendor/pr2839/independent_owners.py" \
  --work "$work/allocation"
```

This checks the mathematical flow constraints before the retained edge-coloring
realization. Regenerated FILL equality uses the **whole decompressed payload**,
with a successful changed-gzip-container control and a rejected changed-payload
control. The original discovery used OR-Tools 9.14.6206 (four workers, seed 124,
300-second cap): T37 was feasible in about 39 seconds. `OPTIMAL` here is a
feasibility solver status, not proof of an optimal bound. A T124 attempt timed
out `UNKNOWN`; no impossibility claim follows. Search code, exact flow, model,
solver settings, controls and predecessor attribution are retained in
`allocation/`.

## Open next questions

Finite evidence remains conditional on inherited all-size compiler,
source-access, hosting, precision/tape and analytic interface obligations.
There is no new Lean kernel audit, unconditional multiplication theorem,
maintainer review or selected-frontier change.

Further repacking of this inventory has at most about `4.18e-9` of the displayed
fixed-capacity relaxation gap, so it does not justify another search for a
`1e-6` gain. A materially larger follow-up should change the local or
source-consuming contract and first price its complete consumer, cleanup,
transport and precision costs. A separate useful task is to close one named
all-size interface obligation. [TASK.json](TASK.json) records these questions,
feasible first steps and blockers.

## Credit and coordination

Prepared for Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance,
including separate construction and audit implementations. Builds on Jeremy
Kothe's PR2833 dirt-entry words; concurrent @philippeVV PR2853; Marius-Paul
Dumitrean's PR2843 owner construction and earlier local words; Dugongue's PR2839
tensor-block interface; Tekalign's native/admission work; and the other retained
source authors. See [NOTICE](NOTICE) and source-specific notices and licenses.
New work is Apache-2.0.

The initial base is `c719a5e0b3a6760a6fdf5d5af82d6ff2399329e5`; the branch was
advanced to current main at `130a7ce63a233e6812b7c037993c721fec827014` before
submission without changing scientific pins. Latest priority/overlap coverage is in
`TASK.json`. The canonical coordination update is
[Discussion #2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18963373).
