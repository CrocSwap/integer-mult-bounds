# Sharp polynomial budgets for acyclic interaction errors

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped written mathematical proof with exact finite corroboration.
If all interaction-error matrices share an acyclic coordinate support with
paths of at most h edges, the sharp forward norm envelope is the degree-h
sum of elementary symmetric polynomials in their individual norm budgets.
The sharp inverse envelope uses complete homogeneous symmetric polynomials.
No small-total-error restriction is needed. A common shift matrix attains
each envelope exactly in the infinity norm, with separate sign choices.

For R=(I+D_K)...(I+D_1), d_i>=||D_i||, write e_r and H_r for these two
classical symmetric polynomials. [PROOF.md](PROOF.md) proves

```text
||R||       <= sum_(r=0..h) e_r(d),
||R^-1||    <= sum_(r=0..h) H_r(d).
```

Subtracting the degree-zero term gives sharp operator-defect bounds. The
proof also gives a sharp suffix-weighted arithmetic-noise budget. Products
of more than h errors vanish because every such product follows a directed
walk in the common graph. This argument permits arbitrary finite real or
complex matrices; they need not commute or be individually square-zero.

At depth one, the exact forward and inverse envelope is `1+sum_i d_i`.
Twenty errors of norm `1/10` therefore have bound **3**, strictly below the
earlier sufficient shear product `(11/10)^20` of Ali Romman's
[PR5288](https://github.com/CrocSwap/integer-mult-bounds/pull/5288).
This uses the stronger common-depth-one hypothesis. At depth two the exact
bounds for the same norm list are **49/10 forward** and **51/10 inverse**.
Those higher-depth errors may have nonzero squares, outside that earlier
shear theorem. Neither predecessor result is re-audited here.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/acyclic-interaction-budgets/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/acyclic-interaction-budgets/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/acyclic-interaction-budgets
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/acyclic-interaction-budgets --check-source-history
```

Another CPython 3.12 path may replace that executable. Expected direct marker:
`PASS_ACYCLIC_INTERACTION_BUDGETS`, with `errors=0`. Each run emits a newly
computed JSON receipt bound to every package file by SHA256. The verifier
writes nothing. No receipt is handwritten, and no solver or predecessor
executable is required. The two registered commands each have a 120-second
timeout. Provenance pins are authenticated separately by the package checks.

The finite replay covers:

- 326 coefficient comparisons against independently enumerated subsets and
  multisets, plus two maximum-capacity checks.
- All 729 pairs of three-dimensional strictly upper triangular matrices with
  entries in `{-1/2,0,1/2}`. A separate adjacency-power oracle checks graph
  depth, and rational Gaussian elimination computes the actual inverses.
- Fifteen permuted-coordinate words and two twenty-step words. Across these
  and the exhaustive pairs, 746 support graphs, 1,553 prefixes and 1,553
  arithmetic-noise steps pass.
- Fifty-one attaining families, including empty words, zero depth, zero
  norms and the executable's maximum dimension and step count.
- Twenty malformed-input rejections and seven mathematical controls. These
  distinguish individual from common nilpotence, elementary from homogeneous
  inverse coefficients, chronological inverse order, suffix noise, and
  physical from interaction-coordinate support.

These finite checks corroborate the universal written proof. They do not
exhaust all matrices or supply formal proof-kernel acceptance.

## Scope, sources and limitations

The interaction identity `D_i=F_i^-1 Delta_i F_(i-1)` and the physical
prefix/noise contract come from ywz65's
[PR2701](https://github.com/CrocSwap/integer-mult-bounds/pull/2701), head
`c21f5a50b9f4682ff9d4fe622d3d4e81c3cc86fb`. Ali Romman's PR5288,
head `cd33c723408bb98875211ee3145582c507881f29`, supplies the distinct
square-zero shear product comparison. Classical nilpotent inverse formulas,+symmetric polynomials and directed-path expansions retain their mathematical
credit. No general literature-priority claim is made for those methods.

The new step is the pair of sharp common-depth budgets, their attaining
families and exact precision-interface consequence. The predecessor's
production-caller question is refined to this additional-structure question;
it is not claimed as a completed caller binding. No predecessor executable,
construction or scientific replay is used. Predecessor files and credit lines
remain unchanged. Their retained proof texts, the original card and selected
record are pinned as historical provenance in [SOURCES.json](SOURCES.json).

The `uniform-transfer-audit` card explicitly changes scope to this side
result. It does not discharge the selected `precision_tape` assumption.
Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision eight, selected #7000 with conditional kappa `363005817/10^11`.
The selected bindings-only baseline passed. No selected cold replay,
predecessor scientific replay, native build, Lean or Docker run is claimed.

Common acyclicity must hold for the actual interaction errors. Triangular
physical perturbations can acquire diagonal entries under the required
prefix conjugation. A written two-dimensional example and its exact control
show this distinction. The optimal bounds concern all support graphs of
depth at most h; a prescribed graph can have smaller optima. The physical
frame-norm factors are sufficient, with no sharpness claim for them.

Arithmetic rounding may be nonlinear. An inverse of its realized perturbed
linear product is not a reversible finite-grid program. Actual coefficient
storage, a bounded-error arithmetic kernel, overflow, physical representation,
ownership/restoration, native operations, tape/storage costs, a complete
signed invoice and supplier admission remain open. All five framework
assumptions remain. No new kappa or selected-frontier change is claimed.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19591516)
and local reservation precede the result. Live coverage included 800 open PRs
and 7,400 Discussion records with complete pagination, followed by distinctive
all-main README and merged-PR searches. Sparse local notes were incomplete;
the separate full closed-PR refresh timed out. Arbitrary historical diffs and
unpublished work remain outside coverage. These checks are not a novelty
certificate. [TASK.json](TASK.json) records the source and scope decision.

## Open next questions

1. Bind one actual emitted tile and coefficient-storage policy to the common
   acyclic interaction hypothesis. Compute the exact prefixes, their inverses
   and transformed error supports in one fixed basis. Include basis-change
   norms, arithmetic error and physical costs before judging any precision
   or complete-invoice gain. The supplied caller contract is the blocker.
2. Determine the sharper envelope for one particular acyclic graph that
   excludes the shift witness. Start with its chronological paths and the
   within-factor paths appearing in inverse expansions. A specific error
   budget and consumer decision are needed before a new census is useful.

No further construction or search is supplied here.

## Verifier constraints

The bounded rational API accepts dimensions at most 16, words of at most 32
steps and input numerator/denominator heights of at most 256 bits. The proof
has no such finite restrictions. Polynomial updates use O(K(h+1)) arithmetic
operations and O(h+1) rational entries; the trajectory helper uses O(K^2(h+1)).
The support checker uses a bounded topological elimination on at most 256
edges. All new functions have fewer than sixty physical lines and use no
recursion. Explicit exceptions keep every scientific check enabled under
optimized Python. No subprocess, network access or persistent write occurs.

Power of Ten rule 3 deviation: CPython dynamically allocates rational numbers
and containers. The dimensions, step counts, bit heights and serial fixture
domains bound live data. The pair inventory has 27 matrices and tests one pair
at a time. An attaining fixture holds two lists of at most 32 matrices. Internal runtime
allocation is not instrumented. Receipt reads are limited to seven regular
files, each at most 128 KiB. A fixed-allocation implementation would be needed
before using this checker as an embedded runtime service.

The isolated verifier explicitly loads its one adjacent implementation module
because isolated Python omits the script directory from the import path.
This is the only dynamic module target, with no generated code or arbitrary
callback dispatch. Package-file hashes bind its source in each generated
receipt. Warning-strict normal and optimized replay and in-memory syntax
compilation supply diagnostics; no separate static analyzer is claimed.
