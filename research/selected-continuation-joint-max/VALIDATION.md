# Validation and engineering limits

Local environment: macOS arm64, uv-managed CPython 3.12.15 and Homebrew CPython
3.14.8. Standard library only. Registered normal/optimized Python 3.12 replay
passes the complete receipt and all nine tests. Optimized Python 3.14 matches
the receipt and passes the same nine tests. Ruff 0.17.1 diagnostics and format
checks pass. The longest new function is `execute`, 59 physical lines.

```sh
uv run --python 3.12 --no-project python -I -Werror -B scripts/research_package.py --package research/selected-continuation-joint-max
/opt/homebrew/bin/python3.14 -I -O -Werror -B research/selected-continuation-joint-max/verify.py
uvx ruff check --select E4,E7,E9,F,I,UP,B,RUF research/selected-continuation-joint-max
uvx ruff format --check research/selected-continuation-joint-max
uv run --python 3.12 --no-project python scripts/check_research_commit.py --package research/selected-continuation-joint-max
```

The new checker independently computes the per-level array recurrence and
observes unchanged literal Tape.write/Stack.pop/Callback.weight operations.
It reuses authenticated PR2758 fixture construction and arithmetic checks.
It does not independently implement the numerical matrix algorithm. A separate
internal source derivation checked the joint induction, found the required
history restriction and supplied the nonuniform-tree counterexample. This is
internal review with automated assistance, not independent human review or a
formal-kernel proof.

Build the Lever shaped the rerunnable exact-length checker. Prove It Works
shaped the attaining lengths and pre-growth one-cell-short rejection. Test
Behavior, Not Implementation shaped the returned-coefficient, warm-history
and cleanup tests. No production source, frozen package or selected frontier
is changed. The selected cold replay is unrelated to this scoped package and
was not rerun. Hosted CI and full selected GL64 payload execution are separate.

## Power of Ten inspection

The new call graph has no recursion. The symbolic envelope evaluates constant
arithmetic with bounded tool inputs; the exact mode recurrence has at most six
iterations. The census has 518 cases plus twelve attaining stress cases,
three literal fixtures and fixed controls. Source authentication reads exactly
eight inputs, each at most one million bytes. Four tapes have fixed identities;
warm input lengths are at most 1024. Fixture index widths are at most 38 and
residue widths at most 128. Every quota is checked before a growing write.
All rejection checks use explicit exceptions and remain active under -O.

External input checks, record-length invariants and exact final lengths enforce
the contracts. SHA256/Git-blob checks precede dynamic source compilation.
Temporary observers and fixture replacements restore in finally blocks and
on failed context entry. Tests exercise both paths. No source/receipt writing
occurs during normal replay. New functions are checked against the roughly
60-line review ceiling after formatting. Scoped Ruff diagnostics and -Werror
run on the new code. Frozen predecessor code is authenticated, not rewritten.

Rule 3 deviation: CPython integers, tuples and bytearrays allocate dynamically,
so a static no-allocation steady phase cannot describe this checker. Scope is
the fixed finite census above. Bounded fixture dimensions, four observed tape
identities, exact per-tape quotas and command timeouts constrain the experiment.
The numerical fixture's managed allocations and allocator capacity are not a
physical reserve proof. A physical caller would need a separate fixed-capacity
implementation and lifetime certificate.

Rules 8/9 deviation: observing unchanged source requires authenticated dynamic
compilation and temporary Tape.write/Stack.pop/fixture callback dispatch. The
closed dependency inventory fixes every executable target, and tests verify
restoration after success and both failure phases. A source change invalidates
the pins and requires re-review. Removing this observation would defeat the
independent unchanged-source check; production compilation remains separate.

Rule 2 inherited-source boundary: frozen tape arithmetic contains data-dependent
loops. The fixture widths, modes and extents bound their inputs, and registered
commands have 120-second timeouts. The proof explicitly assumes successful
source calls; this package does not prove their general arithmetic termination
or failure cleanup. A whole physical implementation must discharge that source
obligation rather than infer it from these finite replays.
