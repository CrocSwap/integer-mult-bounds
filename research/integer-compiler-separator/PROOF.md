# Exact integer optimization of the compiler separator

This is a scoped proof about the two sufficient inequalities below. The
compiler induction, tail hypotheses and physical implementation are premises
from Cinna Davis's query-thinned-controller construction, not results proved
or audited here. Its native, owned-erasure, whole-job, precision, tape, stock,
analytic and recovery obligations remain.

## Model and result

Let `0 < U < C < 1`, `v >= 1` be an integer, and `h > 0`. Set

```
Delta = C-U,   a = v(8h-3),   D = 1+8vC,
e = Delta*a+D,   d = Delta*h.
```

For integers `H0,H1` and a real separator `x`, the fixed sufficient model is

```
H0 >= 8v,      0 < x < Delta,
H0*h*x >= (5+8h)*v*x + 1+8v(C-x),
H1*(Delta-x) > H0*(C-x).                    (1)
```

Here `x=z0-t`, `C=1-t`, `U=1-z`. The predecessor chooses
`x=Delta/2`. We optimize `x` and both integers, retaining exactly (1).
The theorem does not assert that (1) is necessary for any other compiler.

Put

```
y_star = (e + sqrt(D*U*e/C))/d,
y_min = floor(e/d)+1.
```

For each legal integer `y >= y_min`, define

```
x_y = D/(h*y-a),
F(y) = y*(C-x_y)/(Delta-x_y)
     = y*(C*h*y-C*a-D)/(Delta*h*y-e).
```

The exact minimum sufficient integer `H1` in (1) is

```
min_y (floor(F(y))+1),
```

where only the legal integers immediately below and above `y_star` need be
tested. If `y_star < y_min`, test `y_min` alone. An integer `y_star` needs
only itself, although testing its legal predecessor is harmless. A minimizing
candidate `y` gives the rational witness `H0=y`, `x=x_y`. Other integer
`H0` values can tie after rounding; uniqueness is not asserted.

## Proof

Rearrange the induction inequality in (1) to

```
(h*H0-a)*x >= D.                              (2)
```

Because `D>0`, a feasible pair must have `h*H0-a>0`. The existence of
`x<Delta` satisfying (2) is then equivalent to

```
H0 > e/d.
```

Moreover

```
e-8v*d = D-3v*Delta = 1+5vC+3vU > 0.
```

Thus `e>0` and every such integer `H0` automatically exceeds `8v`.
At fixed `H0=y`, the smallest permitted separator is `x_y`. The function

```
(C-x)/(Delta-x)
```

has derivative `U/(Delta-x)^2 > 0`. Therefore the minimum final threshold
occurs at `x_y`, including equality in the non-strict induction inequality.
The strict final inequality requires precisely
`H1 >= floor(F(y))+1`. In particular `F(y)>y`, so every feasible integer
pair has `H1>H0`.

Polynomial division yields

```
F(y) = (C/Delta)*y + (D*U/Delta)*y/(d*y-e).
F'(y) = C/Delta - D*U*e/(Delta*(d*y-e)^2).
F''(y) = 2*d*D*U*e/(Delta*(d*y-e)^3) > 0.
```

On the legal real half-line `y>e/d`, the unique stationary point is
`y_star`. The function decreases before it and increases after it.
Its minimum over legal integers is consequently at the two bracketing
integers, or at `y_min` when the real minimum is below that boundary.
Applying the monotone map `r -> floor(r)+1` preserves the minimum value.
This proves the theorem, including its rational attainment witness.

## Exact implementation

The implementation never approximates the square root. It finds the first
legal integer `k` satisfying

```
C*(d*k-e)^2 >= D*U*e.
```

It checks `k` and its legal predecessor. With
`S=D*U*e/C`, the initial right endpoint
`ceil((e+S+1)/d)+1` is beyond the root because `sqrt(S)<S+1`.
The binary search has at most the bit length of its initial interval plus
one iterations. The executable accepts positive rational `h<=1`, integer
`v<=4096` and fraction components of at most 256 bits. These are executable
resource bounds, not restrictions of the mathematical proof.

The separate interval oracle asks whether the original inequalities admit a
separator, without using the stationary-point formula. For fixed `y,H`, it
compares the closed lower endpoint from (2) with the strict upper endpoint

```
(H*Delta-y*C)/(H-y).
```

Every improving integer pair has `8v<=y<H<=H_best-1`. The small exhaustive
check therefore enumerates every possible `y` at `H=H_best-1`. Feasibility
is monotone in `H`, so this excludes every smaller `H` as well.

## Two concrete applications

Both use `v=1024`, `h=1/64`. The constants `C,U` are cited inputs; no
predecessor native invoice or tail is recomputed.

- Cinna Davis's merged BIT example has `C=.00346`, `U=.003459`.
  The midpoint gives `H0=3755884544`, `H1=25986965159937`.
  The new witness has `H0=3755518935`, `x=5868864/11736585471875`,
  `H1=25986964913670`, saving 246267 in the sufficient exponent.
- ai-nanachi's PR4814 has `C=.00347545806`, `U=.00347545805`.
  The midpoint gives `H0=377228190883840`,
  `H1=262208150916063859466241`. The new witness has
  `H0=377228190518280`, `x=11512090792/2302418156168798828125`,
  `H1=262208150916063859220003`, saving 246238.

These are improvements in the fixed sufficient exponent for `N=2^H1`.
They are not claims about a smaller eventual multiplication-input threshold,
runtime, a changed native word or a new kappa. PR4814's ordinary saving and
the selected frontier remain unchanged.

## Implementation constraints

`verify.py` has no recursion or dynamic code loading, and writes no files.
Its binary search has an explicit finite budget; the oracle has 36 fixed
parameter cases and checks a derived range capped below 10000 per case.
The entry validates exact fractions, sizes and domains. `need` contracts
remain active under optimized Python. Functions are below 60 physical lines.

Power-of-ten rule 3 has a managed-runtime deviation: Python's Fraction,
integer and JSON operations allocate during calculation. The executable
input caps, fixed fixture list, two candidate rows and bounded oracle keep
live data finite; no cumulative search history is retained. The standard
library's internal allocation is not instrumented. A fixed-capacity numeric
runtime would be needed if this verifier were ever moved to such an
environment. Rule 9's JSON `default=str` is one bounded standard-library
serialization callback. Warning-as-error normal and optimized runs are the
available interpreted diagnostics; no repository-wide analyzer configuration
is changed.
