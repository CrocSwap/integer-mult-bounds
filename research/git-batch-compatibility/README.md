# Source-pin validation on older Git

The registered-package runner now falls back to `git cat-file --batch` when
Git rejects its initial `--batch -z` invocation with usage status 129 and no
response. Exact blob IDs, SHA256 pins, live-input equality and catalogue checks
are unchanged. Supported Git still uses one process. There is no version cache.

This repairs an environment failure documented in the merged
[P104 obstruction package](../p104-side-correction-rank-obstruction/README.md)
and pending [PR2721](https://github.com/CrocSwap/integer-mult-bounds/pull/2721)
at `6b14e212a1aba401d29f2bf7378e745ee2aed7f2`. It is a tooling contribution,
not a supplier, mathematical verification or new kappa.

## Scope and evidence

The original command fails on an unmodified Git 2.34.1 build:

```sh
python3.12 -B scripts/research_package.py \
  --package research/r439-copyshare-h2sem-admission --check-only
```

Before the repair it exits 1 with `unknown switch 'z'`, followed by a
`missing or non-blob Git source` error. After the repair the same checkout,
package and Git binary produce `PASS_PACKAGE_METADATA_AND_PINS`. Git 2.47.3
passes too. The source objects were present throughout; neither their pins nor
the validator's acceptance conditions changed.

The fallback consumes the failed first request again and streams the remaining
iterator exactly once. It never retries after a valid response or a non-usage
failure. Before sending a CR/LF-containing expression through the line protocol,
it resolves that expression as one literal `rev-parse --verify --end-of-options`
argument and requires a hexadecimal object ID. That ID, rather than the path,
is sent to the batch reader. The reader still rejects non-blobs and NUL-bearing
requests and verifies exact payload sizes and terminating newlines.

Ten new behavioral tests cover the option failure, rejection before the first
write, exact binary/empty/Unicode/duplicate inputs, CR/LF paths, SHA256 object IDs,
missing/non-blob/NUL requests, non-usage failures, a usage exit after one valid
blob, early iterator closure and changed commits across invocations. The tests
simulate only the unsupported-option exit; actual Git serves every fallback
object. The existing seven Git-stream tests retain their original coverage.
A real older Git run separately avoids relying on that simulation.

Local checks on Linux x86_64 and CPython 3.12.15:

- All 17 Git-stream/compatibility tests pass, with resource warnings as errors.
- All 80 `test_research_*.py` tests pass on both Git 2.34.1 and 2.47.3.
- The unchanged `research-package-pin-batching/verify.py` passes all 12 controls
  on Git 2.47.3. Its three-pair benchmark retains one Git process for both the
  10-row and 130-row source inventories. This is not a new speedup claim.

The old Git binary was built outside the checkout from
`https://www.kernel.org/pub/software/scm/git/git-2.34.1.tar.xz`, SHA256
`3a0755dd1cfab71a24dd96df3498c29cd0acd13b04f3d08bf933e81286db802c`, using:

```sh
make -j4 NO_GETTEXT=YesPlease NO_TCLTK=YesPlease \
  NO_CURL=YesPlease NO_OPENSSL=YesPlease git
```

That build was used only on local fixtures. It is not a recommendation to use
an old Git release for network access. No source archive is added or modified.

## Reproduce

```sh
python3.12 -B scripts/research_package.py \
  --package research/git-batch-compatibility
python3.12 -B -m unittest discover -s tests -p 'test_research_*.py'
python3.12 -I -B research/research-package-pin-batching/verify.py
```

To exercise an actual older Git, put its binary first on `PATH` and run the
first two commands again. The registered hook runs the 17 focused tests;
metadata/pin validation precedes them. It does not install another Git version.
[SOURCES.json](SOURCES.json) pins predecessor code and reports as historical
provenance; the changed runner and new tests are bound by the contribution's
Git commit and declared in [VERIFY.json](VERIFY.json) for CI invalidation.

## Limits and engineering checks

Only Git 2.34.1 and 2.47.3 were exercised. This does not establish a minimum
supported version, Windows behavior, arbitrary package-command compatibility
or a complete multiplication theorem. The CR/LF filename fixture is skipped
on Windows because those filenames are invalid there. No selected cold replay,
supplier admission, hosted CI result or independent human review is claimed.

The reader has no recursive call path; the compatibility retry is limited to
one. Each source inventory is finite and each reply is consumed before the next
request, retaining one-blob memory use. The two functions have 47 and 19 lines.
Managed-runtime allocations are a Power of Ten rule 3 deviation, bounded here
by the current blob and finite inventory rather than a new persistent cache.
Existing synchronous pipe reads and the general Git helper have no per-read
deadline, a rule 2/7 limitation not repaired by this option-compatibility change.
The existing 90-second process-exit and 5-second cleanup waits remain in place.
A hung-reader report would need a separately scoped cancellation/deadline fix.
Tests cover both normal exit and early/error cleanup; no new assertion depends
on Python optimization being disabled. Python compilation and warning-enabled
unit tests supply diagnostics. Ruff passes the new test file and reports no
new runner finding. The runner retains two existing diagnostics, `FURB167` on
`re.I` and `PLW1510` on Windows timeout cleanup. Those unrelated paths are
unchanged; no diagnostic is suppressed.

## Open next questions

Other Git versions or package commands may have distinct compatibility failures.
Start with one reported command and exact source pins, then reproduce the first
failure. No additional failure is established here, so further compatibility
work should wait for evidence rather than infer support for every Git version.
The structured question is in [TASK.json](TASK.json).

## Credit

Douglas Colkitt supplied the package format and validation contracts.
Arham Tahir supplied the NUL-delimited pin batching and its retained failure
controls. Woklerx supplied the earlier streamed Git reader and cleanup tests.
Maxime Fleury's reproducibility work distinguishes immutable source pins from
regenerated artifacts. The P104 package and Abhinav Ramachandran's PR2721
recorded the older-Git failure. Their constructions and mathematical claims are
not re-established here. Prepared by Nick Petalas. Apache-2.0.
