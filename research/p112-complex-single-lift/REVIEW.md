# Independent AI review of the complex single-lift extension

This is an independent reasoning review by a delegated OpenAI Codex agent,
prepared on 2026-10-13. It is not human review or a proof-assistant
formalization. The review inspected the predecessor's `PROOF.md` and
`geometry.py`, together with this contribution's `CLAIM.md`. It accepts
the predecessor's stated exact finite premises; this note does not claim
to have independently rerun their executable certificates.

## A stronger and simpler transfer lemma

Let `X` be any finite real `n` by `m` matrix, with columns `x_j`. For every
`a in C^m` and `z in C^n`, there exist `b in R^m` and `w in R^n` such that

    supp(b) = supp(a),
    supp(w) = supp(z),
    supp(Xb) = supp(Xa),
    supp(x_j - b_j w) = supp(x_j - a_j z)  for every j.

Thus every support pattern of this one-lift family over `C` is already
attained over `R`. This is stronger than the support inclusion needed
for a monotonic-cost lower bound. It does not require the P112 alphabet,
the finite binary sign census, or any rank hypothesis on `X`.

**Proof.** Let `W` be the finite collection of the following nonzero
complex numbers, omitting every zero entry:

1. all `a_j`;
2. all `(Xa)_i`;
3. all `1/z_i` for `z_i != 0`;
4. all `a_j - X_ij/z_i` for `z_i != 0` and all `j`.

For a real parameter `t`, put `f_t(u) = Re(u) + t Im(u)`. For each nonzero
`u`, at most one real value of `t` makes `f_t(u)=0`. Choose `t` outside
the finite set of forbidden values. Such a `t` can even be an integer:
if `W` has `N` members, at least one of `0,1,...,N` is allowed. This
argument does not assume that the entries of `a` or `z` are algebraic
or computable. If `W` is empty, choose `t=0`.

Set `f=f_t`, `b_j=f(a_j)`, and

    w_i = 0                  if z_i = 0,
    w_i = 1/f(1/z_i)        if z_i != 0.

The denominators are nonzero by construction. The first and third
parts of `W` preserve the supports of `a` and `z`. Because `X` is real
and `f` is real-linear, `Xb=f(Xa)` entrywise; the second part of `W`
preserves that support. If `z_i=0`, both residual entries are `X_ij`.
If `z_i!=0`, real-linearity gives

    X_ij - b_j w_i
      = [X_ij f(1/z_i) - f(a_j)] / f(1/z_i)
      = -f(a_j - X_ij/z_i) / f(1/z_i).

The expression vanishes if and only if `a_j-X_ij/z_i=0`, by the fourth
part of `W`. This is equivalent to `X_ij-a_j z_i=0`, proving exact
preservation of every residual support. The cases `a=0`, `z=0`, and
individual zero coordinates are included. QED.

The fourth part of `W` can be omitted if only residual support inclusion
is required. In that version, a complex cancellation remains a real
cancellation, while additional real cancellations are harmless for
support-monotone costs.

## Consequence for the inherited P112 pairing-rank cost

The predecessor defines `beta(d,s)` from the binary pairing matrix on
the supports of `d` and `s`. It depends only on those supports, whether
the scalar entries are real or complex. Deleting support indices can
only decrease its rank, since the smaller matrix is a submatrix.

Apply the transfer lemma to the real P112 matrix `X`. Every one of the
nine pairing-rank costs at complex parameters `(a,z)` is exactly equal
to its cost at real parameters `(b,w)`. The predecessor theorem for
all real parameters therefore yields

    sum_j beta(x_j, x_j-a_j z) + beta(Xa,z) >= 64

for all complex parameters. Conversely, real parameters are complex
parameters, so the attainable nine-term cost vectors, not merely the
minimum total cost, coincide for this family over the two scalar
domains. This does not assert any correspondence for numerical source
values, physical implementations, or multiple simultaneous lifts.

## Characterization of exact nine-term factorizations

Suppose the first eight reader columns are the columns of `X`, and an
exact algebraic-transpose factorization over `C` satisfies

    XX^T = X T^T + d z^T.

The real full column rank of `X` persists over `C`, for example by its
nonzero integer minor. If `z!=0`, pass each column of the equality to
`C^112 / col_C(X)`. The result is `[d] z_i=0` for every `i`; choosing
one nonzero `z_i` proves `d` belongs to `col_C(X)`. Write `d=Xa`.
The identity then becomes

    X (X^T - T^T - a z^T) = 0.

Injectivity of `X:C^8 -> C^112` gives `T=X-z a^T`, exactly the family
covered above. If `z=0`, it gives `T=X` directly and the ninth term
has cost zero, regardless of `d`. Independent nonzero complex
rescalings of the eight coordinate readers can be absorbed into
their source columns; all relevant supports are unchanged.

Everything uses ordinary algebraic transpose. No assertion about a
Hermitian factorization is required. Symmetry of the inherited binary
pairing makes `beta(d,s)=beta(s,d)`, so transposing an exact identity
gives the corresponding obstruction with the coordinate source
columns retained.

## Audit of the initially proposed signed-class route

The route in the claim also appears sound, conditional on the inherited
finite certificates, with one detail needing an explicit sentence.
For `z_i!=0`, all selected indices obey `X_ij=a_j z_i` with nonzero
`X_ij in {+1,-1}`; their coefficients are therefore in a single
equality-up-to-sign class. The direct-sum kernel gives even total
selection parity, so each class satisfies the inherited sign equations.
For `z_i=0`, selected coordinate entries are zero. Classes of sizes
2 through 7 are killed by the inherited full-rank sign systems. A
singleton class is killed by `beta(x_j,x_j)=8`: its sign equations
force its vector in `V_j` to annihilate every label on `supp(x_j)`.
If all eight coordinates form one class, incompatible values among
`X_ij epsilon_j` in the inherited exceptional kernel still cannot
equal the single complex value `alpha z_i`. Nonzero rational minors
also remain nonzero over `C`.

The transfer lemma removes the need to repeat that case analysis or
present a new finite sign certificate for the extension. The new
mathematical premise is the explicit real-linear support transfer;
the value 64 and the P112 geometry remain credited to the predecessor.
