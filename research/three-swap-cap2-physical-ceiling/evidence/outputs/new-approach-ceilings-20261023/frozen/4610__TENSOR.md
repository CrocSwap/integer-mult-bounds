# Native tensor products with paid completion of small targets

This construction applies to the all-fresh p7/keep232127 native word in
`NATIVE.md`. It retains the source all-column arbitrary-input semantics,
complete spectators, whole-job matchers, finite-program closure and integer
uniform compiler. The local word and controller come from zxv's PR4359;
the integer compiler is Jacob Alan Sussman's Theorem 1G. The tensor product
construction follows PR4414. Apache-2.0; substantial OpenAI/Codex assistance.

The new step is to complete small productive endpoints before choosing the
paid-rank cutoff. The enormous finite program is specified algorithmically;
it has not been materialized. Finite moment checks do not prove the inherited
analytic, precision, storage, fixed-tape or recovery premises. The selected
frontier is unchanged.

## 1. Chronological native product

Let U have productive ranks k_i and chronological paid ranks r_l, and V
have productive ranks h_j and paid ranks s_a. Their ambient ranks equal
their maximum productive ranks and contain every paid job. Work in the
product ambient space, retaining every unused coordinate as an arbitrary
spectator.

For each role j of V, instantiate a separate U copy at column count h_j.
Its independent arbitrary productive fields have labels (i,j). Give each
copy its own initialized, erased and uncredited center banks. Run these
copies in lockstep through their common scalar and paid-call list.

At paid position l, pause all copies. Copy j requests a rank r_l*h_j job
on its current physical owner. The owners are distinct across the copies;
they may include centers and may contain correlated values. Invoke V at
column count r_l on these j-indexed fields, using permitted role-specific
whole-job matchers. Its endpoints provide the requested ranks h_j*r_l.
Its owned centers have separate identities. Complete V and restore every
matcher before resuming the suspended U copies. Never combine different
paid positions of the same U copy.

This is a finite acyclic chronological substitution. Arbitrary-input
correctness allows correlated data in distinct slots; no input is copied
to create productive credit. Its final targets have ranks k_i*h_j and its
remaining paid jobs have ranks r_l*s_a. Thus both moments multiply.
The same argument lifts at every further positive column multiplicity by
substitution of the fixed coordinate, phase and scalar generators. It does
not tensor a sum of matrix operators.

For v copies of the p7 unit, write T_tau and P_tau for the raw target and
paid moments and B for the number of raw productive fields. The product
has B^v distinct productive fields, target moment T_tau^v, paid moment
P_tau^v, and ambient m^v where m=121.

## 2. Paid completion on the actual productive owners

Choose integers 1<c<b<m and put L=b^v, J=c^v. For every product role of
rank K<L, provide an additional paid positive transform on D=L-K disjoint
axes of that same physical owner. Roles with K>=L receive no completion.

For precision about coordinates, conjugate the complete existing product
word by its permitted per-role whole-job normalizers: the inverse map is
applied to each input and the corresponding map to its final output. This
gives the canonical rank-K endpoint on that field. After the whole product
has finished, apply the positive transform on axes K,...,L-1. The disjoint
factors commute and give exactly the canonical rank-L endpoint. Restore
the external matchers where the surrounding interface requires them.
A map only on the output would not be a whole-job conjugation.

Every field remains an arbitrary original productive input. There is no
new productive credit and no new owned bank. Since L<m^v, the needed axes
already fit in the complete ambient array. At larger column multiplicity,
use the corresponding disjoint column blocks. Completion runs after the
entire native product, so it cannot interfere with any suspended local
request, scalar contact or center cleanup.

The new targets have ranks max(K,L), hence moment at least T_tau^v.
Their minimum is exactly L and their maximum is m^v. Adding D target
rank and paying D rank preserves the original positive rank-one surplus.

## 3. Split every paid job and bound both tails

Write tau=1-C with 0<C<1. Replace each paid rank R>J by consecutive
jobs on disjoint axes of ranks J,...,J,r where R=qJ+r and 0<=r<J.
Omit a zero remainder. Keep the original whole-job normalizers around
this complete replacement. The exact disjoint-axis identity preserves
its endpoint and rank-one mass.

For an original paid job R>J, its new charge satisfies

```
q*J^tau+r^tau <= R*J^(-C)+J^tau <= 2*R*J^(-C).
```

Retaining the original moment as an overcount for the lower paid jobs
therefore bounds the original paid part by

```
P_tau^v + 2*P_1^v/J^C.
```

For each added completion D<L, the same partition gives the bound

```
charge(D) <= D*J^(-C)+J^tau < (L+J)*J^(-C) < 2*L/J^C.
```

This bound also covers D<J: then q=0 and D^tau<=J^tau. For D=0 there
is no job. Summing over at most B^v productive roles bounds all additional
completion calls by 2*B^v*L/J^C. Consequently the complete normalized
moment, using the lower bound T_tau^v on the new target moment, is at most

```
alpha^v + 2*gamma^v + 2*delta^v,
alpha = P_tau/T_tau,
gamma = P_1/(c^C*T_tau),
delta = B*b/(c^C*T_tau).
```

All three ratios must be below one. A favorable raw mixed moment alone
does not imply this construction. Every final paid rank is at most c^v,
strictly below every final target rank b^v. The complete target and paid
inventories are generated by exact finite products, completion and integer
division; no real-valued batching is used.

## 4. Exact finite p7 instance

The source-bound native audit supplies m=121 and the complete invoice

```
T = {5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224},
P = {1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}.
```

There are 7,688 productive fields and 55,998 paid calls. Their rank-one
moments are 131,723 and 131,115, with surplus 608. At the exact tested
saving C=0.00268648 the rational interval checker proves

```
alpha < 1-1/10^8,
gamma < 4991/5000       with c=10,
delta < 2/3            with b=11.
```

Take v=6240. The exact integer comparison
`(4991/5000)^390<1/2` gives gamma^v<2^-16. Also `(2/3)^2<1/2`,
so delta^v<2^-3120<=2^-16.
Bernoulli's inequality bounds alpha^v by 1/(1+v/10^8), so

```
alpha^v+2*gamma^v+2*delta^v
  < 1/(1+6240/10^8)+4/2^16 < 1.
```

This proves an explicit finite power. The checker separately rejects an
undamped completion tail and an insufficient single decay block. It also
checks the raw rank-one cutoff-base-five tail at this point: that simpler
tail condition fails, explaining why target completion is needed here.
The exact sufficient gap is greater than 0.00000136095023295546.
An earlier sufficient choice used v=30000, c=7 and b=8. The new parameters
reduce the finite tensor power and the derived uniform rank at the same
saving. No smallest tensor power or optimal native controller is claimed.

## 5. Effective uniform rank

The completed mixed unit has m_new=121^v, k_min=11^v and r_max<=10^v.
The exact comparison 10^26<11^25 gives theta<25/26; put h=1/26.
For ambient rank x>=m_new the inherited exit estimate gives

```
m_new*E(x)/x <= r_max*m_new^h*x^(-h)
                < 2^((111/26)*v)*x^(-h),
```

using 10<16=2^4 and 121<128=2^7. For a desired uniform exponent
z>t=1-C, put z0=(t+z)/2 and d=z0-t. The exact complement coefficient
eta=z0*m_new^(z0-1), with z0>1/2, satisfies

```
-log2(eta) < 1+7*v*(1-z0).
```

Thus rational sufficient choices are

```
H0 = ceil((((111/26)*v)*d+1+7*v*(1-z0))/(h*d)),
H1 = floor(H0*(1-z0)/(z-z0))+1,
N = 2^H1.
```

Check H0>=7v to cover all base ranks. Below the threshold, positive
rank-one surplus gives L(x)<=x. Above it, the source strong induction gives
L(x)<=A*x^z0 with A=(2^H0)^(1-z0). The strict H1 inequality then gives
L(N)<N^z. The endpoint script supplies exact H0 and H1 and replays all
outer predicates. It uses the actual new eta, not a dimension-independent
lower bound inherited from a small raw word.

## 6. Full constants and conditional scope

Expand the product, completion, splitting and uniform compiler. Let U_raw
count actual raw p7 instances and allocate O=U_raw complete owned-center
banks, retaining each until its owner erases it. This counts raw units,
not product macros. Let W be final productive width, P final rank-one
paid count, and R the complete count of non-scalar native records and
normalizers, including all completion, product and compiler routes.

With S=2490856, the authenticated raw scalar allowance in `NATIVE.md`, use
G=S*U_raw+8R as a conservative coefficient envelope. Pay actual coordinate
movement separately. Unit phases and coordinate permutations have zero
coefficient height. Substitute the new full-word constants

```
Z=W+O,
E=64*(Z+N+P+G+1)^3,
B_constant=P+E,
C0=32*N*B_constant^2.
```

The completed-child recurrence retains the form
`A(e)<=A(floor(e/N))+P*floor(e/N)+E`, hence A(e)<=2*B_constant*e.
Every allocated field, scalar record, phase, role route, parking stack
and borrowed-stock reserve comes from the newly expanded word. No old
small-word numerical reserve is substituted for these counts.

All these constants are finite and fixed before the multiplication input
varies. Their absorption still requires the stated inherited physical,
analytic, fine-prime, fixed-tape and exact-recovery hypotheses.

The related [PR4375 tensor-frame audit](https://github.com/CrocSwap/integer-mult-bounds/pull/4375),
read at head `9712f7cfc09723a557b3230a0d5e9826eaedcd2e`, concerns the
different PR4088/PR4100 profile. It distinguishes one rank-r*f child from
f scalar rank-r copies and leaves native frame realization and monomial
pricing open. The construction here requires the complete PR4359 all-column
contract: a paid position at column count f is one rank-r*f job, with every
whole-job route charged. Factorwise repetition is not a substitute for that
contract. The finite p7 geometry and moment checks do not independently
discharge this all-column native or tape-action premise.

Open next questions include reducing the sufficient tensor power, varying
the target completion and paid cutoff, and extending the native controller
only with independently verified contacts, phases and helper ownership.
