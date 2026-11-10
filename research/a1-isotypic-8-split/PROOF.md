# The 8-dimensional isotypic summand is reducible under A_1

This is an exact proof over `Q` for one invariant subspace of the historical
`c=1` doubled centre block. It is not a new minimal polynomial of the full
one-slot operator, not a census of the signed-permutation normalizer, and not
a multiplication bound.

## Operator and the joint space

The input is the 8-by-112 query in `INTERFACE.json`, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
On `Q^8 ⊗ Q[F_2^9]`,

```text
A_1 = (1/4) sum_q r_q r_q^T ⊗ P_q(1),
B   = 4 A_1.
```

`P_q(1)` sends `e_a` to `e_{a+q}` when the least bit of `q` is 1, and to
`(-1)^{q·a} e_a` otherwise. A signed permutation acts by
`(S v)_k = eps[k] v[inv[k]]` and by the induced orthogonal label map.

PR #6944 supplies the commuting involutions `g` and `t` that fix sector 1.
The sign stabilizer `H` of sector 1, with positive sign on coordinate 0, has
order 16. Its trivial character has dimension 864. The joint `(+1,+1)`
eigenspace `E` of `g` and `t` inside that character has dimension 216 by the
trace formula

```text
(tr_V I + tr_V g + tr_V t + tr_V(gt)) / 4 = 216.
```

The same dimension is the number of components in the least-representative
solution of the corresponding sign equations. That ordered basis is identical
to the basis pinned by the merged characteristic-polynomial package
`research/a1-joint-216-charpoly/`. This note uses the basis. It does not
recompute the degree-216 characteristic polynomial.

## The dihedral character

The open question in PR #7008 names two signed permutations inside the
`c=1` stabilizer:

| name | `inv` | output signs |
|---|---|---|
| `u` | `(0, 1, 2, 3, 7, 6, 5, 4)` | all plus |
| `r` | `(0, 1, 6, 7, 3, 2, 5, 4)` | minus on coordinates 0 and 7 |

Both preserve the root lines and sector 1. They satisfy `u^2 = 1`, `r^6 = 1`,
`r`, `r^2` and `r^3` are not the identity, and `u r u^{-1} = r^{-1}`. The
twelve words `r^k` and `r^k u` are distinct operators, so they present a
dihedral group `G` of order 12. Each word preserves `E`, because its action
on every canonical basis vector lands in `E`.

Let `ψ` be the linear character

```text
ψ(r^k) = (-1)^k,    ψ(r^k u) = (-1)^{k+1}.
```

The standard isotypic projector is

```text
P = (1/12) sum_{g in G} ψ(g^{-1}) ρ(g)
  = (1/12) sum_{k=0}^{5} (-1)^k (ρ(r^k) - ρ(r^k u)).
```

The reflections are involutions and `ψ(r^{-k}) = ψ(r^k)`, so the inverse in
the character does not change the coefficients. On the explicit basis of `E`,
`12P` satisfies `(12P)^2 = 12 · (12P)`, its trace is 96, and its image has
rank 8. A projector whose trace equals its rank has image equal to that
trace, so

```text
W = im P
```

is 8-dimensional. The same traces give character multiplicity 8, in agreement
with the rank. On `W`, both `r` and `u` act by `-I`, which is the character
`ψ`. The opposite linear character, with `ψ(u) = +1`, has projector trace 960
and image rank 80, so the sign of `u` distinguishes the two linear summands.

Each of those signed permutations fixes sector 1. Direct comparison of the
two operator orders on all 4096 ambient basis vectors shows that `B` commutes
with every element of `H`, with `g`, with `t`, and with all twelve dihedral
words. Therefore `B` commutes with `P` and preserves `W`.

## Explicit basis

Index the canonical basis of `E` by `e_0, ..., e_215`. The following eight
vectors are fixed by `12P` and have disjoint supports, so they are a basis of
`W`:

| vector | combination | representative roots |
|---|---|---|
| `w0` | `e_104 - e_120 + e_142` | 528, 576, 694 |
| `w1` | `e_105 - e_121 + e_143` | 529, 577, 695 |
| `w2` | `e_106 - e_122 + e_140` | 534, 582, 688 |
| `w3` | `e_107 - e_123 + e_141` | 535, 583, 689 |
| `w4` | `e_116 - e_124 + e_134` | 570, 618, 668 |
| `w5` | `e_117 - e_125 + e_135` | 571, 619, 669 |
| `w6` | `e_118 - e_126 + e_132` | 572, 620, 666 |
| `w7` | `e_119 - e_127 + e_133` | 573, 621, 667 |

Each `e_j` is the signed orbit vector of support 16 pinned in the published
basis, and the representative root is its least ambient index. In this basis
the matrix of `B` is

```text
[  8  -4   0  -4   0   0   0   0 ]
[ -4   8  -4   0   0   0   0   0 ]
[  0  -4  -8  -4   0   0   0   0 ]
[ -4   0  -4  -8   0   0   0   0 ]
[  0   0   0   0   0  -4   0  -4 ]
[  0   0   0   0  -4   0  -4   0 ]
[  0   0   0   0   0  -4   0  -4 ]
[  0   0   0   0  -4   0  -4   0 ]
```

The two actions of `B`, by the 112 ports and by the precomputed columns,
agree on every ambient realization of `w_i`. The matrix of `A_1` is this
matrix divided by 4. Every entry of the matrix of `B` is divisible by 4, so
the matrix of `A_1` is an integer matrix.

## Invariant decomposition

The matrix is block diagonal, with two 4-by-4 blocks. Each block contributes
proper invariant subspaces. Write vectors as coordinates in `(w_0, ..., w_7)`.
The following six subspaces are `A_1`-invariant, pairwise independent, and
span `W`:

| summand | basis | annihilator of `A_1` |
|---|---|---|
| `U+` | `w0+w1`, `w2+w3` | `x^2 + 2x - 4` |
| `U-` | `-w0+w1`, `-w2+w3` | `x^2 - 2x - 4` |
| `Z1` | `w4-w6` | `x` |
| `Z2` | `w5-w7` | `x` |
| `L+` | `w4-w5+w6-w7` | `x-2` |
| `L-` | `w4+w5+w6+w7` | `x+2` |

The annihilators are checked as integer identities in `B = 4 A_1`:
`B^2 + 8B - 64 I` kills `U+`, `B^2 - 8B - 64 I` kills `U-`, `B` kills `Z1` and
`Z2`, `B - 8I` kills `L+`, and `B + 8I` kills `L-`. The characteristic
polynomial on `W` is therefore

```text
chi_{A_1,W}(x) = x^2 (x-2) (x+2) (x^2 - 2x - 4) (x^2 + 2x - 4).
```

Equivalently, ascending coefficients of `chi_B` and `chi_{A_1,W}` are

```text
chi_B     (0, 0, -262144, 0, 16384, 0, -256, 0, 1)
chi_{A_1} (0, 0, -64, 0, 64, 0, -16, 0, 1)
```

and `chi_{A_1,W}(x) = 4^{-8} chi_B(4x)`. Both quadratics are irreducible over
`Q`: each has degree 2 and no rational root among the candidates `±1, ±2, ±4`.
Their discriminants equal 20, which is not a square. A 2-dimensional module
annihilated by an irreducible quadratic is irreducible. The lines are
1-dimensional, hence irreducible. On `span{w4-w6, w5-w7}` the operator `A_1`
is zero, so every line of that plane is invariant.

Thus, as a `Q[A_1]`-module,

```text
W ≅ Q[x]/(x^2+2x-4) ⊕ Q[x]/(x^2-2x-4)
    ⊕ Q[x]/(x) ⊕ Q[x]/(x) ⊕ Q[x]/(x-2) ⊕ Q[x]/(x+2).
```

In particular `W` has proper nonzero `A_1`-invariant subspaces. One explicit
example is the line `Z1 = span{w4 - w6}`, on which `A_1` acts by 0.

The nullity of `B` on `W` is 2, equal to the algebraic multiplicity of
eigenvalue 0. That count is internal to `W`.

## Evidence class

This is a proof by exact finite linear algebra over `Q`. The joint space is
the full solution of a finite sign system, and its dimension matches the trace
formula. The projector identity is checked on every vector of a basis of that
space, and the image rank equals the character multiplicity, so the eight
vectors are a basis of the whole isotypic component rather than of a
subspace found by sampling. The matrix entries and the six annihilators are
integer identities. No enumeration was stopped early, and no floating-point
approximation was used.

It is not an exhaustive census of the `c=1` stabilizer or of the normalizer
of `{g,t}`. Those counts belong to PR #7008. It is not a heuristic search.

## Corollary from the published degree-216 factorization

The merged package `research/a1-joint-216-charpoly/` factors the
characteristic polynomial of `A_1` on all of `E`. In that factorization the
quadratics `x^2 - 2x - 4` and `x^2 + 2x - 4` each occur once. Each already
occurs once on `W`, on a 2-dimensional subspace. Therefore, if that published
factorization is used, `U+` and `U-` are the full primary components of those
factors inside `E`. This note does not recompute the degree-216 polynomial.

## What this does not say

The argument uses only the subgroup generated by the recorded elements `r` and
`u`. It does not say whether a signed permutation outside that subgroup
preserves `W` and acts non-scalarly. That is the other open question of
PR #7008.

The multiplicity-80 and 128-dimensional isotypic components of the same
dihedral action are not given matrices or characteristic polynomials. The
unique 32-dimensional `c=1` sign character, and its four joint spaces of
dimension 8, are a different subspace. Nothing here computes their
characteristic polynomials.

Algebraic multiplicity 24 for eigenvalue 0 on `E` remains the published count.
The geometric multiplicity of that eigenvalue on the 216-by-216 matrix is not
computed. The calculation above gives geometric multiplicity 2 on `W` only.

The degree-881 one-slot annihilator is untouched. The selected conditional
kappa stays `781451/250000000`.
