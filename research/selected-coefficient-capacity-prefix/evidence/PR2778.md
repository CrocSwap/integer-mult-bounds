# Numerical storage while constructing a selected BIT form

The unchanged PR2697 form constructors have these sharp excess live-Word bounds,
above **all** numerical Words live on entry:

| Constructor, m=64 | Additional residue Words | Stored output Words |
| --- | ---: | ---: |
| `good_form`, rank r, 1 <= r <= 42 | `6m²+4mr-r²+10`, at most **33,574** | `m²+2mr-r²`, at most 7,708 |
| `fallback_form` | `8m²-2m+5` = **32,645** | `4m²` = 16,384 |

Literal 64-dimensional projectors attain both peaks. The input projector is
borrowed and already consumes 4,096 entry Words. Including just that projector,
the modulus and `ring.one`, the rank-42 good fixture needs **37,672** live Words,
above unrelated borrowed residents. This exceeds PR2770's 36,879 allowance for
an initialized Page's evaluation. That earlier result explicitly excludes
construction; this closes the form-construction part of its first next question.

These are occupied numerical-content bounds. They do not price erased backing
slots, Python heap objects, other simultaneous caller residents, physical tape
placement or a complete reserve. No selected frontier or kappa changes.

## Contract and sources

Fix a square 64-by-64 matrix of distinct canonical residue Words in the Ring's Arena,
as returned by the pinned preparation.
Fix an admitted odd prime power `M=q^w`, positive w, with the pinned arithmetic
word margin. Every entry Word and the permanent template have their heads at
cell 1. The input satisfies the invoked branch's unit-pivot and endpoint
contracts. Execution is sequential, with sufficient arena capacity and no
observer allocating numerical Words. The conclusions concern successful
execution. The bounds do not establish that every projector has a legal pivot
sequence. The constructors do not validate arbitrary Python matrix shapes.

Let L count all live Arena slots on entry, including the projector, modulus,
`ring.one`, incoming callback constants and every unrelated borrowed Word.
The live count is at most `L+G(r)` or `L+F`. Successful return preserves every
entry Word and its head, retains exactly the stated owned output, and leaves
no other numerical temporary. Closing that form restores exactly the entry
live set. Each live Word has b binary cells and one RIGHT delimiter; the Arena
also retains one permanent template. Thus occupied non-LEFT content is at most
`(L+G(r)+1)(b+1)` or `(L+F+1)(b+1)`. LEFT markers are separate.

Jose Manuel/jmbarrancoml's
[PR2697 at a53fdf4](https://github.com/CrocSwap/integer-mult-bounds/tree/a53fdf4bcbe33c6732f0bec1badc8c023380f9d1/research/selected-bit-node)
supplies the unchanged algorithms. [SNAPSHOT.json](SNAPSHOT.json) records
original paths, Git blobs and SHA256 hashes of three byte-identical modules
and their complete [notice](vendor/NOTICE.md). All exports authenticate before
any execution. Compilation uses those bytes directly and bypasses stale caches.
[SOURCES.json](SOURCES.json) pins the base catalogue and selected result as
historical provenance.

Nick Petalas's [PR2759](https://github.com/CrocSwap/integer-mult-bounds/pull/2759)
supplies the primitive ten-Word inverse bound. The
[PR2770](https://github.com/CrocSwap/integer-mult-bounds/pull/2770) evaluator
inventory and handoff exclude these constructors. David Arias's
[PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753) already gives
a coarser complete logical inventory. This contribution sharpens one component;
it is not the first logical reserve or admission of that pending caller.

## Lifetime proof

The following primitive excess allowances follow the actual allocation/free
order in [words.py](vendor/words.py): add/subtract at most two Words, negate
three, multiply four and inverse ten. Modular inversion retains four Euclidean
Words, quotient and remainder while multiply allocates at most four more.
Those operands are freed before the next iteration. Iteration count does not
accumulate live Words. The same proof applies at arbitrary legal bit widths.

`Matrices.inverse` adds `2d²+10` above all its entry residents. Its d² identity
Words alias the augmented rows' right halves; copied input occupies another
d² Words. Pivot inversion adds ten. Row normalization and elimination add at
most six. Matrix multiplication adds its output size plus at most four.

### Good form

Write `S=r+2 sum(k=0..r-1)(m-1-k)=2mr-r²`. This counts every retained pivot,
row scalar and column scalar, including zeros. The original projector is an
entry resident throughout. The following table counts additional Words.

| Phase | Excess upper bound |
| --- | --- |
| Initial reversed copy and two identities; elimination | `3m²+S+10` |
| Invert left after freeing reversed copy | `4m²+S+10` |
| Invert right while retaining left inverse | `5m²+S+10` |
| Build `lp` | `5m²+S+4` |
| Build `a0` | `5m²+mr+S+4` |
| Build `b` | `5m²+2mr+S+4` |
| Negate `a0` and `b` | `5m²+2mr+S+3` |
| Allocate cross and invert each pivot | `6m²+2mr+S+10` |

The first phase's pivot copy is included in S. A retained inverse plus a row
or column update adds at most five beyond its matrix/scalar residents. Slices
and reversed row lists borrow existing Words. At the last phase, `left`,
`right`, `li`, `ri` and `lp` contribute `5m²`; `a0` and `b` contribute `2mr`;
the cross contributes `m²`. The largest phase is therefore
`G(r)=6m²+4mr-r²+10`. Replacing cross entries uses at most five excess Words,
below its ten-Word inversion allowance. All seven intermediate matrices are
then freed. The returned form contains exactly `m²+S` distinct owned Words.
For m=64, G increases over ranks 1 through 42 and G(42)=33,574.

For attainment over F3, put the all-2 rank-one block on coordinates 0 and 42,
put diagonal ones on coordinates 1 through 41, and set everything else zero.
This is an idempotent of rank 42. The first pivot is 2. Its final cross-phase
inverse attains ten while every listed matrix is retained. The two nonzero
cross entries are `(21,0)=1` and `(63,42)=2`. The literal replay independently
checks the complete cross, pivots and chronological scalar lists.

### Fallback form

Put `n=2m=128`. The residual matrix has n² Words. Each completed pivot column
retains exactly n-1 shear scalars, including zeros. Swap records own no
numerical Words. At pivot column j there are j(n-1) retained scalars, so even
failed unit candidates fit `n²+(n-1)²+10=32,523` above entry.

A row update can coexist with all `n(n-1)` retained scalars, its one pivot
inverse, and four multiply temporaries. This gives
`n²+n(n-1)+5=32,645`. Computing a new negative coefficient before appending it
uses no more. Residual construction needs n²+4. Terminal determinant processing
needs at most n²+n(n-1)+5, before freed off-diagonal Words reduce that count.
After cleanup the diagonal's n Words and the n(n-1) retained scalars total n².

For attainment, over F3 use the rank-one block `[[2,1],[1,2]]` on coordinates
0 and 1 and zero elsewhere. At the last shear the coefficient is 2, the last
diagonal is 2, the inverse remains live and multiplication reaches four
temporaries. The bound is attained. The integer checker replays every returned
row operation on an independently constructed full residual matrix, verifies
all chronological permutations and the diagonal, and checks determinant parity.

The selected formula is restricted to m=64. The smaller test fixtures use
`max(n²+(n-1)²+10, n²+n(n-1)+5)`. At m=2 the first term is 35; the second is
33 and would be an invalid bound. No small-dimension shortcut is imported into
the selected proof.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -Werror -B \
  scripts/research_package.py --package research/selected-form-construction-storage
```

Direct replay also works from a Git-free package export:

```sh
python3.12 -I -Werror -B research/selected-form-construction-storage/verify.py
python3.12 -I -O -Werror -B research/selected-form-construction-storage/test_verify.py
```

[RESULT.json](RESULT.json) is a fixed typed receipt. Normal replay compares it
without writing. `verify.py --emit` prints a fresh receipt. Twenty-two fixtures
cover dimensions 1, 2, 3, 5 and 64, ranks 1 and 42 at dimension 64, F3 and Z/9,
and three or seven unrelated borrowed residents. The receipt distinguishes
each measured peak from its allowance. Allocation checks run on every source
allocation; independent scans count the literal occupied cells, including
erased backing slots and the permanent template. Integer checks verify complete
form endpoints outside measured execution. Closing checks exact ownership,
borrowed bytes and restored heads, then the fixture erases every owned Word.

Twelve tests include one-Word-underbudget rejection for both constructors,
omitted input-matrix charge, the insufficient initialized-evaluator allowance
on a literal rank-42 fixture, extra borrowed residents, a wrong cross entry,
borrowed-input corruption, the entry-head precondition, repeated construction/close,
typed receipt and source pin corruption, and a demonstrably loadable stale-bytecode trap that the
authenticated loader bypasses. Valid-but-incompatible or invalid source inputs
exercise the good pivot, northeast endpoint, fallback unit and determinant
guards. Rejection cleanup uses explicit external rollback; no constructor-level
exception-safety claim is made.

The universal upper bounds rest on the written lifetime argument. Finite
fixtures demonstrate attainment and detect errors; they do not enumerate all
projectors or prove selected-catalogue membership. A separate read-only review
independently derived both bounds and attained them from the original source.
This is internal review, not human review or formal-kernel verification. Full
Boolean payload execution, the selected cold replay and total reserve admission
are outside this check.

## Scope, engineering and continuation decision

The session follows the live PR2770 handoff instead of the task picker's initial
bit-mechanism suggestions. [TASK.json](TASK.json) records that change, exact
sources, live overlap coverage, freshness, commands and structured next questions.
The canonical claim is in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18959091).
The active physical Frame/bank and fresh-row-padding work concerns different
obligations. Metadata searches do not inspect arbitrary code diffs or prove
novelty. This package changes no predecessor bytes or selected record.

The expansion decision is **narrow and finish this audit**. The constructor's
numerical excess is proved and attained. The entry-resident total remains an
explicit L, and program/field tapes, simultaneous callers, continuation,
markers, backing capacity and physical placement remain separate charges.
Unknown costs are not zero. No new dependent search or supplier expansion is
justified by this local lemma alone.

Build the Lever led to the rerunnable authenticated census. Prove It Works led
to literal cells, complete algebraic endpoints and rejection checks. Power of
Ten bounds new replay dimensions to 64, residuals to 128, arenas to 65,536 slots,
and fixture bit widths to five. New functions fit within 60 physical lines.
Acceptance checks remain active under optimized Python.

Managed-runtime deviations, rules 3, 8 and 9: Python allocates heap objects, the
loader explicitly compiles three authenticated predecessor modules, and the
census temporarily instruments one fixed allocation method. Fixture dimensions
and arena capacities bound live replay data, and the replay manifest bounds
subprocess time. The method is restored on every exit. This does not assert
fixed-heap or physical-tape compliance. Replace this measurement arrangement
when the physical allocator/compiler is admitted. Frozen source loops are
bounded by their finite matrices, word extents and decreasing Euclidean state;
their implementation remains unchanged. Scoped Ruff diagnostics and the
registered normal/optimized checks are the maintained validation commands.

## Open next questions

1. What entry residents coexist with these forms in actual `selected_page`
   construction, surrounding route operations and suspended callers? Start by
   joining this lifetime table to PR2770's evaluation theorem and tracing the
   caller's actual constants, high matrices and index words. That simultaneous
   inventory blocks a complete numerical reserve claim.
2. Does the combined numerical inventory fit physical shared banks with the
   required movement and time cost? Start from the active Frame/bank codec and
   charge backing slots, templates, markers, grants and return lifetimes.
   Logical live content alone does not provide that implementation.

## Credit

Nick Petalas, Apache-2.0. Jose Manuel/jmbarrancoml supplied the unchanged PR2697
algorithms and their retained control, source, normal-form and hosting lineage.
The complete predecessor [NOTICE.md](vendor/NOTICE.md) remains unchanged.
Nick Petalas's PR2759/2770 supply the primitive/evaluator components and handoff;
David Arias's PR2753 retains credit for its earlier coarser all-size logical
inventory. This package adds the constructor proof, sharp fixtures and census.
