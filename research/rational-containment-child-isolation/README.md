# Current-source imports throughout the rational-containment customer

This opt-in successor restores the original six historical input blobs and gives
the complete rational-containment caller tree fresh import-cache namespaces.
It retains the original h=10/h=12 audit payload, all 42,860 inclusion decisions,
7,614 distinct targets, eight arithmetic tests in normal and optimized Python,
four arithmetic mutants, six source mutations, two frame failures, two adapter
guards and the original single paired benchmark. No mathematical checker or
frozen source is edited, and no speedup or new kappa is claimed.

## Reproduced failure

The actual caller is `research/rational-containment-performance/verify.py`.
Its independent `-I -B adapter.py` subprocess authenticates all six historical
inputs, then imports `scripts/rational_span_frames.py`. The registered parent's
private `-X pycache_prefix` does not pass to an independent Python command;
`-B` permits cache reads, and `-I` ignores `PYTHONPYCACHEPREFIX`.

In a disposable copy, compile a cache with the one-digit `dot` coefficient
changed from 9 to 8, then restore the exact original source bytes and timestamp.
The unchanged adapter passes source authentication but fails its real `spans()`
check with `A forbidden source-to-target path exists`. Remove only that cache:
the same source and command pass the entire original benchmark with payload
SHA256 `faa0f9c0159a6e70d4e2cfcdb4012ea62ef350bd26b81312d11da4a770f8b218`.
This is a reproducibility failure caused by a source/execution disagreement;
it does not demonstrate acceptance of an invalid mathematical certificate.

The entry observation on macOS used CPython 3.12.2: the stale run rejected in
0.40 seconds and the clean run passed in 1.47 seconds. These are diagnostic
durations, not performance measurements. The tests reproduce both timestamp
and unchecked-hash failures, checked-hash invalidation, the isolated success,
and cache-removed success through the actual original adapter CLI. They check
the source bytes/timestamp and preexisting cache bytes remain unchanged.

## Exact historical context

The original package's source base is
`410026dc5513b87db92ae98571d1d5984c69a983`. At this contribution's canonical base
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, three original input files have drifted:
`exclusion_circuit.py`, `experiments/mixed_point_circuit.py`, and
`rational_span_frames.py`. The original entry in the current checkout rejects
those input pins. We do **not** claim that entry passes on current main.

[ORIGINAL.json](ORIGINAL.json) records 17 byte-identical retained files: all
11 original package files at the contribution base and the six original input
blobs at their historical base. They occupy 95,894 bytes. The unchanged original
`SOURCES.json`, `VERIFY.json`, `VALIDATION.json`, README, authorship and benchmark
remain in `retained/`. The six original hashes and Git blob IDs are not revised.
[SOURCES.json](SOURCES.json) binds every retained origin as historical provenance;
all actual runtime data are inside this new package, so `VERIFY.json.inputs` is
empty. The same package exports without Git or access to the current scripts.

## Fixed caller tree

| Actual caller | Actual child entries | Calls |
| --- | --- | ---: |
| Original `verify.py` | `test_kernel.py` normal and `-O`; `adapter.py` reference, annihilator, compare, existing-output rejection and `-O` rejection | 7 |
| Original imported `benchmark.py` | `adapter.py` reference and annihilator | 2 |
| Original normal `test_kernel.py` | Four private copies of `test_kernel.py`, each with its original changed arithmetic kernel | 4 |

[replay.py](replay.py) authenticates all 17 retained sources before execution.
It replaces only the three `subprocess.run` AST expressions in those caller
files with a synchronous launcher. All original argument values, optimization
flags, keyword arguments, timeouts, failure decisions and scientific assertions
remain in place. The imported benchmark receives the same one-call replacement.
No original code is rewritten on disk.

The launcher accepts only the two original flag forms and fixed child scripts.
A mutation grandchild must contain the exact original test script and one of
the original four changed kernels; the adapter never replaces a mutant with a
good kernel. Each child and grandchild owns a new cache directory until it
returns or raises. The normal parent also owns a fresh namespace. An optimized
outer coordinator launches this historical parent in its required normal mode;
the original explicit optimized test and rejection commands remain optimized.

[RESULT.json](RESULT.json) records 13 child/grandchild calls, 14 distinct
namespaces, seven successful children and six expected rejections. All cache
directories are removed. The actual parent and five successful adapters report
the current source's `dot((1,), (1,)) == 8`. The original complete scientific
receipt is compared with JSON type preservation; only the paired timing ratio
and historical host/provenance metadata are excluded. The original benchmark
still executes and checks both complete payloads.

## Reproduce

Use CPython 3.12, standard library, a writable temporary directory and full Git
history for the metadata provenance check:

```sh
python3.12 -B scripts/research_package.py --package research/rational-containment-child-isolation
```

The primary marker is `PASS_CONTAINMENT_CHILD_ISOLATION`. The second command runs
four test groups: real CLI cache differentials, exact launch grammar and original
mutants, all 17 retained-source changes rejected, and a full Git-free export with
an unchecked-hash cache present under an optimized outer coordinator. The export
uses empty `PATH`, preserves every copied file and prior cache byte, and requires
exact equality with `RESULT.json`. It retains all original controls and the
13-call tree; it is not a substitute mini-verifier.

## Limits and open obligations

This is the fixed historical caller tree and normal adapter entrypoint, not a
general Python sandbox or shared-runner change. Custom import loaders, preloaded
modules from outside this entrypoint, concurrent source mutation, standalone
bytecode and additional descendant commands remain outside its contract.
Cleanup is observed on successful and expected-rejection calls; hard process
termination and changes to transitive process lifetime are not claimed.
The retained customer imports POSIX `resource`; native Windows portability is
not claimed. Local validation is macOS arm64/CPython 3.12.2. No native Linux,
hosted CI, repository-wide suite, selected cold replay, scientific supplier
admission or all-size multiplication theorem is inferred.

## Open next questions

Which other actual registered caller has a demonstrated import-cache failure?
Pin a named caller and helper, reproduce a numeric disagreement, and retain that
caller's complete checks before extending any execution policy. This package
does not justify a general descendant census or interception mechanism.

## Credit and coordination

CubeJerry's rational-containment implementation and all credited source authors
retain their work unchanged. PR2553 supplies the registered-interpreter cache
boundary; the frame-closure child-isolation successor supplies the earlier fixed
caller/child adapter; PR2990 and `isolated-descendant-bytecode` supply the isolated
unittest boundaries. Their guarantees are credited, not recounted as new work.
This contribution closes one different, demonstrated `-I` customer tree.

Canonical claim: [Discussion 2988](https://github.com/CrocSwap/integer-mult-bounds/discussions/2988#discussioncomment-19130816).
Entry overlap covered 506 open PRs, 3,650 Discussion/comment/reply records and
5,860 local notes. Exact caller searches found no overlapping child repair;
closed PR bodies, arbitrary diffs and unpublished work are outside that snapshot.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0. Independent
human or hosted review is not claimed.
