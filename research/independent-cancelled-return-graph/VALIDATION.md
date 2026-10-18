# Local validation and publication boundary

CPython **3.12.13** and **3.14.5**, macOS **27.0.1 arm64**; standard library only.
Recorded on 2026-10-14. No predecessor executable is imported or run.

The registered command passed:

```sh
python3.12 -B scripts/research_package.py --package research/independent-cancelled-return-graph
```

It rebuilt the complete certificate and ran all six external tests. The tests
include actual modified-source rejection, a false source head, a tampered unused
terminal edge with its graph digest also rehashed, duplicate/nonfinite JSON,
prefix-only integrality failure, and an optimized read-only relocated export
in a path containing spaces. A relocated `--emit` run reproduced the complete
certificate bytes. The six registered tests took 21.528 seconds; this is a
local test observation, not a performance comparison.

An additional isolated optimized **Python 3.14.5** rebuild with `--emit` was
byte-identical to the committed certificate. Certificate SHA256:
`7cff9f9db0a6b5f6e355a91fff0862998ae6a1a4a6c073fb9080aea9fb1209d3`.

Other passing checks:

- package metadata/provenance validation;
- all 20 `test_research_*.py` repository workflow tests;
- all five `test_selected_result.py` tests;
- `scripts/research_baseline.py` selected source bindings/arithmetic;
- all four retained source files matched actual Git objects at the pinned
  PR1563 head, and both PR1537 files matched their original Git objects;
- normal/optimized certificate equality, Python syntax and staged whitespace.

The audit found no discrepancy in the source graph or 35-point frontier.
The complete rebuilt graph, 1,618 cap decisions, 42 complete source records,
all 53 Fraction-checked terminal edges and 14 semantic controls pass.
The 128-partition seed-82 small fixture independently supports the decomposition
and cost recurrence. These finite checks do not formalize the multiplication
theorem or independently review the source's nested recurrence.

Research base: `0a201997097b8a89b638f3a2afcb35db4184c8b2`.
Refreshed main: `858771bcca3b8dd5d4ef4aa682a13cc9b7e23920`.
The selected record, AGENTS.md, CONTRIBUTING.md, catalogue and package runner
are byte-identical between those commits. The new directory is absent from
refreshed main. No upstream, frozen package, ledger or selected-frontier file
is changed.

The final pre-submission overlap refresh at **04:45–04:46 UTC** covered **663
open PRs** and **280 Discussion/comment/reply records**, with complete pagination
and no warnings. It searched PR/discussion text, local top-level package notes
and the ledger, not every code diff or unpublished result. The matches were the
original construction, earlier canonical audit, rounding-related context and
this claim/package. This is coverage evidence, not a priority guarantee.
PR1563 `e7d1ebfc3093a704b55c14ea4d10d0d0bdfdd0db`, PR1575
`20828301c60f4b0581964ac3170694da5b8ce12e`, and PR1537
`407f00df6ca0bf86b455b5640f18ec2f62ee77b9` were rechecked unchanged.

Not run: full selected-construction cold replay, native/physical or rounded
admission, a nested-cap optimizer, Lean or independent human review. Hosted CI
is separate from these local checks; no hosted success is asserted here.

Prepared by Sricharan Vagvala with substantial OpenAI Codex assistance.
Apache-2.0; one parent agent, no subagents.
