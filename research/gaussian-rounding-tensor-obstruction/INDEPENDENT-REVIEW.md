# Independent review of the all-axis Gaussian tensor obstruction

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. This is a fresh written mathematical review of
`PROOF.md`, including
the nonzero-output sharpening in Section 6. No duplicate finite computation,
human peer review or proof-kernel acceptance is claimed.

**Conclusion:** the all-axis defect identity, broad sharp bound and stronger
sharp bound are valid under the stated hypotheses. No scalar or phase error
was found. The argument does not assume covariance under the nonunit alpha.

## Phases and the universal identity

Writing alpha=(1-i)^n and N=2^n, one has

    (1-i) M = [[1,-i],[-i,1]],
    alpha U_rs = (-i)^wt(r xor s).

Thus alpha clears the tensor denominator with its absolute phase intact.
The phase ratio is alpha/conjugate(alpha)=(-i)^n, so

    lambda_r=(-i)^n i^wt(r)=alpha(U^-1 e0)_r.

Every lambda entry is a Gaussian unit. Direct bit factorization gives a
factor two at each zero bit of r and zero at each one bit, proving
alpha U lambda=(-i)^n N e0=alpha^2 e0. This verifies U lambda=alpha e0
for every n, independently of a finite tensor enumeration.

For X=lambda z^T, column-first uses exactness on lambda times a Gaussian
scalar to give e0(alpha z)^T. Row application then gives e0(alpha Uz)^T,
using exactness on alpha z. Row-first instead gives lambda(Fz)^T by global
unit covariance on each row; its column application is exactly
e0(alpha Fz)^T. This proves the stated difference and norm equality.
Ordinary transpose is the correct convention; no complex conjugation is
introduced when forming the rank-one array. F need not be linear.

The two exactness uses are legitimate because alpha U is Gaussian-integral
and U(lambda t)=alpha t e0. Multiplication by alpha is not assumed to
commute with F; that particular evaluation follows from exactness.

## Integer gap, nearest-grid claim and broad sharpness

At z=e0, each first-row defect entry is a Gaussian unit minus alpha times
a Gaussian integer. For n>=1, alpha is a nonunit, so every entry is a
nonzero Gaussian integer and has magnitude at least one. All other rows
vanish. There are exactly N first-row entries, proving norm at least sqrt(N).

The equivalent nearest-grid argument is valid. For n=1, each real and
imaginary component of Ue0 is plus or minus one half. For n>=2, each complex
coordinate has magnitude at most one half, so both real components do too.
Zero is therefore a nearest Gaussian lattice vector, and ||Ue0||=1 by
unitarity. The ties at n=1 and n=2 do not invalidate the claim.

Nearest-even component rounding is odd and commutes with the swap/sign
action of multiplication by i. Applied to Uz it is globally unit-covariant
and exact whenever Uz is integral. It sends e0 to zero for every n>=1,
so it attains squared defect N. It also sends zero to zero, and hence is
not bijective; its basis-input sum is zero, so it is not sum-preserving.
The broad sharpness statement correctly does not assert those properties.

## The stronger bound and its sharp bijective attainment

Let w=F(e0) be nonzero and put m=2^(-ceil(n/2)). Every real or imaginary
component of q=Ue0 has absolute value at most m. For the Gaussian integer
L1 mass L=sum_j(|Re w_j|+|Im w_j|),

    ||w||^2 >= L >= 1,
    Re <q,w> <= m L,
    ||q-w||^2 >= 1+(1-2m)L >= 2-2m.

The last inequality uses m<=1/2, valid for n>=1. Multiplication by
|alpha|^2=N gives squared tensor defect at least

    N(2-2m)=2N-2^(floor(n/2)+1).

Injectivity implies w!=0 because exactness gives F(0)=0. Sum preservation
also implies it because the basis-input sum is one. Neither property is
needed separately once w!=0 is assumed. The stronger bound equals the
broad bound for n=1,2 and is strictly stronger for n>=3.

A maximizing coordinate can be chosen without a search:

    j=2^floor(n/2)-1.

Its weight is floor(n/2), so q_j has phase zero for even n and phase pi/4
for odd n. In both cases Re q_j=m. Setting w=e_j attains all inequalities.

The proposed global attainment construction is valid as well. Let
L_U={z in G^N:Uz is integral}. Since U^2=J and U^4=I, U maps L_U bijectively
onto itself. This set is stable under Gaussian units. The full global-unit
orbits of e0 and e_j are outside L_U, since every entry of their ideal
images is a unit divided by the nonunit alpha.

Define F=U on L_U. On its complement swap those two global-unit orbits,
or do nothing if j=0, and fix everything else. The two domains are disjoint
invariant sets, and each restriction is a bijection. The construction is
globally unit-covariant and integral-image exact. U preserves coordinate
sums, while the swapped vectors have the same unit sum, so the whole map
preserves sums. It sends e0 to e_j and attains the stronger bound. This
does not furnish a bounded-error approximation or an exact-square rounder;
those properties are not used or claimed for this attainment example.
The proof's explicit failure controls are correct: adding alpha t e0 to e0
stays outside L_U and eventually outside the finite swapped orbits, making
the identity-complement error unbounded; the complement permutation squares
to identity, whereas J moves e0 for every n>=1.

## Boundary and assumptions that can be weakened directly

For n=0, U=I and alpha=1. Exactness forces F=I. The defect identity still
holds, but its value is zero and the positive lower bounds do not apply.
The n>=1 condition is therefore essential to the incompatibility claim.

The all-input defect identity needs integral-image exactness only on
lambda G and alpha G^N, as the proof already states. For the fixed witness
lambda e0^T and either lower bound, it can be weakened further to exactness
on lambda G plus the single input alpha e0. Covariance is only needed on
the global-unit orbit of e0 for that witness. These local hypotheses suffice
because the unknown entries of F(e0) are Gaussian integers and the second
column evaluation stays in lambda G. No claim is made that these conditions
are necessary or that covariance can be removed altogether.

The sharper inequality's exact extra hypothesis is only F(e0)!=0, weaker
than injectivity or sum preservation. This is the appropriate formulation
if those stronger assumptions are not otherwise required by a caller.

If the integer codomain is relaxed, using U for both fiber orders is a valid
commuting comparison on the enlarged rational-Gaussian domain. That control
requires a domain closed under the intermediate rational outputs; it should
not be described as evaluating a G-only map on inadmissible inputs.

The fixed positive-grid scaling is valid: both evaluated arrays and their
defect scale by h, as does the Frobenius norm of the explicit witness.
No precision, storage, physical tariff or selected-theorem conclusion follows
from that scaling. Applying this obstruction to an actual caller still
requires proving that it demands the stated independent fiber contract.
