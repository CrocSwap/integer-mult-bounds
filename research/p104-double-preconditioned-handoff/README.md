# A 232-unit nonunit helper handoff

Two ordered preconditioners reduce the concrete PR6322 handoff to **22 ADDs
and scalar allowance 232**. This saves 40 allowance units against its
26-ADD, 272-unit alternative, and 48 against its 22-ADD, 280-unit construction.
The complete new local word has 25,162 events and allowance 217,660.

Claim type: scoped algebraic construction with exact finite corroboration.
The 22-ADD count matches the predecessor's proved minimum for four separately
completed boundaries. No weighted optimum or new kappa is claimed.

The change answers [PR6322](https://github.com/CrocSwap/integer-mult-bounds/pull/6322)
Open next question 2 for its exact historical dual pairs. Its elementary
column-unit formula is a premise. The new step is the ordered pair of
preconditioners, their cheaper explicit completion and its whole-word use.
See [PROOF.md](PROOF.md) and [completion.py](completion.py).

## Scope and evidence

The constructor retains 736 independent public inputs, eight owned lifetimes,
peak owned storage one, the rank-9 to rank-5-plus-rank-4 split and the complete
paid profile. Two retained arithmetic engines check the **new** word on all
744 formal columns, including 553,536 endpoint coefficients. One uses rational
sparse rows and the other integer rows with binary denominators. Both are
checks using credited predecessor implementations.

The verifier checks both boundary equations and their full inverses. It rejects
all eleven single forward-boundary gate omissions, both reversals of the
preconditioner order and eight whole-word coefficient, chart, ownership or
boundary faults. Its computed stdout receipt includes all source and package
hashes plus the deterministic candidate-word hash. It writes no receipt or
word into the checkout.

[SOURCES.json](SOURCES.json) pins the four live inputs at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. This includes the original PR5580
word, Ali Romman's handoff constructor and primary scalar checker, and
CubeJerry's second arithmetic implementation. No predecessor scientific suite
is replayed as the deliverable. The bounded discovery search stopped when this
first reduction appeared; no exhaustive search conclusion is asserted.

The selected record and all five framework assumptions remain unchanged.
This is a historical scalar boundary improvement. Native phase/implementation,
complete physical caller, stock, rounded precision/tape, compiler closure and
outer admission are unrun or inherited. The recursive paid and target profiles
are unchanged, so the scalar saving supplies no exponent gain. There is no
complete multiplication theorem or independent human or proof-kernel review.

## Reproduce

From the contribution checkout root, with Python 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-double-preconditioned-handoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p104-double-preconditioned-handoff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-double-preconditioned-handoff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-double-preconditioned-handoff --check-source-history --check-modes
```

Another CPython 3.12 executable can replace the local interpreter path.
Expected markers are `PASS_P104_ORDERED_HANDOFF inserted_events=22
inserted_allowance=232`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Registered normal and optimized commands have
120-second bounds. [CODE-BOUNDS.md](CODE-BOUNDS.md) records implementation limits.

## Open next questions

Can allowance fall below 232 under these same boundary equations? A
coefficient-sensitive lower bound, including both inverses, would decide whether
this construction is optimal. The existing ADD-count bound does not do so.

Does a current source word retain a compatible nonunit handoff? First extract
its exact prefix/suffix pair and available charts. Changed helper boundaries
and the complete native/caller bill block transfer of this historical saving.
Structured questions and the narrowed card scope are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.
CubeJerry PR6322 supplies the dual pairs, column-unit construction, ADD-count
minimum, lower-allowance alternative and separate arithmetic checker.
unpaidmoon PR6297 supplies the original concrete nonunit split. Ali Romman
PR5611/5602 supplies dyadic completion and the coupled handoff contract.
The retained source word and checker credit David Arias, Cinna Davis,
Gareth Davidson, Ali Romman and their P104/native/controller predecessors.
Their files and credit lines are unchanged. Elementary shears and the
rank-one handoff identity are classical or credited predecessor work.
