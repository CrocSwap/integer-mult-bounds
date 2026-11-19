# A Gaussian-dyadic left inverse for the Clifford tensor alphabet

This is an algebraic construction of a left inverse. It gives an explicit
coefficient-ring guarantee at a sufficient tensor width, without constructing
the enormous matrix or pricing a physical decoder. No new kappa is claimed.

## 1. Statement and boundary

Put `R = Z[i,1/2]`, fix `n >= 1`, and set `d = 2^n`. Let `G` be the
Gaussian-dyadic unitary Clifford group on `n` qubits, and choose one matrix
`U_a` in every scalar coset of `G / <iI>`. The scalar convention and signed
Hermitian Pauli action are those of
[alephnan's Clifford framework](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md).
Write `N = |G / <iI>|`. Define the raw tensor-column matrix

```text
C_f[:,a] = vec(U_a^(tensor f)).
f_0 = 4 n 2^n = 4nd.
```

**Theorem.** For every integer `f >= f_0`, there is an explicitly specified
matrix `L_f` with entries in `R` such that

```text
L_f C_f = I_N.
```

The specification consists of determinant, trace and polynomial coefficient
operations on the chosen representatives. It introduces no division by odd
integers. In particular, the columns generate a direct summand of the free
`R`-module of observations. The sufficient width is not asserted to be minimal.

For the full four-qubit alphabet, `d=16`, `N=12,128,668,876,800`, and
`f_0=256`. The normalized map used in
[Ali Romman's odd-width spectral proof](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md)
is

```text
A_f[:,a] = vec(U_a^(tensor f)) / 16^(f/2)
         = vec(U_a^(tensor f)) / 2^(2f).
```

Thus `B_f = 2^(2f) L_f` has entries in `R` and satisfies `B_f A_f=I_N`
for every integer `f >= 256`, including every residue class modulo four.
For general `n`, the same normalized conclusion follows whenever `nf` is
even. The raw theorem above does not need that restriction.

This answers the existence part of
[PR #7792's arbitrary-left-inverse question](https://github.com/aliromman/integer-mult-bounds/blob/9321c67e29c3c41a188154bc5c2add7d7802b694/research/clifford-odd-division-obstruction/PROOF.md)
at an explicit larger width. In particular, at `f=257` that source proves
that the canonical least-squares map has a necessary odd denominator, while
the present map has none. Existence at widths `13 <= f < 256`, the least
width for such a split injection, and an efficient or stable realization
are not settled here.

## 2. Elementary ring and Pauli facts

### Gaussian-dyadic numbers of modulus one

If `z=(a+bi)/2^k` belongs to `R` and has modulus one, then
`a^2+b^2=2^(2k)`, for integers `a,b` and `k >= 0`. For `k>0`, squares
modulo four show that both `a` and `b` are even. Divide them by two and
decrease `k` by one. Repetition reaches `a^2+b^2=1`, so

```text
z in {1, i, -1, -i}, and z^4 = 1.
```

If `U` is any unitary matrix over `R`, its determinant `Delta(U)` lies in
`R` and has modulus one. Therefore `Delta(U)^4=1`. This fact needs neither
a generating set for the Clifford group nor a determinant-one convention.

### Signed generator images distinguish scalar cosets

Use the `2n` Hermitian Pauli generators

```text
P_1,...,P_(2n) = X_1,Z_1,...,X_n,Z_n.
```

They square to the identity and have entries in `R`. Clifford conjugation
sends each one to a signed Hermitian Pauli. For any two signed Hermitian
Paulis `Q,Q'` that are not scalar identities, their normalized pairing is

```text
Tr(Q Q')/d =  1  if Q'=Q,
            -1  if Q'=-Q,
             0  otherwise.
```

This follows from the ordinary Pauli orthogonality relation; the Pauli
matrices form an orthogonal basis for all `d`-by-`d` complex matrices.

If `U_a` and `U_b` have the same signed conjugation image on every `P_j`,
then `U_a^* U_b` commutes with all `P_j`. Commutation with the `Z_j`
makes this matrix diagonal, and commutation with the `X_j` makes all its
diagonal entries equal. Hence `U_a^* U_b = zI`. It is unitary over `R`,
so the preceding ring fact gives `z in <i>`. Consequently the two chosen
representatives have the same coset. This proves that agreement on all
`2n` signed images is equivalent to `a=b`.

## 3. Homogeneous interpolation without odd division

Let `X=(x_uv)` be a matrix of independent commuting indeterminates over
`R`. Write

```text
Delta(X) = det(X),
Q_(a,j) = U_a P_j U_a^*,
t_(a,j)(X) = Tr(Q_(a,j) X P_j adj(X)) / d.
```

The adjugate is its usual cofactor polynomial, defined even when `X` is
singular. `Delta` is homogeneous of degree `d`; every entry of `adj(X)`
is homogeneous of degree `d-1`; therefore `t_(a,j)` is homogeneous of
degree `d`. All coefficients lie in `R`, because `1/d=2^(-n)` is a
dyadic unit. No inverse of a variable matrix is used in this definition.

At an alphabet point `U_b`, unitarity gives
`adj(U_b)=Delta(U_b) U_b^*`. Hence

```text
t_(a,j)(U_b) = Delta(U_b) u_(a,b,j),
u_(a,b,j) = Tr(Q_(a,j) Q_(b,j))/d in {-1,0,1}.
```

Now define the homogeneous polynomial of degree `2d`

```text
h_(a,j)(X) = (t_(a,j)(X)^2 + t_(a,j)(X) Delta(X)) / 2.
```

For `u in {-1,0,1}`, the value `(u^2+u)/2` is one exactly when `u=1`,
and zero otherwise. Thus

```text
h_(a,j)(U_b) = Delta(U_b)^2 * 1[Q_(a,j)=Q_(b,j)].
```

An individual factor need not itself be the indicator: its determinant
factor can be minus one. Retaining that phase is essential. Define

```text
F_a(X) = product_(j=1)^(2n) h_(a,j)(X).
```

This has coefficients in `R` and degree `4nd`. At every `U_b`, the
determinant phases cancel because
`(Delta(U_b)^2)^(2n)=Delta(U_b)^(4n)=1`. Section 2 then proves

```text
F_a(U_b) = product_j 1[Q_(a,j)=Q_(b,j)] = delta_(a,b).
```

Only powers of two have been divided out. In particular, a difference of
two spectral eigenvalues or two trace values is never inverted. That is
why odd factors in the canonical Gram inverse do not obstruct this
construction.

### Padding to every larger width

For each fixed representative define the degree-one polynomial

```text
ell_a(X) = Tr(U_a^* X)/d,
ell_a(U_a) = 1.
```

For `f >= f_0`, put

```text
F_(a,f)(X) = F_a(X) ell_a(X)^(f-f_0).
```

It is homogeneous of degree `f` over `R`, and
`F_(a,f)(U_b)=delta_(a,b)`. If `a!=b`, the first factor already vanishes;
if `a=b`, the padding factor equals one. The exponent can be zero.

## 4. From a polynomial to a linear tensor functional

The distinction between a polynomial in a matrix and a linear map on
tensor observations matters. A homogeneous degree-`f` polynomial is a
linear functional on the `f`-fold tensor coordinates, once an ordering
convention is fixed. Here that lift can be made without symmetrization
or factorial denominators.

List the `d^2` coordinates of `X` in a fixed order. Expand

```text
F_(a,f)(X) = sum_(alpha: sum alpha=f) c_(a,alpha) x^alpha.
```

For each multi-index `alpha`, choose the one ordered tensor word that
lists coordinate 1 `alpha_1` times, then coordinate 2 `alpha_2` times,
and so on. Give that word coefficient `c_(a,alpha)` and every other
word for the same commutative monomial coefficient zero. On
`vec(X)^(tensor f)` the resulting functional evaluates exactly
`F_(a,f)(X)`. The entries of `vec(X^(tensor f))` are a fixed permutation
of these same ordered products, so permuting the functional gives a
row indexed by the observations in `C_f`.

Stack the rows for all `a` to obtain `L_f`. Its entries are the
coefficients above or zero, hence lie in `R`. The interpolation identity
in Section 3 proves, entry by entry,

```text
(L_f C_f)[a,b] = F_(a,f)(U_b) = delta_(a,b).
```

No multinomial coefficient is divided out. This is a finite algebraic
specification for every fixed `n,f`; its possibly enormous number of
terms is not a polynomial-time or physical-resource bound.

The direct-summand conclusion also follows explicitly. `C_f L_f` is an
idempotent on the observation module, with image `im(C_f)` and kernel
`ker(L_f)`. Every observation `y` has the unique decomposition

```text
y = C_f L_f y + (y - C_f L_f y),
R^(d^(2f)) = im(C_f) direct_sum ker(L_f).
```

In particular, if a nonzero `r in R` and `ry` lies in `im(C_f)`, then
`r(y-C_f L_f y)=0` in a free module over the integral domain `R`.
Thus `y=C_f L_f y` also lies in the image: the column module is
saturated. No separate saturation assumption is required.

## 5. Recovery contract and relation to the canonical obstruction

For four qubits the normalized conclusion is

```text
B_f A_f = I_N,           f >= 256,
B_f in Mat_(N,d^(2f))(R).
```

It implies `B_f(A_f c)=c` for every complex coefficient vector `c`,
and in particular for every coefficient vector over `R`. The map `B_f`
is linear and defined on the entire observation space. For arbitrary
observations of the form `y=A_f c+e`, its output is

```text
B_f y = c + B_f e.
```

There is no claim here that `B_f e` is small, or that `B_f` minimizes a
norm or least-squares residual. On the image of `A_f`, every left inverse
agrees with exact recovery. Outside that image, different left inverses
may differ.

At width `257`, the canonical map
`A_f^+ = (A_f^* A_f)^(-1) A_f^*` exists and, by the scoped theorem in
PR #7792, does not have all coefficients in `R`. Since `B_257` does,
these are distinct maps. This is a positive realization of the
left-inverse distinction in that source; it does not contradict its
canonical-map obstruction. The spectral identification in PR #7792 is
needed for this comparison, but not for the interpolation theorem.

The result supplies no precision allocation, bounded recovery norm,
native preparation, routing, clean-stock funding, owned-state restoration
or full caller invoice. A finite algebraic matrix is not a physical
supplier. The selected exponent, five framework assumptions and existing
source packages remain unchanged.

## 6. Why the Clifford hypothesis cannot be dropped

Take `n=3`, let the target representative be the identity, and consider
the unitary Gaussian-dyadic matrix

```text
W = CCZ = diag(1,1,1,1,1,1,1,-1).
```

This is not a Clifford matrix. It commutes with every `Z_j`, so the
three corresponding normalized pairings `u_j` are one. For `X_j`,
conjugation changes the sign on exactly the two basis states whose
other two bits are one. Thus

```text
Tr(X_j W X_j W^*)/8 = (6-2)/8 = 1/2.
```

Its determinant is minus one, so the total determinant factor still
cancels. Nevertheless the proposed identity-target interpolant gives

```text
F_I(W) = (( (1/2)^2 + 1/2 )/2)^3 = (3/8)^3 = 27/512.
```

This is neither zero nor one. The indicator argument requires the
discrete pairings `{-1,0,1}` furnished by signed Pauli normalization;
unitarity and Gaussian-dyadic entries alone are insufficient.

The scalar convention matters as well. At width 256, `U` and `iU` have
identical tensor columns, so no left inverse can distinguish all exact
scalar lifts as separate columns. The theorem concerns one representative
per scalar coset, exactly as in the retained spectral contract.

## 7. Evidence, credit and next questions

The all-`n` and all-sufficient-width statements follow from Sections 2--4.
Finite evaluations check implementations and failure controls; they do
not replace this proof. In particular, no full four-qubit matrix or
left inverse is materialized, and no independent human or proof-kernel
acceptance is claimed.

Ali Romman supplied the canonical odd-division obstruction and the
four-qubit tensor normalization and spectral context. Nick Petalas
supplied retained character projections and related exact denominator
work. alephnan supplied the Gaussian-dyadic scalar and Pauli-sector
framework used above; its own source retains the pointwise-faithfulness,
MatShep and earlier Clifford lineage. Those sources retain their credit
and licenses. Adjugates, Pauli orthogonality, polynomial interpolation,
tensor coefficient lifts and direct-summand arguments are classical.
This contribution is the explicit dyadic interpolant and its application
to the different-left-inverse question. Prepared by **apoursh**, with
substantial OpenAI Codex and separate agent assistance. Apache-2.0.

The smallest useful next question is whether a Gaussian-dyadic left
inverse already exists near the known four-qubit complex independence
threshold, starting at width 13. A minor-ideal or modular rank obstruction
would distinguish failure of a split injection from mere failure of a
canonical inverse. The present construction gives the finite upper bound
256, without deciding the intermediate widths.

A separate implementation question is to bound the norm and realizable
cost of a specified left inverse at a specified caller. The sparse
polynomial specification alone does not supply such a bound or a
favorable complete signed bill.
