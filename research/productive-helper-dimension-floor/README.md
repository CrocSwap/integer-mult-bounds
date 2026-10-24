# Fixed chart heights cannot improve the productive-helper invoice

On the pinned round-three word, arbitrary Clifford chart changes and native-map
changes cannot lower the complete paid-minus-helper invoice if each contact
keeps its original **projection dimension** and owned-center tariffs stay
fixed. The theorem includes quadratic chart forms and nonnested transitions.
It holds separately in both program orientations for
`H_r = r^(1-C)`, `H_0 = 0`, and `0 <= C < 1`.

This is an analytic obstruction with an exact source-bound census, not a
search failure. Its useful consequence is a stopping rule: an improvement
must change contact heights, owned costs, the scalar graph, helper contracts,
or another stated hypothesis. No new kappa or supplier is claimed.

## Why the obstruction holds

For a physical frame `F`, use the inverse-image Lagrangian chart
`L(F)=F^-1(Z)`, where `Z` is the vertical coordinate space. The height
`k(L)=dim(proj_x L)` equals the relative Fourier rank `d(L,Z)`. The metric
inequality `d(L,M) >= |k(L)-k(M)|` shows that every original nested paid edge
already has the smallest possible rank at its endpoint heights. Changing
charts at fixed heights cannot make any such edge cheaper. Source native
transitions have rank zero and cannot get cheaper either.

Of 408 helpers, 358 have height-zero entrances, whose charts are necessarily
`Z`; their residual ranks remain fixed. Each of the other 50 has a paid-only
entry-to-exit wire whose source rank sum equals its original helper residual.
These paths share no charged edge occurrence. Every old-zero edge is retained.

If a path's source ranks are `r_i` and their increases are `delta_i >= 0`,
concavity gives

```text
sum_i [H(r_i+delta_i)-H(r_i)]
    >= H(sum_i r_i + sum_i delta_i) - H(sum_i r_i).
```

The metric triangle inequality bounds the new helper residual by the new
path rank sum. Thus each path pays for its helper's entire additional credit;
edge-disjointness prevents reuse of that payment. All other costs are
nondecreasing. [PROOF.md](PROOF.md) gives the full argument for any
nondecreasing concave tariff on nonnegative reals with `H(0)=0`.

## Reproduction

Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/productive-helper-dimension-floor --check-only
python3 -B scripts/research_package.py --package research/productive-helper-dimension-floor
python3 -I -O -B research/productive-helper-dimension-floor/verify.py
```

The direct replay prints `PASS_PRODUCTIVE_HELPER_DIMENSION_FLOOR`; the
registered runner also prints `PASS_REGISTERED_RESEARCH_PACKAGE`.

The checker authenticates the compressed source and its complete JSON
payload, reconstructs both chronological graphs, validates every source
native rank and the full paid/helper invoices, and records all 50 paths per
orientation in the deterministic `PATHS.json.gz` receipt, bound by
[RESULT.json](RESULT.json). Each orientation has 1,016 selected
paid edge occurrences. All 448 source adapters touch only main roles.

Eight corruption controls reject source changes, missing old-zero edges,
double-counted debt, and native transitions inserted into paid-only paths.
A separate finite calibration enumerates all Lagrangians in dimensions one
through three and checks the height/rank convention on 18,459 ordered pairs.
These checks remain active under `python -O`. The checker imports no
predecessor graph builder, compiler, optimizer or numerical library.

Parent and independent agents checked the source paths and the argument
separately. This is not independent human or proof-kernel acceptance. No
new physical word is emitted, and no new phase, compiler, precision, supplier
or outer-theorem admission is asserted.

## Scope, sources and credit

The only live input is Cao Yifan's round-three word from
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, pinned in
[SOURCES.json](SOURCES.json) at canonical main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. This original-source theorem does
not depend on the compression or finite fusion certificate in
[PR #5301](https://github.com/CrocSwap/integer-mult-bounds/pull/5301).

Each node may choose any Lagrangian chart of its original projection
dimension, including a different projection direction and quadratic form.
Compatible shared native maps may change. The proof even allows independent
native maps at different occurrences and independent chart choices between
orientations; actual physical constraints may narrow this relaxation.
Owned-center tariffs and helper contracts remain fixed. Changed projection
dimensions, owned costs, scalar/contact graphs, helper contracts and other
supplier mechanisms are outside the theorem.

Related path-floor work includes Matarener's
[PR #5060](https://github.com/CrocSwap/integer-mult-bounds/pull/5060), Cinna
Davis's [PR #5136](https://github.com/CrocSwap/integer-mult-bounds/pull/5136)
and [PR #5140](https://github.com/CrocSwap/integer-mult-bounds/pull/5140), and
zxv's arbitrary-Clifford owned-tree extension in
[PR #5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283).
Those concern owned-center or other constrained path costs. The contribution
here is the source-specific 50-helper path census and complete-invoice
accounting at fixed heights. [PR #5144](https://github.com/CrocSwap/integer-mult-bounds/pull/5144)
provides distinct nonmonotone owned/shared-map context. The subspace metric
and concavity principles are standard; the proof credits the metric's
Koetter–Kschischang reference and the retained inverse-chart grammar.

Overlap checks read the start/handoff/native discussion context and an initial
800 most-recently-updated PRs, followed by a 100-PR delta on 2026-10-23 ending
at 13:09 UTC. This is bounded coverage, not a census of unpublished work or
all open PRs. Canonical main was refreshed before this package.

Credit Cao Yifan's #4610 source word, Cinna Davis's canonical/native and helper
accounting lineage, Dugongue's chart contract, zxv's supplier, and all retained
scalar/Clifford/compiler authors. Prepared by flyingviper with substantial
OpenAI Codex assistance and independent agents. Apache-2.0.

## Open next questions

Can a coordinated change of contact heights and native interfaces lower the
complete invoice? Start with a concrete source-derived dimension change and
its full signed paid/helper polynomial, then optimize the coupled native
interfaces while charging every old-zero edge. A favorable exact invoice
still needs one compatible shared map per operator and the applicable dual
native, phase, compiler and outer checks. [TASK.json](TASK.json) records this
scope change, first step and blockers.
