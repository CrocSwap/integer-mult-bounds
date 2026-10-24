# A lower bound for the retained Gaussian inverse normalization

## Scope

This result concerns the exact Gaussian sampling map `T` in
`upstream/build/sections/07-resampling.tex`. The retained manuscript
pin is `adc7f1241b42e322a6451854ab7e4b4c146bf78a`. The inspected
vendored section is at checkout
`a900f98be8ff2c09d3292b5112d4731dbd0c8438`; its byte hash and Git
blob are in `SOURCE-MANIFEST.json`.
The later phase-cell and microbox inverses retain this Gaussian map
and the arbitrary-input disk contraction interface.

The result proves that any complete left inverse of the tensor sampler
needs `Omega(d*u)` normalization bits, where `u=alpha^2`. This includes
a joint inverse which does not factor by axis. A sharper estimate of
the complete inverse norm cannot replace this charge by `O(d log p)`
when `u` is a positive power of `p`.

This result does not exclude a different sampler, a different precision
or representation contract, or an algorithm with a new proved restriction
on input and error directions. It is not a lower bound for all integer
multiplication algorithms.

## Exact column bound

For coprime integers `3 <= s < t` with odd `s`, and `u >= 1`, the
periodic Gaussian map has matrix entries

    T[k,j] = sum over v in Z of exp(-pi*u*(t*j/s-k+t*v)^2),
    0 <= j < s, 0 <= k < t.

This is the unit-column form of the exact source definition; the input
coordinate `u_j` is periodic modulo `s` in that definition. Let `e_j`
be a unit coefficient vector, which is an allowed disk input.

Multiplication by `t` permutes the residues modulo `s`. Choose `j` so
that `t*j mod s = (s-1)/2`. Its nearest-integer phase is

    beta = (s-1)/(2s), with 1/3 <= beta < 1/2.

For every integer output index `k`, choose its closest periodic Gaussian
image. Let its distance be `delta`. Then `beta <= delta <= t/2`.
The remaining images, in either direction, have distances at least
`t*(ell-1/2)`, for integers `ell >= 1`.

Put `v=ell-1`. Since `t >= 3` and `beta^2 <= 1/4`,

    t^2*(ell-1/2)^2-beta^2
    >= 9*(v+1/2)^2-1/4
    = 9*v^2+9*v+2 >= 2+v.

The main image contributes at most `exp(-pi*u*beta^2)`. The remaining
images, relative to that main upper bound, contribute at most

    2 sum over v>=0 of exp(-pi*u*(2+v))
    = 2*exp(-2*pi*u)/(1-exp(-pi*u))
    < 2*2^-6/(1-2^-3) = 1/28,

using `u >= 1`, `pi > 3`, and `exp(1) > 2`. Thus

    ||T e_j||_infinity < (29/28)*exp(-pi*u*beta^2)
                      < 2*exp(-pi*u*beta^2).

The two classical constant bounds do not need a numerical approximation:
an inscribed regular hexagon gives `pi > 3`; the series for `exp(1)`
has sum greater than `1+1+1/2 > 2`.

## Every full left inverse has a large norm

Let `L` be any complete linear left inverse, so `L T = I`. The source
uses `L = D N^-1 C`, and verifies this identity before normalization.
The unit column above gives

    1 = ||L T e_j||_infinity
      <= ||L||_infinity * ||T e_j||_infinity.

Consequently

    ||L||_infinity > (1/2)*exp(pi*u*beta^2)
                  >= (1/2)*exp(pi*u/9)
                  > 2^(u/3-1).

This bound uses the complete inverse and its actual scalar identity.
It does not multiply loose norm bounds for internal factors.

For `d` tensor axes, choose the corresponding unit column on each
axis. The infinity norm of their sampled tensor product is the product
of their column norms. Hence any complete left inverse of the tensor
sampler, even a joint non-factored inverse, has norm greater than

    2^(d*(u/3-1)).

To make this inverse a contraction on arbitrary disk coefficient
inputs, a dyadic normalization `2^-gamma` therefore needs

    gamma > d*(u/3-1) >= d*u/4, when u >= 12.

An approximate inverse with `||L T-I|| <= 1/2` has the same bound
with one additional normalization bit: its selected unit output has
norm at least `1/2`. Thus `gamma >= d*u/4` also follows for `u >= 24`.

## Consequence for the current analytic route

The retained map uses `d=Theta(p^epsilon)` and `u=Theta(p^r)`.
The retained proof uses a sublinear normalization exponent `gamma=o(p)`.
The lower bound makes `epsilon+r < 1` necessary for that sublinear
condition. Equality prevents `gamma=o(p)`. A larger sum forces
superlinear normalization and therefore cannot use the retained `O(p)`
precision.

There is a distinction at equality: a new constant and recovery analysis
might support `gamma=Theta(p)` with `O(p)` precision. This note does not
exclude that boundary case. It proves `epsilon+r <= 1` as a necessary
exponent condition for `O(p)` normalization with this sampler, and
strict inequality for the current sublinear-normalization proof.

The phase-cell implementation reduces computational work to
`O(Tp*(d*p^delta + p^(1-r+delta)))`. Its boundary margin is at most
`r`. The compact phase layer has margin `epsilon*q`, with `q <= 1`
for a full-stream local supplier. These retained terms therefore give

    kappa < epsilon*q <= epsilon,
    kappa < r <= 1-epsilon,
    kappa < 1/2.

The new polylogarithmic spectator theorem removes the short-width
routing condition. It does not remove this analytic obstruction.
Increasing kappa toward one requires a new paid compact/analytic
construction that changes these actual interfaces. It cannot result
from tighter factor pricing or parameter selection alone.

The retained `b < 1/32` and `r < 1/4` numerical guards give smaller
current-model ceilings. This argument does not remove either guard.

## Reproduction and credit

`verify_gaussian_normalization.py` uses exact rational arithmetic.
It constructs every selected phase for 227 coprime size pairs, checks
the nearest periodic distances and the tail inequality, and records the
nonnegative polynomial coefficients which certify the tail comparison
for every alias. The proof, rather than the finite cases, establishes
the all-size bound. Run `python3 -B verify_gaussian_normalization.py`.

The Gaussian maps and Fourier identity are credited to Harvey and
van der Hoeven, as carried in the OpenAI manuscript and its retained
licenses. The efficient inverse and normalization interfaces are
credited to the RaD project, PR20/23 and their retained notices. This
note only supplies the unit-column normalization obstruction. It
claims no literature novelty or full multiplication theorem.

Prepared with OpenAI Codex assistance. Apache-2.0.
