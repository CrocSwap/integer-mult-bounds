# Exact spectrum in the Bell central sector

This is an algebraic theorem with exact finite certificates. It gives a
sharp stability contract. It does not construct a physical decoder.

## Result

Use the full Gaussian-dyadic four-qubit Clifford group G, natural module
V of dimension 16, Pauli subgroup P and scalar subgroup `Z=<iI>`. Write
S=G/P=Sp(8,2) and N=|G/Z|=12,128,668,876,800. Choose one unitary U_a
per scalar coset. The normalized tensor map A_f has columns
vec(U_a^(tensor f))/16^(f/2). Its Gram matrix is

```text
K_f(a,b) = (tr(U_a* U_b)/16)^f.
```

The star denotes the conjugate transpose. A change of representatives
gives diagonal unitary conjugation and preserves the spectrum.

For every integer f>=14 with f=2 modulo 4, put p=(f-2)/2 and t=2^(-p).
Define

```text
H(t) = 1 + 136t + 8619t^2 + 271320t^3 + 4205460t^4
       + 31541664t^5 + 110396096t^6
       + 165593600t^7 + 82796544t^8.

lambda_min(K_f) = H(-t) > 0,
lambda_max(K_f) = H(t).
```

Each endpoint has eigenspace dimension 14,400. Every other irreducible
block lies strictly between them. Thus the exact Gram condition number
is H(t)/H(-t), the condition number of A_f is its square root, and the
least-squares coefficient-recovery norm is 1/sqrt(H(-t)). These constants
are sharp for the full alphabet. They remain valid for each subalphabet
by restriction, without a sharpness claim for a proper subset.

## 1. Complete module decomposition

The [Bell-line source proof](https://github.com/aliromman/integer-mult-bounds/blob/8561dad6b1dfd09d08b25564d70f4edb1270b5ee/research/clifford-width-ten-nullity/PROOF.md)
constructs the actual line extensions and both stabilizers. The
[all-odd-width phase proof](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md)
gives, because f-1=1 modulo 4,

```text
V^(tensor (f-1)) = V tensor W,
chi_W(s) = sigma^d 2^(p d),
sigma = (-1)^(p/2),       dim(W) = 2^(8p).
```

Here d is the fixed-space dimension of s on the natural binary space.
Consequently V^(tensor f)=(V tensor V) tensor W. The 256 Pauli weight
lines of V tensor V correspond to quadratic refinements of the
symplectic form. Their two orbits have the following stabilizers.

| Type | Orbit size l | Stabilizer H | Order | Irreducible rows |
|---|---:|---|---:|---:|
| minus | 120 | O8-(2).2 | 394,813,440 | 60 |
| plus | 136 | O8+(2).2 | 348,364,800 | 67 |

For each orbit representative q, use the actual Bell-line character
eta_q of its inertia group T_q. For an H irreducible rho of degree e,

```text
pi_rho = Ind_(T_q)^G(eta_q tensor rho),
dim(pi_rho) = l e,
m_rho(f) = <Res_H W, rho>.
```

The source proves that these are all irreducibles with scalar character
iI -> -1. The Bell character cancels in the multiplicity calculation;
it need not be trivial. Their regular dimensions sum to

```text
120^2 |H_minus| + 136^2 |H_plus| = N.
```

Thus all 127 blocks belong to this Gram matrix and exhaust it. The
other even sector, f=0 modulo 4, requires a different decomposition.

## 2. All 127 eigenvalue polynomials

For each stabilizer row let C_d be the sum of class size times its
character over elements with fixed dimension d. The retained projection
supplies C_1,...,C_7. Identity and character orthogonality give

```text
C_8 = e,
C_0 = |H| [rho is trivial] - sum_(d=1)^8 C_d.
```

The projected sums are real integers. Set x=sigma t. Central convolution
in the scalar-character ideal gives the eigenvalue

```text
lambda_rho = N m_rho / (16^f l e)
           = |H| m_rho / (e 2^(8p))
           = P_rho(x),
P_rho(x)   = sum_(r=0)^8 (C_(8-r)/e) x^r.
```

The normalization uses 16^f=256*2^(8p) and |S|=l|H|. It follows from
the projective regular representation, with each block repeated
(l e)^2 times. The
[normalization proof](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/PROOF.md)
explains the scalar-lift factor.

There is a separate coefficient calculation. Let R_(j,rho) be the
ordinary restriction coefficient from the Sp(8,2) row j of degree e_j,
and let P_j^S be its quotient spectral polynomial. Then

```text
P_rho(x) = sum_j R_(j,rho) e_j P_j^S(x) / (l e).
```

All 1,143 coefficient identities agree. This checks the whole width
family, not only the width-ten multiplicities in the source.

The Dickson character is delta(s)=(-1)^rank(s-I)=(-1)^d, since the
ambient dimension is eight. Tensoring rho by delta permutes the
irreducible rows and gives P_(rho tensor delta)(x)=P_rho(-x). The
checker confirms the complete degree-and-polynomial multiset identity
for both stabilizers. It does not identify a unique row permutation
when distinct interior rows have the same polynomial.

Two complete moment identities give additional checks. If c_d is the
number of Sp(8,2) elements with fixed dimension d, then

```text
sum_rho (l e)^2 P_rho(x) = N,
sum_rho (l e)^2 P_rho(x)^2
    = N sum_(r=0)^8 c_(8-r) x^(2r)/2^r.
```

The second formula also follows directly from the Pauli lifts: there
are 2^(8-d) nonzero projective traces of squared modulus 2^d over each
symplectic element. This gives the factor 2^(-r). Every coefficient
in both identities is checked exactly.

## 3. Strict endpoint order for the entire width range

The first minus row is trivial and has polynomial H(x). The second
minus row is Dickson and has polynomial H(-x). For 0<t<=1/64 the
certificate proves that H(-t) is the unique minimum and H(t) is the
unique maximum among all 127 rows.

There are 126 lower comparisons and 126 upper comparisons. The shared
endpoint pair is counted once, giving 251 distinct comparisons. Set
t=y/64. Every difference has constant coefficient zero, so divide by
y and write the result q(y) in the degree-seven Bernstein basis:

```text
q(y) = sum_(j=0)^7 b_j binom(7,j) y^j (1-y)^(7-j).
```

All 2,008 coefficients are strictly positive. The smallest is
1347892245/17179869184. The basis terms are nonnegative and sum to one
on [0,1]. Thus q is positive there, and y q(y)>0 for 0<y<=1. A separate
degree-eight Bernstein certificate for H(-y/64) has least coefficient
5741614935/34359738368>0. The checker expands every certificate back
into the power basis and requires exact equality.

Reflection by the Dickson character proves the same endpoint values
when x=-t. If f=2 modulo 8, the minimum is minus row two and the
maximum is row one. If f=6 modulo 8, these rows swap. Both have
Clifford degree 120, so both endpoint eigenspaces have dimension
120^2=14,400. No other row attains either endpoint.

The exact stability statement follows from the spectral theorem:

```text
H(-t) ||c||_2^2 <= ||A_f c||_2^2 <= H(t) ||c||_2^2.
```

Least-squares recovery from A_f c+error has coefficient error at most
||error||_2/sqrt(H(-t)), even for errors outside the column span. Since
H(t)=1+136t+O(t^2), the sharp leading condition terms are

```text
cond_2(K_f) = 1 + 272t + O(t^2),
cond_2(A_f) = 1 + 136t + O(t^2).
```

These are asymptotic coefficients, not finite-width bounds on the
unspecified remainder.

## Evidence and limits

Registered replay runs the unchanged stabilizer source checker, which
also runs its retained threshold source. All 40 source files are
authenticated. At the 22 widths 14,18,...,98, multiplicities are positive
integers, dimensions agree, and both squared-multiplicity sums agree
with independent quadratic-space tuple-orbit counts. The interval proof
supplies the infinite quantifier; those finite checks corroborate it.

A literal one-qubit calculation constructs all 24 projective operators,
checks all 576 products and computes four complete Gram matrices at
widths 6,10,14,18. Their five-root annihilators and first five moments
(including dimension) give the full spectral multiplicities 1,1,4,9,9.
Six controls reject a changed restriction coefficient, a missing orbit,
a wrong scalar factor, swapped endpoints, a positive but false
certificate, and a width from the other even sector.

Published ordinary character tables and class fusions remain
mathematical inputs. Their archive is not re-extracted here. The full
four-qubit Gram, full three-qubit suite, Lean, Docker and selected cold
replay are not run. The source conditioning and odd-spectrum checkers
are used only for generic arithmetic helpers; their full suites are
not invoked. The stabilizer and threshold source suites do run.

Native preparation, inverse realization, precision, routing, recovery,
stock and complete caller costs remain unknown. No independent human
or proof-kernel acceptance is claimed. T(4)=13, all five framework
assumptions and the selected frontier remain unchanged. No new kappa
follows.

## Open next questions

Determine the exact spectrum in the f=0 modulo 4 central sector. Its
Pauli characters have different inertia groups, so the two Bell
stabilizers above do not suffice.

Construct and price a decoder for a specified caller with this exact
stability contract. Include precision, owned recovery and stock costs.
