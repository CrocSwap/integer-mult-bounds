# Exact integer-pair elimination for the retained K-rank calls

Let `K=Q(w)` with `w^2+w+1=0`. A rational pair `(a,b)` represents `a+bw`.
The polynomial is irreducible over Q, so a pair is zero exactly when both
components vanish, and every nonzero pair is invertible in K.

The adapter changes only calls with `field == 'K'`. The retained Q and F4
implementations, all geometry generation, trace identities, reduction checks,
support samples, fitting identities and negative controls are unchanged.

## Rank-preserving operations

For each input row, multiply by the least common multiple of the denominators
of every rational component. This is a nonzero rational scaling, hence an
invertible row operation over K, and leaves a row of integer pairs. Divide all
its integer components by their positive gcd when that gcd exceeds one. This
is another nonzero rational scaling. A zero row has content zero and stays zero.

At a pivot column, interchange rows to select a nonzero entry `p=a+bw`. For
each lower row whose entry is `f=c+dw`, replace

    row_i <- p*row_i - f*pivot_row.

This operation is invertible over K because `p` is nonzero; no inverse is
actually computed. Using `w^2=-w-1`, one component pair becomes

    (x,y) <- (a*x-b*y-c*u+d*v,
              a*y+b*x-b*y-c*v-d*u+d*v),

where `(u,v)` is the corresponding pivot-row pair. These are exact integer
operations. The pivot column cancels. Previously processed columns below the
pivot are already zero, so replacing the entire prefix by zero does not discard
information. Removing the new row's integer content again preserves rank.

At termination the nonzero rows have distinct leading columns. They are
linearly independent over K; every remaining row is zero. The number of pivots
is therefore exactly the original K-rank. This proves the routine for every
finite rectangular matrix of rational pairs, including empty and singular
matrices, rather than only the finite replay census.

Content reduction is an integer gcd, not reduction modulo a prime and not a
gcd in the Eisenstein ring. Only nonzero rational scaling is needed. The routine
does not return a nullspace or a canonical echelon basis. It makes no claim
about general coefficient-growth complexity or speed on arbitrary matrices.

## Independent check by restricting scalars

Multiplication by `a+bw` on K, in the Q-basis `(1,w)`, has matrix

    [ a   -b  ]
    [ b   a-b ].

Replacing every entry of an `m` by `n` K-matrix with this block gives the same
linear map viewed over Q. Its image is a K-subspace, whose Q-dimension is twice
its K-dimension. Thus the expanded rational matrix has rank exactly twice the
desired K-rank. `independent.py` computes that rational rank by separate
Fraction elimination. It imports neither the retained K-rank routine nor the
new verifier. It exhausts all 2-by-3 and transposed 3-by-2 matrices over four
small pairs, all 2-by-2 matrices over a five-entry alphabet including a rational
denominator case, and bounded rectangular, duplicate-row and large-integer
fixtures: 9,009 matrices in total.

## Source-bound application and limits

`verify.py` authenticates the exact source files before import, observes every
rank call of the original PR2017 replay, and compares all 359 K results against
the new routine without changing the original returned values. It checks that
the input matrices survive unchanged. It then installs the optional adapter
and reruns the complete verifier, requiring identical complete stdout, including
the full JSON receipt and all seven original negative controls. The 311 F4 and
209 Q calls remain delegated to the original implementation.

Controls exercise the K relation, a bad mod-two rank surrogate, floating-point
near-dependence, changed same-object inputs, invalid exact-input forms, and a
wrong K-rank replacement rejected by the original verifier itself. Source
corruption is rejected before retained code import. There is no mathematical
result cache whose stale success could replace execution.

This is replay tooling, not a new Eisenstein cost bound, native compiler or
supplier theorem. Jose Manuel's PR2017 proof and all geometry/decoder lineage
retain credit. Primitive integer-row elimination and restriction of scalars
are standard methods; the useful delta is this measured complete-replay
application with exact retained coverage and an optional runnable adapter.
