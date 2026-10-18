# Radix-9 coefficient-interface audit

This note audits the coefficient input to Chafik Boukhalfa's PR628, pinned at
`0768f97d06c623b8211e651543c66135796b62bf`. It uses a different exact construction
from that package's Machin-pi/Taylor-exponential interval engine. No defect was
found in the stated finite scope. This is an independent arithmetic path, not
independent human review or a proof-assistant theorem.

## Object and dependencies

For `u = exp(2*pi*i*k/9)`, `k in {1,2,4,5,7,8}`, the subject is

```
h_0 = 1,
h_j = h_(j-1)/(1-u^j),  1 <= j <= 8,
P_k(z) = sum_(j=0)^8 h_j z^j.
```

PR628's `interval_kernel.kernel(9,k)` encloses these coefficients by evaluating
the backward tail products using a 1536-bit interval approximation of the root
of unity. Its submitted factor rows for `(9,1)` and `(9,2)` are claimed to give
small coefficient residuals, which enter an inverse-operator perturbation bound.
The predecessor's independent closed-coefficient checks cover radices 4 and 8;
the present audit supplies an algebraic path for radix 9 and all its embeddings.

The subject and its original notices are copied byte for byte in `vendor/`.
`SOURCE.json` binds the Git head, original paths and SHA256 values. The full
original `FACTORS.json` is retained to make selecting its two radix-9 rows
reviewable; other radices are neither accepted nor audited by this checker.

## 1. Select the primitive root without pi or trigonometry

Let `t` be the unique root of

```
p(t) = t^3 - 3t + 1
```

in `(3/2,8/5)`. At the left endpoint `p=-1/8`; at the right endpoint
`p=37/125`. The derivative `3t^2-3` is positive throughout the interval.
Consequently a sign-changing bracket in this interval identifies exactly one
root. The checker bisects on a fixed integer grid `S=2^2048`, checking the
integer polynomial numerator at each comparison. It returns adjacent grid
points `a/S < t < b/S` and rechecks their strict signs.

Define

```
u = (t + i sqrt(4-t^2))/2,
```

with the positive square root. Then `|u|=1`, `Re(u)>3/4`, `Im(u)>0`, and
`u+u^-1=t`. The cubic identity implies

```
u^3 + u^-3 = -1,
u^6 + u^3 + 1 = 0.
```

Thus `u` is a primitive ninth root. The real and imaginary signs select the
root with angle between zero and `pi/3`; its cube is the upper primitive cube
root. It is therefore `exp(2*pi*i/9)`. This argument identifies the embedding;
no numerical value of pi, exponential or trigonometric function is evaluated.

For the imaginary part, monotonicity gives

```
sqrt(4-(b/S)^2) < sqrt(4-t^2) < sqrt(4-(a/S)^2).
```

The lower endpoint is bounded downward by
`isqrt(4S^2-b^2)/S`; the upper endpoint is bounded upward by
`(isqrt(4S^2-a^2)+1)/S`. Integer squaring checks those directions.
Dividing both real and imaginary intervals by two gives a rational rectangle
containing exactly the intended root. Subsequent arithmetic uses exact
`Fraction` endpoints without floating-point rounding.

## 2. Construct the coefficients in a cyclotomic field

Work in `K=Q[X]/(X^6+X^3+1)`, with `X` corresponding to the root above.
The modulus is `Phi_9`, so the six power-basis coordinates determine an
element uniquely. Multiplication reduces by `X^6=-X^3-1`.

For each of the six primitive embeddings use `u_k=X^k`. For `1<=j<=8`,
put `v=u_k^j`. Its order is either 3 or 9, hence `v^9=1`, `v!=1`, and
`sum_(a=0)^8 v^a=0`. Telescoping then gives

```
(1-v) sum_(a=1)^8 a v^a = -9,
(1-v)^-1 = -(1/9) sum_(a=1)^8 a v^a.
```

This includes `j=3,6`; it does not incorrectly require every `u_k^j` to be
primitive of order 9. Starting at `h_0=1`, multiply by this exact inverse for
each successive `j`. The checker separately verifies all eight inverse
identities and all eight recurrences for every embedding in the quotient
field. It also verifies `h_8=1/9` and the 27 conjugation identities pairing
embeddings `(1,8)`, `(2,7)` and `(4,5)`.

This construction uses forward division via a finite weighted geometric sum.
It imports neither the predecessor's tail-product code nor its arithmetic.
Exact rational interval Horner evaluation at the independently isolated `X`
then encloses each coefficient's real and imaginary components.

## 3. Audit the predecessor's enclosures by containment

For each embedding, the independent rectangle is required to be wholly
contained in the predecessor's rectangle, component by component. Merely
overlapping intervals would not suffice: both could overlap while the claimed
outer rectangle misses the true coefficient. Independent containment, together
with Sections 1-2, proves the claimed inclusion for these 54 coefficients.
All 108 real-component containment checks pass.

`EXPECTED.json` contains the isolating root rectangle and all 54 exact
six-coordinate field elements, in addition to the summarized comparisons.
For example, embedding 1 gives `h_4=X^4/3` and `h_8=1/9` exactly.

The exact algebraic coefficients and their enclosures are computed before the
subject module is loaded. That module is used solely to supply the rectangles
being audited. Its pi/Taylor implementation is not an oracle for the audit's
field elements, embedding choice, square roots or factor residuals.

## 4. Audit the two submitted factor certificates

For each submitted radix-9 row, expand the eight given dyadic complex roots
exactly to form

```
Q(z) = (1/9) product_(j=1)^8 (z-rho_j).
```

Check the declared dyadic representation limit and, using rational squared
moduli, the row's stable margin `beta`:

```
|rho| <= 1-beta             for an inner root,
|1/rho| <= 1-beta           for an outer root.
```

For every coefficient of `Q`, maximize the absolute difference against both
endpoints of each independent real and imaginary interval. Summing these
maxima bounds `||P-Q||_1`, because `|a+ib| <= |a|+|b|`. Round that bound upward
to the next power of two. Both submitted rows give

```
||P-Q||_1 <= epsilon = 2^-1020.
```

The remaining operator/scan analysis is inherited from PR628; this audit
checks its rational substitutions, rather than claiming another execution
replay or a new proof of its scan theorem. In its unit-shift model,
`A=9 beta^-8` bounds `||Q(W)^-1||`. With `A epsilon < 1`, the Neumann
perturbation bound gives

```
||P(W)^-1-Q(W)^-1|| <= A^2 epsilon/(1-A epsilon).
```

For unit-bounded input, grid `u=2^-w`, and
`alpha=beta^-1+7u beta^-3`, the predecessor's rounding recurrence has the
closed form

```
E_8 = 7u beta^-3 sum_(j=0)^7 alpha^(7-j) (9 beta^-j + 1).
```

The independent checker evaluates this sum exactly, checks
`u<=beta^2/2`, and rounds `E_8` upward to a power of two. It adds the
perturbation bound and checks the submitted `2^-128` target.

| Embedding | Inner / outer factors | beta | Coefficient residual | Execution bound | Combined bound |
|---|---:|---:|---:|---:|---:|
| 1 | 1 / 7 | 1/1024 | <= 2^-1020 | <= 2^-659 | <= 2^-658 |
| 2 | 0 / 8 | 1/128 | <= 2^-1020 | <= 2^-689 | <= 2^-688 |

These are conservative bounds on the existing 768-bit certificate settings,
not observed errors, new execution settings, or a performance improvement.
Reversing the roots preserves the result; conjugating all roots validates
the corresponding embeddings 8 and 7 as positive controls.

## 5. Adversarial evidence and limits

Fifteen mathematical mutations must fail at the named condition: wrong
embedding enclosure; omitted conjugation; a `2^-256` perturbation to the
seed-selected coefficient; and, for each submitted row, a unit-circle factor,
a missing factor, 128-bit working precision, a `1/16` root perturbation,
wrong factor embedding, and omission of the `1/9` normalization.
The seed selects coefficient `73 mod 9 = 1` and factor `73 mod 8 = 1`.
Valid conjugation and factor reordering are accepted, so the tests do not
merely require the original literal row to remain unchanged.

This is exhaustive over the six primitive radix-9 embeddings and both
radix-9 rows in the pinned certificate. It is not a parameter search,
an impossibility theorem, or a uniform verification over all radices.
No issue is alleged in PR628. Its scan analysis, factor-preparation
complexity, phase approximation, dirty restoration, routing, full-transform
composition and all multiplication interfaces remain outside the audit.
The inherited selected result is conditional and remains unchanged.

Prepared for William Lawyer with substantial OpenAI Codex assistance.
Attribution and related work are in `NOTICE.md`; no literature-priority,
independent human review, or formal full-theorem claim is made.
