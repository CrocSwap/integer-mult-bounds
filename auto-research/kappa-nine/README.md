# Targeting a conditional saving above 2^-9

Author: Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
This is an active research investigation, not a new multiplication result.
The selected published witness is unchanged. No merge, push or announcement
is part of this investigation.

## Objective and current progress

Investigate a credible route to kappa > 1/512, starting from reviewed PR82
at `3410b940aa26e5876202152dfa7c4f66451ee22c`. Establish the target budget,
screen joint-boundary optimization, different geometries/topologies, and
stronger recursive primitives, then pursue at most two promising construction
experiments. Seek a complete exact small example and a defensible scaling
argument. Report exact negative results where a branch fails; optimistic
arithmetic is not an implementation. Complex compatibility is mandatory
before claiming a path to the headline.

The bounded investigation found **no new multiplication witness or surviving
complete construction**. It produced an exact target budget, recurrence-cost
decomposition, compression/batching exclusions, a modern-ledger geometry
screen, and two exact negative block-label experiments. The experiments were
stopped at necessary geometry conditions, before inventing unproved side
circuits or extrapolating savings. See [the final assessment](ASSESSMENT.md)
for the ranking, scope, missing lemmas and recommended next experiment.

## Reproduction

```sh
python3 research/kappa-nine/target_budget.py --output /tmp/kappa9-budget.json
python3 research/kappa-nine/geometry_screen.py --output /tmp/kappa9-geometries.json
python3 research/kappa-nine/block_fano_obstruction.py --output /tmp/kappa9-fano.json
python3 research/kappa-nine/covariant_block_test.py --output /tmp/kappa9-covariance.json
python3 -m unittest discover -s research/kappa-nine -p 'test_*.py' -v
```

The script uses only the Python standard library and the repository's current
balanced assembly module. It verifies input hashes and reconstructs the entire
PR82 child histogram from the two component profiles. Exact root enclosures
are proved by integer powers, not floating-point logarithms. Floats are labeled
diagnostics. Ten tests cover enclosures, profile corruption, invalid children,
rank mass versus moment, the scope of the exclusions, independent determinant
replay, a destroyed-rank control, exact signed ranks and projector products.

The three files in `baseline/` are byte-preserved reviewed PR82 inputs, with
source URLs and hashes in `baseline/SOURCE.json`. Their finite-construction
audit is recorded in [the round-four review](../../docs/research/community-round4-review.md).
This experiment does not redo that compiler audit or the upstream theorem.

## Target and assembly

The current balanced assembly gives kappa < a/(1+a), so exceeding 1/512
requires a_bit > 1/511. At the retained beta=1/20 it also requires
a_complex > (20/19)/511. These are necessary conditions, not sufficient
network certificates.

For a concrete screening target, hypothetical savings a_bit=11/5000 and
a_complex=1/400 pass all 47 assembly inequalities with
kappa=1/512+1/10^9, using the current finite bridge. **Neither network is
supplied.** A changed dimension, role count, maximum child or scalar charge
requires recomputing the bridge; the hypothetical check does not waive that.

Write M(1-a)=sum_t (n_t/W)*(t/m)^(1-a). At a=1/511, PR82 has
M approximately 1.00088553625, whereas acceptance requires M<1.
The normalized rank deficit is approximately 0.0000240979.

The decomposition of the moment penalty M(1-a)-M(1) is approximately:

| Component | Target penalty |
|---|---:|
| Internal compiler calls, both axes | 0.000428390 |
| Auxiliary boundary calls, both axes | 0.000391132 |
| Data macros | 0.0000574985 |
| Fixed center/data-growth calls | 0.0000326141 |

Auxiliary costs dominate at the existing role count. That does not imply
their removal alone can achieve the target: the denominator W falls too.

## Exact fixed-mass screen

Let R=s/(Wm) be normalized total child width and r the maximum child. Then

    M(1-a) >= R*(m/r)^a.

At a=1/511, rejection follows from the integer inequality

    s^511*m >= (W*m)^511*r.

This holds for PR82's m=575, r=529, W=133289600 and s=76639673100.
At that same rank mass, even ideal regrouping needs a maximum child of at
least 568 to have any chance of reaching the target. Such a child has not
been constructed, and a larger maximum child also changes the depth/row
reservation bridge. The fixed-r ceiling is approximately a<0.000289011.

## Arbitrary role compression with unchanged boundaries is insufficient

Put N=C(23,3)*C(25,3). The data child inventory per N is
19 children of width one and two each of widths 21,17,481. Each axis h has
two fixed children of width one and two of width h-2 per data pair.
For R_h auxiliary roles per invocation, its boundary children are h and
m-2h per role. Its compiler rank mass is h*R_h+h*(h-1).

Grant arbitrary nonnegative real R_23,R_25 and pack all compiler rank mass
optimistically into h-wide children. This is more generous than a physical
implementation. The total numerator and W are affine in the R_h.
Every role's moment coefficient exceeds its unit contribution to W.
At R_23=R_25=0 the constant normalized moment is already greater than
1.00108305622. Thus **every nonnegative role-count pair fails** in this
relaxation; no finite role-count scan is needed.

Even erasing the fixed compiler return mass entirely leaves the unchanged
data/center profile above 1.00060479978. This stronger relaxation still
fails. Changing actual boundary profiles or their rank cost remains outside
this exclusion.

## Even ideal within-macro batching plus compression is insufficient

Grant a single full-rank child for every retained non-compiler macro:

- Two rank-528 data macros and one rank-one endpoint correction per pair.
- Two rank-(h-1) growth macros per axis and pair.
- One rank-(m-h) boundary macro per auxiliary role.
- Compiler mass as above, packed into h-wide children.

The rank-528 data macro is the existing 9 singletons +21+17+481 profile;
the rank-(m-h) boundary macro is the existing h+(m-2h) profile. For exponent
between zero and one, merging positive widths lowers their summed power,
so these replacements are optimistic lower bounds, not asserted algorithms.

Again every role coefficient exceeds one. The zero-role constant moment is
greater than 1.00027819607. Consequently **no amount of role compression and
within-macro batching reaches the target while retaining this rank ledger**.
If the fixed central overhead is additionally erased, the optimistic constant
falls below one (approximately 0.99979993964). This records a possible escape
from the screen, not a central-loss-removal construction.

The proof does not cover merging operations across macro boundaries, changing
central rank loss, new label geometry, different child volumes or different
transfer obligations. It does not establish a ceiling on integer multiplication.

There is a stronger screen when the existing auxiliary injection contract is
retained: every label has a distinct auxiliary source port, so R_h>=v_h.
With that floor, **even erasing all fixed center loss** and granting perfect
within-macro batching leaves a target moment above 1.00007003731. Further
roles increase the numerator by more than their volume contribution. Thus
central-loss improvements alone cannot rescue this fixed geometry and these
obligations; a cross-boundary approach must change another part of the ledger
or eliminate the distinct-port requirement legitimately.

## Consequence for selecting experiments

Do not spend a construction slot on more compression or basis optimization
that stays inside the excluded ledger. Cross-boundary work must explicitly
change that ledger, rather than improve only the legal scheduling search.

The completed geometry comparison rescores specified two-field cores against
an explicitly optimistic modern two-stage/copying ledger. Historical
three-stage and singleton-transfer ceilings were not reused. For new cores,
that ledger remains a hypothesis: it does not supply a compatible auxiliary
circuit. Older routing screens also require matching their actual all-role
contract; copied or restricted workspace is not automatically an additional
independent input or a free child.

The two selected construction experiments were rank-two labels in dimension
14, followed by fully permutation-covariant rank-two labels in dimensions
15 and 16. Each has favorable optimistic moment budgets at ground size 16.
Both failed exact necessary geometry tests. No third construction experiment
was launched. The proposed unrestricted continuation is documented separately
as future work, not presented as a surviving implementation.
