# Planar asymmetric decoders cannot save copy cost

## Statement

Let \(K\) be a subfield of \(\mathbb C\) closed under complex conjugation.
Let \(v_1,\ldots,v_n\) represent distinct nonzero projective lines in a positive-definite Hermitian space over \(K\).
Write \(G_{ab}=\langle v_a,v_b\rangle\).

A binary decoder is a finite family of pairs \((A_j,R_j)\) of sets of line indices.
Its fitting matrix is

\[
B=\sum_j 1_{A_j}1_{R_j}^{T}\quad\text{over }\mathbb F_2.
\]

It satisfies \(B_{aa}=1\) and \(B_{ab}=0\) whenever \(a\ne b\) and \(G_{ab}\ne0\).
Its cost is

\[
C=\sum_j \operatorname{rank}_K G[A_j,R_j].
\]

**Theorem.** Suppose each joint support is planar:

\[
\dim_K\operatorname{span}\{v_a:a\in A_j\cup R_j\}\le2.
\]

Then \(C\ge n\). Singleton totals attain equality.

This theorem permits asymmetric supports, any number of totals, and arbitrary cancellation over \(\mathbb F_2\).
It does not require a bound on the number of roots in each plane.

## A plane with a partial diagonal

Fix a physical plane \(P\), and consider any collection of totals whose supports lie in \(P\).
Suppose their binary sum \(M\) vanishes on all distinct nonorthogonal pairs in \(P\).
Let \(d\) count the ones on the diagonal of \(M\).
We prove that this collection has cost at least \(d\).

Each line in \(P\) has exactly one orthogonal projective line in \(P\).
The represented orthogonality graph is therefore a matching, with possible isolated vertices.
Consequently, \(M\) is block diagonal after a permutation, with blocks of size at most two.
This assertion applies to asymmetric \(M\).

A term of physical rank zero contributes only to orthogonal pairs.
It has no diagonal contribution, since the Hermitian form is positive definite.
Discard these terms; the required zeros and the diagonal remain unchanged.

Let \(k\) count the remaining terms of physical rank one and \(\ell\) those of physical rank two.
A term has physical rank two if both of its supports span \(P\).
Indeed, a basis change identifies their pairing matrix with the nonsingular Hermitian form on \(P\).
Thus every physical-rank-one term has a support that spans a single line on at least one side.
Distinct projective lines imply that this support contains exactly one index.

For each rank-one term, select such an index.
Delete all selected indices from both the rows and columns of \(M\).
This step deletes at most \(k\) indices and removes every rank-one term.
The remaining matrix \(M'\) is the sum of at most \(\ell\) binary outer products.
Hence

\[
\operatorname{rank}_{\mathbb F_2}M'\le\ell.
\]

At least \(d-k\) diagonal ones remain.
Every matching block with a diagonal one has rank at least one.
A matching block contains at most two diagonal entries, so

\[
d-k\le2\operatorname{rank}_{\mathbb F_2}M'\le2\ell.
\]

The physical cost is \(k+2\ell\ge d\), as required.

## Decomposition by physical plane

Discard empty totals.
Group every total with joint span of dimension two by that exact physical plane.
Group a total with joint span of dimension one by its unique projective line.

Fix distinct nonorthogonal lines \(v_a,v_b\).
Any total contributing to matrix entry \((a,b)\) has joint span containing both lines.
Under the planar assumption, this span must equal the unique plane \(\operatorname{span}_K(v_a,v_b)\).
Therefore, only one plane group can contribute to this constrained entry.
The global fitting condition forces that group's entry to vanish.

Each plane group's matrix thus satisfies the preceding partial-diagonal lemma.
Its cost is at least its number of diagonal ones.
Each one-dimensional group has the same property: it consists of singleton totals of cost one.

At every line index, the global diagonal is the parity sum of the group diagonals and equals one.
At least one group diagonal must therefore be one at that index.
Summing the group bounds gives \(C\ge n\).

## Gaussian E8 consequence and exact scope

The sixty Gaussian E8 lines are distinct lines in a positive-definite four-dimensional \(\mathbb Q(i)\)-space.
Every planar asymmetric decoder therefore costs at least sixty.
The sixty singleton totals attain sixty, so the restricted optimum is exactly sixty.

Every symmetric decoder with physical rank at most two per total is planar.
The theorem therefore rules out any saving from this whole symmetric class.
It also rules out local replacements within rank-two flats, even with asymmetric supports and additional totals.

The theorem does **not** cover all totals with pairing rank at most two.
In the canonical ordering of `geometry/core.py`, take

\[
A=\{0,1\},\qquad R=\{0,3\}.
\]

Their doubled real-coordinate representatives are

\[
\begin{aligned}
v_0&=(-2,-2,0,0,0,0,0,0),\\
v_1&=(-2,0,-2,0,0,0,0,0),\\
v_3&=(-2,0,0,0,-2,0,0,0).
\end{aligned}
\]

The joint span has Gaussian dimension three, while

\[
G[A,R]=\begin{pmatrix}8&4-4i\\4+4i&4\end{pmatrix}
\]

has rank one. All four entries are nonzero.
This example marks a genuine gap between low pairing rank and planar joint support.
A cheaper unrestricted Gaussian decoder remains open.

## Extension: allow arbitrary singleton-sided totals

The same lower bound holds if every total is planar or has a singleton support on at least one side.
A singleton-sided total can have joint span greater than two.

Discard every zero-cost total; it affects neither the diagonal nor a constrained nonorthogonal entry.
Let \(k\) count the nonplanar singleton-sided totals.
Each has cost one.
Select its singleton index and delete all selected indices from both rows and columns.
This step deletes at most \(k\) indices and removes every nonplanar total.

The remaining totals form a planar fitting decoder on at least \(n-k\) surviving lines.
Restriction cannot increase a pairing rank.
The planar theorem therefore bounds the original cost of those remaining totals below by \(n-k\).
Including the deleted singleton-sided totals gives \(C\ge k+(n-k)=n\).

Consequently, a saving requires a total with at least two dimensions on each side.
Its joint support must span at least three dimensions.
The Gaussian rank-one example above satisfies all three conditions.

## Quantitative extension: remove nonplanar totals by their smaller support

Discard zero-cost totals first.
For each remaining nonplanar total, write

\[
\beta_j=\operatorname{rank}_K G[A_j,R_j],\qquad
m_j=\min(|A_j|,|R_j|),\qquad
\delta_j=m_j-\beta_j\ge0.
\]

Choose a smaller support of each such total, and let \(D\) be the union of the chosen indices.
Delete \(D\) from both rows and columns of the fitting matrix.
Every nonplanar total disappears.
The surviving planar totals decode the remaining \(n-|D|\) lines.
By the planar theorem and rank monotonicity, their original cost is at least \(n-|D|\).
Thus

\[
C\ge n-|D|+\sum_{j\text{ nonplanar}}\beta_j
\ge n-\sum_{j\text{ nonplanar}}\delta_j.
\]

Equivalently,

\[
\boxed{\quad n-C\le\sum_{j\text{ nonplanar}}
\left(\min(|A_j|,|R_j|)-\operatorname{rank}_K G[A_j,R_j]\right).\quad}
\]

The sharper first inequality applies to any choice of smaller supports, including choices that overlap.
It remains valid if \(D\) contains every line.

In particular, \(C\ge n\) when each nonplanar total satisfies
\(\beta_j=\min(|A_j|,|R_j|)\).
This includes all singleton-sided totals and every symmetric total whose support is an orthogonal frame.
For Gaussian E8, a decoder that mixes the sixty-cost orthogonal-frame construction with arbitrary planar replacements therefore still costs at least sixty.

Any cheaper decoder needs a nonplanar total with a strict deficit
\(\beta_j<\min(|A_j|,|R_j|)\).
A saving of \(s\) requires the sum of these nonplanar deficits to be at least \(s\).
This is a necessary condition, not a sufficient construction.
