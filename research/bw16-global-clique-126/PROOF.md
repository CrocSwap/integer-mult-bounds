# A global upper bound of 126

This contribution was produced by Nick Petalas. Apache-2.0.

## The finite object

Coordinates are indexed by x in F2^4, represented by the integers 0 through
15 in little-endian binary. Use ordinary real inner products. The vertex set
V consists of the following canonical norm-eight lines, with the first
nonzero coordinate positive:

1. The 240 lines 2(e_i + s e_j), i<j and s in {+1,-1}.
2. On each affine hyperplane H={x:a dot x=b}, a!=0, the 64 lines with entries
   +1 or -1 on H, zero elsewhere, and an even number of negative entries.

The second family has 30 supports, each of size eight. Quotienting the 128
even sign patterns by overall sign gives 64 lines per support, so |V|=2160.
This is the norm-eight BW16 shell in DaysSky's PR895 normalization. The shell
setting and its two-shape description are credited premises. They can also
be seen directly in RM(1,4)+2 RM(3,4)+4 Z^16: a norm-eight low residue has
weight zero or eight, and RM(3,4) is the even-weight code.

A clique means a subset of V with every two distinct lines nonorthogonal.

## Lemma 1: the D16 equality case

Let D be the first 240-line family. A clique in D has size at most 15. Every
15-line clique has the form

    S(i,s) = { 2(e_i+s_j e_j) : j!=i },  s_j in {+1,-1},

up to independent overall signs of the representatives.

To prove this, replace each line by its two-element coordinate support.
Disjoint supports give orthogonal lines. Two distinct lines on the same
support are orthogonal too, so a clique has at most one line per support.
A pairwise intersecting family of two-element subsets either has a common
point, or is contained in a triangle. Indeed, take {a,b} and {a,c}. Any edge
avoiding a must be {b,c}; if that edge is present, all edges lie in the same
triangle. A common-point family on sixteen coordinates has at most fifteen
edges, and equality uses every other coordinate. This proves the lemma.

## Lemma 2: a full star permits at most thirty lines in all

If a clique C in V contains S(i,s), then |C|<=30. The bound is attained.

Lemma 1 gives |C intersect D|<=15. Now consider an odd line v in C on an
affine hyperplane H. If i is outside H, choose j distinct from i outside H;
there are seven such choices. Both coordinates of 2(e_i+s_j e_j) vanish
in v, contradicting compatibility. Thus i is in H.

Choose the sign of v so v_i=1. For each j in H other than i, the inner
product with the star line is 2(1+s_j v_j). This is nonzero exactly when
v_j=s_j. Hence a fixed H permits at most one odd line. There are precisely
fifteen affine hyperplanes containing i, one for each nonzero a with
b=a dot i. Therefore |C|<=15+15=30. Some prescribed sign patterns fail the
even-parity requirement; this can only reduce the count.

For attainment take i=0, all s_j=+1, and the fifteen all-positive indicator
vectors of the hyperplanes through zero. Distinct hyperplanes intersect in
four coordinates, so these odd lines are mutually nonorthogonal. Each also
meets every star line nonorthogonally. The resulting clique has thirty lines.

## The exact nine-chart certificate

List the six quadratic monomials in this order:

    x0*x1, x0*x2, x0*x3, x1*x2, x1*x3, x2*x3.

An integer c from 0 through 63 encodes their binary coefficients. Put
q_c(x)=sum_{i<j} c_ij*x_i*x_j in F2 and define the integer matrix

    H_c[x,b] = (-1)^(q_c(x)+b dot x),  x,b in F2^4.
    U_c = H_c/4.

Use exactly these eight forms:

    0, 57, 53, 46, 35, 28, 18, 15.

Together with the identity chart they satisfy the following finite facts:

- H_c H_c^T=16 I for each of the eight matrices, so U_c is orthogonal.
- D and the eight sets U_c D are pairwise disjoint subsets of V of size 240.
  Their union is V.
- For every c and every v in V, U_c^T v is integral and represents a line
  in V. This exhausts 8*2160=17280 image checks. Orthogonality and the finite
  bijection establish U_c^T V=V.

`verify.py` constructs the entire shell and checks these facts with exact
integer arithmetic. It divides only after testing divisibility. Thus these
facts are a complete finite certificate, rather than sampled evidence or
floating eigenvalue estimates. No theorem about an unmaterialized orbit is
needed. Quadratic-phase Walsh bases and Kerdock/mutually unbiased bases are
classical; the table is an explicit certificate, not a claim to those ideas.

## Theorem

Every clique in V has at most 126 lines.

Suppose |C|>=127. The nine disjoint D16 sets partition V, so at least one
contains fifteen members of C. Lemma 1 excludes more than fifteen. If it is
the identity set, Lemma 2 gives |C|<=30. Otherwise apply U_c^T to the whole
clique. The exact certificate ensures that the image is still a clique in V,
and its intersection with D contains a full fifteen-line star. Lemma 2 again
gives |C|<=30, a contradiction. Equivalently, every clique larger than thirty
has at most fourteen lines in each chart, giving |C|<=9*14=126.

The basic nine-chart counting bound is 135. The new step removes its D16
equality case in every chart, improving that bound by nine. The classical
135-frame geometry itself is not claimed as new. This is a finite geometric
obstruction with a scoped written proof over all subsets of this fixed V;
it is neither a failed clique search nor an all-dimensional lattice theorem.

## Exact evidence and limits

Besides the complete chart checks, the verifier compares the star formula
with direct integer inner products against all 1920 odd lines on 176 named
center/sign fixtures. It enumerates all 32768 sign patterns at center zero
by the independent hyperplane-parity formula. The proof covers arbitrary
signs at every center; the 176 direct fixtures are not described as an
exhaustive census of all center/sign pairs. The thirty-line attainer has
all 435 pairs checked.

The published 72-line lower witness in PR895 is a cited result, not replayed
here. The resulting interval 72<=omega(V)<=126 does not determine omega(V).
A clique upper bound is not an upper bound on the binary decoder's minimum
fitting rank. Physical native realization, scalar/helper delivery, arbitrary
dirty restoration, a complete paid invoice and the five selected framework
assumptions remain separate. No kappa or selected-frontier change follows.
Independent human and formal proof-kernel review are unclaimed.
