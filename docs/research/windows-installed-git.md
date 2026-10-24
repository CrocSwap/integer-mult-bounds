# Actual older Git for Windows reader checks

The shared source reader passes the previously unrun older-Git Windows boundary
from [Discussion #4681](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681).
The actual MinGit **2.35.3.windows.1** executable rejects `cat-file --batch -z`
with exit 129 and no stdout. The unchanged reader retries exactly once through
the line protocol and returns the expected object IDs and bytes. The installed
Git **2.47.1.windows.1** is the supported-protocol control and needs one batch
process. This is tooling compatibility evidence, not a mathematical replay.

## New coverage

[The four installed-Git tests](../../tests/test_research_git_installed.py) use
real blobs, NUL-delimited trees and commits. The temporary repositories contain
only `.git`; no working file has to carry a Windows-forbidden name. SHA-1 and
SHA-256 fixtures each check eight reads: empty, 262,148-byte binary, space and
Unicode names, literal LF/CR/CRLF names, and a duplicate empty object.
Independent `hashlib` calculations establish every expected blob ID.

The launch observer delegates to the real `Popen` with its original arguments
and pipes. It does not replace Git or synthesize a protocol reply. On an
unsupported binary, the exact-byte tests wait for the actual probe to exit
before returning its handle to the reader, exercising the native closed-stdin
case as well. The early-close test uses ordinary launch scheduling. The tests
check the exact batch-process sequence and the three literal `rev-parse`
arguments used for line-separator names on the legacy path.

Additional controls require missing objects, tree objects and NUL-bearing
requests to reject. Early closure must not consume the next request, every
observed process must be reaped with its pipes closed, and no watchdog thread
may remain at a blob yield. The existing simulated-failure tests still supply
controlled non-129 exits, failures after a valid reply and pipe error injection;
these new tests complement their coverage.

The new module is discovered by the existing onboarding workflow's
`test_research_*.py` command. No workflow, production reader, source pin, frozen
package, scientific artifact or selected record is changed.

## Sources and environment

Canonical main base: `7c472563474e60185e6ca101a17622133d047e56`, priority revision 7.
The unchanged `scripts/research_package.py` has Git blob
`ef9b52c392323362621baf6ee188a26fc5122bf9` and SHA256
`8e07ddee4d8e1c70a278538b2758d423a298b96d5d1a18233dc29925696fc96f`.

The old executable came from the official
[Git for Windows 2.35.3 release](https://github.com/git-for-windows/git/releases/tag/v2.35.3.windows.1),
asset `MinGit-2.35.3-64-bit.zip` (26,052,150 bytes). Its downloaded SHA256 equals
the publisher's value:

```text
9b88c81ad796acf9969825e8736b953cb0e0bfb4717be57fd59336ae94d521e4
```

The archive was expanded in the task's scratch directory. Its `cmd` directory
was prepended only to the test process environment's `PATH`; it was not
installed as system Git and performed only operations on disposable local
fixtures. The tests do not download or install Git.

Native evidence uses Windows 11 build 26300, CPython 3.12.0 x64 and the two Git
versions above. `PYTHONUTF8=1` is explicit for the complete existing reader suite.
An initial broader run with MinGit 2.40.1 and the default Windows encoding failed
the existing `test_unicode_spelling_is_not_normalized` diagnostic assertion:
the rejected decomposed filename was escaped on stderr. The planner still
rejected the alias. This is not counted as a suite pass or fixed by this change.
MinGit 2.40.1 also supports `-z`, so its initial probe is not fallback evidence;
the canonical claim retains that correction.

## Reproduce

With either Git version on `PATH`, run the new module normally and with Python
assertions disabled:

```sh
python -W error -B -m unittest discover -s tests -p 'test_research_git_installed.py' -v
python -O -W error -B -m unittest discover -s tests -p 'test_research_git_installed.py' -v
```

For the full focused suite on Windows, save and restore the environment in the
same PowerShell process. Substitute the local extracted MinGit directory:

```powershell
$savedPath = $env:PATH
$savedUtf8 = $env:PYTHONUTF8
try {
    $env:PATH = (Resolve-Path 'PATH_TO_MINGIT/cmd').Path + ';' + $savedPath
    $env:PYTHONUTF8 = '1'
    git --version
    python -W error -B -m unittest discover -s tests -p 'test_research_git_*.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'Normal reader suite failed' }
    python -O -W error -B -m unittest discover -s tests -p 'test_research_git_*.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'Optimized reader suite failed' }
} finally {
    $env:PATH = $savedPath
    $env:PYTHONUTF8 = $savedUtf8
}
```

Local results on 2026-10-23, with `-W error -B` throughout:

| Environment and scope | Normal Python | Optimized Python (`-O`) |
| --- | --- | --- |
| Windows, MinGit 2.35.3, full focused suite | 61 discovered: 53 passed, 8 skipped (86.099 s) | 61 discovered: 53 passed, 8 skipped (77.445 s) |
| Windows, Git 2.47.1, full focused suite | 61 discovered: 53 passed, 8 skipped (73.409 s) | 61 discovered: 53 passed, 8 skipped (71.214 s) |
| Windows, MinGit 2.35.3, final new module | 4 passed, none skipped (3.903 s) | 4 passed, none skipped (3.821 s) |
| WSL Ubuntu, Git 2.43.0, CPython 3.12.3, final new module | 4 passed, none skipped (0.466 s) | 4 passed, none skipped (0.190 s) |

The eight Windows skips are six existing POSIX descendant tests and two existing
tests that create physical CR/LF filenames. The new object-tree fixtures cover
literal CR/LF names without those filesystem restrictions. The full older-Git
run preceded a final test-only failure-teardown guard and unused-import cleanup;
the final new module was then rerun with both Git versions and on Linux. The
production reader was identical throughout.

Two separate disposable source copies supplied semantic failure controls with
MinGit 2.35.3. Adding an immediate `raise` after
`except _UnsupportedNulBatch as exc:` disables fallback; replacing the
`if not nul and ("\n" in spec or "\r" in spec):` condition with `if False:`
disables literal-name resolution. In each copy, running
`python -W error -B tests/test_research_git_installed.py InstalledGitTests.test_installed_git_exact_sha1_objects_and_literal_line_separators -v`
exited 1: respectively an unsupported-batch exception and rejection of
`HEAD:line\nname` as missing/non-blob. Neither mutation was retained. This shows
the new test detects these transport regressions, beyond passing the current
implementation.

## Limits and next questions

The native Windows direct-child deadline controls use real Python subprocesses
to stall headers, payloads, terminators and writes; they do not demonstrate a
production Git hang. Their success corroborates the composed #4686/#4738/#5185
reader on this host. Windows descendant-held pipes, escaped processes, other
Git/Python versions and arbitrary package replay compatibility remain outside
scope. No selected cold replay, broad mathematical suite, proof-kernel review
or independent human acceptance is claimed. Hosted CI is separate from the local
evidence above.

The concrete older-Git handoff is complete for this version pair. A useful next
step would be a native Windows descendant-held-pipe ownership fixture, as already
identified by #5185: first show that a ready descendant can keep the pipe open
after the leader exits, then test a bounded ownership mechanism without changing
source authentication. That needs a separate lifetime contract and is unclaimed
here. The Windows diagnostic-encoding mismatch above is a separate small test
portability question; begin with the single failing spelling test.

## Coordination and credit

This follows task `portable-replay`, refined to the explicit older-Git handoff
after checking #1166 and the source thread. The verifier-engineering chooser
seed was `1f8eb9e1a9a35f2f4e6152b366e68143`. The original card's canonical-payload
method is **changed** to an installed-binary and immutable-source transport check:
valid source pins must be readable before research can be independently replayed.
The stop rule is this version pair and the composed direct-child controls,
without a production-reader redesign.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19152845)
records the exact scope and correction. Initial remote overlap covered 304 open
PR bodies and 4,625 Discussion records with complete pagination. The submission
refresh at 19:13 UTC covered 305 open PR bodies and 4,637 Discussion records,
again with complete pagination; the specific older-Git search surfaced this
claim and its predecessor handoffs. Canonical main was unchanged on refresh.
The sparse local note inventory is incomplete; relevant Git compatibility/provenance
packages, evidence notes, the central review ledger and the live #4681 thread
were read. Searches do not cover every historical diff or unpublished result.

Nick Petalas's #2752 supplies the fallback and original compatibility tests;
Mihir Srivastava's #4686 supplies Windows pipe handling; Brian / JoyboyBrian's
#4738/#5185 supply response deadlines and POSIX descendant ownership. Woklerx,
Arham Tahir and Douglas Colkitt retain the streaming, batching and package-contract
credit. The object-tree fixture follows Tekalign's exporter tests and their
Windows portability successors. Prepared for Mihir Srivastava with substantial
OpenAI Codex assistance, one agent. Apache-2.0.
