# Rational witnesses suffice for fixed-reader single lifts

This is a written proof, not a proof-assistant formalization. It generalizes
@woklerx's retained complex-to-real reciprocal-projection argument. The real
P112 obstruction is due to Mihir Srivastava, PR845. Exact source pins and
credit are in SOURCES.json and NOTICE.md.

## Descent over an infinite base field

Let F be an infinite field, E a field containing F, and X an n by m matrix
over F, with columns x_j. For a in E^m and z in E^n, consider the identity

    XX^T = sum_j x_j (x_j - a_j z)^T + (Xa) z^T.             (1)

Transpose is algebraic. No conjugation is used. There exist b in F^m and
w in F^n such that

    supp(b) = supp(a),          supp(w) = supp(z),
    supp(Xb) = supp(Xa),
    supp(x_j - b_j w) = supp(x_j - a_j z), for every j.      (2)

Thus each of the m+1 rank-one terms has exactly the same reader/source
support pair in the two identities. Every cost determined solely by those
support pairs agrees term by term.

To prove this, collect the distinct nonzero elements among

    a_j, (Xa)_i, 1/z_i, a_j - X_ij/z_i,                     (3)

where the last two expressions are included only when z_i is nonzero.
Call this set W and its size N. Let V be its finite-dimensional F-span.
Write d = dim_F V. If W is empty, a and z are zero, and b=w=0 works.

Otherwise choose a basis e_0,...,e_(d-1) of V. For t in F define

    f_t(sum_h c_h e_h) = sum_h c_h t^h.                     (4)

For every u in W, f_t(u) is a nonzero polynomial in t of degree at most
d-1. It has at most d-1 roots. At most N(d-1) elements of F are forbidden.
Since F is infinite, some t avoids them all. Fix such an F-linear f=f_t.
The argument needs only a linear map on V; it does not require a field
homomorphism or a map defined on all of E.

Set b_j=f(a_j), and set w_i=0 when z_i=0, otherwise

    w_i = 1/f(1/z_i).                                      (5)

All denominators are nonzero. The first and third groups in (3) preserve
the supports of a and z. Since X has coefficients in F, Xb=f(Xa), entry
by entry, so the second group preserves its support. For nonzero z_i,

    X_ij - b_j w_i
        = -f(a_j - X_ij/z_i) / f(1/z_i).                    (6)

The fourth group makes this zero exactly when X_ij-a_j z_i=0. For z_i=0
both residual entries are X_ij. This proves (2). Identity (1) holds by
distributivity over both fields. No multiplicativity of f was assumed.

The same proof works over a finite F when |F| > N(d-1). This is a
sufficient condition for this argument, not a necessary condition for a
particular lift to descend.

## Rational consequence and effective scope

Take F=Q and E=C. If X is rational, every complex single lift, including
ones with irrational or transcendental coefficients, has a rational
representative with the identical ordered term-support pairs. Conversely,
every rational lift is a complex lift. Their attainable support-only cost
vectors are therefore equal. This also includes every intermediate field
Q contained in E contained in C.

This strengthens complex-to-real support transfer when X is rational.
The finite-dimensional Q-span in the proof exists even for transcendental
inputs. It does not furnish an algorithm for discovering exact rational
relations between arbitrary black-box complex numbers.

When coordinates in a known finite-dimensional extension are supplied
exactly, the construction is effective. One may use any finite-dimensional
F-space of dimension D containing W, not necessarily its minimal span.
The same polynomial argument then uses N(D-1). Over Q, one of the integers
0,...,N(D-1) is allowed. For W empty choose t=0. These bounds concern the
projection parameter; they are not bounds on numerator sizes, denominators,
precision, or physical circuit cost.

The pinned P112 coordinate matrix has integer entries. Its fixed eight-reader
single lifts therefore have the same ordered nine-term pairing-rank cost
vectors over Q, R, and C. Mihir Srivastava's retained real theorem gives
the inherited floor 64, attained by z=0. This contribution neither reproves
its geometric finite premises nor changes that floor. It justifies restricting
the coefficient field to Q when enumerating support patterns in this class.
It gives no finite bound on rational heights, so such an enumeration is
not a terminating exhaustive search.

## A minimal finite-field boundary

Let F=F2, E=F4=F2[alpha]/(alpha^2+alpha+1), X=[1], and a=z=alpha.
Then a, z, Xa, and the residual 1-a*z=alpha are all nonzero.
Any F2 representative with the same a and z supports must have b=w=1.
Its residual 1-b*w is zero, so descent fails. The single original term
and the added term are both nonzero over F4; no F2 lift preserves that
pair of term supports. The matrix is already 1 by 1.

Here W={1,alpha,alpha+1}, N=3, d=2. The sufficient size condition fails.
The certificate checks the F4 arithmetic and all four F2 choices for b,w.
This is a counterexample to unconditional descent over finite fields, not
a counterexample to the infinite-field theorem or the P112 floor.

## Scope and cost boundary

The proof retains the original reader columns and exactly one added total.
It permits arbitrary coefficients in the extension but does not address
several added totals, altered readers, conjugate-transpose decompositions,
or coefficient-sensitive costs. The projection need not preserve signs,
norms, integrality, bounded denominators, or a physical instruction word.

No complete supplier is proposed. The optimistic support-only cost is
exactly preserved, so this mechanism offers zero improvement in that cost.
Preparation, restored scratch, decoder execution, precision, tape and
recursive hosting have not been priced or implemented. A paid supplier
claim would require all of them, in addition to the retained all-size,
common-label, analytic and bit H1-H5 assumptions. The selected exponent is
unchanged.
