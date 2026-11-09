# Current two-output swaps as executable coded-tape tables

Prepared for **@CubeJerry**, with substantial OpenAI assistance. **No new κ.**

This package closes the current **SWAP/SIGNED_SWAP source class** on the same
two-work-port physical ABI as the preceding ADD/SCALE tables. The actual
ordered semantics are `(x,y) -> (y,x)` and `(x,y) -> (y,-x)`. The generated
130-row and 171-row tables execute through the unchanged published lifecycle
`execute_table` and `Controller.primitive`; they contain no runtime numerical
callback, decoded width or field-length parameter.

For arbitrary nonempty complete complex fields with matching ordered shapes
and grids, SWAP always succeeds. SIGNED_SWAP succeeds exactly when the old
first operand has no most-negative component in its original signed width.
The second operand may be most-negative. This is exactly final-output signed
admission, with no intermediate-word headroom requirement.

The routine stages x or -x and leaves y protected. After checking the **entire
pair**, it installs `(old y, staged signed x)`, reading each old y symbol before
overwriting it. There are no writes to either public field before full-field
admission, including when the last component fails. On success the original
wrapper returns all heads and physically erases work. An immediate rejection
can leave heads advanced and work occupied; physical rollback is not claimed.

## Exact source closure

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The selected
certificate remains conditional at **κ = 0.003125804**, with all five assumptions.

| Source region | Original instructions | Emitted current services |
| --- | ---: | ---: |
| Right-boundary SWAP | 27 | 2,808 |
| Left-boundary SWAP | 30 | 3,120 |
| Outer SIGNED_SWAP | 48 | 4,992 |
| Total | 105 | **10,920** |

The original current source mapper expands each instruction across 104
columns. The binder retains actual ordered owners through caller/product/
unit-fragment wrappers and checks exact source instructions. It separates
active source tokens from issuing PAID provenance in chronological products.

Combined with the frozen [current ADD/SCALE package](https://github.com/CubeJerry/integer-mult-bounds/tree/13193a22b1070a74a8580c5d3ea27470443f815a/research/current-scalar-flat-tables),
this supplies tables for all **377,762 original ADD/SCALE/SWAP/SIGNED_SWAP
services** in the 642,410-event selected caller. COPY keeps its original
lifecycle implementation. Native/phase, row/recursive, geometry, precision,
global ownership and analytic obligations retain their separate scope.

## Complete costs

The universal proof in [PROOF.md](PROOF.md) includes both source passes,
protected staging, guided rewinds, both output writes, head restoration and
literal erasure. With public length V, initially occupied work D and fixed
work/context inventory Q, time is **O(V+D+Q)**. The two used current work
bodies occupy **2V+3+O(1)** raw cells; historical visited backing remains their
coordinatewise maximum and is never treated as deleted.

Matching coordinate meanings and widths, a common grid, distinct physical
ports, all supplied heads at current origins, and contiguous initially dirty
work prefixes remain explicit entry premises. Corresponding component widths
may vary along a field. No complete old numerical allowance, complete supplier
invoice, full multiplication improvement or unconditional theorem is claimed.

## Executed finite evidence

The direct permutation/sign oracle checks **2,728** physical cases: every
signed x,y pair at widths 1–5 for both operations, encoded as a complete
complex record with equal component pairs. It accepts 2,666 and rejects 62.
Another 96 wider/asymmetric/mixed-width fields reach width 129, with 70 accepts.
Thirty-two failure and boundary controls include most-negative first/last
components, minimum second operands, signed equal values on distinct tapes,
shape/alias/source failures, four transition mutants, physical ordered inverse,
dirty extra work, protected contexts, and shrinking retained backing.

Two real unchanged-controller fixtures use all **13,444 public fields**:

- The entire 5,720-service right boundary, joining the retained scalar tables
  and new swap table, executes 11,015,757 physical cell actions and 1,493,648
  table steps. A separate interpretation of the original boundary program
  checks every public endpoint and spectator.
- The actual first 104-service signed block executes 216,813 physical actions
  and 28,912 table steps, including most-negative second operands.

These are actual contiguous source blocks entered at explicit assumed cuts;
they do not execute preceding native entries or the complete recursive caller.
The finite tests challenge the implementation, while the written proof gives
the universal quantifiers. Details and exact receipts are in
[VERIFICATION.md](VERIFICATION.md) and [RESULT.json](RESULT.json).

## Reproduce

From the repository root with Python 3.12 and its standard library:

```sh
python3 -B scripts/research_package.py --package research/current-swap-flat-tables
```

`VERIFY.json` registers eight bounded commands: normal and optimized execution
of arithmetic, complete source binding, actual controller blocks and controls.
Each checks exact immutable input/dependency bytes and committed receipts.

## Predecessors and attribution

[#3098](https://github.com/CrocSwap/integer-mult-bounds/pull/3098), Jose Manuel
(`jmbarrancoml`), supplies the earlier aligned scalar-recipe execution.
[#969](https://github.com/CrocSwap/integer-mult-bounds/pull/969), prepared for
ToikY, defers historical scalar names and pays boundary copies, while explicitly
leaving physical arrays/current production admission open.
[#4516](https://github.com/CrocSwap/integer-mult-bounds/pull/4516) checks the
older caller's exact Laurent signs. Classical permutation and negation are
not new claims. Ali Romman's productive caller and #5356 continuation source,
DreamingOfClouds' selected #6030 word, the current lifecycle/compiler source,
and the frozen current scalar provider retain their credit and exact pins.

## Open next questions

The next obligations are the still-uncovered native/recursive provider tokens
and the actual all-success geometry, precision, ownership, full-cost and
analytic join. [TASK.json](TASK.json) records these questions and the exact
canonical task card. No independent human or proof-kernel acceptance is claimed.
