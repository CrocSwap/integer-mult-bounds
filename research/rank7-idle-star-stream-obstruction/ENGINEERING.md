# Verification and bounded implementation

Build the Lever led to a standalone source projection and exact operator
checker rather than an additional prose-only warning. Prove It Works led to
reconstructing the actual T740 fill and helper chronology before applying the
older PR1387 obstruction. No predecessor executable is imported.

The code has no recursive call path, subprocess, dynamic execution, network or
output file mutation. Local functions remain below sixty physical lines.
Meaningful checks use exceptions and remain active under optimized Python.
Inputs are authenticated before interpretation, with a 32,000,000-byte bound
on compressed and decoded individual files. Proof-relevant data is fixed by
source hashes, not supplied as an unbounded user collection.

Loop bounds are: 2,717,280 fill rows, 145 edits, 271,728 base rows, 666 base calls,
6,660 lifted calls, 30 projected hosts, 408 provider widths, 112 recipes,
20 children per recipe, 73 axes per child at most, two projected moves of three
axes, eight streams and 147 baseline characters. Vendor moves have 125,706 rows
before projection. Template loops use its fixed authenticated event/recipe lists.
The fill hash is streamed; only thirty projected rows are retained.

Power of Ten rule 3 deviation: CPython requires allocation for JSON, integers,
lists and exact row operations. Scope is this bounded offline checker. Input
caps, fixed authenticated inventories and a streamed lifted fill bound live
objects; the complete multi-million-row lifted fill is never retained. JSON and
gzip runtime internals are not allocation-audited. Verification runs include
the complete fill, controls and read-only source exports. A future general-input
tool must add an explicit configurable memory/resource contract before relaxing
these fixed inventories.

Rules 8/9 framework deviation: unittest discovers nineteen explicitly defined
test methods, and two controls use scoped mock dispatch. The only custom
callback substitutes bytes in a twelve-file source inventory; its patch context
restores the original function on success or failure. No runtime-generated code
or vendor executable is involved. These targets and lifetimes are exercised by
the optimized test run. A broader input service would need an explicit adapter
instead of expanding these test-only callbacks.

Rule 10: the registered replay is the recurring interpreted-code check.
Warning-as-error compilation and available Ruff checks run before publication;
CHECKS.json records exact commands. New package code does not alter shared
verification configuration or frozen predecessor bytes.

The independent internal mathematical review found that the original structural
star rule lacks the physical stream conjugacy equation. This changed the
investigation from a formal profile optimization to the actual candidate's
semantic acceptance gap. The interval proof and direct exact matrices agree.
Human and proof-kernel review remain open.
