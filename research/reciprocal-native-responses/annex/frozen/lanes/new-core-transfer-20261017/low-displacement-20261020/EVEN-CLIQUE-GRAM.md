# Cross-Gram obstruction for the rank-sixteen response

The current rank-sixteen response admits a complete native data word.
This note tests a different obligation: inversion of the cross-Gram
matrix used by the proposed centre section-swap code.

Let E-I=UV be the exact factorization in the frozen rank-sixteen
payload. The matrices U and V have sizes 112 by 16 and 16 by 112.
Both have rank 16. Let Q be the diagonal matrix of the physical line
operators. Then Q_p squared is translation by the actual binary
direction q_p. The cross-Gram matrix is

```text
T = V Q^2 U.
```

On the character indexed by w in F2^9, it is the rational matrix

```text
T(w) = V diag((-1)^(q_p dot w)) U.
```

The exact ranks of these 512 matrices are:

| Rank | Number of characters |
| --- | ---: |
| 0 | 32 |
| 4 | 96 |
| 8 | 12 |
| 14 | 256 |
| 16 | 116 |

Thus T is not an invertible operator on the full spatial field.
This rules out a section-swap construction that requires T inverse
for this response and this complete spatial domain. It does not
rule out the response, its retained-grid inverse, or a different
terminal construction.

## The eight small clique coordinates

For each of the eight disjoint small cliques C_j, the query row is
the indicator of C_j. The scatter column is its negative. No other
query or scatter uses these ports. Therefore these eight coordinates
are separate one-dimensional blocks of T(w), with entries

```text
t_j(w) = -sum_{p in C_j} (-1)^(q_p dot w).
```

Each actual clique contains eight orthonormal directions. They are
linearly independent. The map from w to its eight dot products is
therefore onto F2^8, with two preimages for each output. A zero sum
requires four negative signs. It occurs on

```text
2 * binomial(8,4) = 140
```

of the 512 characters for each clique. This argument applies to any
orthonormal eight-clique in this nine-axis space.

In the actual partition, all eight zero sets are equal. The checker
tests this additional source-specific fact on all 512 characters.
Its complete zero-mask distribution is 372 copies of mask 0 and
140 copies of mask 255. On those 140 characters, the full cross-Gram
has rank 0, 4, or 8, with counts 32, 96, and 12.

Each clique sums to z=45. This vector is isotropic, and every clique
direction has dot product one with z. On a zero character,
the product of the eight signs is positive. Thus every small-block
zero is in the positive-z sector. In the negative-z sector all
eight small blocks are nonzero, but the full cross-Gram has rank 14
on all 256 characters. The exact checker evaluates the large block
as well; it does not infer this latter rank from the small blocks.

For example, w=2 gives signs

```text
(-1,-1,+1,+1,+1,+1,-1,-1)
```

on the first clique, whose ports are
`[1,5,19,54,64,73,82,83]`. Its cross-Gram entry is zero.

## Changing the factor basis does not remove the obstruction

Let E-I=U'V' be another factorization through 16 scalar coordinates,
with both factors of full rank. The image of U and the image of U'
are both the image of E-I. There is an invertible 16 by 16 matrix M
with U'=UM. Since U is injective, V'=M inverse V. Consequently,

```text
V' Q^2 U' = M^-1 (V Q^2 U) M.
```

The ranks in the table do not depend on the choice of minimal
scalar factors.

More coordinates do not make this particular cross-Gram invertible.
If E-I=AB factors through r coordinates and B Q^2 A is invertible,
then A is injective and B is onto. Hence rank(AB)=r. Since E-I has
rank 16, necessarily r=16. An extension that changes the encoded
operation or adds a separate data response is outside this argument.

## Exact evidence and scope

The source is `odd16-normal-v2/EXTENSION-PROGRAM.json.gz`, with
decompressed SHA256
`d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4`.
`EXTENSIONS-FREEZE.json` pins the native producer. The separate
extension matrix review checks E-I=UV and the complete inverse.

`check_even_clique_gram.py` checks the source hash, both factor ranks,
the actual clique cover, all orthogonality and support claims, all
512 zero masks, and all 512 complete rational matrix ranks. It uses
exact fractions and explicit checks that remain active under
optimized Python. The two final receipts are
`gram-v2-normal.json` and `gram-v2-optimized.json`; they are
byte-identical. The earlier two receipts are retained as draft
small-block checks.

This note supplies no centre formation or capture operation. The
native words have 112 productive fields in each data bank and 416
unchanged auxiliary fields. They do not expose a separate 16-field
or 30-field productive centre cohort.

The response uses the root's low-displacement proposal, the actual
clique partition in the native extension, and the proposed section
code from the root and coherent-port lane. AI assistance was used.
No complete supplier bound or publication claim is made.
