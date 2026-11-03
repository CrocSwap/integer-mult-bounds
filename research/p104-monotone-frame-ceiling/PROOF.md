# Exact monotone-frame cost and caller ceilings

## 1. Domain and statement

Use either exact scalar program in `CASES.json`. Both have 770 public fields,
29 owned labels and 104 main ports. The main roles are the live roles r and
r+112. Keep every scalar event, coefficient, COPY, INIT, CLEAR and owned
lifetime. Keep the source main input and output frames. Assign a binary
subspace U of F2^9 to each field segment between MOVE events. At an ADD or
COPY, the two field segments must have the same subspace. Public MOVE events
must go from U to V with U contained in V. Owned MOVE events must go in the
reverse direction. Keep these directions even when the two subspaces become
equal. Each public helper must have nested input and output subspaces.

Use the source canonical frame maps. A nested move of dimension difference r
costs H(r)=r^(1-kappa). A helper with forward dimension difference r earns H(r).
Set H(0)=0. Every other implementation condition can restrict this domain;
such a restriction cannot weaken a lower bound proved for the larger domain.
The proof does not assert that every assignment in the domain is a physical
native implementation.

Let D_U(kappa) be the sum of all paid MOVE moments minus all productive helper
moments for an assignment U. The main outputs are priced by the caller. Then:

1. For PR6453 at kappa=0.0032915, D_U is greater than 1734.45465379.
   Its improvement over the original local invoice is less than 0.053864.
2. For PR6529 at kappa=0.003293, D_U is greater than 1734.44478776.
   Its improvement over the original local invoice is less than 0.053888.
3. For each word and every U, the derivative of D_U is greater than 3866
   throughout 0<=kappa<=0.0034.
4. The PR6398 mixed root, with every positive integer child size, every binary
   child tree and every mixture of these native variants, has negative raw
   margin at its corresponding ceiling and above, through kappa=0.0034.

The domain fixes each source separately. A frame assignment for PR6453 is not
silently applied to PR6529. Both source words and both constraint systems are
rebuilt and checked.

## 2. Contact components and forced subspaces

Give each initial field and each new MOVE or INIT segment a distinct node.
Identify the two nodes at every ADD and COPY. This gives 1,063 components
for PR6453 and 1,061 for PR6529. Associate one unknown subspace U_a with each
component. Reverse owned edges, so every directed edge a->b means U_a<=U_b.
The fixed main boundary nodes give fixed subspaces.

Start with L_a={0} and K_a=F2^9 at unfixed nodes. At fixed nodes set both to the
fixed subspace. Propagate L forward by sums and K backward by intersections
until stable. Every legal assignment satisfies

```text
L_a <= U_a <= K_a.
```

This follows by induction at every propagation step. The original source
assignment is also checked against all resulting bounds. There are 757 and
755 components with different lower and upper bounds.

For an edge or any directed path a->b, put

```text
g_ab = dim(L_b) - dim(L_b intersection K_a).
```

Since U_a<=U_b, the quotient U_b/U_a contains the image of L_b. Thus
`dim(U_b)-dim(U_a) >= g_ab`. This remains valid when g_ab is zero.
For a pair of incoming edges a->c and b->c, dimension submodularity gives

```text
dim(U_a)+dim(U_b)-dim(U_c) <= dim(K_a intersection K_b).
```

For outgoing edges c->a and c->b, it gives

```text
dim(U_a)+dim(U_b)-dim(U_c) >= dim(L_a+L_b).
```

These statements use the actual binary subspaces. Dimensions alone would not
supply the right-hand sides. The checker computes each sum and intersection
as a set of the at most 512 binary vectors.

## 3. An exact relaxation of the complete local invoice

For each component a and each integer d between dim(L_a) and dim(K_a), use
one variable x_(a,d). Their sum at a is one. For each paid or helper edge,
use pair variables x_(a,b,d,e), with `e-d>=g_ab`. Their two marginals equal
the corresponding node variables. All variables are between zero and one.
Encode the path and fork inequalities of Section 2 as linear inequalities
in the expected dimensions.

A legal subspace assignment gives a zero-one feasible point: choose its exact
dimension at each node and its exact dimension pair at each edge. We do not
need the converse. Fractional points or unrealizable dimensions only enlarge
the feasible set.

Combine equal edges with signed integer weights. A paid MOVE contributes +1;
a public helper from its input component to its output component contributes
-1. Its tariff is

```text
weight * H(e-d).
```

A zero-weight edge can retain constraints. A zero-rank edge has zero tariff.
The public helper credit is not frozen at its source value. The complete
source controls are:

| Rank | PR6453 paid | PR6529 paid | Helpers in each source |
| --- | ---: | ---: | ---: |
| 1 | 2236 | 2234 | 14 |
| 2 | 453 | 453 | 8 |
| 3 | 491 | 491 | 4 |
| 4 | 109 | 107 | 107 |
| 5 | 151 | 153 | 15 |
| 6 | 8 | 8 | 3 |
| 7 | 9 | 9 | 9 |
| 8 | 1 | 1 | 39 |
| 9 | 0 | 0 | 363 |

Each paid mass is 5925 and each helper mass is 4205. Their difference is
1720. Owned reverse moves have total rank 56. These controls do not replace
the variable helper debit in the proof model.

The two exact models have respectively 13,266 and 13,132 variables, 12,793
and 12,697 equalities, and 119,534 and 119,463 inequalities. Their canonical
integer descriptions are bound by SHA256 in each dual certificate. Model
construction uses no solver.

## 4. Rational weak-duality certificates

Write the exact relaxation as Ax=b, Bx<=d, 0<=x<=1. For any rational y and
any componentwise nonpositive rational z,

```text
c*x >= b*y+d*z + sum_j min(0, c_j-(A^T*y+B^T*z)_j).
```

Indeed, `y*A*x=y*b`, `z*B*x>=z*d`, and each residual coefficient times
x_j is at least its minimum with zero. Thus a rounded dual does not need an
exact zero residual. The residual correction is included in full.

The four retained duals use integer numerators and denominator 10^10. The
checker validates each index, disallows duplicate indices, checks each upper
bound dual sign, reconstructs every residual and sums its negative part.
No numerical optimizer status is used as proof.

`exact.py` encloses every needed H(r) with integer intervals in units of
2^-160. To enclose log(r), reduce to a ratio in [1,2] and use

```text
log(a/b) = 2 sum_(j>=0) z^(2j+1)/(2j+1), z=(a-b)/(a+b).
```

Here 0<=z<=1/3. After 80 terms, the remaining sum is at most
`2*z^161/(161*(1-z^2))`. Every division rounds outward. The exponential
uses terms through degree 48 for an argument in [0,1]. Twice the outward
upper bound on term 49 bounds its tail. Inverting the resulting interval
for exp(kappa*log(r)) gives the H(r) interval. The replay checks the argument
bounds before each use. No floating value decides a proof condition.

For the derivative, a tariff w*H(r) has derivative -w*H(r)*log(r). If w>=0,
a uniform lower bound on [0,.0034] is -w*r*log(r). If w<0, a uniform lower
bound is -w*H_.0034(r)*log(r). Use outward endpoints for both expressions.
A separate rational dual for each word proves the lower bounds
3866.27671714 and 3877.25840291. Thus every fixed legal assignment has a
strictly increasing native deficit on this interval. The model itself does
not depend on kappa.

## 5. Every binary child and the complete fixed root

The root and recurrence are from PR6398 Section 5, retained byte for byte in
`input/ROOT-PROOF.md`. The source root has outputs with stage supports
ABCD, AB, CD, empty, C and B. It pays three thin queries and individual
whole idles for B and C. Every full site contains a binary query supplier.
A binary node with n leaves pays two whole idles H(8n), one thin query H(1),
and earns two independent main targets H(8n+1).

Let L be the certified native lower bound divided by 104. Let C(n) be the
minimum binary-node cost for n leaves. Then

```text
C(1)=0,
C(n)=min_(1<=a<n) [C(a)+C(n-a)+2H(8n)+1-2H(8n+1)].
G(n)=max_(1<=b<n) [H(8n+1)-nL-C(n-b)-C(b)+H(8b+1)-H(8b)].
```

For positive child sizes with pair totals x,y, the complete raw margin per
port is at most `H(8(x+y)+1)+G(x)+G(y)-2`. The negative native term uses a
uniform bound that holds for every legal variant. Each leaf can therefore
choose its own variant. No shared frame choice across leaves is assumed.
At the later ceiling, the earlier source also has a larger native lower
bound. Its certified value at the earlier ceiling is already larger, and
its deficit increases. Thus the later bound permits mixtures of both source
words as well as mixtures of frame assignments.
All native paid jobs, helper targets, binary queries, paired idles, root
queries and individual idles occur in this expression.

The checker uses lower bounds for C and upper bounds for each margin. For
each source it checks all 4,851 binary splits below 100 leaves and all 4,656
root pair choices with four through 99 leaves. The largest margin upper
bounds are less than -0.0005725 and -0.0010388. Both occur at total 18 and
pair totals 9+9. They are negative before any compiler or outer fee.

For a total N>=100, concavity gives `C(n)>=-(n-1)` and
`H(8b+1)-H(8b)<=H(9)-H(8)`. Jensen's inequality gives

```text
B(N)=H(8N+1)+2H(4N+1)-N(L-1)+2(H(9)-H(8))-6.
B'(N)=8(1-kappa)*[(8N+1)^(-kappa)+(4N+1)^(-kappa)]-(L-1).
```

For both sources B(100)<-1.86 and B'(100)<-0.059. Also B''(N)<0.
Thus B(N)<0 for every real N>=100. No larger tree is omitted.

Each positive H term decreases with kappa. Each increment H(r+1)-H(r)
for r>=8 decreases, because x^(1-kappa)*log(x) increases for x>=1.
Every binary-node cost consequently increases. Section 4 proves the same
property for every native deficit. Therefore each complete caller margin
decreases through kappa=.0034. The exclusions extend from their tested
ceilings to that cap, even if one chooses a different tree or frame
assignment at each kappa.

## 6. Interpretation and limits

The latest source comparison is PR6529's reported conditional .003288299.
The ratio `.003293/.003288299-1` is less than .00143. Thus the whole stated
frame-only class has less than .143 percent remaining headroom. This is an
upper bound on possible improvement, not an attained construction.

The proof does not cover scalar-word changes, added contacts, nonnested
Clifford frames, altered main boundaries, transported noncommuting codes,
a different root or a different binary module. It does not establish an
optimum for all P104 suppliers. Native phase correctness, physical ownership,
precision, compiler and outer admission of the source constructions are
retained premises; their full cold replays are not repeated here. Granting
all extra nonnegative costs zero is valid for a negative raw-margin result.
It would be invalid for a positive kappa claim.

Weak duality, the dimension identities and the series bounds are standard.
The new evidence is the source-specific joint constraint system and its
uniform all-size consequence with changed helper credits. All checks in this
package are author-side and AI-assisted. The donor's requested large complete
kappa improvement has not been achieved.
