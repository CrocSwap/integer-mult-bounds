# Validation receipt

Validated on 2026-10-13 in Linux x86_64, glibc 2.41, CPython 3.12.14.
Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Input and predecessor pins are in [SOURCES.json](SOURCES.json).

| Command | Observed result |
|---|---|
| `python -B research/complex-coefficient-reuse/verify.py` | Both full scalar replays pass; certificate matches; 716 logical plus nine arbitrary private input columns; savings 18,510 / 46,400; all 14 controls rejected |
| `python -B research/complex-coefficient-reuse/test_package.py` | Minimal relocated copy with spaces passes under `-B -O`; different gzip containers accepted by payload; no default writes; changed payload rejected; prior output preserved on failure; understated primitive certificate rejected |
| `make selected-record-check` | PASS selected record, exact κ, original source inventory and proof supplement |
| `git diff --cached --check` | No whitespace errors |

The clean-copy test carries only this package and the eight named input files,
uses an unrelated working directory, and imports no upstream verification code.
Its mutations affect temporary copies only. Exact regeneration of EXPECTED.json
was followed by the default comparison mode; the regeneration command is not
represented as a certificate comparison. The full focused replay took about
20 seconds in this environment; this is a verification observation, not a
claimed implementation speedup or a performance benchmark.

The overlap refresh covered 535 open PRs through #716. PR681's changed head
`fdc2e4f3c6825530b02143b30deab5de10209479` now covers fourteen raw factory
windows, still a distinct scalar-word resynthesis. PR696 remained at
`5a3f983715027c4fd83f50bc9001d4b18463bed1`; the extra savings here are explicitly
measured beyond its per-macro mechanism. No combined savings with PR681 are
claimed. There was no pinned coordination issue. See [OVERLAP.json](OVERLAP.json).

No existing generator, selected supplier or certificate changes. Repository-wide
`make verify`, the selected cold/global replay, fresh phase/controller checks,
remote Linux CI and Lean were not run. They are not represented as passing.
The complete original local finite invoice is reconstructed, but this package
does not issue a new selected/global admission. Its grouped scalar interface
and inherited all-size/physical/analytic obligations remain as described in
[README.md](README.md).

Checks and review were performed with substantial OpenAI Codex assistance;
there was no separate human or delegated-agent review.

Publication-time refresh: 567 open PRs through #748. Newly published #722
independently overlaps forward cleanup sharing; #739 extends that cleanup
class across magnitudes. Their exact heads and scope are now credited in
README.md and OVERLAP.json. A census using the unchanged lowering confirms
additional A/centre/B coverage and all 1,088 backward precondition runs.
This update changes documentation/coordination metadata only; the executable
code, inputs and verified certificate are unchanged.
