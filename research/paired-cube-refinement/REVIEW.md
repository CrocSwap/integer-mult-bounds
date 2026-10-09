# Review of PR164, PR168 and PR169

Reviewed snapshots:

- PR164: `4391a60bb26f75ea47a4c55c508c88a036b5a2b8`.
- PR168: `98c115b53742b6613ad630de4d493f37b0119da7`.
- PR169: `4895ba1104cedc7908b6d6ba64fdd6290e0ed7ae`.

Both are conditional witnesses; neither proves the retained all-size
interfaces. PR168 changes the scalar modules and carrier arcs, so its
physical plan cannot be combined with PR164 by copying operation indices.
This package recompiles its frame proposals against PR168's actual word.

## Confirmed findings

1. **Fixed-gauge bit reuse is obstructed.** The selected 5,720 gauges have
   220 distinct spaces. None contains any of the 1,760 source incidence
   lines. Each eligible donor endpoint must contain at least one source
   line in its conservative support. Hence no such endpoint can be inside
   any selected gauge, irrespective of its lifetime. Exact certificates
   in `../paired-cube-bit-reuse` check this for both snapshots. Changing
   donor matching weights cannot fix this obstruction with those gauges.

2. **Restricting optimization to descent misses improvements.** The paid
   moment depends on the entire child distribution. Enlarging an operation
   frame can merge adjacent transition costs and improve that moment while
   preserving stock, rank deficit, support and nesting. The new search tests
   both causal prefixes and suffixes and verifies the selected plan separately.

3. **PR168 retains avoidable arithmetic slack.** It uses an atom exponent
   of 10^-3 and a coarse decimal saving grid. The least strictly paid atom
   and exact rational root refinement improve the bound even before changing
   frames. Its fallback envelope can also be tightened using the already
   written theorem. Matched comparisons are generated in `RESULTS.md`.

4. **PR168's physical complex replay is seeded.** Its two modular seeds are
   useful controls, but do not by themselves prove equality over the rationals
   on every input. The added exact adjoint and coefficient-bounded formal
   replay pass every source, target and dirty column in both shear directions.

5. **The older proof-text mismatch is real, but does not apply unchanged to
   PR168.** At PR164's inherited PR161 note, `a=a_b` contradicts
   `(1-beta)a_c>a` with the displayed constants. The code uses the minimum
   and strict weakening. The correct old transfer saving is
   `a=0.0005885667994114331`. PR168's updated complex supplier exceeds its
   bit supplier, so its corresponding displayed inequality is valid. We
   preserve the historical pinned sources and document the erratum here.

## PR169 comparison

PR169 independently applies lower and upper operation-frame moves to PR168,
using PR165's replacement checker. It reports 1,716 changed frames and
kappa 0.0006105562. Its original scalar and frame inputs match PR168.
`compare_pr169.py` independently replays its supplied plan through the same
geometry, ledger, prime and all-column checks used for our candidate.

The saved comparison also prices both profiles using the same exact
envelope, coarse grid, least-paid-atom rule, complex supplier and balanced
transfer settings. Its values are stored in `pr169-comparison.json`.
This separates a better physical child profile from a finer atom or
assembly calculation; the number of replaced frames alone is not a score.

Further exact search from PR169's plan improves our earlier PR168-based
local optimum. Pointwise intersections and spans of the two plans were
also tested after exact nondegeneracy and chain checks. The intersection
start returns the previous paid profile; the span start returns the same
final frame records as the PR169 start. We select the PR169 start for its
simpler source provenance. The selected plan adds 240 accepted downward
closure moves and 120 upward closure moves to that input. It uses 2,196
replacement frames; the complete result is independently certified.

## Implemented and deferred

Implemented: bidirectional frame search; exact fallback and paid atom
refinement; all-column scalar checks; strict frame-plan schema checks;
regenerated source-bound proof numbers; and an exact reuse obstruction.

A useful next research direction is to change gauges together with target
read schedules, since fixed-gauge matching has no legal edges here. Parity
decoder hierarchies and dimension-specific module search remain separate
experiments requiring new scalar words and complete recompilation. Their
possible improvements are not included in this certificate.

## Baseline verification

PR164's complete `research/paired-cube-bit-descent/verify.py` passed under
Python 3.12 on Ubuntu. Its Linux-only `resource` import prevented the same
unmodified check from completing under native Windows Python.

PR168's `make paired-cube-verify`, byte-identical p12 bit word regeneration,
and independent bit checker with all five mutation controls passed under
Python 3.12 on Ubuntu. The successor adds its own complete finite check and
source closure. These are the relevant package gates, not a claim that all
fourteen unrelated historical repository verification groups were rerun.
