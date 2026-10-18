# Complex single lifts have real representatives with identical supports

This is written mathematics, not a proof-assistant formalization. The new
transfer lemma is independent of E8 geometry. Its P112 application inherits
the real single-lift theorem of Mihir Srivastava (@mihir-s-05), [#845](https://github.com/CrocSwap/integer-mult-bounds/pull/845),
whose exact sources and finite premises are pinned in [SOURCES.json](SOURCES.json).

## Support transfer for any finite real matrix

Let `X` be a real `n x m` matrix with columns `x_j`. The identity

    XX^T = sum_j x_j (x_j - a_j z)^T + (Xa) z^T                 (1)

holds for `a in C^m`, `z in C^n`. Transpose in this formula is algebraic;
there is no complex conjugation. For a vector, `supp` is its set of
nonzero coordinates.

**Theorem.** For every such `a,z`, there are `b in R^m`, `w in R^n` with

    supp(b) = supp(a),      supp(w) = supp(z),
    supp(Xb) = supp(Xa),
    supp(x_j - b_j w) = supp(x_j - a_j z)   for every j.       (2)

Thus every individual rank-one term in (1) has the same reader and source
supports in the real identity determined by `b,w`. No rank, sign, or
integrality hypothesis on `X` is needed.

**Proof.** Form the finite set `W` of all nonzero values among

    a_j, (Xa)_i,
    1/z_i                         (z_i != 0),
    a_j - X_ij/z_i                 (z_i != 0, every j).

Put `f_t(u) = Re(u) + t Im(u)`. A nonzero `u` excludes at most one real
parameter `t`, since this is a nonzero polynomial in `t` of degree at
most one. With `N = |W|`, at least one integer in `{0,...,N}` is allowed.
Choose such a `t` and write `f=f_t`. Set

    b_j = f(a_j),
    w_i = 0                       if z_i = 0,
    w_i = 1/f(1/z_i)              otherwise.                  (3)

All denominators are nonzero. The first and third parts of `W` preserve
the supports of `a` and `z`. Real-linearity, and the assumption that `X`
is real, give `Xb=f(Xa)` entrywise. The second part of `W` preserves this
support. When `z_i=0`, both residuals in (2) equal `X_ij`. Otherwise

    X_ij - b_j w_i
       = -f(a_j - X_ij/z_i) / f(1/z_i).                      (4)

The fourth part of `W` makes (4) zero exactly when
`a_j-X_ij/z_i=0`, equivalently `X_ij-a_j z_i=0`. This proves (2).
Zero vectors and individual zero coordinates are included; if `W` is
empty take `t=0`. The finite-avoidance argument also covers transcendental
complex coefficients. It does not presume an exact numerical oracle for
arbitrary computable or noncomputable real inputs. QED.

For rational real `X` and Gaussian rational `a,z`, (3) is an effective
exact rational construction. There are at most `m+2n+nm` nonzero exclusions
before deduplication; for P112 this is **1128**, so testing integers
`0,...,1128` always suffices. The shipped implementations usually need
far fewer, but do not assume a smaller bound.

The reciprocal in (3) matters: projecting `z` directly does not preserve
products. Omitting the fourth part of `W` preserves inclusion of each
residual support, but need not preserve equality. For example `X=[1]`,
`a=1+i`, `z=1`, `t=0` turns the nonzero residual `-i` into zero. These
failure modes have exact executable controls.

## P112 consequence: same attainable nine-term copy-cost vectors

Use #845's real `112 x 8` P112 matrix `X`, with `XX^T=2G`, and its binary
labels `l_i` and dual labels `v_i`. Extend its definition to complex
vectors without changing the binary pairing:

    beta(d,s) = rank_F2 (v_i dot l_u)_(i in supp(d),u in supp(s)).

This is a **support-only algebraic cost**. It is not a rank over the
complex field or a physical bit-width estimate. Theorem (2) preserves
every support pair and hence every individual beta. Conversely every
real lift is a complex lift. Therefore the set of attainable ordered
nine-term beta vectors is the same over `R` and `C`.

The predecessor's all-real theorem gives

    sum_(j=0)^7 beta(x_j, x_j-a_j z) + beta(Xa,z) >= 64       (5)

for **all complex `a,z`**. Equality is attained at `z=0`. There are also
nonzero ninth terms attaining equality: take any nonzero complex `a_0`,
set every other `a_j=0`, and `z=x_0/a_0`. Term zero then vanishes and the
ninth term replaces it at cost eight; the other seven terms cost eight
each. The minimum and priority for the coordinate value 64 remain with
the predecessor work, especially #620. The new result removes #845's
explicit exclusion of complex scalar coefficients.

## Which nine-term factorizations this covers

For the P112 matrix, real rank eight persists over `C` by a nonzero real
minor. Suppose an exact identity on **all matrix entries** has the form

    XX^T = X T^T + d z^T.                                   (6)

If `z!=0`, reduce each column modulo `col_C(X)`. At any index with
`z_i!=0`, this forces `d` into `col_C(X)`. Write `d=Xa`; injectivity of
`X` in (6) gives `T=X-z a^T`, so (5) applies. If `z=0`, injectivity gives
`T=X`, and the ninth term costs zero regardless of `d`. Nonzero complex
rescalings of the first eight reader columns may be absorbed in their
source columns without changing supports. Symmetry of the inherited
binary pairing gives the corresponding transposed statement with the
coordinate source columns retained.

The theorem does not treat changed coordinate readers, multiple added
totals, masked matrix equality with free corrections, a complex-valued
underlying `X`, or nonlinear/interacting delivery programs. It neither
characterizes arbitrary rank-one decompositions nor proves that real and
complex matrix factorizations in general have the same support patterns.

## Accounting and inherited obligations

The investigated mechanism changes the scalar domain of a single added
total, hoping to lower copied-information cost through new cancellations.
Before attempting a physical implementation, grant **zero additional
cost** to preparing the total, source access, frame changes, copying
infrastructure, cleanup/restoration, and recursive children. Even this
optimistic accounting cannot lower (5); in fact it cannot produce a new
ordered copy-cost vector at all. Thus no improved complete-cost candidate
was advanced or priced as a new kappa.

This conclusion only blocks the proposed support-based copy saving. The
real representative may have different coefficient sizes, preparation
circuits, precision costs, frame feasibility, or scheduling properties.
No efficiency-preserving physical compiler follows from (3), and benefits
in those other expenses remain open. The physical interpretation of beta
inherits DreamingOfClouds' #446 Theorem C separate-total/drop-free gather
and copy-tree assumptions. The new support-transfer theorem does not need
that interpretation; applying it to multiplication does.

The base-selected #942 conditional construction, its bit supplier, and
its all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape and analytic obligations are unchanged. No formal proof
of the full integer-multiplication theorem or new exponent is claimed.
