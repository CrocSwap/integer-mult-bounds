# One spectator bit and a whole-layer terminal product

This note gives an exact terminal factorization. It is conditional on a
portwise endpoint for each complete layer. The retained paired controller
does not have that endpoint. Replacing two fields by two slices of one
existing address bit does not change that content fact.

## Exact product

Let z be one fixed address bit. Both z slices contain arbitrary data.
For a fixed port, let the operators Q_1,...,Q_m commute. Suppose

```text
Q_j^2 = X_(v_j),       Q_j^4 = I.
```

Here X_(v_j) translates active address coordinates and fixes z. Define
the affine pullback A_j and the involution T_j by

```text
(A_j f)(x,z)=f(x+z v_j,z+1),
T_j=Q_j A_j=[[0,Q_j],[Q_j^-1,0]].                       (1)
```

The matrix uses the order z=0,z=1. Thus A_j^2=X_(v_j), and A_j
commutes with Q_j. These statements do not require either slice to be
zero. A_j can be applied as a literal affine map on the same field.

Let E=T_m ... T_1, with T_1 applied first. Put

```text
epsilon_j=(-1)^(m-j),
U=prod_j Q_j^epsilon_j,
V=sum_j v_j,
V_minus=sum_(epsilon_j=-1) v_j,
S=[[0,I],[I,0]],       D_V=diag(I,X_V).
```

All vector sums are binary. Direct multiplication of the two by two
matrices gives

```text
E=diag(U,U^-1) S^m
 = Q_all X_(V_minus) D_V S^m,
Q_all=prod_j Q_j.                                      (2)
```

For the first equality, the upper entry acquires alternating exponents
when it passes each off-diagonal factor. For the second, use
Q_j^-1=Q_j X_(v_j), so U=Q_all X_(V_minus) and
U^-1=U X_V. There is no omitted scalar phase.

The factor M=X_(V_minus) D_V S^m is one affine address map. All Q_j
commute with M. Its exact inverse is

```text
M^-1=S^m D_V X_(V_minus),
E^-1=M^-1 Q_all^-1.                                    (3)
```

The displayed order is material when m is odd: S D_V and D_V S differ
by X_V. An implementation can retain (3) without a reordering rule.

## Native consequence and admission conditions

In the actual original complex line, C_q=alpha I+beta X_q, with
alpha=(1+i)/2 and beta=(1-i)/2. A layer with f_j tensor columns has
Q_j=C_(q_j)^tensor(f_j). If all layer columns have disjoint coordinate
supports, their D=sum_j f_j line directions are orthonormal. A binary
gather P gives

```text
Q_all=P^-1 C^tensor(D) P,
Q_all^-1=P^-1 [(-i)^D Z_all C^tensor(D) Z_all] P.         (4)
```

Thus (3) needs one native C_D call, one gather and its inverse, two sign
passes, one Gaussian-unit scale, and one affine map. It needs no new
zero field. All other coordinates, including z, remain spectators of
the native call. The native call and each map must be priced.

Equation (4) is an operator identity. It is not an admission of an
all-size child with D coordinates. In particular, a gather of all
completed outer offsets must satisfy the actual complete-row contract,
the chunk and guard conditions, and the volume and depth conditions.
The terminal cost is conditionally

```text
S(V,D) + cost(P,P^-1,Z_all,Z_all,M^-1,unit scale).
```

S includes all child work, helper restoration and precision costs. No
argument here sets the chunk width to one or discards inactive ranges.
A proof that this cost is below the outer multiplication bound remains
separate from (2).

The theorem also permits a known port permutation between complete
layers, provided it transports each Q_j and v_j covariantly and fixes z.
One follows each port through those permutations and applies (2) on
that path. Scalar bank maps on identical port types also commute with
the factors. A sum that mixes different port types, such as R or K,
does not satisfy this condition merely because the address supports of
two layers are disjoint.

The coordinates in (1)--(4) are the actual endpoint coordinates. If an
interface instead gives P_past^-1 E P_past, that conjugation must be
kept in the terminal word and priced. A completed Fourier factor on z
is not an affine address change and is not silently removed here.

## Why the unchanged paired controller is not an application

Slicing one field at z defines an exact vector-space isomorphism to two
fields. A linear raw core that preserves z acts equally on the two
slices. Under this isomorphism, (1) is exactly the previously emitted
two-replica operator. All arbitrary input values in both slices remain.

Consequently the retained nine-stage word still has the reviewed joint
map

```text
V_modes=-U_modes-T_query D_data,
D_data'=D_data-L U_modes-L P T_query D_data.
```

It is not a product of independent T_j maps on the old fields. For a
specific witness, the reviewed regular-cover vector

```text
h=(56I-R_1^*R_1) R_0^* e_k delta_identity
```

satisfies R_1 h=0, while the identity coefficient of R_0 h is 2912 e_k.
Use a constant active payload times the z-odd vector (1,-1), with all
initial mode values zero. The stage-zero mode query is nonzero, the
stage-one query is zero, and every later ordinary source coefficient
for this input is zero. Invertible mode-only transport cannot restore
the zero mode input. The same witness applies whether the two entries
are separate fields or z slices of one field.

This does not exclude a changed controller, an extra data read, a mixed
data/mode terminal, or a different invariant input domain. It identifies
the required new equality: the complete admitted layer must produce the
portwise code in (1), or another code with a proved terminal factorization.
The affine spectator realization alone does not supply that equality.

## Checks

Run `python3 -I -O -B check_spectator_terminal_product.py` in this
directory. Expected output is `PASS_SPECTATOR_TERMINAL_PRODUCT`.
The checker uses all 112 actual line labels and exact Gaussian
fractions. It verifies (2)--(3) for one through six disjoint layers,
both spectator slices and every nonzero kernel entry. Translation
covariance then gives every active input column. It rejects an omitted
controlled translation and a wrong order for the odd product inverse.
It pins the paired controller proof used for the content witness.

This is a terminal operator theorem and a scoped content check. It is
not a new supplier, a native whole-layer layout proof, or a complete
kappa improvement.
