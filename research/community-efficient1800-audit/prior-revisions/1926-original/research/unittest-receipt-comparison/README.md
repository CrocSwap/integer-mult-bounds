# Preserve unittest diagnostics when comparing benchmark receipts

**Verifier engineering; no new kappa or speedup claim.** The integrated PR921
benchmark can accept changed stderr as identical after timing normalization.
This package reproduces two collisions and supplies an opt-in repair without
changing the frozen benchmark or the isolated test runner.

## Result and scope

The object is `research/agent-07-verifeng-seed88/benchmark.py` at main
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Its `normalize()` applies
`in \d+\.\d+s` everywhere in stderr, after decoding with `errors='replace'`.
Consequently:

- `AssertionError: invoice in 1.000s` and `... in 2.000s` become equal even
  though this is a failure diagnostic rather than the final wall-clock field.
- Distinct captured bytes `ff` and `fe` become the same replacement character.
  Test processes may write bytes directly, including subprocess diagnostics.

Both cases reproduce with real `python -m unittest` captures. In an additional
bounded integration control, the unchanged benchmark actually reports PASS
when a fault changes either diagnostic between its sequential and concurrent
captures. The adapter rejects both faults. These are counterexamples to the
comparison's coverage, not evidence that any historical measured run contained
such a fault. Exit codes and raw stdout comparisons are still required.

[RESULT.json](RESULT.json) stores the two complete byte witnesses and hashes,
source pins and the 20-test replay count. [TASK.json](TASK.json) records the
portable-replay selection, refined scope, overlap coverage and remaining work.
Source Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json). The
selected record and catalogue are historical provenance; the three explicit
predecessor inputs are live and must still match their immutable pins.

## Comparison contract

`comparison.py` operates on bytes. It recognizes only a final standard unittest
trailer: a 70-hyphen separator, the canonical singular/plural `Ran N test(s)`
line with a three-decimal elapsed value, a blank line and an `OK` or `FAILED`
status line. It retains LF versus CRLF, counts, result details and all other
bytes. Unrecognized/custom output receives an exact raw comparison key.
Only the numeric elapsed value in that final trailer may differ; timing-shaped
text elsewhere, including an earlier complete summary, remains substantive.

The key uses distinct `raw\0` and `summary\0` tags. A summary key stores the
prefix length in eight bytes, then the original prefix and suffix around the
elapsed value. Thus equality of two summary keys implies equality of both
retained slices: the stored length fixes their boundary. Equality of raw keys
implies exact byte equality. The disjoint tags prevent a raw literal marker
from colliding with a recognized summary. This avoids the ambiguity of simply
substituting a printable timing marker.

This is a syntactic contract for captured unittest output, not authentication
of who produced it. A producer can fabricate a final summary; this comparator
does not certify execution or test correctness. Custom output may conservatively
fail equivalence when its timing varies. The benchmark retains its original
SHA256-based comparisons, failure-set reporting and rejection of every remaining
mismatch, including nondeterministic mismatches. SHA256 collision resistance is
the inherited hashing assumption.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/unittest-receipt-comparison --check-only
python3.12 -B scripts/research_package.py --package research/unittest-receipt-comparison
```

The registered replay checks the complete deterministic receipt in normal and
optimized Python modes. Direct commands are:

```sh
python3 -B research/unittest-receipt-comparison/verify.py
python3 -O -B research/unittest-receipt-comparison/verify.py
python3 -B research/unittest-receipt-comparison/test_comparison.py -v
```

Expected verifier line: `PASS_UNITTEST_RECEIPT_COMPARISON collisions=2 tests=20`.
The tests cover real passing/failing captures, genuine timing-only acceptance,
all 256 diagnostic byte values, each nontiming byte of a full fixture, fake
earlier summaries, unknown trailers, marker collisions, LF/CRLF, singular/plural
counts, retained result details and altered stdout/exit-code/count/status faults.
Changed predecessor inputs and a missing input pin are rejected before loading.
Integration tests use two tiny modules, real child captures and deliberate
post-capture faults; they do not rerun the repository suite.

To use the strict comparator with the predecessor's **entire** benchmark:

```sh
python3 -B research/unittest-receipt-comparison/adapter.py --workers 4 --output /tmp/fresh-benchmark.json
```

Use a fresh output path appropriate to your platform. The adapter admits the
exact pinned benchmark and runner, replaces only the stderr comparison function,
and records `stderr_comparison_policy=unittest-final-elapsed-bytes-v1` in each
module's receipt. Commands, discovered module inventory, scheduling and stdout
hashing remain those of the predecessor. This all-module benchmark was not run
for this contribution; no new performance measurement or suite-wide PASS is
claimed. Source drift intentionally requires a new reviewed pin before reuse.
The selected construction and its mathematical replay are outside this scope.

## Open next questions

Run the adapter on the full suite in a supported replay environment and identify
any custom stderr trailers that conservatively fail comparison. That would
establish practical compatibility beyond the small integration fixtures. Start
with the exact pinned command above, retain raw per-module captures when
investigating a mismatch, and allow a new trailer only after demonstrating that
its removed field is solely elapsed time. Full-suite dependencies and runtime
are the blocker; additional formats must not relax diagnostic byte equality.
The structured version is in [TASK.json](TASK.json).

## Credit

Aaron Wang / navinor supplied PR921's concurrent isolated-test scheduling and
benchmark (reviewed submitted head `c1ee2fbfdc5700a1ba0251e7727ee8ae0cb4782f`).
Douglas Colkitt's [batch932 review](../../docs/research/community-batch932-review.md)
already hardened acceptance against nondeterministic mismatches; this successor
addresses two remaining normalization collisions in that integrated version.
Related PR1852 protects child assertions and addresses a separate obligation.
Prepared by Arham Tahir with substantial OpenAI Codex assistance in the audit,
implementation, tests and writing. No subagents or independent human review.
Apache-2.0, with the repository and predecessor licenses retained.
