# The exact local interchange tariff over odd residue rings

Let m>=3 be odd and R=Z/mZ. On six equally sized, physically ordered
ADDRESS fields let s=(1,0,1,-1,0,-1)^T and r=(1,0,-1,-1,0,1)^T. Define
M(k)=I+(k/4)sr^T, for any integer k, with 4 inverted in R. These are
the actual PR521/PR840/PR2593 push maps, not VALUE-linear surrogates.

Allow arbitrary finite invertible ordered affine ADDRESS maps: a field can
be multiplied by a unit and receive linear combinations of earlier fields
and a constant. Charge every ordinary CHILD_C(0,5), the swap of the first
and sixth fields, once. No other ADDRESS permutation, change of field order,
nonlinear map, new register or different swap is free. Scalar affine work
is billed separately. Each word must implement M(k) on the complete six-field
domain, with any exterior/intervening spectators fixed. The minimum number
of these children is

    0   if k=0 in R;
    1   if k is a unit in R;
    2   otherwise.                                      (1)

This is a theorem for every odd m and integer k, not a finite extrapolation.
It is local to one query with its specified endpoint; it is not an optimum
for a surrounding DATA program with intermediate XORs or changed permissions.

## Lower bound

The linear part of any zero-child ordered affine word is lower triangular.
The (0,5) entry of M(k) is k/4, hence zero children require k=0 in R.
Conversely M(0)=I and the empty word attains zero.

Any exactly one-child word has linear part Q C P, where P,Q are invertible
lower triangular matrices and C swaps 0 and5. Its (0,5) entry is
Q[0,0] P[5,5], a product of units. Translations do not affect this linear
part. Thus one child cannot implement a nonzero nonunit k. The same argument
works with fixed ordered spectator coordinates: earlier rows of P cannot
depend on field5, and only the swapped row contributes to this entry. The
two decisive diagonal entries remain units. This is the elementary
triangular-factor invariant; no general novelty for that invariant is claimed.

## Attainment and the source word

For any unit k, PR840's unchanged seven-event word has six ordered affine
events and one C. Its diagonals are 1, k/4 and -4/k, all units. Direct
substitution gives M(k), as in the pinned source proof. This includes
composite rings: no field division by a nonunit is performed.

For any nonzero nonunit k, choose u with both u and k-u units modulo m.
Such a u exists: at each odd prime p dividing m, exclude residues0 and k
in F_p; at least one residue remains. Choose any lift to each prime power
and use the Chinese remainder theorem. The executable generic compiler
finds the first such u by bounded finite search; no efficient factorization
or uniform preparation bound is claimed.

Since r^T s=0, multiplication gives M(v)M(u)=M(u+v) over every R. Composing
the two source words for u and k-u therefore attains M(k) with two children.
Both words are complete permutations of the same six fields, so they restore
the required complete boundary and all spectators. The literal concatenation
has twelve affine events; their count is an upper bound, not a proved minimum.

## Closing PR2593's excluded prime

PR2593 fixes k=+/-3*2^j, j>=0, and excludes multiples of3 from its one-child
lowering. The exclusion is correct, not a bug. For all odd moduli use:

* m=3: k=0, so no ADDRESS work is needed;
* 3 does not divide m: use the original one-child word;
* 3 divides m and m>3: concatenate the two dyadic source words for
  +/-2^j and +/-2^(j+1).

The last branch has two unit summands on every odd modulus. It has two
children, and (1) proves this necessary in the stated local alphabet. Its
coefficient tables depend on j exactly as in PR840; growing j is not free.

For the completed triadic DATA shear F_a(x,y,z)=(x+(h^a+h^-a)y,y,z), lower
the three queries in PR2593's unchanged chronological word

    x<-h^-a x; x^=y; x<-h^(2a)x; x^=y; x<-h^-a x.

The composed ADDRESS identities give the full arbitrary dirty DATA endpoint,
not merely a single matrix entry. Source y, every dirty spectator and initial
x are preserved apart from the stated increment. Reversing all events restores
the original data. No helper row is initialized or discarded. The retained
target-exclusive-access permission is essential.

For 3|m, m>3, this literal fusion has six ordinary children,36 affine events
and two XOR scans, versus eight children,48 affine events and four XOR scans
for the separately completed pair lowered by the same adapter. Per-query
optimality cannot be added to prove global optimality: adjacent ADDRESS
words or another surrounding program could admit further fusion. At m=3,
h^a=I, so the entire DATA shear is identity; the compiler returns the empty
program, cancelling the two aligned XORs. On coprime moduli the old3/18/2
counts remain unchanged.

With C(U,b) the genuine restored-workspace ordinary child, L_u(U,b) the six
complete affine-stream charges and X(U) an aligned XOR scan, define
Q_k=C+L_k in the unit branch, Q_k=2C+L_u+L_(k-u) in the two-unit branch,
and Q_k=0 for the identity branch. Then the literal fused bill is
2Q_-a+Q_2a+2X+R_f, versus2Q_a+2Q_-a+4X+R_b for the separate pair. The m=3
empty endpoint has only any caller routing still required. Each C acts on
the whole actual DATA row of volume U=V/3, with child width b=N/3 and all
spectator ranges retained. Physical tape allocation, source access, counters,
coefficient preparation, routing and restoration remain in L and R; there is
no runtime-saving, supplier admission, analytic transfer or new kappa claim.

## Evidence and boundaries

The source-pinned compiler executes the original PR2593 address_word after
authenticating its bytes. The primary verifier compares complete matrix
columns over many odd composite rings, executes every ADDRESS position of
(Z/9)^6 for all four forward/inverse triadic query powers, and composes the
full dirty BIT endpoint and inverse. A separate checker builds the event
matrices itself, checks the actual coefficient identity and enumerates small
triangular double cosets. Controls reject the excluded original word,
noninvertible affine events, changed signs/children, the false one-child
nonunit tariff and an enlarged free alphabet. Finite checks test the code;
the proof above supplies all-size quantifiers.
