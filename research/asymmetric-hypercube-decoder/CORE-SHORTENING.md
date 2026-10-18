# q=3 shortening to a common original-pair core

**Uniform shortening theorem; no new κ.** Let p=k+3, let K be k−2 original pairs, and
shorten C+_(p,k) to ports containing every pair in K, with their signs
unrestricted. Put c=k−2. The remaining five original pairs carry a signed
two-port, identified with an edge of the ten-vertex cocktail-party graph.
Write s∈F2^c for the core signs, and expand a shortened word uniquely as

    f(s,e) = sum_(S subset K) s_S g_S(e),
    s_S = product_(i in S) s_i.

## Exact filtration

Define nested residual spaces V0⊂V2⊂V3⊂V4 on the forty residual ports:

* V0 is C+_(5,2), dimension 10, minimum nonzero weight 8.
* V2 adds arbitrary functions of the unsigned residual original-pair edge
  to V0. It has dimension 15 and minimum weight 4.
* V3 consists of arbitrary affine functions of the two residual signs on
  each of the ten unsigned pair-edge blocks. Dimension 30, minimum weight 2.
* V4 is the full forty-coordinate space. Dimension 40, minimum weight 1.

Then the exact shortened code is the following direct sum, with completely
independent choices for every core ANF coefficient:

    g_S ∈ V0             if c−|S| = 0 or 1;
    g_S ∈ V2             if c−|S| = 2;
    g_S ∈ V3             if c−|S| = 3;
    g_S ∈ V4             if c−|S| ≥ 4.                     (1)

Its dimension, with binomial coefficients outside their range set to zero,
is

    40·2^c − 30(1+c) − 25 binom(c,2) − 10 binom(c,3).

For c=0,1,2,3,4 this gives 10,20,45,115,300. The naive tensor space of
arbitrary core-sign functions with V0 has dimension 10·2^c, so it is exact
only for c≤1 and is strictly too small for every c≥2.

## Sign coefficients reduce the proof to an unsigned shortening ladder

For original pair i, use occupancy z_i=x_(i,0)+x_(i,1) and sign coordinate
x_i=x_(i,1). Products x_A z_B with A and B disjoint, total degree at most
k−1, span exactly the proper-star observations (including the empty star).
On the occupancy block I, x_A contributes the sign monomial indexed by A.
Its coefficient is an arbitrary degree-at-most k−1−|A| polynomial in the
remaining occupancies, evaluated on subsets of size k−|A|.

These sign-ANF components are independent: vanishing on any occupancy block
means that every sign coefficient vanishes separately on that block.
Consequently shortening also separates over A. On our allowed ports write
A=S union B, where S⊆K, B consists of b residual sign indices, and b≤2.
Let t=c−|S|. The remaining occupancy problem has

    n=t+5−b vertices,
    m=t+2−b occupied vertices,
    degree bound d=t+1−b.

There are exactly three absent vertices. Replacing occupancies by one plus
absence indicators preserves degree, so the coefficient code is the
polynomial code of degree at most d on the three-subsets of n=d+4 vertices,
shortened to subsets avoiding the t core vertices.

For d≥3 this unsigned code is full: each individual absence triple is the
evaluation of its degree-three monomial. For d<0 it is zero. The remaining
three cases follow from the ladder

    degree≤2 on triples of 6 --avoid one vertex--> degree≤1 on triples of 5
                            --avoid one vertex--> constants on triples of 4
                            --avoid one vertex--> zero on triples of 3. (2)

Here is a direct proof of the first arrow. Write a quadratic as Q(y)+x L(y),
where x is the avoided vertex and y comprises five others. Vanishing at
x=1 on every two-subset of y means R=Q+L vanishes on every two-subset.
Writing

    R(y)=a + sum_i b_i y_i + sum_(i<j) c_ij y_i y_j

gives c_ij=a+b_i+b_j. On any three-subset, R equals sum_i b_i y_i, hence
Q=R+L restricts to an affine linear function. Conversely multiplying any
such affine linear function by (1+x) provides a quadratic supported away
from x. For the second arrow, an affine linear function vanishing at x=1
on all two-subsets of four remaining vertices has equal coefficients on
those four vertices, and therefore is constant on their three-subsets.
The reverse inclusion is (1+x). The final arrow is immediate.

Apply (2) t times when d≤2. For b=0 the surviving coefficient space is the
affine linear code on residual triples of five vertices, equivalently the
cut-plus-constant code on their complementary unsigned edges, dimension 5.
For b=1 it consists of constants across the four possible partner pairs,
dimension 1. For b=2 it is zero. A coefficient becomes arbitrary precisely
when its initial degree d≥3, namely t≥b+2. Thus:

* unsigned block coefficients become arbitrary at t=2;
* each residual linear-sign coefficient becomes independently arbitrary
  across partner blocks at t=3;
* residual bilinear-sign coefficients become arbitrary at t=4.

This proves (1), including independence of all coefficients.

## The 16-weight barrier for every extra word

Choose vector-space complements along the nested residual spaces, so every
word has a unique decomposition into its V0 part and its new V2, V3, V4
layers. The new Vj layer has coefficient functions in the core variables
of degree at most c−j, for j∈{2,3,4}. This follows directly from (1).

Suppose a word has a nonzero extra layer, and let j be its highest nonzero
layer. Choose a residual linear functional that annihilates the previous
space but detects this layer. Applying it separately at every core sign
s gives a nonzero Boolean polynomial of degree at most c−j. It is nonzero
on at least 2^j core assignments. On every such assignment, the residual
word is nonzero and lies in Vj. Its weight is at least 4,2,1 for j=2,3,4,
respectively. The total word weight is therefore at least 16 in all cases.

The polynomial weight bound used here has an elementary induction proof.
If P=P0+x P1 and P1≠0, then deg P1≤d−1; every input where P1 is nonzero
contributes exactly one nonzero value among the two x choices. If P1=0,
P is duplicated over x. These two cases give weight(P)≥2^(c−d).

The residual distances are elementary. V3 is a direct sum of ten length-four
affine codes, each of distance two; V4 is full. A V2 word has the form

    alpha_ij + beta_i epsilon_i + beta_j epsilon_j

on block ij. If all beta_i vanish, any nonzero block has weight four. If
some beta_i is nonzero, the four blocks incident to i each have a nonzero
linear part and therefore weight two, so total weight is at least eight.
Thus V2 has distance four. V0 has distance eight by the cut-code calculation
below. The extra-layer barrier is sharp when c≥2: multiply one unsigned
residual block by a core monomial of degree c−2. It is an allowed V2-layer
word of weight 4·4=16, outside the naive tensor space.

## Consequence: every weight-14 word fixes the entire core sign

Any word of weight less than 16 lies in the naive tensor space: every
core-sign branch independently carries a word of V0. Since V0 has minimum
weight eight, a weight-14 word has exactly one nonzero core branch.

To classify that branch, write a V0 word as a cut delta(A), or its complement,
and replace A by its complement so a=|A|≤5. If A contains t complete original
matched pairs, the cut weight is

    a(10−a)−(a−2t)=a(9−a)+2t.

For a=1 the weight is eight. The only way to get weight fourteen is a=2,
t=0: A contains two vertices from different original pairs, so these are
adjacent signed vertices. For a≥3 the cut weight is at least eighteen.
The maximum cut weight is twenty-four, so complements have weight at least
sixteen. Hence a weight-14 residual word is exactly the sum of two adjacent
singleton stars. There are forty such residual words.

After restoring the fixed signed core, every weight-14 shortened word is
therefore the sum of two adjacent (k−1)-stars sharing that signed core.
There are exactly 40·2^c such words. This is a uniform statement for every
k≥2 at q=3, conditional only on the support containing the specified common
original-pair core, not a global second-weight classification outside that
shortening.

## Independent finite checks

Run:

    python3 -I -O -B research/asymmetric-hypercube-decoder/core_shortening_verify.py --self-test

The standard-library verifier generates every global proper-star evaluation
row directly, then eliminates outside coordinates to obtain the actual
shortened code. A separate rank-difference identity checks its dimension.
It transforms the result to core-sign ANF, compares every component space
with the explicit residual generators above, and reinserts those components
to verify that there are no hidden couplings.

| k | p | Full ports | Global star generators | Global rank | Shortened rank | Naive tensor rank |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 6 | 160 | 73 | 60 | 20 | 20 |
| 4 | 7 | 560 | 379 | 280 | 45 | 40 |
| 5 | 8 | 1,792 | 1,697 | 1,106 | 115 | 80 |
| 6 | 9 | 5,376 | 6,883 | 3,864 | 300 | 160 |

This covers 9,032 global generators and all thirty core ANF components.
The verifier separately checks the unsigned shortening ladder, enumerates
all 1,024 words of V0 and all 32,768 words of V2, and verifies their exact
minimum weights. It checks all forty residual weight-14 words against
adjacent-star sums. For c≤4 it also exhaustively checks the relevant core
polynomial distance bounds, enumerating 2,102 polynomials across six cases.

Finally it enumerates all 1,048,576 words of the k=3 shortened code. The
only nonzero weights below sixteen are eight (twenty words) and fourteen
(eighty words), and every such word fixes the core sign. The larger cases
are exact space checks, not exhaustive word enumerations. Negative controls
verify that one unsigned residual block does not belong to V0, while its
suitable core-monomial lift really is an extra weight-sixteen word for each
of k=4,5,6. Thus removing the extra filtration layers would be detected.
Normal and optimized (`-I -O -B`) executions produced byte-identical JSON.
All checks use explicit exceptions, not removable assertions. The self-test
also checks isolated optimized relocation, corrupt-receipt rejection, and
preservation of an existing output on a failed check. Expected output is
`PASS core_shortening_verify.py`; the deterministic receipt is
[CORE-SHORTENING-RESULTS.json](CORE-SHORTENING-RESULTS.json).


## Dependencies, interpretation and attribution

The signed proper-star definitions, paired-cube geometry, and predecessor
attribution follow [MINIMUM-WORDS.md](MINIMUM-WORDS.md) and
[HIGHER-WEIGHTS.md](HIGHER-WEIGHTS.md). The graph identification used for
V0 is proved in [HIGHER-GRAPH.md](HIGHER-GRAPH.md). The shortening
filtration above is proved directly from the proper-star generators,
without assuming that fixing original pairs also fixes their signs.

This note concerns C+ exactly. C− is a subspace, so it inherits the
weight-sixteen barrier and the weight-fourteen classification, but no
equality of the full two shortened spaces is asserted. The global
second-weight classification, without a preassigned common core, has
a separate proof in [FIFTH-WEIGHT.md](FIFTH-WEIGHT.md).

These are scalar information statements. They do not price source access,
helpers, frame changes, copies, restoration, or recursive children.

Prepared by Sam Sung with substantial OpenAI Codex assistance, including
separate AI-assisted proof review and an independently written finite
checker; Apache-2.0.
