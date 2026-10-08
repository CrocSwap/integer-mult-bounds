# Independent review of the reusable circular-banded Gaussian inverse

The complete proposed analytic transfer passes this review. The sharp row
estimate, reused exact-rational setup, rounded banded/Woodbury application,
normalization, guard refinement, and prime replacement are mutually
compatible. This remains conditional on the retained upstream multiplication
theorem and on separate finite-circuit realization certificates. It does not
claim an unconditional new multiplication theorem or global optimality.

Campaign interval: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned reference: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.
The reviewed proposal is
[downstream-reusable-banded-inverse.md](downstream-reusable-banded-inverse.md).

## Row bound and truncation

The rational nearest-rounding exponents satisfy

```text
phi(j,+1) >= 1+2theta+2beta_j,
phi(j,-1) >= 1+2theta-2beta_j,
phi(j,delta) >= rho^2 delta^2-rho|delta| >= delta^2-|delta|.
```

For the first two inequalities, inspect whether the nearest integer moves
one or two steps; the additional term in the second case has the correct
sign by the nearest-rounding threshold. For the general bound, use
`|rho delta+beta_j|>=rho|delta|-1/2` and `|beta_(j+delta)|<=1/2`.
This also covers all periodic aliases.

The sum of the two nearest weights is convex in `beta_j`; its maximum
is `exp(-2pi*u*theta)*(1+exp(-2pi*u))`. The remaining two-sided lattice
tail is less than `4exp(-2pi*u)` for `u>=4`. Thus
`||E||<exp(-2pi*u*theta)+5exp(-2pi*u)`. Under
`u>=ceil(log2(8p))`, `theta>1/(4p)`, and `p>100`, this gives gap
`mu=min(u*theta,1)/4>=1/(4p)`. The elementary bounds `pi>3` and
`e>2` suffice for the constants; the contraction does not depend on a
floating-point threshold.

With `w=ceil(sqrt(16p/u))+2`, the omitted lattice tail is below
`4*2^(-3u*w*(w+1))<2^(-46p)`. Downward real dyadic coefficients
preserve the original row-dominance gap. Subtracting two work-grid units
from an approximation with error below two units, then clipping at zero,
gives error below four units and cannot enlarge an off-diagonal entry.
The dyadic truncated matrix `H0` therefore has inverse norm at most
`4p`. Its difference from the exact periodic matrix is bounded by
`8w*2^(-P)+2^(-46p)`. The stated inverse perturbation bound follows.

## Exact elimination and circular correction

Removing the wrap entries only increases the diagonal-dominance gap.
For a Schur step eliminating pivot `k`, the triangle inequality gives

```text
gap_i_new >= gap_i+|a_ik| gap_k/a_kk,
row_norm_i_new <= row_norm_i-|a_ik| gap_k/a_kk.
```

Positive diagonal entries persist, every pivot is at least `mu`, and
every Schur row norm remains below two. The band widths do not grow.
Writing `A=L U`, these invariants give `||U||<2` and
`||L||<=1+2w/mu<=9p^2`. The identities
`L^-1=U A^-1` and `U^-1=A^-1 L` establish the stated polynomial
factor inverse bounds independently of the line length.

For boundary-selector columns `B`, write `H0=A+B V`. The correction
uses `Z=A^-1 B` and `K=I+V Z`. The exact identity
`K^-1=I-V H0^-1 B` proves nonsingularity and controls its norm.
The application `A^-1 b-Z K^-1 V A^-1 b` has the correct Woodbury
orientation. Both boundary sides are included; no periodic alias is
implicitly identified with a noncyclic band entry.

All setup matrices can be dyadic/rational. Standard determinant bounds
control their reduced numerators and denominators by a fixed polynomial
in line length and precision. Long exact records are allowed in setup.
Exact elimination, even implemented inefficiently by ordered fixed-tape
scans, takes a fixed polynomial in `s,p`. There is one setup per tensor
axis, reused across all its input lines. Since `s<=2^Theta(p/d)` and
`d=Theta(p^epsilon)` grows, the combined setup is `n^o(1)`.
Charging it once per input line would invalidate this argument; the
reviewed construction explicitly reuses it.

## Rounded solve and fixed-tape cost

The rounded reciprocal of a pivot is greater than one quarter. Replacing
the pivot by the reciprocal's effective diagonal changes it by less than
eight work-grid units. The triangular matrix perturbations are at most
`p*eta` and `2p*eta`, and their product differs from `A` by less than
`22p^3*eta`, with `eta=2^(-256p)`.

Accumulate each row's dyadic dot product exactly at `2P` fractional bits
and sufficient integer guard bits, then round its completed coordinate.
The forward and backward solves consequently satisfy perturbed triangular
equations with local residual norms below `2eta` and `8eta`. Applying
the polynomial factor inverse bounds to these residual vectors gives
the proposed loose bound `2^25*p^9*eta`; it avoids an exponential loss
from successively estimating each individual row error. The computed
noncyclic solution stays below `5p` in norm.

The three Woodbury factors have norms bounded by `1,4p,5p`; their
rounded dense rows have polynomial length. Propagating the noncyclic
solution error and the completed-row residuals gives a bound below
`2^32*p^11*eta`. The retained simpler interface

```text
||computed_x-N^-1 b||
 < 2^40*p^14*2^(-256p)+16p^2*2^(-46p) < 2^(-p-10)
```

has ample exact margin for `p>100`. Intermediate magnitudes are
polynomial in `p`, requiring only `O(log p)` integer guard bits.
Internal records, exact products, and accumulators thus use `O(p)` bits.

A band dot product scans and rewinds a length-`w` buffer. The dense
boundary correction scans its length-`2w` vector once for every row of
`Z`. These operations take `O(swp)` tape steps. The dense small solve
takes `O(w^2 p^(1+delta))`, included in the line bound because the line
length is superpolynomial in `p`. Factor tapes are rewound between
input lines at the same `O(swp)` cost. A fixed collection of tapes and
sequentially stored counters suffices; there is no head per coordinate,
axis, or buffer entry. The resulting application bound is
`O(t p^(3/2+delta)/alpha)`. Short scalar products use the published
unconditional integer multiplier, with no dependency on the new main
multiplication bound.

## Normalization, guard, and prime interfaces

The new inverse normalization `2^j`, `j=ceil(log2(32p))`, gives norm
below `1/8`. Along with `S/2` and `D/2^(2u)`, the exact identity has
scale `2^(2u+j+1)`. The completed routines retain disk-grid outputs and
the convenient `p^2` error allowance. Tensor normalization is therefore
`gamma=d(2u+j+1)`, including the logarithmic inverse scale. With
`u=Theta(p^(1/3))`, the Gaussian normalized cost is
`p^(1/2+delta+epsilon-1/6)` and sublinear normalization requires
`epsilon+1/3<1`.

The guard refinement preserves the existing constant `C0=128mB^2`.
The actual one-piece depth is `9B^2 d^(5-4beta)`. The number of pieces
is at most `5m d^(1/4)`. For `beta>=15/16`, their combined depth is
at most `45mB^2 d^(3/2)`; the remaining `18d` charge fits within
`63mB^2 d^(3/2)<C0 d^(3/2)`. Hence the changed guard exponent is
`C1=3/2`, and its sublinear reservation is compatible with
`epsilon<2/3`.

The prime replacement is a genuine new dependency. Baker, Harman, and
Pintz's Theorem 1 supplies a prime in every sufficiently large interval
`[y-y^(21/40),y]`. Place `d` such intervals inside the required interval
of length `x/(4d)`, with centers separated by `ceil(2x^(21/40))`.
Their total extent is below `3d x^(21/40)`, so
`12d^2<x^(19/40)` suffices for containment and distinctness. For
`x=2^Theta(p^(1-epsilon))`, this holds for every fixed `epsilon<1`.
The existing deterministic scan remains `n^o(1)`. The source capacity,
coprimality, odd primes, and `theta>1/(4d)` are unchanged. The legacy
negative condition `1-2epsilon>0` is explicitly replaced, with its
prime and normalization uses accounted for separately.

The strict choice `epsilon=2/3-2^-20`, `delta=2^-22` and its explicit
cutoff `b_input>=2^7340032` satisfy these requirements. The very large
cutoff is part of an asymptotic proof, with no practical runtime claim.

## Independent finite and parameter evidence

[review_banded_inverse.py](../code/review_banded_inverse.py) compares the
banded procedure to a separate dense rational inverse. It checks 368,480
exact exponent inequalities through ground size 48, including 1,052
nearest-rounding ties and periodic aliases.

Its four cyclic 24-by-24 systems have row gap `2^-20`. Three attain the
worst allowed inverse norm exactly, `||H^-1||=2^20`: a positive
alternating Laplacian, a negative Laplacian, and wrapped positive pairs.
The wrapped pairs also force pivots near `2^-19` and small-border inverse
norm `2^20`. These cases exercise actual large condition numbers.
For each system the checker verifies every one of 576 factor product
entries, all 300 full Schur rows, and the full dense Woodbury identity.
Twenty-six right-hand-side probes per system pass at 96 fractional bits;
some outputs have magnitude `2^19`. The largest certified rounded error
is below `9*10^-23`, which is much smaller than the explicit acceptance
bound `2^-32`.

These finite tests independently discriminate factor, wrap, reciprocal,
and rounding mistakes. They do not simulate the asymptotic tape machine
or replace the all-size proof above. The producer's separate true-Gaussian
interval tests remain additional evidence.

[review_lu_assembly.py](../code/review_lu_assembly.py) reads the revised
saved assembly certificate without importing its producer. It independently
checks 30 strict constraints per row, primitive logarithm enclosures, all
seven margins, the exact guard constant, root orientation, the changed
prime condition, and the explicit Gaussian cutoff. The three accepted
conditional savings are

| h50 physical side roles | Exact kappa |
|---:|---|
| 509,194 | `366204013939/(625*10^26)` |
| 494,250 | `6204988737403/10^30` |
| 487,650 | `636749338179/10^29` |

Physical role realization remains separately certified. The fresh review
run retains compact exact outcomes, source and input hashes, interpreter
version, and reproduction commands.

## Literature and novelty boundary

Harvey and van der Hoeven already proposed exploiting circular-banded LU
in section 4.4.2. Their discussion leaves the numerical error analysis
aside. The current branch supplies a concrete error/setup/tape treatment
and a weaker separation requirement; it should not claim discovery of
banded LU for this Gaussian system.

Primary references inspected on 2026-10-07:

- David Harvey and Joris van der Hoeven, *Integer multiplication in time
  O(n log n)*, Annals of Mathematics 193(2), 563–617 (2021),
  DOI `10.4007/annals.2021.193.2.4`; author-hosted 45-page
  [manuscript](https://www.texmacs.org/joris/nlogn/nlogn.pdf),
  section 4.4.2 and the retained scalar exponential lemmas.
- R. C. Baker, G. Harman, and J. Pintz, *The Difference Between Consecutive
  Primes, II*, Proceedings of the London Mathematical Society 83(3),
  532–562 (2001), DOI `10.1112/plms/83.3.532`; received 2000-05-03,
  revised 2000-11-15, Theorem 1 on page 532,
  [primary paper](https://www.cs.umd.edu/~gasarch/BLOGPAPERS/BakerHarmanPintz.pdf).

The reviewed model's two-thirds boundary follows from its current
generic banded solve and normalization powers. It excludes neither a
faster structured inverse nor a different normalization scheme.
