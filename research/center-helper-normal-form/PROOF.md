# A legal helper basis and exact three-step chains

Prepared for Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

## Source interface and real common charts

Assume the exact PR4694 interface M on 640 arbitrary inputs. Let x=(X,Y,h),
with 408 original helpers, and let z contain the eight retained centers:

    x_out = A x + B z,       z_out = R_X X + R_H h + z,
    A(X,Y,h)=(X,Y+X,h).

B has rank eight and is supported only on Y. All 106 helper columns used by
R_H have birth chart 0 and complete output chart 1. The complete cold pool
contains 326 helpers. The frozen source has no endpoint adapter on these
helpers, so the charts used by the boundary circuit are actual common charts.
The source supplies their identical exact operator F=C^tensor(9f), for each
positive column width f, under its retained native/all-width hypotheses.

## Exact sparse basis

Let J be the eight pivot roles in RESULT.json and let N be the other cold
roles. Set L=R_H[:,J]. Exact rational elimination gives det(L)=64 and pivots
2,2,1,4,1,2,1,2. In particular every division used in the emitted algorithm
is a dyadic unit. Define h=P u by

    h_N = u_N,
    h_J = L^-1 (u_J - R_H[:,N] u_N).

Then R_H P u=u_J. This is an invertible change, not a restriction or a clean
input promise: all 408 original helper inputs remain arbitrary. The verifier
emits the gathering subtractions and the eight-row elimination as 379 actual
ADD/SCALE gates. Row exchanges use three ADDs and a sign scale. All operands
are cold helpers at chart 0. Reverse the gates and invert each to emit P^-1
in 379 gates at output chart 1. Their coefficients and both inverse identities
are checked exactly.

Because P acts on field labels and F is the same operator on each cold field,

    P^-1 diag(F,...,F) P = diag(F,...,F)

at every width f. This is ordinary commutation of a scalar matrix with an
identical direct-sum operator, not tensoring a sum or assuming equal ranks
imply equal physical jobs. Other helper jobs are untouched. All monomial
normalizers and source physical phase conventions remain the source's.
The entry and exit circuits add no recursive Gaussian request. Fixed scalar,
route and storage work is real finite work and is not claimed to cost zero.

Conjugating M only on these helper coordinates therefore preserves A, B and
all helper targets, while replacing R_H by the coordinate selector E_J.
Data observations R_X and all center input columns are exactly retained.
The native replay checks this full identity on all 640 columns and also on
the true gatewise raw inverse transpose. It retains every paid source call.

## Eight actual chains and the scalar Jordan type

Put K=M_new-I. On the three sectors (old fields, centers),

    K = [[S,B],[R_new,0]],   S=A-I,
    K^2 = [[B R_new,0],[0,0]],   K^3=0.

S maps the 112 X coordinates bijectively to Y. B is supported on Y, and
R_new reads only X and the eight distinct pivot helper inputs. Thus the image
of K contains all 112 Y directions (choose X and cancel R_X X with the pivot
helpers) and all eight center directions (choose pivot helpers). It is
contained in their sum. Hence rank(K)=120.

R_new is surjective because of its helper selector. B is injective, so
rank(K^2)=rank(B R_new)=8. For a nilpotent operator of index at most three,
the number of size-three blocks is rank(K^2), and the number of size-two
blocks is rank(K)-2 rank(K^2). The remaining dimension gives 408 size-one
blocks. This proves the stated Jordan type over Q, not only numerically.

More concretely, for each pivot helper e_hj,

    K e_hj = e_zj,       K e_zj = B e_j,       K B e_j = 0.

Their 24 vectors are independent: the first eight lie in the helper sector,
the next eight in the center sector, and the last eight are the independent
Y columns of B. The verifier checks those exact sparse columns. It does not
claim that converting all Y/data fields to a full Jordan basis is physically
free; those output charts differ.

## Verification and remaining bottleneck

The frozen source engine is reused unchanged for actual native replay; it is
not relabeled an independently written evaluator. Separate sparse matrix
composition checks the basis inverses, conjugation and both operator inverses.
Every native scalar chart and paid rank is checked. Complete positive scalar
envelopes for primal and raw dual remain below 2^192, without a new rounded
recursive induction claim. Controls reject a changed header sign, an omitted
output inverse and an output circuit moved to the wrong chart.

The eight center outputs still contain R_X X, and incoming z still enters Y.
Thus eight normalized observations are not eight independent Gaussian jobs.
No contraction, complete controller, uniform compiler, new BIT endpoint,
outer saving or multiplication theorem is established by this basis change.
