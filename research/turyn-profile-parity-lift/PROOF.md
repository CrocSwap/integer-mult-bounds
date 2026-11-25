# Actual-port rank-nine parity certificates in characteristic two

## Statement

For each of the three Turyn profiles, the certificate gives **20 actual
ports** whose active graph has 124 edges. Fix any field K of characteristic
two and any positive integer d. A d-block fitting of this graph is a matrix
M over K, with its rows and columns grouped by the twenty vertices, such that

    M_vv = I_d,
    M_vw = 0 for each ordered pair of adjacent distinct vertices.

No symmetry, transpose relation between factors, or standard-dot
representation is required. Then

    rank(M) ≥ 9d.

The same statement holds if the fitting convention permits arbitrary
invertible diagonal d-by-d blocks: multiplying each block row by the
inverse of its diagonal block normalizes it to I_d, preserves every zero
edge block, and does not change matrix rank. The graph convention here
requires zeros on **active edges**, as displayed; it is fixed explicitly
rather than inferred from any alternate minrank/complement convention.

For every K and d there is a fitting of rank exactly 9d. Thus the scalar
minimum fitting rank and the normalized minimum block fitting rank are
both nine for each of the three explicit graphs. Moreover, the minimum
asymmetric d-block fitting rank of **each complete canonical 7,680-port
Turyn profile is exactly 9d**. Restriction to its listed twenty ports gives
the lower bound, and the complete upper-bound verification is below.

This does **not** imply a global bound of 27 for all three profiles together.
It does not exclude a global 25-dimensional full-port fitting. It changes
no supplier, cost recurrence, or κ certificate.

## 1. The finite geometric certificate

The source is DominikScholz's PR598 Turyn construction. Its integer vectors
x have squared norm 32; the real vector is x/√8. A profile consists of
three eight-dimensional blocks whose squared norms are 16, 8, 8, with the
location of the norm-16 block specifying the profile. Two distinct ports
are active exactly when all three integer block inner products are nonzero.
The scalar tensor kernel is their product divided by 8³, so this exact
integer test involves no approximation.

The predecessor's quotient groups eight ports with the same two low roots
into one glue class. An edge of that quotient only means that **some**
pair of representatives is active. It does not alone certify an edge
between chosen representatives.

We restrict the predecessor's nine 24-cliques to one profile, obtaining
nine sets of eight glue classes. The new construction selects one actual
port per used class, consistently across all nine sets. It verifies every
required edge using that port's literal integer coordinates. This succeeds
separately for all three profiles. Each lift has:

- Twenty distinct actual ports
- Nine actual 8-cliques
- Twelve ports occurring in two cliques, and eight occurring in six
- Exactly 124 distinct active edges, all contained in the listed cliques

There are 9·8·7 = 504 ordered clique-edge checks per profile. The independent
verifier also examines all 190 unordered coordinate pairs, checks exact
Turyn shell membership, and checks the upper-bound labels on every active
edge. Its inputs are explicit coordinates, not existential quotient edges.

## 2. The rank argument allows asymmetric blocks

Let r = rank(M) and choose a rank factorization M = AB, where A has r
columns and B has r rows. Write A_v for the d-by-r row block belonging to
vertex v, and B_v for the r-by-d column block. The diagonal and edge
conditions give

    A_v B_v = I_d,
    A_v B_w = 0 whenever v and w are adjacent.

Set P_v = B_v A_v, an r-by-r matrix. It is an idempotent of rank d:

    P_v² = B_v (A_v B_v) A_v = P_v.

Its image is precisely the d-dimensional image of B_v. For two adjacent
vertices, both P_v P_w and P_w P_v vanish, because both ordered fitting
blocks vanish.

For one of the eight-vertex cliques C, put

    Q_C = sum_{v in C} P_v,
    R_C = I_r - Q_C.

The summands in Q_C mutually annihilate. Their images form a direct sum:
applying P_w to a relation among these images isolates its w component.
Thus Q_C is an idempotent of rank 8d, and R_C has rank r−8d.

Every vertex appears an even number of times in the nine cliques. Since
K has characteristic two, summing their Q_C gives zero. There are an odd
number of cliques, so

    sum_C R_C = 9 I_r - sum_C Q_C = I_r.

Rank subadditivity now yields

    r = rank(I_r) ≤ sum_C rank(R_C) = 9(r−8d),

or 8r ≥ 72d. Hence r ≥ 9d, as claimed. This is a field-independent written
linear-algebra argument in characteristic two. No symmetry of M and no
finite-field enumeration is used.

## 3. Tight upper bound

For each twenty-port graph, `CERTIFICATE.json` supplies explicit binary
labels p_v in F₂⁹. The verifier checks

    p_v·p_v = 1,
    p_v·p_w = 0 on every active edge.

The same zero/one labels are defined over every characteristic-two field.
Their Gram matrix G is a scalar fitting of rank at most nine. The block
matrix G tensor I_d is a d-block fitting of rank at most 9d. Together with
the lower bound, its rank and the minimum possible rank are exactly 9d.

The explicit labels are generated from a low-root binary Gram matrix, but
their correctness is checked directly and does not depend on trusting that
generation procedure. The checker also confirms their binary rank is nine.

## 4. Complete-profile upper bound, without sampled edges

`FULL-PROFILE-UPPER.json` gives 120 canonical integer low roots r of
squared norm eight and a nine-bit label p(r) for each. The verifier checks
all 7,140 pairs of distinct roots. Their pairings belong to {-4,0,4}, and

    p(r)·p(s) = 1 + (r·s)/4 mod 2.

Every diagonal label has odd weight. In profile a, assign a port the label
of its low block (a+1) mod 3. The independent full-profile checker rebuilds
all 23,040 canonical ports from the binary-span Turyn code and exact shell
families. It matches the pinned complete-array SHA256 and checks every
port's coordinate membership, norm, canonical signs, and profile. In each
profile it verifies that the 120 low roots partition all 7,680 ports into
fibers of exactly 64.

For two distinct ports in the same root fiber, all 241,920 such pairs per
profile are checked to be inactive. For ports with different low roots:

- Root pairing zero makes their scalar tensor kernel zero
- Root pairing +4 or -4 makes their binary label pairing zero

In particular, an active pair with distinct low roots must have nonzero
inner product in the selected low block, because activity requires all
three block products to be nonzero. The checked distinct-root spectrum
then forces that product to be +4 or -4, and the displayed Gram formula
forces its label inner product to be zero.

Thus every actual edge has label pairing zero. These three cases partition
**all 29,487,360 unordered pairs in each profile**; no edge sampling or
assumption about unexamined high-block pairings is used. The distinct-root
cases need only 7,140 root-pair checks rather than expanding every pair of
their 64-port fibers.

The zero/one Gram fitting again works over every characteristic-two field,
and tensoring with I_d gives rank at most 9d. The twenty-port lower-bound
restriction makes equality necessary. The full-profile checker additionally
binds all sixty lower-witness source indices to their literal coordinates
in the independently regenerated complete array.

## 5. What this extends and what remains open

The predecessor established a 27-dimensional characteristic-two quotient
obstruction for class-constant labels, and a different 24-port nine-bit
obstruction for symmetric standard-dot labels over F₂. It explicitly did
not assert an asymmetric fitting lower bound from that enumeration.

This contribution lifts the **per-profile restrictions** of the older
parity certificate to actual ports. The resulting twenty-port witnesses
give the stronger per-profile statement for arbitrary asymmetric block
fittings over every characteristic-two field. In particular, neither an
extension field nor block normalization can make a separately realized
profile have fitting dimension below nine in this model.

The three per-profile results do not add automatically: source and target
spans from different profiles need not be mutually orthogonal. The new
chosen lifts also fail numerous cross-profile edges of the original
24-cliques; `GLOBAL-SCOPE-CONTROL.json` records those exact failures. This
does not contradict the predecessor's nonliftability example for a global
quotient clique, and it is not a search over alternative global lifts.

The rank argument is the predecessor's parity-projector argument, credited
there, applied to these newly exhibited actual-port covers. The new result
is the geometric lift and the resulting removal of the per-profile
symmetry, scalar-block, and F₂-only restrictions, not a new general parity
principle or a new exponent improvement.
