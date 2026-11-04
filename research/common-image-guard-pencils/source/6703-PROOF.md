# Strict positive correlation over every finite field

This is a modest sign corollary of Nick Petalas's credited PR4807 formula,
closing its README Open next question2. It supplies no new counting law.
PR4807 already proves the binary sign and explicitly suggests the identity
q*delta-alpha^2=q-1 used below. Its marginal is predecessor PR4227.

## Source model and claim

Let K=F_q, q>=2 a prime power, m>=2. Let a,c be independent columns in
K^m and b a covector satisfying ba=bc=1. Write U=ab,V=cb and the corank-one
complements P=I-U,Q=I-V. Complete equally weighted headers G range over
GL_m(K). Event E_P (respectively E_Q) requires every leading principal
minor of GPG^{-1} (respectively GQG^{-1}) of orders1,...,m-1 to be nonzero.
These are full proper-minor events on the complements, not first-pivot
requests on U,V. Other two-way pairs and restricted headers are outside scope.

We prove

    Pr(E_P and E_Q) > Pr(E_P) Pr(E_Q) = p(q,m)^2.                (1)

The source law and uniform conjugation make both marginals equal to p.
The algebra below holds for all integer parameters q>=2,n>=1; a field/count
interpretation is asserted only for finite-field prime-power q.

## Credited formulas and exact cancellation

Put n=m-1, A=q^2-q+1, D=q^2+(q-1)^3 and x=q^{n+1}. PR4807 proves

    p = (q-1) A^n / [(x-1) q^n],
    J = (q-1)(D^n-A^n) / [(x-1)(x-q) q^{n-1}].               (2)

Those formulas, their common-covector orbit count, dependent-pair subtraction
and finite source censuses are cited premises, not independently recounted
here. In particular the binary sign was already a theorem in that source.
All denominators in (2) and below are positive: q>=2,n>=1 imply x>q>1,
A>0 and p>0. Cancellation gives the exact ratio

    R = J/p^2
      = x(x-1)/[(q-1)(x-q)] * [D^n/A^{2n} - 1/A^n].         (3)

The identity qD-A^2=q-1>0 shows D>A^2/q. Since n>=1 and all bases
are positive, replacing D^n by (A^2/q)^n strictly decreases (3). Therefore

    R > L = q(x-1)/[(q-1)(x-q)] * [1-(q/A)^n].              (4)

It remains to prove L>=1. Strictness in (1) is already supplied by (4),
including any boundary equality for L.

## Nonnegative coefficient certificates

Set t=q-2>=0. Direct polynomial expansion gives

    qD-A^2 = q-1,
    A-q = t^2+2t+1 > 0,
    2A-q(q+1) = t^2+t >= 0,
    A^2-q^3 = t^4+5t^3+9t^2+6t+1 > 0.                     (5)

The coefficient lists in RESULT.json are in increasing order: [-1,1] in q
for the first identity, and [1,2,1], [0,1,1], [1,6,9,5,1] in t for
the other three. Nonnegative coefficients and the positive constant terms
prove the strict signs stated in (5) throughout the quantified domain.
The written expansions establish identities; finite coefficient calculations
corroborate them and are not an inference from a numerical sign grid.

If n=1, simplify (4) to

    L = (q^2-1)/A,
    L-1 = (q-2)/A >= 0.

Equivalently, clearing positive denominators before simplification gives
2A>=q(q+1), whose certificate is the third identity in (5). At q=2 this
lower bound is exactly one. The strict replacement in (4) still gives R>1.

If n>=2, the second and fourth identities in (5) give A>q and A^2>q^3.
Consequently

    A^n = A^2 A^{n-2} > q^3 q^{n-2} = q^{n+1} = x.

This step is strict also at n=2. It follows that (q/A)^n<1/q. Substituting
this strict bound in (4)'s expression for L gives

    L > q(x-1)/[(q-1)(x-q)] * (1-1/q)
      = (x-1)/(x-q) > 1,

because q>1. Thus R>L>=1 for all q>=2,n>=1. Since p>0, multiplying
by p^2 proves (1), in particular for every finite field and every m>=2.
No correlation-sign statement for a different pair orbit follows.

## What is new and what remains

PR4807 supplies both probabilities, their all-field validity, the binary
strict-positive theorem and the suggested qD-A^2 identity. PR4227 supplies
the marginal and PR4261 the partial-sum/header method. The increment here
is the short quantified sign proof for the remaining field sizes, using
these existing formulas. It is not a new orbit count, full audit of4807,
generic positive-correlation principle, larger-family law or physical saving.

The program evaluates205 fixed parameter pairs exactly and obtains the four
actual coefficient arrays by degree-bounded rational interpolation. A separate
engine uses polynomial convolution and integer recurrences with Euclidean
rational normalization. Neither imports a predecessor or peer program. These
checks corroborate the algebra; no GL census or predecessor scientific checker
is run. Non-prime-power rows are explicitly parameter algebra, not field counts.

The original hypotheses remain: independent a,c, ba=bc=1, one common covector,
corank-one full guards and a complete uniform header distribution. Independent
covectors/general two-way pairs, larger families and restricted headers remain
open here. Header production, selection, emission, dispatch, dirty restoration,
stock, precision, producer compatibility and the full physical caller bill are
unpriced. No supplier admission, selected-frontier change, kappa improvement,
complete multiplication theorem or human/formal-kernel acceptance is claimed.
