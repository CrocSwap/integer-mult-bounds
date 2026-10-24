# Unicode arguments in Windows replay launchers

The Windows replay wrappers could reject a valid verifier command before it
started. Their JSON transports used the default ASCII escaping: one Greek
character became six command-line characters, and one supplementary Unicode
character became twelve. A native command with 6,000 Greek kappa characters
succeeded directly but failed through the registered replay gate with
`FileNotFoundError: [WinError 206]`.

Both `research_package.run_windows_command` and
`run_isolated_tests.windows_module_command` now serialize their argument lists
with `ensure_ascii=False`. Their existing `json.loads` consumers reconstruct
the same arguments. Windows already accepts a Unicode command line; the change
removes this extra expansion at both layers. Job assignment, isolated startup,
bytecode isolation, deadlines, completion receipts and cleanup are unchanged.

This is a portability repair. It neither changes a mathematical certificate
nor proposes a new selected exponent.

## Reproduction and evidence

Initial canonical base: `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`.
Publication base: `5948b8770d5f6df94d70a9f8ec6c0759586f592c`.
The refresh incorporated PR5017's worker scheduling repair; the branch was
rebased and the new tests and isolated-runner suite were rerun. The selected
record, priorities and registered Job Object implementation were unchanged.
Environment: Windows 11 build 10.0.26300, AMD64, CPython 3.12.0
(`MSC v.1935 64 bit`), Git 2.47.1.windows.1. No third-party dependencies.

For the small diagnostic command
`python -I -S -c 'import sys; print(len(sys.argv[1]))' ARG`, the measured
Windows command lengths were:

| ARG | Direct | Original gate | Repaired gate |
|---|---:|---:|---:|
| 6,000 Greek kappa characters | 6,072 | 37,064 | 7,064 |
| 3,500 grinning-face characters | 7,072 | 43,064 | 8,064 |

Lengths include Windows argument quoting, UTF-16 surrogate pairs and the
terminating NUL. The executable path affects the fixed overhead.
[CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)
limits the command line to 32,767 characters including NUL.
[Python's JSON documentation](https://docs.python.org/3.12/library/json.html#json.dumps)
specifies the default escaping and its `ensure_ascii=False` alternative.

The regression module runs every fixture directly first, confirms its exact
argument vector in a file, removes that receipt, and then requires the same
receipt through the actual registered replay path or isolated supervisor.
The tests cover BMP and supplementary characters, empty arguments, spaces,
quotes, backslashes, tabs/newlines, distinct combining/precomposed strings,
literal Unicode escape text, unpaired UTF-16 surrogates, and exit status 7.
The nonzero command must still fail the registered replay.

```sh
python -W error -B -m unittest discover -s tests -p test_research_windows_unicode_argv.py -v
python -O -W error -B -m unittest discover -s tests -p test_research_windows_unicode_argv.py -v
python -W error -B -m unittest discover -s tests -p test_research_windows_job.py -v
python -B -m unittest discover -s tests -p 'test_isolated_test_*.py' -v
```

| Check | Observed result |
|---|---|
| New regression against unchanged base scripts | Six error outcomes across five methods; short mixed arguments pass. Every error is WinError 206; 1.572 s. |
| New regression after rebase | Six pass, zero skips; 3.589 s. |
| New regression with optimized outer interpreter after rebase | Six pass, zero skips; 3.504 s. |
| Existing native Job Object suite | Eight pass, zero skips; 6.874 s. |
| Existing isolated-runner suite after rebase | 50 methods: 42 pass, eight Linux-only skips; 62.683 s. |

The newly incorporated `test_research_worker_failure_order.py` was checked
separately: one pass, six POSIX-only skips, and one existing Windows newline
assertion failure at line 69 (`b'earlier module completed\r\n'` versus `b'earlier
module completed\n'`). The same failure reproduces with all six fixture/import
files exported byte-for-byte from unchanged publication main; no Unicode
repair is present in that control. The fixture's expected output remains
unchanged in this PR. This is not a green claim for every Windows test.

Two private-copy mutation runs separately restore ASCII escaping in each
production file, with the other repair retained. Under the optimized outer
interpreter, restoring the inner gate yields three failures and three errors;
restoring the outer supervisor yields three errors. Each restores the native
WinError 206 failure. The same six regression methods check the complete
argument vector rather than accepting a shorter or truncated command.

The existing lifetime suite still detects parent-only cleanup mutants and
checks normal exit, failure, timeout, interruption, assignment refusal and
startup-hook isolation. The isolated-runner suite also covers receipt failures,
bytecode isolation, cancellation, queued deadlines and captured output. These
are bounded regression checks; the durations are not a performance benchmark.
`-O` applies to the outer test interpreter, while descendants retain their
explicit original interpreter options.

## Task, overlap and attribution

Task `portable-replay`, scope status **refined** to this reproducible native
environment failure. The task picker selected verifier engineering with nonce
`b7847175b3ee9e8ce9f110910afc833a`, priority revision 7. The selected-source
orientation passed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is not an operator
or supplier replay. Success was exact native argv transport with existing
ownership checks retained; the stopping point is this two-site repair.

[Canonical claim and completion record](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-19140347).
Entry overlap covered all 6,710 tracked in-scope local notes, 325 open PRs
at 2026-10-23 07:06:54 UTC, and 4,146 Discussion records at 07:08:15 UTC,
with complete reported pagination. Focused Unicode/JSON/argv searches found
no same-scope implementation. The sparse-baseline pathspec batching and
PR5017's worker-exception handling concern different boundaries. These searches
do not cover arbitrary diffs, every nested source or unpublished work.

The submission refresh searched 303 open PRs at 07:15:17 UTC and 4,152
Discussion records at 07:16:44 UTC, with complete pagination and no warnings.
After rebase, the local search covered all 6,754 tracked in-scope notes at
07:19:02 UTC. The focused Unicode/JSON query found only this claim. An AST
comparison against publication main confirms the two serialization options
are the only executable changes in the production scripts.

Credit ywz65's gated Job Object implementation and startup isolation,
Mihir Srivastava's isolated Windows supervisor, Nick Petalas and Paul Romeo's
lifetime checks, Aaron Wang/navinor's scheduler, Douglas Colkitt, and the
retained runner/bytecode contributors. Their original source attribution and
frozen evidence remain intact. Prepared for Mihir Srivastava (@mihir-s-05)
with substantial OpenAI Codex assistance, one agent; Apache-2.0.

## Open next questions and limits

This removes avoidable non-ASCII escaping; it does not make every command
that barely fits a direct launch fit inside a wrapper. Wrapper source, paths,
JSON syntax and quote/backslash escaping still consume the operating-system
budget. If an actual replay hits that remaining boundary, the next useful
step is a bounded transport through a private file or pipe, preserving the
ownership gate, exact arguments and cleanup. No new transport is justified by
this repair alone.

The native test module intentionally skips non-Windows hosts. No new macOS,
Linux, newer-Python, archive-wide, Lean, Docker, full selected cold replay or
independent human review is claimed. Shared-runner changes can select many
registered packages in hosted CI; the focused local regression results above
are not a claim that every historical package was replayed. Existing immutable
source pins have not been weakened or repinned. The selected frontier remains
`60403/20000000`.
