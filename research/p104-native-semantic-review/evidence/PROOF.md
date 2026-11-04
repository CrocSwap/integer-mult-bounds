# Exact current native application delta

This is an author-side independent application review of the unchanged PR6702
native word used by PR6716 at `17c08db090004c1fb54220a6d8463a5095789fa9`.
It follows the method and conditional scope of the selected PR6030 review.
It is neither an external admission decision nor a new general lifting theorem.

## Source and comparison boundary

The admitted reference is the exact PR6030 word retained in canonical commit
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, not an arbitrary historical word
with the same inventory size. Its compressed SHA256 is
`7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`.
The current compressed word has SHA256
`e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d`.

`SOURCES.json` identifies every retained input and interpreter. The current
word has a direct reachable 17c Git pin. Its actual compiler comes from that
commit's retained `source6702/source.tar`, through the authenticated
`RETAINED.json` and `engines.tar` members. `SOURCE-CUSTODY.json` binds these
members to the exact local compiler files. Earlier nested `source_head` labels
are lineage labels; this review does not claim that edited archive members
belong to those earlier Git trees. The optional custody checker reads scoped
Git objects and named members without executing source archive code.

Each word contributes all distinct typed MOVE, helper, main-input and
main-output tasks, with the literal nine-axis frame data and central port.
Task type, frame numbers and inventory counts alone are not semantic keys.
The comparison uses complete operator signatures as follows.

## Exact signed operator signature

Let U and V be unitary Clifford operators on the nine-axis complex space.
Suppose their conjugations agree on all nine X and nine Z generators,
including the Pauli phases in Z/4Z. Then V inverse times U commutes with
all these generators. They generate the full matrix algebra, so that
operator is a scalar multiple of the identity. Equality of the complete
nonzero columns U|0> and V|0> fixes the scalar to one. Thus the complete
eighteen signed images and exact zero column determine the operator,
including its absolute phase.

The zero column consists of integer real and imaginary arrays divided by
2 to a nonnegative integer power. Removing their largest common power of
two, capped by that denominator, makes its representation unique. Every
column's exact squared norm is checked to be one. Comparison and deduplication
use the complete tuples, not their SHA256 labels. A global multiplication by
i preserves all signed Pauli images but changes the zero column and is
explicitly rejected.

`compare_maps.py` applies the retained independent literal and dense
interpreters to both inventories. It also checks the intrinsic binary B-block
rank against the declared paid Gaussian rank. A selected witness is accepted
only at the same rank. The outcome is 3,145 matched typed current tasks and
39 unmatched typed tasks, the latter all distinct: 34 MOVE tasks and five
helper tasks. All 208 intrinsic main adapters match. There are 2,367 matched
distinct current operators, 2,406 total distinct current operators, and
2,393 distinct selected operators. The difference between 2,939 and 2,922
internal frame pairs is not the number of new operators.

## Delivered current recipes, not just expected operators

Expected-operator equality identifies an old implementation witness; it does
not alone validate the current compiler's output. Therefore
`check_signatures.py` invokes the actual authenticated current compiler for
every current task. It checks the emitted recipe's eighteen signed Pauli
images and its complete exact zero column through separate retained
interpreters, and compares the full result to the independently built literal
task signature. It also checks the actual emitted rank. This covers all
2,939 internal frame pairs and all 208 main adapters, including tasks that
have selected witnesses. It does not assume that the current prefix-state
cache is correct or infer its correctness from an AST comparison.

`check_dense.py` gives the 39 unmatched tasks an additional direct check of
every one of their 512 complex matrix columns. Every recipe is emitted by
the actual current compiler, rather than emitted by the old compiler on a
new expected task. Column norms and the Gaussian support rank are checked.
A phase-only corruption and an incorrect order of helper inverse factors
are rejected. The old/current compiler-function comparison is recorded as
diagnostic provenance only; it is not the proof of current recipe correctness.

For each helper task, a valid recipe expresses its complete operator as
U = L G_r R, with ordinary invertible signed monomial factors L and R.
Their inverses applied before and after the complete native invocation give
L inverse times U times R inverse = G_r on the helper's arbitrary input.
All current recipes are checked as above. The five unmatched helper jobs
additionally check this complete normalized operator on all 512 columns,
including both normalizer phases and their placement. No helper input is
assumed zero; no correlated observation is substituted for an independent job.

## Scalar word and every positive tensor width

`check_scalar.py` uses the unchanged independent Matarener interpreter used
in the selected lineage, on only the complete current word. It checks all
18,577 events, strict span nesting at MOVE, the common chart of scalar
operations, actual chronological ownership, COPY conditions, and all 800
exit rows over the rationals. Those rows include all 771 independent public
inputs and 29 owned labels. There are 563 independent helper outputs, 47
owned lifetimes and a peak of 14 owned fields. An actual compensation ADD
sign fault is rejected at endpoint row 173. No historical word or full
historical native suite is replayed.

Here is the existing factorwise common-chart argument, stated to delimit the
finite check. Fix arbitrary f >= 1 and let T_c[f] be the f-fold tensor power
of the literal one-column frame operator T_c. For independent raw public
input x_j in initial frame a_j, define z_j = T_a_j[f] inverse applied to x_j.
These z_j are independent arbitrary arrays; they need not be pure tensors.
The invariant at each active field r is

    payload_r = T_current_frame_r[f] times sum_j s_rj z_j,

where s_rj is the checked rational scalar row. Exact individual MOVE and
adapter equalities lift to tensor powers in the same multiplication order.
A common-chart ADD or SCALE acts on the exterior scalar row. INIT creates
zero, COPY follows the checked owned contract, and CLEAR follows the retained
erasure contract. The checked exit rows therefore give the prescribed native
endpoint for every arbitrary original input under this factorwise ABI.
Appending an identity spectator factor preserves the argument for payloads
correlated with spectators.

A one-column phase i^a becomes i^(af) under tensoring. An exterior scalar
coefficient stays that scalar. No identity between width-one scalar sums of
operators is tensorized. In particular, this review does not use a finite
width accidental linear dependence as an all-width proof. The same
factorwise frame-induction method is already present in the retained native
checker and PR6030 review; this application and exact source census are the
additional evidence here.

## Remaining scope

The global five framework assumptions, including the retained
`native_all_columns` implementation contract, remain explicit. This review
does not establish all-size physical production, layout, stock, callbacks,
precision, or the actual fixed-tape allocator. It changes no invoice,
claimed kappa, selected result, caller word or native word. It supplies a
reproducible source-bound delta for mathematical review, using AI-assisted
author-side independent execution. Scientific admission remains a maintainer
decision.

## Attribution

DreamingOfClouds' PR6030 and its maintainer repair supply the exact admitted
reference. Matarener supplies the retained independent scalar and inventory
machinery; Clear1nsight supplies the exact dense Gaussian-dyadic interpreter.
Charles Bethin and the retained lineage supply the Clifford compiler and
literal semantics. Ali Romman supplies the retained current prefix evaluator
and PR6702 lineage. The existing common-chart argument and predecessor
conditional scope are credited explicitly rather than claimed as new.

This source-bound comparison, current emitted-signature driver, narrow dense
and scalar orchestration, and documentation were prepared for thu-nmrc with
substantial OpenAI Codex assistance, Apache-2.0.
