# A scalar-polynomial limit for the actual doubled centre Gram

For every positive tensor size, the actual 112-port doubled centre Gram
has no annihilating scalar polynomial of degree less than 409. This
result rules out a short
polynomial identity for that operator. It does not bound the cost of
general weighted ADD circuits, matrix-valued encodings, or native
decoders.

The source is `circuit-interface/INTERFACE.json`, SHA-256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
It gives the actual eight-by-112 matrix R and its port labels. No eight
normal columns are added. In particular, `RR^T=56I`.

The exact Bell action was proved in
`residual-syndrome/physical-algebra/review-gauss/bell-compression/BELL-COMPRESSION.md`.
For one doubled tensor copy, the invariant Bell label is `c=a+b`.
On the a coordinate of the block with fixed c, the involution at port q
is `P_q(c)=X_q` when `q dot c=1` and `P_q(c)=Z_q` otherwise. Thus the
centre Gram on this block is the 4,096-dimensional rational matrix

    A_c = (1/4) sum_(q in the actual112 ports) r_q r_q^T P_q(c).

Choose `c=11` and the prime `p=65537`. The entries of A lie in
`Z[1/2]`, so reduction modulo p is defined. The vectors v and w are
integer vectors. Their 4,096 entries are the little-endian unsigned
16-bit words of 8,192 SHAKE256 bytes, from the UTF-8 seeds
`actual-bell-gram-c11-trial0` and
`actual-bell-gram-c11-trial0-observer`, respectively. Reshape them as
eight rows of 512 entries.

Form moments `s_j=w^T A_c^j v` and the 409-by-409 Hankel matrix
`H[i,j]=s_(i+j)` for indices from zero through 408. The exact modular
calculation gives

    det(H) = 2984 modulo65537.

In particular, the determinant is nonzero over Q. It follows that
`v,A_c v,...,A_c^408 v` are linearly independent: any dependence among
them would give the same dependence among the columns of H. Therefore
the minimal polynomial of A_c over Q has degree at least 409.

The full doubled centre operator contains this invariant block. There
is also an exact embedding at every positive tensor size lambda. In
Bell coordinates the vector `e_(a=0,b=0)` is a common positive-one
eigenvector of every `Gamma_q`. Restrict

    A_lambda=(1/4) sum_q r_q r_q^T Gamma_q^tensor(lambda)

to the first `c=11` block tensored with `e_0^tensor(lambda-1)`. The
restriction is exactly `A_1,c=11`; the root coefficient is applied once,
not once per tensor slot. Thus every individual positive tensor size
has minimal-polynomial degree at least 409. This also rules out a
lower-degree polynomial identity proposed uniformly for all sizes.
Scalar extension to the Gaussian rationals or complex numbers does not
remove a nonzero rational determinant.

`certify_bell_gram_degree.py` reproduces the 817 moments and the
determinant. It uses signed integer root coefficients and exact modular
arithmetic. All vector and matrix products fit in signed 64-bit integers
before reduction. The moment list and its SHA-256 are in
`BELL-GRAM-DEGREE.json`; the hash is
`a438880f142ea5c0a53120246fa5aed60c36db1d8052c911b485345fcb332150`.
A duplicate-row negative control must fail the same determinant check.
The certificate does not use a guessed recurrence or a characteristic
polynomial. Independent review passed in
`interface-proof/BELL-GRAM-DEGREE-REVIEW.json`. It derived R from the
original word, built the integer sparse operator `4A`, checked all
57,344 Bell monomial columns and all 817 moments, and used a separate
fraction-free Bareiss determinant calculation. A duplicate-column
control gave zero. The reviewer also supplied the invariant-subspace
extension to every positive tensor size.

The earlier degree-39 experiment concerned a different operator: the
paired single-Walsh construction. It cannot be transferred to this
doubled Bell representation. Conversely, this lower bound does not
invalidate that experiment or rule out a direct circuit for the weighted
sum. It narrows the short scalar-polynomial approach only. This work
used AI assistance.
