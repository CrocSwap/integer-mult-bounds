# Local replay

Executed 2026-10-13 on Windows / Python 3.14.5, standard library only.
No solver, native compiler, package installation or environment change was
used. All subprocesses finish before commit; no background receipt writers
are left running.

```text
python -I -O -B research/r439-matching-neighborhood13/verify.py
PASS_MATCHING_NEIGHBORHOOD13 proposals=711624 words=857 admitted=0 controls=6

python -I -O -B research/r439-matching-neighborhood13/independent.py
PASS_INDEPENDENT13 words=857 complete_ADDs_replayed=10239436 admitted=0

python -I -O -B research/r439-matching-neighborhood13/test_package.py
PASS_PACKAGE13 relocated=1 controls=6
```

The main replay checks the original frozen-parent reconstruction and the
96,141-edge PR941 dual floor, preserves gain 1,260, verifies all 661 dirty
D columns for each candidate, and compares macro and literal bounds. The
independent engine uses a different complete-neighborhood enumeration and
set arithmetic, then reconstructs and prices every stream in both directions.
Its reported ADD count is per direction; COPY/ERASE events are also replayed.

Six mathematical controls reject overlapping helper pairs, omission of the
two paid helper gates, acceptance without the nine-stage guard, missing odd-set
dual prices, omitted final dirty-helper restoration, and a scope check that
would silently treat the frozen matched vertices as the whole helper set.
Six package controls reject a missing source-pin entry, changed builder,
altered selected snapshot, a float substituted for an integer, omitted expected
candidate and output overwrite. Relocated replay uses only the source closure
and package in a workspace-local path containing spaces, without Git/network.

`python -B scripts/verify_selected_result.py` verifies the unchanged selected
record in this frozen checkout (PR942, 1661960547713947/10^18). That does not
assert that PR942 remains current upstream: the documents separately record
the later PR1042 selection. The staged whitespace check is run before commit.
The Python launcher prints a harmless location diagnostic; successful exit
codes and complete summaries determine pass status.

No full repository suite, selected cold replay, native 5/9/11-stage execution,
hosted invoice, Linux/remote CI, proof-assistant or multiplication theorem
validation is claimed. No candidate is admitted or published as a supplier.
