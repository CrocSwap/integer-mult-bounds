# Faster complete member-bank census through exact containment reuse

This contribution was produced by Nick Petalas. Apache-2.0.

A bounded cache lowers the local median time of ToikY's complete PR6396
independent census from **4.2855 seconds to 3.8666 seconds**, a **9.78%**
reduction over five alternating fresh-process pairs. Every pair improves.
All ten processes return the exact original success output without errors.
The complete scientific receipt and its checks remain unchanged.

Claim type: scoped implementation-equivalence proof, exact finite
conformance and a local performance observation. No new kappa, admission
or selected-frontier change follows.

## Change and evidence

The source is [PR6396](https://github.com/CrocSwap/integer-mult-bounds/pull/6396)
at `2a5bc94df6d741b49afbadd36d96eb2aea0f6f1f`. Its mathematical result is a
credited premise. The new result is a cheaper equivalent execution of one
complete census command, not a new audit of that result.

[PROFILE.json](PROFILE.json) records a separate profile of that command.
Rational containment takes 3.363 of 12.013 profiled seconds, about 28%.
The adapter retains the original containment predicate and caches its Boolean
result by the complete ordered pair of immutable rational spaces. It avoids
11,194 of 14,788 predicate evaluations and retains 3,594 entries. The hard
capacity is 32,768; an uncached miss after capacity exhaustion still evaluates
the original predicate.

[PROOF.md](PROOF.md) proves equivalence under the source's pure-predicate
and immutable-space contract. The census class, event loop, geometry,
elimination, direct checkpoint checks and receipt construction retain their
original bytes. Every current context still participates. The original
comparison against `FULL-CENSUS.json` remains active, and `--emit` returns
the same canonical scientific object. This does not reuse a previous
context's rank result as a substitute for evaluating a new context.

The new checker includes 432 ordered positive/negative containment
comparisons at capacities zero, one, two and 32,768. Four invalid capacities
and two actual wrong-result implementation mutants reject. The separate CLI
controls run normal and optimized replay after Git-free relocation with
empty PATH and read-only source files. Changed frozen bytes, a changed
source manifest and a removed cache installation reject.

## Complete-command measurement

[BENCHMARK.json](BENCHMARK.json) binds the benchmark and adapter bytes and
contains every process result. Both sides run the same CPython 3.12.15 with
isolated mode, bytecode writes disabled and warnings treated as errors.
The timer includes process startup, all current census work, checks,
receipt comparison, output capture and exit. The new side also authenticates
all seventeen frozen files. Output validation follows the timer.

| Complete command | Median seconds | Observed range |
| --- | ---: | ---: |
| Original source | 4.2855 | 4.1155 to 4.8022 |
| Cached adapter | 3.8666 | 3.6853 to 4.1152 |

These are five serial alternating pairs on one shared macOS arm64 host,
with warm filesystem cache. Startup and the remainder of the census still
cost time; containment accounts for only part of the complete command.
Profiler overhead prevents comparing its absolute times with the unprofiled
benchmark. The measurements give no cross-host speed guarantee or claim of
an optimal cache policy. No further optimization followed the first gain.

## Reproduce

From the repository root, using the supplied interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/g20-member-bank-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/g20-member-bank-cache/verify.py
TMPDIR=/absolute/private/run /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/g20-member-bank-cache/test_controls.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/g20-member-bank-cache
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/g20-member-bank-cache --check-source-history --check-modes
```

Create the private external temporary directory before using it. Substitute
an existing CPython 3.12 path on another host. `verify.py` emits
`PASS_G20_MEMBER_BANK_CACHE`, actual cache statistics, the scientific digest
and hashes of every package file. `test_controls.py` emits
`PASS_G20_CACHE_CLI_CONTROLS`. The registered runner must print
`PASS_REGISTERED_RESEARCH_PACKAGE`.

For the optimized complete caller alone, run `replay.py`. Its `--emit` option
prints the complete canonical source result; `--stats` reports cache counts
on stderr. Normal replay writes no files. To repeat the local measurement,
run `benchmark.py --pairs 5` and redirect its JSON outside the checkout.
The benchmark is deliberately outside registered CI checks; timing is noisy
on a shared runner.

[FROZEN.json](FROZEN.json) binds seventeen necessary source files by SHA256
and Git blob ID, with the exact repository, commit, path and tree. Their
bytes and modes were compared with the public source tree. They are retained
unchanged in `frozen/`, including the source notices. This self-contained
committed export makes the pending source available without relying on
foreign objects in a local Git cache. [SOURCES.json](SOURCES.json) separately
binds the main-branch catalogue and selected record as historical provenance.
Its source-history check covers those declared pins; the external origin is
recorded in the frozen export manifest.

## Scope and limitations

This refines the current `replay-runtime` card. The base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. The selected
metadata baseline passed before work. Live open and recent account PRs,
handoffs, active Discussions, local reservations, merged searches and main
README terms were checked before the
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360872).
The overlap cache covered 355 open PRs and 6,261 Discussion records, with
complete reported remote pagination. Only 101 of 8,917 main note paths were
materialized locally; separate Git searches covered the named object.
Unpublished work, arbitrary diffs and omitted historical notes remain limits.

This changes one isolated opt-in package. It does not change the source
default, typed word, targets, paid bill, native implementation, physical
restoration, compiler, ordinary supplier or outer bound. All five framework
assumptions retain their status. The other seven PR6396 registered commands,
the selected supplier cold replay, Lean and Docker are outside this cost
result and were not run. No independent human or formal proof-kernel review
is claimed. Engineering bounds and managed-runtime deviations are in the
proof. Hosted CI status belongs in the PR body.

## Open next questions

Should a future version of the original census adopt this bounded cache?
Bind one exact new source head and its immutable-space and pure-predicate
contract, then preserve the complete receipt and failure controls. This
isolated adapter does not cover a changed geometry or a stateful predicate.
No adoption or further optimization is reserved. The question is structured
in [TASK.json](TASK.json).

## Credit

Credit ToikY for PR6396's census, independent oracle and complete coverage
contract; Ali Romman for PR5679/5708; unpaidmoon for the bank-gap handoff;
Nick Petalas for PR5983/5609; and Dugongue, ai-nanachi, compact436, Cinna
Davis, DreamingOfClouds, eumemic, rohanarun, zxv, Jacob Alan Sussman and the
full lineage in the unchanged frozen notices and source README. Memoization
is classical. The new contribution is this bounded source-specific adapter,
its equivalence and failure controls, and its complete-command measurement.
