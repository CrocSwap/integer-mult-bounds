# Numerical word lifetimes in the selected BIT coefficient evaluator

The unchanged PR2697 `Callback.weight` needs at most **20,490 additional
residue Words and ten additional index Words**, above every numerical resident
on entry. The bound is independent of chronological depth. An initialized
current Page, including its retained form and incoming callback, needs at most
**36,879 residue Words and 23 index Words** above unrelated borrowed residents.
Literal 64-dimensional fixtures attain each of these four bounds, separately.

This is a source-level occupied-content lemma. It answers the caller-resident
handoff from [PR2759](https://github.com/CrocSwap/integer-mult-bounds/pull/2759)
for coefficient evaluation. Page construction, other node/route residents,
serialized continuation/program/field tapes, erased backing slots, physical
placement and complete reserve admission remain separate.

## Contract and exact sources

The scientific source is Jose Manuel/jmbarrancoml's
[PR2697 at a53fdf4](https://github.com/CrocSwap/integer-mult-bounds/tree/a53fdf4bcbe33c6732f0bec1badc8c023380f9d1/research/selected-bit-node).
[SNAPSHOT.json](SNAPSHOT.json) pins the original paths, Git blobs and SHA256
hashes of six unchanged runtime modules and their complete notice. All exports
are authenticated before any is executed. The checker compiles authenticated
bytes directly and bypasses bytecode caches.

Fix the two arenas, an initialized `Ring`, a valid `Callback`, and a successful
call satisfying the pinned source contracts. The matrix dimension is `m=64`;
proper good ranks obey `1 <= r <= 42`. Residues are canonical modulo the
admitted prime power, arithmetic words have their required high-bit margin,
index words fit all addresses, and the supplied program/fields satisfy the
chronological and frozen-prefix contracts. Execution is sequential, with enough
arena capacity and no observer that allocates numerical Words. Finite source
tables remain the caller's supplied compilation data. Borrowed Words and
serialized input tapes enter with their heads at cell1.

Let `L_R,L_I` count **all** live arena slots immediately before `Callback.weight`,
including its constants, request coordinate, any current Page form, retained
numerators, and unrelated caller data. Then its simultaneous live slots obey

```text
residue slots <= L_R + 5m² + 10 = L_R + 20490
index slots   <= L_I + 10.
```

Returned Words count toward these bounds. On successful return, the original
live slots and their values/heads are restored, with one additional owned
residue result. Both continuation stacks are empty. The numerical bound does
not say those stacks have constant space during evaluation.

For `Page.evaluate`, let `B_R,B_I` instead count unrelated caller slots before
the call, excluding the initialized Ring, incoming Callback and current Page.
Include the borrowed request coordinate in `B_I`. Assume the Page's weight
callable is that incoming Callback's `weight`, as in `selected_page`. Then

```text
residue slots <= B_R + 9m² + 15 = B_R + 36879
index slots   <= B_I + 23.
```

The same restored-input/one-owned-result conclusion holds. These bounds cover
the head/tail/cross/shear adapter and good/pair/unit child branches, including
the final negative inverse, by the source lifetime argument below. The literal
Page fixtures exercise paired children, their reversed columns and negative
inverses; they do not exhaust every adapter branch or the selected catalogue.

Each live numerical Word occupies `b+1` non-LEFT symbols, its `b` bits and RIGHT
delimiter. Each arena also owns one permanent template. Thus the weight bound
implies numerical occupied content at most

```text
(L_R + 20491)(b_R + 1) + (L_I + 11)(b_I + 1).
```

For the initialized Page, substitute `B_R+36880` and `B_I+24` for the two word
coefficients. LEFT markers and retained erased-slot capacity are excluded.
The formulas do not bound Python heap objects. Freed slots can still have
Python references and backing arrays; they contain no live numerical payload.

## Proof by source lifetimes

### Primitive and matrix interiors

The primitive arithmetic bounds are the credited result of
[PR2759 at 2fd8fbe](https://github.com/CrocSwap/integer-mult-bounds/blob/2fd8fbe0d2f57c4a8ebb7b7c9ae45df1fcf69be9/research/selected-word-scratch/README.md).
For completeness, division retains scan/quotient/remainder and one replacement,
so adds at most four Words. Modular add/subtract add at most two, negate three,
multiply four, and `Ring.literal` four. Inversion retains four Euclidean Words,
then quotient/remainder, and calls multiply while all six remain live. This
gives ten. Its iteration frees quotient, product and two old Euclidean Words
before repeating, so iteration count does not accumulate live Words.

`Matrices.inverse` adds exactly `2d²` stored elimination Words to its borrowed
input: `d²` identity Words and `d²` copied input Words. The identity list aliases
the right halves of the elimination rows. Pivot inversion adds at most ten;
normalization and elimination add at most six. Its bound above all entry
residents is therefore `2d²+10`. Diagonal `2I` modulo five attains this bound
for each tested `d=1,2,3`, and returns `3I`.

`Callback.prepare` includes the high matrix it reads and later frees. These
are conservative simultaneous bounds, including that high matrix:

| Phase | Residue Words above the surrounding entry residents |
| --- | ---: |
| Raw header, its palette and q literal | at most `3m²+5` |
| Preparation constants, palette and literal/inverse scratch | at most `max(4m²,3m²+11)` |
| Header matrix product | at most `4m²+4` |
| Projector inverse | at most `4m²+10` |
| Final projector product | at most `4m²+4` |

For constants, the palette has at most `m²` distinct entries. While computing
one entry, at most `m²-1` previous palette Words survive beside numerator,
denominator and ten inverse scratch Words. While copying the output, the full
palette can coexist with its `m²` output copies. For the projector inverse,
high and header are the two borrowed `m²` matrices. Since `m² >= 1`, every
listed phase fits `4m²+10`. On return only the `m²` projector survives.

`good_pivots` retains that projector, its `m²` copy and at most `r` pivot Words.
Before the kth pivot is appended, inversion sees only the previous k pivots,
with `k <= r-1`. This gives `2m²+r+9`. Elimination retains inverse/coefficient
and primitive scratch, at most `2m²+r+6`.

`fallback` retains the `m²` projector and its `4m²` residual matrix. Building
one residual-entry tuple temporarily adds at most four Words; elimination
adds at most six. Pivot inversion adds ten, giving `5m²+10`. The final diagonal
aliases matrix entries; collecting it creates no additional Word per entry.

### The iterative weight evaluator

The pending/value stacks store **serialized copies**, then free the numerical
Words used to create those records. At an iteration boundary, no earlier
ancestor matrix or reduction scalar remains live in an arena. A `VALUE` record
pops two index Words. A nonunit-reset request prepares one projector and
processes one good or fallback reduction, then frees that projector and its
returned pivot/diagonal vectors after serializing their needed coefficients.
Only one such preparation is live at a time.

CONSTANT adds one residue result; MULTIPLY has two popped operands plus four
multiply scratch Words; PAIR has three popped operands plus ten inverse scratch
Words, or its inverse/product and multiply scratch. All fit thirteen additional
residues, below `5m²+10`. UNIT allocates no projector. The largest preparation
bound is therefore the claimed residue bound, independently of depth.

The index inventory is also independent of depth. A VALUE expansion retains
level, coordinate, parent, child, f and slot, six Words. The good branch's
division adds four, attaining ten. A Program/Fields seek adds three while fewer
addresses are retained. The halved unit's step reaches nine. In a pair branch,
the retained six, column, first address and position total nine; the intermediate
`times_small` result/replacement also fits nine. No earlier request's Word
operands survive after its next pending records have been serialized.

### Current Page residents and nested evaluation

`good_form` returns `m²` cross Words, r pivots, and
`2rm-r(r+1)` row/column scalars, including zero scalars. Its stored form has
exactly `m²+2mr-r²` Words. For `m=64,r<=42`, this is at most 7708.
`fallback_form` stores one scalar for every off-diagonal position of its
`2m`-dimensional elimination, and `2m` diagonal Words. Swaps store labels only.
Its form has exactly `4m²=16384` Words. Constructing either form is outside
the Page evaluation theorem.

The modulus, `ring.one`, incoming root unit and high cap add four resident
residue Words. Evaluating a second bank can retain the first bank's numerator,
one more Word. Applying the weight bound gives

```text
B_R + stored_form + 4 + 1 + 5m² + 10.
```

The fallback-form maximum yields `B_R+9m²+15`. A good Page has the smaller
bound `B_R+6m²+2mr-r²+15`, at most `B_R+28203` at rank42. Ratio arithmetic,
adapter negation and the final child negative inverse use fewer residues.

The incoming Callback retains six index Words: root size, depth, final size,
one, two and 64. The Page retains columns and its three geometry constants,
bringing the baseline to `B_I+10`. A pair child's column plus two bank address
Words add three while weight may add ten. This gives `B_I+23`. A good child
retains quotient/remainder instead and fits `B_I+22`; ordinary adapter banks
also fit `B_I+22`.

These are source invariants for successful execution. An exhausted arena or
invalid input can leave temporaries live. The failure tests explicitly roll
back to protected live sets and clear continuation tapes before resuming;
the bounds do not grant arbitrary exception safety to the source routines.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -Werror -B \
  scripts/research_package.py --package research/selected-callback-word-liveness
```

Direct commands also work in a Git-free export:

```sh
python3.12 -I -Werror -B research/selected-callback-word-liveness/verify.py
python3.12 -I -O -Werror -B research/selected-callback-word-liveness/test_verify.py
```

[RESULT.json](RESULT.json) is a fixed typed receipt. `verify.py --emit` prints
a fresh receipt without writing it; ordinary replay compares and writes nothing.
The checks execute the authenticated literal algorithms, with real complete
64-dimensional matrices and 128-dimensional residuals. Their q=3/q=5 templates
are explicit test inputs, not a claim of selected-catalogue membership or the
large-prime root coupling used by supplier admission.

Eleven weight histories cover root, good, pair, unit, halved unit, reversed
pair, mixed good/pair and binary fallback depth four. They include three or
seven unrelated live Words in each arena. The fallback fixture attains the
20,490 residue bound; the good fixture attains ten indices. Five initialized
Page evaluations retain all 16,384 fallback-form Words and exercise both
column orientations, negative inverses and a mixed ancestor history. They
attain `B_R+36879` and `B_I+23`, separately. Every successful evaluation checks
the literal returned coefficient, original numerical values/heads, serialized
input bytes/heads, erased continuation tapes and complete cleanup.

The allocation observer checks the budget on every allocation, and scans
literal occupied cells at geometric allocation thresholds and each new
inversion peak. It counts the permanent templates and scans erased backing
slots as well as live ones. The numerical routine and observer allocate no
hidden Words outside these two arenas. Small independent form fixtures verify
both exact stored-form formulas; `2I` inverse fixtures verify the nested ten-word
constant and endpoints. The separate tests reject one-word-underbudget residue
and index bounds, an omitted retained Page form, corrupted source/head/path/blob/
inventory, stale bytecode and an understated or wrongly typed receipt. Repeated
Page calls check reuse and preserve all borrowed inputs.

The universal conclusion rests on the written lifetime proof. Finite execution
supports it and detects implementation mistakes; it is not a universal proof
by enumeration. A separate read-only source review found no correction to the
inventory. No independent human review or formal-kernel result is claimed.
No selected GL64 Boolean payload, whole caller, cold supplier replay, physical
compiler, total reserve, new supplier or kappa claim is made here.

Registered replay passes on macOS27.0.1 arm64 / CPython3.12.15, including all
23 literal fixtures, 452 direct cell scans and twelve optimized behavioral
tests. Scoped Ruff diagnostics pass with `E4,E7,E9,F,I,UP,B,RUF`. The base
workflow suite passes70 tests with three skipped. A separate worktree at
refreshed main `8e22a9d9f621c72ab5b299061c2be4c7f638fd3c` passes the full registered
package under its changed subprocess-cleanup runner, and its updated workflow
suite passes74 tests with seven skipped. These are local results; hosted CI
has not been claimed.

## Engineering and overlap

Started from canonical main `936fac15b1b1b59dc5285c713a77f9f3c07b2906`, priority
revision5. The originating nonce, precise scope and predecessor heads are in
[TASK.json](TASK.json). The canonical claim is in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18958443).
Entry overlap covered 710 open PRs and 1399 discussion/comment/reply records with
complete pagination; the focused numerical/callback search at20:54UTC covered
715 open PRs without warnings. Searches cover metadata and local package notes,
not arbitrary code diffs. Live thread inspection distinguished Jose Manuel's
active numerical-bank codec and David Arias's coarser logical inventory.

Submission refresh covers715 open PRs at20:58UTC and1402 Discussion records
at21:00UTC, with complete pagination and no warnings. Main refreshed to
`8e22a9d9f621c72ab5b299061c2be4c7f638fd3c`; guidance, selection and the inspected
PR2697/2753/2759 heads are unchanged. The new independent PR2753 ordered-child
geometry claim in the same thread is complementary. TASK.json records the
coverage, exact environments and compatibility decision.

Build the Lever led to an authenticated allocation/cell checker. Prove It Works
led to returned-coefficient, literal-cell and input-preservation checks.
Power of Ten bounds the new fixture domain to depth four, matrices to128,
residue arenas to65536 slots and index arenas to128. New functions are below
60 physical lines, and acceptance uses errors that remain enabled under `-O`.

Managed-runtime deviation, rules3/8/9: Python allocates heap objects and the
checker must load six predecessor modules with their original import names,
and temporarily instrument two fixed methods. All source bytes are authenticated
before bounded explicit compilation; methods are restored on success/failure.
Fixture dimensions/capacities bound replay state, and subprocesses have timeouts.
This compensates for checker resource risks without claiming a fixed-heap or
physical-tape implementation. Revisit these deviations when the physical
allocator/compiler replaces the model. Frozen predecessor functions and their
data-bounded loops are inspected and left unchanged. Diagnostics and verification
commands/results are recorded in TASK.json.

## Open next questions

1. What numerical Words coexist during `selected_page` construction and the
   surrounding node/route primitives? Trace `good_form` construction and actual
   call sites, with the same entry-resident convention. This is needed before
   joining the category into a complete reserve. Constructor and surrounding
   lifetimes remain the blocker.
2. Can these numerical and separate continuation components fit the intended
   physical banks with the required time bound? Check the active numerical-bank
   codec, including slot identities, templates, markers, erasure and cursor
   movement. Physical lowering and the selected H2 contracts remain blockers.

These bounded questions and first steps are also structured in TASK.json.

## Credit

Prepared by Nick Petalas, Apache-2.0. Jose Manuel/jmbarrancoml supplied the
unchanged PR2697 implementation and its full control, normal-form, source and
hosting lineage. The complete predecessor notice is retained unchanged at
[vendor/NOTICE.md](vendor/NOTICE.md). Nick Petalas's PR2759 supplies the
primitive scratch bound and public resident-count handoff, and PR2758 supplies
the separate continuation component. David Arias's
[PR2753 at 7dba545](https://github.com/CrocSwap/integer-mult-bounds/tree/7dba5452a4071a856a0b11cebdcd2d3b6bcd7659/research/selected-bit-recursive-caller)
already supplies an all-size logical caller with a deliberately coarser
numerical inventory. This smaller component is not a first complete reserve
or an independent admission of that pending package. The related payload,
count and directory components retain their source notices and individual
credit in their respective packages.
