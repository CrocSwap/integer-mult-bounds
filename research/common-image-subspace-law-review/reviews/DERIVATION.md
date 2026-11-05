# External derivation of the dependency-space common-image guard law

## Verdict and exposure

**Verdict: the supplied PR6710 joint-law statement follows under the stated finite-field, fixed-family and complete-uniform-header assumptions. No gap was found in this derivation.** This is an external written audit of SHIN09-git's existing law, not a new generalization of our binary result or a new probability/count theorem.

The coordinator supplied the target statement and formula, identifying PR6710 head `465a0060fbd236a5e202619de4a45a694d44970a`, `research/common-image-guard-pencils/PROOF.md`. Before sealing this draft I did **not** open that source proof, the coordinator's sketch, or another current-session derivation. The statement/formula were known, so this is source-proof-unexposed derivation of a known target, not blind discovery. I participated in the earlier B10 binary-family6701 and all-field pair-sign6703 work, and this round read their prose plus Petalas4807's pair proof. That prior source/method exposure is retained rather than obscured.

No scientific/source program, constructor, import, compilation, census, numerical experiment, native operation or formal kernel was executed. Only this written argument and its metadata seal were authored. No sign inequality, special pencil count, restricted/fixed-determinant header result, implementation audit, physical interface or complete caller claim is included.

## 1. Precise family and statement

Let K=F_q be a finite field, q a prime power. Let m>=2 and k>=1. Write t=(1,...,1)^T in K^k. Fix a nonzero column u in K^m and a k-by-m matrix V, with rows v_i, such that

    V*u=t,    im(V)=S,    dim(S)=r<=m.

Necessarily r>=1 because t is nonzero, and the one-dimensional subspace T=<t> is contained in S. No independence or distinctness of the k rows is required. In particular k can exceed m. Each row is nonzero because v_i*u=1, so U_i=u*v_i is a rank-one idempotent and P_i=I-U_i is its corank-one complement.

A complete header G is uniform in GL_m(K). Event E_i means that every leading principal minor of G*P_i*G^-1, of orders1 throughm-1, is nonzero. The full determinant, which is zero, is not a required guard.

For each subspace L with T<=L<=S, put

    h(L) = #{z in L : every coordinate z_i is nonzero},
    lambda(L) = q^dim(L)+(q-1)*h(L),
    mu(L,S) = (-1)^c q^[c(c-1)/2],  c=r-dim(L).

Let

    D_r = (q^m-1) q^(m-1)
          * product_(i=0)^(r-2) (q^(m-1)-q^i),

where the product is empty and equals one when r=1. The reviewed claim is

    Pr(E_1 and ... and E_k)
      = (q-1) * [sum_(T<=L<=S) mu(L,S) lambda(L)^(m-1)] / D_r.   (1)

The subspaces are subspaces of the actual coordinate image S in K^k. Coordinate support is meaningful in that fixed ambient space. An arbitrary abstract isomorphism of S need not preserve h(L); the prescribed rows/output coordinates cannot be discarded.

## 2. The normalized-vector tuple orbit

Consider the action

    (u,V) -> (G*u, V*G^-1).

It preserves u nonzero, im(V)=S and V*u=t. Conversely it is transitive on the set of all pairs satisfying these conditions, with S and t fixed.

Choose once a basis s1=t,s2,...,sr of S. For a tuple (u,V), choose b1=u and choose b_j with V*b_j=s_j for2<=j<=r. Append a basis b_(r+1),...,b_m of ker(V). These m columns form a basis of K^m: applying V to a linear relation first makes all coefficients of b1,...,br zero, and the remaining kernel basis is independent. Let B be its matrix and Q the k-by-r matrix with columns s1,...,sr. Then

    B^-1*u=e1,    V*B=[Q 0].

Perform the same construction for a second tuple (u',V'), giving B'. The invertible matrix G=B'*B^-1 satisfies G*u=u' and V*G^-1=V'. This proves transitivity. In particular the row dependencies are handled exactly by im(V)=S, rather than by a false independent-row normalization.

Uniform G therefore gives uniform probability on this tuple orbit. For a fixed starting tuple, the headers mapping it to any target tuple form a coset of its stabilizer, so every fiber has equal size.

For completeness, in the adapted coordinates a stabilizer matrix has the block form

    [ I_r   0 ]
    [  A    H ],

with H in GL_(m-r)(K). Indeed [Q0]*G^-1=[Q0] is equivalent to [Q0]*G=[Q0], and Q has independent columns, forcing the upper block to be [I_r0]. Fixing u=e1 forces the first column of A to vanish. The other (r-1)(m-r) entries of A are arbitrary. Thus every complete-header fiber has exactly

    q^[(r-1)(m-r)] * |GL_(m-r)(K)|                 (2)

members, with |GL_0|=1. At r=m this gives fiber one.

These are normalized **vector** tuples, not common-image lines. Replacing u by a nonzero multiple and V by its reciprocal multiple preserves the underlying idempotents, but creates a different vector tuple in this orbit. Such lifts have equal multiplicity and the guard event is unchanged. One must not divide D_r by q-1 while leaving the tuple numerator unchanged. The q-1 in (1) below comes from the final coordinate's factorizations, not from a line/vector gauge adjustment.

## 3. Counting the full tuple orbit: D_r

There are q^m-1 choices for u. For a fixed u, use any domain basis with u as its last vector. The constraint V*u=t fixes the last column of V to t. Its other m-1 columns lie in S, and together with t they must span S.

Pass to S/T, of dimension r-1. The first m-1 columns must project to a surjective map K^(m-1)->S/T. In fixed quotient coordinates, its r-1 rows must be independent. Choosing those rows successively gives

    product_(i=0)^(r-2) (q^(m-1)-q^i)

possibilities. For each projected column, there are q independent lifts along T; over m-1 columns this contributes q^(m-1). Thus the number of V for each nonzero u is exactly the latter factor times the product. Multiplying by q^m-1 proves that the orbit size is D_r.

There is no choice of an additional endpoint column: it is the fixed vector t. The empty product handles r=1. The product is positive for all1<=r<=m, including r=m; the excluded r>m case would have no such surjective V. This count is consistent with (2), but does not require evaluating a full GL census.

## 4. Every proper guard is a safe partial-sum condition

For a transformed tuple let x=G*u and W=V*G^-1. Write z_a for column a of W. For each prefix length ell set

    s_ell = sum_(a=1)^ell x_a*z_a in S,
    s_0=0,    s_m=W*x=t.

For row i, the leading ell block of the transformed complement is I_ell minus the outer product of the first ell entries of x and row i of W. The rank-one determinant identity gives

    det((G*P_i*G^-1)[1:ell,1:ell]) = 1-(s_ell)_i.

Hence all the required events are equivalent to

    (s_ell)_i != 1 for every i and every1<=ell<=m-1,     s_m=t.   (3)

This applies in every characteristic. In F_2 the safe coordinate must be zero, but for larger fields it need only avoid one; no binary zero-support simplification has been used. Repeated rows simply repeat guard conditions and do not invalidate (3).

## 5. Count column images contained in L before requiring exact image

Fix T<=L<=S and write d=dim(L). Let F(L) count all pairs (x,W) such that every column of W lies in L, W*x=t, and (3) holds. Rank is not yet required to be d or r. Although x is initially allowed to range over K^m for this counting step, W*x=t!=0 automatically excludes x=0.

The safe partial-sum set is

    A_L = {s in L : every coordinate s_i !=1}.

It contains0 and excludes t. Translation s->t-s is a bijection from A_L to the full-support vectors of L, because T<=L and 1-s_i is nonzero exactly when s_i!=1. Thus |A_L|=h(L). This is why the invariant in (1) uses full support, even though the guard itself avoids one.

At one coordinate a, the scalar/vector pair (alpha,z)=(x_a,z_a) lies in K times L and supplies increment y=alpha*z. For a zero increment there are q^d choices with alpha=0, plus q-1 choices with alpha nonzero and z=0. For any specified nonzero y in L, alpha must be nonzero, and each of its q-1 choices uniquely determines z=alpha^-1*y. Therefore the increment multiplicity is

    weight_L(y) = q^d * 1_(y=0) + (q-1).               (4)

For safe states s,s' in A_L, their difference lies in L. The weighted transition matrix for one proper coordinate is consequently

    M_L = q^d I + (q-1) 11^T,

where the matrix has h(L) rows and columns. Every row sum is lambda(L). Starting at the safe state0, the total weight of all m-1 proper safe transitions is lambda(L)^(m-1): multiplication by M_L preserves the all-ones vector up to this factor.

For the final coordinate, every safe state s has t-s nonzero, since t itself is not safe. Its final increment has exactly q-1 factorizations by (4). Thus

    F(L) = (q-1) lambda(L)^(m-1).                       (5)

In particular alpha=x_m=0 is **not** permitted in that terminal count. If it were zero, the last increment would vanish and the preceding proper prefix would already be t, violating every coordinate's guard. Treating this last step as an ordinary safe-state step or applying the zero-increment multiplicity would be an error. No terminal-rank cutoff, first-pivot substitute or omitted final coordinate has entered (5).

Each coordinate pair (x_a,z_a) is counted once by its increment and factorization; choices at different coordinates are independent Cartesian choices. Conversely those choices reconstruct exactly one pair (x,W). This justifies using transfer weights to count actual tuples, rather than only unweighted paths.

## 6. Enforce exact image by interval Möbius inversion

Let H(M) count passing pairs whose column image is exactly M. The endpoint W*x=t forces M to contain T. Thus for every T<=L<=S,

    F(L) = sum_(T<=M<=L) H(M).                         (6)

The splitting is disjoint because a matrix has a unique image. In particular it does not subtract only repeated rows or only pairwise dependencies; all possible relation spaces are present. This is the point at which a naive extension of a dependent-pair subtraction would be inadequate.

Inversion on the finite subspace interval gives

    H(S) = sum_(T<=L<=S) mu(L,S) F(L).                 (7)

Here mu(L,S)=(-1)^c q^[c(c-1)/2], c=dim(S/L). The fact that we work in the smaller interval above T does not change this coefficient: the interval from L to S is still the full subspace lattice of S/L.

For a self-contained verification of that coefficient, let N(c,j) be the number of j-dimensional subspaces of K^c. Relative to a fixed hyperplane, those contained in it number N(c-1,j); for each (j-1)-dimensional intersection, those not contained in it number q^(c-j). Hence

    N(c,j)=N(c-1,j)+q^(c-j) N(c-1,j-1).

Induction with this recurrence proves the polynomial identity

    product_(i=0)^(c-1) (1-q^i z)
      = sum_(j=0)^c (-1)^j q^[j(j-1)/2] N(c,j) z^j.

At z=1 the sum is zero for c>0 because the product contains1-1, and equals one for c=0. These are exactly the interval-sum recursion for the proposed subspace Möbius coefficients. The coefficient at c=0 is one; the vanishing sum recursively determines every higher coefficient, establishing the formula and therefore (7). No inversion theorem tied to a special characteristic or an unproved finite enumeration is needed.

Substitute (5) into (7), then divide by the full normalized-vector orbit size D_r from Section3. Uniformity from Section2 makes that ratio exactly the complete-header event probability. This yields (1).

## 7. Boundaries and nonclaims

- **r=1:** only L=T=S occurs in the sum, with mu=1; the empty product in D_r is one. All normalized rows of V are the same covector, so duplicated guard events introduce no false independence factor.
- **r=m:** the adapted-kernel blocks are empty and the header fiber is one. The quotient rank count still applies with r-1=m-1. No extra endpoint or basis choice is to be divided out.
- **k>m, dependent or repeated rows:** these are allowed because the law depends on the actual image space S and its coordinate-support geometry, with1<=r<=m. Full row rank k is never assumed. A zero row is excluded by V*u=t, not by a separate unstated condition.
- **Every prime-power q:** all arguments use finite-field vector spaces, exact scalar factorization, and the subspace lattice. They do not treat a non-prime-power integer as a field size or use an odd-characteristic-only step.
- **Complete uniform headers:** G^-1 is part of the stated conjugation. Inversion is a permutation of GL_m, but it does not license exchanging action conventions without transforming both u and V consistently. Restricted, weighted or determinant-constrained header distributions need a different measure argument.
- **Normalized vector versus line:** scalar lifts do not change the event, but tuple numerator and denominator must be counted at the same normalization. No q-1 factor is removed or introduced by silently passing to common image lines.

The numerator in (1) is an alternating expression, but the derivation identifies it with the nonnegative integer count H(S). This audit does not assert a correlation sign relative to the product of marginals, classify pencils/affine flats, optimize header distributions or produce new finite numeric values.

## Credit and remaining obligations

The all-field arbitrary-dependency-space law is the existing PR6710 result of SHIN09-git. Nick Petalas4807 supplies the predecessor safe-prefix increment method and dependent-pair subtraction, with4227/4261 marginal/partial-sum lineage. The earlier binary6701 proof and pair-sign6703 result remain prior, not newly counted. Rank-one determinants, orbit-stabilizer, full-rank matrix counts and subspace Möbius inversion are classical methods; their ownership is not reassigned by this review. Retain the source's complete notices, construction/compiler lineage and AI-assistance disclosures.

This written audit supplies no executed verification, numerical sign/census, physical header selection/emission/dispatch, input producer, dirty restoration, stock/precision/tape costs, full caller invoice, native supplier admission, human/formal-kernel acceptance or selected-frontier change. It does not repeat the source's separate sign or geometric classifications merely because the joint-law formula is now derived.
