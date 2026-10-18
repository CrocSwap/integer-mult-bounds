# Verification record

Status: local construction and implementation verification.
There is no hosted CI, external human, or formal-kernel result in this record.

## Source and environment

The scientific predecessor is PR2776 at
`7de16285a02ebb45cf46e7501baa7eafa78335e3`.
The isolated base is `e24ccc79caa1943fb126c61b45032fefddf2d3f2`.
The submission check fetches main at `fbdbcb533128462ebfd9dd75b82b02a4f40ecc5a`.
Relevant guidance, the selection, the runner, and the affine input have no changes.

Primary verification uses the Math `research-python` wrapper:

```
3.15.0 (main, Oct  9 2026, 11:16:41) [Clang 21.0.0 (clang-2100.3.34.2)]
/opt/homebrew/opt/python@3.15/bin/python3.15
```

The official Python downloads page lists 3.15.0 as stable during this run.
The [Python release list](https://www.python.org/downloads/) distinguishes the
3.16 prerelease. The runtime needs no update.

The repository's generic package runner explicitly requires Python 3.12.
Its separate compatibility replay uses:

```
3.12.12 (main, Oct  9 2025, 11:07:00) [Clang 17.0.0 (clang-1700.3.19.1)]
/opt/homebrew/opt/python@3.12/bin/python3.12
```

That invocation is a declared compatibility exception, not the research runtime.
The unchanged predecessor's own historical runtime records remain unchanged.
The new package uses only the standard library.

## Completed checks

| Command | Result |
| --- | --- |
| `python3.15 -I -B research/fixed-tape-unit-carry/verify.py` | PASS_FIXED_TAPE_UNIT_CARRY |
| `python3.15 -I -B -O research/fixed-tape-unit-carry/verify.py` | Same complete receipt bytes |
| `python3.15 -I -B -O research/fixed-tape-unit-carry/test_integrity.py` | Eight integrity/export controls pass |
| `python3.15 scripts/research_package.py --package research/fixed-tape-unit-carry --check-only` | Metadata and exact provenance pins pass |
| `python3.12 -B scripts/research_package.py --package research/fixed-tape-unit-carry` | Both registered commands pass |

The main receipt contains 270 dense cases over 78 shapes, 24 sparse comparisons,
156 identical-input predecessor comparisons, 12 nontrivial inverse round trips,
and 12 actual nonzero-carry source comparisons. Ten semantic controls reject
their injected faults. One preserves every final value and head while adding
two paid moves; the exact ledger rejects it.

The direct coordinate gather model shares no split traversal or controller
helpers. The dense interpreter reads the serialized table independently of the
producer. These are the independent checks of the finite implementation.
The sparse interpreter and repeated receipts provide additional consistency checks.

The all-size argument separately proves the changed phase invariant, every
fibre endpoint, complete cleanup, and the exact cost difference from PR2776.
It retains that source's counter and primitive-macro arguments explicitly.
It does not turn the finite corpus into a theorem about unrestricted multiplication.

## Coverage and stopping rule

Shapes cover both parities of Q, Q=1, simultaneous spectators, and descriptor
shrink boundaries through 128. The maximum payload has 961 bits. The corpus
includes all 16 four-bit payloads and complete bases for two other layouts.
The proof covers arbitrary positive extents; the executions cover only this corpus.

The implementation stops after the unit-carry contract and its verification pass.
It does not expand to arbitrary carries, runtime coefficients, reversed fields,
caller allocation, or the selected H2 recurrence.

No global historical suite runs for this additive primitive. The selected cold
replay is unnecessary because the selected construction and its inputs do not change.
There is no wall-clock speed claim. The complete physical comparison uses the
same inputs before and after, with the changed affine endpoints stated explicitly.
