# A column-factor obstruction over a finite chain ring

Let R = F2[z]/(z^q), where q is any positive integer. For an R-module M,
write S(M) = {m in M : zm = 0}. This is an F2-vector space. All matrices
and all module inclusions below are over this same R.

**Column lemma.** If U is an n by L matrix, dim_F2 S(im U) <= L.

Proof. If U is nonzero, select an entry with minimum z-valuation v and move
it to the top left using row and column permutations. Every nonzero element
has the form z^v a with a a unit: a has constant coefficient 1 and its
inverse is the terminating geometric series for 1+(a+1). Scale the pivot
row by a inverse, making the pivot z^v. By minimality of v, every entry of
the pivot column is divisible by z^v. Subtract its quotient times the pivot
row to clear that column below the pivot. Every entry remaining in the
pivot row is also divisible by z^v; subtract its quotient times the pivot
column to clear the row to the right. These are invertible elementary
operations. No division by a nonunit was used: a quotient by z^v means
any explicit polynomial r such that z^v r equals the entry.

Repeat on the remaining submatrix. The result is a rectangular diagonal
matrix with r <= min(n,L) nonzero entries z^{v_i}, 0 <= v_i < q.
Column operations do not change the image; row operations give an
R-linear isomorphism of images, hence preserve S. The image of this
diagonal matrix is the direct sum of r ideals z^{v_i}R. Each ideal has
one-dimensional S, spanned by z^{q-1}. Thus dim S(im U)=r<=L. This also
covers U=0 and empty U, with r=0. QED.

**Product theorem.** Suppose P is a product of L matrices I+u_j v_j^T,
where u_j and v_j have n entries in R. No idempotence or invertibility
assumption on these increments is needed. If

    P = diag(d_1,...,d_n),

then L is at least the number t of indices with d_i != 1.

Proof. Use the written matrix product order P_j=P_{j-1}(I+u_j v_j^T),
with P_0=I. Telescoping gives

    P-I = sum_j (P_{j-1}u_j) v_j^T = UV,

where U has L columns. Thus im(P-I) is a submodule of im U, and
S(im(P-I)) is a subspace of S(im U). A nonzero diagonal entry d_i-1
generates a nonzero ideal z^{w_i}R, whose S has dimension one. Distinct
diagonal coordinates have disjoint support. Hence dim S(im(P-I))=t.
The column lemma gives t<=L. QED.

**Cyclic application and exact minimum.** Let q=2^k, k>=1, and let
g generate C_q. The map g -> 1+z identifies F2[C_q] with R: in
characteristic two (1+z)^q=1+z^q, and both quotient descriptions have
dimension q. For 0<s<q, g^s-1 is nonzero (its valuation is
2^{v_2(s)}); for s=0 it is zero. Consider n arbitrarily dirty registers,
with target diag(g^{s_1},...,g^{s_n}) and s_i in {0,...,q-1}. Allow paid
factors I+(g^s-1)xy^T for every 0<s<q and every binary x,y with y^T x=1.
There are no additional free transformations. Every paid increment is a
rank-one outer product over R, so the theorem gives L>=t, where t counts
nonzero s_i. Taking x=y=e_i and s=s_i for each such i gives exactly t
paid calls. Therefore the minimum is t.

The conclusion permits any number of additional dirty helper roles with
s_i=0: their diagonal entries in P-I are zero and contribute no S, while
the lower bound still sees every column on all roles. Helper restoration
and absence of cross terms are exact endpoint identities. An initially
zero helper promise is outside this model. Restricting the allowed powers
or changing the tariff preserves the lower bound on factor count but need
not preserve the t-call upper bound or give a native-cost bound.

For PR2187's four involution outputs, q=4 and t=4. The same conclusion
holds for q=8,16,... with target diag(g^{q/2} repeated four times), even
with arbitrarily many restored dirty helpers. At q=8 the ordinary binary
regular-rank screen gives only ceil(16/7)=3 calls. S distinguishes the four
independent target ideals and closes the root-lifting route uniformly.

**Boundary control.** The column lemma is not asserted for arbitrary
group algebras. In F2[x,y]/(x^2,y^2), the one-column matrix U=(x,y)^T
has kernel (xy) and image isomorphic to R/(xy). Its annihilator by the
maximal ideal (x,y) is two-dimensional, with images of x and y as a basis.
Thus a corresponding socle bound by one column fails. The verifier checks
this witness. This does not construct a saving in that group algebra.

This is an elementary written proof, not a kernel-checked theorem or a
claim of literature priority. The finite verifier independently compares
valuation elimination with binary image/nullity calculations; it supplies
diagnostic evidence for the proof's algebra, not exhaustive coverage of
all q, n or words. No native rational-frame supplier is constructed.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
