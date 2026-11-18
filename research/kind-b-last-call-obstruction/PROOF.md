# A kind B part cannot finish by one last call alone

## Statement and model

Work in the formal group algebra `Q[G]`, where `G=Sp(2m,2)` and `m>=3`. Write labels as `(x,z)` and let the raw Lagrangian be `L={x=0}`. Let `P=Stab_G(L)`. Free combinations act on the left and lie in `Q[P]`. A paid call is a symplectic transvection with normal outside L. Calls are involutions. Products act right to left.

The frame of a term g is `g^-1 L`. Its level is `ell(g)=m-dim(L intersection g^-1 L)`. Two terms have the same frame exactly when `g h^-1` is in P. Level is invariant under left and right multiplication by P. It is also unchanged under inversion. We can therefore compute level as the dimension of the horizontal image `X(gL)`, where X projects `(x,z)` to x.

Let D,W,T be first, shared and final calls, and suppose `ell(TWD)=3`. Set

```text
M = WD,      E = W gamma,      y = M+cE,
gamma in P, c in Q with c != 0, E not in PD,
U = span_Q {p, pD, py : p in P}.
```

The nonplain condition `E not in PD` excludes a free image of the first-call output. E has level one, so it is already outside P. The finishing condition in [Jacob Sussman's PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629) is `TM in U+TU`. This allows free preparation of the last call and free additions of earlier arrays to its output. It permits no free map on the output itself and no access to another last-call output.

**Theorem.** Under these hypotheses, `TM` is not in `U+TU`, at every address width and every nonzero rational c.

The source checked this nonfinishability at three address bits and three coefficients. This proof includes arbitrary spare address bits and all nonzero rational coefficients. It does not exclude a general two-in-five program, post-call free processing, joint decoding, extra terms, or phase-sensitive engine programs. There is no new kappa.

## A horizontal-plane fact

For a call with normal u, write d=X(u). Acting on L, the call produces horizontal component `d*(d dot z)`. If two calls have linearly independent horizontal normals d,w, their product maps L to a subspace whose horizontal image is exactly `span(d,w)`. The two coefficients are independent linear forms: applying the second call and then the first makes a triangular change to `d dot z` and `w dot z`. No condition on the vertical parts or commutation of the calls is needed.

Let d,w,t be the horizontal normals of D,W,T. The horizontal image of `TWD L` is contained in `span(d,w,t)`. The level-three hypothesis thus makes d,w,t linearly independent. In particular `ell(M)=ell(TW)=2`. If gamma is free, it has block form `[[A,0],[C,A^(-T)]]`, with A invertible, and sends every horizontal image V to AV.

We will use one consequence. If `ell(D gamma D)=1`, then `A d=d`. Indeed `D gamma D` has the same image of L as the two calls `D` and `gamma D gamma^-1`. Their horizontal normals are d and Ad. If they were distinct, they would be independent over F2 and the preceding fact would give level two.

## The first two forced coordinates

Write `g0=TM` and `g1=TE`. Their levels are three and two. The available singleton columns have support in `P,PD,TP,TPD`; their levels are at most two. The available binomial columns are `py` and `Tpy` for p in P.

The only column touching g0 is `Ty=g0+c g1`. Old first endpoints pM have level two and old second endpoints pE have level one. A paid first endpoint equals g0 only for p=1. A paid second endpoint equals g0 only if `M E^-1` is free, which would give M and E the same level.

At g1, earlier singletons in P or PD are excluded by level. Membership in TP would make E free. Membership in TPD would put E in PD, contrary to the nonplain condition. An old second endpoint has level one. A paid first endpoint at g1 would require `E M^-1` free. The paid second endpoint at g1 again comes only from Ty.

There is one possible additional column: an old first endpoint at g1 exists exactly when

```text
q = TE M^-1 is in P.
```

If q is not free, define a linear functional on the formal basis by `lambda(g0)=c`, `lambda(g1)=-1`, and zero elsewhere. It kills every available column but takes the nonzero value c on the target. This proves the theorem in that case.

## The third coordinate cannot be cancelled

Suppose q is free. Put `g2=qE` and `a=E M^-1`. Then `q=Ta`, g2 has level one, and `qy=g1+c g2` is the sole new column at g1. We show that no further column touches g2.

An old first endpoint has level two, and the only old second endpoint at g2 is qE itself. A paid second endpoint at g2 would require `Tq=a` free, which is impossible since M and E have different levels. A paid first endpoint at g2 would require `a^2` free. In that case `T a^-1=q a^-2` would be free. This is `TM E^-1`, which would make the level-three target TM have the same frame as level-one E. Thus that paid endpoint is absent.

No singleton in P or PD can equal g2: its level is one, q is free, and E is not in PD. For a singleton in TP, we would need

```text
Tg2 = aE = W gamma D gamma in P.
```

Right multiplication by the free gamma inverse would put `W gamma D=ED` in P, again contrary to the nonplain condition.

It remains to exclude TPD. Suppose `Tg2 D=W gamma D gamma D` were free. Its action on L would give

```text
D gamma D L = gamma^-1 W L.
```

The right side has level one. The horizontal-plane fact therefore gives `Ad=d`. On the other hand q is free, and `q=T W gamma D W`. Its action on L gives

```text
gamma D W L = W T L,
A span(d,w) = span(w,t).
```

The left plane contains Ad=d. The right plane cannot contain d because d,w,t are independent. This is a contradiction. It excludes the last possible singleton at g2.

Consequently the only columns incident to `{g0,g1,g2}` are `g0+c g1` and `g1+c g2`. Define

```text
lambda(g0)=c^2,    lambda(g1)=-c,    lambda(g2)=1,
lambda(g)=0 for every other formal term g.
```

Both columns have value zero. Every other available column has disjoint support, so it also has value zero. But the target has value `c^2`, which is nonzero. This proves the theorem. The two- and three-coordinate functionals are explicit separating certificates; the proof does not depend on an orbit size or enumeration of P.

## Exact checks

The checker uses binary row matrices. It constructs all 10752 elements of the three-bit parabolic group from all invertible A and symmetric S, with lower block `A^(-T) S`. Every matrix is unique and satisfies the symplectic identity. The nonplain condition excludes 768 elements. It tests every one of the 32 final calls that raises `WD` to level three for each of the remaining 9984 elements. This covers 319488 part/call pairs for the fixed first and shared calls D and W with horizontal normals 1 and 2.

For each pair the checker enumerates every possible old or paid column incident to each selected coordinate, and all four singleton families. It verifies the separating functional as a polynomial in c. Thus these finite certificates cover every nonzero rational coefficient, not just a sampled list. There are 315392 two-coordinate certificates and 4096 three-coordinate certificates. The universal width and arbitrary-call statement follows from the written proof, not from this normal-form census.

A separate check constructs the whole right-multiplication orbit through TM with step `M^-1 E`. Every binomial stays within such an orbit. It retains every available singleton and binomial in that orbit and solves the rational span problem for the singleton target. Eighty contracts cover both certificate types, five coefficients, widths three through six, and free conjugations that mix the core with spare coordinates. The longest tested orbit has length four. These are selected checks, not a complete wider-width census.

Another 240 checks vary all three call directions and the free map at widths four through six. All have the required independent horizontal directions; 115 have noncommuting first and shared calls. These sampled cases all use the two-coordinate separator. They complement the wider three-coordinate examples above.

Five nonzero coefficients on a plain extra term give positive finishing controls. A zero coefficient and a final call that fails the level-three premise also give positive controls. Deleting the third weight from a three-coordinate separator is rejected. Two rational-elimination controls check a small full-rank and a deficient system. [Receipt and examples](RESULT.json) · [Verifier](verify.py)

## Credit and limits

Prepared by Ali Romman with substantial OpenAI Codex assistance. Jacob Sussman supplied the model, the finite kind B nonfinishability observation and the source boundaries in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629), [exact source](https://github.com/jacobalansussman/integer-mult-bounds/blob/c2a2131e7dba35f9396b16588e125a7e8b5fab8e/research/complex-m3-shared-call-finish-or-remove/README.md). Nick Petalas's [kind A finishing proof](https://github.com/petalas/integer-mult-bounds/blob/f642d2740265a61f8ac64b3a087f0118382c56e3/research/kind-a-last-call-coset/README.md) in [PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649) supplies a related coset method. The [kind B removal proof](https://github.com/aliromman/integer-mult-bounds/blob/7c3b229d0788d6e980f75cbaabe07287899263a2/research/kind-b-frame-swap-removal/PROOF.md) in [PR #7679](https://github.com/CrocSwap/integer-mult-bounds/pull/7679) supplies the related endpoint method. Its binary matrix and rational-span routines are reused here; the finishing separator, horizontal-plane proof and census are new. No source file is read at run time. New work is Apache-2.0.

The finite source already observed zero finishable parts for its tested coefficients. The new result is the proof at all widths and all nonzero rational coefficients. It remains a theorem about formal terms with Pauli phases removed. No paid native word, physical decoder, precision bound, restoration protocol, complete invoice or selected-assumption discharge follows. The selected frontier and its five assumptions remain unchanged. Independent human and formal-kernel review are unclaimed.
