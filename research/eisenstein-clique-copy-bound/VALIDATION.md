# Validation and handoff

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Local platform: Linux 6.6.87.2, x86_64, WSL2. Checks completed on
2026-10-13. New work is confined to this research package.

| Check | Observed result |
|---|---|
| `python3 -B research/eisenstein-clique-copy-bound/verify.py --write /tmp/intmul-eisenstein-replay-seed48.json` | PASS on Python 3.12.3; committed certificate reproduced |
| `python3.11 -O -B research/eisenstein-clique-copy-bound/verify.py` | Identical certificate and PASS on Python 3.11.15 |
| `python3 -O -B research/eisenstein-clique-copy-bound/crosscheck.py` | PASS: 298,378 modular primal inequalities and 241 exact Fraction dual costs |
| `python3 -B research/eisenstein-clique-copy-bound/test_verify.py` | Three tests OK: relocated minimal-input optimized replay/export; corrupted dual receipt rejection; modified source rejection; output preserved on failure |
| `make selected-record-check` | PASS: selected record, exact κ, original source inventory and proof supplements |
| Python parsing, package links and staged whitespace | PASS |

The main receipt contains eight mathematical rejection controls and the full
finite coverage. The modular checker imports no package implementation; its
rank lower bounds suffice for the primal inequalities, while its Fraction
engine checks the dual costs exactly. This corroborates the arithmetic;
the written proof and main replay supply the geometry/completeness reduction.

The main replay and tests use only Python's standard library. The discovery
LP is unnecessary to reproduce or verify the result. No proof-assistant,
independent human review, hosted CI pass, repository-wide `make verify`, or
selected supplier cold-replay pass is claimed. Those expensive supplier
checks were not repeated because this adds a separate research certificate
without changing a supplier, generator, assembly, or selected-frontier input.

The final fetch left `origin/main` at the recorded base. The pre-submission
metadata refresh covered **614 open PRs through #795**, plus an all-state
Eisenstein/Witting search. No competing Eisenstein result was found. PR703
and PR738 retained the pinned heads; PR767 concerns Gaussian subclasses,
and PR785 extends the Hurwitz model to fixed-support nonlinear messages.
They are related work in different geometries/models, not this certificate.

The completed result is **C ≥ 22**, with **22 the exact optimum of the
weighted-clique certificate method**. The actual decoder optimum remains
in [22,40]. The distinction is essential: no cost-22 decoder or new κ is
claimed. Under the stated physical/accounting premises, costs 22–26 remain
unexcluded candidates for a positive three-stage deficit; implementation
and all remaining expenses are unresolved.

Prepared by Jonathan Lam (@jonathanlam) with substantial OpenAI Codex
assistance. Predecessor contributions and their review status are pinned
in [SOURCES.json](SOURCES.json). Apache-2.0.
