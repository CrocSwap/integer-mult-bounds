# Thirty-seven replicas on the unchanged U8 word

This finite witness gives conditional

```text
kappa = 1661960547713947 / 10^18 = 0.001661960547713947.
```

The gain over [PR890](https://github.com/CrocSwap/integer-mult-bounds/pull/890),
`0.001661957774647029`, is **0.000000002773066918**. This is a tiny improvement
from whole-helper owner packing. The U8 local word, its 504 helper widths, and
the PR589 bit supplier are unchanged.

This package is a research submission. It does not change the repository's
[selected result](../../certificates/selected-result.json). The two prerequisite
PR890 directories, [`complex-t21-owners`](../complex-t21-owners) and
[`complex-t21-owner-bound`](../complex-t21-owner-bound), are retained unchanged,
including their original claims, notices, manifests, and source pins.

## Construction and changed allowance

The construction combines PR890's T21 owner map and the inherited T16 map in
disjoint replica namespaces. It merges their complete call orders by comparing
the T21 event index times 144 with the T16 index times 189, breaking ties in
favor of T21. [EDITS.json](EDITS.json) gives the eight subsequent owner edits;
[ORDER.json](ORDER.json) and [OWNERS.json.gz](OWNERS.json.gz) freeze the result.
The independent constructor derives this map without importing a search or
owner generator. Omitting any one of the eight edits is rejected.

The remainder trade is `44 + 3 + 2 -> 48 + 1`. An early width-four helper fills
a larger bin, while the displaced late helper joins the two capacity-32 bins.
Their roles repartition as `32 = 8 + 6*4` and `31 = 3*9 + 4`.

| Quantity | T37 witness |
| --- | ---: |
| Replicas | 37 |
| Complete calls | 333 |
| Whole-helper roles | 167,832 |
| Live families | 33,152 |
| Physical families | 33,666 |
| Rank deficit | 11,840 |
| Idle profile | `{48:11086, 1:6}` |

The full paid profile is

```text
{1:848490, 2:112554, 3:148518, 4:53946, 5:23976, 8:2664, 48:11086}.
```

PR890's fixed-family bound assumes a 512-bit prefix charge. T37 exceeds that
allowance: the retained conservative formula gives
`72 + 37 + 333 + 333 + 4 = 779` bits. This witness **charges 1024 bits**, using
the repository's existing larger-reserve mechanism. The recomputed physical
row coefficient is `17495 < 20161`; the row charge and bootstrap cutoffs use
the enlarged allowance. The bit supplier retains its original 512-bit charge.
This explicitly changes the prefix hypothesis of the earlier family bound.

Five dedicated bank groups have `8,8,8,8,5` active lanes. The partial group's
complement coordinates are checked independently, and the final hosted
controller removes all dedicated banks. Whole roles retain their full widths,
actual bridge-aware windows, physical families, offsets, and coordinate charts.

Both exact moment engines accept complex endpoint
`0.001664727258740678855772` and reject its successor on the `10^-24` grid.
All 47 outer inequalities pass at the stated kappa. The separate
[all-replica proof](ALL-T-PROOF.md) gives the same `10^-18` upper grid point
for every positive replica count in the fixed U8/width/capacity/outer-recipe
relaxation. It does not bound different local words, helper splitting, other
capacities, or other outer recipes.

The retained [arithmetic evidence](evidence/README.md) includes the exact
assembly and all-replica bound receipts. These snapshots are not verifier inputs.

## Reproduce

From the repository root, use Python 3.11+ with assertions enabled, Bash,
a C++17 compiler, Boost headers, and the inherited scientific dependencies:

```sh
python -m pip install -r research/e8-bit-p111-tuned/requirements.txt
python -B research/complex-t37-owners/package_controls.py --out /tmp/T37-PACKAGE-CONTROLS.json
python -B research/complex-t37-owners/verify.py --work /tmp/t37-cold
```

The package controls check source closure, reject five package/dependency
mutations, and check nine explicit guards against optimized Python. Their output
file and the replay output directory must be new and outside the checkout.
The default replay rebuilds
PR589, PR741, and PR799 from their pinned source chain, verifies ancestry
coverage and bindings, and rebuilds U8 including its native phases. It then
checks the frozen owner construction, every role and chart, the partial-bank
parent, both exact prices, emitted controller, full invoice, and final result
bindings. The metadata-recording pass and the strict replay use separate fresh
directories. No owner optimizer runs.

An already completed PR799 replay may be explicitly reused:

```sh
python -B research/complex-t37-owners/verify.py --work /tmp/t37-reuse \
  --baseline799 /absolute/path/to/completed-frontier799
```

Its complete ancestry coverage and official source/artifact bindings are
rechecked. U8 and T37 are rebuilt in either mode. The successful top-level
receipt is `RESULT.json`, with status
`PASS_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY`; `FINAL-BINDING.json` identifies
the checked receipts. A reused completed baseline is identified explicitly.

The checks include 38 U8 construction cases, 95 inherited end mutations,
six independent owner mutations, eight omitted T37 edits, eight partial-bank
mutations, fifteen controller mutations, 69 assembly admission mutations,
twelve bit-supplier mutations, and eleven payload/prefix/row mutations.
Seven additional reserve boundaries exercise strict prefix and row limits.
Source-to-runtime adaptations are recorded and checked; predecessor files
remain unchanged. For regenerated compressed artifacts, proof-relevant content
identity is distinguished from the compressed container hash.

After the completed replay, binding controls reject twelve actual-file mutations
and check eight optimized-Python guards:

```sh
python -B research/complex-t37-owners/binding_controls.py \
  --work /tmp/t37-cold --baseline /tmp/t37-cold/baseline799 \
  --out /tmp/T37-BINDING-CONTROLS.json
```

The [focused workflow](../../.github/workflows/t37-owners.yml) runs the package
controls, default cold replay, and binding controls on Ubuntu with Python 3.11
and 3.14, checks that tracked files stay unchanged, and retains small receipts
and logs. Large emitted programs and controller trees are not uploaded. A successful local replay and a successful
hosted CI run are separate evidence; the workflow's result reports the latter.

## Scope and attribution

All-size compilation, common-label/mutable-source realization, whole-call
hosting, precision/tape, analytic transfer, and bit H1-H5 remain inherited
hypotheses. Finite certificate success is not a formal verification of the
complete multiplication theorem or a measured multiplication speedup.

This builds on Chafik Boukhalfa's PR890 and PR741, Hao Yan's PR858, Jeremy
Kothe's PR799, the PR869/870 U8 lineage (NewBArch's triangle-hybrid construction
and ColdWitness/icekylinx's driver and composition), the PR589 bit lineage,
the retained supplier and controller work, the PR795 signed dual, and the
exact arithmetic engines
credited in their source files. Predecessor notices and source pins remain
intact; see [PR890's notice](../complex-t21-owners/NOTICE.md).

Prepared with substantial OpenAI Codex assistance, including separately
implemented AI checks. No independent human review is claimed. New work is
under Apache-2.0; retained source-specific licenses and notices continue to
apply.
