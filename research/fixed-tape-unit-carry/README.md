# A fixed-tape ordered shear with unit carry

**Construction:** for every positive binary-encoded P,Q,G,S and every Boolean
payload of volume V=P Q² G S, the finite controller moves

```
(p,x,g,y,z) -> (p,x,g,(y ± (x+1)) mod Q,z).
```

Each direction uses **fourteen tapes, seven symbols, and 552 microinstructions**,
independent of runtime extents. It preserves the source and descriptors, returns
their heads, creates an owned output, and erases all scratch cells and markers.
The complete bound is **449V transitions and 41V visited cells**. The exact
transition count is the PR2776 zero-carry count plus **seven**, for every valid
shape and payload. This is a physical cost statement, not a wall-clock speedup.

David Arias's [PR2776](https://github.com/CrocSwap/integer-mult-bounds/pull/2776)
leaves named nonzero-carry kernels as its first open question. This package
implements the coefficient/carry pairs (+1,+1) and (-1,-1). They occur in the
existing low-digit arithmetic at (q-1,1) and (q-1,0), respectively. The generic
ordered-affine method and the zero-carry controller remain predecessor work.
This does not establish arbitrary carries, a full caller, selected H2, or a new kappa.

## Argument and evidence

[PROOF.md](PROOF.md) gives the quantified contract, full loop invariant, endpoint
argument, exact instruction-count comparison, visited-space ledger, and binding
to the existing source interface. [carry.py](carry.py) implements the changed
phase. [TABLE.json](TABLE.json) contains both complete finite programs.

The changed phase starts its unary split at (Q-1,1), visits Q consecutive splits,
and restores that pair between prefixes. The endpoint follows from splitting
each target fibre into lengths Q-x-1 and x+1. The initial transfer adds seven
steps; all later transfer, reset, copy, and cleanup counts retain their totals.

[RESULT.json](RESULT.json) records:

- 270 executions in a separate dense interpreter, across 78 shapes and complete
  small Boolean payload/basis families, with independently translated origins.
- A direct coordinate **gather** oracle that shares no split traversal, counters,
  or assembler with the controller; 24 sparse/dense whole-bank comparisons.
- 156 predecessor comparisons on the **same inputs**, all with exactly seven
  extra transitions; 12 inverse round trips and 12 literal nonzero-carry source
  comparisons, without an ordinary-interchange oracle.
- Ten semantic controls, including the correct zero-carry predecessor, missing
  carry resets, retained scratch, omitted rewind, corrupted payload, and nonlocal
  movement. A cost-only control preserves every endpoint but adds two unbilled moves.
  Separate tests exercise source/table/receipt changes, preloaded
  modules, stale bytecode, and optimized read-only exports.

These are finite implementation checks. The all-size result rests on the written
induction and path count, including the retained PR2776 counter lemmas. There is
no independent human review or proof-assistant verification. Receipt
equality and repeated execution alone are not independent validation.

## Reproduce

Primary research verification uses stable CPython 3.15.0, standard library only:

```sh
python3.15 -I -B research/fixed-tape-unit-carry/verify.py
python3.15 -I -B -O research/fixed-tape-unit-carry/test_integrity.py
```

Expect `PASS_FIXED_TAPE_UNIT_CARRY` and `PASS_UNIT_CARRY_INTEGRITY`, respectively.
In the originating Math workspace, invoke each command through `research-python`.
The repository's generic runner currently requires a Python 3.12 declaration.
VERIFY.json retains that separate compatibility environment:

```sh
python3.12 -B scripts/research_package.py --package research/fixed-tape-unit-carry
```

Verification reads saved artifacts without changing them. Explicit `--emit`
refuses to overwrite an existing table or receipt. [VALIDATION.md](VALIDATION.md)
records actual interpreter versions, commands, and results. Local replay does
not establish a hosted CI result.

## Scope, pins, and contribution

The fixed program accepts arbitrary spectator lengths and Q=1. It assumes
canonical positive descriptors, complete Boolean input, distinct physical roles,
and blank output/scratch tapes. It does not establish cleanup after arbitrary
invalid inputs or exceptions. Installing these roles inside a recursive caller
remains separate work.

[EXPORTS.json](EXPORTS.json) authenticates the required PR2776 exports at commit
`7de16285a02ebb45cf46e7501baa7eafa78335e3`, plus the frozen affine source from
main `e24ccc79caa1943fb126c61b45032fefddf2d3f2`. Original source bytes remain
unchanged. The separate SOURCES.json pins historical task and selection context.
The selected result and upstream files do not change.

The contribution is one completed physical carry case with the same role count
and an exact marginal cost. It narrows an explicit compiler gap and supplies a
reviewable component; it does not improve the multiplication exponent. Initial
overlap covers 690 open PRs, 1471 discussion records, and 2105 local records.
No matching carry implementation appears in that metadata search. This is not
a novelty certificate and does not cover arbitrary diffs or unpublished work.

## Open next questions

1. Can one fixed carry other than ±1 use this role budget? Start by constructing
   a complete cycle through Q split positions; arbitrary offsets need another
   stopping invariant. Do not assume repeated unit shears implement translation.

2. Can the named physical caller allocate these roles without an alias or lifetime
   conflict? Bind one actual call only after its input, output, and scratch owners
   are explicit.

   The kernel alone does not settle physical reserve or H2.

TASK.json records these questions, the scope, seed, stopping rule, and overlap.
See [NOTICE.md](NOTICE.md) for complete predecessor credit. New work is Apache-2.0,
prepared for Charles Bethin with substantial OpenAI Codex assistance.
