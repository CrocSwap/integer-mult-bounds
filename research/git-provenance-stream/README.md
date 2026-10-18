# Stream pinned Git source reads through one process

Research package validation previously started two Git processes per source and
reread the originating catalogue. This change streams one pinned object at a time
through `git cat-file --batch`, reducing ordinary blob-only checks from 2N+1 Git
processes to one. It preserves every Git blob, SHA-256, live-input, original-card
and metadata check. It retains one-blob memory usage and no persistent cache.

Newline-containing object expressions and non-blob objects retain legacy Git
semantics. The generator is explicitly closed on an early validation failure;
missing/truncated responses reject and the child is reaped. A process exit is
checked after consuming the full list.

## Reproduce

```sh
python -X utf8 scripts/research_package.py --package research/git-provenance-stream
```

Use Python 3.12. The benchmark executes the exact base-commit validator and the
modified validator against this package's same 33 provenance pins, three times
each. It compares results and subprocess counts; timings are measurements, never
a correctness gate. BENCHMARK.json records the original Windows run. The benchmark
does not mutate source manifests. SHA and object-id mutation controls must reject
under both implementations. Separate tests cover live-input drift through the
existing onboarding suite, binary/empty/Unicode/tree objects, cleanup and no cache.

This affects metadata loading only. No mathematical check is removed or skipped,
and no cold circuit replay improvement is claimed. Existing Windows locale and
timeout compatibility issues belong to PR1298 and are not duplicated here; use
UTF-8 mode for the old validator in this benchmark.

## Credit

Douglas Colkitt authored the base validator with OpenAI Codex assistance. This
optimization and tests were prepared by woklerx with substantial OpenAI Codex
assistance. SOURCES.json pins the base implementation and representative source
closure for reproducible comparison.

## Open next questions

Measure this same complete check on Linux and a larger source inventory. Windows
wall times do not establish a platform-independent speedup; the reduction in Git
process count and unchanged validation coverage are the portable result.
