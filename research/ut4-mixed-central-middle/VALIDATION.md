# Validation and review limits

Author-checked on 2026-10-14, CPython 3.12.15, Linux x86_64 under WSL2,
glibc 2.41. Standard library only. No hosted CI or independent human review is
claimed. The scientific baseline is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

## Exercised checks

| Command or check | Observed result |
| --- | --- |
| `python3 -B scripts/research_baseline.py` | Selected source bindings and arithmetic pass; complex side binds |
| `python3 -B research/r439-bsection-stars-seed01/verify.py` | Suggested helper-card positive control passes; overlap redirected work |
| `python3.12 -I -B scripts/research_package.py --package research/ut4-mixed-central-middle --check-only` | Metadata and exact provenance/source pins pass |
| `python3.12 -I -B scripts/research_package.py --package research/ut4-mixed-central-middle` | Exact census, fifteen endpoint controls and nine optimized test groups pass; 11.769 seconds |
| `python3.12 -I -O -B -W error research/ut4-mixed-central-middle/verify.py` | Same exact receipt and scientific marker; 10.338 seconds |
| `python3.12 -I -B -W error research/ut4-mixed-central-middle/test_package.py` | Nine test groups pass, including the separate dense/literal oracles |
| `python3.12 -B -W error -m unittest discover -s tests -p 'test_research_*.py'` | All 65 repository research-workflow tests pass; expected invalid-fixture tracebacks are negative controls |
| Minimal source export, direct optimized verifier and tests | Pass without Git/network; all nine final package files remain byte-identical and no pycache is created |
| `ulimit -v 262144` followed by the optimized verifier | Exact replay passes with a 256 MiB virtual-memory cap |
| Fresh ordinary direct replay measured with `resource.getrusage` | 10.836 seconds, maximum child RSS 26,624 KiB |
| AST parse/compile and function-length inspection | Both Python files compile; maximum function length 30 lines in the verifier and 37 in the final tests |

Normal replay is read-only. Explicit receipt generation created EXPECTED.json
once; subsequent replays compare every field canonically. The additional
receipt-type test rejects a Boolean substituted for an integer count.

The new implementation reports 3,600 middle sequences, 441 zero-sum outer
sequences, 9,721 distinct profiles, 89,052 A-side and 1,201,320 C-side passes,
68 key pairs, 152 profile pairs and 5,536 complete words. None survives Q.
The expansion transcript SHA256 is
`118ea0c1edc09d94b02e90dce7a6bf6168f917b5d10f78a9d59ef77dd04703a8`.

A LOCAL-ONLY exploratory cross-check at `/tmp/probe_ut4_mixed.py`, importing
PR1690's source-pinned `search.py` helpers, independently reconstructs the
profile/gap domain using that predecessor's recursive implementation. It gave
the same census counts, zero quotient survivors and zero full formal survivors
on CPython 3.13.5. This optional local corroboration is not a public artifact or
an extra proof premise. The kept dense/relation and literal-address oracles are
in test_package.py and are publicly replayable.

## Freshness and overlap

Canonical main was fetched at entry and before submission. The second fetch
still resolved to `0fdd7d82`; instructions, priority revision, selected record
and scientific inputs were unchanged. The final complete reported overlap
snapshot covered 418 open PRs and 850 Discussion records, at
21:55:28 UTC and 21:56:55 UTC respectively. It found only PR2027's handoff,
retained context and this investigation for the precise mixed question.

The search does not cover every code diff, all closed remote history or
unpublished work. It is not a novelty guarantee. Discussion coordination is
[the existing mixed-root thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/2019#discussioncomment-18934668).

## Engineering decisions and bounded deviations

Build the Lever led to a kept deterministic census rather than an unsupported
numerical claim. Prove It Works led to ordinary, optimized, registered and
read-only-export replays against the actual receipt. Test Behavior, Not
Implementation led to literal address execution, an independent raw-word
quotient and a planted-word reconstruction test.

The changed code has no recursion, dynamic evaluation, generated code or
unbounded search. Its largest fixed enumeration is `9^5`; the outer catalogue
contains at most `9^4 * 126` placements and actually stores 55,566. There are
six gaps, four outer calls, five middle calls and at most seventy A/C
interleavings per realization pair. Q has seventeen basis elements and the
full group has sixty-four. Subprocess tests use ten-second timeouts; registered
commands have 180/120-second limits. Failure propagates as a nonzero exit;
exclusive-create output mode protects existing files and checks write length.

Power-of-Ten rule 3 requires a managed-runtime deviation. Python allocates
integers, strings, dictionaries and sets during replay; preallocating every
object is not a supported runtime contract. Scope is this fixed finite model,
not a user-controlled word search. Fixed enumeration sizes bound live
collections, transcripts stream into SHA256 instead of accumulating, and the
memory-capped replay passes. Reassess explicit capacity guards before adding
variable roles, call counts or imported candidate files.

Rules 8/9 use the standard unittest discovery/dispatch boundary in the fixed
nine-group test class. Semantic arithmetic calls are direct. There is no eval,
plugin registration or arbitrary callback execution. No static type checker or
linter is installed in this environment. AST compilation and `-W error` in
both registered commands provide the available diagnostics; no warnings were
suppressed. Add a strict Python analyzer if the repository adopts one.

## Attention

The review capability was local proof inspection and separate executable
oracles; no subagent tool was available. The universal conclusions depend on
the written span/compression argument plus the finite group homomorphism and
complete quotient census. Finite fixtures alone would not establish arbitrary
workspace. This package does not establish weighted optimality, native/compiler
realization, rational frames, physical hosting, precision/tape, all-size or
analytic-transfer obligations. No selected cold replay, frontier change, Lean
kernel check or complete multiplication theorem is claimed.
