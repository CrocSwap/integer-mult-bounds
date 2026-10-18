# Sharp rank-six three-piece shortening on P112

Fix the 112 nonframe E8 root lines and nine-bit labels reconstructed by the
pinned geometry. Let K have characteristic zero. With doubled root
representatives r_t, put

```text
C = {(r_t dot h)_t : h in K^8}.
```

For a common coordinate set S, let pi_S delete S. The binary support rank of
a piece is the F2 rank of its live labels. Coefficients belong to K.

**Theorem.** If |S| <= 29 and each of three residual pieces has binary support
rank at most six, their span meets pi_S(C) in dimension at most one. The
pieces may be dependent and their coefficients are arbitrary. The uniform
threshold 29 is sharp. The literal common-cut-30 witness in RESULT.json has
three independent pieces of binary rank six and code intersection dimension
two.

PR3255, pinned at `2977a895c35fa019f53f181edee45177c77ec436`, proved the
sufficient threshold 21 using singleton capacity sixteen. The new step
couples singleton capacity to the endpoint's total support and retains the
actual orthogonal puncture. No historical profile exclusion, full C5,
decoder floor, supplier, all-size multiplication theorem or kappa follows
from this package alone.

## Geometric dependencies

The pinned root-simplex proof supplies these characteristic-zero statements.
Every nonzero word of C has support at least 53. Any nonzero word with support
strictly below 70 is proportional to a root word. Every third root line in
a plane through two root lines is the A2 sum or difference. The primary
replay checks the finite chamber counts, all 960 simple reflections and all
7,140 root-line pairs underlying those statements. The Weyl-chamber theorem
and its rational-kernel extension remain written dependencies.

Every binary six-space contains at most twenty P112 labels. The replay
checks all 788,035 such spaces through unique three-dimensional annihilators.
A lower-dimensional space extends to a six-space, so the bound holds for
binary rank at most six.

There are 1,120 A2 root planes in E8. The eight simple reflections act
transitively on them. On the fixed P112, their nonzero evaluation unions
have sizes 78 and 80, with multiplicities 896 and 224. The corresponding
full E8 union has 84 lines. Thus the orthogonal eight-line frame removes
at most six positive coordinates, improving the arbitrary-eight-cut
relaxation used in PR3255.

The replay checks transitivity and verifies that each reflection induces an
invertible linear map on the nine-bit labels. Specifically, the labels span
nine dimensions and the 120 paired input/output labels span the graph of a
nine-dimensional linear map. The root permutation is bijective. Hence
binary ranks and the closure bounds below transport to every A2 plane.

## Normalize a putative two-dimensional intersection

Replace each piece by its restriction outside S and call the pieces q_i.
No nonzero scalar multiple of one q_i can belong to pi_S(C). Its unique
code lift would have support at most |S|+20 <=49<53. The same distance
bound makes pi_S injective on C.

Suppose D = span(q_0,q_1,q_2) intersect pi_S(C) has dimension at least two.
The pieces must be independent. Otherwise their span has dimension at most
two and equals D, contradicting the preceding observation for any nonzero
piece. Their span has dimension three and D has dimension exactly two,
since dimension three would again put every piece in pi_S(C).

The quotient by D is one-dimensional and each q_i has nonzero image.
Rescale the pieces so that their quotient images agree. Supports and
binary ranks do not change. The two differences q_1-q_0 and q_2-q_0 are
independent restricted codewords. Lift them uniquely to c_h and c_k.
Each of c_h, c_k and c_h-c_k has support at most |S|+40 <=69<70, so each
is a nonzero scalar root word.

The root-plane fact gives h=z*a and k=z*b for one nonzero z in K and
oriented doubled roots with a dot b=4. Indeed, the third root direction
forces the two scalar coefficients to have ratio +1 or -1. Orient the
roots to absorb the signs. Their difference is then a root. This reasoning
also holds over K by solving a nonsingular rational coordinate minor.
The vertices 0,a,b are an A2 simplex. Outside S the three piece values are
z times its evaluations plus one arbitrary coordinate shift. In particular,
the shift need not minimize support.

## Joint singleton and total-support capacity

For the simplex 0,a,b, full E8 has 36 coordinates where the evaluations
agree, three where they are all distinct, and three disjoint singleton
classes A_i of 27 coordinates each. In A_i, endpoint i differs from the
other two equal endpoints. Each A_i spans a binary seven-space W_i.

Here is the complete hyperplane inventory inside any one W_i. The first
column counts all full E8 labels in a hyperplane V; the second counts
labels from A_i.

| Full support | Singleton support | Hyperplanes |
|---:|---:|---:|
| 0 | 0 | 1 |
| 12 | 11 | 27 |
| 12 | 12 | 36 |
| 16 | 15 | 36 |
| 16 | 16 | 27 |

The 127 nonzero functionals of W_i enumerate its 127 hyperplanes exactly
once. Their maximum support-plus-singleton count is 32. The separate
2,667-subspace census in each W_i shows that any binary space of dimension
at most five meets A_i in at most ten labels. These are full E8 statements;
removing frame or common-cut coordinates cannot increase the bounds.

Consider the actual binary support span V_i of q_i. If
`dim(V_i intersect W_i)<=5`, its singleton support is at most ten and its
total P112 support at most twenty, giving sum at most thirty. Otherwise
V_i has dimension six and is contained in W_i. It is one of the enumerated
hyperplanes, whose total full E8 support plus singleton support is at most
32. The actual supports are subsets of those intersections. Therefore,
with M_i the total residual support and J_i its own singleton support,

```text
M_i + J_i <= 32.
```

This argument covers all ambient six-spaces, including those not contained
in a singleton seven-space. It does not assume that a piece fills its
binary closure or uses a modal shift. A change of simplex orientation
permutes its three large projective fibers, so the checked three classes
and plane transitivity cover every normalized simplex.

## Count arbitrary shifts

Let U be the union of the two full code supports. The A2 inventory gives
|U|>=78. Write x_i(t)=1 when q_i(t) is nonzero. At a singleton coordinate
of A_i outside S, an arbitrary common shift satisfies

```text
x_0(t)+x_1(t)+x_2(t) >= 2-x_i(t).
```

If x_i=0, both other values are nonzero. If x_i=1, the sum is at least one.
At an all-distinct coordinate the sum is at least two. Sum over U outside S.
Extra piece support elsewhere only increases M_i. Consequently

```text
2*|U minus S| <= sum_i (M_i+J_i) <= 96.
```

For |S|<=29 the left side is at least `2*(78-29)=98`, a contradiction.
This proves the theorem over every characteristic-zero field.

## Literal sharpness witness at thirty

Use the doubled roots

```text
a = (0,0,0,0,0,2,-2,0),
b = (0,0,0,-2,0,2,0,0).
```

Their live union has 78 coordinates. For each singleton class choose the
lexicographically first sixteen-label hyperplane intersection containing
only live labels. Each chosen set has binary rank six. The sets are
disjoint. Delete the other thirty union coordinates as ONE common set S.
On the chosen singleton supports define

```text
q_0(t) = -(a dot r_t),
q_1(t) =   a dot r_t,
q_2(t) =   b dot r_t,
```

respectively, and set each piece to zero elsewhere. Then outside S,
`q_1-q_0=pi_S(c_a)` and `q_2-q_0=pi_S(c_b)`. All 48 support coefficients
are nonzero. The exact indices and coefficients are committed in
RESULT.json and regenerated from the pinned source ordering. Rational
elimination gives code rank 8, piece rank 3 and joined rank 9. Thus the
intersection dimension is exactly `8+3-9=2`. No finite counting equality
is substituted for this actual witness.

## Credit and limits

The affine quotient and arbitrary-shift argument follows Nick Petalas's
PR3255. The rank-five capacity and projective-fiber perspective follow
PR3249, with the root-simplex geometry from the retained PR3161/3162/3164
lineage. DreamingOfClouds/PR3154 supplies the C5 motivation. The original
E8/P112 lineage, including joaqcoo, retains its credit.

Worker1's concurrent rank-five equality audit and worker5's mixed-rank
caller have distinct endpoint hypotheses. No result from either is needed
here. A use in TWOSIDE still needs a separately checked caller reduction.
This proof is written and supported by finite exact checks. It is not a
proof-kernel or independent human verification.
