Actual real characteristic certificate
======================================

SelectedProfileReal.actual_power_characteristic_lt_one proves, without any
analytic enclosure premise,

  sum over the 27 literal rows of (n_t/W) * (t/m)^(1-a) < 1

in Lean's real numbers, with

  a = 63787735011827529 / 1250000000000000000000,
  m = 575, W = 137151806, sum(n_t*t) = 78860441550.

This closes the transcendental-certificate gap for the selected ranked-pair
profile. It is not a claim to exceed subsequent public numerical profiles,
nor a complete formal integer-multiplication theorem. Physical generation of
this profile, the all-size physical recurrence, tape costs, analytic reduction,
precision, and exact recovery remain separate obligations. The source-data
binding check is executable Python; the finite real inequality itself is Lean.

Proof chain
-----------

AnalyticEnclosures.lean proves four generic facts from pinned Mathlib:
1. A finite exponential polynomial commutes with the rational-to-real cast.
2. q <= sum_{j<24} L^j/j!, with q>0 and L>=0, implies log(q)<=L.
3. For 0<=x<=1, the upper bound
     exp(x) <= sum_{j<8} x^j/j! + x^8 * 9/(8!*8)
   follows from Real.exp_bound'.
4. Range reduction q=2^k*r combines separate log(2) and log(r) bounds.

SelectedProfileCertificate.lean proves all rational witness inequalities,
the weighted sum bound, exact gap, row count, and rank mass by ordinary Lean
kernel computation. `decide +kernel` is not `native_decide`.

SelectedProfileReal.lean applies those certificates to the actual log and exp
functions, sums positive weighted bounds, and proves the exact identity

  (n/W)*(t/m)^(1-a) = (n*t/(m*W))*exp(a*log(m/t)).

The resulting rational upper bound is below 1 by exactly

  23551960513937 / 4285993937500000000000000000000000000.

All 17 theorem declarations are included in theorem-manifest.json and audited
with #print axioms. The only dependencies reported are propext,
Classical.choice, and Quot.sound. There is no sorry, admitted fact, custom
axiom, enclosure hypothesis, or native computation axiom.

Reproduce
---------

Use an existing project pinned to leanprover/lean4:v4.21.0 and Mathlib
308445d7985027f538e281e18df29ca16ede2ba3 (v4.21.0), with its dependencies/cache
already built. Put the matching Lean/Lake executables on PATH. No installation
or dependency mutation is performed by this bundle.

From the mission directory:

  python3 outputs/next-proof/analytic/check.py \
    --lake-project work/agents/lean-foundations/formal/lean \
    --certificate outputs/selected-certificate.json

The runner can be used from any working directory when given absolute input
paths. --output selects a different result directory. It compiles all three
modules in dependency order into an isolated olean directory, checks compiler
and dependency pins, verifies source hashes and complete 17-theorem audit
coverage, and writes axiom-audit.json plus source-binding.json. The latter
directly compares the literal Lean constructors with the selected certificate's
width/multiplicity map, m, W, a, and mass. Historical profile provenance hashes
are also compared when present in that certificate. A sources-only
check is available via --check-sources-only. The saved verification/ directory
contains a successful complete run.

To rediscover the exact rational witnesses, run:

  python3 outputs/next-proof/analytic/generate_selected.py \
    outputs/pair-ranked-profile.json \
    --output-dir /tmp/ranked-analytic-regeneration \
    --lean-output /tmp/ranked-analytic-regeneration/SelectedProfileCertificate.lean

This generator uses rational atanh calculations only to choose candidate log
bounds. Their validity is subsequently proved by the independent lower-exp
polynomial certificate in Lean, so the discovery calculation is outside the
logical trust boundary. The generator's default saving is the exact a above.

The original five published Lean sources are unchanged. This is a separate
three-module proof bundle with seventeen new audited theorems.
