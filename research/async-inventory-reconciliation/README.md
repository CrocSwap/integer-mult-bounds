# Source reconciliation for the archived asynchronous inventory bound

**Research consolidation; no new κ.** All 146 copied profile/width pairs in
the archived asynchronous inventory certificate agree with their retained
constructor results. Both original exact receipts reproduce byte-for-byte.
The companion checker closes a provenance gap and makes its mathematical
rejections explicit, including under Python optimization.

There is a concrete false-success case in the archived entry point: delete
every menu word's rank-one charges and run its verifier with `-O`. Both engines
still emit `PASS_EXACT_FIXED_INVENTORY_FINITE_MENU_DUAL_WALL`, although their
moment-minus-one lower bound is approximately **−0.30861318239717017**.
The ordinary, assertion-enabled command correctly rejects that input.
Changing a menu source path to a nonexistent path also passes with or without
optimization: the old arithmetic verifier treats provenance fields as inert
metadata. That second experiment is a missing provenance check, not a
counterexample to its rational arithmetic.

These are controlled alterations, **not corruption of the committed evidence**.
The archive's documented command does not enable optimization. Its original
sources, manifests, reports, and claims are preserved without modification.

## Reproduce

From the repository root, with UV and Python 3.10 or later available:

```sh
uv run --offline python -B research/async-inventory-reconciliation/verify.py
```

Expected:

```text
PASS_ASYNC_INVENTORY_RECONCILIATION 146 source rows, 696 dual inequalities, 24 rejection controls, 12 historical replays
```

The command uses the standard library and requires no network or solver. It
compares its deterministic report with [RESULT.json](RESULT.json). Every
historical subprocess writes to a fresh temporary directory. The same command
with `python -I -O -B` checks that the companion's rejection conditions survive
optimization. `--write /absolute/new-report.json` saves a report to a fresh
path instead of comparing it with the committed result.

Local validation on macOS used Python 3.10.21, 3.13.15, and 3.14.7; reports
agreed, including isolated optimized runs. Seven focused tests pass normally
and under optimization:

```sh
uv run --offline python -I -B research/async-inventory-reconciliation/test_reconciliation.py
uv run --offline python -I -O -B research/async-inventory-reconciliation/test_reconciliation.py
```

The original archive integrity check and the selected-record/source-inventory
check also pass. No repository-wide supplier rebuild was run: this additive
package changes neither construction sources nor selected certificates.
Hosted CI and the full mathematical theorem remain separate from these checks.

## Evidence chain and completed coverage

The exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCE-PINS.json](SOURCE-PINS.json) pins the original verifier, both arithmetic
engines, copied menu, two exact receipts, explanatory records, and the archive
manifest. That manifest supplies hashes for every resolved constructor result;
the companion checks both the manifest's own pin and those actual file bytes.
The inventory-bound archive was introduced by commit
`01ad6ae33543b4df9732e7399a21f115d5cf94fd`. The subsequent research integration
records PR477 at `a5b588d7f16be383ec80e6c5adaa1a75049cb758`, with scope limited
to archive integrity/navigation rather than historical mathematical replay.

| Source family | Rows checked | Retained status |
|---|---:|---|
| `complex501-selective-gauges` | 65 | `PASS_LOCAL_CONSTRUCTOR_ONLY` |
| `complex501-kernel-gauge-trades` | 78 | `PASS_LOCAL_CONSTRUCTOR_ONLY` |
| `async505-retimed-new-kernels` | 3 | `PASS_LOCAL_CONSTRUCTOR_ONLY` |

The last three menu labels add `retimed-` to their source labels; the aliases
are explicit. The first 143 source reports call their width histogram
`width_counts`, while the last three call it `widths`. All numerical entries
agree exactly after this field-name mapping. Every row contains 560 helpers.
There is no new constructor replay or physical admission of these 146 words.

The fixed model has ambient dimension 73, 7,680 live families, 72 complete
invocations, widths `{5,7,8,9}`, and capacities with multiplicities
`{8:5760,16:3840,32:3840,48:3840}`. At
`b = 1373311441205186394131 / 10^24`, the independently enumerated multiplicity
tuples give 4, 14, 77, and 253 legal patterns for those capacities: **348 per
engine**, including empty patterns. This enumeration differs from the archived
verifier's recursive enumeration of nondecreasing width lists.

For each engine, the checker evaluates all dual inequalities, all 146 reduced
word costs, the minimum, its exact bound and strict margin, and the retained
six-step outer recurrence. Both margins remain positive (approximately
`3.1131651758e-26` and `3.1123866414e-26`); `baseline` is the unique minimum.
The exact rational margins are retained in RESULT.json. This corroborates the
historical obstruction at its original endpoint; it does not improve it.

## Why these checks imply the scoped obstruction

Let `c(r)` be the moment numerator for a paid remainder of rank `r`, including
the inherited `10^-16 * 32*m^2` rank-one fallback charge per paid child, and
let `c(0)=0`. The pinned engines give outward rational bounds on these costs.
For each available capacity `r` and every fitting helper pattern `p`, the
companion checks

```text
alpha[r] + sum(beta[w] for w in p) <= lower(c(r - sum(p))).
```

Summing over all capacity bins bounds the remainder cost below by the
inventory's alpha contribution plus the total helper beta contribution.
For each whole-word menu choice, the checker adds its local paid profile
cost to its helper beta contribution. Therefore even a fractional mixture
of 72 menu choices pays at least 72 times the smallest reduced word cost.
Dividing their sum by `m*live` gives the independently recounted bound.
Its value is strictly above one at the rejected endpoint. The nonnegative
moment terms increase with the saving, so this fixed model cannot certify
that endpoint or a larger one. Discarding chronology, distinct-call owner
constraints, and integrality only enlarges this model.

The retained outer recurrence is checked separately, with its original
eta, beta, initial value, six steps, and rounding grid. No other outer
assembly is excluded. This derivation inherits the interval engines and
fallback law; the companion is not a third implementation of transcendental
enclosures or a formal proof of the general multiplication theorem.

## Negative controls and historical discrepancy

Twelve distinct controls run against each engine: nonexistent source,
changed paid profile, changed widths, omitted row, duplicate source,
boolean in place of an integer count, raised capacity dual, raised width
dual, wrong input digest, changed bound, changed outer grid, and deleted
rank-one charges. All 24 checks reject. In particular, the deleted-charge
control reaches the mathematical `bound > 1` check independently of source
binding. The original entry point is also replayed on unchanged inputs and
the two counterexample inputs, both normally and under `-O`, for both
engines (12 subprocesses). All four unchanged receipts match the committed
bytes; the altered-input behavior is recorded separately in RESULT.json.

This is finite evidence reconciliation. It does not establish the physical
legality of every menu entry, validate an LP solver's completeness, extend
the fixed word menu, or certify all-size compilation, common-label/mutable
basis realization, hosting, precision/tape/exact recovery, or analytic
transfer. No new κ and no failure of the selected #626/#543 construction
is claimed. The selected record and `upstream/` are unchanged.

## Attribution and coordination

Rohan Arun supplied the archive, source searches, inventory-dual construction,
and portable certificate, with the AI-assistance disclosure retained in the
original records. Credit remains with the PR501/502 retiming authors, PR505
whole-owner construction, PR496 pooling, PR484 gauges/kernel, DreamingOfClouds
and preceding suppliers. The arithmetic is the pinned PR361/Mercator engine
and Douglas Colkitt's independent base-two cross-check inherited through that
chain. Colkitt's integration records explicitly separated archive integrity
from mathematical replay.

This companion was prepared by Alexander Templeton (`azide0x37`) with
substantial OpenAI Codex assistance, under Apache-2.0. It is not independent
human peer review. [CLAIM.md](CLAIM.md) records seed 95, the three candidate
tasks, base, overlap checks, bounded coverage, and timing. No new search was
run. PR695 concerns selected Linux evidence, PR704 concerns the central review
ledger, and PR630 corrects a different E6 archive screen; this contribution
depends on none of those pending changes.
