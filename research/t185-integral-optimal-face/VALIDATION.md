# Validation and limits

2026-10-16, Windows x64, standard library only. Author-checked with substantial
OpenAI Codex assistance; no separate human review or formal-kernel proof.

## Executed checks

- Python 3.12 registered replay: both `-I -B` and `-I -O -B` commands pass,
  followed by `PASS_REGISTERED_RESEARCH_PACKAGE`. The runner's temporary
  directories were placed in the writable workspace because this Windows
  sandbox's default temporary-directory ACL denied cleanup. The initial
  default-temp attempt passed its first mathematical command but failed
  cleanup; it is not counted as a passing registered replay.
- CPython 3.14.6: both direct normal and optimized commands pass and agree
  exactly with committed `RESULT.json`; warning-as-error source compilation
  passes. The generic runner deliberately requires Python 3.12; its version
  gate under 3.14 is not reported as a registered replay.
- Relocated package, Python 3.12 optimized: all package files read-only,
  empty `PATH` (Git unavailable), separate working directory, no checkout
  inputs supplied. Replay passes and every copied file remains byte-identical.
- Metadata/provenance check passes. Publication bytes are separately checked
  against the contribution commit with `scripts/check_research_commit.py`.

Every mathematical replay checks the five original source exports by SHA256,
byte count and Git blob hash; reconstructs all 1,163 patterns and eleven tight
identities; proves every other slack >1/250 by direct positive-binomial
intervals; independently reproduces the existing root signs; and row-reduces
the nine inventory equations exactly. It checks all 11,236 distinct T5 vectors,
large-domain boundary fixtures through T=10^12, and 200 rounded witnesses.
These finite cases support the written all-T elimination proof, rather than
replacing it.

Eleven controls cover invalid/nonintegral face parameters, a nondivisible
replica count, changed bin/helper inventories, a feasible T37 packing that
does not attain the optimum, a forged dual price, corrupted source bytes,
and the exact counterexample to omitting the binomial remainder. Interval
calibration at exponent 1/2 uses exact squaring, including short series where
the tail matters. Acceptance uses explicit checks and survives `-O`.

## Source and freshness boundary

Scientific/assignment main: `ffbd90dd90dbe0055464f3a1411b25a3a4fdc6b8`,
priority revision 5. Before submission canonical main was fetched at
`38746ad3f6ffebcc0275e286b1dbb733d7c696dd`; relevant root guidance,
catalogue and selected record were unchanged. The contribution branch is
rebased onto that refreshed main. Its historical scientific pins remain intact.

The source PR2863 head was re-read and remains
`34328b1d5e5bebac62d5cabec993dfbfd7b2123f`.
Final live metadata refresh covered 486 open PRs including drafts and 1,543
Discussion body/comment/reply records, with complete pagination. Relevant
terms include T185, tight face, integral attainment and replica divisibility;
local package notes and the ledger were also searched. The earlier historical
R480 divisibility theorem and PR2863/2875 are credited. Metadata coverage does
not search arbitrary diffs, unpublished work or every closed PR body, and is
not a proof of novelty. Exact UTC timestamps are retained in `TASK.json`.

## Unrun obligations

No new physical allocation, source-window/family/chronology audit, native
circuit replay, selected cold replay, all-size/precision/tape proof, supplier
admission, outer release or Lean build was run or established. PR2863's
physical T185 construction and its inherited assumptions remain separate
predecessor evidence. There is no new kappa claim or selected-record change.
