# When formal binary address identities are actual stream identities

## Declared action and claim

Fix integers d>=1 and w>=0. The address set is
`Omega_(d,w)=(F2^d)^w`: an ordered tuple of **w point columns**, each with
d bits. Equivalently it is a d by w binary matrix, or d coordinate words
of w bits each. A scalar register contains an arbitrary binary payload at
every one of these `2^(dw)` addresses. It is the vector space
`F2^Omega`, not just a single address vector or a homogeneous-coordinate
representation. There is no clean-input promise.

For G=GL_d(F2), g sends each column x_j to g*x_j. For G=AGL_d(F2),
g=(A,b) sends **every** column to A*x_j+b using the same b. Thus a coordinate
translation complements all w bits in that coordinate word. Allowing an
independent translation for each column would define a different group.
At w=0 the address set has one empty tuple.

Write P_g delta_X=delta_(gX). Extending linearly gives a representation
`rho_w:F2[G] -> End(F2^Omega)`. Faithful means injective as an algebra
representation; merely distinguishing group elements is insufficient.

**Theorem.** For d>=2, rho_w is faithful exactly when w>=d in the linear
case, and exactly when w>=d+1 in the affine case. For d=1, GL_1(F2) is
trivial and the representation is faithful for all w>=0; AGL_1(F2)=C2 is
faithful exactly when w>=1.

The proof uses the standard regular-orbit and orbit-stabilizer arguments.
The contribution here is the sharp boundary for this declared stream action,
its full dirty-register consequence, and a legal-word witness to the failure
below it. It is not a new general representation-theory principle.

## A regular orbit recovers all formal coefficients

If X has trivial stabilizer, the addresses gX for g in G are all distinct.
For any `c=sum_g c_g[g]`, the value at gX of `rho_w(c) delta_X` is exactly
c_g. Thus a single delta input recovers every formal coefficient. A regular
orbit suffices even when other address orbits have nontrivial stabilizers.

In the linear case w>=d, take the first d columns to be the standard basis
and any remaining columns zero. A matrix fixing them is identity. In the
affine case w>=d+1, take the first d+1 columns to be 0,e_1,...,e_d. Fixing
zero forces b=0, then fixing the basis forces A=I. Additional columns do
not enlarge the stabilizer. For the exceptional d=1 affine case, translation
already acts regularly on one point; no pair of points is necessary.

This applies entrywise to a matrix in `M_R(F2[G])` for any finite R. Feed
delta_X to input role j and zero to the other roles: output role i recovers
all coefficients of entry (i,j). These are legitimate basis tests for
equality on **all arbitrary inputs**, rather than a promise of clean helper
inputs. Consequently formal equality of complete endpoints is equivalent
to equality of actual full-stream operators at every faithful width.
The endpoint includes spectator identity and every off-diagonal coupling.

This equivalence applies to every finite word at each such w, including
words chosen separately for different widths, provided the alphabet and
action remain exactly the declared ones. It does not price physical storage
or grant free address conversion. An existing formal paid-call lower bound
therefore transfers under the same pricing and scalar-mixing conventions.

## The norm is a nonzero kernel element below the boundary

Let `n_G=sum_(g in G)[g]`. Its formal coefficients are all one, so it is
nonzero. For any address X and any Y in its orbit, exactly |Stab(X)| group
elements send X to Y. Hence rho_w(n_G) is zero if all point stabilizers have
even order. This is an all-input statement because the deltas span the
payload space.

In the linear case let the columns span a k-dimensional subspace, k<d.
In a basis beginning with that subspace, its pointwise stabilizer consists
exactly of matrices `[I_k B;0 C]`, where B is arbitrary and
C in GL_(d-k)(F2). Its order is

```
                 2^(k(d-k)) * |GL_(d-k)(F2)|.             (1)
```

For d>=2 this is even whenever k<d. If d-k>=2, the GL factor is even
(for example its order product contains `2^(d-k)-2`). If d-k=1, k=d-1>=1
and the first factor is even. Thus w<d forces every stabilizer even.

For an affine tuple with w>=1, translate its first point to zero. Fixing
the tuple is then equivalent to a linear transformation fixing all w-1
differences. Their span has dimension k<=w-1, and the stabilizer again has
order (1). For d>=2 and w<d+1 it is even. At w=0 the stabilizer is the whole
AGL group, of even order. In dimension one, the empty tuple still has the
two-element stabilizer, but any nonempty tuple has trivial stabilizer. The
linear d=1 group instead has order one, so its norm never vanishes. These
are substantive exceptions, not omitted small cases.

## A legal two-register word exhibits the failure

For either nontrivial group of even order, let D_g apply g to role 0 and
identity to role 1; let X add role 1 to role 0. X is a free scalar XOR in
the credited optimistic models. D_g is expanded into paid coordinate CNOTs
and, in the affine case, paid coordinate translations; elementary binary
row elimination generates GL, and adjoining translations generates AGL.
All inverses are charged. No clean role, reset or erasure is used.

Execute the following block chronologically for every g other than identity:

```
                         D_g, X, D_g^-1, X.
```

Its formal matrix is `I+([g^-1]+1)E_01`. Products of these off-diagonal
shears add their coefficients, since E_01 squared is zero. Inversion
permutes the nonidentity elements; because |G| is **even**, |G|-1 is odd,
so their coefficient sum is

```
          sum_(g!=1)([g^-1]+1) = sum_(g in G)[g] = n_G.
```

The complete word is `I+n_G E_01`, formally different from identity. At
every nonfaithful width proved above it nevertheless acts as identity on
both full arbitrary dirty streams. At a faithful width a delta on the
regular orbit exposes the nonzero coupling. This is a legal-word alias,
not merely a polynomial outside the invertible word algebra.

The retained explicit GL_2 word uses shortest address paths of total length
9 for the five nonidentity elements, then their inverses: **18 paid CNOTs
and 10 free scalar XORs**, two dirty roles, no extra role. RESULT.json records
the chronological word using generator indices from `generators(2,False)`.
The full formal replay is exactly I+n_G E_01. At w=1 all eight input basis
columns give identity. At w=2 six of the 32 input columns expose the norm;
all 32 agree with the full formal action. Deleting any of the 18 paid calls
fails the formal endpoint. Clean-only testing of role 1 would hide the
coupling even at w=2, which is why the full dirty boundary matters.

This example does not show that a particular monomial target becomes cheaper
below the threshold. It proves that unrestricted formal endpoint tests and
physical endpoint tests are different there; a target-specific transfer
could still be true by a separate argument.

## Source-bound consequence and limits

PR1974 at `a4992da8e4e81a74cf1fd2b2d3af948662476d6e`, retained in
`research/bit-gl3-mixed-targets-length10`, credits seed18 and certifies
`min=d(a)+d(b)` for all 28,224 two-register GL_3 target pairs under six
coordinate-CNOT labels and free scalar GL_2 mixing. The theorem above
transfers that **credited** formal conclusion to the specified full binary
bit-plane stream action for every w>=3, without changing the 36 paid
generators or endpoint. Its bounded third-register result also transfers
only with its existing length-seven coverage; lengths 8..12 remain open.
This package does not independently rerun or certify that predecessor's
C++ lower-bound census. Its unchanged README is an authenticated input.

PR1333 at `7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`, retained in
`research/binary-affine-register-bound`, already proves an arbitrary-register
floor for a broader affine rank-one alphabet and gives a nonzero norm killed
by a homogeneous representation. That earlier alias is credited. Here the
representation is the action on all point-tuples, with an exact width
threshold and a paid legal word; the predecessor's rank theorem is not
re-proved or re-counted.

None of these statements identifies this action with arithmetic modulo
q^w, a rational additive frame action, or a native selected tape layout.
An address coordinate here is a w-bit word with **bitwise binary** linear
operations, not an integer with carry. Scalar mixing is still optimistically
free. Restricted payload subspaces, independent affine offsets per plane,
changed group labels, physical compiler costs and selected supplier admission
need their own arguments. No multiplication exponent or frontier changes.

Finite exact checks for d<=3 corroborate the all-size proof. They are not a
substitute for it, a new exhaustive word search, or a formal-kernel proof.
Credit the predecessor authors and standard regular-orbit arguments.
Prepared for ywz65 with substantial OpenAI Codex assistance; Apache-2.0.
