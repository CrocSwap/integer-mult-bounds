# Independent raw-array review of the literal CRT terminal

## Disposition and independence boundary

The supplied 73-role terminal passes this independent finite execution review.
The reviewer imports exactly `compile_terminal` from the implementation. It
does not import its `Port`, `execute`, fixture, relocation, digest, `Entry`, or
`Word` machinery. The imported compiler remains the object under review; this
check does not independently regenerate its graph.

The interpreter is a separate implementation over lists of single characters,
integer head positions, a literal program counter, and unit opcode dispatch.
The finite alphabet is renamed bijectively: implementation tokens `10` through
`13` become characters `a` through `d`. This changes neither branches nor
physical-cell counts. No packed record or abstract Word operation occurs in
execution. Every read, write, and move checks an explicitly supplied finite
backing, and moves into an absent first blank fail instead of granting storage.

Source `terminal.py` SHA256:
`1df6d9531caef791ee8ba75adb9a84dc8550ecce8acb2baf2018548ea9d4a6f6`.

The raw graph has 2,949 states and 73 roles. Every read branches over the complete
14-symbol alphabet; every write is literal; every move has displacement +1 or
-1; every target is inside the graph. Its addressed roles are exactly 8 through
72. No instruction addresses protected roles 0 through 7. The independent
canonical graph hash is
`f060e7097028921bda8945724d0b9668cdc20e9d6552d65215a925ee5bd78914`.

## Exact prices and postconditions

Let `P` be the precision-template length and let `n70`, `n71`, and `n72` be the
three nonblank record-prefix lengths. Direct counting of the literal paths
gives the following table. The record row is for one record of length `n`.

| Part | R | W | M | J | H |
| --- | ---: | ---: | ---: | ---: | ---: |
| Read-only guard | 370 | 0 | 730 | 0 | 0 |
| 56 inactive Word markers | 112 | 56 | 224 | 0 | 0 |
| Precision template | `2P+3` | `P+2` | `2P+6` | `2P` | 0 |
| One record | `2n+3` | `n+1` | `2n+6` | `2n` | 0 |
| Metadata and successful halt | 354 | 338 | 702 | 0 | 1 |

Thus, with `u=P+n70+n71+n72`, the full success price is exactly

```
R = 848 + 2u
W = 399 + u
M = 1680 + 2u
J = 2u
H = 1
total = 2928 + 7u.
```

The reviewer checks every opcode count separately; checking only the total
would miss a write replaced by an equally priced jump.

Twenty independently constructed raw fixtures use `P` equal to 4, 8, 23, 128,
and 1024. Each precision uses record lengths `(0,0,0)`, `(1,2,3)`, `(17,31,5)`,
and `(P+5,2P+3,P//2+11)`. The 56 free records are rotated or reversed rather
than always listed in numerical order. Every fixture has 76 distinct physical
arrays, unequal historical capacities, blank inactive historical tails, and
dirty protected arrays with heads at varied positions including zero and the
last backed cell. Roles 73 through 75 are additional protected spectators.

For every successful execution, the reviewer verifies every cell of every
historical backing: roles 8 through 72 are completely blank, the original
arrays and capacities remain, and all protected arrays and heads are unchanged.
The restored owned heads are 1, except that roles 64 through 67 and 69 return
to zero. The exact reached intervals are `[0,1]` for roles 8 through 63,
`[0,7]` for roles 64 through 67, `[0,P+1]` for role 68, `[0,337]` for role 69,
and `[0,nj+1]` for record role `j`. Protected heads never move.

The already blank historical tails are checked, not rescanned by the graph.
Consequently this result relies on the admitted inactive-tail premise; it does
not assert that arbitrary dirty inactive tails can be retired for the same
price.

## Independent relocation

The reviewer relocates every explicit read and jump target by 1,435,098 using
its own transformation. The resulting target range is contained in
`[1435098,1438047)`. The interpreter runs with absolute program counters and
fetches the local suffix at `pc-base`; no million-state prefix is constructed.
The relocated graph hash is
`71eff59af7dab72a7a9be37ebf92cecae9f3fd646ff54632ae8de7db49cf9901`.

Every fixture is executed both locally and after relocation. The normalized
instruction traces, opcode prices, final cells, final heads, and reached
intervals agree exactly. There are 40 successful terminal executions comprising
247,208 literal instructions.

## Controls

1. **A returning mutation is rejected.** The last blank write to role 70,
   state 1521, is replaced by a jump to its successor. The mutant still returns
   `CLOSED` with the same total number of instructions, but has one fewer write
   and one more jump. The role-70 left marker survives. The independent complete
   postcondition rejects it.

2. **No implicit blank grant.** A role-70 backing containing its left marker and
   seven nonblank body characters, with no backed first blank, raises the
   independent window error. Its backing identity and capacity remain unchanged.
   This is a domain control, not a promise of rollback after a failed close.

3. **A live slot prevents destructive close.** A legal 55-record free stack
   leaves role 8 live. The graph returns `REJECTED` with exact price
   `R=364, W=0, M=387, J=0, H=1`, total 752. Every physical array is unchanged.
   Head rollback on rejection is not claimed.

4. **The fixed-70 variant has a genuine footprint limit.** Its graph has 2,904
   states and operands only in roles 8 through 69. It returns
   `NUMERICAL_CLOSED` with exact price
   `R=839+2P, W=396+P, M=1662+2P, J=2P, H=1`, total `2898+7P`.
   All three nonempty record owners, their heads, and their left markers remain
   unchanged. More generally, induction on its literal instruction sequence
   shows that an array outside its fixed role binding cannot be written. It
   therefore cannot meet complete close for those record owners. This is a
   fixed-binding obstruction, not a lower bound against redesigned graphs,
   aliases, or independently supplied rebinding operations.

## Portable replay

The script and its deterministic receipt can be copied into a package without
changing the script. If the files are installed as `review/check_terminal.py`
and `review/RESULT.json`, register both commands:

```
python3.12 -I -B PACKAGE/review/check_terminal.py --terminal PACKAGE/terminal.py --expected PACKAGE/review/RESULT.json
python3.12 -I -O -B PACKAGE/review/check_terminal.py --terminal PACKAGE/terminal.py --expected PACKAGE/review/RESULT.json
```

Both commands have passed against the supplied source with the original local
filenames `check_terminal_independent.py` and `EXPECTED.json`. Assertions are
implemented as explicit conditional exceptions, so optimized Python preserves
the checks. The receipt is compared exactly and the script writes no file.

## Scope and attribution

This review covers the standalone literal terminal, its supplied success
domain, exact execution price, historical postcondition, and independent suffix
relocation. It does not replay the million-state arithmetic prefix or certify
that every producer establishes the entry premises. Free-stack uniqueness,
the inactive-tail invariant, pre-backed first blanks, disjoint owner bindings,
and correct lifecycle attachment remain explicit integration premises.
No selected foundational assumption or full multiplication bound is discharged
by this finite review.

Credit remains with the CRT terminal author and the preceding CubeJerry
Entry/lifecycle and current-CRT arithmetic work retained by the host package.
This portable review was prepared by a separate OpenAI-assisted review worker
for Jerry Chen / CubeJerry. It is not a human audit or a proof-kernel certificate.
