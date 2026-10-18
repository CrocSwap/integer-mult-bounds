# Scope and exact algebra

Fix one non-center helper h and k in Z. Let D multiply its entire scalar register
by2^k and leave every other data, helper and center coordinate fixed. An ADD
`t += q*s` becomes `t += (q*2^(k_t-k_s))*s`, where k_h=k and all other k_i=0.
Each existing SCALE commutes with D and is left literally unchanged. Clear/COPY
events have no incidence with h by the definition of the477-helper domain.

For chronological original operations A1,...,Am, the new chronological word is
D, DA1D^-1,...,DAmD^-1,D^-1. Its matrix is

```text
D^-1 (DAmD^-1) ... (DA1D^-1) D = Am ... A1.
```

This equality holds on all input vectors, including arbitrary helper dirt. It
does not assume a helper is initially zero. The stored backward program is
checked independently; the inverse-transpose coefficient rule changes the
chosen basis to D^-1 (k=+2), in the same chronological direction, rather than
naively reusing k=-2. Both candidate and original forward transfer are
`Y += X`, and both backward transfers are `X -= Y`, preserving480 helpers and
clearing8 centers. The sparse rational replay includes each center's initial
dirty column, not merely zero center initialization.

All unchanged non-scalar operations act linearly on an individual register;
uniform scalar multiplication commutes with them. Center operations act on the
separate C registers. Excluding helper COPY sources ensures they commute too.
The selected candidate h427 starts in frame0 and ends in FULL frame1, and has
no residual wrapper. Its entry scale is after the zero-precondition phase
marker; the exit is after full-frame cleanup, before the done marker. This is
why the concrete stream requires no new frame climb or wrapper. Coefficient
changes use the original operands and frame labels. Native type/admission
replay and the complete hosted/compiler invoice remain separate obligations.

# Actual retained cost, including the unit discontinuity

For reduced q with |q|=p*2^e and positive odd p, Sagar Thakrar's retained
copy-init lowerer emits

```text
c(p,e) = 2 + floor(log2(p)) + popcount(p) + |e| - 1[p=1 and e=0].
```

The shortcut at q=+1 or-1 costs2: signed direct ADD followed by work clear.
Otherwise COPY initializes work from the source; numerator Horner steps, any
denominator halvings, signed accumulation and final clear are all charged.
The old Horner formula is `3+floor(log2(p))+popcount(p)+|e|`.
SCALE by a signed power of two costs `|e|+1[q<0]`. New boundary scales are
positive and cost2|k| in total, per real component. Real and imaginary words
each incur this complete cost.

For each ADD incident with h, set s=+1 when h is its target and s=-1 when h is
its source. The exact change is

```text
Delta_h(k) = 2|k| + sum_g ( c(p_g,e_g+s_g*k) - c(p_g,e_g) ).
```

No unchanged SCALE or disjoint ADD contributes a delta. Complete invoices
nevertheless recount them, and also count all clears/COPYs. The coefficient
work is arbitrary on entry: non-unit COPY overwrites it; unit direct ADD does
not read it; every macro clears it on exit. The independent checker executes
the predecessor's literal primitive words, including that work register.

# Why finitely many exponents certify an unbounded optimum

Let B={0} union {-s_g*e_g}. All absolute-value slope changes and all negative
unit discounts occur at integer points of B. Between consecutive points the
undiscounted objective is affine and there are no discounts. An affine function
attains its minimum at an endpoint (or is constant); the possible negative
discounts at endpoints only strengthen this conclusion. Outside the extreme
points every absolute-value term has the same outward slope, so the objective
increases with slope `2 + number_of_incident_ADDs`. Therefore at least one global
integer minimizer is in B. The method does not assume convexity of the discounted
function and is not simply a weighted-median argument.

The certificate prices every B point for all477 helpers, including k=0, in both
orientations. It uses (cost,|k|,k) to resolve per-helper ties and then helper index
for global ties. The independent method enumerates *every* integer from two
below to two above the extreme valuations and derives the outward slope using
the actual lowerer's lengths. It agrees with every per-helper certificate row.
The unique global winner in each orientation is h427, with123 incident ADDs;
forward costs at k=-4,-3,-2,-1,0,1 are75,-46,-166,-128,0,132 relative to baseline.
The backward list is reflected. No exponent cutoff assumption is used.

The pure unit-discount control has two incident coefficients1/2: the continuous
absolute-value objective is constant between k=0 and1, so the lower weighted
median is0; the correct discounted price strictly prefers1 by2 primitives.

# Prefix and admission boundary

For the source-bound positive scalar envelope, each original L/C register starts
with majorant1, clears set it to0, COPY copies it, SCALE multiplies by|q|, and
ADD replaces the target majorant by target+|q|*source. During non-unit numerator
Horner construction, the work majorant is at most |numerator(q)|*source before
denominator halvings. Unit direct ADD does not touch work until it clears.
Starting coefficient work at arbitrary unit majorant1 covers its dirty entry.
This exact rational recurrence accounts for every emitted primitive's absolute
coefficient majorant. Its complete maximum is unchanged at52/68bits, below192.

These are scalar-majorant and exact map certificates for one finite provider
word, with actual retained lowering. They are not a rerun of the native checker,
global512-bit accounting, row inventory/packing admission, or the outer root.
The477-helper cost optimum fixes all other coordinate scales; joint scaling,
center normalization, phase-varying diagonals, stage retiming and coefficient
work persistence lie outside the class. The current selected result is retained.
