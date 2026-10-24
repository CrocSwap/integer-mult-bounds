# A uniform design with exactly one orthonormal basis

Put S=(0,1,4,10,12,17), zeta=exp(2 pi i/36), and

    v_k = (zeta^(k s))_(s in S) / sqrt(6),  0 <= k < 36.

Let X consist of these 36 rays and the six coordinate rays in C^6. Then X
has 42 distinct rays, its uniform measure is a projective 2-design, and
its orthogonality graph is K6 together with 36 isolated vertices. Consequently
the coordinate rays are its only orthonormal basis, counted as an unordered
set of rays. In particular X cannot be partitioned into seven bases.

This is a finite explicit construction and a scoped algebraic proof. The
harmonic construction is Bodmann and Haas's; the Sidon-set design theorem
is Jasper and Mixon's. The new claim here concerns this literal uniform
instance and its complete orthogonality structure. Neither the general
construction nor existence of designs in dimension six is claimed as new.

## Distinct rays

Each v_k is unit length. Its first coordinate is 1/sqrt(6), and its second
is zeta^k/sqrt(6). Therefore equality of two rays forces the proportionality
scalar to be one and then forces k=l modulo 36. Every coordinate of a flat
vector is nonzero, so no such ray equals a coordinate ray. The coordinate
rays themselves are distinct.

## The second moment

The positive pairwise differences of S are

    1,2,3,4,5,6,7,8,9,10,11,12,13,16,17.

They are distinct and smaller than 18. Thus all 30 ordered differences
between distinct marks are distinct modulo 36. Equivalently, S is Sidon
modulo 36: s_a+s_c=s_b+s_d holds modulo 36 exactly when the two unordered
pairs of marks, including repetitions, agree. For completeness, a
nontrivial equality of sums can be rearranged into an equality of ordered
nonzero differences. Distinctness of those differences forces the trivial
matching. This argument also excludes a collision involving a doubled mark.

Write P_x=xx* for a unit vector. The ((a,c),(b,d)) entry of the sum over
the flat vectors is

    (1/36) sum_(k=0)^35 zeta^[k(s_a+s_c-s_b-s_d)].

The geometric series equals one if the frequency is zero modulo 36 and
zero otherwise. By the Sidon property this gives one for each of the
two matching patterns a=b,c=d and a=d,c=b, except that the all-equal case
is counted just once. The coordinate-ray contribution is one exactly
in that all-equal case. Hence, on C^6 tensor C^6,

    sum_(x in X) P_x tensor P_x = I + Swap.

Dividing by 42=6(6+1) proves the projective 2-design identity, with weight
1/42 on every distinct ray. This is the operational definition in atlas
B042. It is stronger than a numerical fourth-potential test.

## All orthogonality relations

A coordinate vector has nonzero overlap with every v_k. Distinct coordinate
vectors are orthogonal. It remains to exclude flat-flat orthogonality.
Set

    P(t)=1+t+t^4+t^10+t^12+t^17.

Then <v_k,v_l>=P(zeta^(l-k))/6. For k different from l the order n of
zeta^(l-k) is one of 2,3,4,6,9,12,18,36. The remainders of P modulo
the corresponding cyclotomic polynomials are as follows. Coefficients
are in ascending powers in the verifier; this table uses ordinary notation.

| Root order n | Remainder of P modulo Phi_n |
| --- | --- |
| 2 | 2 |
| 3 | 1 + 2 t |
| 4 | 2 + 2 t |
| 6 | 3 - 2 t |
| 9 | 1 + 2 t - t^2 + t^3 + t^4 - t^5 |
| 12 | 2 + t^3 |
| 18 | 1 + t^2 - t^3 + t^4 - t^5 |
| 36 | t + t^4 - t^5 + t^6 + t^10 + t^11 |

Every listed polynomial is nonzero and has degree below phi(n). The
standard irreducibility theorem for cyclotomic polynomials therefore
implies P(w) is nonzero for every primitive nth root w. This excludes
every possible difference l-k. The verifier independently evaluates all
35 differences in Q[t]/(t^12-t^6+1), as well as every unordered ray pair.

Thus all orthogonality edges lie among the coordinate rays and all 15
such edges occur. Every orthonormal basis among X must be a six-clique
in this graph, so it is precisely the coordinate basis. The checker also
enumerates these cliques from each vertex's neighbor set.

## A restriction on this construction, not on all designs

The uniform-weight condition is forced in the coordinate-plus-flat model.
Suppose d>=2, there are M flat unit vectors and all d coordinate rays,
and the M+d indexed vectors carry uniform weight. A diagonal fourth
moment is (1+M/d^2)/(M+d). Equating it to 2/[d(d+1)] forces M=d^2.
For a complete cyclic character orbit with d distinct exponents, the
off-diagonal tensor equations then hold exactly when the exponents are
Sidon modulo d^2, by the same character sum above. This explains the
choice 36 and the exact 42-ray budget. It is a specialization of the
credited harmonic method, not an existence theorem in arbitrary d.

## Proof and implementation boundary

The universal complex-field implications are the geometric-series and
cyclotomic arguments above. The checker uses integer polynomial division,
without floating-point tolerances. It checks all 1,296 tensor entries,
all 861 unordered ray pairs and all 630 flat-ray distinctness pairs.
The printed receipt is computed from these checks and binds all six package
source files by SHA256. It is generated on stdout and never committed.

All loops have fixed finite domains. The largest mathematical Cartesian
domain has 6^4 entries, each with 36 character terms and 12 coefficients.
Functions are below 60 physical lines. Checks use explicit exceptions and
remain active under optimized Python. Managed Python allocation is an
explicit Power of Ten deviation: arrays have at most 72 polynomial
coefficients, the graph has 42 vertices, and source hashing reads six
bounded package files. No global diagnostics or predecessor code is changed.

This is not a native circuit, physical supplier, multiplication theorem,
SIC, MUB construction or selected-frontier update. Independent human and
formal proof-kernel review and global literature priority are unclaimed.
No predecessor verifier is replayed as the scientific deliverable.

## Credit

This contribution was produced by Nick Petalas. David Ganz's atlas PR2849,
B100 supplies the finite construction question, and B042 supplies the
moment convention. Gary S. Bloom's classical six-mark ruler supplies S;
the ruler is not a new discovery. Credit Bernhard G. Bodmann and John Haas
for the harmonic design construction and John Jasper and Dustin G. Mixon
for its Sidon-set formulation. Their results are cited methods, not audited
claims or original results of this package. See the README for references.
