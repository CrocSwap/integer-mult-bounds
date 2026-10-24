# Five-call controllers after arbitrary binary changes of basis

This is a finite binary-algebra exclusion, not a new supplier or a multiplication
bound. The result concerns four main fields, five chronological query-bearing
calls, independent fresh stage multipliers, no idle calls, and constant binary
input/output changes of basis. It does not restrict longer words, other fields,
other output contracts, or arbitrary native resynthesis.

## Model and completeness of the alphabet

Work over `F2[Q,D0,...,D4]/(Q^2-1)`. The `Ds` are independent commuting
indeterminates; their squares are **not** identified with one. A thin call is
`I+QN`, where `N` is a rank-one nilpotent binary 4-by-4 matrix. There are
15 nonzero image vectors `u`, seven nonzero annihilating covectors `v` per
vector, and hence 105 distinct `N=u v^T` with `v^T u=0`.

A full call is

    (I+(Ds+1)P)(I+QN),

where `P` is a rank-two projector and `PN=NP=N`. These are precisely the
simultaneous conjugates of a native call acting on two coordinate fields.
On the image of P the nilpotent has its single size-two Jordan block; on the
kernel of P it is zero. An adapted binary basis therefore gives the ordinary
coordinate call. For each N there are 16 distinct P, giving 1,680 full calls.
The verifier checks ranks, idempotence, nilpotence, and both commutations.

Allowing arbitrary scalar changes between calls produces no larger class:
push each intervening basis change to the right, conjugating the subsequent
call. The remaining terminal basis change is absorbed in the allowed output
boundary. A simultaneous global conjugation fixes the first full or thin call
to the canonical coordinate call. This preserves the desired property and
explains the symmetry reduction used in the enumeration.

## What counts as success

A successful operator has constant invertible L,R with

    L M R = diag(Q*m0, Q*m1, Q*m2, Q*m3),

where each mi is a monomial in the stage multipliers. The coefficient of every
Q-even term must first vanish. This necessary cancellation is not sufficient.
Write the remaining matrix as `sum_g g A_g`, using distinct Q-odd monomials g.
It has the required two-sided constant factorization exactly when

    sum_g rank(A_g) = 4.

Necessity follows by taking the coefficients of the diagonal form. For
sufficiency, choose rank factorizations `A_g=U_g V_g` and concatenate U_g and
V_g. The total rank assumption makes their inner dimension four. Evaluation
at Q=Ds=1 gives an invertible product UV, since every call is invertible at
that evaluation. Thus U and V are both invertible and supply the required
left/right bases. This is an exact test, not a numerical eigenvalue test.

## Safe finite-field pruning

The search evaluates Ds at the five nonzero elements 2,3,4,5,6 of
`F16 = F2[x]/(x^4+x+1)` and retains Q formally as `E+QO`. Every full scale is
invertible. A query changes the even part from E to `E+NO`, so its rank can
fall by at most one. With r calls remaining, `rank(E)>r` safely rejects a
prefix. Specialization can lower a rank, so this pruning can retain false
positives but cannot remove a symbolic success.

For the last query, zero even part requires `E=NO`. Then
`O+NE=O`, because `N^2=0`. Invertibility of the final evaluated word implies
O was already invertible. The last nilpotent is therefore uniquely determined:
`N=E O^-1`. The search checks whether it is a binary nilpotent in the declared
alphabet and enumerates all compatible full projectors when appropriate.
It never guesses a last call from a numerical near-equality.

Every surviving word is then replayed separately over the original polynomial
ring, using integer bitsets for exact monomial supports and binary Gaussian
elimination for coefficient ranks. No F16 evaluation enters that final test.
The 12,480 evaluated survivors all pass exact Q-even cancellation. Every one
has coefficient-rank sum at least six; none has sum four. The per-mask rank
histograms, actual prefix counts and survivor hashes are in RESULT.json.

## Resource connection and limits

For five calls on four main fields, with f full calls and 5-f thin calls,
the original complex local inventory would have formal rank surplus
`4*112 - 64*f - 112*(5-f) = 48*f - 112` in a no-idle exact diagonal unit.
The BIT inventory gives `48*f-111`. The enumerated masks have f=3,4,5;
these include every mask with positive first-order surplus under those
inventories. The other masks have negative first-order surplus. That
observation is not asserted to exclude every possible interior moment sign.

The search is a result over F2 and does not prove the analogous complex
exclusion: reduction modulo two need not preserve arbitrary dyadic boundaries.
A complex lift would require its own exact coefficient calculation and native
phase/contact proof. The positive control is two disjoint three-call words,
which **do** factor. Thus the alphabet is not being rejected by an impossible
success condition. An actual five-call all-Q survivor demonstrates that
checking only query cancellation, or setting all stage multipliers to one,
would incorrectly promote a candidate.

The result blocks a precise small route to removing the controller's largest
bill. It establishes no all-length obstruction and gives no new kappa.
