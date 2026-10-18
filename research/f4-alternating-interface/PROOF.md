# Exact interface statement

## 1. The trace obstruction is real, but narrower than compilation

Put F4=F2[t]/(t^2+t+1), conjugation a -> a^2, and Tr(a)=a+a^2.
For a Hermitian matrix H define

    h(x,y) = conjugate(x)^T H y,
    B(x,y) = Tr(h(x,y)).

B is symmetric F2-bilinear. Hermitian symmetry forces h(x,x) to belong to
F2, whose field trace is zero. Thus B(x,x)=0 for every x: B is alternating.
No positive-dimensional restriction can have an orthonormal basis for B.

The radical of B is exactly the radical of h, considered as an F2 space.
One inclusion is immediate. For the other, suppose h(x,y)=a != 0. By
scaling y by c, h(x,cy)=ca can take any field value, including t with
Tr(t)=1. Then B(x,cy)!=0. Consequently a nonsingular Hermitian H of
F4 dimension n has a nonsingular alternating trace form of F2 rank 2n.
More generally its binary rank is twice its F4 rank. The checker independently
counts H's nullspace by enumerating all field vectors, then compares it with
packed binary elimination of B. It includes singular H rather than assuming
all frames are nonsingular.

## 2. An alternating block admits a valid fourth-root quadratic phase

Let G be a symmetric nonsingular alternating binary r-by-r matrix. For
any linear mask ell define

    q(x) = 2 sum_{i<j} G_ij x_i x_j + 2 sum_i ell_i x_i (mod 4).

A direct expansion gives

    q(x+y) - q(x) - q(y) = 2 x^T G y (mod 4).

All additions in the argument are XOR. This is a quadratic refinement;
its values are even, but that does NOT make its polar form zero. In
particular q(a,b)=2ab refines the hyperbolic matrix [[0,1],[1,0]].

Let S=sum_z i^q(z) and let W(t)=sum_z i^q(z) (-1)^(z^T t).
Shifting the summation variable by v gives the exact complete-square identity

    W(Gv) = S i^(-q(v)).

The Fourier multiplier kernel is therefore

    K(x,y) = 2^-r W(G(x+y))
           = 2^-r S i^(-q(x)) (-1)^(x^T G y) i^(-q(y)).

This is the same normal-form identity as the pinned endpoint note in a
different coordinate convention: that note starts with polarization G^-1
and hence uses q(Gx). Here q has polarization G, so it uses q(x).
There is no assumption of an orthonormal basis in either formula.

Every nonsingular alternating form splits into hyperbolic pairs: choose
nonzero u, choose v with B(u,v)=1, and split off their nondegenerate span
by orthogonal projection. Repeat on its complement. On one pair a
refinement is 2(ab+alpha a+beta b); direct summation gives

    sum_{a,b} (-1)^(ab+alpha a+beta b) = 2 (-1)^(alpha beta).

Hence r is even, |S|^2=2^r, and S=+/-2^(r/2).
With b=(1-i)/2, S b^r is a fourth root of unity. The scaled Walsh kernel
is a binary permutation of H0^tensor-r, where

    H0 = (1/2) [[1,1],[1,-1]] = b diag(1,i) C diag(1,i),
    C = (i I + X)/(1+i).

Thus the normal form uses one rank-r C child, binary address changes,
diagonal fourth-root phases and a scalar fourth-root phase, exactly as
in the repository endpoint note. This inherits that compiler's physical
and analytic conditions; it is not an independent all-size implementation.
The child itself retains its ordinary precision bill; no free arithmetic,
free wrappers, free copies or reduced recurrence cost is asserted.

## 3. A concrete legal ambient block

In F2^3 with its ordinary dot product, take u=110 and v=011. Both have
even norm and u dot v=1. Their span is nondegenerate, with hyperbolic Gram
matrix G. The ambient weight refinement is

    q(a,b)=weight(a*u+b*v) mod 4 = 2a+2b+2ab mod 4.

Its values are [0,2,2,2], Gauss sum -2, and S b^2=i. This supplies an
actual even-weight ambient residual block, not just an abstract form.
Its orthogonal complement is the nondegenerate line 111. The checker
executes the complete kernel identity on this embedded block separately.

## 4. Coverage and rejected controls

The field census includes every Hermitian matrix in dimensions 1,2,3
(2,16,512 matrices respectively), with all field-vector nullspaces. The
phase census includes all symmetric alternating nonsingular matrices in
binary dimensions 2 and 4 and every even-valued quadratic refinement
(4 and 448 cases respectively). Every polarization pair and kernel entry
is checked, as is the exact Gauss magnitude and fourth-root normalization.

Controls reject: a changed phase that violates polarization; a singular
Gram input; a perturbed Gauss scalar that spoils the kernel; and the
replacement of the Hermitian product by an unconjugated product. For the
last, x=t has Tr(conjugate(t)*t)=0 but Tr(t*t)=1. All checking conditions
remain active under `python -O` (no implementation assertions).

## What this does not settle

The historical report was discussing a particular orthonormal phase
calculus. Its statement remains an obstruction to that narrow method.
The added finding is that it cannot be used as a general exclusion of
alternating-compatible compilers already documented elsewhere in the
repository. There is no contradiction in the trace computation itself.

Degenerate trace restrictions remain a problem: nonsingular full H does
not imply every support or intersection is nondegenerate. A supplier also
requires fitting labels, source/read incidence, nested frames, paid adapters,
restorable auxiliaries, physical owners and fresh composition. None is
supplied here. Existing copy-floor results are not invalidated by this audit.
