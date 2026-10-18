# The PR848 pair does not retain its saving on the PR1062 star word

**Fixed-pair composition result; no new κ or supplier.** This answers one
explicit next question in Victor Li's [PR1805](https://github.com/CrocSwap/integer-mult-bounds/pull/1805):
compose its `277→434` helper-sharing wrap with the 11,500-ADD PR1062 word and
recompute the complete boundary and invoice. Exactly three stated splices are
tested. The original pair's 65-ADD saving does not survive these compositions.
No claim is made about other cuts, pair choices or unrestricted optimization.

The parent is Sagar Thakrar's
`research/r439-bsection-stars-seed01/candidate.json.gz` on main
`c4e06b3822987b4272c70ff82ae1c84773ee4426`. It has 111 sources, 111 targets
and 439 arbitrary-dirty helpers (661 input columns). In this note `a=277`,
`b=434` and G executes **`a ^= b`**, with every D operation at frame zero.
Entry preparation and final restoration each cost one scalar ADD.

## Three literal, fully charged cases

| Case | D / complete ADDs | F / B | local / nine-stage bits | complete dirty D boundary |
|---|---:|---:|---:|---|
| PR1062 parent | 5,548 / 11,500 | 25,717 / 5,911,840 | 95 / 182 | exact |
| naive entry wrap, target-only edits, exit wrap | 5,551 / 11,503 | 26,097 / 5,912,595 | 96 / 182 | **fails** |
| whole-prefix conjugation, including helper gates | 5,557 / 11,509 | 28,453 / 5,913,350 | 96 / 182 | exact |
| prepared-middle wrap and column correction | 5,551 / 11,503 | 26,173 / 5,911,840 | 96 / 182 | exact |

All three numerical invoices fit the inherited 104/192-bit guards. The naive
case is nevertheless inadmissible: it restores every helper but changes 68
target rows. Target 111 exposes dirty input column 434. A numerical guard is
not a boundary proof. PR1805's original constructor explicitly requires
target-only D writes and rejects a helper-writing D; this negative case is a
deliberate extension outside that precondition, not a predecessor software bug.

The corrected cases preserve the complete 661-column D operator and the
literal whole-word COPY/ERASE endpoint in both directions. Their A, scatter,
B, C, labels and prescribed start/final frames stay fixed. Ordered frame paths,
nine rank-seven COPY/ERASE pairs and the paid profile remain
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, rank mass 5,129.
Thus neither case improves the recursive profile. The bit side is nonbinding
in the selected result, and these are not proposed selected suppliers.

## Why the helper basis matters

The exact D slices are:

```
[0,236)       helper preparation: 236 gates
[236,542)     target preparation: 306 gates
[542,653)     middle: 111 target gates, 4,464 helper reads
[653,959)     target postprocessing: 306 gates
[959,1195)    reversed helper preparation: 236 gates
```

All are frame zero and source-free. At the middle, helper values already have
the prepared basis P. Let M be the middle helper-to-target matrix. A restored
middle wrap is valid with `M' = M G`, since `M' G P h = M P h` for every h.
For this fixed orientation, the prepared columns have weights 1 (a), 13 (b),
and 14 (their XOR). There are no middle rows containing both a and b, and
exactly one containing a alone. The column correction adds one read; two paid
wrap gates give **three more ADDs**. The pair's earlier saving was measured
in PR589's different D basis and cannot be added to PR1062's scalar saving.

For a whole-prefix wrap, helper gates must be transformed too. In column-vector
convention put `G=I+e_a e_b^T` and `E_ds=I+e_d e_s^T`. Since `G²=I`,

```
G E_ds G = I + (G e_d)(e_s^T G).
```

Conjugate every literal D gate, including its helper operations, and put G at
both ends. The complete product is then D again, so its zero-frame prefix
boundary is unchanged on every F2 module. This is standard elementary
conjugation, not a new algebraic identity. The implementation charges every
resulting scalar ADD:

- `d=b,s=a` becomes the three-ADD exchange of a and b.
- `d=b,s` different from a and b becomes `a ^= s; b ^= s`.
- A different destination reading a additionally reads b; grouped source
  sets are combined by exact symmetric difference.
- Other cases stay unchanged.

The affected helper gates are D[27] `434 ^= 277` and D[181] `434 ^= 429`,
and their reversed counterparts D[1167] and D[1013]. Their conjugates cost
six extra ADDs in total. Target edits add one and the entry/exit gates add two:
**nine more ADDs**. These are literal implementation costs, not shortest-circuit
lower bounds. No commuting, cancelling or reordering search is included.

## Interface and physical boundary

The replacement interface and chronological bridge are credited to woklerx's
PR1194, retained in `research/r439-semantic-d-contract-seed10/PROOF.md`.
Both corrected implementations are source-free at the common zero frame, have
no target-to-helper feedback, and contain no internal COPY/ERASE, child,
allocation, observer or frame-change event. They leave the same values and
frames at the D/A cut. Equality of the complete binary coefficient matrices
therefore gives pointwise equality on arbitrary finite or infinite F2 streams.
The identical continuation receives the identical state. No later operation
is rearranged or interpreted as a frame-free operator.

The proof-only PR589-D virtual splice is checked on all 661 columns in both
directions, and nine scalar hypothesis/conclusion flags are recomputed by this
package. Its root-lattice geometry and chronological realization remain
source-bound predecessor evidence. The first working example freshly
replayed PR1062's unchanged finite checker. This package's exact D, whole-word,
frame-path and positive-envelope checks are separate from full physical
supplier admission. The inherited common-frame/all-size realization is not
proved anew here. Equal binary boundaries do not imply equal intermediate
integer envelopes; the table and RESULT recompute those envelopes literally.

## Reproduce

Python 3.12, standard library only:

```text
python3 -I -B research/r439-copyshare-star-composition/verify.py
python3 -I -O -B research/r439-copyshare-star-composition/test_verify.py
python3 -B scripts/research_package.py --package research/r439-copyshare-star-composition
```

`RESULT.json` is checked against fresh computation. Regeneration is explicit
and writes an external fresh file without replacing one. Source hashes and
Git blobs are checked before replay. The task catalogue and historical selected
record are provenance, so later priority/frontier edits do not change this
fixed-word result. The source-export checker needs no Git or network.

This is a precisely scoped negative result with valid, fully billed positive
controls. It is not a full native multistage, hosted, compiler, precision/tape,
analytic or Lean multiplication proof. No full selected frontier replay is
needed for a new package that changes no selected construction.

## Open next questions

1. Can a different explicitly specified cut or cancellation rule make this
   fixed pair economical? Prove its full dirty boundary and charge every
   preparation/restoration before searching. The three cases here supply no
   unrestricted optimality or all-placement exclusion.
2. Can a genuinely cheaper composed word pass full physical supplier admission?
   Start with native multistage execution and complete hosted emission/invoice
   on that word, followed by supplier bindings and outer assembly. There is no
   cheaper candidate here; those inherited obligations remain open.

## Credit

Victor Li / Wentao Li (PR1805) supplied the baseline invoice and composition
question. Aaron Wang (PR848/1782) supplied the pair census and admission;
woklerx (PR1194) supplied H2-sem and its bridge. Sagar Thakrar (PR1062) supplied
the tested block/star word, on Sricharan Vagvala's PR967 and Gareth Davidson's
PR915/926 basis. Aaron Wang's PR1015 and Ross Richardson's PR923 supply its
phase-B programs. Woklerx's PR1047 supplies a different prepared-middle shear
and pricing method. DreamingOfClouds' PR589, eumemic's PR555/checker and Dylan
Crow's exporter supply the retained lineage. Their savings and lemmas are not
claimed again here.

Prepared for ToikY with substantial OpenAI Codex assistance, including separate
source-cut and code review. No independent human review is claimed. Apache-2.0;
frozen predecessor files and source attribution are preserved.
