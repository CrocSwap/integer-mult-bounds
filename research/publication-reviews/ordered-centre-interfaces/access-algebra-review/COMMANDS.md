# Commands and check scope

The required description standard was read before the body review:

```sh
cat /Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md
```

The exact independent command, current directory, and environment are in
[COMMAND.json](COMMAND.json). The copy and output locations are in
[RUN-LOCATION.json](RUN-LOCATION.json). The runner copies the frozen
layout for each child, removes its old receipt, and compares its newly
generated receipt with the frozen bytes. It then checks all input hashes.

From a published repository root, use:

```sh
python3 -I -B research/ordered-centre-interfaces/annexes/access-algebra/replay.py --out /tmp/ordered-access-algebra
```

Use Python 3.10 or later with the standard library. The output directory
must be new and outside the annex. Its parent must exist. Keep at least
3 GiB of disk space free and run one process at a time. The final line is:

```text
PASS_ORDERED_ACCESS_ALGEBRA_ANNEX
```

This review ran all three independent checkers in normal and optimized
Python. It did not rerun the producer dependency suites, native emitters,
recursive child implementations, full-cover map prices, finite precision,
or complete supplier calculation. The proof review supplies the scope
beyond the finite cases. It does not replace those open obligations.
