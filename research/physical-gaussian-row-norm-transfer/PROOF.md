# All-center contraction and unit-ball preservation for PR #3878

## Quantified interface

PR #3878, exact head `1a86a8fb73bb7a0982fff99852a031832c191902`, states the
physical tile contract for integer `p > 100`, integer
`2 <= alpha < sqrt(p)`, `u = alpha^2`, `1 < t/s < 2`, and its production-halo
hypotheses. Its exact normalized map is

```text
(A x)_v = (1/(2 alpha)) sum_(j in Z)
            exp(-pi (j - c_v)^2/alpha^2) x_j,
c_v = (s/t)v.
```

The `x_j` are periodic source labels and may be any complex values with
`||x||_infinity <= 1`. PR #3878 proves a uniform per-output error

```text
||T(x) - A(x)||_infinity < C 2^-p,
C = sqrt(2) + 2^-11.
```

This note independently proves the exact all-center row bound

```text
for every real c and every alpha >= 2:
  sum_(j in Z) exp(-pi (j-c)^2/alpha^2) <= 1 + alpha,
  ||A||_(infinity -> infinity) <= 1/2 + 1/(2 alpha) <= 3/4.
```

It then derives the local domain-preservation implication. For every `p >= 3`
and every unit-ball tile input,

```text
||T(x)||_infinity <= ||A(x)||_infinity + C 2^-p
                  < 3/4 + 1/4 = 1.
```

Thus PR #3878's stated `p > 100` is more than enough for the output of one
tile to satisfy the next tile's unit-ball numerical domain, if the caller
passes the values directly on a compatible grid. This is a local implication
only; it does not prove a full tensor schedule or any inter-axis precision
conversion.

## Proof of the row bound

Fix `c` and `alpha >= 2`, and put
`f(z)=exp(-pi (z-c)^2/alpha^2)`. Its values lie in `[0,1]`, and every strict
level set `{z : f(z) > h}`, `0 < h < 1`, is an interval. Any interval of
length `ell` contains at most `ell+1` integers. The layer-cake identity gives

```text
sum_(j in Z) f(j)
  = integral_(h=0..1) #({j in Z : f(j)>h}) dh
 <= integral_(h=0..1) (length({z : f(z)>h}) + 1) dh
  = integral_R f(z) dz + 1
  = alpha + 1.
```

The bound is uniform in the center `c`; no alignment of `(s/t)v` with the
source lattice is needed. With periodic labels, multiple terms can name the
same source coordinate, but all Gaussian weights are nonnegative. For any
input with `||x||_infinity <= 1`, the absolute output is at most the sum of
all those weights. Therefore the induced sup-norm bound for the periodic map
is the same row-sum bound. Dividing by `2 alpha` yields

```text
||A||_(infinity -> infinity) <= (alpha+1)/(2 alpha)
                              = 1/2 + 1/(2 alpha) <= 3/4.
```

For the error constant, `sqrt(2) < 10/7`, so
`C < 10/7 + 1/2048 < 3/2`. If `p >= 3`, then
`C 2^-p < (3/2)/8 = 3/16 < 1/4`. Combining this with the row bound proves
`||T(x)||_infinity < 1` for every unit-ball input. The deduction uses only
PR #3878's pointwise error premise and the exact row bound; it does not use
the implementation's separate output-norm assertion.

## Boundary controls and scope

The bound `alpha >= 2` makes the sufficient contraction estimate at most
`3/4`. At `alpha=1` the same estimate gives only `1`, so this proof route does
not establish a `3/4` contraction. This is a limitation of the estimate, not
a counterexample to the actual Gaussian row sum at `alpha=1`.

The error precision guard in the domain-preservation deduction also matters.
At `p=2`, the source constant obeys `C/4 > 1/4`; the abstract maps
`A(z)=3z/4` and `T(z)=3z/4+1/4` have error at most `C/4` on the unit disk but
`T(1)=1`. Thus a `<1` output bound does not follow from the row and error
bounds at that precision. For `p>=3`, the exact rational upper bound above
does imply it.

The live handoff at discussion #1166 comment `19010279` claims the larger
physical Gaussian tensor join. This result stops at the local all-center norm
and domain-preservation implication. It does not prove tensor-error
recurrences, tile routing, disjoint output coverage, coordinate moves,
precision conversion, tape/hosting costs, chirp composition, CRT or integer
recovery. PR #3877 already states a separate all-dimension recurrence for its
positive coefficient-rounded operator; that recurrence is outside this
audit.
