# Rigidity of the fixed PR1064 factory gauge

This audit concerns the 26 ordered unit ADDs derived from the pinned PR924
factory. PR1064 supplies a nine-shift witness and a dual flow. The new result
is that this witness is the **only optimal ADD-boundary level vector, even in
the real relaxation**. Every other integer vector costs at least eleven
shifts, and that gap is attained. This is a scoped negative result for changing
the gauge, not a counterexample to PR1064.

## 1. Exact object and cost

Move each original diagonal factor into a logical change of coordinates.
If the current diagonal factors are D_r and a macro is x_t += q x_s, the
logical coefficient is q D_s / D_t = sigma 2^e. Its target and source physical
levels must be p_t = l_j and p_s = l_j + e to implement it as one signed unit
ADD. Original SCALE macros update D_r. The resulting ordered list and final
exponents are in `CERTIFICATE.json`.

For each register, join consecutive uses and its initial/final boundaries.
A use at ADD j has offset 0 on the target and e on the source. Between uses
(a,u) and (b,v), set c = u-v and d = l_b-l_a-c. The initial boundary has level
and offset zero; the final boundary has level zero and that register's final
exponent as its offset. There are 60 edges. The abstract boundary is vertex
-1, with l_-1 = 0. The shift cost is

    F(l) = sum_e |l_b-l_a-c_e|.

For integer levels, this is the minimum number of binary DOUBLE/HALVE steps
between the specified ADD uses. A monotone sequence attains each distance;
extra excursions can only increase the invoice. Signed unit ADDs and the two
final sign changes are fixed in this class. The canonical eager emitter has
26 ADDs + 9 shifts + 2 NEGs = 37 instructions. The separate exit work CLEAR
is paid as instruction 38. No helper, copy or recursive child is introduced
by this audit, and it does not compose a new full supplier.

## 2. Lower bound and uniqueness over all real levels

The pinned dual flow has |f_e| <= 1 and zero divergence at every ADD vertex.
The independent checker derives the wire paths from the macro word, verifies
those conditions, and finds -sum_e f_e c_e = 9. Conservation gives, for every
real level vector,

    sum_e f_e d_e = 9,
    F(l)-9 = sum_e (|d_e|-f_e d_e) >= 0.

Each summand is nonnegative. At F(l)=9, every edge with f_e=0 must have d_e=0.
The 35 zero-flow edges form a connected graph on all 27 vertices, including
the fixed boundary. `anchored_spanning_tree` lists 26 of those edges. Traversing
them from vertex -1 uniquely determines every l_j. All remaining zero-flow
edges are consistent with those values. They equal PR1064's supplied vector;
the other edges satisfy complementary slackness and their absolute residuals
sum to nine. Thus existence and uniqueness both hold. This is an all-real
argument; it does not rely on bounding or searching an integer box.

The same certificate gives a stability estimate. Set delta_j=l_j-l_j*.
For a zero-flow edge, d_e=delta_b-delta_a. Consequently

    F(l)-9 >= sum_{f_e=0} |delta_b-delta_a| >= max_j |delta_j|.

The last inequality follows by taking the unique anchored tree path to j
and applying the triangle inequality. Boundary anchoring is essential:
removing all boundary zero-flow edges isolates the boundary and leaves two
variable components, so the uniqueness argument would fail.

## 3. Sharp gap for integer gauges

Every ADD vertex has two incoming and two outgoing register-path edges.
The certificate checks this incidence cancellation and sum_e c_e = -5.
For every level vector, sum_e d_e = 5. For integer levels all d_e are integers,
so

    F(l) = 5 + 2 sum_e max(-d_e,0)

is odd. Uniqueness and F>=9 imply F>=11 for every other integer vector.
Changing l_0 from 1 to 0 attains eleven, making the bound sharp. As additional
local evidence, all 52 signed unit perturbations were checked: thirteen cost
11 and thirty-nine cost 13. The parity argument proves the general gap; this
finite perturbation census does not prove it by itself.

## 4. Precision and limits

The independent dense Fraction replay compares all eight arbitrary input
columns with PR924 in four orientations. For the canonical eager emitter,
the peak row L1 norms are main 12, cleanup 8, inverse-transpose 10, transpose
11; fractional depths are respectively 1, 2, 2, 1. These corroborate PR1064.
A different optimal level vector cannot improve those numbers because no
such vector exists. Moving unary steps within unused-wire intervals may still
change prefix precision at the same levels; that question is outside this
result. We do not claim a unique primitive ordering, optimal precision over
all schedules, arbitrary-circuit optimality, or a new kappa.

This local algebraic result does not verify PR1064's 725-column raw program,
72-call host, all-size compiler, source access, physical frames, precision/tape
recovery, or analytic transfer. Transport to the selected T37 supplier remains
an unresolved obligation. The finite certificate is not a formal proof of the
full multiplication theorem. No concrete counterexample or failed search is
reported: the finding is a proved singleton optimum in the stated class.

Prepared for @ToikY with substantial OpenAI Codex assistance, including a
separate agent's read-only proof and implementation review. Credit Ali Romman
(PR1064) for the primal/dual certificate and construction; CubeJerry
(PR922/924), Alluri (PR681), and the compiler/hosting predecessors listed in
`SOURCES.json`. New work is Apache-2.0.
