# Current selected preflights load checker source

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a tooling correction, with no new multiplication bound or theorem claim.

## Failure and correction

At canonical main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, two
mutable selected preflights could authenticate with old checker bytecode:

* `scripts/research_selected_baseline.py` imported `verify_selected_result.check`.
* `scripts/check_selected_ci_inputs.py::check_records` used a file-location
  import loader for the same checker.

Python's `-B` prevents cache writes; it still permits cache reads. A real
timestamp cache compiled before an equal-length, same-timestamp source change,
or an unchecked-hash cache, can therefore run guards different from the visible
`scripts/verify_selected_result.py`. This is an integrity failure at the import
boundary, without needing a malformed selected record.

Both mutable callers now use standard-library `runpy.run_path` on the checker
source file and retain its `check` function. The original module names and
`__file__` path conventions are retained; the checker still derives `ROOT` from
its own resolved path. Its validation code, record context, exception handling,
error strings and output schemas are unchanged. Existing cache files are neither
deleted nor rewritten. The file-form source loader does not consult an adjacent
checker `.pyc`.

## Discriminating regression

`tests/test_research_selected_source_loading.py` reuses Mihir Srivastava's complete
productive-helper fixture from `test_research_selected_baseline.py`, retaining
the real selected checker. It compiles a checker with only the inventory-equality
condition disabled, then restores the exact original source bytes and mtime.
The cache is a genuine `py_compile` timestamp or unchecked-hash cache, with the
appropriate normal or optimized filename. Child processes deliberately expose
the adjacent cache, even if the containing test uses a private cache namespace.

The six test methods cover twenty child-process scenarios per invocation:

* Both actual entry boundaries reject a changed inventoried source, for both
  cache modes under normal Python and `-O` (eight negative cases).
* The corresponding eight valid closures still pass with those caches present.
* Both callers retain the original checker module name, `__file__` and `ROOT`.
* Invalid current checker source raises `SyntaxError` instead of falling back
  to an unchecked-hash cache, at both boundaries.

Every cache case checks that checker bytes, mtime and pre-existing cache bytes
remain unchanged. Against the unmodified base callers, six methods produce ten
failures: eight false accepts of drift and two cached accepts of invalid current
source. After the correction, the same methods pass under normal Python and
an optimized containing test process; each invocation also tests normal and
optimized child interpreters.

A separate local disposable export exercised the actual selected source closure,
not just the small fixture. It copied 527 files: the manifest closure, selected
record and evidence, checker, and both mutable entry scripts. Appending a benign
comment to `research/joint-helper-lattice/native_joint.py` caused all eight
cache-mode/interpreter/entry negative cases to pass incorrectly with base callers.
With corrected callers, all eight reject with the original
`Selected package inventory or bytes changed` error. All eight unchanged-source
controls pass. Checker source/time and cache bytes are preserved in every case.
This export checked source binding only and ran no construction commands.

## Sources and affected callers

All pins below refer to the canonical base above, before this correction.

| Source | SHA-256 |
| --- | --- |
| `scripts/research_selected_baseline.py` | `c23d8a94958a00bb6c9f296393d7fe96bf7c70a23c967c1e39e691b9864e8447` |
| `scripts/check_selected_ci_inputs.py` | `dc629c5d357859f63a409a3ca8f56ac8e947a080ff54342ef49ac28e18f4a1eb` |
| Unchanged `scripts/verify_selected_result.py` | `d6b305eac5b9bdb8172c469ad30a1655a60fa0aceac8b1bf610e1b73f51babd8` |
| Unchanged `scripts/verify_frontier4470.py` | `9bdb7b304f6ede7fcba72bc04a8aaf75d288a1678ebf9e03b4ddd6d93caa5a91` |
| Unchanged `certificates/frontier4470-source.json` | `09f71f10800837b6ba6e2652a5237ea3dff907176e8dbba827969972da6fc069` |

The other direct checker imports are the frozen selected driver
`scripts/verify_frontier4470.py` and historical callers
`scripts/research_baseline.py` and `scripts/verify_frontier4359.py`.
Their bytes are retained. Direct execution of `verify_selected_result.py` is a
different boundary: it executes that script as source. In particular, the
selected Make target already has a direct-source checker prerequisite and a
fresh exported replay. This finding does not demonstrate a bypass of that
complete replay. It does not upgrade the historical import callers.

The new regression is discovered by the existing `test_research_*.py` onboarding
step in `.github/workflows/research-packages.yml`; no workflow change is needed.
No source manifest, selected record, frozen package or archived pin is refreshed.

## Reproduction and local evidence

Run from the repository root with Python 3.12:

```sh
python3.12 -Werror -B -m unittest discover -s tests -p 'test_research_selected_source_loading.py' -v
python3.12 -O -Werror -B -m unittest discover -s tests -p 'test_research_selected_source_loading.py' -v
python3.12 -Werror -B -m unittest discover -s tests -p 'test_selected*.py' -v
python3.12 -O -Werror -B -m unittest discover -s tests -p 'test_selected*.py' -v
python3.12 -Werror -B -m unittest discover -s tests -p 'test_research_selected_baseline.py' -v
python3.12 -O -Werror -B -m unittest discover -s tests -p 'test_research_selected_baseline.py' -v
python3.12 -Werror -B -m unittest discover -s tests -p 'test_research_*.py' -v
```

Local environment: macOS 27.0, arm64, Homebrew CPython 3.12.7
(`Clang 16.0.0`). The new regression passes six methods under each outer mode;
the affected selected tests pass 52 methods with four skips under each mode;
the orientation tests pass thirteen under each mode. The complete onboarding
suite passes 385 tests with eighteen platform skips in 141.236 seconds.
Test-suite parent processes
used fresh private cache namespaces. The cache regression itself removes that
inherited setting from its children to reproduce the ordinary adjacent-cache
boundary.

A five-file `git archive` of code commit
`73fe5d35aa235f7adb5879ddc3237ea64a041aaf` also passes all six new methods
under normal Python and `-O`, with no `.git`, an empty `PATH`, and all exported
files/directories read-only. Exported file hashes remain unchanged. The archive
SHA-256 is `c3bad4d4737b3792442a469442559537bd425499a464d08ffb798539ad794e4b`;
it contains both entry scripts, the unchanged checker, the existing orientation
fixture test and the new cache regression. Fixtures write only in their own
temporary directories outside the export.

Both current CLIs also pass under normal Python and `-O`. The full
`check_selected_ci_inputs.py` JSON report is identical to the canonical base,
including its existing workflow-trigger advisory; strict trigger coverage has
not been added or claimed.

## Open next questions and limits

* Any future change to a frozen or historical checker import needs a separately
  scoped successor with its own source and replay obligations. This fix supplies
  a reproducible import-boundary regression, not permission to repin an archive.
* The loader trusts the current checker source and standard library. This is not
  protection against concurrent writes to that source, a modified interpreter,
  or arbitrary executable-file replacement. Those require a different threat
  model and first-step fixture before expanding this correction.
* Native Linux and Windows execution, complete selected construction replay,
  historical scientific suites, Lean and Docker were not run locally. Finite
  source-binding tests do not establish the all-size multiplication theorem.
