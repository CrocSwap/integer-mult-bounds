# Exact tensor fixed spaces of the forward F9 transport

This contribution was produced by Nick Petalas. Apache-2.0.

Claim types: a scoped written proof, with one exact finite signed-cycle
certificate as its source-specific input. The proof covers every positive
integer tensor width over the complex numbers. It is not a complete
multiplication theorem or a physical supplier construction.

## 1. Source and question

Let V be the complex vector space on the 512 addresses x in F2^9. Use the
forward monomial T of unpaidmoon's [PR #7447](https://github.com/CrocSwap/integer-mult-bounds/pull/7447),
at head `a60ddc19848b945250a78a1e3daea94e3c96b2f5`:

```text
T e_x = i^q(x) e_(Mx).
M rows = (1,2,4,8,398,85,270,16,58).
Q rows = (85,186,213,186,111,26,21,270,384).
alpha  = (3,1,1,1,2,0,0,0,3).
q(x) = sum_i alpha_i x_i + 2 sum_(i<j) Q_ij x_i x_j mod 4.
```

Bits are numbered from zero; output bit i of Mx is the parity of row i
against x. This is a definition of the object for this package. The
predecessor's identification with its Fourier sandwich is a cited premise;
neither that identification nor its original circuit is replayed here.
Its exact `RESULT.json` and `PROOF.md` are retained without changing their
credit. [SOURCE-PINS.json](SOURCE-PINS.json) binds their origin, head, Git
blob IDs and SHA256 hashes. No off-main Git object is needed at runtime.

The new question concerns the largest complex payload subspace on which
T to tensor width f acts as identity. It differs from counting fixed basis
addresses. It also gives the exact linear rank of the correction to identity.

## 2. Finite signed-cycle certificate

Partition the addresses into orbits of M. For an orbit
`C=(x_0,...,x_(l-1))`, define its holonomy
`h(C)=sum_j q(x_j) mod 4`. The complete certificate is:

| Orbit length l | Holonomy h | Number of orbits |
| --- | --- | --- |
| 1 | 0 | 16 |
| 2 | 0 | 8 |
| 5 | 0 | 48 |
| 10 | 0 | 24 |

There are 96 orbits, using `16+2*8+5*48+10*24=512` addresses.
The executable constructs each orbit from its least unused address,
evaluates every local phase, and checks every closing edge. Thus it
enumerates the entire finite domain, rather than sampling it. These new
orbit and holonomy data are the computer-assisted part of the theorem.

For each orbit put `d(x_0)=0` and
`d(x_j)=sum_(k<j) q(x_k) mod 4`. Zero holonomy makes the definition
consistent across the closing edge. Let D be diagonal with
`D e_x=i^d(x)e_x`, and let P be the unsigned permutation `P e_x=e_(Mx)`.
Then the explicit edge identity

```text
d(Mx)-d(x) = q(x) mod 4
```

proves `T=D P D^-1`. The verifier checks this identity at all 512
addresses. D is a mathematical change of basis here; no physical tariff
or permissible native implementation for D is asserted.

An orbit contributes the characteristic factor `z^l-1`. Consequently

```text
det(z I-T) = (z-1)^16 (z^2-1)^8 (z^5-1)^48 (z^10-1)^24.
```

Writing `zeta=exp(2 pi i/10)`, the multiplicities of `zeta^k` for k=0,...,9
are respectively

```text
(96,24,72,24,72,32,72,24,72,24).
```

In particular T has a 96-dimensional fixed space. An explicit basis is
one vector `sum_(x in C) i^d(x)e_x` per orbit. These vectors have disjoint
supports, so they are independent, and the eigenvalue equation follows
from the same edge identity. There are no additional fixed vectors because
each single cycle has a one-dimensional fixed space.

## 3. The all-width formula

For every f>=1, set `U=T^(tensor f)`. Since `T^10=I`, also `U^10=I`.
The operator

```text
E_f = (I+U+...+U^9)/10
```

is the projector onto `ker(U-I)`. Indeed, U fixes the image of E_f by
telescoping, and E_f acts as identity on every fixed vector. Therefore its
trace equals the dimension of that space. Trace is multiplicative on
tensor products, giving

```text
dim ker(T^(tensor f)-I) = (1/10) sum_(j=0)^9 tr(T^j)^f.
```

An unsigned l-cycle contributes l to the trace of P^j exactly when l
divides j, and otherwise contributes zero. The cycle certificate gives

```text
tr(T^j), j=0,...,9 = (512,16,32,16,32,256,32,16,32,16).
```

Substitution proves the exact formula

```text
F_f = dim ker(T^(tensor f)-I)
    = (512^f + 256^f + 4*32^f + 4*16^f)/10,
R_f = rank(T^(tensor f)-I)
    = (9*512^f - 256^f - 4*32^f - 4*16^f)/10.
```

The expression is an integer because it is a projector rank. It also
follows from the integer cyclic convolution of the displayed tenth-root
multiplicities. At f=1 and f=2 the respective fixed dimensions are 96 and
33,280, and the respective correction ranks are 416 and 228,864.
Every subspace W on which U acts as identity lies in its kernel, and the
kernel itself attains the maximum F_f. Thus the subspace statement is sharp.

The universal quantifier follows from this projector proof. The executable
checks the character formula against exact spectral convolution through
width 64. It separately constructs all 262,144 two-column addresses and
their signed orbits, obtaining 33,280 fixed vectors without using the
one-column histogram or the character formula to count those orbits.

## 4. What the correction rank rules out

Suppose a linear correction written as a sum of k maps of complex rank at
most b satisfies

```text
U + A_1 + ... + A_k = I.
```

Rank subadditivity yields `k*b >= rank(I-U)=R_f`. For b>=1 this gives
`k>=ceil(R_f/b)`. With unrestricted rank-one linear maps the bound k=R_f
is attained by any rank decomposition of I-U. This last upper bound is
only an algebraic statement, not an allowed query or native construction.

The rank is the matrix rank on a `512^f`-dimensional complex array. It is
not the number of native address axes, Fourier support rank, a recursive
child rank, a monomial-pass price, or the inherited H8 centre charge. In
particular, this proof does not convert R_f into a recursive invoice.
It excludes only proposals whose additive corrections have a stated bound
on this same complex matrix rank. The fraction R_f/512^f tends to 9/10;
tensoring this transport does not make it equal to identity on most of V.

## 5. Executable evidence and limits

The direct script authenticates its two retained inputs and emits a
generated receipt binding all nine package files by SHA256. It writes no
files. A separate sparse Gaussian elimination of the literal 512-column
matrix T-I over F257 has rank 416. The map `i -> 16 mod 257` preserves
the cycle rank formula: on an l-cycle the kernel exists exactly when the
product of edge phases is one, and reduction keeps the four roots of
unity distinct. This is exact corroboration, not a numerical rank estimate.

A phase fault at address zero changes its eigenvalue to i. Both the cycle
certificate and trace test detect it, and no diagonal gauge to P exists.
The verifier also checks the distinction between basis-address and linear
fixed spaces, rejects an additive tensor-rank guess, and rejects four
out-of-domain reference widths. Runtime checks survive Python optimization.

The predecessor's opcode -2 is a different unresolved operator; this package
does not identify it with T. No physical caller, dirty restoration program,
native implementation, precision/storage bound, supplier admission, new
kappa or selected-frontier update is claimed. No predecessor scientific
verifier, selected cold replay, Lean or Docker run is required or performed.
Independent human and formal proof-kernel review are unclaimed.

## 6. Code constraints

The script has no recursion, subprocess, network, write path or plugin
loading. Each function is below 60 physical lines. The largest explicit
domain has 262,144 addresses; an orbit takes at most ten steps there.
One-column orbit and elimination loops take at most 512 steps. The
spectral recurrence uses 64 steps and 100 products per step. Source files
are bounded to 128 KiB, coefficient rows to nine, and reference f to 64.

Power of Ten rule 3 deviation: CPython requires managed allocation during
integer arithmetic and dictionary operations. The scope is this finite
offline verifier. Its largest visited table is a 262,144-byte bytearray;
Gaussian elimination has at most 512 pivots and 512 entries per pivot,
and reference integers have at most 577 bits. Fixed allocation is not
claimed. The declared input/domain bounds and warning-strict normal and
optimized replays constrain and exercise this deviation. A future API
with larger dimensions must replace these budgets.

Warning-strict execution, source parsing and an AST function-size check
provide local diagnostics. No shared compiler or CI setting is changed.
Build the Lever led to retaining the complete signed-orbit and rank
verifier. Prove It Works led to literal two-column execution and a distinct
Gaussian elimination rather than relying only on the character formula.
Character averaging, cycle gauges, rank decompositions and rank
subadditivity are classical. No global literature-priority claim is made.
