# Unbiased native coarsening with an exact residue codec

This result gives a numerical interface and an information-preserving codec.
It does not give a new kappa, a finite-state reversible circuit or a tape bill.
The retained-information optimum is for the full fine input grid. Correlations
in an actual caller can reduce that information; no caller storage optimum is
claimed.

## Contract and source

Let A=L C_r R be a serialized Gaussian native child on 512 complex coordinates.
L and R are Gaussian-unit signed permutations, including their global phases.
The central pair is C=[[1+i,1-i],[1-i,1+i]]/2. At tensor width f>=1, put
N=512^f, a=r*f, d=ceil(a/2), and use the tensor L,R with a active C axes.
Below, A denotes this complete tensor operator. Choose integer k>=d and m=2^k.
Input x is any vector in Z[i]^N, stored in units h/m for h>0. Output q is in
Z[i]^N, stored in units h. One fresh uniform integer u in [0,2^(k+d)) serves
every real and imaginary coordinate of the call. The seed stays unchanged.

The selected PR6030 word has 3453 MOVE events, 2886 distinct directed frame
edges, and 1001 frames used by those edges. All endpoint frame checks pass.
An independent 18-bit matrix inverse/composition and finite-span pass agrees
with every B block and the complete rank census.
The rank census is 2219,457,496,100,163,11,6,1 for ranks 1 through 8. The
unchanged Clifford compiler and separate coordinate oracle agree on all 512
columns of the first event of each rank. The new interpreter also checks all
4096 columns. It does not instantiate every one of the 2886 edge recipes.
The universal argument applies to any supplied L C_r R recipe in this class.

Source pins are in SOURCES.json. The selected word and the retained native
implementations are unchanged. The native/global compiler and all-size supplier
premises are not discharged by these representative checks.

## One common seed gives the minimum unbiased mean squared error

Each entry of C^tensor a has an integer Gaussian numerator over 2^d. Products
of a factors 1+i or 1-i are divisible by 2^floor(a/2). Gaussian monomials
preserve this property. Thus n=2^d A x is an integer Gaussian vector.
Set D=2^(k+d), and round each real component by

```text
q_j = floor((n_j+u)/D).
```

Write n_j=D*b_j+t_j with 0<=t_j<D. Exactly t_j of the D seeds give b_j+1;
the others give b_j. Therefore E(q_j|x)=n_j/D, and its error variance is
t_j*(D-t_j)/D^2. This argument is conditional on the complete incoming data
and past: u must be fresh and uniform given that past. Independence between
coordinates is not needed. With the Euclidean norm on all 2N real components,

```text
E(h*q | input) = h*A*x/m,
E(||h*q-h*A*x/m||^2 | input) = h^2*sum_j t_j*(D-t_j)/D^2 <= N*h^2/2,
||h*q-h*A*x/m|| <= h*sqrt(2N)*(1-1/D) for every seed.
```

For any integer-valued Z with mean b+t/D, the pointwise inequality
(Z-b)*(Z-b-1)>=0 gives Var(Z)>=t*(D-t)/D^2. Summing over real coordinates
proves that this quantizer attains the least possible mean squared error among
ALL unbiased grid-valued outputs at each input. Reversibility is not required
for this lower bound. Some outcomes are the farther adjacent integer; no
minimum deterministic-error claim is made.

A unit input column has a real or imaginary numerator equal to +1 or -1 after
the common reduction to denominator 2^d. Gaussian monomials preserve that
property. Its required mean is +1/D or -1/D. An integer-valued sampler using
a fixed b fair bits has a mean equal to an integer divided by 2^b. It needs
b>=k+d, even without the minimum-error condition. The common seed attains this
minimum fixed fair-bit count. This is not a minimum entropy or expected variable-length
sampling theorem. Reuse of the same seed in a later adaptive call is not
authorized by the conditional proof. The inverse uses the retained seed for
exact decoding; it is not a new stochastic call.

## The coarse-period lattice and its explicit Gaussian digits

Because k>=d, B=m*A^-1 is integral over Z[i]. The quantizer Q_u satisfies

```text
Q_u(x+B*z) = Q_u(x)+z for every z in Z[i]^N.
```

Put pi=1+i and H=[[1,i],[i,1]]. Then C^-1=pi^-1 H. The integral unimodular
matrices U=[[1,0],[-i,1]] and V=[[1,-i],[0,1]] satisfy U H V=diag(1,2).
Tensor them over the a active axes. The source R maps the period lattice
B Z[i]^N to m*C^(-tensor a) Z[i]^N, since L^-1 preserves Z[i]^N. Applying U
maps it to a diagonal Gaussian lattice with coordinate ideals

```text
(pi^e_j),  e_j = 2*k-a+2*weight(active bits of address j).
```

Indeed m*pi^-a*2^weight is a Gaussian unit times pi^e_j. Every e_j is
nonnegative. Their sum is 2*k*N because each active address bit is one at
exactly half the coordinates. Thus

```text
Z[i]^N / B Z[i]^N  is isomorphic to  product_j Z[i]/(pi^e_j),
number of cosets = 2^(2*k*N).
```

These Gaussian Smith methods are prior work, including
[PR5815](https://github.com/CrocSwap/integer-mult-bounds/pull/5815), its
[executed form](https://github.com/CrocSwap/integer-mult-bounds/pull/5821), and
the distinct modular-overwrite capacity in
[PR5880](https://github.com/CrocSwap/integer-mult-bounds/pull/5880).
The new use here is the quantizer's coarse-period quotient, its exact codec,
the minimum unbiased law and the actual selected native bindings.

Each Gaussian remainder has exactly e_j binary pi-adic digits. For z=A+iB,
take digit b=(A+B) mod 2, subtract b and divide by pi. The quotient is
((A-b+B)/2)+i*((B-A+b)/2), with exact integer halves. Repeat e_j times.
The e_j bits give one representative of every coset modulo pi^e_j. Reverse
Horner evaluation with pi reconstructs the representative. The implementation
packs all digits into exactly 2*k*N bits; byte containers use ceiling(bits/8)
bytes with required zero padding. At N=512^f there is no padding.

## Exact two-sided codec and sharp retained information

Encode x by taking the digits of U R x and returning (Q_u(x),digits). Decode
the digits to a representative x0 by applying U^-1 and R^-1. Then set

```text
z = q-Q_u(x0),
x = x0+B*z.
```

The translation identity proves Q_u(x)=q. The added B*z leaves the digits
unchanged. Conversely, any original x differs from its representative by a
unique B*z, so this formula recovers it exactly. For every fixed u, this is
a bijection between the fine-grid integer input representation and all pairs
(coarse integer output, 2*k*N-bit residue label). Every coarse output has
exactly 2^(2*k*N) fine-grid preimages.

An injective implementation that retains the seed and coarse output therefore
needs at least 2*k*N bits of additional information. An arbitrary finite dirty
bank with Q possible initial values cannot reduce this bound: the preimage
slice has 2^(2*k*N)*Q states and the output side has at most 2^b*Q states.
The codec attains b=2*k*N. This is a retained-label capacity result on the
advertised full input lattice. It is NOT an initially clean hardware-register
minimum, a full-state permutation on identical finite registers, or a lower
bound on correlated inputs reached by the complete selected caller.

The label cannot be erased from q and u alone. The inverse needs it. Any
physical uncompute, reuse, ownership or erasure schedule must still be paid.
The mathematical conversion between two representations does not silently
provide such a circuit.

## Selected grid interface and its boundary

At f=1 every selected MOVE rank is at most 8. Thus k=5 is sufficient. A call
accepts the h/32 grid and returns the h grid, matching the grid ratio in
[PR6499](https://github.com/CrocSwap/integer-mult-bounds/pull/6499) and
[PR6506](https://github.com/CrocSwap/integer-mult-bounds/pull/6506). Each full-grid
codec retains 5120 bits. Its seed has 5+ceil(r/2) bits, hence 6 through 9 for
the selected ranks. Allocating one such residue slot for each of the 3453
MOVE events uses 17,679,360 bits; separate fresh seeds use 21,683 bits.
These are uncompressed slot counts for that proposed interface, not joint
entropy lower bounds or a complete multiplication invoice.

This is only a grid match. The stochastic error contract is new; the scalar
predecessors' completed error budgets are not imported as proved consequences.
Whole-word restoration and caller probability bounds remain open. At tensor
width f, k>=ceil(r*f/2) is required for the stated integral-period codec.
Fixed k=5 does not cover all widths. For the rank-eight class, k>=4*f is
required. A larger fine grid can represent the scalar inputs but has a larger
full-grid residue code; its cost must not be omitted.

The condition is exact for integral inclusion m*A^-1 Z[i]^N subset Z[i]^N:
a unit column has a primitive component over 2^d. If k<d, that component
remains nonintegral. This excludes the stated period-lattice construction,
not all possible quantizers, codecs or changed encodings at smaller k.

## Complete direct implementation invoice

The code evaluates each native operator with a*N/2 Gaussian butterflies,
two tensor monomial passes and one final numerator normalization. Each route
pass reads f address digits per coordinate. Forward encoding
uses one such evaluation; decoding uses two more. The quotient adds one
triangular pass and its inverse on each active axis, plus 2*k*N digit extractions
and 2*k*N digit reconstructions. It does not use a free Gaussian query.

For one encode/decode round trip, payload arithmetic is bounded by

| Item | Count |
|---|---:|
| Direct native butterflies | 3*a*N/2 |
| Integral triangular pair updates | a*N |
| Tensor monomial coordinate passes | 8 |
| Whole-field copies in the displayed code | 2 |
| Extracted digits, and reconstructed digits | 2*k*N each |
| Real additions/subtractions | (20*a+14*k+8)*N |
| Real sign changes | at most 3*a*N/2+16*N |
| Payload binary shifts, including floor shifts | (4*k+12)*N |

The additions include the seed offsets, coarse differences and final recovery.
There are two coarse floor passes, three final native numerator normalization
passes and one final power-of-two scale. A butterfly uses 12 real additions/
subtractions and one sign change. A pi-digit extraction uses four additions/
subtractions and two exact halves; reconstruction uses three additions.
The phase helper evaluates only the selected phase, with at most two signs.
Bit packing, validation, buffer initialization, address loops and control add
O((a+k+f)*N) ordinary operations. Route and precision-index setup are included:
two 512-entry quadratic route tables, a active-axis list and N digit widths.

For input components of magnitude less than 2^w, w>=1, a sufficient signed
temporary width is W=w+4*a+2*k+12. One raw native stage enlarges a component
by at most four. A triangular stage enlarges it by at most two. A pi^e digit
representative has magnitude below 3*2^(e/2), and e<=2*k+a. These bounds give
an x0 component bound 2^(k+ceil(a/2)+a+2); the coarse q0, direct inverse and
final scale fit W. The width is sufficient, not optimal. Addresses need
O(f+log(k+1)) bits. The displayed algorithm thus uses
O((a+k+f)*N*(w+a+k+f)) indexed bit work and O(N*(w+a+k)) data storage, plus
the 2*k*N retained bits. At most six live Gaussian fields are needed during
decoding, including its coarse input, with separate precision/route tables.

This ordinary integer reference does not provide a reversible gate circuit,
fixed multitape routing, physical clean storage, sampler access, entropy
recovery, an accelerated recursive tariff or a complete caller. It does not
imply additivity, native-graph flatness or dirty compensation after intervening
arithmetic. All five selected assumptions and the frontier remain unchanged.

## Verification scope

The finite checks enumerate 25,184 complete quotient endpoints and 16 retained-
bit collisions, compare 36 small tensors to a separate dense coefficient oracle,
and run 432 small seed round trips. The source checks include 4096 columns in
each of two interpreters, 128 signed source round trips, 64 arbitrary coarse/
residue endpoints and exact means/variances for all 1920 relevant seeds.
A full 262,144-coordinate tensor uses a 524,288-bit label and all four seeds;
its exact mean squared error is 326311/4, below N/2. Eleven semantic/domain
controls and three source corruption controls are retained. These finite checks
corroborate the all-size proof. Independent human and proof-kernel acceptance,
all selected native instances and a complete selected cold replay are unrun.
