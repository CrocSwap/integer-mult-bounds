# A hash-checked parse cache is faster on the selected record

**Partial. No new exponent.**

The selected reproduction command is `make frontier1094-verify`. Its baseline
stage may be reused only when the published receipt hash matches. This package
does not run that stage. It times one smaller source-bound reuse on the
selected record itself.

Four thousand cold parses each build a new cache. The cached pass hashes the
same bytes every time and parses them once. On this machine the cached pass
was faster by more than a factor of two. The checker requires that ratio on
every replay and prints both times.

Changing the last digit of the `decimal` field misses (on the pinned record, `8` to `9`; the checker now changes whatever digit the live record has). Restoring the original
bytes parses again, so the changed object is not reused. A hit returns the
object from the fresh parse.

## What was executed

The checker reads `certificates/selected-result.json` and applies the cache
above. It does not call the frontier replay.

## Scope and evidence

Original card: `replay-runtime`, priority revision 6, refined to this parse
of the selected record. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the coverage checker
and the frontier driver. No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:22 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3542 note at 2026-10-18
05:14 UTC, was released work. Draw seed `a5f2e8440fbfa35d468f338e46b20574`,
track `verifier-engineering`, second card `replay-runtime`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/selected-record-parse-cache/verify.py
python3.12 -B research/selected-record-parse-cache/test_verify.py
python3.12 -B scripts/research_package.py --package research/selected-record-parse-cache
```

The timed check finishes in under a second.

## Open next questions

The cached parse is faster on this one record, and a changed byte misses.
The frontier baseline stage is a different replay and is not timed here.

## Credit

The frontier driver states that baseline reuse requires the published receipt
hash. The coverage checker states that selected coverage does not guess reuse.
The selected record is the fixture.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
