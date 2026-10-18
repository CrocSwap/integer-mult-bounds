# The length-18 census budget rejects a universal four-label word

**Partial. No new exponent.**

The pinned #2542 census groups prefix states by bit 0 and prunes them with a
budget derived for Hamming-weight parity. On the universal word `01021323`
those two groupings disagree. The same budget rejects 6 of the 22 simple
canonical universal words at four labels and length 8. No seven-label census
was run.

## What was executed

The word `01021323` has prefix states `0,1,3,2,6,4,12,8` and then returns to
`0`. Those eight states are distinct, their pairwise sums cover all 16 masks,
and every label occurs twice. Grouped by Hamming weight the classes are
`(4, 4)` and the collision count stays 0, inside the balanced budget 5.
Grouped by bit 0 the classes are `(6, 2)` and the collision count reaches 8
at the seventh step. The budget substituted from the balanced weight split is
5, so that walk is rejected. The budget for the actual bit-0 sizes is 9, and
8 does not exceed it.

The pinned call is `cyclic_census(7, 18, budget=9, simple=True)`. Its comment
derives 9 from `C(9,2)+C(9,2)-63`, the weight split `(9, 9)`. The engine
itself puts a new state in the odd class when `nq & 1`. The length-20 package
vendors that same engine text.

The small domain is every restricted-growth word with even label counts at
`(n, L)` in `{(3, 6), (3, 8), (4, 8)}`. The universal counts are 10, 182 and
26. Restricting to words whose nonclosing states are distinct, which is the
`simple=True` walk, leaves no false prune at three labels. At four labels and
length 8 it leaves 6. None of those six exceed the budget of their own weight
split.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
word and this domain. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the two engines, the length-18 call, and
the task catalogue. No selected frontier file changes. This does not replay
the corrected seven-label census and does not decide `f(7)`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/f7-bit0-false-prune/verify.py
python3.12 -B research/f7-bit0-false-prune/test_verify.py
python3.12 -B scripts/research_package.py --package research/f7-bit0-false-prune
```

The domain enumeration is the slow command. It finishes in well under a second.

## Open next questions

A corrected weight-parity replay would be needed before the length-18 zero-hit
receipt can be read as an exclusion. That replay is a separate seven-label
budget, and this package does not run it.

The author-checked claim `22 <= f(7) <= 24` in the PR943 model likewise stays
outside this check.

## Credit

Aaron Wang supplied the #2542 engine and the length-18 call that this walk
reconstructs. The length-20 package vendors that engine. Nicholas Stone's
#2973 named `01021323` and separated the two budgets; this package recomputes
the walk and the small domain rather than importing that checker. Ross
Richardson supplied the PR943 prefix-walk model in which the later census
question is posed.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
