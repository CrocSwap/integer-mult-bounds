# Affine sectors of maximum dimension

Let `S_n` be the binary `n`-by-`lambda` matrices `X` for which

    wt(sum_i q_i x_i) mod 4

is the same for every odd binary vector `q`. Here `x_i` is row `i`.
The common residue can depend on `X`. Let `S_(n,d)` fix that residue.
All vector spaces and dot products below are over `F_2`.

This note proves the equality classification proposed by the parent.
It uses the common-form dimension bound from `ACCESS.md`, SHA256
`a5a91cdc4deed08aa15693aedbcc01f48186859f8902acdb864aa74fb6feba4d`,
and proves the further equality steps here. The term "maximum" means
maximum dimension. It does not mean maximal only under inclusion.

## 1. Classification

Assume `n>=3` and `lambda>0`. Write `omega` for the all-one vector of
length `lambda`, and `Omega=(omega,...,omega)` for its common row tuple.

For `lambda=2f`, an affine set `A+V` in `S_n` has dimension `nf` if and
only if

    A+V = (a+W)^n,

where `W` is self-dual for the dot product and `a+W` has constant
Hamming weight modulo four. In particular, `dim W=f`.

For `lambda=2f+1`, an affine set in `S_n` has dimension `nf+1` if and
only if

    A+V = (a+W)^n + span(Omega),

where `W` is self-orthogonal of dimension `f` and `a+W` has constant
Hamming weight modulo four. Equivalently, this set is

    (a+W)^n union (a+omega+W)^n.

The assertion concerns the whole affine set. A different choice of
offset can give the same set.

### The common form and its equality cases

Let `p_i:V->F_2^lambda` be the row projection. Since the row weights
agree modulo four, their second differences give one common symmetric
binary form

    B(u,v)=p_i(u).p_i(v)

for all `i`. Put `r=rank B`, `K=rad B`, and `W_i=p_i(K)`.
The image `W_i` is the radical of `p_i(V)`. If `s_i=dim W_i`, then

    r+2s_i<=lambda,
    dim V=r+dim K<=r+sum_i s_i
         <=r+n floor((lambda-r)/2).

The middle inequality uses the injective combined row map on `K`.

If `lambda=2f` and `r=2t`, the last bound is
`nf-(n-2)t`. If `r=2t+1`, it is
`nf-(n-2)t-(n-1)`. For `n>=3`, dimension `nf` therefore forces `r=0`.
It also forces all `s_i=f` and

    V=K=W_1 x ... x W_n.

Each `W_i` is self-dual.

If `lambda=2f+1` and `r=2t`, the bound is `nf-(n-2)t`.
If `r=2t+1`, it is `nf+1-(n-2)t`. Dimension `nf+1` therefore forces
`r=1`, all `s_i=f`, and

    K=W_1 x ... x W_n.

Each `W_i` is self-orthogonal. Since every vector in `W_i` is even,
`omega` is in `W_i^perp`. Its weight is odd, so

    W_i^perp=W_i direct-sum span(omega).

Choose `v` outside `K`. The nonzero rank-one symmetric form has
`B(v,v)=1`. Thus every `p_i(v)` is odd and lies in
`p_i(V)=W_i^perp`. It has the form `omega+w_i`, with `w_i` in `W_i`.
Subtract the tuple `(w_1,...,w_n)` in `K`. This proves

    V=K direct-sum span(Omega).

### The row spaces must agree

Choose distinct rows `i,j,k`. Directions supported only in row `i`
and only in row `j` belong to `K`. Apply their second difference to
the equality between the phase at `e_i+e_j+e_k` and the phase at
`e_k`. The latter row does not change. The former gives

    2 w_i.w_j = 0 mod 4.

Therefore `W_i` is perpendicular to `W_j` for every pair of rows.
This is the step that needs a third row.

In even width, `W_j` lies in `W_i^perp=W_i`, so the spaces agree.
In odd width, it lies in `W_i+span(omega)`. The even vectors of that
space are exactly `W_i`, so the spaces again agree. Denote their
common value by `W`.

### The row offsets must agree

Directions in a single row belong to `K`. The other rows stay fixed,
so every `a_i+W` has one constant weight residue `d`, equal for all
rows. Since `W` is self-orthogonal, the map

    q_W(w)=wt(w)/2 mod 2

is linear on `W`. A coset `a+W` has constant weight modulo four if
and only if

    a.w=q_W(w) for every w in W.                         (1)

The solution set of (1) is one coset of `W^perp`.
In even width, `W^perp=W`, so there is only one such `W`-coset.
Every row has that same offset coset.

In odd width, there are two such cosets, exchanged by adding `omega`.
Their weight residues are `d` and `lambda-d`. These are different
because `lambda` is odd. Equal row residues therefore select the same
coset in every row. This proves the required form of `A+V`.

Conversely, an odd sum of elements from one coset `a+W` stays in that
coset. The same holds for `a+omega+W`. Both displayed constructions
therefore lie in `S_n` and have the stated dimensions.

## 2. The phase residues are forced

The classification has a stronger consequence. For every maximal
self-orthogonal `W`, its constant-weight coset has residue

    f mod 4                      if lambda=2f,

and its two constant-weight cosets have residues

    f and f+1 mod 4              if lambda=2f+1.

To prove this, sum `i^wt(x)` on a coset `b+W`. The sum is

    i^wt(b) sum_(w in W) (-1)^(q_W(w)+b.w).

The inner sum is zero unless (1) holds; then it is `2^f`.
The full sum on `F_2^lambda` is `(1+i)^lambda`.

In even width, exactly one coset contributes. Hence
`2^f i^d=(1+i)^(2f)=2^f i^f`, which gives `d=f mod 4`.
In odd width, the two nonzero contributions give

    i^d+i^(lambda-d)=i^f(1+i).

The four possible residues show that the two residues are exactly
`f` and `f+1`. No classification of binary codes is required.

Thus every even-width sector of maximum dimension is contained in
`S_(n,f)`. Every odd-width sector of maximum dimension uses only the
two preferred residues `f` and `f+1`.

## 3. A sharp fixed-residue refinement

For `lambda>=3`, define

    kappa_lambda(d)=f    for the preferred residue or residues above,
                    f-1 otherwise.

For `lambda=1`, only residues 0 and 1 occur, and both have value zero.
For `lambda=2`, residues 0,1,2 have values 0,1,0; residue 3 is empty.

For every nonempty fixed residue and every `n>=1`, the largest affine
dimension in `S_(n,d)` is exactly

    n kappa_lambda(d).                                  (2)

Indeed, each row projection of such an affine set is a constant-weight
coset. Its direction is self-orthogonal by second differences. Its
dimension is at most `f`. If the dimension is `f`, the Gauss-sum
argument forces a preferred residue. This proves the upper bound by
the injective combined row projection.

For attainment, use the same constant-weight coset in all rows.
Let `D_j` be the pair-repetition code of length `2j`, with offset
`a_j=(10)^j`. Its coset has weight exactly `j`.

- The preferred residues use `a_f+D_f`, with a fixed last bit in odd
  width.
- In even width, residues `f-1` and `f+1` use `a_(f-1)+D_(f-1)` and
  two fixed bits, respectively 00 or 11.
- The remaining even-width residue `f+2` uses
  `(a_(f-2)+D_(f-2)) x {0000,1111}`. Its dimension is `f-1` and its
  residue is `f-2=f+2 mod 4`. This case requires `f>=2`.
- In odd width, the other two residues use `a_(f-1)+D_(f-1)` and three
  fixed bits, respectively 000 or 111.

These constructions also cover the stated nonempty small-width cases.
Equation (2) is a dimension statement. It does not classify every
set that attains a nonpreferred fixed-residue bound.

## 4. Number of sectors of maximum dimension

For `n>=3`, each maximal self-orthogonal row code gives exactly one
maximum-dimension affine sector. In even width its constant coset is
unique. In odd width its two constant cosets give the same union.
The code is recovered from the radical of the sector's direction,
so distinct codes give distinct sectors.

For `lambda=2f`, let `E=omega^perp` be the even-weight subspace.
Every self-dual `W` contains `omega`. The quotient
`E/span(omega)` is symplectic of dimension `2f-2`, and
`W/span(omega)` is a Lagrangian subspace in it.
For `lambda=2f+1`, `E` itself is symplectic of dimension `2f`, and
`W` is a Lagrangian subspace in it.

The number of Lagrangian subspaces in symplectic dimension `2g` is
`product_(j=1)^g (2^j+1)`. One proof counts pairs consisting of such
a subspace and a nonzero vector in it. For each vector, quotient by
its line in its perpendicular space. This gives the recurrence
`N_g(2^g-1)=(2^(2g)-1)N_(g-1)`, with `N_0=1`.

The numbers of maximum-dimension affine sectors are therefore

    product_(j=1)^(f-1) (2^j+1)       if lambda=2f,
    product_(j=1)^f     (2^j+1)       if lambda=2f+1.

An empty product is one.

## 5. Boundaries and exact checks

The third-row hypothesis is necessary. For `n=2, lambda=2`, the
linear set `{(x,x):x in F_2^2}` has dimension two and lies in `S_2`.
Its row projection has dimension two. It cannot be a product of
one-dimensional self-dual row codes. The even rank bound has an
equality plateau when `n=2`.

There is no such plateau for `n=3`. The proof above applies to that
case. It also applies to `lambda=1`: `W=0` and the only maximum set
is the common all-row bit.

The independent checker exhausts all 28 affine lines for
`n=3, lambda=1`, and all 11,160 affine sets of dimension three for
`n=3, lambda=2`. Their equality cases match the theorem. It also
enumerates all self-orthogonal row subspaces through length six,
checks the sharp fixed residues, and checks the 38 maximal row codes
and their sector counts. These finite checks support the proof; they
do not replace its argument for general dimensions.

This result classifies affine parts of the sufficient all-odd sector
`S_n`. It does not classify a larger sector defined by only the actual
supplier's port labels. It supplies no projector stream, native
access map, controller, complete precision invoice, or supplier gain.

Proof and exact checks: OpenAI Codex under the user's direction.
The parent proposed the rigidity statement. The correlated-access
packet supplies the common-form dimension bound. No producer file
was changed. No PR, commit, or push was made. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
