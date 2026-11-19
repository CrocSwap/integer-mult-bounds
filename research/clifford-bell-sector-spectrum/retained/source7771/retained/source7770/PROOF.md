# The full width-twelve nullity

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Use the full four-qubit Gaussian-dyadic Clifford group G, its natural
16-dimensional representation V, its Pauli subgroup P and scalar
kernel Z of order four. These are the exact conventions in
[PR #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766).
Put S=G/P=Sp(8,2), E=P/Z and N=|G/Z|=12,128,668,876,800.

For the normalized projective Gram matrix at tensor width twelve,

```text
nullity H12 = 10,677,394,
rank H12 = 12,128,658,199,406.
```

The only absent irreducible modules are the inflated S rows 9 and 22,
of degrees 595 and 3213. Every module with a nontrivial Pauli character
occurs. This makes the source lower bound exact. The threshold T(4)=13
is unchanged. No physical supplier or new kappa follows.

## 1. The width-eleven source and the two Pauli orbits

The [pinned source proof, Section 7](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md)
gives honest quotient modules W11 and W13 with

```text
V^(tensor 11) = conjugate(V) tensor W11,
V^(tensor 12) = End(V) tensor W11.
```

It computes every W11 multiplicity from the ordinary S character
table. Exactly rows 9 and 22 are absent. Their degrees are 595 and
3213. All 79 other rows have positive multiplicity. We retain and
replay that computation unchanged.

For v in E, let D_v be the Hermitian Pauli matrix. Its line in End(V)
has P character

```text
lambda_v(D_a) = (-1)^(omega(a,v)),
```

where omega is the nondegenerate binary symplectic form. The 256 lines
are distinct and span End(V). G permutes their labels by the ordinary
linear S action. There are two label orbits: {0} and the 255 nonzero
vectors. This is a linear action, not the affine quadratic-form action
that occurs in the central-character-minus-one sector.

Fix v!=0. Let H be its stabilizer in S and T its preimage in G.
Conjugation by T preserves the actual line C D_v. Its scalar action
eta_v is therefore a one-dimensional character of T that extends
lambda_v. It can have a negative sign; it must not be replaced by a
trivial extension. Since W11 is trivial on P, the lambda_v weight
space of the width-twelve module is

```text
eta_v tensor Res_H(W11).                         (1)
```

For each irreducible H module rho, the module

```text
Ind_T^G(eta_v tensor rho)                        (2)
```

is irreducible. To see this, decompose it into its distinct P weight
spaces. A G-invariant subspace restricts on one weight to a
T-invariant subspace of eta_v tensor rho, hence to zero or the whole
space. Transitivity then gives zero or the whole induced module.
Conversely, any irreducible G module on this nonzero P orbit has this
form: take one weight space and divide its T action by eta_v. The
result factors through H, is irreducible, and induction recovers the
original module. Their squared dimensions sum to 255^2 |H|=255|S|.
Together with the quotient sector of size |S|, this accounts for all
256|S| dimensions of the central-character-one regular algebra.
Thus (1) contains all modules in (2) precisely when
Res_H(W11) contains every irreducible H module. This argument does
not assume that G/Z splits over S.

## 2. A restriction test using classes outside all conjugates of H

Let S be any finite group, H a subgroup and W a complex S module.
Suppose that its only absent irreducibles are chi_1,...,chi_r.
Choose classes C_j that meet no conjugate of H. If the matrix

```text
M_(j,i) = chi_i(C_j)
```

has column rank r, then Res_H(W) contains every irreducible H module.

Indeed, if rho were absent, Frobenius reciprocity would make every
constituent of Ind_H^S(rho) absent from W. Its character would be
sum_i a_i chi_i, with nonnegative integer a_i. An induced character
vanishes on every chosen class, because no conjugate of that class
lies in H. Thus M a=0. Full column rank forces a=0, contrary to
Ind_H^S(rho) having positive dimension. This is a direct application
of induction and reciprocity, not a claim of new general character
theory.

For a nonzero-vector stabilizer in S, the required classes are exactly
those that fix no nonzero vector in E. A class meets some conjugate
of H if and only if it fixes such a vector.

## 3. Two authenticated class columns settle the restriction

Use the ordinary S8(2) table in CTblLib 1.3.11, in its published row
and column order. The source identifies the action on all 256 vectors
with character 2+chi_5+chi_6; the two degrees are 119 and 135.
The following exact entries come from the authenticated table member.

| Class column | Centralizer order | chi_5 | chi_6 | Fixed vectors, including zero | chi_9 | chi_22 |
| --- | --- | --- | --- | --- | --- | --- |
| 9 | 77,760 | -1 | 0 | 1 | 10 | 0 |
| 25 | 300 | -1 | 0 | 1 | 0 | 3 |

The new checker reads all four rational rows across all 81 classes.
It verifies these two columns, all ordinary inner products and all
nine fixed-dimension bins against the retained source projection.
The two classes are outside every conjugate of H. On the two missing
rows they give diag(10,3), with determinant 30. Section 2 therefore
proves that Res_H(W11) contains every irreducible H module. Equation
(1) and the classification in Section 1 prove that every nonzero
Pauli-character sector occurs at width twelve.

For v=0, the Pauli line is the scalar identity and eta_0 is trivial.
The entire P-invariant part of End(V) tensor W11 is W11. Hence the
only missing G modules are exactly the inflated rows 9 and 22.

## 4. Exact nullity and a nullspace projector

At width twelve, Z acts trivially. The projective Gram matrix is the
central convolution matrix of the character of the tensor power,
up to its positive normalization. For an irreducible module of degree
e, its regular block has dimension e^2 and has a positive Gram
eigenvalue exactly when that module occurs. Thus

```text
nullity H12 = 595^2 + 3213^2 = 10,677,394,
rank H12 = N - 10,677,394 = 12,128,658,199,406.
```

There is also an exact implicit orthogonal projector onto the entire
nullspace. For projective group representatives g_a,g_b, let
s_a,s_b be their images in S. Put

```text
Q_(a,b) = [595 chi_9(s_a^(-1)s_b)
           + 3213 chi_22(s_a^(-1)s_b)] / N.
```

Both characters are real. Character orthogonality gives Q^2=Q and
Q*=Q; its trace is 10,677,394. Both modules are absent, so H12 Q=0.
The exact nullity above shows that this is the complete nullspace
projector. The formula does not require a chosen phase for g_a.
No N-by-N matrix or full group enumeration was materialized.

## Evidence and limits

The CTblLib release archive and table member pass their retained
SHA-256 pins. The optional archive replay reconstructs all four new
rows and all 81 columns, and reruns the original 81-row projection.
The published character table is a mathematical input. These checks
do not reconstruct it from group multiplication.

Literal checks use all 65,536 Pauli character pairs and all 1,048,576
nonzero matrix entries in those conjugations. For all twenty legal
Clifford generators, they compute 5,120 adjoint images, their actual
signs, linear label maps and symplectic action. A separate orbit walk
has sizes 1 and 255. The nonzero stabilizer order is 185,794,560.
The Gaussian Hadamard prefactor cancels with its conjugate; the
quadratic-sector prefactor would give the wrong calculation here.

Changed character values fail full row orthogonality. The identity
class fails the no-nonzero-fixed-vector condition. Repeated witness
columns fail the rank test. A literal Pauli with negative action on
the selected line rejects the trivial-extension substitution.

The general induction argument is written mathematics. Finite gate
checks support the exact conventions; they do not replace the proof.
Full width-ten nullity, sharp conditioning, native realization and
complete caller pricing remain open. The source threshold T(4)=13,
all five framework assumptions and the selected frontier remain
unchanged. No selected cold replay, full three-qubit suite, Lean,
Docker, independent human acceptance or formal proof kernel was used.
No global literature priority is claimed.
