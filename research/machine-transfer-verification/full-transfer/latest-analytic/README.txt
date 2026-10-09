Pinned PR71/73 profile: actual real characteristic and conditional state cost
===========================================================================

Fresh Lean4.21.0 compilation passed all 66 printed axiom audits: 52 unchanged
dependency declarations and 14 Pr73 declarations. Only propext, Classical.choice
and Quot.sound occur. This is an instantiation of the previously developed
analytic/floor-transfer proof, not a new general analytic theorem. Of the 14,
power_term_identity copies a generic identity; 13 are profile-specific
certificate or transfer declarations. The build logs and manifest are retained.

Pr73ProfileReal.actual_power_characteristic_lt_one proves, without hypotheses,

  sum over the 26 literal rows of (n_t/W)*(t/m)^(1-a) < 1,

for m=575, W=135075665, rank mass=77666660475, deficit 1846900, maximum child 529,
and a=12854322426487/250000000000000000. The exact rational upper-bound gap is

  699597017858129667 / 4221114531250000000000000000000000000.

The actual real characteristic gap is at least this number; equality is not
claimed. Every log bound is proved by a 24-term lower exponential polynomial,
and every exponential upper bound by the existing 8-term polynomial/remainder
theorem. The generator discovers rational witnesses; Lean checks their validity.
No analytic enclosure hypothesis remains in the finite real inequality.

The candidate pr73-candidate.json is byte-identical to the public Git blob:
https://github.com/DominikScholz/integer-mult-bounds/blob/253ecc88faeed55a950c76026d1fe67a7f690123/research/round6-pr71/parameter-certificate.json
SHA256: f391f7cee5377ab148f3cecc223fd8111c3075578b1ee327610e4dd3e3468fb0

This preserves the full public schema, including accepted_moment, bit,
finite_bridge and preferred. The checker binds every literal width and
multiplicity, m, W, saving and mass directly to those bytes. It does not create
a normalized substitute certificate. SOURCE.json records both PR73 and PR71
pins. The public global kappa = 25707323052097/500000000000000000 is metadata here;
no complete multiplication-machine theorem at that kappa is asserted.

Pr73PhysicalCost.state_cost_bound also instantiates the already proved generic
state-indexed floor theorem. It requires explicit child width t*floor(e/m),
child volume V/W, nonnegative volume, uniform base cost B*V, and local work
C*V plus every indexed child's cost. It concludes a uniform A*V*e^(1-a) bound.
Those physical hypotheses are not discharged by this analytic package.

Credit: Chafik Boukhalfa's PR71 supplies the anchored split graph and composed
profile-cost live compiler. Dominik Scholz's PR73 retains those physical words
and refines the positive assembly backoff. They build on Rohan Garg's PR59
split operation, Rohan Arun's PR65 region orders and PR67 profile costs,
Dominik Scholz's PR68 live controls, Avi Eisenberg/ikeboy's PR62 interval/pair
graph, eumemic's PR57 compiler, and Chafik Boukhalfa's PR60 ranking, together
with the retained data geometry, complex-layer and assembly contributors.
The current proof specialization was prepared with OpenAI Codex assistance.
It claims no priority for the public finite construction.

https://github.com/CrocSwap/integer-mult-bounds/pull/71
https://github.com/CrocSwap/integer-mult-bounds/pull/73
All inherited licenses and notices remain applicable.

Reproduction from the research workspace, with installed Lean4.21.0/Lake on PATH:

  python3 outputs/full-transfer/latest-analytic/check.py \
    --lake-project work/agents/lean-foundations/formal/lean \
    --repository work/agents/repository-audit/pr73

The default dependencies are outputs/next-proof/analytic and
outputs/transfer-proof/recurrence. Their manifests and every source hash are
pinned. --analytic-dir, --recurrence-dir, --candidate and --output override
locations. The optional --repository rechecks the exact Git blob; otherwise
the pinned SHA256 still binds the candidate. No toolchain installation occurs.

  python3 outputs/full-transfer/latest-analytic/independent_review.py \
    --repository work/agents/repository-audit/pr73

This separate Fraction/Horner checker imports neither generator nor package
checker, and passed every literal witness inequality, profile identity and
final build receipt. Regeneration of Pr73ProfileCertificate.lean and
pr73-witnesses.json was byte-identical. Mutated candidate multiplicity and
changed Lean source were rejected, as recorded in negative-controls.json.
The finite-word/CRT checks belong to ../audit; none were repeated by this
analytic package. Existing PR68 and selected-profile deliverables are unchanged.
