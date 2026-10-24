# Windows closed-stdin errors in source-pin verification

The Git blob reader now recognizes Windows `EINVAL` from a closed child stdin
at both request writing and cleanup. This lets the existing older-Git fallback
run when its unsupported-option probe exits before the first request. The retry
still requires the first NUL-mode request, an absent response and exit status
129. Other OS errors, non-129 exits and failures after a valid response still
reject; a failing legacy reader cannot start a third process.

This is a shared-tool portability repair. It changes no source hashes, frozen
research packages, supplier claims or selected frontier.

## Reproduced failure and repair

Base: canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.
The base reader's Git blob is `ad2f94e3d38c3167feb66b07cbe6c52192284d39`;
the unchanged compatibility tests' blob is
`4e6a4c66a4945a718446c34db387a013e98e780e`.

On native Windows with CPython 3.12.0 and Git 2.47.1.windows.1:

```sh
python -W error -B tests/test_research_git_compatibility.py -v
```

The original `test_option_rejection_before_first_write_handles_broken_pipe`
raises `OSError: [Errno 22] Invalid argument` at `process.stdin.flush()`, then
again at `process.stdin.close()`. The module reports eight passes, one error
and one existing CR/LF-path skip. Its fixture waits for an actual process to
exit 129, then attempts the write; real Git serves the fallback objects.

The reader caught only `BrokenPipeError`. CPython itself handles this Windows
closed-pipe behavior in
[`Popen._stdin_write`](https://github.com/python/cpython/blob/v3.12.0/Lib/subprocess.py).
The new classifier accepts `BrokenPipeError` everywhere and `errno.EINVAL`
only when `os.name == "nt"`. It classifies a pipe error, not a successful
verification or permission to retry. The existing exit/response gate,
one-pass input iterator, exact object and byte checks, and cleanup remain.

## Verification

The six new tests in `tests/test_research_git_pipe_errors.py` inject errors at
write, flush and close around real exited subprocesses. Actual Git supplies
every successful fallback payload. They check binary/empty/duplicate objects,
independent blob IDs, iterator consumption, process counts, closed streams and
reaped children. Controls cover EPIPE on both platform branches, POSIX EINVAL,
unrelated EIO, exit statuses 0/7, a failure after a valid blob and a failed
legacy reader. Only the module's platform view is injected; the host's OS and
subprocess module retain their actual behavior.

The final six-test suite against an exact byte copy of the base reader fails with
eight error subcases. With the repair they pass normally and under `-O`.

| Environment | Modules | Result in each of normal and optimized runs |
|---|---|---|
| Native Windows, CPython 3.12.0, Git 2.47.1.windows.1 | Six modules below | 51 passed, one existing CR/LF-path skip |
| Ubuntu under WSL, CPython 3.12.3, Git 2.43.0 | First three modules below | 23 passed, no skips |

Every run used `-W error -B`. From the repository root:

```sh
python3 -W error -B tests/test_research_git_batch.py -v
python3 -W error -B tests/test_research_git_compatibility.py -v
python3 -W error -B tests/test_research_git_pipe_errors.py -v
python3 -W error -B tests/test_research_git_replacements.py -v
python3 -W error -B tests/test_research_commit_bytes.py -v
python3 -W error -B tests/test_research_source_history.py -v
```

Repeat with `-O` to reproduce the optimized checks. The latter three modules
retain replacement-ref, source-history and committed-byte rejection coverage.
`git diff --check` also passes. These are local results; hosted CI is separate.

The unchanged registered `research/git-batch-compatibility` hook passes on
Ubuntu under WSL: metadata/source pins and all 38 currently discovered
Git-reader tests, including the new tests. Reproduce with:

```sh
python3 -W error -B scripts/research_package.py --package research/git-batch-compatibility
```

The repository planner selects all 2,480 registered packages because this is
a shared runner change. That selection was checked; those scientific replays
were not run locally. The planner's coverage policy is unchanged.

An old Git binary was not installed for this repair. Unsupported-option exit
129 is simulated, as in the predecessor tests; native Windows pipe behavior
and successful Git blob reads are real. The original CR/LF fixture remains
skipped on Windows and passes under Linux. An initial broader Windows onboarding
run encountered unrelated existing fixture errors and was stopped; no complete
onboarding or selected scientific replay pass is claimed. The sparse selected
baseline also stopped on an absent input, before verifying its closure.

## Scope, overlap and credit

This follows the `portable-replay` card from verifier-engineering picker seed
`f65c1c7a783342c01e342be2f39f11a8`, priority revision 7. Scope is **changed**
from canonical regenerated-payload comparison to an observed Windows failure
in immutable-source verification. The bounded question is whether the existing
compatibility retry can recover without broadening its admission conditions.
The stop rule is that boundary's repair and regression evidence, not a wider
runner rewrite. Coordination is in
[Discussion #4681](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681).

The canonical main refresh before submission remained at the base above.
A refreshed overlap scan covered 450 open PRs and 3,612 Discussion records
with complete remote pagination. The local follow-up searched all 5,860 tracked
in-scope notes (package README/TASK files and the PR ledger). Exact error/path
searches found this claim and no competing repair. Arbitrary diffs, closed remote PRs and unpublished
work are not covered. The adjacent #4579/#4679 work repairs exporter fixtures;
the active isolated-runner Windows lifetime task in #1472 owns a different
launcher. None is claimed here.

Nick Petalas's [PR2752](https://github.com/CrocSwap/integer-mult-bounds/pull/2752),
head `73406fd73ebaf8361b51674fad5e0b02a26db075`, supplies the fallback and its
original tests. Its retained package explicitly left Windows untested.
Douglas Colkitt supplied the runner's contracts, Arham Tahir the NUL pin
batching, and Woklerx the streamed-reader/cleanup lineage. Maxime Fleury's
reproducibility distinction and the original P104/Abhinav Ramachandran reports
retain their predecessor credit. Prepared for Mihir Srivastava with substantial
OpenAI Codex assistance, one agent. Apache-2.0.

## Open next questions

An actual older Git for Windows run would complement the controlled rejection
test. First put that binary on the PATH of a disposable local fixture and run
the three Git-reader modules; the missing prerequisite here is that binary.
This repair does not address synchronous pipe-read deadlines or establish
compatibility with every Git/Python version. A separate reported failure is
needed before expanding the work.
