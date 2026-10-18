# Verification record and implementation limits

Local environment: macOS 27.0.1 arm64, CPython 3.12.15 and CPython 3.14.8.
No third-party Python dependencies. Publication base was fast-forwarded from
initial main a1bfbc677fdcbc2a27a9b3bf6c78cac8fd6da9e2 to refreshed main
ba3de47290c3882cbbe406db1f657578f7ecda69. The priority revision remains 5.
Exact freshness and overlap timestamps are retained in TASK.json.

Completed checks:

```sh
uv run --python 3.12 --no-project python -Werror -B scripts/research_package.py --package research/selected-native-payload-backing
uv run --python 3.12 --no-project python -Werror -B -m unittest discover -s tests -p 'test_research_*.py'
```

Registered replay passes 60 native fixtures, 22 complete origin-bit-plane
executions and 13 test methods. The repository workflow suite passes 138 tests,
with seven platform/environment skips. Its deliberately rejecting fixture
subprocesses print expected exceptions; the suite itself exits successfully.
All ten exported files were also compared byte-for-byte with their original
Git objects. The five unchanged primitive dependencies in PR2753's exported
predecessor match the PR2697 bytes; SOURCES.json records both identities.

A separate temporary copy without Git and with all package files read-only passes
both direct commands under CPython 3.14.8 with `-Werror -I -O -B`. Mutation
controls explicitly make only their private copied targets writable. No source
or receipt is regenerated during normal verification.

The new checker has no recursive calls. The main domain has 4 primitive kinds,
5 radix/exponent pairs, 3 spectator tuples and 22 extra origin planes. The fixture
entry point admits q in {3,5}, 1<=w<=3, spectator extents in {1,2}, and rejects
volumes above 5000 before constructing payload/origin arrays. Each source scan
therefore has a finite fixture bound. Source loading visits exactly six named
modules; authentication requires exactly ten named exports. Functions stay
within the 60-line review ceiling. Explicit ValueError checks remain enabled
under optimization, including typed domains, exact peaks, restoration and pins.

Managed Python allocation is a stated Power of Ten deviation. Observation uses
weak references to bounded fixture allocations, rather than a preallocated
physical inventory. The returned witness retains only integer lengths. The
source classifier uses frame inspection at literal constructor sites. Loading
uses compile/exec on six authenticated fixed source files so adjacent bytecode
cannot replace the pinned runtime; this is a constrained metaprogramming
exception. Source Tape methods and numerical/callback dispatch are necessary
instrumentation interfaces, not arbitrary external callbacks. The exported
predecessors retain their original loops, allocation and style; rewriting those
immutable inputs would invalidate the source-bound question.

Warnings are errors in every registered command. No separate type checker or
linter is configured for this scoped standard-library package. The source proof,
source-byte authentication, finite execution and receipt checks are separate
claims. The all-size theorem, total native private storage, physical compiler,
stronger time contracts, full selected cold replay, human/formal-kernel review
and hosted CI are not claimed here.
