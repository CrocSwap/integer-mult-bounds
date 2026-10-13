# Two-scan periodic inversion with length-independent rounding error

This local result supplies a rounded first-order inverse primitive. It does
not change the multiplication exponent or supply a complete growing-radix
coefficient-preparation, tape, or scratch-restoration contract.

Let S be the cyclic predecessor shift in either direction on L>=1 entries.
Suppose |b|<=1-beta, 0<beta<=1, and ||x||infinity<=B. The equation

    y_j - b y_(j-1) = x_j

has a unique solution of norm at most B/beta, by the Neumann series.
In the selected cyclic order, compute a zero-seed pass

    z_-1=0, z_j=x_j+b z_(j-1), c=b^L,

then set s=z_(L-1)/(1-c). A second pass with initial value y_-1=s
produces the exact periodic solution. This follows from
y_(L-1)=z_(L-1)+b^L s=s. The method also works at L=1.

## Rounding bound

Use a dyadic grid of spacing u=2^-P. Round both real and imaginary
components to the nearest grid point after every completed complex
multiply-add, after every power multiplication, and after the closure
division. A complex rounding error has modulus at most u/sqrt(2)<=u.
Assume u<=beta^2/2. This counts ideal rounded division; an implementation
must implement or bound that scalar operation accordingly.

In the first pass maintain a rounded power starting from 1. The errors
in its final power and in z_(L-1) are each at most u/beta, by geometric
summation. For d=1-b^L, |d|>=beta. The computed denominator dhat therefore
has |dhat|>=beta/2. Write the exact cyclic seed as s=z/d; crucially,
|s|<=B/beta from the periodic inverse bound, rather than estimating the
numerator and denominator separately. Before rounding the division,

    |zhat/dhat - s|
       <= (|zhat-z| + |s| |dhat-d|) / |dhat|
       <= 2u/beta^2 + 2B u/beta^3.

After rounding, the seed error is at most 5(B+1)u/beta^3. The second
scan adds at most u/beta, while attenuating the initial error. Thus

    ||yhat - (I-bS)^-1 x||infinity <= 6(B+1)u/beta^3.

This bound is independent of L. The first-pass values have norm at most
(B+u)/beta, the rounded powers at most 1+u/beta, and second-pass values
at most B/beta plus the displayed error. There is no exact representation
of b^L with bit length proportional to L: its rounded running value has
the working precision throughout.

For target absolute error 2^-p, it suffices that
P >= p+ceil(log2(6(B+1)/beta^3)), along with u<=beta^2/2.
Dyadic arithmetic uses O(P+log(B+1)+log(beta^-1)) bits per component.
The procedure uses two sequential input scans, O(L) complex arithmetic
operations and O(1) scalar state beyond input/output arrays. Rewinding
between scans costs O(L) tape movement. Cascades need alternating arrays
or a separately justified overwrite schedule. This is not an in-place
clean reversible word and does not restore dirty scratch.

## Connection to the PR621 kernels

For a prime-power radix r, PR621 proves |P(z)|>=delta on the unit circle,
where n=r-1, H=2^r-1, delta=1/(2rn H^(n phi(r)-1)), and the coefficient
l1 norm of P is at most M=H/r. Define

    eta=min(1/2, delta/(n M 2^(n-1))), beta=eta/2.

Every root rho has ||rho|-1|>=eta. Indeed, if its radial distance d is
less than 1/2, compare it to the radial projection onto the unit circle.
Along that segment |P'|<=n M 2^(n-1), so delta<=d n M 2^(n-1).
Roots farther away already meet the bound. Consequently each outer root
gives a stable factor (I-rho^-1 U)^-1 with margin at least beta; each
inner root gives (I-rho U^-1)^-1 U^-1 with that margin. Outer factors
also contribute a scalar -rho^-1. Since the leading coefficient is 1/r,
the remaining overall scalar is r. Each outer scalar has modulus <=1.
Unit gauges can be absorbed into the first-order coefficients.

At the level of exact, supplied roots this yields n stable scans pairs,
with prefix amplification bounded by r beta^-n. The logarithm of this
crude prefix bound is O(r^4), independent of L. Root preparation,
certified factor approximation, accumulated coefficient/scan/scalar errors,
and their bit cost must all be paid before claiming a growing-radix
algorithm. Some roots may be inside; no all-outer-root assumption is used.

For U=tau Z^w, the array decomposes into cycles. This gives O(rL)
arithmetic operations if those cycles are accessible. On fixed tapes,
the sequential argument above directly covers w=1 or -1. Arbitrary w
requires a charged layout/permutation argument; the RAM count alone does
not establish linear tape traffic. The case w=0 reduces to scalar division.

## Evidence and attribution

Run `python3 -I -O -B scan.py --out GENERIC-CHECK-fresh.json`; compare with GENERIC-CHECK.json.
The independent exact Gaussian solver checks 72 cases. Residual certificates
check all 108 cases, including lengths 1,2,3,8,17,64, both directions,
three stability margins down to 1/4096, and real/complex factors. Five
malformed or corrupted controls are rejected. These finite checks support
the implementation; the inequalities above establish the all-length result.

Periodic causal/anticausal filtering is standard. See Briand and Davy,
"Optimization of Image B-spline Interpolation for GPU Architectures"
(2019), https://www.ipol.im/pub/art/2019/257/article_lr.pdf, for related
recursive filtering and boundary initialization. No novelty claim is made
for that method. PR621 by aliromman supplies the kernel and circle theorem
(head 520774462b19b29af41554b74def31f9d01e997e). The explicit rounding
budget, exact local checker and application boundaries here were prepared
with OpenAI Codex for chafreaky.
