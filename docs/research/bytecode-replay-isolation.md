# Registered replay: source hashes and bytecode caches

A verifier can authenticate the expected `.py` bytes and still execute different
code from an existing `.pyc`. In an isolated copy of the retained P104 native
channel, `python -I -O -B verify.py` accepts the unchanged interpreter source
SHA256, then executes a harmless sentinel from a matching timestamp cache.
The sentinel raises an error; no incorrect mathematical result is claimed.
The clean replay passes. Giving the same command a fresh cache namespace also
passes, with its complete mathematical receipt unchanged.

The source under test is
`research/p104-native-channel/vendor/native_verify.py`, SHA256
`3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38`,
from canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
The source bytes remain unchanged throughout the final replay. The test creates
and alters files only in temporary copies; frozen packages are not patched.

## Why the old invocation was insufficient

Python's `-B` option prevents writing bytecode caches; it does not prohibit
reading an existing valid cache. A timestamp cache records modification time
at second resolution and source length. A same-length edit with that timestamp
can leave it apparently valid after the source bytes are restored. An unchecked
hash cache is a second independently tested case. A checked-hash cache with
different source bytes is already rejected by Python and is retained as a
positive boundary control.

This is a source-execution boundary, not a new P104 construction or a failure
of its clean mathematical receipt. Source hashes still detect changed source
files. They do not authenticate an unrelated compiled cache selected by the
default import loader.

## Runner behavior

For each `{python}` verification command, `scripts/research_package.py` creates
an empty private directory and adds `-X pycache_prefix=<directory>` before the
script, `-m` module or `-c` command entry point. It removes the directory after
the command returns, fails or times out. Separate commands get separate paths.
The general subprocess helper and dependency-install command are unchanged.

Earlier interpreter-level `pycache_prefix` settings are removed explicitly.
Appending another setting is insufficient on the tested CPython 3.12.14:
`sys.pycache_prefix` uses the first duplicate value while `sys._xoptions` reports
the last. The tests reproduce that precedence with actual contaminated caches.
The runner preserves normal, `-O`, `-OO`, combined short options, warnings,
hash-cache validation options, `-m`/`-c` forms and script arguments. A script
argument spelled `-X` is not treated as an interpreter option.

Inherited environment cache prefixes are overridden for the registered command
without changing the parent environment. The existing `PYTHONOPTIMIZE` cleanup
is retained. The namespace is enforced for registered Python commands only;
arbitrary non-Python commands are not silently rewritten.

## Reproduce

The focused tests use public `py_compile` APIs to compile changed scratch source,
then restore its exact bytes and timestamp before the source-authenticating
fixture runs. They check both the observed old failure and the new behavior.

```sh
python3.12 -B tests/test_research_bytecode_isolation.py
python3.12 -O -B tests/test_research_bytecode_isolation.py
python3.12 -B tests/test_research_bytecode_isolation.py --p104-probe
python3.12 -B -m unittest discover -s tests -p 'test_research_*.py'
```

The slower `--p104-probe` runs the actual retained clean native replay, installs
the sentinel timestamp cache in its temporary vendor directory, observes the
old invocation fail with that sentinel, then checks that the isolated invocation
returns the identical complete receipt. It compares every copied original file
hash afterward, records those hashes and the receipt digest, and confirms `-B`
left the private namespace without generated `.pyc` files. It needs the checkout
files but no network or Git command. The ordinary focused tests are small and
do not rerun the P104 mathematics.

Controls cover timestamp and unchecked-hash caches in normal/optimized modes,
checked-hash invalidation, explicit and environment-selected cache prefixes,
entry-point placement, original script arguments, fresh per-command directories,
unchanged source hashes, changed-source refusal, and cleanup after nonzero exit
and timeout. The original P104 receipt remains a source-bound inherited check;
its Gaussian interpreter is not independently reimplemented here.

Local validation used CPython 3.12.14: the eight focused tests passed normally
and under `-O`; the research test discovery passed 73 tests with three
Linux-only skips; and the actual P104 probe returned the original receipt
SHA256 `c9681a03d9a752b5b387250f841e43f7333b9984a325c4f37166e03f11676eb5`.
A separate Codex reviewer ran all eight focused tests on native CPython 3.14.5
under `-I -O -B` and reviewed the runner boundary. This does not extend the
registered package runtime requirement beyond Python 3.12. No hosted CI or
selected-frontier cold replay is claimed.

## Scope and open next questions

This protects the default cache namespace of the registered interpreter.
Direct calls, standalone `.pyc` execution, custom loaders and separately launched
child interpreters are outside it. A verifier spawning Python must explicitly
forward the cache policy or use the wrapper for that child. It is not a sandbox
against hostile verifier code, a file-mutation race solution, or a replacement
for complete source provenance and meaningful mathematical checks.

The next useful audit is a named registered verifier that delegates source-bound
checks to Python subprocesses: identify those child calls and propagate a fresh
namespace at their actual execution boundary. Do not infer process-tree coverage
from a protected parent. No such child-call census or fix is claimed here.

This is round006's evidence-driven pivot from P104 interface research to
`portable-replay`, priority revision 4, picker nonce
`5be9ea8a295e13a739b8817d39aec470`. Canonical main was fetched at round start
and again before the pivot, unchanged at 2026-10-15 13:45:26 UTC. The initial
P104 picker and partial investigation were preserved outside the checkout.
The pre-submission fetch at 14:03:52 UTC was unchanged; the newest 100 open
PRs and the source PR's comments were checked again via REST at that checkpoint.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2522#issuecomment-6193623013)
records the bounded scope. Overlap used complete cached 679-PR and 1,197
Discussion/comment/reply snapshots through 12:25/12:29 UTC plus the 100 newest
open PRs and targeted source comments via REST; complete current Discussion
coverage was unavailable due to quota. No relevant prior bytecode fix was found,
which is not a novelty guarantee. PR2506's matrix-product cache is a different
optimization and is not modified or relied upon here.

Prepared for **ywz65** with substantial OpenAI Codex assistance in diagnosis,
implementation, tests and writing. Credit the existing runner authors, Rohan
Arun / PR1972, Chafik Boukhalfa / PR1991, Ali Romman / PR1862 and retained
native/compiler contributors for the unchanged replay and its mathematics.
Apache-2.0. No new theorem, supplier, kappa, selected-frontier change, independent
human review or proof-assistant verification is claimed.
