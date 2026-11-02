# A mixed projector root for independent Gaussian outputs

This construction changes the caller. It keeps the complete PR6349 native
source. Four binary query suppliers, with 7, 2, 2 and 7 native leaves, enter
a six-field root. The root has three thin queries and two individual
whole idle jobs. It gives six independent Gaussian outputs. The child
suppliers give another 28 independent main outputs.

The conditional claim is kappa 0.00328467. The five inherited framework
assumptions remain. This is not an unconditional multiplication theorem,
a materialized uniform word or an independent scientific review.

## 1. An ordinary normalization of the native query

Write q = Q^-1 for the actual common central Gaussian. The native checker
verifies Q^2 = Q^-2 = X with absolute phase +1. X is an ordinary translation
and X^2 = I. These identities hold under the retained tensor implementation.
Define

```text
lambda = (1+i)I/2 + (1-i)X/2,
lambda^-1 = (1-i)I/2 + (1+i)X/2,
S = lambda q.
```

Then lambda^2 = X, S^2 = I, and lambda^-1 S = q. All these operators commute
with the fresh stage products D. The normalization is applied to the complete
field, using its global translation X. Its scalar coefficients stay outside
tensor powers. In general S is not the tensor power of the one-column S.

The translation has disjoint two-address orbits. On one orbit lambda has
matrix [[a,b],[b,a]], where a=(1+i)/2 and b=(1-i)/2. Four ordinary complex
scalar operations implement it in place:

```text
x <- x - i*y
x <- a*x
y <- (1+i)*y
y <- y - i*x.
```

Conjugate each coefficient to implement the inverse. No owned field, paid
Gaussian job or productive input is added. The pair map is unitary; each
displayed operation has growth at most two in the maximum norm. There are
four operations per address pair. A loop over the existing translation
pairs has linear data work. The ordinary-work bill below includes these
operations and translations.

A child supplies D U(q), where U(q)=I+q E01, on two arbitrary fields.
Conjugation by diag(lambda,1), followed by U(-1), gives
D U(S-1). A thin query has the same conversion and retains its paid H1
charge. Thus the central-involution root below has an actual native
implementation. Its output S is converted back to q by lambda^-1.

## 2. The six-field root

Use the shortest-query normal form from
`research/five-call-projector-rigidity/PROOF.md`. For i=0,...,5 set u_i=e_i.
Set u_6=(-1,1,-1,1,-1,1), and (v_i)_j=sign(i-j). Let R_i=u_i v_i.
Each R_i is square-zero and has rank one. Direct exact multiplication gives

```text
(I-2R_6) ... (I-2R_0) = -I_6.
```

`ROOT.json` specifies an invertible rational basis F, four stage projectors
P_i, and their native two-field bases C_i. Full sites are 0, 1, 5 and 6.
Sites 2, 3 and 4 are thin. In F coordinates the four projector masks are

| Site | Output coordinates in the stage | Rank | Native leaves | Extra whole idles |
| --- | --- | ---: | ---: | --- |
| 0 | 0,1 | 2 | 7 | none |
| 1 | 0,1,5 | 3 | 2 | one H16 |
| 5 | 0,2,4 | 3 | 2 | one H16 |
| 6 | 0,2 | 2 | 7 | none |

The exact checker verifies P_i^2=P_i, P_i R_i=R_i P_i=R_i and pairwise
commutation of the four P_i. It also verifies that P_i commutes with the
query prefix (I-2R_i)...(I-2R_0). These conditions permit each independent
stage factor to move past its own query prefix. The two central characters
then give the same diagonal stage product, with scalar factor +1 or -1.
The checker also multiplies every independent stage coefficient directly.

At a full site, C_i takes R_i to E01 and P_i to diag(I_r,0). Apply the child
supplier to the first two coordinates. Apply D_i separately to each of the
remaining r-2 coordinates. These are exactly the charged whole idle jobs.
All basis changes are emitted as rational ADD, SCALE and SWAP operations.
At a thin site, the corresponding C_i converts one paid query to R_i.

Apply F at entry and F^-1 at exit. Apply lambda^-1 to all six root outputs.
Their independent stage supports are

```text
ABCD, AB, CD, empty, C, B.
```

For child sizes 7,2,2,7, the six Gaussian ranks are 145,73,73,1,17,17.
No root input is owned or initialized. The scalar basis maps are invertible.

## 3. Binary children and full endpoint

PR6348 supplies the unchanged four-field binary query extension. Each node
combines two query suppliers, one paid thin query and two whole idle jobs.
It returns another query supplier and two independent Gaussian outputs.
Its separate Laurent checker is replayed here under its source hash.

The four child trees have 18 native leaves and 14 binary nodes. Their node
size counts are {2:8,3:2,4:2,7:2}. The root adds three thin queries.
The complete caller has 34 main fields per port, 18 distinct native stages,
17 thin queries, 14 paired whole idles and two individual whole idles.
Its 570 literal instructions include all basis maps and 20 normalizations.

The full replay uses exact coefficients in Q(i)[Q,D_1,...,D_18]/(Q^4-1).
It checks all 1,156 input/output entries. Stage variables remain distinct.
It checks the complete Gaussian endpoint, not only the S=+1 and S=-1 cases.
Missing native calls, thin queries, paired idles, individual idles,
normalizations and central translations are rejected.

Each native call receives 562 independent helper inputs. These are separate
from all main fields and from every other call's helpers. There are
18*562+34*104=13,652 productive fields. Calls execute in sequence. The 29
owned labels, 32 native lifetimes and peak 13 fields remain as in PR6349.
Thin-query storage is reused between calls. Normalization adds no storage.

The physical checker verifies all 7,488 native contacts, their absolute
phases, every output Gaussian and every paired or individual idle. The
fresh stage axes are orthonormal and fix the central port. The source word
receives its complete arbitrary-input, dense-transpose and native replay.

## 4. Complete price and outer transfer

The complete invoice has 66,988 paid jobs and 13,652 productive jobs.
Paid rank mass is 185,340; productive rank mass is 186,100. The surplus is
760. The maximum target rank is 145 and maximum paid rank is 56. The
emitted-event count agrees with a separate fixed-tree and root count.

The strict raw crossing is in (0.00328468791927,0.00328468791928), between
adjacent points on the 10^-14 grid. `RESULT.json` records both rational
moment engines, completion, compiler and outer ledger. The claim is
0.00328467; the tested
saving is 0.003284675. The completion uses power 1024, cutoff 12, floor 13,
offset 1/7, reserve 10^-12 and decay 31/32. The logarithm power is 1100.
All local native, route and scalar costs remain charged. The new caller
uses a conservative 32 real scalar units per field per instruction,
including the normalization. Its complete ordinary bound is below 10^9.
The retained admitted BIT saving is .0034. All 54 strict and four functional
outer predicates must pass.

The comparison is PR6353's published conditional .00315057. The present
source is PR6349; it does not consume PR6353's output-contracted word.
The source-relative gain is from the new caller, not new digits of an old
crossing. PR6353 and PR6350 retain their separate construction credit.

The basis search checked 241,886,080 bounded bases modulo 65521. It found
695 support patterns. Floating searches selected the rank 2,3,3,2 pattern.
The exact rational checker then verified the chosen basis and every stage
coefficient. This finite search does not prove a global basis optimum.
The new child-size search selected 7,2,2,7. Section 5 gives an exact ceiling
for all binary children of this fixed root.

## 5. A ceiling for every binary child size of this root

This statement keeps the root and the PR6349 native source fixed. It permits
all positive integer child sizes and all binary tree shapes. Let H(r)=r^t,
t=1-kappa, and let L be the native paid-minus-helper moment per port.
Let C(n) be the minimum binary-node cost for n leaves. Then

```text
C(1)=0,
C(n)=min_{1 <= a < n} (C(a)+C(n-a)+2H(8n)+1-2H(8n+1)).
```

For a pair with total n, the best root contribution is

```text
G(n)=max_{1 <= b < n}
     (H(8n+1)-n L-C(n-b)-C(b)+H(8b+1)-H(8b)).
```

For four positive children, with pair totals x and y, the complete margin
per port is H(8(x+y)+1)+G(x)+G(y)-2. The two pairs contain all root outputs,
three thin queries, both individual idles and every binary-node job.

At kappa .00328469, `ceiling.py` uses rational outward intervals. It checks
all 4,851 binary splits below 100 leaves and all 4,656 root pair choices with
four through 99 leaves. Every margin upper bound is strictly negative.

For larger totals f, concavity gives C(n) >= -(n-1) and
H(8b+1)-H(8b) <= H(9)-H(8). Jensen's inequality gives the upper bound

```text
B(f)=H(8f+1)+2H(4f+1)-f(L-1)+2(H(9)-H(8))-6.
```

The checker proves B(100)<0 and B'(100)<0 with rational intervals. Since
t is strictly between zero and one, B' decreases. Thus B(f)<0 for every
real f>=100. No larger binary tree is omitted.

The native deficit L has strictly positive derivative throughout
0<=kappa<=.0034. The checker proves this with an interval lower bound above
42. Each binary-node cost increases with kappa, while each positive H term
and each increment H(r+1)-H(r) decreases. Thus every root margin decreases
throughout the retained BIT admission range. Failure at .00328469 also
excludes every larger saving in that range.

This fixed root cannot reach .00328469 with the retained native source.
The claim .00328467 is within .00000002 of that ceiling. This is a scoped
ceiling, not a bound for other roots, source words or query interfaces.

## Scope and open next questions

The inherited assumptions are native_all_columns, owned_erasure, compiler,
precision_tape and analytic_recovery. Finite operator and compiler checks
do not discharge their full quantified statements. The large uniform word
and rounded multiplier are not materialized. No global optimality or
practical speedup is claimed. The selected frontier stays unchanged.

An independent reviewer should first check the global-field normalization,
the two charged rank-three projectors, and input independence.
Then replay the exact source and complete invoice. A later improvement can
change this root or combine it with a verified source, but must include
every changed productive debit, ordinary operation and compiler cost.
