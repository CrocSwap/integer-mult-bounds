# Sparse factorization of the tensor-root identity

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Fix an integer s>=1 and n=2^s. Index rows and columns by binary words of length s,
also identified with subsets of {1,...,s}. Let

```text
G = [[2,1],[1,2]]^(tensor s),
B = (G + J) mod 2.
```

These are the Gram matrix and the binary pairing used in Cinna Davis /
1337isnot1337's [PR3895](https://github.com/CrocSwap/integer-mult-bounds/pull/3895).
The two starting roots are (1,1,0,0,0,0,0,0) and (1,0,1,0,0,0,0,0).
Their tensor products give G. The identity to factor is **2G over Q**, hence
also over C with ordinary transpose. This is the predecessor's changed tensor
alphabet, not the selected E8 alphabet.

A term p q^t has COPY charge rank_F2 B[supp(p),supp(q)]. The term weights
are exact scalar coefficients. We construct n terms with profile

```text
(n-1) H1 + Hn.
```

Their rank mass is 2n-1. This is a constructive upper bound, with no assertion
that it is the minimum over all factorizations. The all-s claim is a scoped
written algebraic proof. The executable corroborates s=1,...,6 exactly.

## The factorization

Put

```text
U = [[2,0],[1,1]],       W = diag(1/2,3/2).
[[2,1],[1,2]] = U W U^t.
F = U^(tensor s),        w_z = 2^(1-s) 3^|z|.
```

Taking tensor powers gives

```text
2G = F diag(w_z) F^t = sum_z w_z F[:,z] F[:,z]^t.       (1)
```

Every w_z is nonzero and dyadic. A literal factor pair is p_z=w_z F[:,z],
q_z=F[:,z]. Its supports coincide, and

```text
F[x,z] = 2^(s-|x|) if z is a subset of x, and zero otherwise.
S_z = {x : z is a subset of x}.
```

There is also a direct entry proof independent of the matrix product rule.
The (x,y) entry of the right side of (1) is

```text
2^(1+s-|x|-|y|) sum_(z subset x intersect y) 3^|z|
 = 2^(1+s-|x|-|y|) 4^|x intersect y|
 = 2^(1+s-|x symmetric_difference y|) = 2G[x,y].
```

Thus every scalar coefficient of the full matrix identity agrees. No entry
is discarded through a mask or by a promise on the inputs. In particular,
for arbitrary complex x,y the weighted scalar queries give exactly x^t(2G)y.

## Support charges

Modulo two, the base Gram matrix is the two-bit exchange matrix. Hence its
tensor power P sends x to its bitwise complement, denoted bar(x), and B=J+P.
The n-dimensional all-ones matrix satisfies J^2=nJ=0 over F2. Thus
(I+J)^2=I. Since P is invertible and PJ=J, B=P(I+J) is invertible and has rank n.

For z=0 the support S_0 is the whole set, so the term costs n. For any z!=0,
choose a coordinate in z. Every x,y in S_z has value one at that coordinate,
so y cannot equal bar(x). Consequently P[S_z,S_z]=0, and

```text
B[S_z,S_z] = J[S_z,S_z].
```

The support is nonempty, so this block has rank exactly one. There are n-1
nonzero z. This proves the stated profile and rank mass.

At s=4 the profile is 15 H1 + H16, of mass 31. PR3895's displayed dense
factorization has 16 H16, of mass 256. Those predecessor counts are cited
comparison data, not a replay deliverable. More generally, for any real t>0
the dense versus sparse power-price difference is

```text
n*n^t - (n^t+n-1) = (n-1)(n^t-1) > 0.
```

This compares only these local COPY profiles under the same declared tariff.
It does not compare complete suppliers or grant a recursion normalization.

## Frame arithmetic and scope

Each factor of F has three nonzero entries, so F has exactly 3^s nonzero
entries. Both unweighted input transforms use F^t. The inverse of U is
[[1/2,0],[-1/2,1]], so F and its inverse are Gaussian-dyadic matrices.
This supplies an exact scalar frame inverse, with every payload coordinate
retained. One can keep the weights in the final scalar accumulation.

The weighted factor F diag(w_z) is invertible over Q, but for s>=1 its inverse
need not be Gaussian-dyadic because of the factors 3. No dyadic inverse of that
weighted frame is claimed. Reversible use of the unweighted F is a different
contract from requesting such an inverse.

The rank of B is still n. For n=16 it therefore cannot be represented by a
bilinear pairing of nine-bit labels. ToikY's [PR3928](https://github.com/CrocSwap/integer-mult-bounds/pull/3928)
already establishes the literal tensor-pairing embedding boundary; reducing
the term supports here does not change it. No new selected-port embedding is
claimed.

Scalar frame invertibility is not a native realization or a dirty-helper
program. Native source/reader transport, coefficients and scaling, temporary
precision, arbitrary ambient dirt outside the product-root span, ownership,
restoration, the complete paid and productive invoice, compiler and outer
admission remain unpriced. No new kappa, selected-frontier change or complete
multiplication theorem follows. All five selected framework assumptions remain.

## Credit

Cinna Davis / 1337isnot1337, PR3895, supplies the root-pair tensor identity,
the changed pairing, dense comparator and block-interface question. ToikY,
PR3928, supplies the embedding obstruction. DreamingOfClouds / PR717,
themilkman216 / PR968 and woklerx / PR1077 retain the decoder conventions;
the preceding E8/native/Clifford lineage retains its credit. LDL factorization,
Kronecker products, Boolean-subset sums and binary elimination are classical.
The new contribution is the sparse factorization with its exact support-aware
COPY profile for this tensor-root interface. No broad literature-priority
claim, independent human review or formal proof-kernel acceptance is made.
