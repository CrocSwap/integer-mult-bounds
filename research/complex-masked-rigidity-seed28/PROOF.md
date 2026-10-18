# The even-pair mask is rigid with one root-linear factor

The conclusion requires at least one factor to lie in the root-coordinate
column space. It does **not** assume that an arbitrary masked decoder has
that property.

## 1. Statement and concrete domain

Let \(\mathcal L\) be the 120 E8 root lines, with one representative \(r_i\)
of squared norm 2 on each line. In standard coordinates these are the lines of

\[
 \{\pm e_a\pm e_b:a<b\}\;\cup\;
 \{(\sigma_1,\ldots,\sigma_8)/2:
       \sigma_a\in\{\pm1\},\ \#\{a:\sigma_a=-1\}\text{ even}\}.
\]

An orthogonal frame consists of eight pairwise orthogonal lines. Fix the frame
\(F_0=\{\mathbb R(e_{2a-1}\pm e_{2a}):1\le a\le4\}\). Our concrete live sets are:

- P112: \(\mathcal L\setminus F_0\);
- its 112 P111 deletions: \(\mathcal L\setminus(F_0\cup\{j\})\), \(j\notin F_0\);
- the 1260 P104 sets \(\mathcal L\setminus(F_0\cup F_1)\), where \(F_1\) is an
  orthogonal frame disjoint from \(F_0\).

The finite frame enumeration supplies the number 1260; the argument below
applies to every such frame independently of that count. There are thus 1373
concrete live sets in the certificate.

For a live set \(L\), let \(R\) have rows \(r_i^T\), \(i\in L\). The **even-pair
mask** consists of the ordered pairs with \(r_i^Tr_j\) even. Since distinct E8
root lines have inner product \(-1,0,1\), this means precisely the orthogonal
ordered pairs and every diagonal pair. All transposes below are ordinary
transposes, not conjugate transposes.

**Theorem.** For any of these live sets and any integer \(m\ge1\), let
\(D,T\in\mathbb C^{|L|\times m}\). Assume at least one of

\[
 \operatorname{col}(D)\subseteq\operatorname{col}(R),\qquad
 \operatorname{col}(T)\subseteq\operatorname{col}(R).                       \tag{H}
\]

If \((DT^T)_{ij}=2r_i^Tr_j\) on the even-pair mask, then
\(DT^T=2RR^T\) on **all** live ordered pairs. The other factor is unrestricted
and no rank assumption on either factor is needed. The same holds over
\(\mathbb Q\) and \(\mathbb R\).

**Both-factor corollary.** In particular, for arbitrary
\(A,B\in\mathbb C^{8\times m}\), the factors \(D=RA\), \(T=RB\) satisfy the
mask if and only if \(AB^T=2I_8\). Thus the masked and all-pairs feasible
sets coincide separately for every term count \(m\), either with both
factors root-linear or with just one specified factor root-linear.

## 2. Two elementary covariance identities

The orientation chosen for a line does not affect its outer product. For
true-root coordinates,

\[
 \sum_{i\in\mathcal L}r_i r_i^T=30I_8,                                      \tag{1}
\]
\[
 \sum_{i:r_i\perp r}r_i r_i^T=18I_8-9rr^T
       =18\left(I_8-\frac{rr^T}{2}\right).                                \tag{2}
\]

Here \(r\) is any E8 root representative and there are 63 lines in the sum in
(2). These identities can be proved without any classification of flats or
Weyl-group transitivity assumption:

For (1), even sign changes make each off-diagonal entry zero, coordinate
permutations make the diagonal entries equal, and the trace is \(120\cdot2\).
For (2), even signed coordinate permutations reduce to two cases.

- For \(r=e_1+e_2\), the perpendicular integer-root lines are \(e_1-e_2\)
  and the 30 D6 lines on coordinates 3 through 8. Their covariance is
  \((e_1-e_2)(e_1-e_2)^T+10I_6\), with the last term supported on those six
  coordinates. The 32 perpendicular half-root lines contribute
  \(8(e_1-e_2)(e_1-e_2)^T+8I_6\): their first two signs are opposite and the
  last six have odd parity, so the other mixed entries cancel. The total is
  \(18I_8-9rr^T\).
- For \(r=(1,\ldots,1)/2\), the 28 perpendicular integer-root lines are
  \(e_a-e_b\), with covariance \(8I_8-J\). The 35 perpendicular half-root
  lines have four negative signs. Their covariance has diagonal \(35/4\),
  constant off-diagonal entries, and row sums zero, so it is
  \(10I_8-(5/4)J\). The sum is \(18I_8-(9/4)J=18I_8-9rr^T\).

Here \(J\) denotes the all-ones matrix. The finite checker verifies both
identities directly for all 120 lines. If \(q_i=2r_i\) are its integer doubled
coordinates, the identities checked entry by entry are

\[
 \sum_i q_iq_i^T=120I_8,\qquad
 \sum_{i:q_i\perp q}q_iq_i^T=72I_8-9qq^T.                                 \tag{3}
\]

## 3. Survival after removing orthogonal sets

For any set \(F\) of pairwise orthogonal norm-squared-2 roots and any real
vector \(x\), Bessel's inequality gives

\[
 \sum_{i\in F}(r_i^Tx)^2\le2\|x\|^2.                                    \tag{4}
\]

Suppose the deleted set \(P\) is contained in the union of \(k\le8\) such
orthogonal sets. They may overlap and need not be complete frames. For every
live root \(r\) and real \(x\perp r\), (2) and (4) give

\[
 \sum_{i\notin P,\ r_i\perp r}(r_i^Tx)^2
 \ge(18-2k)\|x\|^2>0\quad(x\ne0).                                      \tag{5}
\]

Thus the live roots perpendicular to \(r\) span the full seven-dimensional
space \(r^\perp\). Moreover, (1) and (4) give

\[
 \sum_{i\notin P}(r_i^Tx)^2\ge(30-2k)\|x\|^2>0\quad(x\ne0),               \tag{6}
\]

so the live roots span \(\mathbb R^8\). For our concrete domain, \(k=1\) for
P112 and \(k=2\) for P111 and P104; a singleton is an orthogonal set. The
respective perpendicular-space lower bounds are 16 and 14, and the
whole-space lower bounds are 28 and 26.

This proves a modest geometric extension as well: the theorem holds whenever
the deleted lines are covered by at most eight orthogonal sets. No census of
those larger deletion domains is claimed.

## 4. From the mask to the full product

First assume \(D=RA\) for some \(A\in\mathbb C^{8\times m}\), leaving
\(T\) arbitrary. Let \(t_j\in\mathbb C^m\) be the transpose of row \(j\)
of \(T\), and define

\[
 c_j=A t_j-2r_j.
\]

Column \(j\) of the product error \(DT^T-2RR^T\) equals \(Rc_j\).
The masked equations say that \(r_i^Tc_j=0\) for every live \(r_i\perp r_j\)
and for \(i=j\). The perpendicular live roots span \(r_j^\perp\) by (5),
and adjoining \(r_j\) spans \(\mathbb R^8\). This real spanning statement
also holds after complexification. Therefore \(c_j=0\), for every \(j\),
and the entire product error vanishes. If instead \(T\) is root-linear,
transpose the error and apply the same argument; the mask is symmetric.

If both factors are root-linear, the result gives
\(R(AB^T-2I_8)R^T=0\). Since \(R\) has rank eight by (6), multiplication
by a left inverse of \(R\) and its transpose gives \(AB^T=2I_8\).
The converse is immediate.

Equivalently, every live vertex has masked neighbours whose root-coordinate
rows span eight dimensions. This local spanning condition proves the
one-sided assertion; it is stronger information than a 64-column tensor-rank
calculation alone supplies. The both-factor corollary also implies that the
ordered even-pair tensors \(r_i\otimes r_j\) span all 64 dimensions.

The diagonal equations are essential. If only orthogonal off-diagonal pairs
were imposed, the zero product would satisfy those zero target entries but
fail every target diagonal. Likewise, the homogeneous tensor equations on
orthogonal pairs alone annihilate \(K=I_8\).

## 5. Scope and the omitted hypothesis

This is a statement about factors with at least one root-linear side, of any
finite term count. It
does not establish a copy-cost minimum for nine or more terms, a realizable
physical supplier, a new exponent, or a result for arbitrary masked factors.
Existing all-pairs results can only be transferred with their other
hypotheses intact. In particular, an existing eight-term result does not
become an arbitrary-term result through this theorem.

Requiring a root-linear side is essential. Choose a live odd pair \((i,j)\)
and form \(M=2RR^T+E_{ij}\), where \(E_{ij}\) is the corresponding matrix unit.
Then \(M\) satisfies every masked equation but differs on that odd pair.
Writing \(v=|L|\), the unrestricted factors \(D=I_v\) and \(T=M^T\) satisfy
\(DT^T=M\). Such factors are outside the theorem: neither side satisfies (H). In
particular, \(I_v\) cannot have its columns in the eight-dimensional
root-coordinate column space when \(v>8\); if the other side satisfied
(H), the theorem would contradict the nonzero product error. The checker
includes this semantic negative control.
