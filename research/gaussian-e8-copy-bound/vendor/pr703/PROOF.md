# The asymmetric copy floor for the ten Hurwitz E8 lines

**Result.** In the scalar-total model specified below, the minimum copied
information is **10 quaternionic rank units = 40 rational rank units**.
This holds for every fitting decoder matrix separately, including every
nonsymmetric completion and decompositions with arbitrarily many totals.
It closes the particular asymmetric case left open in
[#620's extension-ring report](../e8-decoder-floors-and-cold14-notes/s1-extension-rings/REPORT.md).
It is a statement about that finite model, not a new supplier or a universal
lower bound for integer multiplication.

## 1. Geometry and the exact model

Use the 240 E8 roots in doubled standard coordinates in Q^8:

- all vectors with two nonzero coordinates, each equal to +2 or -2;
- all vectors in {+1,-1}^8 with an even number of minus signs.

Identify Q^8 with two copies of the rational Hamilton quaternions, and let
1, i, j, k act by **left** multiplication on both blocks. The Q-span of these
four translates of a root is a four-dimensional line over the quaternions.
The roots partition into ten such Q-subspaces L_0,...,L_9, with 24 roots each.
Our deterministic ordering has orthogonal pairs

    (0,9), (1,8), (2,7), (3,6), (4,5).

Each pair of distinct lines spans Q^8. Each line is orthogonal to precisely
its mate. The verifier constructs this geometry from scratch using the
Hamilton multiplication formula. Equality of the matrices 8 P_L, where P_L
is the orthogonal projector onto L, identifies the lines; no floating rank
test or tolerance is used.

Let B be a 10 by 10 matrix over F2. Its fitting conditions are

    B_tt = 1;
    B_ts = 0 whenever t != s and L_t is not orthogonal to L_s.

There is no restriction on either directed mate entry. In particular B need
not be symmetric. Write an arbitrary finite scalar-total decomposition as

    B = sum_j 1_{R_j} 1_{A_j}^T    over F2,

where R_j is the reader set and A_j is the source set. Every binary rank-one
term has this form. Both sets may be empty, terms may repeat, and no bound on
the number of terms or on rank(B) is assumed.

For a set S, concatenate the four-vector bases of its lines into a matrix
V_S. Define the charge exactly as in #620's proposed Theorem-C relaxation:

    c(R,A) = rank_Q(V_R V_A^T) / 4.

The total charge is C = sum_j c(R_j,A_j). This is the proposed pairing-rank
copy floor, not the F2 rank of the decoder rectangle. The factor four must
be restored when using the repository's rational-rank accounting.

For this geometry, direct linear algebra gives

    c(R,A) = 0  if either set is empty, or R={t}, A={mate(t)};
             1  otherwise, if either nonempty set is a singleton;
             2  if both sets have at least two elements.

Indeed two distinct lines span Q^8, so two sets of size at least two have a
Gram block of rank eight. A singleton against a spanning set has rank four.
Two quaternionic lines have a zero Gram block when orthogonal and an
invertible four by four Gram block otherwise. The verifier checks all 3,025
ordered pairs of singleton or two-line sets with two independent rational
rank implementations. Every larger set has the same span as its first two
lines; this is an exact reduction, not a sample of larger supports.

## 2. A weighted transversal rank bound

A transversal T chooses one line from each of the five orthogonal pairs.
There are 32 transversals. Two different elements of T are nonorthogonal,
so the fitting conditions force

    B[T,T] = I_5.

For a single rectangle R x A, its restriction to T x T has rank one exactly
when R meets T and A meets T, and otherwise has rank zero. Denote this
indicator by a_T(R,A). Rank subadditivity over F2 yields, for each T,

    5 <= sum_j a_T(R_j,A_j).                         (1)

For every rectangle the following local inequality holds:

    (1/16) sum_T a_T(R,A) <= c(R,A).                 (2)

There are only three cases:

1. If c=0, an empty set makes all indicators zero. In the other zero-cost
   case, a transversal cannot contain both orthogonal mates, so again all
   indicators are zero.
2. If c=1, at least one set is a singleton. Its one line belongs to exactly
   16 transversals, so the sum of indicators is at most 16.
3. If c=2, there are only 32 transversals, so the sum is at most 32.

Multiply (1) by 1/16 and sum it over the 32 transversals. Then apply (2)
term by term:

    10 = (32/16)*5
       <= sum_j (1/16) sum_T a_T(R_j,A_j)
       <= sum_j c(R_j,A_j) = C.

This is the complete lower-bound argument. In particular it does not
assume that all totals have full rank, that B has minimum possible rank,
that the decomposition is symmetric, or that the number of totals is ten.
Zero-cost terms are allowed and are invisible to every inequality (1).
No solver infeasibility claim is used.

The same argument works for 2m distinct lines in quaternionic dimension
two when their orthogonality graph is a perfect matching and the displayed
charge formula holds: average over the 2^m transversals and obtain C >= 2m.
Only the m=5 E8 instance is certified here.

## 3. Sharpness, including nonsymmetric matrices

For the symmetric completion with all directed mate entries equal to one,
use one total R=A={t,mate(t)} per orthogonal pair. These five disjoint two
by two all-one blocks satisfy the fitting pattern. Each costs two, so C=10.
Its F2 rank is five, also the minimum possible by B[T,T]=I_5.

More strongly, **every** fitting B has a cost-ten decomposition. For each
row t, take R={t} and A equal to that row's nonzero positions. The set A is
either {t} or {t,mate(t)}; the charge is one in both cases. These ten
rectangles sum to B. Combining this with the lower bound proves that
the minimum charge is ten for each of the 1,024 directed completions.

There are 32 symmetric and 992 nonsymmetric completions. Their ranks
5,6,7,8,9,10 occur with multiplicities 1,15,90,270,405,243 respectively.
Each mate block has rank one only when both free entries are one, and
rank two for the other three choices, giving these counts. The replay
also enumerates and row-reduces all completions independently.

This attains the abstract Gram-block charge. It does not assert that a
complete physical supplier implements it without any additional expense.

## 4. Optimistic complete-budget screen

The [format accounting, axiom Dfc](../format-limits-corrected/README.md)
and #620's rank-four scaling give, conditionally on using that same stage
format, v=10, k=4 and cst=4C >= 40:

    D/T = (s-1) v k - s cst
        <= (s-1)*40 - s*40
         = -40

for every positive stage count s. Equivalently x_K=C/v >= 1, with equality
already at the most favorable abstract copy cost. Even granting zero
additional cost for helpers, source access, frame changes, restoration,
and recursive work cannot make this accounting produce positive deficit.
There is therefore no reason to implement a paid supplier for this
particular mechanism before changing another premise. No assembly or
other supplier can turn this negative local deficit into a positive one
within the stated Dfc criterion.

The finite receipt checks the arithmetic for s=1,...,32 as error controls;
the displayed identity, not those examples, supplies the all-s argument.
The abstract floor does not depend on the validity of this accounting
interface. Its application to a multiplication bound does.

## 5. Scope and verification

The finite exhaustive domain is all 1,024 reader sets times all 1,024
source sets, all 32 transversals, and all 1,024 fitting matrices. The
certificate records every transversal and the exact weight 1/16. The
verifier checks each local inequality (2), all principal identities (1),
and attaining decompositions. Eight deliberately corrupted controls are
rejected; nonsymmetric and zero-cost examples are accepted.

The written rank argument extends the finite certificate to every finite
number of totals. Enumeration alone is not presented as that proof.
This is not a proof-assistant formalization.

The result does not address arbitrary rational sub-line supports,
matrix-valued or vector-linear totals, altered fitting patterns, punctured
units, other Gaussian/Eisenstein units, changing the stage format, or
physical realizations outside the declared pairing-rank model. In
particular it is not a universal obstruction to quaternionic methods.
It neither improves the selected kappa nor discharges the selected
construction's compiler, hosting, precision, tape or analytic assumptions.

Prepared by Douglas R. Colkitt with substantial OpenAI Codex assistance.
See [NOTICE.md](NOTICE.md) for predecessor credit and source status.
