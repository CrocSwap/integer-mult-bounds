# One selected BIT route with explicit q-adic carries

This package lowers one nontrivial selected BIT port route into exact low/high
row-field updates. The written identity holds at every atom width. Its executable
receipt contains 77 elementary column factors, 4,928 row-field steps per route,
and 24 comparisons with a separate dense modular oracle. Ancestors, the physical
role slot, unused descendant stock, and head/data spectators remain unchanged.

This is a row-index implementation of one missing interface, not the full GL64
compiler, a physical routing implementation, a stock-bound improvement, or a new
kappa. The selected frontier and all predecessor files remain unchanged.

## Scope and predecessors

The scientific base is main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4. The selected record binds PR1094's assembly, which cites the exact
PR589 BIT receipt by Git blob. That receipt binds the tuned P111 word. Its live
port 8 is original E8 port 8 with root `[0,1,1,0,1,0,0,1]`. The ambient dimension
is 64. The complex supplier's dimension 73 is not substituted into this argument.

This takes the released field-split handoff from
[PR2120](https://github.com/CrocSwap/integer-mult-bounds/pull/2120), head
`378593574261e0b0915e7e8a83147aa640274fc8`, and
[Discussion 2114](https://github.com/CrocSwap/integer-mult-bounds/discussions/2114).
Adam Gall's [PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084),
head `8001a23b003bec5dff5e61edec907b652c475932`, supplies the conditional BIT
packet/restoration implication. [PR2097](https://github.com/CrocSwap/integer-mult-bounds/pull/2097),
head `1d3ee0926656d5260c6cb1c0b81964ffe9fe1377`, proves fresh-fiber counting
under a field-dependency contract and leaves its selected lowering open.
Those results are credited, not claimed as new here. None of their verifiers
is imported or executed, and none of their packages is vendored.

The task's scope changes from computing a reserve coefficient to this concrete
implementation obligation. The existing notes already state affine chart routing
and fresh fields. The new artifact emits the low/high carry program for an exact
selected rational route, proves its integer formula, and checks its factor order,
field isolation and inverse. It does not claim that affine routing itself is new.
See [TASK.json](TASK.json) for the selection override and limits of live overlap.
No Discussion claim was posted because the local engineering workflow prohibits
human-directed posts. The public artifact is the contribution PR.

## Source-bound rational route

The pinned `code/nine/geometry.py` constructs an isometry `g` taking the first
root to the port root up to sign, using its fixed breadth-first reflection rule.
With `q_port` the root, it sets

```
P = q_port*q_port^t / 4
A = g[:,1:]
rho = [[P, A], [A^t, 0_7]]
```

The retained PR545 adapter builds this geometry over all 120 original roots,
then selects and reindexes the 111 live ports. This checker independently
reconstructs that rule with rational arithmetic and emits only port 8. It checks
`rho^t=rho`, `rho^2=I_15`, and the exact elementary product. The route acts on
axes `0..7` plus one exterior seven-block. The receipt checks both stage 1,
axes `8..14`, and stage 8, axes `57..63`. Other columns remain fixed.

Gaussian row elimination gives `E_k ... E_1 rho = I`. Thus right multiplication
by `rho` executes the column factors `E_1^-1, ..., E_k^-1` in that order.
A row operation adding `c` times row j to row i becomes a right-action column
operation adding `-c` times column i to column j. All 77 factors are checked
against the rational matrix; deleting any single factor changes the product.
A separate noncommuting fixture tests column orientation and order, since the
selected route's symmetry could otherwise hide a transpose error.

There are 63 column additions, seven swaps and seven scalings. Each operates
on 64 matrix rows. The 4,928 count is row-field instructions, not scalar writes,
recursive children, measured runtime, or a paid physical invoice. The only
coefficient numerators and denominators have prime factor 2. Every odd radix
therefore makes the factors invertible. For the full-cover interpretation,
retain the source's stronger eligible-prime conditions.

## Exact all-width carry lemma

Let q be an integer at least two, w at least one, and `Q=q^(w-1)`. Write two
current matrix entries uniquely as

```
x = x0 + q*X,  y = y0 + q*Y,
0 <= x0,y0 < q,  0 <= X,Y < Q.
```

For a rational coefficient `a/d` with `d>0` coprime to q, the elementary
addition `y <- y + (a/d)*x` modulo `q^w` has the following exact lowering:

```
t = ((d*y0 + a*x0) * inverse(d,q)) mod q
c = (d*y0 + a*x0 - d*t) / q
Y_new = ((d*Y + a*X + c) * inverse(d,Q)) mod Q
(y0_new, Y_new) = (t, Y_new)
```

The numerator defining c is divisible by q by the definition of t. In integers,

```
d*y + a*x = d*t + q*(d*Y + a*X + c).
```

Reducing modulo `q^w` and multiplying by the inverse of d proves the result.
This permits negative carries. For example, adding half of 1 to 0 at q=5,
w=2 gives `(t,c,Y_new)=(3,-1,2)`, hence entry 13 modulo 25. Omitting the carry
would give 3 and is wrong.

For scaling `y <- (a/d)*y`, replace the two numerators by `a*y0` and `a*Y`.
Require a coprime to q as well to make scaling a permutation. Swapping entries
swaps both their low and high fields. At w=1 the high field has one value, 0;
the high congruence modulo one is vacuous. These derivations require no bound
on w and no floating-point approximation.

Each factor is an invertible map on every matrix over `Z/q^w Z`. Composing the
emitted factors therefore gives exactly `G <- G*rho` for all such matrices,
and in particular permutes the invertible ones. Low reduction depends only on
the current low matrix. For each fixed low matrix, the high update is affine
and bijective onto the complete high fiber over the new low matrix. Thus the
route preserves all `q^(4096*(w-1))` high completions; it does not silently drop
the high fibers charged by the stock proofs.

### Why low routing and row restoration do not suffice

A concrete carry-omission mutant applies the rational route separately modulo
5 to the low matrix and to the high matrix, then rejoins them. At w=2 it has
the correct low routing, fixes all other fields, and restores the entire row
after two applications because `rho^2=I` in each separate factor. Nevertheless
it is not right multiplication modulo 25. For the receipt's stage-8 invertible
fixture, matrix entry `[0,6]` is 19 instead of 14. Both reduce to 4 modulo 5.
The active input row is retained in the receipt.

This is a counterexample to those checks being sufficient, not a defect found
in the selected compiler. No selected all-size q-adic compiler was executed.
It explains the need for a full-width oracle in this contribution.

## Parent/child field boundary

Consider a complete row represented as

```
(ancestor_fields, role_slot, current_low, current_high, unused_child_stock,
 head_data, other_spectators).
```

The emitted operation reads and writes only the current low/high matrices.
Its program and coefficients are fixed by the selected port and stage, not by
unused child stock or head/data values. Consequently it is the identity on
every other factor of this product, for arbitrary initial values of those
factors. Its inverse restores the entire original row, not merely its low
residue. Changing another factor cannot change the current route's result.

If unused stock is a complete range divisible by the next role-packet divisor,
Euclidean quotient/remainder splitting still supplies all next-role values
with equal multiplicity after this route. At a child boundary, the exposed
parent fields may become ancestors without changing the unused range. This
is the local field-preservation implication needed by the handoff. Complete
invocation domains, ancestor-only child weights, every other owner route and
restoration of a completed child still need their own certificates. This
single routing identity does not establish those assumptions by itself.

The selected finite program describes orthogonal cover classes. Transferring
its complete physical recipe to the local-ring GL64 full cover remains the
explicit inherited realization assumption in PR2084/2097/2120. The present
matrix identity works over GL64, but does not prove that transfer, common-label
or mutable-source realization, or fixed-tape physical hosting.

## Reproduction and failure controls

Standard-library Python 3.12, from the repository root:

```
python3.12 -I -B research/selected-bit-qadic-route/verify.py
python3.12 -I -O -B research/selected-bit-qadic-route/test_route.py
python3.12 scripts/research_package.py --package research/selected-bit-qadic-route
```

Expected output includes:

```
PASS_SELECTED_BIT_QADIC_ROUTE factors=77 cases=24 no_new_kappa
Ran 11 tests
OK
```

Every live input is authenticated before semantic use. The registered metadata
check authenticates the historical selected record at the pinned base; the
verifier links its frozen PR1094 assembly citation, tuned receipt and word.
The moving selected pointer is provenance, not a live replay input. A later
frontier change does not silently change this scientific baseline.
Predecessor Python is read as pinned source, never executed. The regenerated
receipt must equal the committed [RESULT.json](RESULT.json); missing or corrupt
receipts fail. `--write-result PATH` is explicit and refuses to overwrite files.

The route cases use dense invertible `L*U` matrices at q=5, 7 and `2^89-1`,
widths 1, 2, 3 and 8, in both exterior-block embeddings. A direct dense modular
right product is the oracle; it does not use the carry interpreter or elementary
program. Exact inverse replay restores all fields. These finite cases do not
prove the all-width lemma, which is the integer identity above. No eligible
selected-prime inference follows merely from testing a large prime.

Eleven test groups include the carry-omission mutant, 1,493 exhaustive
elementary-addition cases, scaling bijections, signed carry fixtures,
noncommuting order, inactive columns,
arbitrary spectators, wrong selected citations, all eight external input
corruptions, and optimized public-CLI missing/corrupt-receipt and no-overwrite
controls. Acceptance uses explicit exceptions, not removable assertions.

## Implementation and verification limits

The executable is a bounded research checker. Its public carry evaluator caps
w at 16, q below `2^127`, and rational coefficient components at 16 bits.
The proof has no such width bound. Matrices are at most 64 by 64,
local rational matrices are 15 by 15, programs have at
most 240 factors, and the source BFS has at most 120 rounds over 120 roots.
Inputs and decompressed words are capped at 8 MiB. Each subprocess test has a
15-second timeout. All loops have finite collection or numeric bounds; there
is no recursion or background work.

Power-of-Ten deviations concern Python managed allocation and unittest/import
dispatch. Runtime arithmetic and collections allocate dynamically; dimensions,
widths, file caps and bounded fixture counts constrain their live size. The
fixed local imports are the only added module targets, and tests exercise both
normal and optimized entry points. Syntax compilation and warnings-as-errors
are the available diagnostics. A native fixed-capacity implementation and
physical interpreter remain follow-ups if this is used outside a research
checker. No repository-wide lint or compiler configuration is changed.

No full selected cold replay, physical routing benchmark, native compiler,
formal-kernel proof, independent human review, or new stock coefficient is
claimed. Scalar gates, owner/slot permutations, weighted children, ordinary
leaf borrowing, all-size physical lowering, precision/tapes, recovery and outer
analytic obligations remain outside this package.

## Open next questions

1. Can every selected helper/bank/hosted route and child-weight descriptor
   satisfy the same field-dependency contract? Begin with one residual-isometry
   route and emit its ancestor-only reads. This matters because a single data
   route cannot establish the full fresh-field premise. The all-size compiler
   and complete invocation domains remain blockers.
2. Can these field operations be physically implemented with the retained
   ordered-affine and completed ordinary-leaf costs? Begin with one
   carry-controlled shift or scaling, including preserved spectators and its actual
   ordinary-call bill. Exact row-index arithmetic does not discharge fixed-tape,
   hosting, internal borrowing or precision obligations.

## Credit

The rational port geometry and reflection construction are retained from
Zhihao Chen's PR386 and its credited PR370 lineage. DreamingOfClouds supplied
PR545's live-port adapter and the selected PR589 tuned BIT pipeline on eumemic's
base. Rohan Arun supplied the selected PR1094 assembly on Jeremy Kothe's PR1087
predecessor and the retained completed-row contracts. Adam Gall's PR2084 and
PR2097, Nick Petalas's PR2120, Josie Elliston's PR1956/1965 and ToikY's PR1990
identify the stock and field obligations used here. Their constructions,
conditional envelopes and numerical receipts are not claimed as new.

Nick Petalas retains authorship and responsibility for this scoped lowering
and checker. Apache-2.0, following the repository license.
