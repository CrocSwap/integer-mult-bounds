# Spectator terminal proof review

The conditional operator theorem and its phase addendum pass this proof
review. Execution and final package integrity are recorded separately.
This note adds no construction, search, or kappa claim.

## Product and order

The theorem uses one fixed spectator bit z with two arbitrary input
slices. Each Q_j acts on the active coordinates in the same way on both
slices. The Q_j commute, satisfy Q_j^2=X_(v_j), and have fourth power I.
The translations fix z. The theorem does not require the T_j to commute.

With T_j=[[0,Q_j],[Q_j^-1,0]], direct multiplication gives alternating
exponents in the chronological product E=T_m ... T_1. For
epsilon_j=(-1)^(m-j), put U=prod Q_j^epsilon_j. Then
E=diag(U,U^-1) S^m. Since Q_j^-1=Q_j X_(v_j), the binary vector sums
V and V_minus give

```text
E = Q_all X_(V_minus) D_V S^m = Q_all M,
E^-1 = S^m D_V X_(V_minus) Q_all^-1.
```

Every Q_j commutes with M: it commutes with the other Q factors and
their squares, and it acts equally on the two slices. The inverse
retains its displayed order. In an odd product, S and D_V need not
commute. Moving the slice flip across the controlled translation can
change the result by X_V.

This argument applies to every finite positive number of factors and
all widths that satisfy the operator premises. Its justification is
the ordered matrix identity, not an extrapolation of finite cases.
No slice is initialized or discarded.

## One native factor, conditional admission

For the actual original line, C_q=alpha I+beta X_q. Directions from
disjoint coordinate supports are independent. The actual odd port
labels have unit binary norm. A binary gather can therefore identify
the D selected directions with D distinct coordinate bits, giving
Q_all=P^-1 C^tensor(D) P. The source identity
C^-1=-i Z C Z gives the inverse factor with two sign passes and the
Gaussian unit (-i)^D.

This proves one C_D operator factor. It does not prove an admitted
all-size child on those coordinates. The complete-row, chunk, guard,
volume, depth, helper-restoration, and precision contracts remain
premises. The gather, inverse gather, signs, unit scale, affine map,
and native child all have costs. The note does not set chunk width to
one, discard inactive ranges, or prove that the total cost fits an
outer supplier bound.

Port permutations can be followed only when they transport the line
operators and translation vectors covariantly and fix z. A scalar bank
map may cross the factors only for identical port types. This does
not permit the actual R or K to mix different types without proof.
An endpoint conjugation by a past transform must remain in the word.
A Fourier operation on z is not an affine address map.

## Phase and twiddle addendum

The separate addendum is required. For each layer j, S_j is a monomial
operator on that layer's active coordinates, with identity action on
z and on all other layers. Its coefficient cannot depend on z.
These premises imply S_k T_j=T_j S_k for k different from j and give

```text
(S_m T_m S_m^-1) ... (S_1 T_1 S_1^-1)
    = S_all E S_all^-1.
```

The inverse has ordered wrappers S_all M^-1 Q_all^-1 S_all^-1.
Each wrapper still has a cost. Fixing the address value of z is
insufficient: a z-dependent diagonal phase can fail to commute with
the slice flip.

The exact retained layer source has H0=b S C S. Thus a native endpoint
E_j C_j becomes (S_j E_j S_j^-1) H0_j. The code is placed before the
current outer twiddle. That twiddle depends on both the current branch
and unprocessed bits, so it is not one of the disjoint-support S_j
operators. The existing current-twiddle limitation remains in force.

An application must prove a complete-round portwise endpoint after
the twiddle, implement a valid encoded twiddle, or return the raw H0
operation. The spectator product does not supply any of these.

## Unchanged paired controller

The retained controller proof has a mixed data/mode endpoint. An exact
isomorphism between two fields and two productive slices preserves
that endpoint. It cannot turn it into independent portwise T factors.

The inherited witness uses the source schedule (1,1,0,...,0) on the
initial X0 bank and distinct involutive stage-one routes. Under those
facts, h=(56I-R_1^*R_1)R_0^*e_k delta_identity satisfies R_1h=0, while
the identity coefficient of R_0h is (56^2-224)e_k=2912e_k. A constant
active payload and the z-odd input (h,-h) give a nonzero first query
and zero later queries. Invertible mode-only maps cannot remove that
signal. This conditional proof transfers to the slice representation.

The terminal checker verifies the scalar 2912 calculation and pins
the controller proof. It does not reconstruct the route witness or
rerun the source schedule. The separate controller proof review also
retains those producer dependencies. Their status must remain explicit.
No general controller obstruction or native-child lower bound follows.

## Finite checks and their limits

The actual-label checker uses exact Gaussian fractions for 112 ports,
one through six disjoint layers, and both slices. Its translation
covariance gives all active input columns from the origin kernels.
It checks 1344 slice cases and 28224 nonzero kernel entries. It rejects
672 omitted-control cases and 672 wrong odd-inverse-order cases.

The independent checker uses formal commuting fourth-root generators.
It imports no producer kernel and checks 64 cases: lengths one through
32 and both initial slices. It separately checks the alternating
exponents, affine factor, inverse order, and odd-order failure control.
It is independent evidence for the ordered identity. It is not an
independent replay of native layout, the controller witness, or a
complete layer endpoint.

The accepted claim is a conditional terminal factorization with a
necessary phase qualification. A complete portwise layer endpoint,
native admission, final physical layout, helper host, finite invoice,
and recursive precision remain separate obligations. No complete
supplier or kappa improvement is established.
