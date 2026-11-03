# Sharp rank cost of separating a Gaussian transform into two banks

This is a scoped proof over the real or complex numbers. The integer `t`
counts tensor factors, and `N=2^t` is the number of address coordinates.
Ordinary matrix rank on these coordinates is different from the binary
frame rank used in a recursive invoice.

## Contract and theorem

Let `H_t[x,y]=(-1)^(x dot y)`, with `x,y` binary `t`-tuples. Choose arbitrary
partitions `R0,R1` of the rows and `C0,C1` of the columns, each part of size
`N/2`. An independent-bank target `D` has zero blocks `D[R0,C1]` and
`D[R1,C0]`, and its two diagonal blocks are invertible. Nothing else is
required of these blocks. Inputs are arbitrary on all `N` coordinates.

For `t>=2`, every additive repair `E` satisfying `H_t+E=D` has

```text
rank(E) >= N/4 = 2^(t-2).
```

The minimum over all partitions, independent-bank targets and repairs is
exactly `N/4`. The equality target can be chosen orthogonal after the same
normalization `1/sqrt(N)` used for `H_t`. The multiplicative version is
equally sharp: `Q H_t=D` requires `rank(Q-I)>=N/4`. At least `N/4` arbitrary
rank-one linear updates after the transform are necessary. A product of
exactly `N/4` invertible, mutually commuting reflections attains the minimum
for the exhibited partitions and target.

Arbitrary invertible monomial input and output adapters do not change the
minimum. They may permute addresses and multiply them by arbitrary nonzero
scalars. They need not be reciprocal or have equal phases.

For `t=1` the separate exact minimum is one. The quarter expression is not
an integer in this case.

## Lower bound

We include the classical submatrix argument to make the proof self-contained.
Walsh orthogonality gives `H_t H_t*=N I`. If `B` is an `a` by `b` submatrix,
coordinate restriction and extension have operator norm one, so
`||B||_2 <= sqrt(N)`. Since every entry of `B` has modulus one,

```text
ab = ||B||_F^2 <= rank(B) ||B||_2^2 <= N rank(B).
```

This is the standard Hadamard submatrix rank bound associated with Lokam's
spectral method. It is not a new uncertainty or rigidity theorem.

Apply it to `B=H_t[R0,C1]`, where `a=b=N/2`. Since the target's corresponding
block vanishes, `E[R0,C1]=-B`. Thus `rank(E)>=rank(B)>=N/4`.
Invertibility of the target was not needed for this lower bound.

Because `H_t` is invertible, `rank(Q-I)=rank((Q-I)H_t)=rank(D-H_t)`.
For a product of `k` rank-one updates `Q_j=I+u_j v_j*`, telescope the product
minus identity. Each summand has rank at most one, so `rank(Q_k...Q_1-I)<=k`.
The same bound therefore applies with arbitrary coefficients, collection
linear forms, scatter directions and intermediate states granted free.

A monomial matrix is a permutation followed by invertible diagonal scaling.
Pull both adapters back from `L H_t R + E = D`. This replaces `E` by
`L^-1 E R^-1`, preserves its rank, and replaces the two target partitions by
permuted coordinate partitions. Their sizes and cross-block zeros persist.
Thus the preceding argument applies. It would not apply to arbitrary
encoders that mix coordinates across banks.

## Sharp four-coordinate identity

Permute the columns of `H_2` in order `0,2,1,3`, obtaining

```text
M = [ 1  1   1   1 ]     u = [ 1 ]
    [ 1  1  -1  -1 ]         [-1 ]
    [ 1 -1   1  -1 ]         [ 1 ]
    [ 1 -1  -1   1 ]         [ 1 ].
```

Put `Q=I-u u^T/2`. Since `u^T u=4`, `Q^2=I` and `Q^T=Q`, so `Q` is an
orthogonal reflection with `rank(Q-I)=1`. Direct multiplication gives

```text
Q M = diag(2 X, -2 X),   X = [[0,1],[1,0]].
```

Both banks are invertible and independent. Dividing both the transform
and target by two makes them orthogonal. For `t>=2`, tensor the displayed
identity with `H_(t-2)`. The row banks consist of the first and last two
four-coordinate groups. The column permutation swaps the first two bits.
The resulting repair is

```text
Q_t = (I_4-u u^T/2) tensor I_(N/4),
D_t = diag(2 X tensor H_(t-2), -2 X tensor H_(t-2)).
```

It has `rank(Q_t-I)=N/4`, and `D_t D_t^T=N I`. There is no inactive or
zero-input coordinate. For each of the `N/4` suffix addresses, apply the
reflection on its four-coordinate fiber. These reflections have disjoint
supports, commute, and give `Q_t` exactly. This proves attainment by exactly
`N/4` invertible rank-one updates. The target is allowed to vary in this
minimum. It is not asserted to equal two specified width-`t-1` native jobs.

For `t=1`, `H_1=[[1,1],[1,-1]]` and the independent invertible target
`D=diag(3,-1/2)` have rank-one difference. The nonzero cross entry excludes
rank zero.

## Connection to the Gaussian kernel

For the raw one-axis complex Gaussian kernel,

```text
G = [[i,1],[1,i]] = diag(i,1) H_1 diag(1,-i).
```

Tensoring supplies the required monomial equivalence for every `t`.
Multiplication by `(1+i)^(-t)` gives the usual unitary Gaussian convention
and does not change a correction rank or a cross-block zero. Thus the
obstruction applies to this Gaussian kernel as well as to Walsh matrices.
The equality construction transports through these monomial maps. In the
Gaussian normalization its coefficients are Gaussian dyadics. No phase
is discarded. The checker corroborates the raw kernel identity entry by
entry without importing a predecessor's native implementation.

## What this settles

One dense binary Gaussian transform cannot supply two independent balanced
coordinate banks with a correction of rank below one quarter of its address
dimension, even when the two resulting invertible bank maps may be chosen
freely. Monomial routing alone is the rank-zero case and is excluded.
The bound is attained by the explicit reflection family.

This is a lower bound on a deliberately generous linear interface. It gives
no physical price for one rank-one update. A native call, ADD or collected
array can have a different relation to ordinary coordinate rank. The result
does not establish an unfavorable complete signed moment, exclude general
cross-bank encoders, or audit any earlier supplier. Native realization,
causal reads, ownership, dirty restoration, precision, stock, tape, compiler
and outer transfer remain obligations. No new kappa or complete
multiplication theorem is claimed.

## Credit

The submatrix rank inequality is classical. See S. V. Lokam,
[Spectral methods for matrix rigidity](https://doi.org/10.1006/jcss.2001.1786),
and the independent quantum-information proof by de Wolf in
[Lower bounds on matrix rigidity via a quantum argument](https://homepages.cwi.nl/~rdewolf/publ/qc/qr-icalp06.pdf).
Walsh orthogonality, tensor products, Householder reflections and rank
telescoping are classical as well. No literature-priority claim is made.

Greer Guthrie's PR679 supplies the repository's selector-batching and
monomial-support warning. Arham Tahir's PR1920, ToikY's PR1924 and ywz65's
sharp nonreciprocal correction package study reciprocal encoders or clean
spectral injection, with different targets and cost contracts. Nick Petalas's
PR6443 studies unitary reciprocal encoders and specified repeated Clifford
lanes. None is used as a theorem or executed here. The present contribution
is the balanced-coordinate, freely chosen independent-bank repair minimum
and its sharp reflection witness. The Gaussian/native lineage retains
icekylinx, Rohan Arun, Chafik Boukhalfa, Jeremy Kothe, DreamingOfClouds and
the credited source authors. This contribution was produced by Nick Petalas.
