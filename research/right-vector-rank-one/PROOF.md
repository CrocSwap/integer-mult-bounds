# Exact cost of an ordinary rank-one target

Let K be any field, R=M_m(K), m>=2, and n>=1. A paid factor is
P(u,y)=I_n+u y^T, where u belongs to R^n and y belongs to K^n. Free maps
are GL_n(K), acting as S tensor I_m. Cost counts paid factors in an arbitrary
word of paid and free maps. The target M is an nm by nm matrix, partitioned
into n by n blocks of size m. Rank in this note always means ordinary K-rank
on K^(nm), rather than the predecessor's column-image dimension on K^n.

**Theorem.** If rank_K(M)=1, then cost(M)=n. There is an attaining word with
n paid factors and one free input-block permutation, without scratch roles.

The ordinary rank inequalities below are classical. The contribution is their
application to this restricted-right-vector alphabet and the attaining word
for every ordinary rank-one matrix-algebra target at every role count. The
alphabet and exact-cost questions are inherited from #4099/#4243/#4265/#4276.

## Lower bound, including arbitrary free maps

For y nonzero, P(u,y) fixes (ker y^T) tensor K^m pointwise. That subspace has
dimension (n-1)m, so rank P(u,y)>=(n-1)m. If y=0 the factor is the identity.
Thus each paid factor has nullity at most m. Each free map has nullity zero.

For square matrices of common size N, Sylvester's inequality gives

    nullity(A B) <= nullity(A) + nullity(B).

Induction along any word with k paid factors, allowing any number and position
of free maps, therefore gives rank M >= nm-km. If k<=n-1, rank M>=m>=2,
which contradicts rank M=1. Hence cost(M)>=n. In fact this proves the same
lower bound for every target with ordinary rank strictly below m.

## Attaining word

Write M=a b, where a is a nonzero column of length nm and b is a nonzero row
of length nm. Write a_i and b_j for their length-m blocks, so M_ij=a_i b_j.
Choose a nonzero block b_j. A free permutation of the input blocks moves it
to b_1. In this paragraph M denotes that permuted target; undo the permutation
at the right endpoint at no paid cost.

Choose an internal coordinate h with b_1[h]!=0. For j=2,...,n, define the
m by m matrix

    C_j = e_h b_j / b_1[h].

Then b_1 C_j=b_j. Define F_1 to equal I_n with its first block column
replaced by (a_1 b_1,...,a_n b_1)^T. This is the allowed paid factor

    F_1 = I_n + u_1 e_1^T,
    (u_1)_i = a_i b_1 - delta_(i,1) I_m.

For each j>=2 define F_j to equal I_n with its j-th block column replaced
by e_1 C_j. Equivalently,

    F_j = I_n + u_j e_j^T,
    (u_j)_1=C_j, (u_j)_j=-I_m, all other blocks zero.

Right multiplication by F_j replaces block column j by block column 1
times C_j, and preserves every other block column. Starting from F_1,
successive right multiplication by F_2,...,F_n therefore gives columns

    a b_1, a b_1 C_2, ..., a b_1 C_n
    = a b_1, a b_2, ..., a b_n.

Consequently F_1 F_2 ... F_n=M. The displayed product is a matrix product;
on column data its chronological execution is F_n,...,F_1, after the free
input permutation at the right endpoint. All right vectors e_j are over K.
The left coefficients belong to R, as permitted. The formula also covers
n=1 with only F_1. This proves cost(M)<=n and completes the theorem.

## Boundary controls and scope

The zero target also has cost n, by the same rank bound and n coordinate
zeroing factors. This zero-target fact is already a case of #4243's diagonal
theorem and is not claimed as new.

The assumption m>=2 matters. At m=1 every nonzero rank-one target has cost
n-1: free left/right field basis changes reduce it to diag(1,0,...,0),
and ordinary nullity gives the matching lower bound. This also follows from
the predecessor diagonal theorem. Free maps of the theorem are always
S tensor I_m. Its lower bound also survives arbitrary invertible maps on
K^(nm), since such maps have nullity zero.

These are singular formal targets. Their overwrite behavior discards data.
No reversible dirty-helper restoration, native coefficient preparation,
physical routing, precision, stock or complete supplier invoice is supplied.
No multiplication theorem or exponent improvement follows.
