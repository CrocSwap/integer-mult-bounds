# Exact minimum grids for the current banked native graph

The final forward scalar DAG of
[PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674)
needs odd entrance factor **225** and **12 binary coefficient bits**
for every literal product and addition. The source's sufficient values
are 2025 and 18. This is an exact finite precision result for the pinned
graph; it does not replace the full common-root proof or change kappa.

Stored snapshots alone need factor 45 and nine bits. That coarser grid
fails during products, even though every completed row fits. Read
[PROOF.md](PROOF.md), [RESULT.json](RESULT.json) and [verify.py](verify.py)
for the exact scope, all prime-factor witnesses and literal failures.

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -I -W error -B research/banked-native-minimum-grid/verify.py
python3.12 -I -W error -B -O research/banked-native-minimum-grid/verify.py
python3.12 -B scripts/research_package.py --package research/banked-native-minimum-grid
python3.12 -B scripts/check_research_commit.py --package research/banked-native-minimum-grid --check-source-history --check-modes
```

Expected markers are PASS_BANKED_NATIVE_MINIMUM_GRID,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The new evaluator checks 8533666 exact products at each of the two
grids, all 7643 snapshots and all 1501 public endpoint rows. A separate
Fraction interpreter checks six sharpness witnesses on four basis
inputs. Eight negative controls reject missing prime factors or a
snapshot grid used for product work. There is no external run-time input.
The exact retained source bytes are bound in [PREDECESSOR.json](PREDECESSOR.json).
The graph constructor is reused from the source; the coefficient audit
is new. It is not an independent graph compiler or human review.

## Task and scope

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`,
priority revision 8, with selected PR #7000 unchanged. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19703488) takes the arithmetic-grid portion of the
candidate's review request. Card `supplier-boundary-audit` is narrowed
to one quantified finite precision obligation. The exact source graph,
its paid/target counts and the original PR are unchanged.

The broad overlap search found the historical precision method in
PR #866 and the current candidate's review request. The old method and
source construction are credited; neither is claimed as new. Sparse
local notes and unpublished work remain coverage limits.

No predecessor scientific suite, selected cold replay, Lean or Docker
was run. Native Clifford entries, recursive debt, the signed caller,
magnitude and physical costs remain outside this arithmetic replay.
All selected assumptions remain. Independent human and formal-kernel
review are unclaimed.

## Open next questions

Can the smaller native scalar factor and guard be substituted into the
source's complete common-root proof without changing its caller and
boundary contracts? First keep the caller's separate scale, quantify
the Clifford and unfinished-depth contributions, and check each final
unscaling. The scalar minimum alone does not prove that substitution.
A different product lowering could also change the temporary grid.

## Credit and exact sources

Prepared by Ali Romman with substantial OpenAI Codex assistance.
The banked circuit and sufficient common-root bound are from
[PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674),
[exact source proof](https://github.com/aliromman/integer-mult-bounds/blob/26b6c469aa6c4aa04322ce25a22150f90e5fb14e/research/p104-banked-transfer-pivots/PROOF.md)
and [source arithmetic evaluator](https://github.com/aliromman/integer-mult-bounds/blob/26b6c469aa6c4aa04322ce25a22150f90e5fb14e/research/p104-banked-transfer-pivots/native.py).
The scientific commit is `26b6c469aa6c4aa04322ce25a22150f90e5fb14e`;
head `28b2af322a1fab01b3734365988930920f9dda48` adds the shared CI repair.
SYLforge supplied [PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669);
its [original credit](predecessor/source/7669-CREDITS.md) and the
[source notices](predecessor/NOTICE) are retained unchanged.
Gareth Davidson / bitplane's
[PR #866](https://github.com/CrocSwap/integer-mult-bounds/pull/866),
[exact precision proof](https://github.com/bitplane/integer-mult-bounds/blob/5ae580bf68516f1cbe3b2dd3cb646be55170288f/research/dyadic-fractional-grid/README.md),
supplied the prefix-coefficient grid criterion and basis-input witnesses.
The new result binds that method to this graph and distinguishes product
precision from snapshot representability. New work is Apache-2.0.
