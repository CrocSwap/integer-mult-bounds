# Exact conditioning of the positive-line centre section

The reviewed squared-line code gives more than an algebraic right
inverse. It gives a uniformly bounded complement to the actual query
kernel at every tensor width. This note states its exact conditioning
and identifies the line-power classes in which such a section exists.
These are operator norms for the coefficient Hilbert space. They do
not replace the stored-field and arithmetic guards of a native word.

Use the actual B, D=B^*, and BD=13I. Let Q be the diagonal ordinary
native line operator. It is unitary and Q^4=I. Put

```text
A = BQ,             T = BQ^2D,
K_minus = qD/13,     K_plus = QD T^-1,     q=Q^-1.
```

The independent spectral review proves that T is self-adjoint and that
its exact spectrum, across the complete address space at every positive
width, is

```text
{ -13,-11,-5,-3,-1,1,3,5,11,13 }.
```

All these values occur. T^-1 now has a literal one-bank implementation
with one C0, as reviewed in `inplace-service-review/REVIEW.md`. Its odd
grid, conditional scan cost, and physical view contract remain part of
every use below.

## A bounded complement to the query kernel

The identities

```text
A K_minus = I,       A K_plus = I
```

follow from BD=13I and T T^-1=I. Since AA^*=13I, K_minus=A^*/13 is
the minimum-norm right inverse. For each centre c, every solution of
Ay=c has the orthogonal decomposition

```text
y = K_minus c + z,       z in ker(A).
```

Thus its norm is at least ||c||/sqrt(13). The positive-line section
instead has

```text
K_plus^* K_plus = 13 T^-2.
```

Its exact singular values are

```text
sqrt(13), sqrt(13)/3, sqrt(13)/5, sqrt(13)/11, 1/sqrt(13).
```

Hence ||K_plus||=sqrt(13), its smallest singular value is 1/sqrt(13),
and its condition number is 13, independently of tensor width. The
right inverse can use the positive-line image im(QD), at a bounded
conditioning cost. This image is a direct complement to ker(BQ), not
an additional independent field bank.

The associated oblique projector is

```text
P_plus = K_plus A = QD T^-1 BQ.
```

It has P_plus^2=P_plus, image im(QD), and kernel ker(BQ). Its exact
norm is 13: multiplication by Q on either side does not change norm,
while D/sqrt(13) is an isometry and B/sqrt(13) is its adjoint. Thus
||D T^-1 B||=13||T^-1||=13. The canonical projector K_minus A is
orthogonal and has norm one.

## The two phase images

Let U_plus=QD/sqrt(13) and U_minus=qD/sqrt(13). They are isometries.
Their cross-Gram operator is

```text
U_minus^* U_plus = T/13.
```

Therefore the exact principal-angle cosines between their images are

```text
1/13, 3/13, 5/13, 11/13, 1.
```

The cross-Gram map is uniformly invertible. The two images are not a
direct-sum pair: cosine one occurs. The useful direct-sum statement is
the complement of ker(BQ) above. This distinction prevents an incorrect
claim that the positive- and inverse-line centre images are disjoint.

In contrast, the unsquared operator BQD is singular at every width at
least five. The frozen exact witness uses copy characters (1,2,3,6,6)
and centre vector (0,0,1,0,-1,1,0,1). Thus the unchanged image im(D)
contains no right inverse for BQ at those widths. The squared-line code
changes the admissible image rather than inverting that singular map.

## All coherent line-power sections

More generally, let A_m=BQ^m and require a section with image in
im(Q^nD). Such a section has the unique form Q^nD H, if it exists,
because D is injective. Its query response is

```text
A_m Q^nD H = S_(m+n) H,       S_k=BQ^kD.
```

The reviewed coherent-power classification gives the exact uniform
answer:

| m+n modulo four | Right inverse with this image |
| --- | --- |
| 0 | Q^nD/13 at every positive width |
| 2 | Q^nD T^-1 at every positive width |
| 1 or 3 | No such right inverse at any width at least five |

The negative statement holds even for a nonlinear choice of H. At the
singular mode, some centre outputs are outside the response range.
The positive statements provide the unique section in the stated image.
For residue zero its norm is 1/sqrt(13). For residue two its norm is
sqrt(13), with condition number 13. All stage routes preserve these
claims because they are unitary and commute with their own port lines.

## Construction boundary and evidence

The positive-line section is a concrete interface opportunity: its
centre correction T^-1 now needs one existing eight-field bank and one
owned C0. The Q^nD scatter still needs a legal source, physical target
frames, complete cost, and restoration. This note does not supply those
operations or a complete decoder. The Hilbert norm bounds do not
remove the native word's local guard, root scaling, or owner leases.

This note depends on these frozen packets:

- `schur-review/REVIEW.md`, SHA256
  `2402984a028bef456df8ca4a5e46dd45bbd3ed68611a558f77196f63b66996a5`.
- `schur-power-classification/CLASSIFICATION.md`, SHA256
  `9f06ddba79bb14cb88c3a19000d1ed1bb41a9fbbe8149d35b7e2854b4593feb6`.
- `inplace-service-review/REVIEW.md`, SHA256
  `d0315887769ec9bc12527a4bdb255b7804b0675b7638767a19062587b41e89cf`.

The algebra above is a consequence of those exact identities; it does
not use a new numerical search. OpenAI Codex assisted the work. No
supplier, native-child saving, or kappa claim is made. No PR, commit,
or push was made. Before a future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
