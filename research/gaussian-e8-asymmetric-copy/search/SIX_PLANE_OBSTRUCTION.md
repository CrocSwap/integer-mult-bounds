# A binary incidence obstruction for all full six-line planes

The sixty Gaussian E8 lines use the canonical ordering in `geometry/core.py`.
Let \(\mathcal P\) be the thirty full six-line rank-two flats.
Let

\[
U=\operatorname{span}_{\mathbb F_2}\{1_P:P\in\mathcal P\}\subseteq\mathbb F_2^{60}.
\]

The binary dimension of \(U\) is 25.

**Theorem.** Suppose every column of a binary matrix \(B\) belongs to \(U\).
If \(B_{ji}=0\) for every distinct nonorthogonal pair \((j,i)\), then \(B_{ii}=0\) for all \(i\).
The corresponding statement holds with rows in \(U\), by transposition.

Thus a decoder with reader indicators in \(U\) cannot fit any nonzero diagonal, even with unrestricted source supports.
The same conclusion holds when all source indicators belong to \(U\), with unrestricted readers.

## Finite incidence identities

For each line \(i\), the saved certificate gives a seven-element set \(W_i\).
Each index in \(W_i\) differs from \(i\) and is physically nonorthogonal to it.
For every plane \(P\in\mathcal P\),

\[
1_P(i)=\sum_{j\in W_i}1_P(j)\pmod2.
\tag{1}
\]

For example,

\[
W_0=\{1,3,6,13,16,22,23\}.
\]

These identities hold on every vector in \(U\), by linearity.
Apply identity (1) to column \(i\) of \(B\):

\[
B_{ii}=\sum_{j\in W_i}B_{ji}=0.
\]

This proves the theorem.

Each set \(S_i=\{i\}\cup W_i\) has a stronger verified property:
its eight lines are pairwise nonorthogonal, and it meets each plane in zero or two lines.
This gives a direct parity interpretation of (1).

Seven is the minimum possible witness size for every line.
The exact search excludes sizes one, three, and five before finding size seven.
Every incidence row has odd weight three, so even witness sizes cannot reconstruct it.
This minimum claim concerns the stated incidence identities, not arbitrary decoder complexity.

## Cost consequence with fitting controls

Consider any mixture of the following two types of totals:

1. Totals whose reader indicators belong to \(U\), with arbitrary source supports.
2. Totals that individually vanish at every forbidden off-diagonal entry.

Write their binary matrices as \(M\) and \(D\), respectively.
The complete fitting condition and the second type give zero forbidden entries in \(M\).
Every column of \(M\) lies in \(U\).
The theorem therefore gives \(\operatorname{diag}(M)=0\), so \(\operatorname{diag}(D)=\mathbf1\).

For a total of the second type, let \(I=A\cap R\).
The lines indexed by \(I\) are pairwise orthogonal.
The principal Gram submatrix on \(I\) is nonsingular, so

\[
\operatorname{rank}_{\mathbb Q(i)}G[R,A]\ge |I|.
\]

The diagonal supports of these controls cover all sixty indices, because their parity sum is \(\mathbf1\).
Consequently,

\[
C\ge\sum_{\text{controls}}\operatorname{rank}_{\mathbb Q(i)}G[R,A]
\ge\sum_{\text{controls}}|A\cap R|\ge60.
\]

Singleton totals attain equality.
The fifteen orthogonal-frame baseline totals also attain equality.
The theorem allows all forbidden-free rectangular controls, beyond these two examples.

## Complete full-plane rectangle audit

The bounded domain contains all 900 ordered pairs \((P,Q)\in\mathcal P^2\).
Their exact pairing-rank census is:

| Pairing rank | Ordered pairs |
|---:|---:|
| 0 | 30 |
| 1 | 360 |
| 2 | 510 |

The positive-cost rectangles give 870 columns on the 2,640 forbidden off-diagonal entries.
This binary matrix has rank 595 and kernel dimension 275.
Every saved kernel basis vector has zero diagonal image.
Thus the full rectangle audit agrees with the stronger incidence theorem.
The domain is complete; no optimizer timeout or numerical rank test enters this result.

## Reproduction and limits

Run these commands from the research directory:

```sh
python3 search/six_plane_certificate.py --verify search/six_plane_certificate.json
```

The verifier reconstructs the geometry and discovers the planes from exact pair closures.
It checks all sixty witnesses and rejects sixty deliberately altered identities.
It also checks all 900 rectangle costs and the full binary kernel certificate.

The result does not give an unrestricted lower bound.
It does not cover arbitrary partial plane supports, mixtures of the two orientation classes, or additional totals that produce forbidden entries.
This work gives no construction with cost below sixty.

The search used deterministic ordering and seed metadata 3476255234.
Its base commit is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
