# Stable Gaussian block maps by one paid convolution

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
This is a constructive native Word RAM theorem. It uses no Turing machine,
transition table, machine simulation or free convolution/root/exp oracle.

## 1. Exact diagonal-Hankel-diagonal identity

Let a>0 and u,v,c be real. For integer row and column coordinates x,y, define

    W[x,y] = exp(-a*(u*x-v*y+c)^2).

On a rectangle 0<=x<m, 0<=y<l, with m,l<=q, set

    D[x] = exp(-a*(u^2+u*v)*x^2 - 2*a*u*c*x - a*c^2),
    E[y] = exp(-a*(v^2+u*v)*y^2 + 2*a*v*c*y),
    H[z] = exp(a*u*v*z^2),       0<=z<m+l-1.

**Theorem 1.** For every complex input array Z,

    sum_y W[x,y]*Z[y] = D[x] * (H * reverse(E*Z))[x+l-1],

where the star on the right is ordinary linear convolution, not cyclic
convolution and not a pointwise operation.

**Proof.** Expand the total exponent in D[x]*E[y]*H[x+y]. The x^2 term is
-a*u^2*x^2, the y^2 term is -a*v^2*y^2, the cross term is 2*a*u*v*x*y,
and the remaining terms are -2*a*u*c*x+2*a*v*c*y-a*c^2. Their sum is
-a*(u*x-v*y+c)^2. Thus W[x,y]=D[x]*H[x+y]*E[y]. With B[y]=E[y]*Z[y], the
convolution of H and B reversed at index x+l-1 is exactly
sum_y H[x+y]*B[y]. All needed H indices lie in [0,m+l-2]. ∎

This is a chirp/convolution identity, with Gaussian rather than unit-modulus
chirps. It is standard algebra; no claim of historical priority is made.
The finite-word conditioning and complete blocked cost below are essential.

## 2. Quantitative conditioning after centering each block

For a global block beginning at row x0 and column y0, replace c by

    c0 = u*x0-v*y0+c,

and use local x,y starting at zero. Assume

    a*(|u|*q+|v|*q+|c0|)^2 <= C*p.                         (A)

Here C is a fixed constant and p is the requested global precision scale.
Every exponent defining D, E and H then has absolute value at most C*p.
For D and E this follows by the triangle inequality and expanding the square
in (A). For H, use 4*|u*v| <= (|u|+|v|)^2 and x+y<2q.
Consequently every factor and its reciprocal have magnitude at most

    M=exp(C*p).

If p=Theta(log n), these are polynomially bounded in n. Large cancelling
Gaussian chirps therefore do not require an unbounded-precision exact scalar
model: a sufficiently large constant times log n integer/fractional bits pays
for them. Condition (A) is checked from actual block geometry; small final
kernel weights alone would NOT prove it.

## 3. A complete native block algorithm and its error budget

**Theorem 2.** Under (A), |Z[y]|<=X and q<=n^c for fixed c, one rectangle's
Gaussian map can be evaluated to any requested absolute error 2^-p0 with
O(q log(q+2)) bounded-word operations, assuming p,p0,log(X+1)=O(log n).
There is shared paid setup O(n^eta polylog n+q log(q+2)) for fixed 0<eta<1.
Every physical word has a sufficiently large fixed constant times log n bits.
For this algorithmic statement, a,u,v,c are supplied as O(log n)-bit rational
parameters, or as certified dyadic enclosures produced by an explicitly paid
routine. Their magnitudes, nonzero denominators and coordinate indices have
polynomial numeric bounds in n. Arbitrary real parameters are not an oracle
input model. Computing a centered c0 from global indices may require an extra
O(log(t+s)) precision guard; this remains O(log n) under the declared polynomial
index bound. Exact identity Theorem 1 itself does not need this representation
restriction.

**Construction.** Generate D,E,H with the explicitly paid signed exp-table
algorithm in NATIVE-EXP-TABLE.md. It provides exp on [-C*p,C*p]
using n^eta polylog n setup and O(1) word work per query. Positive arguments
are obtained with quantitatively guarded reciprocal division, not by assuming
an exact exponential instruction. Its input arguments and values are evaluated
to the guard precision below. This costs O(q) per block. When u,v,a are fixed
across blocks, H is identical in all blocks: its forward transform is prepared
once and charged to shared setup.

Pad to a power-of-two convolution size N0>=m+2*l-2. For a power-of-two q,
N0=4q always suffices. Perform the ordinary radix-two forward FFT of reversed
E*Z, multiply by the prepared transform of H, and perform the inverse FFT
with its 1/N0 normalization. Select indices x+l-1 and multiply by D[x].
The fixed kernel's transform is also paid; it is not a free arbitrary-kernel
convolution. Without sharing H, this is three FFTs per block; with sharing,
it is two per block plus one shared FFT.

The FFT is the direct iterative bounded-word algorithm from native_fft.py and
FFT-ERROR.md: signed dyadic arithmetic, a generated root seed, explicit
bit-reversal/butterflies, word-sized products, and exact-grid addition. The
root seed and required root powers are generated once for N0 at guard precision.
There is no TM multiplier call. The pure arithmetic algorithm and its error
proof apply to arbitrary complex bounded inputs; integer recovery is not used
inside this Gaussian block.

For clarity, a conservative sufficient error budget is

    block error <= 2^30*q^8*M^4*(X+1)^2 * 2^-P,              (B)

when all factor/input, root and local rounding errors are at most 2^-P
at their stated certified interfaces. One may use a larger fixed constant.
Choose

    P >= p0 + 30 + 8*ceil(log2(q+2))
              + 8*ceil(C)*p + 2*ceil(log2(X+1)) + 4. (C)

The integer coefficient 8*ceil(C) safely bounds 4*C*log2(exp(1)); no transcendental
constant is needed to choose precision. Choose this common precision once from
the global parameter and input bounds, rather than recomputing logarithms at
every block. Rounding P up and adding a fixed guard for the supplied exp
implementation makes (B) strictly below 2^-p0. Exponent arguments are computed
with enough additional guard bits that their exp(Cp)-Lipschitz images meet the
factor-error interface; that costs only O(p+log(t+s)) extra bits. The common
physical word width covers this larger internal precision as well. Thus all
working precisions remain O(log n).

**Proof of (B).** Approximate D,E,H within epsilon=2^-P and use rounded
complex products with error <=2*epsilon. Factor magnitudes are at most M,
and their approximants at most 2M. The preweighted input has magnitude at
most 2M*(X+1) after a fixed rounding guard. Replacing all three exact factors
by their approximants changes each D*E*H product by at most 7M^2*epsilon;
rounding pre/post products and input contributes further constant multiples of
q*M^3*(X+1)*epsilon. The independent three-transform error proof supplies
at most 216*N0^6*beta0^2*epsilon for the convolution, where
beta0<=4M*(X+1), using correspondingly certified twiddles. Multiplication by
D contributes at most 2M times that error, plus its own factor/rounding terms.
Using N0=4q and absorbing the fixed constants and lower q powers yields (B).
The same estimates bound all intermediates by a fixed polynomial in q,M,X.
Since their logarithms are O(log n), both raw word products and their sums fit
a common O(log n) width, including the root-seed implementation's larger guard
width. This proves the constructive block bound. ∎

If this map's global output sums at most K such rectangles per row, replace
p0 by p0+ceil(log2(K+1))+2. For fixed K this is a constant extra guard.
If the input and arguments themselves are dyadic approximations, their errors
must be included in the certified factor/input interfaces in (B); they are not
assumed exact simply because they are held in words. A polynomial Lipschitz
bound exp(Cp) times the exponent-argument error supplies that guard.

## 4. Rectangular blocking and the complete fast banded Gaussian map

Let 0<=x<t and 0<=y<s, with s=O(t). Assume u,v>0 have bounded ratio in both
directions. Fix a radius R and retain a whole q-by-q block whenever some pair
in it satisfies |u*x-v*y+c|<=R. Sum its full Gaussian rectangle; do not apply
a per-entry band mask that would destroy the Hankel identity.

For each row block, the possible column coordinates form an interval of length
at most [u*(q-1)+2R]/v. It intersects at most

    K = ceil((u*(q-1)+2R)/(v*q)) + 3

column blocks. If q is within fixed constant factors of R/max(u,v), K is a
fixed constant. There are O(t/q+1) row blocks, hence O(t/q+1) retained
rectangles. For an active rectangle,

    |c0| <= R+(u+v)*(q-1),

so its conditioning follows from

    a*(R+2*(u+v)*q)^2 <= C*p.                               (D)

Choosing a*R^2=Theta(p) and q a power of two within a fixed factor of
R/max(u,v) ensures (D). Require q>=1; when the resulting q exceeds the array
length, use one appropriately smaller block and the direct small case.

**Theorem 3.** Under these explicit geometric hypotheses, the retained map
costs

    O(t log(q+2) + s + n^eta polylog n)

native Word RAM operations, including shared root/exp setup, generated chirps,
all block FFTs, gathers/scatters, summation and IO. When q is a positive power
of log n, the dominant map work is O(t loglog n+s), rather than the naive
O(t*q) neighbor enumeration. Every term is paid.

**Proof.** Multiply O(t/q+1) rectangles by the O(q log(q+2)) block price, add
O(q log(q+2)) shared fixed-kernel FFT setup, O(t+s) data IO and gathering,
and the n^eta polylog n exp preparation. Use q<=t in the nonsmall branch.
Geometry bounds K uniformly, so summing blocks adds O(t) word work. ∎

For the full untruncated Gaussian map, every omitted weight is at most
exp(-a*R^2). Its row error is at most

    s*X*exp(-a*R^2).

Thus a*R^2 >= (p0+ceil(log2(s*X+1))+2)*log(2) makes omitted tails less than
2^-p0/2. This is compatible with (D) when s,X are polynomially bounded in n
and p0=Theta(log n). Add one precision bit to the block summation budget and
obtain a constructive approximation to the full map. No Gaussian tail is
ignored merely because its entries look numerically small.

## 5. Scope and actionable use

This is a positive sufficient replacement for a concrete forward Gaussian
resampling map once its actual grid slopes, smoothing parameter, input bound,
row/column ranges and requested error instantiate (A) and (D). It removes the
naive q factor from the local convolution part with a wholly native arithmetic
algorithm. It does not by itself certify every Gaussian row in the multiplication
source or establish a new global kappa. The root must bind the block layout and
precision to the chosen complete native caller before claiming such a bound.

The exp tables and root tables are numerical function tables generated from
bounded arithmetic. They are not TM transition tables or simulations. The
Gaussian chirp identity, ordinary FFT convolution, and radix blocking have
classical precedents; no worldwide novelty is asserted. Our result is the
explicit stable finite-word interface and complete cost/error assembly.

A power-of-two block size satisfying the rationally expressed normalized-span
bound can be found by a doubling loop and squared comparisons. The program
need not receive an exact real square-root primitive. A chosen radius may also
be specified by a rational squared bound and a proved tail inequality. The
actual source instantiation must supply these bounds rather than relying on
an uncomputed real-valued parameter selection.
