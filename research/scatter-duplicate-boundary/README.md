# Selected scatter rows agree; an even duplicate does not

**Partial. No new exponent.**

The scatter repair from #2977 is not in the pinned exporter. On the selected
tuned word, the symbolic replay and the export action agree, because every
scatter row has distinct indices. Appending `[0, 0]` to the first row makes
them disagree. A triple append agrees again. Uniqueness is a sufficient guard,
and it is stronger than that agreement rule. The frozen exporter is unchanged.

## What was executed

The pinned word has `v=111` and 111 scatter rows. The first row is
`[4, 5, 6, 7, 8]`. Every row is free of repeated indices. The real
`Word.replay` scatter section and the real exporter statements
`if k in row` were run on that word. All 527 scatter terms agree: the symbolic
coefficient of each retained index is the export ADD.

Appending two copies of the absent index 0 raises the symbolic term count to
529. Those two XORs cancel, so the symbolic coefficient is 0. The exporter
still emits one ADD, so its coefficient is 1. That is the only disagreement,
at target 0 and retained index 0.

Appending three copies leaves both coefficients at 1, so the actions agree.
The agreement rule is that every positive multiplicity is odd. Uniqueness
accepts the selected rows and rejects both appends. The generator builds rows
with `itertools.combinations`, which is why the selected rows meet the stronger
condition. No guard was added to the frozen exporter.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 6, refined to this
fixture. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the exporter, the symbolic checker, the
generator, the tuned word, and the task catalogue. No selected frontier file
changes. The native column checker is not run.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/scatter-duplicate-boundary/verify.py
python3.12 -B research/scatter-duplicate-boundary/test_verify.py
python3.12 -B scripts/research_package.py --package research/scatter-duplicate-boundary
```

Both commands finish in about a second.

## Open next questions

A successor exporter can enforce unique rows, or it can define multiplicity and
make the symbolic coefficient match the exported ADD. Either change needs its
own source binding. This package does not edit the frozen exporter.

## Credit

eumemic supplied the symbolic replay. Dylan Crow supplied the exporter. The
selected tuned word and the combination generator are the PR589 lineage named
in #2977. Nick Petalas's #2977 named this duplicate and left the guard opt-in;
this package reruns the two pinned actions rather than importing that checker.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
