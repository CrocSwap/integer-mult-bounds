# Proof: a closed form for E8 port counts in subspaces

## Setting

The setting is that of PR #6861 (`research/p104-e8-subspace-invariants`).
`F = F2^9`, `wt` is Hamming weight, `par(x) = wt(x) mod 2`, `x.y` is the
dot product, `1` is the all-ones vector and `E = ker par` is the even
hyperplane. The quadratic form is `q(x) = C(wt x, 2) mod 2`, with polar
form `B(x,y) = q(x+y) + q(x) + q(y) = wt(x) wt(y) + wt(x & y) mod 2`. The
radical of `B` is `<1>`, and `q(1) = 0`. The port set is

    P120 = { x : par(x) = 1 and q(x) = 1 }     (weights 3 and 7),

and `N(V) = |P120 ∩ V|` for a subspace `V`.

Fix a subspace `V` of dimension `e`. Write

- `R = { y in V : B(y,x) = 0 for all x in V }`, the radical of `B|V`, and
  `rho = dim R`;
- `delta = 1` if `1` lies in `V`, otherwise `delta = 0`;
- `q' = q + par`, so `q'(x) = C(wt x + 1, 2) mod 2`;
- `sigma = sum over x in V of (-1)^q(x)` and
  `sigma' = sum over x in V of (-1)^q'(x)`.

Since `par` is linear, `q` and `q'` are quadratic forms on `V` with the
same polar form `B|V`. For `y, y'` in `R`, `B(y,y') = 0`, so both forms
are linear on `R`.

Two identities are used throughout.

**(I1)** `B(x,y) = x . tau(y)`, where `tau(y) = y + par(y) 1`. Indeed
`x . 1 = par(x)`, so `x . tau(y) = x.y + par(x) par(y)`. The map `tau` is
linear with kernel `<1>`.

**(I2)** `sum over x in F of (-1)^q(x) = 32`. The weights with `q = 0`
are those congruent to 0 or 1 mod 4, which gives
`1 + 9 + 126 + 126 + 9 + 1 = 272` vectors, against `240` with `q = 1`.

## Theorem 1 (closed form)

Let `V` be a subspace of dimension `e` that is not contained in `E`. Then

    N(V) = 2^(e-2) + (sigma' - sigma) / 4,

    sigma^2  = 2^(e+rho) if q  vanishes on R, and 0 otherwise,
    sigma'^2 = 2^(e+rho) if q' vanishes on R, and 0 otherwise.

So `N(V) = 2^(e-2) + (s' - s) 2^(t-2)` with `t = (e + rho)/2` and
`s, s'` in `{-1, 0, 1}`. The number `s` is zero exactly when `q` is
nonzero on `R`, and likewise for `s'` and `q'`.

*Proof.* The indicator of a port is
`(1 - (-1)^par(x)) (1 - (-1)^q(x)) / 4`. Summing over `V`,

    4 N(V) = 2^e - sum (-1)^par(x) - sigma + sigma'.

`par` is a nonzero linear form on `V`, so the middle sum is zero.

Let `Q` be `q` or `q'`. Substituting `y = x + z`,

    (sum_x (-1)^Q(x))^2 = sum_z sum_x (-1)^(Q(x) + Q(x+z))
                        = sum_z (-1)^Q(z) sum_x (-1)^B(x,z).

The inner sum is `2^e` if `z` lies in `R` and `0` otherwise. Hence the
square is `2^e sum over z in R of (-1)^Q(z)`. As `Q` is linear on `R`,
this last sum is `2^rho` if `Q` vanishes on `R` and `0` otherwise. The
rank `e - rho` of the alternating form `B|V` is even, so `t` is an
integer. ∎

## Theorem 2 (constraints)

For every subspace `V` of dimension `e`:

**(a)** `e + rho <= 8 + 2 delta`.

**(b)** If `delta = 1` then `sigma' = 0`.

**(c)** If `e + rho = 8 + 2 delta` and `q` vanishes on `R`, then
`sigma = 2^(4 + delta)`, which is positive.

*Proof.* (a) By (I1), the `B`-orthogonal of `R` is the dot orthogonal of
`tau(R)`. Since `1` lies in the radical of `B`, it lies in `R` exactly
when it lies in `V`, so `dim tau(R) = rho - delta` and

    dim R^perp = 9 - rho + delta.

`V` is contained in `R^perp`, hence `e + rho <= 9 + delta`. As `e + rho`
is even, this is `e + rho <= 8 + 2 delta`.

(b) If `1` lies in `V` it lies in `R`, and `q'(1) = q(1) + par(1) = 1`.
So `q'` is nonzero on `R` and Theorem 1 gives `sigma' = 0`.

(c) Let `T` be any subspace on which `q` vanishes; then `B` vanishes on
`T` as well. For `r` in `T`, `q(x + r) = q(x) + B(x,r)`. Averaging (I2)
over translations by `T`,

    32 = (1/|T|) sum_x (-1)^q(x) sum_{r in T} (-1)^B(x,r)
       = sum over x in T^perp of (-1)^q(x),

because the inner sum is `|T|` when `x` lies in `T^perp` and `0`
otherwise. Take `T = R`. If `delta = 1` and `e + rho = 10`, then
`dim V = dim R^perp`, so `V = R^perp` and `sigma = 32`. If `delta = 0`
and `e + rho = 8`, then `V` has codimension one in `R^perp`, and `1` lies
in `R^perp` but not in `V`, so `R^perp` is the disjoint union of `V` and
`V + 1`. As `q(x + 1) = q(x)`, `sigma = 32/2 = 16`. ∎

## Theorem 3 (the bound and its equality cases)

For every subspace `V` of `F2^9` of dimension `e`,

    N(V) <= 2^(e-2) + 4.

Equality holds exactly in three cases:

1. `delta = 1`, `e + rho = 8`, `q` vanishes on `R` and `sigma < 0`;
2. `delta = 0`, `e + rho = 8`, `q` is nonzero on `R`, `q'` vanishes on
   `R` and `sigma' > 0`;
3. `delta = 0`, `e + rho = 6`, `q` and `q'` vanish on `R`, and
   `sigma < 0 < sigma'`.

Moreover `N(V) <= 64` when `e = 8`.

*Proof.* If `V` lies in `E` then `N(V) = 0`. Otherwise use Theorem 1.

`delta = 1`. By 2(b), `N(V) = 2^(e-2) - sigma/4`. If `e + rho = 10`,
then `sigma` is `0` or, by 2(c), `32`, so `N(V) <= 2^(e-2)`. Otherwise
`e + rho <= 8`, `|sigma| <= 16`, and `N(V) <= 2^(e-2) + 4` with equality
exactly in case 1.

`delta = 0`. By 2(a), `e + rho <= 8`. If `e + rho = 8`, then `sigma` is
`0` or, by 2(c), `16`, while `sigma' <= 16`. So
`N(V) <= 2^(e-2) + 4`, with equality exactly when `sigma = 0` and
`sigma' = 16`, which is case 2. If `e + rho <= 6`, then
`|sigma|, |sigma'| <= 8` and `N(V) <= 2^(e-2) + 4`, with equality exactly
in case 3.

`e = 8`. If `delta = 1`, then `rho >= 1`, `rho <= 2` by 2(a) and `rho` is
even, so `e + rho = 10` and `N(V) <= 64` by the first paragraph. If
`delta = 0`, then `rho = 0`, so `e + rho = 8` and `q` vanishes on
`R = 0`; by 2(c) `sigma = 16`, and `N(V) = 64 + (sigma' - 16)/4 <= 64`. ∎

## Corollary 4 (ports per dimension)

Let `N_e(S)` be the largest number of elements of a port set `S` in a
subspace of dimension `e`.

1. For every subset `S` of P120 and every `e`,
   `N_e(S) <= min(2^(e-1), 2^(e-2) + 4)`, and `N_8(S) <= 64`.
2. `N_e(P120) = N_e(P104) = min(2^(e-1), 2^(e-2) + 4)` for `1 <= e <= 7`,
   that is `1, 2, 4, 8, 12, 20, 36`. `N_8(P120) = 64` and
   `N_9(P120) = 120`.

*Proof.* A subspace not inside `E` has `2^(e-1)` odd vectors, which gives
the first term; Theorem 3 gives the second and the bound at `e = 8`. For
part 2, `CENSUS.json` lists one explicit basis for each `e = 1..7` whose
span contains the stated number of P104 ports; `verify.py` checks each by
direct enumeration. P104 is a subset of P120, so the same subspaces
attain the bound for P120. A hyperplane with 64 ports is found by the
census, and `N_9 = |P120| = 120`. ∎

## Why the bias is 4, and why the pattern stops at dimension 8

The bias `N(V) - 2^(e-2)` is `(s' - s) 2^(t-2)` with `t = (e + rho)/2`.
Theorem 2(a) caps `t` at `4 + delta`; the 4 is the Witt index of the form
that `q` induces on `F2^9/<1>`. At the cap, Theorem 2(c) gives
`sigma >= 0`: a subspace whose radical is as large as its dimension
allows has no negative character sum. Without 2(c) the estimates of
Theorem 1 alone would allow a bias of `+8`, from `sigma = -32` at
`t = 5` or from `sigma = -16, sigma' = 16` at `t = 4` with `delta = 0`.
With it the largest bias is `+4`.

At `e = 8` every subspace not inside `E` has `e + rho = 8 + 2 delta`,
because `rho` is forced to `2 delta`. Every such subspace is in the
`sigma >= 0` regime, so the bias is at most `0` and `N_8 = 64 = 2^6`
rather than `68`.

For `e <= 3` the bound `2^(e-2) + 4` exceeds the number `2^(e-1)` of odd
vectors, and at `e = 4` the two agree. Theorem 3 therefore also recovers
the saturation depth of PR #6861 Theorem 1: a saturated subspace of
dimension `e` needs `N(V) = 2^(e-1)`, which is impossible once
`2^(e-1) > 2^(e-2) + 4`, that is for `e >= 5`.

## Exhaustive corroboration

`verify.py` visits each of the 8,283,458 subspaces of `F2^9` once. For
the 7,866,259 that are not inside `E` it computes `N(V)`, `sigma`,
`sigma'` and `R` and requires every clause of Theorems 1 to 3. The
98 classes `(e, delta, rho, sign sigma, sign sigma', N)` and their sizes
are in `CENSUS.json`. This run is corroboration; the theorems do not
depend on it. Part 2 of Corollary 4 does depend on the seven explicit
witnesses and on one 64-port hyperplane, which are finite checks.
