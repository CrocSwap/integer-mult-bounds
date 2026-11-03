# Three-coset Hermitian bootstrap orders still cost 784

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped finite obstruction with a written coverage proof and
separate exact implementations. For the native multiplier 118 and line offset
81 on the fixed PG(2,16) minus matching test graph, each of eight three-queue
families has exact minimum bootstrap-order cost **784**. The three queues
may interleave arbitrarily; each of the eight masks independently chooses
point-first or line-first alternation inside each queue. They allow both
point and line orders to change.

This answers one precise part of Open next question 2 in
[Sudarsh Chaturvedi / Sudarsh3301's PR2956](https://github.com/CrocSwap/integer-mult-bounds/pull/2956).
Its two-sequence census is cited context, not replayed or audited here.
The new result rules out cost 783 in this three-coset branch. It supplies
no unrestricted Boot lower bound or new kappa.
[PROOF.md](PROOF.md) gives the exact queues, path bijection and recurrence.

The full integer checks cover all **49,027,896 phase/state pairs** and
**146,279,952 phase/arc pairs**. These are dynamic-programming counts, not
literal full orders individually enumerated. Eight reconstructed witnesses
have their permutation, queue membership and cost checked directly.
The separate checker reverses all queues and uses rolling slices with an
independently constructed neighbor-prefix table. The two implementations
are by the same contributor; independent human and formal proof-kernel
review are unclaimed.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pg16-three-coset-bootstrap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pg16-three-coset-bootstrap/independent.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pg16-three-coset-bootstrap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pg16-three-coset-bootstrap --check-source-history
```

Substitute a local CPython 3.12 path on another machine. Add `--orders` to
the first command to emit all eight complete attaining orders. Both programs
print generated receipts bound to all seven package-file hashes. They read
one authenticated graph input and write no files. Registered replay runs
both programs normally and with `-O`, with warnings treated as errors.

The primary also checks every literal shuffle in forty small graph/phase
domains and rejects invalid optimizer contracts. The reverse checker tests
its cost-reversal identity on three complete orders. The universal claim
about all merges inside each fixed family rests on the written path/recurrence
proof and the complete finite computation.

## Scope, sources and credit

Credit Sudarsh Chaturvedi / Sudarsh3301 #2956 for the graph data, two-sequence
family and explicit three-sequence question. Credit Philippe Van Velzen /
philippeVV's limits-1/limits-2 and
[Discussion2278](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278)
for the bootstrap problem, native cyclic order, cost definition and Hermitian
context. Dynamic programming and regular-graph reversal are classical. No
literature-priority claim is intended. Predecessor source and credit lines
are unchanged; [SOURCES.json](SOURCES.json) pins exact provenance and graph bytes.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The complex-new-helper-inventory card explicitly changes to
this Hermitian bit-side scheduling side result. The selected binding-only
example passed. Live open/account PRs, the 472 account PRs returned by the
creation-date search from October 27 onward, current claims, source/author reservations, cached
body searches and main/merged general-form searches were inspected. No
matching three-queue result was found in that coverage. Arbitrary historical
diffs and unpublished work remain unknown.

The source describes q=16 as a test instance already below its target
Hermitian rate, with q=64 the more consequential instance. The imported
code dimension 772 is not recertified here. This result does not change the
known unrestricted Boot interval, certify back-arc flow feasibility, or
supply a physical/native/restored caller, complete paid/target invoice,
compiler, precision/storage/tape proof or selected frontier. All five
framework assumptions remain. No selected cold replay, Lean or Docker build
was run. Hosted CI is separate evidence, recorded in the PR body.

## Open next questions

Structured first steps and blockers are in [TASK.json](TASK.json).

- Can a stated queue contract that allows internal point/line reorderings
  escape this 784 obstruction? First identify an order outside the eight
  families and its complete objective. Repeating the same families cannot
  improve the result.
- Can the q=64 Hermitian candidate supply a source-bound graph, code dimension
  and affordable causal order with feasible back-arc flow? Those inputs and
  its complete native/caller invoice are missing here. The q=16 equality
  does not transfer to that graph.

## Verifier bounds

Every loop has a fixed finite bound from at most three queues, 546 vertices,
182 entries per queue, eight phases and the explicit forty tiny controls.
Functions are under sixty physical lines. The primary distance array has
6,128,487 unsigned-short entries; the oracle keeps two 33,489-entry slices.
Prefix counts use 299,754 bytes of numeric array payload per implementation.
Python object overhead and the interpreter are additional. Input text and
each receipt source are limited to 128 KiB. No recursion, subprocess, network,
solver, generated code, output file or third-party dependency is used.

Power-of-ten rule 3 deviation: CPython allocates managed containers and
integers while evaluating a bounded one-shot certificate. Fixed input,
table, phase and file bounds constrain live state. Normal and optimized
warning-strict execution checks these bounds. A fixed-allocation backend
would be required for a production embedded implementation, which is not
proposed. Iterator combinators have finite explicit input collections;
there is no application callback or dynamic call target in the verifier.
