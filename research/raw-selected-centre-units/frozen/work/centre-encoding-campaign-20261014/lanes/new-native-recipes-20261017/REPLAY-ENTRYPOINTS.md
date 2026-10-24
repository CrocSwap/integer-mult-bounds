# Reproduce the balanced-word reviews without changing frozen files

Use these entrypoints for a new replay. Each requires a new receipt path
and a new adjacent input-manifest path. Existing output files are rejected
before the mathematical checks start.

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/replay_serial_balanced.py --out /tmp/centre-serial-balanced-rerun.json

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/replay_irregular_38.py --out /tmp/centre-irregular38-rerun.json

Expected final statuses are
`PASS_INDEPENDENT_SERIAL_BALANCED_LOCAL_WORDS` and
`PASS_INDEPENDENT_IRREGULAR_38_NATIVE_AND_RESPONSE_UNIT`.

These files retain the exact mathematical checks from the frozen
check_serial_balanced.py and check_irregular_38.py. They change only
argument parsing and receipt placement. Both new entrypoints were run.
After removal of the checker hash and elapsed time, each new receipt
equals its original frozen receipt exactly. Both input manifests are
also byte-equal to the frozen manifests. REPLAY-ENTRYPOINTS.json records
the source hashes and comparison results.

The original fixed-output scripts and their receipts remain frozen.
The new entrypoints do not modify them. The local review scope and all
unresolved global obligations are unchanged.

No PR, push, or publication commit was made. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
