# Validation and handoff

Validation date: 2026-10-13 UTC. Prepared by Alexander Templeton with
substantial OpenAI Codex assistance. All results below are local execution
receipts, not independent human review or proof-assistant verification.

## Completed checks

- CPython 3.10.21 and 3.13.15: the default exact receipt replay and all four
  independent test cases pass.
- CPython 3.14.7 with `-O`: the same receipt and four tests pass. All proof
  checks in the main verifier use explicit exceptions, not `assert`.
- Exact geometry: 240 distinct E8 roots, ten quaternionic lines of 24 roots,
  100 singleton Gram ranks, and 45 two-line spanning obligations. A separate
  Fraction column-basis algorithm agrees with the integer row algorithm on
  all 145 rank obligations.
- All 1,048,576 ordered support pairs satisfy the weighted inequality.
  There are 2,057 cost-zero, 20,350 cost-one and 1,026,169 cost-two pairs;
  maximum transversal incidences are 0, 16 and 32, respectively.
- Three attaining codes pass all 1,296 input assignments and 33,856
  conditional transcript checks. Two use demonstrably nonlinear encoders;
  a separate explicit inverse decodes all their 1,280 inputs. The remaining
  example includes unequal and zero widths. A zero-cost mate-only message
  is also accepted.
- All twelve internal rejection controls pass. Extra nonorthogonal side
  information is separately shown to permit cost 2 instead of 10; this is
  an explicit counterexample to dropping a premise, not a code in the model.
- The four-port one-bit search exhausts every Boolean truth table, encoded
  by integers 0 through 65,535 in increasing order. Four tables let receiver
  zero decode, and none lets all four decode. Sources and readers are all
  four ports, with independent one-bit inputs and mate-only side information.
  This complete finite search has no randomized choices; assignment seed 42
  selected the research scope. The stopping rule was completion of this
  exact domain. The all-width theorem comes from PROOF.md, not this search.
- A relocated export containing only `verify.py`, `SOURCES.json` and
  `RESULTS.json` passes from an unrelated working directory in isolated,
  optimized mode. Mutating the copied receipt or source-manifest bytes
  makes the process fail. These two artifact controls are additional to the
  twelve mathematical controls.
- `uv run --offline python -B scripts/verify_selected_result.py` passes:
  selected record, exact kappa, original source inventory and proof supplements
  are unchanged.

Commands and expected output are in [README.md](README.md). `--write` was used
once to create the committed deterministic receipt; normal validation only
reads and compares it. No solver, floating rank test, numerical optimization
or network service participates in the replay.

The unchanged full `make verify` and selected supplier cold replay were not
repeated for this isolated research package. No remote CI pass is claimed.
The all-size/physical implementation and nonlinear width-pricing assumptions
remain outside the finite checks.

## Remote refresh and distinct scope

At 05:27 UTC, a fresh fetch still gave main at
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. The open queue contained 594 PRs
through #775. #703 still had head
`358383e2f1b0f292d4d6eb897c06fd8558a4f5e6`, with no submitted reviews.
The preceding contribution #740 remained open with no comments or reviews.
There was no pinned sprint coordination issue, so the claim is local.

The current overlap review inspected #703, #738, #757 and #761 and the
freshly arrived contributions below:

- #765 (`d8eaa3db32f76111b39db9b930f347ef30118a28`) extends a fixed full-E8
  binary matrix floor to tensor basis mixing; it has different geometry and
  factorization restrictions.
- #767 (`96b4b74677d1bef99e8346bfb6a4ed0531e58a62`) gives Gaussian planar and
  incidence subclass obstructions.
- #770 (`48d027a664288ea1d4e987de63cb79588b8b936b`) establishes the weighted
  maximal-clique method ceiling for Gaussian scalar totals; it explicitly
  excludes vector totals.

All-state searches for nonlinear, transcript and Hurwitz research were also
checked. #288's nonlinear controlled-shift frames and #682's tensor-provider
rate audit use different physical models. None of the inspected claims
establishes the fixed-support nonlinear Hurwitz message result here. This
does not assert novelty beyond the repository or claim priority for the
predecessor's geometry, weights, scalar floor or general counting technique.

No source from these concurrent PRs is imported. The geometric facts needed
for this proof are rebuilt locally. Historical claims in #620 are credited
as research provenance, not silently promoted to accepted theorems.
