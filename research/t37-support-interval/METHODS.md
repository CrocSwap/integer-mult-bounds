# Finite certificate methods

These arguments justify the finite premises of the theorem in `README.md`.
They do not replace its continuum proof or establish physical feasibility.

## Complete bin coverage

The primary checker uses one Cartesian product for each capacity `c`.
A helper of width `w` has a count between zero and `floor(c/w)`.
Every feasible count vector lies in this product.
The total-width filter removes exactly the infeasible vectors.
Maximizing the signed price within each residual class therefore computes `u(r)` exactly.
The receipt retains a maximizing pattern for each class.

The independent checker instead computes the largest price `D(m)` of an ordered helper sequence with total width `m`.
It starts with `D(0)=0` and marks other masses as unreachable.
Its recurrence is

```text
D(m) = max_(w <= m, m-w reachable) [price(w)+D(m-w)].
```

Every nonempty sequence has a final helper.
Removing it gives a sequence at a smaller mass.
Conversely, appending that helper constructs a sequence of mass `m`.
Induction therefore proves the recurrence for every mass through 48.

Ordering does not change a multiset's mass or price, and every multiset has an ordering.
Thus the recurrence and Cartesian enumeration cover the same bin patterns through different states.
For each capacity, the independent checker adds its bonus to `D(c-r)` and then maximizes over capacities.
It compares all table entries and their complete rank domains with the primary receipt.

## Integer radical enclosure

For positive rational `x=a/d` and `b=p/q`, put `S=2^128` and

```text
N = a^p*S^q,
D = d^p,
h = floor_root_q(floor(N/D)).
```

Integer bisection finds `h`.
The checker then verifies the exact inequalities

```text
h^q*D <= N < (h+1)^q*D.
```

Taking positive `q`th roots proves

```text
h/S <= x^b < (h+1)/S.
```

No floating operations enter this enclosure.
Signed interval arithmetic then encloses every `F_r(b)`, including negative credits.
Strictly positive lower bounds and strictly negative upper bounds determine the required signs.

## Independent logarithm and exponential enclosure

The independent checker uses scale `S=2^160`.
Dyadic range reduction writes each rational base as `2^k*y`, where `1<=y<2`.
It also computes an enclosure of `log(2)`.

For `1<=y<=2`, set `z=(y-1)/(y+1)`, so `0<=z<=1/3`.
The atanh expansion gives

```text
log(y) = 2*sum_(j>=0) z^(2*j+1)/(2*j+1).
```

The first 80 terms give a lower bound.
Every remaining denominator is at least 161.
A geometric sum therefore bounds the tail by

```text
2*z^161 / (161*(1-z^2)).
```

All series terms and the tail are exact rational numbers.
Multiplication by `k` and addition enclose `log(x)`.
Rounding the lower endpoint down and the upper endpoint up preserves the enclosure at integer scale.
The same outward rounding encloses `b*log(x)`.

All evaluated exponential arguments lie in `[0,4]`; an explicit guard checks this domain.
For the Taylor sum through term 90, let `L_j` and `U_j` enclose the scaled term `S*x^j/j!`.
The integer updates are

```text
L_j = floor(L_(j-1)*lo/(S*j)),
U_j = ceil(U_(j-1)*hi/(S*j)).
```

Nonnegativity proves these enclosures by induction.
Starting at the constant term, summing the lower and upper terms encloses the partial sum.
The next term has upper bound `ceil(U_90*hi/(91*S))`.
Every later term ratio is at most `4/92`.
Multiplying that next-term bound by `92/88`, rounded upward, bounds the full remaining tail.

For `0<r<48` and `b>0`, the denominator `48^b-1` is positive.
The checker requires a strictly positive lower endpoint before division.
It divides the numerator's lower bound by the denominator's upper bound, and conversely for the upper bound.
This encloses the normalized support expression

```text
925*r*((48/r)^b-1)/(48^b-1) - v(r).
```

Its sign equals that of `F_r(b)`.
This calculation shares neither the radical enclosure nor the primary enumeration.
The separate monotone-ratio proof in `README.md` checks the step from these finite signs to the full continuum.

## Exact premises and limits

The primary certificate checks every noncritical attainable rank at `b=2/3`.
Both implementations independently check rank 32 at `16/25` and `13/20`.
These are sufficient premises for the analytic proof; they are not a numerical grid search.
The two implementations also check the countermodel equations.

The proof uses the fixed inventory and inherited signed prices recorded in `README.md`.
`SOURCES.json` binds the predecessor documents and construction records consumed for those inputs.
No claim extends to changed helper widths, bin capacities, call counts, or source interfaces.
An alternative signed-price inequality could remove the relaxed countermodel from a stronger relaxation.
Thus the sharp boundary here does not establish a physical ceiling beyond the interval.
