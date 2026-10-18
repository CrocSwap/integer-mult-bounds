# Full-transform and bit integration: an exact adapter with an unfavorable bill

This note continues PR673 at `0e35f56cab3cae1eb0a99447135569d687c5695a`.
Its result has two parts: an implemented functional adapter, and a rejection
of **this adapter's** recursive cost as a source of a positive saving. It does
not rule out other integrations of the echo mechanism or another supplier.
The PR628 inverse and PR673 local cost improvement remain separate valid
objects under their stated contracts.

## 1. The interfaces that must be connected

PR673 supplies an additive shear

    E(A): (x,y,z) -> (x,y+A x,z),

where z contains arbitrary borrowed data. A supplier for the recursive
framework must instead apply its required operator to **every physical role**,
including roles used as scratch in its scalar word. The complex endpoint is a
product of C kernels on selected binary address positions; the bit endpoint
is an interchange of two address chunks, acting on Boolean data.
`upstream/03-motifs.tex`, `04-swap.tex` and `05-layers.tex` specify these
contracts. Restoring a scratch role is insufficient when that role is owed
its own endpoint transform.

Let A be an invertible operator. Three shears, in execution order,

    y += A x; x -= A^-1 y; y += A x

send (x,y) to (-A^-1 y, A x). Exchanging the two roles and negating the
second gives (A x,A^-1 y). Each shear is implemented with the same distinct
borrowed pool, excluding both current pair roles, and restores that pool.
No fresh zero array is assumed. Pair all W roles, with W even and at least
two plus the echo's scratch depth. Process the pairs serially. A borrowed
role may already have been transformed or may still contain its original
value; the shear contract permits either, and restores it before proceeding.

### Complex endpoint

For the selected positions let A=C^tensor_d, with
C=((1+i)I+(1-i)X)/2. From the retained identities,

    A^-1 = gamma Z A Z,  gamma=(-i)^d,

where Z is the product of sign changes on those positions. Before the three
shears, replace y by Z y. After the exchange/negation, replace the second
output by gamma^-1 Z times that output. The final pair is exactly (A x,A y).
Both forward and inverse C leaves are implemented explicitly. For grouped
positions of width f the same identity holds with d replaced by df; the
inverse wrappers add no recursive children under the inherited interface.

### Bit endpoint

Let the address consist of H_1,...,H_d,D_1,...,D_d, with arbitrary other
fields held fixed. Each A_i interchanges H_i and D_i. These permutations
commute and are involutions, so A=product_i A_i satisfies A^-1=A.
Over Boolean data subtraction equals addition. The same three shears followed
by a role exchange therefore yield (A x,A y), without complex phases.
The implemented tests use radix 3 or 5 with one digit per field. The identity
is valid for arbitrary equal-length fields and spectators: it is an identity
of commuting address permutations, not an interpolation from finite tests.

`adapter.py` implements both endpoints, streams the additive leaf results,
and uses scalar swaps for the role exchange. It needs no clean full-array
output buffer. Its indexed source reads are explicit **reference operations**;
they are not a free tape-routing primitive. Permutation tables used by the
finite test are read-only test descriptions, not a claimed constant-size
uniform machine description.

## 2. Complete synthetic Fourier transform integration

The multiplication framework's transform is over R_r=C[y]/(y^r+1), with
power-of-two r. It uses normalized butterflies and signed coefficient
permutations. It is not an ordinary complex DFT on independently approximated
roots. `transform.py` implements the retained contract for axis lengths t_i
that divide 2r, with M=product_i t_i.

In each decimation-in-frequency round, one address position on each active
axis is selected. The identity

    H0^tensor_d = b^d S_d C^tensor_d S_d, b=(1-i)/2,

converts the all-role C adapter to the normalized butterfly layer. At address
x, S_d is the fourth-root phase i^(sum of selected bits). The grouped twiddle
is multiplication of each polynomial record by

    y^E, E = -sum_i (2r/u_i) b_i k_i mod 2r,

where u_i is the current recursive axis length, b_i the selected branch bit
and k_i its lower unprocessed bits. The monomial acts by a signed rotation of
coefficients; the implementation cycles in place with one held scalar.

The output stays in bit-reversed frequency order B. There is **no hidden
frequency permutation** in the implementation. Reversing the rounds applies
the inverse twiddle first and then the same normalized butterfly. Thus the
two procedures implement B F-minus and F-plus B^-1, and their composite is
I/M. A convolution uses two forward transforms, pointwise multiplication in
R_r, then the opposite transform, followed by scaling by M². Both forward
transforms and the opposite transform include a 1/M normalization; charging
only a factor M would give the wrong answer. The direct convolution oracle
checks the cyclic address wrap and the negacyclic coefficient wrap separately.

The harness includes nonzero data on every role, entire input-basis checks
for the all-role C adapter, full Boolean symbolic columns, and independent
DFT/convolution definitions. No rounded numerical equality is used. Fraction
arithmetic is a prototype, not a fixed-precision or fixed-tape implementation.

For a simple exact resource bound, each C shear adds at most two source
values, with dyadic coefficients of denominator 2, into one target. After J
such leaves the common fractional-bit budget grows by at most J, while the
joint max magnitude grows by less than 3^J. Phase, sign and role-exchange
wrappers are isometries. The additional H0 factors add at most sum_round d
fractional bits and are contractions. Signed twiddles add none. This gives
a deliberately loose word budget

    initial_fraction_bits + O(J + sum_round d + log(initial_norm+1)).

This is an explicit bound for this exact prototype schedule. It does not
establish the retained O(p) precision guard in the growing-parameter
multiplication reduction. Preparation, source access and routing remain paid
obligations. The cost rejection below already holds with all of them free.

## 3. The complete recursive bill rejects this route

Suppose d=n f selected coordinates are grouped into n groups of f. Let N(n)
be the exact leaf count of one echo. There are three shears per pair and W/2
pairs, so the complete all-role program invokes

    L = 3 W N(n)/2

additive leaves. Grant an optimistic oracle in which each additive leaf costs
only **one** recursive child on f coordinates and one role of volume V/W.
This is already more generous than the ordinary lowering: applying a child
to the source, adding it to the target and undoing the child takes two child
calls. Charge zero for the surrounding scalar operations, phases, role
exchange, storage, preparation, routing and precision. These favorable
omissions can only make admission easier.

For a candidate exponent sigma=1-b, the normalized recurrence moment is

    Phi(b) = (L/W) (1/n)^(1-b) = 3 N(n)/(2 n^(1-b)).

Even Phi(0) must be below 1 to obtain a strict saving by this bill. The flat
echo has N(n)=4n-4, giving

    Phi(0) = 6 - 6/n >= 3, for n>=2.

Recursive grouping does not improve this lower bound. First, induction gives
N(t)>=2t-1: at an internal node each group is invoked at least twice and
the number of groups is at most t. For an internal node with group sizes
n_1,...,n_k, use 2N(n_i)>=4n_i-2 on each endpoint and 4N(n_i)>=4n_i on
each interior group. Summing yields N(n)>=4n-4. Hence every fanout supported
here has Phi(0)>=6-6/n. Since n>1, Phi(b) increases with b, so **every b>=0
is rejected**. This is a lower bound on the cost of this specific all-role
adapter, not an optimality theorem for arbitrary suppliers.

The corresponding optimistic finite profile is H_1=L, m=n and W physical
roles. Its deficit Wm-sum_j j H_j is negative. The same calculation applies
to the Boolean and complex adapters. Borrowing more roles does not help:
the W factor cancels because every role is owed an output transform.

For example, a flat eight-factor shear needs 28 leaves and seven scratch
roles. Taking W=10 roles, all outputs require 420 leaves, yielding moment
420/(10*8)=5.25 at b=0. Pricing only the raw 28-leaf shear while counting ten
completed outputs would give the false coefficient 28/80=0.35. The missing
outputs are detected by the `skip_borrowed_outputs` functional control.

Pointwise scalar shortening in an otherwise unchanged supplier likewise does
not change its child histogram, recursive volume fractions or strict moment.
It can improve constants or finite cutoffs. It cannot by itself be multiplied
into κ. This experiment does not modify any accepted supplier's profile.

## 4. Why the literal cyclic inverse is not an automatic replacement

### The Newton factor is triangular

In the pinned exact-DFT source, with h_j=1/product_(s=1)^j(1-u^s), the Newton
factor is T=P(J_r), where J_r is the **nilpotent lower shift**. PR621/628 instead
handle C=P(Z_L), a cyclic shift polynomial. For L=r, C-T is strictly upper
triangular and every first-superdiagonal entry is h_(r-1)=1/r. Its rank is
exactly r-1, as seen from rows 0 through r-2 and columns 1 through r-1.
Where C is invertible, the inverse difference C^-1(C-T)T^-1 also has rank r-1.

This identifies a missing boundary correction; rank alone is not a lower
bound on all algorithms for this structured correction. At r=4, replacing T
by C in the actual Newton factorization sends e_0 to

    (13/16-i/16, 21/32+3i/32, 1/2+i/8, 1/4)

instead of F_4 e_0=(1,1,1,1). `boundaries.py` checks both the correct full
factorization and this counterexample exactly. The present functional adapter
uses the correct retained C butterfly; it does not pretend that cyclic and
triangular P operators agree.

### Complex nonvanishing does not transfer to bit arithmetic

Allow even a two-bit extension field GF(4)=GF(2)[u]/(u²+u+1). The primitive
radix-3 kernel has nonzero preparation denominators and is

    P(z)=1+u z+z².

Nevertheless,

    (1+u z+z²)(1+u z+u z²+z³)=1+z⁵.

Thus on a length-5 cycle, the nonzero vector (1,u,u,1,0) lies in the kernel
of P(S_5). Expanding each GF(4) value into two F2 coordinates preserves this
counterexample. There is no inverse to implement on that domain.

More generally, any nonconstant polynomial over a finite field with nonzero
constant term has a nonzero root alpha in a finite extension. Its multiplicative
order L is finite, so it shares a nonconstant factor with z^L-1. Multiplication
by P modulo z^L-1 is therefore singular. This rules out the *all-cycle-length*
finite-field analogue of the particular complex nonvanishing premise; it does
not rule out restrictions on admissible lengths, another kernel, or bit
address permutations. The Boolean adapter above works with permutations and
makes no use of this invalid cyclic inverse.

## 5. What a substantial κ improvement must change

For the retained outer assembly, kappa < a/(1+a), with a below both supplier
endpoints. Therefore kappa=0.01 requires **both** supplier savings above 1/99.
The current pinned bit profile gives c≈0.0017334270. Its strict adjacent root
bracket gives an upper outer ceiling below 0.001730427469824 even if the
complex supplier ceases to bind. Scalar-call speedups do not alter this ceiling.

`price.py` evaluates both pinned paid moments at the necessary rates for
kappa 0.002, 0.005 and 0.01, retaining the bit fallback charge. At the 0.01
target, uniformly scaling **every paid term**, with unchanged width and live
volume, would need a reduction strictly exceeding about **2.6990784206%** on
the bit side and **2.4734894761%** on the pinned PR659 complex side. These are
optimistic diagnostic budget targets, not feasible fractional gate deletions
or admitted replacement profiles. They identify the quantity a new construction
must improve: the weighted recursive bill at the desired rate, including
its physical hosting and fallback obligations.

Credit: the OpenAI #109 integer-multiplication interfaces and pinned exact-DFT
source; classical Newton/q-calculus sources credited by Ali Romman's #621;
Chafik Boukhalfa's #628 leaf; PR673's echo schedule; DreamingOfClouds/eumemic and
the retained #589 lineage; Jeremy Kothe's #659 and its source notices. The
source-suppressed replay principle already appears in the pinned exact-DFT
source's `loc:replay`, with Bennett and catalytic-space attribution. This
continuation does not claim that general principle as new. Prepared for
@androolloyd with substantial OpenAI Codex assistance, under Apache-2.0.
