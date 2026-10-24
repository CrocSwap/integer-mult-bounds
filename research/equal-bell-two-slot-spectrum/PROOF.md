# Exact spectrum on the equal-Bell two-slot subspace

Use the actual 112 port labels q in F2^9 and eight-entry root columns r_q
from the pinned historical query. Put B_lambda=4 A_lambda, so

```text
B_lambda = sum_q r_q r_q^T tensor Gamma_q^tensor(lambda).
```

The root coefficient occurs once. The doubled representation, one-slot Bell
formula and common positive-one vector of every Gamma_q are inherited from
Ali Romman's PR4958 and the sources retained by PR5168. PR5168 proves that
B_1 has minimal polynomial P of degree 881. Its complete proof is an inherited
premise here. We authenticate its certificate and recompute its polynomial
LCM and hash; we do not rerun its full upper/lower scientific replay.

## A complete reduction for equal outer Bell labels

In the one-slot Bell block c, the port acts on the remaining address a as
X_q if q.c=1 and Z_q if q.c=0. Thus the two-slot joint block (c,d) is

```text
B_(c,d) = sum_q r_q r_q^T tensor P_q(c) tensor P_q(d).
```

For c=d, the payload factors commute. A second Bell basis is

```text
b_(u,v) = 2^(-9/2) sum_a (-1)^(a.v) e_a tensor e_(a+u).
```

The 512^2 vectors are orthonormal: distinct u have disjoint supports, and
for fixed u the Walsh characters in v are orthogonal. X_q tensor X_q acts
by (-1)^(q.v); Z_q tensor Z_q acts by (-1)^(q.u). Consequently every
8-dimensional root space tensor b_(u,v) is invariant, and its exact matrix is

```text
M(c,u,v) = sum_(q.c=0) (-1)^(q.u) r_q r_q^T
         + sum_(q.c=1) (-1)^(q.v) r_q r_q^T.
```

This gives all equal-label spectra, not just selected vectors. Let
F(t)=sum_q (-1)^(q.t) r_q r_q^T. Then

```text
M(c,u,v) = (F(u)+F(u+c)+F(v)-F(v+c))/2.             (1)
```

The complete equal-label subspace has dimension 512^3*8=2^30. It is a
proper invariant subspace of the full width-two space of dimension 2^39.
Unequal outer labels are not classified by this formula.

## Source symmetry and finite coverage

PR5168 supplies 13 signed root permutations with orthogonal label maps T.
The verifier reruns their exact all-port root/label correspondence and their
512-label orbit computation. Orthogonality gives q.c=(Tq).(Tc), and the
root sign disappears in r_q r_q^T. The same root permutation and two address
permutations therefore conjugate B_(c,c) to B_(Tc,Tc).

Every actual q has odd parity. Walsh Fourier on both remaining address
spaces exchanges X_q and Z_q and conjugates (c,c) to (c+511,c+511).
The source-verified orbit representatives and sizes are

```text
(0,2), (1,224), (3,224), (7,16), (30,14), (128,32).
```

This uses the predecessor's symmetries in a new two-slot implication; it
does not claim a new symmetry discovery. Equation (1) evaluates all 512
values of each plus and minus term. Duplicate matrices can be removed
because every pair (u,v) is permitted independently. Thus the Cartesian
product of the distinct plus and minus arrays has exactly the same spectrum
as all 512^2 choices, with multiplicities omitted. It contains 190239 pairs
across the six representatives. This is a complete finite cover of the
specified equal-label subspace, not an exhaustive cover of width two.

## Exact minimal polynomial

Every M is a real symmetric integer matrix. It is diagonalizable, so its
minimal polynomial over Q is the square-free part of its characteristic
polynomial. Taking the monic LCM over all matrices gives the exact minimal
polynomial on the direct sum. The computed degrees are:

| c | Distinct plus/minus arrays | Matrix pairs | Characteristic polynomials | Minimal degree |
|---:|---:|---:|---:|---:|
| 0 | 273 / 1 | 273 | 11 | 9 |
| 1 | 194 / 202 | 39188 | 271 | 191 |
| 3 | 200 / 192 | 38400 | 286 | 251 |
| 7 | 185 / 199 | 36815 | 111 | 87 |
| 30 | 201 / 187 | 37587 | 110 | 81 |
| 128 | 202 / 188 | 37976 | 97 | 67 |

The LCM E has degree 255. RESULT.json contains each representative polynomial
and E in ascending integer coefficient order, together with hashes of the
complete characteristic-polynomial histograms. The square-free argument
proves minimality as well as annihilation; no numerical spectral tolerance
or random rank witness is used.

The verifier computes every characteristic polynomial by exact trace
recurrences and checks the final full matrix Horner remainder is zero.
For all 886 distinct characteristic polynomials across the representatives,
a separate symbolic determinant on a literal port-sum matrix agrees exactly.
That second path uses Python/SymPy integers and does not use the trace
recurrence or equation (1) to construct its matrix. SymPy and NumPy are
trusted arithmetic libraries, not proof kernels. FLINT was used only for
candidate discovery and is absent from the clean verifier environment.

## New spectrum and higher-width consequence

At c=1, u=0, v=2, the second standard root vector is an eigenvector of M
with eigenvalue 32. Exact evaluation gives P(32)!=0. Thus A_2 has eigenvalue
8, absent from A_1. In particular, the complete one-slot annihilator does
not extend to all widths.

More fully, deg(E/gcd(E,P))=212 and deg(lcm(E,P))=1093. The predecessor's
common fixed vector embeds B_1 in B_2 and embeds B_2 in every B_lambda for
lambda>=2. Hence each such minimal polynomial must be divisible by E and
P, and has degree at least 1093. This is not an upper bound for B_2 or for
any larger width. The new 212 degrees come from a complete equal-label
classification, not a small sampled increase of a Hankel minor.

If alpha I+beta A_lambda is invertible in characteristic zero, beta!=0,
and q(A_lambda) is its inverse, then

```text
((alpha+beta t)q(t)-1)(A_lambda)=0.
```

The displayed polynomial is nonzero and has degree at most deg(q)+1.
For lambda>=2, it follows that deg(q)>=1092. This concerns scalar polynomial
inverses only. It gives no lower bound for general ADD circuits, rational
expressions or matrix-valued encodings, and no physical tariff.

## Arithmetic bounds and limits

The query satisfies sum_q r_q r_q^T=56 I. Every signed sum M therefore has
operator norm at most 56. The implementation also checks symmetry and the
conservative maximum absolute row-sum bound 112 before each trace recurrence.
For a symmetric 8-by-8 matrix of norm at most 112, the kth recurrence matrix
has spectral norm at most binomial(7,k)*112^k. This follows by diagonalizing:
each eigenvalue is, up to sign, the kth elementary symmetric function of
the other seven eigenvalues. Each product dot sum and the subsequent trace
is bounded conservatively by 64*binomial(7,k-1)*112^k. For 1<=k<=8 these
bounds are all below 2^63. Coefficient additions also fit. Every division
by k is checked exact. Thus NumPy signed int64 arithmetic cannot overflow
in the fixed accepted domain. LCM and determinant arithmetic use unbounded
integers. The maximum batch contains 202 matrices of size 8 by 8.

The literal Bell check covers 286720 actual port/address columns across five
nonzero representative fixtures. The all-label conclusion follows from the
written Bell identity and complete source symmetry cover. Nine controls
exercise type/monicity, matrix dimension/symmetry/norm, swapped sign labels,
wrong outer label, missing half projections and a changed annihilator.
Source and typed-result corruption checks are separate integrity controls.

No full predecessor scientific replay, selected native/supplier replay,
Lean, Docker or independent human review is claimed. The actual historical
query is preserved; it is not a new selected #4610 supplier. All native
access, precision, workspace, dirty restoration and complete recursive
cost obligations remain open. The selected frontier and kappa are unchanged.

## Attribution

Krzysztof Wojt, with OpenAI Codex assistance, supplied PR5168's one-slot
polynomial, source symmetries and executable model. Nick Petalas supplied
PR5120's preceding exact lower certificate. Ali Romman's PR4958/PR4720
supplied the actual query, Bell identity and fixed-vector lift; PR1719
supplies the doubled representation. JoyboyBrian's released gate supplies
prior symmetry findings. Preserve icekylinx's Gauge44 credit and the full
native/helper/compiler and upstream lineage in the retained NOTICE.

New equal-label reduction, spectrum classification and higher-width bound:
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0. No literature
priority is claimed for Bell diagonalization or the trace recurrence.
