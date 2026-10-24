# Rank-8 factors of the E8 root Gram cost 9 per term

Real coefficients. No new κ. The finite facts cited as **(Bk)** or **(Ck)** are
checked by `verify.py`. One standard theorem is cited rather than recomputed.

## 1. Model

Let the 120 lines of the E8 root system have representatives \(r_i\) of norm 2,
and let \(G_{ij}=\langle r_i,r_j\rangle\). The label pairing is
\[
S(i,j)=(\langle r_i,r_j\rangle+1)\bmod 2.
\]
Its \(120\times 120\) matrix has F2-rank 9 and distinct rows **(A.pairing-rank)**,
so the labels span a 9-dimensional space on which \(S\) is nondegenerate. For
line sets \(X,Y\), the copy cost \(\rho(X,Y)\) is the F2-rank of \(S\) between
them. If \(V_X\) and \(V_Y\) are their label spans, nondegeneracy gives
\[
\rho(X,Y)=\dim V_X-\dim(V_X\cap V_Y^\perp),
\]
and in particular \(\rho=9\) whenever both spans are the whole label space.
The complement of any proper violator spans exactly 8 dimensions
**(B.kernel-sizes)**. Nonzero violators have sizes 56, 64 or 120
**(B.violator-sizes)**.

A real factorization \(\sum_{k=1}^{t} a_k b_k^{\mathsf T}=2I_8\) is called
**root-linear**, or of factor rank \((8,8)\), when every factor is one of these
normals in \(\mathbb R^8\). Equivalently, the \(120\times t\) matrices with
columns \((\langle r_i,a_k\rangle)_i\) and \((\langle r_i,b_k\rangle)_i\) both
have rank 8. The support of \(a_k\) is
\(C(a_k)=\{i:\langle r_i,a_k\rangle\neq 0\}\). Zero factors are deleted; a
nonzero term has both normals nonzero. The live roots span \(\mathbb R^8\)
**(A.root-span)**.

This is the root-span branch of the term-count gap in
`docs/research/complex-decoder-scope-map.md`. It is not a binary factorization
of the pairing matrix, and it does not allow a factor column to leave the
8-dimensional root span.

## 2. Hyperplane census

The eight doubled vectors in `verify.py` are a base of simple roots: their
Gram matrix is a Cartan matrix of determinant 1 with nonpositive off-diagonal
entries **(A.cartan-det)**, and every root is an integer combination of them
**(A.roots-in-lattice)**. Their \(\mathbb Z\)-span \(L\) is therefore the E8
root lattice and is unimodular.

**Lemma 1 (normal length).** Let \(H\) be a hyperplane spanned by roots, and
let \(n\in L\) be a primitive normal. Then \(|n|^2\le 128\).

*Proof.* Seven linearly independent roots in \(H\) have Gram determinant at
most \(2^7=128\) by Hadamard's inequality. Their \(\mathbb Z\)-span sits in
\(H\cap L\) at index \(m\ge 1\), so that determinant equals \(m^2|n|^2\). For
the covolume claim: unimodularity and primitivity give a vector \(v\) with
\(\langle v,n\rangle=1\), hence \(L=(H\cap L)\oplus\mathbb Z v\), and the unit
covolume of \(L\) forces the covolume of \(H\cap L\) to equal \(|n|\). ∎

**Cited theorem (W).** Every vector of an irreducible crystallographic root
lattice is conjugate under the Weyl group to exactly one dominant weight: the
closed fundamental chamber is a fundamental domain. Bourbaki, *Lie Groups and
Lie Algebras*, Chapter VI, §1. The pairing and the orthogonal-line count are
Weyl-invariant, so every lattice normal has the same flat profile as its
dominant representative.

`verify.py` enumerates all 383 dominant vectors of norm at most 128
**(B.dominant-count)**. Their orthogonal-line counts are at most 42, or exactly
63, or 120 for the origin. The 63-line vectors are the eight positive multiples
of one root **(B.root-direction, B.root-flat-profile)**. Every orthogonal set
that spans seven dimensions has one of the eight sizes
\[
14,16,22,23,28,37,42,63
\]
**(B.hyperplane-sizes)**. The 63-line flat has violator profile \((1,24,25)\)
and its complement has label span 9. Every other seven-dimensional flat has
smallest violator at least 14, paired violator at least 25, and complement span
9 **(B.nonroot-flat-profile)**. The same root profile holds for all 120 roots,
and the unique one-line violator is the root line itself **(B.every-root)**.

**Lemma 2 (every real normal).** For every nonzero \(a\in\mathbb R^8\), the
complement \(C(a)\) has label span 9. If \(a\) is not parallel to a root, every
violator meets \(C(a)\) in at least 14 lines. A pair of violators meets \(C(a)\)
in at least 25 lines. If \(a\) is parallel to a root \(\alpha\), the only
violator of size less than 24 is \(\{\alpha\}\).

*Proof.* Let \(U\) be the span of the roots orthogonal to \(a\). Those roots
lie in a root-spanned hyperplane: while their span has dimension less than 7,
some root lies outside it because the roots span \(\mathbb R^8\), and adjoining
roots reaches dimension 7. A root-spanned hyperplane has a primitive lattice
normal of norm at most 128 by Lemma 1, so Lemma W and the census give its
profile.

If \(\dim U=7\), then \(a\) is parallel to that normal. The census gives the
stated violator bounds, and span 9 follows because every violator meets
\(C(a)\). If \(\dim U\le 6\), at least two extra roots can be omitted from an
extension to a root basis of \(\mathbb R^8\), giving two distinct hyperplanes
\(H_1,H_2\) that contain \(U\). Their complements sit inside \(C(a)\). Suppose
some functional met \(C(a)\) in at most 13 lines. Each hyperplane would then
have a violator of size at most 13, so each would be a root flat and the
functional would be that root's self-line functional. Distinct root lines have
distinct functionals **(A.pairing-rank)**, so the two hyperplanes cannot share
that functional. This contradiction gives the bound 14. One hyperplane already
has paired-violator size at least 25, and the same inclusion raises the bound
to \(C(a)\). ∎

Over \(\mathbb F_2\), any two distinct nonzero functionals are linearly
independent, so the paired minimum in the census is the codimension-2 count.

## 3. Rank-(8, 8) bill

**Theorem 3.** Let \(\sum_k a_k b_k^{\mathsf T}=2I_8\) with real vectors
\(a_k,b_k\). After deleting terms with a zero factor, \(t\) nonzero terms
remain, \(t\ge 8\), and the copy cost on all 120 lines is exactly \(9t\).
In particular the cost is at least 72, and at least 81 when \(t\ge 9\).

*Proof.* The identity has rank 8, and each nonzero outer product has rank 1,
so \(t\ge 8\). For nonzero \(a_k\) and \(b_k\), Lemma 2 says both supports
span the label space. Nondegeneracy makes the pairing rank exactly 9. The
coordinate frame attains \(t=8\) and cost 72 **(C.frame-cost)**. Replacing
one frame term \(f_0 f_0^{\mathsf T}\) by
\((e_0+e_1)e_0^{\mathsf T}+(e_0-e_1)e_0^{\mathsf T}\) and keeping
\(2e_i e_i^{\mathsf T}\) for \(i\ge 1\) gives nine terms, still of factor rank
8, and cost 81 **(C.split-identity, C.split-cost)**. Seven frame terms do not
factor \(2I\) **(C.seven-terms)**. ∎

**Theorem 4.** Under the same identity, charge only the lines outside a deleted
set \(P\) of size \(p\le 13\). The live copy cost is at least \(9t-p\). Thus
on any 8-line puncture, nine nonzero terms cost at least 73.

*Proof.* A live support \(C(a)\setminus P\) fails to span the label space only
if some violator is covered by \(P\). By Lemma 2, \(p\le 13\) cannot do that
unless \(a\) is parallel to a root \(\alpha\in P\), in which case exactly one
functional dies. A second functional would be a violator pair of size at most
13, but every pair has size at least 25. The surviving lines therefore span
the whole hyperplane kernel of the self-line functional, not a smaller
subspace.

A term therefore has two live spans of dimension 8 or 9. If either span is the
whole label space, nondegeneracy pins the cost at the other dimension, so the
saving \(9-\rho\) is 0 or 1. If both spans have dimension 8, they are the
kernels of the self-line functionals \(\lambda_\alpha\) and \(\lambda_\beta\).
The annihilator of \(\ker\lambda_\beta\) is the span of the label \(u_\beta\),
and \(u_\beta\) lies in \(\ker\lambda_\alpha\) exactly when
\(S(u_\alpha,u_\beta)=0\), that is when \(\langle\alpha,\beta\rangle\) is odd.
Hence
\[
\rho=8-[\langle\alpha,\beta\rangle\text{ is odd}],
\]
and the saving is 1 or 2. When \(\alpha\) and \(\beta\) are the same line,
\(\langle\alpha,\alpha\rangle=2\) is even, so \(u_\alpha\) is not in its own
kernel and the cost is 8. The saving is then 1. Deleting either sample root from its own
complement drops the span from 9 to 8 **(C.self-line-drop)**. The two odd
roots \(e_0+e_1\) and \(e_0+e_2\), with both lines deleted, have live pairing
rank 7 **(C.odd-pair)**.

The normals of nonzero terms are pairwise non-parallel on each side, because a
parallel pair would make an off-diagonal entry of \(\sum a_k b_k^{\mathsf T}\)
nonzero. A row normal parallel to a column normal of a different term is
likewise impossible. Each deleted root line is therefore used by at most one
term. The saving of a term is at most the number of such lines it uses, so
the total saving is at most \(p\) and the live cost is at least \(9t-p\). ∎

The nine-term witness, after deletion of the coordinate frame
\(\{e_{2a}\pm e_{2a+1}\}\), costs \(8+8+7\cdot 9=79\) **(C.punctured-cost)**.
That is above \(81-8=73\). The bound is a floor, not an attainment claim for
\(t>8\).

## 4. Why factor rank 9 is a different question

Columns confined to the root span cannot cancel a coordinate without changing
the normal. Leaving the span can. Replacing one frame column \(x\) by
\(x+e\) and \(x-e\), with \(e\) supported at one nonzero coordinate, preserves
the Gram identity and raises the left factor rank from 8 to 9. One of the two
new terms then has pairing rank 8, and the nine-term cost is 80 rather than
81 **(C.excursion)**. The rank hypothesis in Theorem 3 is therefore necessary
for the exact count \(9t\).

`research/ten-term-copy-cost` records a different ten-term factorization of
rank \((9,9)\) with copy cost 72. That example sits outside Theorem 3. It
meets the eight-term floor and does not undercut it. This package does not
extend the floor to factor rank 9 or higher.

## 5. E-graph corollary, cited

PR1212, Theorem 1, proves that a real rank-8 solution of the E-graph equations
on P120, or on the complement of any frame, equals \(D(2G)D^{-1}\) for an
invertible diagonal \(D\). This package does not re-prove that theorem. Any
factorization of such a matrix into real rank-1 terms whose two factor
matrices both have rank 8 has columns in that eight-dimensional column space.
The diagonal does not change zero patterns, so the supports and costs are those
of Theorem 3 or, on a frame complement, of Theorem 4 with \(p=8\). Nine or
more nonzero rank-(8, 8) terms therefore cost at least 81 on P120 and at least
73 on a frame complement. Both are strictly above the eight-term floors 72
and 64.

Factor matrices of rank greater than 8, and E-graph solutions of rank greater
than 8, remain outside this corollary. Complex coefficients remain outside it
as well: PR1212's gauge algebra extends to characteristic zero, but the copy
count uses the real normal geometry above, not the PR1077 extension.

## 6. What is not claimed

The selected record is unchanged. There is no frame, restoration, centre, or
full per-call invoice, and no claim that a physical word improves κ. A
factorization whose cost is at least 72 does not by itself produce a supplier.
The dominant-weight transport uses cited theorem (W); the verifier does not
enumerate the Weyl group. Lower-dimensional dominant flats are bounded by the
census **(B.no-large-lower-flat)** only as a check of that list, not as a
classification of every real subspace.
