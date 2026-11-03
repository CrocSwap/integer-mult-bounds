# Complete two-rate guard frontier for the selected P104 word

The source is the exact PR6030 WORD.json.gz at the main base in SOURCES.json.
It has 770 independent public inputs, 29 owned fields and 22803 events. Each
initial public field has Hilbert norm at most B. All frames and completed
native maps are unitary under the retained common-chart contract. COPY with
its coefficient, INIT and owned CLEAR/reset are exact. These are premises.

A native MOVE at guard b_N has completed defect at most 2^-b_N times its
actual input norm. An ADD at guard b_S has defect at most 2^-b_S times
(||actual destination||+|q| ||actual source||). A SCALE uses 2^-b_S times
|q| ||actual input||. Defects may be independent and adverse. This is the
retained relative-error interface with two rates, not a hardware rounding rule.

## Causal sufficient rule

Write ideal field values in the common chart as signed dyadic rows of the
independent initial inputs. Exact row substitution gives each local ideal
allowance A_j B and the maximum ideal field norm 850B. The verifier checks the
complete endpoint on all 799 logical coordinates during this calculation.

For each previous defect i, retain its exact signed coefficient in each
current row. If delta_i B bounds that defect, a current error row has bound
E_r B, where E_r=sum_i |c_ri| delta_i. Cancellation of the same defect is exact;
independent defects are bounded by the triangle inequality. MOVE changes the
unitary chart but not these scalar coefficients. COPY, SCALE and ADD apply
their actual signed coefficients. INIT and CLEAR delete the owned row.

At site j use feedback E_r for MOVE, E_r+|q|E_s for ADD, or |q|E_r for SCALE.
Set delta_j to the upward multiple of 2^-96 above

    2^-b_class (A_j + feedback).

Inject a new independent defect coefficient one. Causal induction proves all
computed row scores are upper bounds. This includes feedback from earlier
errors; a first-order calculation alone would not give the claim. The 96-bit
grid is checker arithmetic, not a physical precision or an uncharged resource.

All signed coefficients are represented exactly on a common dyadic scale.
The new integer evaluator checks every division is exact. Its uniform (16,16)
result equals the unchanged source evaluator at every final coordinate and
at the maximum prefix. A separate complete transpose reconstructs both chosen
profiles' final scores from their actual rounded local defect allowances.
Small independent rational substitutions check mixed rates and exact classes.

## Monotonicity and the complete frontier

The signed error coefficients depend only on the word. Every error score is a
nonnegative linear combination of earlier delta_i. Reducing either class rate
can therefore only reduce each new delta_j, by induction; upward rounding is
monotone. An exact class, with rate zero, is a lower bound for every finite
guard in that class. This remains true even though finite positive rates can
round up to one unit of the checker's grid.

The exact certificate checks these corners. Displayed decimals are only
readable approximations; RESULT.json stores each exact rational value.

| Native guard | Scalar guard | Maximum final public error / B |
| --- | --- | --- |
| 13 | exact class | 1.1498824543 |
| exact class | 15 | 1.6639937133 |
| 14 | 16 | 1.2611349245 |
| 14 | 17 | 0.9175019719 |
| 15 | 16 | 0.9937871706 |

Thus over **all nonnegative integer guards**, the rule passes exactly when

    (b_N >= 14 and b_S >= 17) or (b_N >= 15 and b_S >= 16).

Below native14, even exact scalar steps fail the rule. Below scalar16, even
exact native steps fail it. The remaining excluded corner is (14,16).
Monotonicity covers every other pair. The code also reconstructs the full
0..32 finite boundary from five finite corner checks. There is no inference
from a finite tail trend. Failure of this sufficient rule is not a physical
precision lower bound and does not construct an attaining error adversary.

Both passing corners have ideal-plus-error norm below 1024B at every prefix.
Owned errors return to zero through the exact reset premise. At t extra bits
in both classes, inductively scale the accepted defect bounds by 2^-t. The
new allowance is at most 2^-t times the old one, because earlier feedback also
shrinks. Consequently final error is less than B*2^-t for every integer t>=0,
without rerunning the fixed-grid calculation at each t.

## Complete guard bill and price dependence

There are 3453 native sites and 19265 scalar sites. Uniform guard16 charges
363488 guard bits across occurrences. The minimum sum of guard bits is

    3453*15 + 19265*16 = 360035,

which saves 3453. This is an allocation count, not runtime or a tape tariff.
The other Pareto corner (14,17) allows four times the uniform native defect
at the cost of one extra scalar guard bit. If native and scalar per-occurrence
guard prices are c_N and c_S, its bill is smaller exactly when

    c_N/c_S > 19265/3453.

At equality the two tie. More generally, compare the sums of arbitrary
positive per-occurrence prices in the two classes. The two corners suffice
for every positive additive guard price. Base target precision adds the same
constant to each schedule, so it does not change this comparison.

A physical backend must supply that price law and the completed relative
contracts, exact COPY/reset, range and movement bounds. The current result
constructs sufficient demands on that backend. It does not implement the
rounded child, change recursive rank invoices or establish a new kappa.
