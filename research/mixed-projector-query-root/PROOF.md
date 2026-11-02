# A mixed projector root for independent Gaussian outputs

This construction changes the caller. It keeps the complete PR6349 native
source. Four binary query suppliers, with 7, 2, 1 and 8 native leaves, enter
a six-field root. The root has three thin queries and three individual
whole idle jobs. It gives six independent Gaussian outputs. The child
suppliers give another 28 independent main outputs.

The conditional claim is kappa 0.00327980. The five inherited framework
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
P_i, and their native two-field bases C_i. Full sites are 0, 1, 4 and 6.
Sites 2, 3 and 5 are thin. In F coordinates the four projector masks are

| Site | Output coordinates in the stage | Rank | Native leaves | Extra whole idles |
| --- | --- | ---: | ---: | --- |
| 0 | 0,2 | 2 | 7 | none |
| 1 | 0,1,2 | 3 | 2 | one H16 |
| 4 | 0,3,4,5 | 4 | 1 | two H8 |
| 6 | 0,3 | 2 | 8 | none |

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
ABCD, B, AB, CD, C, C.
```

For child sizes 7,2,1,8, the six Gaussian ranks are 145,17,73,73,9,9.
No root input is owned or initialized. The scalar basis maps are invertible.

## 3. Binary children and full endpoint

PR6348 supplies the unchanged four-field binary query extension. Each node
combines two query suppliers, one paid thin query and two whole idle jobs.
It returns another query supplier and two independent Gaussian outputs.
Its separate Laurent checker is replayed here under its source hash.

The four child trees have 18 native leaves and 14 binary nodes. Their node
size counts are {2:8,3:1,4:3,7:1,8:1}. The root adds three thin queries.
The complete caller has 34 main fields per port, 18 distinct native stages,
17 thin queries, 14 paired whole idles and three individual whole idles.
Its 543 literal instructions include all basis maps and 20 normalizations.

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

The complete invoice has 67,092 paid jobs and 13,652 productive jobs.
Paid rank mass is 188,668; productive rank mass is 189,428. The surplus is
760. The maximum target rank is 145 and maximum paid rank is 64. The
emitted-event count agrees with a separate fixed-tree and root count.

The strict raw crossing is in (0.00327981076011,0.00327981076012), between
adjacent points on the 10^-14 grid. `RESULT.json` records both rational
moment engines, completion, compiler and outer ledger. The claim is
0.00327980; the tested
saving is 0.003279805. The completion uses power 1024, cutoff 12, floor 13,
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

The child-size discovery checked every tuple from 1 through 40 for this
fixed four-site root, at two floating trial savings. It selected 7,2,1,8.
That bounded search is not an exact optimality certificate or a search of
all root bases. The published bound depends only on the exact chosen word
and its complete rational replay.

## Scope and open next questions

The inherited assumptions are native_all_columns, owned_erasure, compiler,
precision_tape and analytic_recovery. Finite operator and compiler checks
do not discharge their full quantified statements. The large uniform word
and rounded multiplier are not materialized. No global optimality or
practical speedup is claimed. The selected frontier stays unchanged.

An independent reviewer should first check the global-field normalization,
the charged rank-three and rank-four projectors, and input independence.
Then replay the exact source and complete invoice. A later improvement can
change this root or combine it with a verified source, but must include
every changed productive debit, ordinary operation and compiler cost.
