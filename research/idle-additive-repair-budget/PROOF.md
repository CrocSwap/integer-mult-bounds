# An additive repair cannot pay for one idle-group consolidation

This is a scoped negative result for a concrete changed interface: retain the
original local and hosted calls, reassign the existing idle axes, and repair the
changed physical operator using additional recursive phase children. The
correction is charged **beyond the fixed original residual rank mass**. It is
not a proof against changing or absorbing work into the original calls.

## 1. The exact comparison model

Let `0 <= a <= 1/400`, `p=1-a`. The raw cost of a rank-`r` recursive child is
`r^p`, with `0^p=0`. Normalized cost is `(r/73)^p`. The same positive stock
division and all other invoice terms are held fixed on both sides.

One original replica/port group has at most twenty residual slots of integer
ranks `0 <= r_i <= 51`. Let `M=sum r_i` and `A=sum r_i^p`. The candidate
redistributes exactly this same residual mass into ranks at most 51. To give it
every advantage, permit even nonnegative real counts and real ranks: write
`A'=sum_j w_j s_j^p`, with `0 <= s_j <= 51`, `w_j >= 0`, and
`sum_j w_j s_j=M`. Any actual reassignment is included in this relaxation.

In addition, charge at least one actual repair child, of integer rank `q>=1`
and full multiplicity one. With several repairs let their raw cost be
`C=sum_l q_l^p`. We grant the repair exact arbitrary-input correctness and no
other overhead; in particular this favorable screen gives it free movement,
adapters and restoration. It does not construct such a free implementation.

The original local and hosted profile, stock, widths and normalization remain
fixed. Enlarging banks, changing original children, crediting repair rank against
residual mass, or sharing one repair across several groups requires a different
invoice. Nonnegative extra costs under the fixed invoice only worsen the result.

## 2. An all-parameter allowance bound

For every positive `s <= 51`, `s^p=s*s^(-a) >= s*51^(-a)`. Hence

```
A' >= M*51^(-a),
A-A' <= B(a) := sum_i (r_i^p-r_i*51^(-a)).
```

Rank zero contributes zero. For integer `1 <= r <= 51`, put
`t=a*ln(51/r) >= 0`. Since `1-exp(-t) <= t` and `r^p <= r`,

```
r^p-r*51^(-a)
 = r^p*(1-exp(-t))
 <= a*r^p*ln(51/r)
 <= a*r*ln(51/r)
 <= a*51/e.
```

The last inequality follows by differentiating `x*ln(51/x)`: its maximum over
positive `x` is `51/e`, attained at `x=51/e`. The exponential series gives
`e > 1+1+1/2+1/6 = 8/3`. Therefore, for `0<a<=1/400`,

```
0 <= B(a) <= 20*a*51/e <= 51/(20*e) < 153/160.
```

Each actual positive-rank repair child costs at least one raw unit, so

```
(A'+C)-A >= 1-B(a) > 7/160 > 0.
```

At `a=0`, both residual profiles cost exactly `M`; the repair costs at least
one, which also proves the strict stated margin. The normalized increase is
greater than `(7/160)*73^(-p)`, followed by any unchanged stock division.
Thus this additive repair cannot improve the fixed-stock recursive moment
inequality anywhere in the stated interval. This does not claim a new root,
a new kappa, or rejection of another supplier interface.

This is a written proof for every real `a` in the interval and every profile
in the declared model. The finite rational endpoint calculation is a control,
not the proof of the whole interval. No formal proof kernel has checked it.

## 3. Binding the source geometry and the proposed repair

The source base is `463113d675af7410ac91d53a4fed51ec6494eb9a`.
The unchanged DATA-PHASES recipes contain twenty idle positions at every one
of 112 ports, with full ranks only `0,8,16,32,48`. A valid hosted prefix removes
axes from these bases, so its residuals have at most twenty slots and ranks at
most 48. The retained halving guard permits new residual rank at most 51:
`2*51^2=5202 < 73^2=5329 <= 2*52^2=5408`.

The verifier authenticates all 2,717,280 decoded T740 fill rows through the
retained PR3148 payload hash, then reconstructs actual residual inventories for
owner replica zero at all 112 ports. Its actual endpoint allowance at `a=1/400`
is below the more permissive analytic bound. The generic twenty-slot theorem
also applies to any other valid residual partition meeting its premises; this
package does not independently rerun hosting/native/owner admission for all
other replicas or certify those partitions by a new full controller replay.

Crucially, the source coverage tool defines `idle_mass=total_mass-local_mass`.
The theorem above is **not** an allowance to insert a repair into that coverage
law and also reduce `M`. Here the repaired proposal is the literal one: assign
each original residual axis once, then insert correction operators in addition.
Its reassigned residual mass is still exactly `M`. All correction children are
extra to that mass. A controller that instead eliminates other existing paid
work has changed this hypothesis and must be priced separately.

## 4. A physical operator witness and the sharp insertion count

Use PR3148 owner replica zero, port zero. Move axis `v=16` from child 10 to
child 12, as in a component of the pinned PR3184 star. The donor and receiver
residual ranks change `48,48 -> 47,49`. The axis is in the donor residual and
is orthogonal to the receiver's full basis. The total rank mass and group axis
multiset are unchanged.

On the translation character `x=16` in `F2^73`, the canonical-cover baseline
eight-stream operator is `i I_8`. With zero-based indices the reassigned operator differs
from it at exactly

```
Delta[1,1] = -1-i,
Delta[3,1] = -1-i,
Delta[7,7] =  1-i.
```

The submatrix on rows and columns `{1,7}` has determinant `-2`, and the only
nonzero columns are 1 and 7. Thus its rank over `Q(i)` is exactly two.
These are operator identities on arbitrary inputs, including dirty streams;
no zero-state promise is used. The global phase is retained in `i I_8`.

An inserted single-stream phase child of any axis rank has, at a fixed
character, an eight-stream action `D=I+(z-1)e_s e_s^T`. If the retained prefix
and suffix are `A,B`, adding it changes the operator by
`B(D-I)A`, of rank at most one. At any cut this cannot equal the required
rank-two correction. Therefore at least two such insertions are necessary at
caller-level cuts in this exact retained-interaction example. It does not
cover edits inside an opaque recursive child's helper-coupled implementation.
The claim concerns completed
Fourier-diagonal single-stream phase insertions; it does not treat new
multi-stream interactions or an unpriced bundled decoder as one such child.

Two rank-one calls suffice algebraically: insert `C_v` next to the donor's
reduced residual phase and `C_v^-1` next to the receiver's enlarged phase.
Here `C_v` has eigenvalue `i^(x dot v)` at character `x`, so `C_v^4=I` exactly.
The donor phase is restored and the receiver's extra factor is cancelled.
This restores each affected original factor and hence the entire operator
for all `2^73` characters, including global phase. It simply repays and
reverts the transfer; it does not achieve a cheaper supplier.

The identity `C_v^2=X_v` also gives `C_v^-1=C_v X_v`. Thus the inverse is one
rank-one selected child plus the explicit rank-zero translation `X_v`, whose
movement is granted free in the favorable comparison of section 1. The
interpreter represents the inverse by three forward phase exponents to test
the same identity. The invoice charges one rank-one child and grants the
translation free, rather than charging three forward calls. No repeated-axis
list in this test is accepted as an orthonormal
residual basis. For the algebraic repair, the generous budget theorem already
loses with one added child, before charging its necessary second insertion.

## 5. Controls and precise reopening conditions

The source-bound replay rejects a wrong inverse, omission of either repair,
and acceptance based only on the unchanged axis multiset. A positive
single-insertion control has difference rank one. The retained interpreter is
reused; a separate specialist implementation independently checked the exact
operator witness. These are AI-assisted checks, not independent human review.

The independent integer-root routine encloses every `r^(399/400)`, `r=0..51`,
using exact integer-power bisection. It certifies the endpoint single-slot
maximizer `r=19` and four **positive relaxed-invoice** controls outside the
model: 22 original slots, half an actual repair call, one repair shared across
two groups, and repair rank deducted from original residual mass. These
relaxations are not claimed to realize correct operators. They demonstrate
why those hypotheses cannot be dropped from this budget argument.

The bounded investigation stops here. A constructive route can reopen it by
absorbing corrections into existing calls, replacing original interactions,
providing an actual shared repair across groups, changing the coverage/rank
contract, or studying another saving interval. Each needs a new complete
invoice and arbitrary-input restoration proof. This result supplies none of
those interfaces and establishes no general barrier to a larger kappa.

Credit: the source construction and physical-stream objection remain with
Rohan Arun, Jeremy Diviney, dcharb78, Marius-Paul Dumitrean, Jeremy Kothe,
Gonzalo-Mier, Gareth Davidson, Nick Petalas, Tekalign and the retained
word/native/geometry lineage. This scoped repair allowance and its exact
application were prepared by Ross Richardson with substantial OpenAI Codex
assistance and independent mathematical-specialist implementations.
New material is Apache-2.0; retained sources are unchanged.
