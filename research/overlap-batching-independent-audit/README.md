# Independent pagination and failure audit of PR2493

Arham Garg's [PR2493](https://github.com/CrocSwap/integer-mult-bounds/pull/2493)
batches the initial Discussion/comment/reply pages used by the research overlap
helper. This package independently corroborates its ordered-record and cache
failure behavior at **`a459ee34fad0488691beba8441e0a31e103b91a5`**. It adds no
collector implementation and claims no new measured speedup or multiplication
result. The selected record and production helper are unchanged.

The added evidence is a boundary cross-product and failure injection at every
request position, rather than a second implementation of the batching change.
The API model and direct record traversal here do not import the predecessor's
test harness. Both harnesses use the usual static-graph/cursor simulation;
this is separate implementation and expanded finite coverage, not an independent
human review or a proof for every possible API response.

## Exact sources

[DEPENDENCIES.json](DEPENDENCIES.json) records commit, path, Git blob and SHA256
for three byte-identical source exports:

| Input | Commit | Purpose |
| --- | --- | --- |
| `sources/baseline.py` | `6ca6f217708b075814de409ad693fea9a2aaa760` | Current-main unbatched collector and cache implementation |
| `sources/candidate.py` | `a459ee34fad0488691beba8441e0a31e103b91a5` | PR2493's actual collector and cache implementation |
| `sources/candidate-tests.py` | same PR2493 head | Six original tests, replayed unchanged in fresh normal/optimized processes |

All three inputs are authenticated before any target module executes. Sources
are compiled directly from those bytes, avoiding saved bytecode. The audit
needs neither Git nor network access. [SOURCES.json](SOURCES.json) retains main,
the selected record and the assigned task as historical provenance. There are
no live production-script pins to become stale if the batching change is adopted.
The generic package metadata check uses repository history; the direct checker
works in a Git-free package export.

## Finite result and failure coverage

The immutable corpus is generated from the full Cartesian product:

- Discussion counts: `0, 1, 49, 50, 51, 101`.
- Busy-thread comment counts and selected-comment reply counts, independently:
  `0, 1, 4, 5, 6, 99, 100, 101, 104, 105, 106, 205`.
- Both the first and last Discussion are busy; other threads have small pages.
  Reply-heavy comments occur at indices 0, 5 and the last comment. This exercises
  replies delivered with initial and continuation comment pages.

The 864 parameter tuples yield **710 distinct graphs** after exact canonical
deduplication. Both collectors match the direct, cursor-free traversal on every
field and record position: **2,062,777 records per collector**. Equal body text
on different nodes prevents text-only comparison from hiding an order/identity
error. Unicode newline characters are retained. Opaque cursors encode their
connection owner and reject reuse in another thread or comment.

On the separate 51-thread / 205-comment / 205-reply busy fixture, every actual
request position is failed with a GraphQL-style exception, transport exception,
or malformed missing-connection response. Each is tested both with and without
previous complete evidence:

| Collector | Request positions | Failure cases |
| --- | ---: | ---: |
| Main baseline | 135 | 810 |
| PR2493 | 84 | 504 |

All **1,314 cases** retain a warning. With old evidence, its complete source,
records and original timestamp survive in memory and on disk. On a first fetch,
no partial Discussion source is admitted. The separately fetched PR source may
still refresh, matching the existing per-source cache contract.

Three actual collector mutants stop listing, comment or reply pagination early;
the direct traversal rejects all three. Three modified source exports fail
authentication. The candidate's six original tests pass in both normal and
optimized subprocesses. [RESULT.json](RESULT.json) is the deterministic receipt;
normal verification compares it without writing package files.

For a fixed 101-small-thread corpus, requests fall from **104 to 3** with equal
records. This is a finite request-count corroboration. It is not a new network
timing measurement, nor a claim that busy threads always use fewer requests.
Arham Garg's existing timing evidence retains its own corpus and environment.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/overlap-batching-independent-audit
```

The registered commands run the complete audit normally and with `-O`. They
also replay the predecessor suite in both modes. To check the exact pinned
package without Git or the repository:

```sh
python3.12 -I -B research/overlap-batching-independent-audit/verify.py
python3.12 -I -O -B research/overlap-batching-independent-audit/verify.py
```

Expected: `PASS_OVERLAP_BATCHING_INDEPENDENT_AUDIT`, 710 static graphs, and the
counts above. `--write` explicitly regenerates only this package's receipt.
On restricted Windows shells, set `TMP` and `TEMP` to an existing writable
workspace directory before running; the checker uses temporary fixtures.

Executed on Windows x64, 2026-10-15: the registered CPython **3.12.14** replay
passes both commands. An optimized Git-free export also passes from an unrelated
directory with spaces, leaving all ten package files byte-identical. The initial
direct CPython **3.14.6** audit passes too. These are local assisted checks; no
hosted-CI or independent human result is claimed. TASK.json records the commands,
environment and final freshness check.

## Limits and integration handoff

This checks finite static API fixtures and specified failures. It does not prove
atomicity under concurrent board edits, certify GitHub availability/rate limits,
recheck every future source head, or provide a live timing ratio. Authenticated
source exports establish which code ran, not a general trust guarantee for code.

PR2493's two reported frozen-dependent failures reproduce on this untouched
main base:

```sh
python3.12 -B scripts/research_package.py --package research/overlap-path-index --check-only
# source blob provenance mismatch: scripts/find_overlap.py
python3.12 -B scripts/research_package.py --package research/research-package-pin-batching --check-only
# working source drift: tests/test_research_onboarding.py
```

They remain unresolved. This package does not edit frozen evidence, adopt the
collector, resolve the wider [PR2255 live-pin audit](https://github.com/CrocSwap/integer-mult-bounds/pull/2255),
or claim those dependent replays passed. Supplier/native/hosting/precision and
selected full cold replays are unrelated to this scoped audit and were not run.

## Open next questions

Can PR2493 be integrated with an explicit disposition for the two dependent
failures? This matters because passing the collector tests alone does not admit
frozen package changes. Reproduce the two commands above and record a maintainer
source-binding decision. That policy/integration decision is the blocker; more
static pagination examples are not proposed as a prerequisite. The structured
question, original task and scope change are in [TASK.json](TASK.json).

## Credit and coordination

**Arham Garg / @arhamgarg** owns PR2493's batching change, six tests, benchmark
and prior coverage argument. **Douglas Colkitt** and the overlap-tool contributors
own the original record schema, complete pagination and cache implementation;
**Nick Petalas** supplied the retained CLI-pagination compatibility work.
**Aaron Wang / PR2255** supplied the existing broader live-pin audit.
Their source headers and Apache-2.0 attribution are retained verbatim.

Prepared for **Arham Tahir** with substantial **OpenAI Codex** assistance in
analysis, implementation, verification and writing. No subagents, independent
human review or formal-kernel result is claimed. New material is Apache-2.0.
The canonical investigation is [Discussion2789](https://github.com/CrocSwap/integer-mult-bounds/discussions/2789).
The initial scalar-to-moment assignment and explicit change to this side audit
are preserved in TASK.json; there is no paid-profile or kappa improvement claim.
