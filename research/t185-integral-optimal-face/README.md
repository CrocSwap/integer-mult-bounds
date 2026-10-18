# Every integral minimizer of the T185 packing relaxation

For the fixed shared-kernel inventory of [Dugongue's PR2863](https://github.com/CrocSwap/integer-mult-bounds/pull/2863)
at `34328b1d5e5bebac62d5cabec993dfbfd7b2123f`, an abstract whole-bin packing
attains the existing fractional optimum **if and only if `5` divides its
positive replica count `T`**. There are exactly **`(21T+1)^2` optimal pattern
multiplicity vectors** at each such count. All have the same idle and complete
paid profiles. [PROOF.md](PROOF.md) gives the complete two-parameter family.

The smallest abstract attaining count is `T=5`, with 11,236 multiplicity
vectors; `T=185` has 15,100,996. These count vectors do not specify physical
owners or chronological schedules. PR2863 supplies the actual T185 witness;
this package supplies no new physical witness at T5 or any other count.

The result holds uniformly on the pinned primitive-saving root interval
`0.001720100805416885927944 <= a <= 0.001720100805416885927945`.
For other positive integer T, every feasible whole-bin packing has
unnormalized idle cost more than `1/250` above `T` times the fractional value.
A simple separately checked rounding witness shows abstract packings still
exist for every T. The divisibility obstruction concerns **exact attainment**.
No exact integer optimum at nonmultiples of five is claimed.

## What this adds

PR2863 already supplies the optimum, matching fractional primal/dual, eleven
tight patterns, existing root interval and literal T185 construction.
[PR2875](https://github.com/CrocSwap/integer-mult-bounds/pull/2875) independently
reproduces the construction and refines its displayed rational precision.
Neither is replaced here. The addition is the all-T integer optimal-face
classification, its exact count, and the uniform nonattainment gap.

The verifier imports no predecessor code. It grows helper multisets
recursively instead of using the predecessor's Cartesian census; encloses
powers directly by a positive binomial series instead of log/exp series;
and row-reduces the complete tight-pattern inventory matrix over the rationals.
It independently rechecks all 1,163 inequalities and both existing root signs,
then checks every smallest-count integer vector and eleven rejecting/falsifying
controls. This is a written proof and exact computational evidence by the same
AI-assisted author, not independent human or formal-kernel review.

## Reproduce

Standard library, Python 3.10 or newer; registered CI targets Python 3.12.

```sh
python3 -B scripts/research_package.py --package research/t185-integral-optimal-face
```

Direct replay is portable without Git or the rest of the checkout:

```sh
python3 -I -B research/t185-integral-optimal-face/verify.py
python3 -I -O -B research/t185-integral-optimal-face/verify.py
```

Both commands recompute and compare [RESULT.json](RESULT.json), without writing
artifacts. `--write-result` explicitly regenerates it. [SOURCE-EXPORT.json](SOURCE-EXPORT.json)
authenticates the five small original source exports with SHA256, length and
Git blob IDs. Generic runner provenance is in [SOURCES.json](SOURCES.json).
Validation details are in [VALIDATION.md](VALIDATION.md).

## Scope

This is a scoped packing side result. It does not improve kappa or discharge
source windows, distinct physical families, chronology, native circuits,
complete supplier admission, all-size compilation, precision/tape or outer
transfer. The optimum is conditional on the fixed inventory and capacity
contract; changed words or helper reuse can change the model. No selected cold
replay or Lean build is claimed.

## Open next questions

The structured question in [TASK.json](TASK.json) asks whether any member of
this abstract face can be realized at a smaller count than the existing T185
witness. That would clarify the physical replica overhead, without improving
the normalized profile. A feasible first step is to intersect the affine face
with the exact source-window and family constraints. Those constraints are
the blocker; this result does not authorize another broad packing search.

## Credit

Credit Dugongue/PR2863 for the model, optimum, dual and physical attainment;
Yiyang (Lyy-iiis)/PR2857 for the shared-kernel words; Marius-Paul Dumitrean/PR2856
for vacancy paths; PR2848/2855's concentration lineage; Jeremy Kothe/PR2833;
Philippe Van Velzen/PR2853; Tekalign and the retained compiler/owner contributors.
The original [NOTICE](source/NOTICE) is preserved byte for byte. Ali Romman's
PR1129 and the historical `selected-t16-pattern-dual` package already contain
replica-divisibility results for a different R480 inventory; this is their
source-specific successor, not a new general integrality method.

Arham Tahir with substantial OpenAI Codex assistance in derivation, code,
checking and writing. New material is Apache-2.0 under the repository license.
