# Fixed-source proportional-pair carrier obstruction

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a pair-only finite-source theorem with an unrestricted dyadic repair
alphabet. It is not a global native optimum or a new multiplication bound.

## Exact domain and census

The pinned #6702 native word, used by #6726, has 631 eligible public-helper
intervals. An eligible interval consists of two consecutive forward MOVEs
A -> B -> C, with at least one intermediate ADD export, and no write to its
helper except SCALE between them. Actual helpers exclude both `live` and
`live+112`; unused main-register slots are included. COPY is not deleted.

Replay the full old-input rows with exact rational arithmetic at each first
MOVE. Normalize a nonzero row by its first nonzero coefficient and group exact
equalities. There are 523 projective classes: 429 singletons, 80 doubletons,
and 14 triples. The complete 122 unordered proportional pairs all use the
same helper, and its whole combined span has only SCALE/MOVE writes. The
exact source endpoint on all 771 public inputs and 800 rows is checked.
Every held row is nonzero modulo 65521; every retained SCALE is a modular
unit. These conditions are explicitly checked also for the disjoint pairs.

The census is deterministically regenerated and compared with a canonical
SHA256, rather than shipping the redundant 1.7 MB rational row dump. The
independent review compares every rational row, class and paired identity.

## Paired edits and exact shared-MOVE accounting

For the 108 pairs sharing a MOVE, the union is a three-MOVE chain
A -> B -> C -> E. Replace it by A -> E and delete exactly the exports at B
and C. Only A/E carrier injections are allowed; B/C are not retained source
frames. If the three paid ranks are a,b,c, the replacement is H(a+b+c),
not two separately credited fusions of a shared MOVE.

For the other 14 pairs, the chain is A -> B -> C -> D -> E. Replace it by
A -> C -> E, deleting exports at B/D and retaining every C export. If the
four ranks are a,b,c,d, replace H(a)+H(b)+H(c)+H(d) by H(a+b)+H(c+d).
Endpoint contracts and all other transports are unchanged. These signed
rank identities are accounting facts, not a paying construction: every
case fails the necessary endpoint condition before costs can establish a gain.

Both forms allow arbitrarily many dyadic ADD injections from the held helper
to any other public or live owned resident at its retained frame. The held
helper cannot be an injection recipient. All other scalar instructions and
recipient histories remain fixed. SCALEs retain their scalar action and
follow the helper's retimed residence. Full-frame public outputs are entirely
unconstrained, granting arbitrary free cleanup as a strict relaxation.
All other final public rows and the actual COPY-zero observable are retained.

## Maximal chronology and complete finite coverage

A cut t is before old instruction t. Let i,j be the outer first/last MOVE.
Let lo be after the preceding non-SCALE helper write or MOVE, and hi the
next such instruction (with program endpoints when absent). Thus the held
row is unchanged up to SCALE over the whole lo..hi residence.

For a shared pair, set

    lower = max({lo} union {z+1 : retained A-read z before i})
    upper = min({hi} union {z   : retained E-read z after j}).

The fused MOVE may be at any t in [lower,upper]; A injections may occur
from lo through t, and E injections from t through hi. All retained outer
reads, including those outside the original pair, are used in these bounds.

For a disjoint pair, the retained middle C reads are nonempty. The first
fusion cut t1 is bounded below by the last retained A read and above by the
first C read. The second cut t2 is bounded below by one after the last C
read and above by the first retained E read. Thus upper1 < lower2 and every
cut pair is ordered. A, C, E injection windows are respectively
[lo,t1], [t1,t2], [t2,hi].

A recipient suffix-response vector and frame are constant between touches.
For a residence segment [l,h], A availability is l<=t1, E availability is
h>=t2, and C availability is l<=t2 and h>=t1. Shared pairs use t1=t2.
The complete threshold grid contains the bounds, A starts/C ends for t1,
and C starts/E ends for t2. Between thresholds, the column set is contained
in the set at a checked endpoint. The two coordinates may be treated
independently because the retained C reads already enforce their order.
This yields exactly 439 shared systems and 248 disjoint systems.

## Why all dyadic repairs are excluded

Let v be the held helper's old-input row at the outer first MOVE. Throughout
the combined window it is a(t)v, with nonzero retained SCALE factors. There
is no other helper write, so recipient perturbations cannot feed back into
this source before any removed export. Deleting the combined exports changes
the constrained observations by -D tensor v. An injection changes them by
b*a(t)*S(t,r) tensor v, with S the recipient's unchanged suffix column.
All-input preservation therefore requires D in the span of the available
S(t,r). No restriction is placed on the number of injections or their dyadic
coefficients. Later feedback after the window is included in the suffix.

Reduction Z[1/2] -> F_65521 preserves a necessary equation. The source row's
nonvanishing and every retained SCALE's invertibility are checked, preventing
vacuity. Every one of the 687 systems fails the finite-field span equation.
The separate forward SSA implementation independently regenerates all these
systems and supplies 687 separating functionals with 9,199 direct dot-product
checks: each functional is zero on every column and one on its target.
Consequently no allowed exact dyadic repair exists. Arbitrary rational
coefficients with denominator divisible by 65521 are not excluded.

A second, direct forward error-vector replay checks all 122 combined targets,
including the COPY monitor, and verifies zero held-source perturbation before
every deleted export. COPY is treated as ADD plus a required pre-COPY-zero
observable, and CLEAR permits dirty owned erasure. The independent review
reconstructs owned lifetimes and residence columns without importing the
primary generator or solver.

## Limits and next questions

This theorem couples exactly TWO eligible intervals. The 14 size-three
classes have all three unordered pairs covered, but simultaneous coupling
of all THREE intervals is untested. That remains an explicit opening.
Changed helper writes or initial bases, interacting distinct helper rows,
new carrier transports, extra deleted outside exports, more than two
intervals, and changed endpoint contracts are also outside the theorem.
No floating paid-stop pilot is included in this package or theorem.

Independent held rows cannot cancel separate errors under an unchanged,
noninteracting schedule: linear independence in R1 tensor v1 + R2 tensor v2
forces both errors to vanish. This observation does not extend the census
to interacting different-helper schedules, nor eliminate triple coupling.
No physical-native, compiler, precision/tape, analytic, or selected-frontier
claim follows. The five retained framework assumptions remain unchanged.
