# Independent POSIX audit of PR6334 Git paths

This package takes the explicit independent POSIX check requested by
[PR6334](https://github.com/CrocSwap/integer-mult-bounds/pull/6334) at
`e579ddc0e0b4614184b869f8d20cffdcc26380a6`. That contribution repairs line-ending
normalization which can collapse distinct CR, LF and CRLF Git paths and falsely
report complete local overlap coverage. The repair and its Windows evidence
belong to the predecessor; this package supplies independent POSIX fixtures.

The original `portable-replay` card is retained verbatim in [TASK.json](TASK.json).
The actual scope changes from its compressed-artifact example to this named
path-identity handoff. Canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. No selected
result, shared helper, frozen predecessor package or mathematical certificate
is changed.

## Scope and evidence

The bounded question is whether the retained candidate preserves distinct
valid UTF-8 Git paths on POSIX and reports the correct local coverage when
line-ending names and symbolic links are present. A separately constructed
Git fixture compares the candidate against the retained canonical-main helper.
Meaningful controls must reject missing or incorrectly reported coverage;
checking that a process merely exits successfully is insufficient.

On macOS 26.5 arm64, CPython 3.12.16, Apple Git 2.50.1, all **83 tests**
from the predecessor's nine documented modules passed, with **zero skips**.
The two path suites also passed under optimized drivers (13 executions).
All five symlink controls skipped in the original Windows run executed here.
Exact commands, timings and log hashes are in
[evidence/predecessor-replay.json](evidence/predecessor-replay.json).
These 96 executions took about 20.5 seconds; this is a local timing, not a
performance claim or a hosted-CI result.

The new independent verifier runs **seven materialized filesystem states**
against both pinned CLI implementations (14 CLI executions per mode). Its
oracle is the explicitly constructed fixture, not either helper's parsed tree.
It preserves an executable note, excludes a committed symlink and a nested
vendor note, and uses `--limit 1` while checking total results and warnings.
The five incomplete states cover removed CR/CRLF files, leaf aliases, parent
aliases, dangling aliases and an unrelated untracked note. In all five, main
falsely reports complete coverage; PR6334 reports the exact two missing names.
Both real-note positive states pass. The cache remains byte-identical.

Normal and optimized receipts are in
[evidence/independent-normal.json](evidence/independent-normal.json) and
[evidence/independent-optimized.json](evidence/independent-optimized.json).
Each also reruns the unchanged 13-test path suites from a disposable export.
Every independent CLI child receives `-O` in optimized mode. The unchanged
predecessor local-suite driver does not propagate `-O` to its own CLI child;
its optimized-driver result is intentionally distinguished from the new probe.

An initial audit-harness check incorrectly searched verbose test output for
any occurrence of `skipped`, including a successful test's name. It was fixed
to require the exact unittest success summary; the receipts above are from
completed reruns. No predecessor functional failure was found.

The separate [controls.py](controls.py) rejects five byte-corrupted retained
sources and eight forged report fields, and accepts two positive controls.
Both normal and optimized runs passed; their receipts are in `evidence/controls-*.json`.
A copy of this package outside the project Git checkout also passed optimized
replay (seven differential cases plus 13 retained tests, zero skips). This
confirms that the direct replay does not rely on cached unmerged Git objects.

Both helper versions and their shared dependency are retained under this
package. [SOURCE-VERSIONS.json](SOURCE-VERSIONS.json) records their original
commits, paths, Git blobs and SHA256 digests; `verify.py` checks the retained
bytes before execution. The predecessor's unmerged Git commit is not needed
for a cold replay. The origin receipt records extraction provenance. Hard-coded SHA256 pins bind
the executed bytes; this is not a cryptographic commit-membership proof or
acceptance of every predecessor claim.

[SOURCES.json](SOURCES.json) binds only the base catalogue and selected record
as historical provenance. There are no live external inputs in
[VERIFY.json](VERIFY.json): all executed helper bytes are package-local.
The registered metadata check needs the canonical base Git history; the direct
verifier creates disposable fixture repositories and does not require project
Git history or a network connection.

## Reproduce

From the repository root, with Python 3.12 and Git available:

```sh
python3.12 -B scripts/research_package.py --package research/pr6334-posix-path-audit --check-only
python3.12 -B scripts/research_package.py --package research/pr6334-posix-path-audit
python3.12 -I -B research/pr6334-posix-path-audit/verify.py
python3.12 -I -O -B research/pr6334-posix-path-audit/verify.py
```

The explicit normal and optimized commands exercise the same contract; the
audit must not depend on Python `assert` statements. Each main replay has a 180-second timeout; the two rejection-control commands
have 30-second limits. No Python dependencies, solver, Lean or Docker build
is requested. The POSIX audit does not extend the predecessor's Windows
coverage or certify arbitrary non-UTF-8 filenames, concurrent worktree edits,
scientific source bindings or the complete multiplication theorem.

After committing, publication checks are:

```sh
python3.12 -B scripts/check_research_commit.py --package research/pr6334-posix-path-audit --check-source-history
```

The unrelated six-test `tests/test_research_current_status.py` module was also
run on the unchanged main files: five passed and
`CurrentCiNavigationTests.test_current_ci_section_matches_selected_record`
failed because CI documentation still names frontier6030 while the selected
record names frontier7000. This is a reproduced baseline failure, not a pass.

Hosted CI results are separate from the local scoped replay. In particular,
the unrelated selected-record/CI-navigation failure reported against canonical
main is already addressed by open
[PR7276](https://github.com/CrocSwap/integer-mult-bounds/pull/7276); this audit
does not duplicate that repair.

## Task selection and overlap

Read the current `AGENTS.md`, `autoresearch.md`, `CONTRIBUTING.md`, and
[coordination guide](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163)
before choosing this source-specific handoff. At the selection check, PR6334
had no comments or reviews and explicitly asked for POSIX execution of both
path suites, including materialized LF names and symbolic links.

Targeted open-PR search for `6334` returned only PR6334, and `overlap POSIX`
returned no result. The Discussion search for `6334` returned
[discussion6356](https://github.com/CrocSwap/integer-mult-bounds/discussions/6356),
which distinguishes PR6357's requested-repository pin reader from PR6334's
overlap index. The latest 500 top-level handoff comments, dated November 3–14,
2026, and up to 5–10 recent replies per comment did not surface a POSIX audit
of PR6334. The repository overlap helper additionally completed a refresh of
901 open PR bodies and 7,512 Discussion records (including comments/replies) at
2026-11-14 13:17–13:20 UTC. The literal `6334` search had unrelated hash/numeric
hits and the separate #6356 work; no additional matching POSIX audit was found.
Local sparse coverage omitted 10,177 of 10,178 tracked notes; closed PR bodies
were not fully fetched. These are bounded search results, not a novelty claim.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19612921)
names the exact scope. A pre-submission canonical-main fetch retained the same
`e54523517` base.

## Open next questions

Does the eventual integration of PR6334 preserve this behavior alongside later
main changes? The first step is to pin that integrated helper, inspect its delta,
and rerun these fixture expectations plus the current path suites. This audit
covers the exact pending head, not GitHub's merge result. Main contains later
inventory parsing and test changes, so passing the pending head is not sufficient
integration evidence. The blocker is an identified integration commit; no extra
search over scientific constructions is justified by this tooling result.

## Credit

Credit josecarlosgonzalezroque-design's PR6334 for the path-byte repair, its
counterexample and Windows evidence; lee-phys's PR4419 for the coverage
contract; Ali Romman's PR5725 for path checks; Nick Petalas's PR6161 and the
retained overlap contributors. Douglas Colkitt and the retained contributors
receive credit for the research-package runner and source-binding machinery.
Original notices remain with retained sources.

Prepared for FanPUYen with substantial OpenAI Codex assistance and separately
scoped agents for handoff/overlap review, package scaffolding and independent
code review. New work is Apache-2.0. This is an agent-assisted tooling audit;
independent human and formal-kernel acceptance are not claimed.
