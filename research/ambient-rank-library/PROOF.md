# Exact rank libraries at an independent ambient cap

This is a quantified metadata theorem and a scoped output-size obstruction.
It constructs evaluated integer library rows for every separated fixed rule
with ambient cap A at least its largest productive rank m. It does not
construct the rule's native word or admit a multiplication algorithm. Exact
source pins are in SOURCES.json. The ambient flow is inherited from the
selected retained compiler proof, §6; the least-cut recurrence is inherited
from #4507/#5071. The algorithm and cost framework extend #7345. The
plateau argument follows #4638, with its ambient dependence proved below.

## 1. Statement and the parameter boundary

Supply sorted nonempty histograms `(k,W_k)` and `(r,P_r)` of positive
integer multiplicities, and an integer A satisfying

```
2 <= k_min <= k <= m <= A,       1 <= r <= r_max < k_min.
```

Let d and q be the numbers of distinct productive and paid ranks,
`W=sum W_k`, and `P=sum P_r`. Each of the P paid sites remains distinct,
even when ranks or physical owners agree. Histograms suffice for the
numerical output; an ordered native manifest is a separate interface.

For every supplied positive maximum N, the algorithm evaluates, at all
`1<=n<=N`, the least chronological replication a_n, productive width B_n,
expanded rank-one leaf count P_n, and expanded mixed-unit count O_n.
O_n counts all executed unit occurrences, including recursive copies;
it is not a peak-live-storage or physical-cell claim. The construction
uses compressed product histograms, without enumerating paid paths.

For each *fixed* A and fixed target/paid histograms, every output integer
has a number of bits polynomial in log N. The indexed arithmetic work is
`N*polylog N`; the explicitly charged sequential companion is
`N^2*polylog N`. The constants and polynomial degrees depend on the fixed
rule. Equations (9)--(12) below expose that dependence when A is instead
part of a binary input.

There is no bound polynomial in `log N+log A` on individual output lengths
uniformly in A, even for fixed two-target and one-paid-site histograms.
For that family, writing every evaluated width through `N=2A-1` requires
Omega(N^2) bits. Thus the fixed-A indexed near-linear result does not
become a uniform near-linear result by treating A as an encoded constant.
This does not preclude polynomial algorithms in `N+log A`, compact symbolic
descriptions, alternate batching policies, or better bounds for selected
special histograms.

## 2. The actual ambient flow and its exact census

For `n<A`, use ordinary base rows

```
a_n=B_n=1,       P_n=n,       O_n=0.                    (1)
```

For `n>=A`, let `C=floor(n/A)` and `G=floor(log_(k_min) C)`; both are
computed by integer multiplication and comparison. A class at depth h is
labelled by a complete sequence of actual paid sites, with rank product
rho. Its degree `g=G-h` units are the productive-role words of length g.
A word of product c is retained exactly when `A*rho*c<=n`.
Grouping words by rank multiplicities gives the same multinomial units as
the selected source's definition. This is an exact occurrence expansion,
not a quotient identifying equal products or equal physical owners.

At a nondeepest parent, remove the first productive role k from its word.
At paid site r, the corresponding child has the extended paid path and
remaining productive word. Its ambient extent is

```
A*rho*r*(c/k) = (r/k)*A*rho*c < A*rho*c <= n.
```

It is therefore retained, and its target-k slot has exactly the parent's
paid rank `rho*c*r`. This association is injective: the child path's last
site and its target role reconstruct the parent. It is the ordered-word
form of the credited Pascal bijection. Every unmatched target slot is
a fresh top source. A root word of product `k_min^G` exists, so the flow
and its source set are nonempty. Every deepest paid path exists, since
`rho<=r_max^G<=k_min^G<=C`; it has one empty-word unit.

The compressed evaluator uses

```
T_0(1)=R_0(1)=1,
T_(g+1)(c)=sum_(k|c) W_k*T_g(c/k),
R_(h+1)(rho)=sum_(r|rho) P_r*R_h(rho/r).
```

At rank n, visit every product pair from `R_h,T_(G-h)`, retaining it when
`A*rho*c<=n`. With `v=R_h(rho)*T_(G-h)(c)`, add v to U_n and add W_k v
to the target count at `s=rho*c*k`. For h<G, subtract P_r v at
`s=rho*c*r` for consumed demands. The remaining counts S_(n,s) are the
literal fresh-source counts, so they are nonnegative and
`S_n=sum_s S_(n,s)>0`. The preceding injection proves this sign claim;
an implementation check is only a diagnostic.

The exit histogram is exactly

```
E_(n,e)=R_(G+1)(e).                                    (2)
```

Each summand represents a different complete chronological cut containing
one array per replica. Equal-rank exits have identical denominators but
remain separate events. E_(n,e) is their number, not a batch size.

## 3. Integrality, exact costs, and descent

Source complements are grouped before the flow. A positive complement
`n-s` therefore needs `B_(n-s) | a_n*S_(n,s)`. At each individual exit of
rank e, precisely a_n replicas are available, so `B_e | a_n`. These are
exactly the credited least chronological constraints, giving

```
a_n=lcm({B_(n-s)/gcd(B_(n-s),S_(n,s)): s<n,S_(n,s)>0}
        union {B_e:E_(n,e)>0}),
B_n=a_n*S_n.                                          (3)
```

The `s=n` source receives no complement and invokes no rank-zero program.
All exact expanded counts are

```
P_n=sum_(s<n) (a_n*S_(n,s)/B_(n-s))*P_(n-s)
    +sum_e E_(n,e)*(a_n/B_e)*P_e,
O_n=a_n*U_n+sum_(s<n) (a_n*S_(n,s)/B_(n-s))*O_(n-s)
    +sum_e E_(n,e)*(a_n/B_e)*O_e.                       (4)
```

In particular `B_e/gcd(B_e,E_(n,e))` is an invalid exit factor in
general. With A=4, targets `(3,2)` and paid sites `(2,2)`, the rank-12
flow has four sources of rank 9 and four distinct rank-4 exits. B_4=2,
and its least replication is 2. Pooling exits permits replication 1,
which fails each actual two-wide invocation.

A root source has target degree G+1, hence
`s>=k_min^(G+1)>C`, and its integer rank exceeds n/A. At a deeper fresh
slot, its absent parent has `A*rho_parent*c_parent>n`. Multiplying by
the last paid rank r shows the source rank exceeds `r*n/A>=n/A`.
Fit and k<=A give s<=n. Consequently every positive complement obeys

```
0<n-s<(A-1)*n/A.
```

An exit has at most G+1 paid factors, so

```
0<e<=r_max^(G+1)<=r_max*k_min^G
   <=r_max*n/A<=(A-1)*n/A.                             (5)
```

Thus every recursive rank decreases uniformly by the factor
`alpha=(A-1)/A<1`. Induction over n constructs (1)--(4) and proves that
all divisions are integral. No positive rank surplus, native realization,
or moment-root saving is needed for this numerical theorem.

## 4. Reproving the width divisor with A exposed

Let Gamma be the multiplicative semigroup generated by all productive and
paid ranks, including 1. Every fit threshold rho*c and each height
threshold `k_min^G` lies in Gamma. At fixed A the complete source census,
cut census, and unit census depend on n only through the set
`{gamma in Gamma:gamma<=floor(n/A)}`. They are constant on each plateau

```
A*gamma <= n < A*gamma_next,
```

where gamma_next is the next semigroup element. Since
`k_min*gamma in Gamma`, `gamma_next<=k_min*gamma`. Write S(gamma) for
the source count on this plateau. The source census as a function of cap
is the same one used at A=m; the recursive complements n-s are different.
No scaling of a default-A library is being asserted.

Fix any prime p, including primes absent from the rank generators. From
(3),

```
v_p(B_n)<=v_p(S_n)+max_child v_p(B_child).              (6)
```

Following maximizing children bounds this by a sum of source valuations
along one strictly decreasing rank chain. The chain may depend on p.
We bound every chain and do not choose a common maximizing chain.

Bernoulli gives `(A/(A-1))^A>2`, hence `alpha^A<1/2`. Set
`tau=A*ceil(log2 k_min)`; then `alpha^tau<1/k_min`. A chain cannot visit
one plateau more than tau times: its first rank is less than
`A*gamma_next`, so after tau edges it is strictly less than
`A*gamma_next/k_min<=A*gamma`, below that plateau. Visits are contiguous
because ranks decrease. Applying this to (6) for every prime gives the
all-prime integer certificate

```
B_n | Q_N = product_(gamma in Gamma, gamma<=floor(N/A))
                     S(gamma)^tau,      1<=n<=N.       (7)
```

This explicitly reproves the #4638 mechanism for independent ambient A.
Using `tau=m*ceil(log2 k_min)` here would be false: §7 gives actual
widths with more than m source factors on a single cap plateau.
Factorization is not used by the evaluator or required to apply (7).

For N>=A, define integers

```
L=ell(N), C=floor(N/A), H=ell(C), G=floor(log_(k_min) C),
Ubar=(G+1)*max(W,P)^G,        Sbar=W*Ubar,
F=1+(W+1)*Ubar+P^(G+1),      D=A*H,
```

where `ell(x)=bit_length(x)` for positive integers. Deleting fit tests
gives U_n<=Ubar and S_n<=Sbar at every n<=N. Let b count distinct
integers >=2 among the target and paid ranks. Every Gamma product <=C
has a representation with each of its b exponents between 0 and H.
There are at most `(H+1)^b` such exponent vectors; redundant
representations only weaken this upper bound. Thus

```
beta=tau*(H+1)^b*ell(Sbar),
log2 B_n<=beta,       log2 a_n<=beta.                   (8)
```

This uses all prime factors of each S(gamma), not just rank primes. The
semigroup bound counts locations and does not restrict width prime support.

## 5. Expanded costs and explicit metadata budget

For nonbase n put `Y_n=(B_n+P_n+O_n)/B_n`. Equation (4) yields

```
Y_n=1+U_n/S_n+sum_batches (t/S_n)*(P_e+O_e)/B_e
   <=F*max_child Y_e.
```

Here t=S_(n,s) for a complement batch and t=1 for each individual exit.
There is at least one exit, and base ratios are `1+n<=A`. Since
`N/A<C+1<=2^H` and `alpha^(AH)<2^-H`, D=A H edges reduce every rank
through N below A. Therefore

```
B_n+P_n+O_n<=B_n*A*F^D,
ell(B_n+P_n+O_n)<=beta+ell(A)+D*ell(F)+1.               (9)
```

All child copies, initialization of the integer rows, and expanded unit
counts are retained. An h-bank native unit would have h O_n bank
occurrences before any reuse; its physical extent and native setup are
outside this metadata theorem.

Let S_bit encode Gamma(A), then each histogram length and its positive
rank/count pairs with Elias Gamma codes, of length `2*ell(x)-1`.
The supplied maximum contributes L additional bits. No parameter is
assumed to fit a machine word. Stars and bars gives these record bounds:

```
M_T=binomial(G+d,d),          M_R=binomial(G+q+1,q),
V=binomial(G+d+q-1,d+q-1),    E=binomial(G+q,q-1).
```

M_T and M_R count all target/paid product records over the required
degrees. V bounds the pairs with h+g=G, including rejected fits; it
follows by convolution of the separate exponent-vector counts. E bounds
the degree G+1 exit products. Multiplicity and product collisions do not
increase these counts, and G=0 and singleton alphabets are included.

One explicit operation and ordinary integer-field budget is

```
K=(S_bit+L+1)^2+d*M_T+q*M_R
  +(N+1)*((d+q+2)*V+E+G+3),
Z=8*(S_bit+L+(G+2)*ell(A+W+P+2)
     +beta+ell(A)+D*ell(F)+ell(K)+2),
J=M_T+M_R+(d+q+2)*V+E+G+S_bit+L+3.                    (10)
```

These are evaluated integers, never unary strings or instructions to
construct `2^beta`. Parsing, summing histograms, generating degree tables,
integer height comparisons, binomial/envelope setup, writing the N base
or nonbase rows, zero-remainder checks, every child access, and each
recurrence summand are charged in K up to an absolute constant. Signed
source contributions use `(d+q)V` records. Ordinary product keys and fit
temporaries are bounded by `A*m^(G+1)`; weighted counts by powers of W
and P; signed partial sums by `2*W*Ubar`. Equations (8)--(9) bound row
values. A multiplication or division numerator temporarily adds operand
lengths; nonnegative cost summands are bounded by their final totals.
Addresses and loop counters are covered by L, S_bit and ell(K). The
factor eight covers these fixed additions. There is no exponentiation
with a_n, B_n, P_n, O_n, beta, or D as an exponent in the constructor.

The code uses deterministic sort-and-add product aggregation. In the
indexed metadata model, an addressed O(Z)-bit record read/write costs
O(Z), schoolbook multiplication/division costs O(Z^2), and a conservative
Euclidean gcd costs O(Z^3). Sorting generated records costs at most
O(K Z^2), because the comparison count adds a factor at most O(Z).
Consequently

```
T_indexed=O(K*Z^3).                                    (11)
```

The fixed-number-of-tapes companion stores completed rows in an immutable
rank-tagged sequence. Each child read scans at most N records, copies its
row, and restores the library head, costing O(N Z). Keep product and
current-flow records in O(J Z) local cells; full scans, insertion sorting,
copies and head resets cost at most O((J Z)^2) per record or recurrence
operation. Schoolbook arithmetic and gcd use O(Z) workspace and the
stated O(Z^3) time. Initialize, erase and reuse these regions, retaining
their historical backing in the stock bill. Thus

```
T_sequential=O(K*(N*Z+(J*Z)^2+Z^3)),
historical cells=O((N+J)*Z).                           (12)
```

Optional retention of every flow census adds O(K Z) written bits and
backing cells. The reference executable retains only product tables,
current census and output rows; independent verification separately
materializes bounded examples. Python indexing is not a tape primitive,
and neither (11) nor (12) describes native data movement or restoration.

If N<A, write (1) directly, with O(S_bit+N*ell(N+1)) bit work/space
up to elementary parsing overhead; no nonbase envelope is needed.
For fixed A and fixed histograms, all quantities in Z,J are fixed
powers of log N, proving §1. For variable A, tau and D contain its
*numerical magnitude*, not ell(A). Equations (10)--(12) state the actual
uniform bounds. The code's finite capacity refusals are not a proof that
an oversized mathematical library does not exist.

## 6. What is supplied to an abstract leaf locator

The output provides all integral widths and costs needed by a separate
chronological source/exit router at the same A, target ranks, paid ranks
and height rule. Every individual exit has a multiple of its child width;
source complements have their separately proved divisibilities; all ranks
descend. Ordered site names and owner tags can be supplied independently
without changing these counts. This supplies a valid-library premise,
not an owner-routing or numerical-execution proof.

The selected source uses A=153^1920 with separated target floor
12^1920, paid ceiling at most 11^1920, and maximum target 145^1920.
It lies within this theorem's *parameter domain*. Its actual evaluated
target/paid manifest, chosen winning N, and all rows through N have not
been materialized here. The selected rank `N=2^H_C` even has an enormous
binary representation. The isolated huge-A fixture in the verifier uses
the toy histograms of §7 and evaluates only integer *bounds and lengths*;
it is not a selected-instance table. Symbolic applicability does not
discharge native words, owned erasure, adapters, complete instruction
emission, physical tape routing, precision or analytic recovery. The
selected kappa remains 0.00363005817 and conditional.

## 7. A uniform ambient-output obstruction

Fix productive histogram `((2,1),(3,1))` and paid histogram `((1,1))`.
For every integer A>=4, the complete interval `A<=n<2A` has G=0:
one root unit, two source slots of ranks 2 and 3, and one rank-one exit.
Both positive complements have source count one. Thus

```
B_n=2*lcm(B_(n-2),B_(n-3)),       B_j=1 for j<A.
```

Strong induction makes every B_n in this interval a power of two. Put
`t=n-A`. Its exponent is exactly

```
b_n=floor(t/2)+1,       0<=t<A.                        (13)
```

For t=0,1 both predecessors are below A. For t>=2, the n-2 predecessor
has exponent floor(t/2); the n-3 predecessor, when nonbase, has no
larger exponent. The recurrence adds one. This proves (13) for the
whole interval, including both parity cases.

In particular `ell(B_(2A-1))=ceil(A/2)+1`, exponential in ell(A).
Because `N=2A-1`, it also exceeds every fixed polylogarithm in N and A
as A grows. Summing the exact lengths gives

```
sum_(n=A)^(2A-1) ell(B_n)
 =sum_(t=0)^(A-1) (floor(t/2)+2)
 =floor((A-1)^2/4)+2A = Omega(A^2).                   (14)
```

These bits occur in the required explicit width output alone, before
replication, leaves, unit counts or source access. Any sequential binary
output of the evaluated all-rank library therefore needs Omega(N^2)
bit writes on this varying-A family. The obstruction is to a uniform
`N*polylog(N,A)` explicit-output bound; it is not a lower bound against
every algorithm polynomial in N, or against compressed expressions.

The same family falsifies an unqualified reuse of default tau=m. For
A>=7 and C=1 there is only one plateau, S(1)=2, and default tau=3
would give Q=8, whereas `B_(2A-1)=2^ceil(A/2)` does not divide 8.
The new tau=A certificate is valid. This is a universal exact example,
not extrapolation from the finite corroborations.

## 8. Verification and remaining obligations

The production evaluator adapts #7345 and therefore is not independent
of it. A separate oracle imports no production code: it enumerates every
productive-role word and paid-site path, constructs all target ports,
marks actual incoming parent demands, and retains distinct exit cuts.
It computes widths by prime-exponent constraints and costs using exact
rational per-array recurrences. All rows and census fields are compared.
An independent multiplication-closure enumeration checks the plateau
divisor with exact integer divisibility at every tested rank. Mutations
exercise lost ambient caps, wrong bases, pooled exits, omitted repeated
cuts, and a false default-width envelope. Default-A outputs are also
compared against the frozen predecessor as regression evidence.

Bounded checks do not establish universal quantifiers; §§2--7 provide
the written argument. No human or formal-kernel acceptance is claimed.
Open tasks include a caller-bound evaluated selected manifest, a full
scalar/phase/adapter instruction emitter, physical gather/return pricing,
and tighter source-specific widths that exploit gcd cancellation. An
ambient-independent bound would need a changed output or extra hypotheses
excluding §7; no such change is assumed here.
