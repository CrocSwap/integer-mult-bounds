# Exact relabeling boundary atlas for the selected mutable-leaver cells

All eight PR1005 cells in the selected PR1042 seven-slot scalar word have the
same complete census among the 720 paired source/target label permutations:

| | Label-span boundary passes | Label-span boundary fails | Total |
|---|---:|---:|---:|
| Entering dirt preserved | **6** | 30 | 36 |
| Entering dirt changed | 42 | 642 | 684 |
| Total | 48 | 672 | 720 |

Every one of the 5,760 rescaled cells implements its prescribed clean transfer.
Thus a clean identity check alone admits all 720 choices; a label-span check alone
admits 42 choices that change the target entering-helper response. Conversely,
the dirt condition admits 30 choices that cannot fit the fixed label-span boundary.
The original selected labeling is one of the six joint successes in every cell.
RESULT.json records all successful permutations, the complete census digest,
actual frames and dirt rows, and an explicit witness for each rejection category.

For example, in cell `01+`, permutation `[0,1,3,2,4,5]` fits the label-span boundary
but adds `1/4` of entering helper 600 to target 136. Permutation `[0,1,2,5,4,3]`
preserves entering dirt but fails the label-span boundary. The certificate identifies
the exact helper, target and rational discrepancy in the first case, and the
first failing operation, register, joined frame and cap in the second.

## Precisely what is classified

The base is `ba82555c64e1879e4b7decce28186f208fcb8262`. The source is the named
member `slots/local/FULL-WORD.json.gz` inside the retained PR1042 selected replay
archive. Its canonical JSON SHA-256 is
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`, with 112
source/target pairs and 480 helpers. The similarly named inherited
`gauge44-slots-t16/evidence/local/CANONICAL-WORD.json.gz` is R492 historical
evidence and is not an input to this atlas. The word's retained stage-status text
does not replace the later selected-source review or assert new admission here.

Each trial acts on one cell independently. Simultaneously relabel its six x and
six y names by a permutation, retaining the ordered 21-operation template. Rescale
to its original coefficient matrix. Entry frames are the actual frames immediately
before the selected cell; the twelve exit caps are its actual original exit frames.
Each operation uses the least binary label span containing both operands' current spans.
The label-span filter passes exactly when these spans remain below both operands' exit caps.
At exit, every remaining label-span rank difference to those caps is included: the certificate's
`rank_increment_tally` includes all such closing rank increments, not just the 21 operations.
This is a rank-difference tally, not an executed primitive or provider invoice.
This makes the label spans reconnect to the retained suffix at the same boundary.
It does not optimize paid profiles or assert that any alternative is a complete
replacement supplier. The six source registers are confirmed untouched by the
remaining B suffix.

The dirt criterion is equality of the six target responses to all 192 entering
helper coordinates at the end of the cell. The six source/leaver registers have
zero entering-helper response at entry. Arbitrary other source and target inputs
remain symbolic in the 12-column cell replay. Changing the target basis or the
leaver mutation requires corresponding precondition, scatter and FULL-cleanup
rewrites; none is emitted, treated as free, or admitted here. There is no claim
that these six alternatives preserve the complete existing unmodified word.

## Proof of coverage and the two independent constraints

For nonzero factors `r_i,c_j`, the intended matrix has off-diagonal entries
`C_ij=r_i c_j` and zero diagonal. Let the diagonal change of coordinates be
`D_x=diag(1/c_j)`, `D_y=diag(r_i)`. Conjugating the unit circuit by this diagonal
matrix gives coefficients `c_s/c_t` on x-to-x gates, `r_t/r_s` on y-to-y gates,
and `r_t c_s` on reads. Paired permutations preserve the unit clean matrix
`J-I`; hence every rescaled permutation has the same clean matrix C. The checker
also verifies all of these identities by literal rational replay, without using
this argument as a shortcut.

For a cell write the block transfer as `(x,y) -> (P x, C x + Q y)`.
The three y-to-y gates have six distinct endpoints. Consequently `Q-I` has three
nonzero entries in different rows and columns. Preserving the existing entering
dirt is equivalent to selecting three zero dirt rows as their sources: there can
be no cancellation between distinct destination rows. Exactly three target rows
are zero, while the selected Q already fixes the dirt. There are therefore
`3! * 3! = 36` admissible paired permutations for this dirt condition. The verifier
checks the hypotheses and the full rational response, including possible source
contributions, instead of assuming the zero-row characterization.

For label spans, induction shows that every monotone label-span assignment to this fixed
operation order contains the least-join assignment at every register and step.
Thus exceeding an exit cap in that assignment proves impossibility for the
specified boundary. Conversely, staying within caps gives the literal least-join
assignment and closing span inclusions. This is an exact finite label-span boundary test,
not a statement about relaxed exit caps. Physical/native frame legality may impose
additional Gram-form or residual conditions: those are not checked here. The six
joint successes pass two exact necessary filters in this fixed-boundary model only; no sufficiency for native
admission is claimed.
The loop is all of S6 for each of the eight cells, with no search budget, pruning
or admission shortlist.

## Independent checks and reproduction

From the repository root:

```
python -I -O -B research/leaver-relabel-atlas-seed81/verify.py
python -I -O -B research/leaver-relabel-atlas-seed81/test_package.py
```

Expected first lines:

```
PASS_LEAVER_RELABEL_ATLAS cells=8 trials=5760 controls=32 no_new_kappa
PASS_LEAVER_ATLAS_PACKAGE relocation=1 corruptions=5
```

`verify.py` uses sparse rational rows and binary Gaussian elimination.
`independent.py` imports no verifier code: it transports numeric basis columns,
reconstructs all 192 entering-helper entry columns independently from the source,
and enumerates actual binary vectors to check frame containment. All 5,760 cell
maps and classification pairs agree. Source discovery uniquely matches each
21-gate sequence to the pinned cell at B indices 527, 548, 569, 590, 611, 632,
653 and 674. It uses the published target bindings as well as every coefficient.

There are eight dropped-read controls, eight empty-cap controls and sixteen
cross-constraint witnesses. Packaging tests run from a minimal relocated tree
under Python optimization, then reject a missing mandatory source pin, duplicate
JSON keys, nonfinite JSON, corrupted source bytes and a Boolean receipt count.
The receipt is compared through typed canonical JSON, including all metadata.
`verify.py --write` explicitly regenerates the receipt; ordinary replay is read-only.

## Credit, overlap and limits

The 21-gate circuits, their scaling rule and dirt-aware selected choices belong
to LeaverSAT/LeaverSAT2 and icekylinx's PR1004/1005 lineage; the seven-slot word is
PR1018 and is reused by selected PR1042. PR1049 (thakrarsagar) already verifies the
eight selected cells, full local endpoints, entering responses and the leaver
premise. PR1112 independently checks the selected finite invoice. This work does
neither audit again: its new object is the complete relabeling boundary atlas and
the separation of two exact boundary filters. The concurrent round23
monotone clean-cell minimum concerns a different class and objective.

No native compilation, Clifford phase audit, provider invoice, outer assembly,
precision admission, all-size closure or new kappa is performed. Existing
conditional hypotheses remain inherited. No relabelings are composed, and no
new optimum or saving is claimed. Contributor @woklerx, with substantial OpenAI
Codex assistance; the second implementation is algorithmically independent,
not an independent human review. Apache-2.0 applies; see NOTICE.md.
