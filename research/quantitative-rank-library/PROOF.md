# Exact all-rank compiler metadata without expanding paid paths

Written proof with bounded exact corroboration; independent review is
recorded separately. No native admission or new kappa. Exact base and
predecessor pins are in `SOURCES.json`; the scope is recorded in `TASK.json`.

## 1. The retained flow and outputs

Fix nonempty target and paid histograms `(k,W_k)` and `(r,P_r)`, with
positive integer multiplicities and

```
2<=k_min<=k<=m=max k,       1<=r<=r_max<k_min.
```

Let d,q count distinct target/paid ranks and W=sum W_k, P=sum P_r.
These d,q are alphabet sizes, not the prime count in predecessor #4638.
Each productive role and paid position remains distinguishable. Numerical
metadata depends on the histograms; they do not certify a native word.
Any original paid-position order with these histograms has the same counts.

Use precisely FINITE-PRECOMPILATION sections 3--4, with
`G_n=floor(log_(k_min)(floor(n/m)))` at n>=m. A depth-h path has paid
product rho; a unit profile of degree G_n-h has target product c and
multiplicity u(alpha). It is present iff `m*rho*c<=n`. Its target k and
paid r jobs have true ranks rho*c*k and rho*c*r. Pascal matching is a
bijection of formal occurrences, never a quotient by equal products.

The outputs are evaluated binary integers: replication a_n, productive
width B_n, expanded rank-one leaf count P_n and expanded mixed-unit count
O_n. O_n is not peak live storage. If an actual unit contract supplies h
owned fields, h*O_n is a safe no-reuse count, before their physical extent.
Base rows are `a_n=B_n=1, P_n=n, O_n=0` for 1<=n<m.

## 2. Compressed exact source and exit counts

Define weighted ordered-word tables, retaining only nonzero entries:

```
T_0(1)=R_0(1)=1,
T_(g+1)(c)=sum_(k|c) W_k*T_g(c/k),
R_(h+1)(rho)=sum_(r|rho) P_r*R_h(rho/r).
```

T_g(c) sums u(alpha) over profiles of degree g and product c. R_h counts
all distinguishable paid paths. Coincident products add their counts.
Fix n and G=G_n. For every h+g=G and stored product pair with
`m*rho*c<=n`, put v=R_h(rho)*T_g(c). Add v to U_n; add W_k*v to A_s
at s=rho*c*k. If h<G, add P_r*v to I_s at s=rho*c*r. Then

```
S_s=A_s-I_s,                 S=sum_s S_s>0.             (1)
```

Proof: A counts all target slots with their complete formal multiplicity.
Every nondeepest paid demand is matched: after removing target factor k,
its child has dilation rho*r and column c/k, and
`m*rho*r*c/k < m*rho*c<=n`. The Pascal identity partitions the parent
occurrences among these child slots, including their first role. Conversely
every matched target slot has this incoming demand at the same true rank.
Subtracting counts leaves exactly the fresh targets, hence S_s>=0. A root
unit of column k_min^G exists, so S>0. This is a universal matching proof;
an executable nonnegativity assertion would not replace it.

Every deepest path is present because
`rho<=r_max^G<=k_min^G<=n/m`. It has one degree-zero unit and all its paid
jobs exit. Therefore

```
E_e=R_(G+1)(e)                                         (2)
```

counts distinct one-job cuts of rank e. E_e is not the number of arrays
available at any one cut. These counts agree with the source-row and
complement-port codecs' fresh physical identities; this evaluator does
not enumerate or route their physical rows.

## 3. Every batch constraint and expanded-count recurrence

Source complements occur upfront, so each s<n requires
`B_(n-s)|a*S_s`. Every individual exit requires `B_e|a`. By the existing
#4507/#5071 least-chronological theorem,

```
a_n=lcm({B_(n-s)/gcd(B_(n-s),S_s):s<n,S_s>0}
        union {B_e:E_e>0}),
B_n=a_n*S,                                             (3)
P_n=sum_(s<n)(a_n*S_s/B_(n-s))*P_(n-s)
    +sum_e E_e*(a_n/B_e)*P_e,
O_n=a_n*U_n+sum_(s<n)(a_n*S_s/B_(n-s))*O_(n-s)
    +sum_e E_e*(a_n/B_e)*O_e.                           (4)
```

The gcd/LCM formula is credited, not new. Repeated identical factors may
be removed from an LCM. Repeated cuts must remain in additive costs.
In particular `B_e/gcd(B_e,E_e)` is generally an invalid exit factor.
The s=n source receives no complement: no B_0 program is invoked.

All child ranks contract uniformly. A root source has target degree G+1,
so `s>=k_min^(G+1)>floor(n/m)` and integrality gives s>n/m. A nonroot
fresh source has a missing parent above the cap; multiplying that parent's
integer product by its positive last paid rank gives the same s>n/m.
Fit gives s<=n. Thus positive complement ranks obey
`n-s<(m-1)n/m`. Each exit obeys `e<=r_max*n/m<=(m-1)n/m`.
Set alpha=(m-1)/m: every recursive edge contracts by alpha.

Evaluating (1)--(4) for n=1,...,N therefore gives exactly the separated
literal flow's least-chronological library metadata. Native arbitrary-input
correctness, all-column lift, adapters, disjoint splitting and physical
finite closure remain the source's separate hypotheses.

## 4. Fully evaluated output sizes, without positive rank surplus

Assume N>=m; otherwise all rows are base rows. For positive x let
ell(x)=bit_length(x). Put L=ell(N), G=G_N, K0=max(W,P), and

```
Ubar=(G+1)*K0^G,       Sbar=W*Ubar,
F=1+(W+1)*Ubar+P^(G+1),       D=m*L.                    (5)
```

Deleting eligibility tests gives
`U_n<=sum_(h=0)^G P^h W^(G-h)<=Ubar`, and hence S_n<=Sbar.
The sum of smaller-batch multiplicities is at most Sbar+P^(G+1).
These bounds hold for every n<=N since G_n<=G.

### A cited width divisor, with no factorization cost

Let b count distinct integers >=2 among all target and paid ranks.
The rank semigroup has at most (L+1)^b products <=floor(N/m): each has
a representation whose b generator exponents are <=L. Repeated
representations only loosen this upper bound. Rank one is omitted.

#4638 proves, for this default policy, the all-prime divisor
`B_n | product_gamma S(gamma)^tau` for every n<=N, over source-count
plateaus up to the cap, with `tau=m*ceil(log2 k_min)`. Substituting the
generator-box and Sbar bounds yields the explicit integer envelope

```
beta=tau*(L+1)^b*ell(Sbar),
log2 B_n<=beta,             log2 a_n<=beta.              (6)
```

This uses all primes of the source counts, including new ones absent from
rank factors. No factorization, valuation algorithm or shared unevaluated
expression is used. The sharper multiplicative-rank result of #5962 is
available but unnecessary. Equation (6) instantiates an existing theorem;
it is not a new width asymptotic. It does not apply to the old nested
choice a_n=B_(n-1), which can have Theta(N log N) width bits.

### Expanded leaves and mixed-unit occurrences

Set Y_n=(B_n+P_n+O_n)/B_n. From (4), positivity and S>=1,

```
Y_n=1+U_n/S+sum_batches(t/S)*(P_q+O_q)/B_q
   <=(1+U_n+sum_batches t)*max_child Y_q
   <=F*max_child Y_q.                                  (7)
```

There is a deepest exit since P>0, so the maximum is nonempty. Base
ratios are n+1<=m. Bernoulli gives alpha^m<1/2; after D=m*ell(N)
contracting edges a positive rank would be below one. Every actual chain
therefore reaches a base rank in at most D edges. Iterating (7) gives

```
B_n+P_n+O_n<=B_n*m*F^D,
ell(B_n+P_n+O_n)<=beta+ell(m)+D*ell(F)+1.                (8)
```

This holds also for formal rules with zero or negative rank surplus.
No saving, moment-root or native-existence assertion is needed. All
replicated child copies remain counted.

## 5. Record counts and an explicit common bit cap

The total product-table and current-rank record counts are bounded by

```
M_T=binomial(G+d,d),       M_R=binomial(G+q+1,q),
V=binomial(G+d+q-1,d+q-1), E=binomial(G+q,q-1).          (9)
```

M_T covers target degrees 0..G; M_R covers paid degrees 0..G+1. For
h+g=G, stars and bars and convolution give at most V product pairs,
including rejected fits. The signed source list has at most (d+q)V
contributions before deduplication; E bounds distinct exits. Coincident
products do not increase these bounds. G=0 and singleton alphabets are
included in the displayed formulas.

Let S_bit encode both nonempty lists as Gamma(list length), followed by
Gamma(rank) and Gamma(multiplicity) for each entry. This counts supplied
histogram bits, not an independently supplied native word. Define

```
K=(S_bit+1)^2+d*M_T+q*M_R
  +(N+1)*((d+q+2)*V+E+G+2),
Z=8*(S_bit+L+(G+2)*ell(m+W+P+2)
     +beta+ell(m)+D*ell(F)+ell(K)+2),
J=M_T+M_R+(d+q+2)*V+E+G+S_bit+2,
L_local=J*Z.                                           (10)
```

Z bounds ordinary integer fields and arithmetic temporaries. Word-product
keys are at most m^(G+1). Weighted counts are at most the corresponding
powers of W and P. All target contributions together are <=W*Ubar;
matched incoming contributions are no larger, so signed partial sums
have magnitude <=2*W*Ubar. Equations (6)--(8) bound library values.
Division numerators such as a*S_s have at most the sum of operand bit
lengths, while each nonnegative completed summand is <=its final sum.
Loop counters and record addresses are covered by L, S_bit and ell(K).
Binomial bounds can be computed by successive exact multiply/divide
steps, whose intermediates add at most one factor's length. The generous
factor eight absorbs these fixed additions. No bound is emitted in unary.

Build each T/R degree by generating fixed-rank extensions, sorting and
adding equal keys. At most d*M_T+q*M_R records are generated. At each n,
enumerate (9), aggregate signed source records by sorting, and evaluate
(3)--(4) against the earlier completed library rows. All zero candidates,
all actual recursive ranks and every chronological exit divisor are paid.

## 6. Indexed and sequential construction models

### Indexed metadata

Specify indexed storage explicitly: fetching/storing an O(Z)-bit record
with an O(Z)-bit address costs O(Z) bit work. Schoolbook multiplication
and division cost O(Z^2). Euclid takes O(Z) divisions, so a conservative
gcd charge is O(Z^3). Comparison sorting k records costs O(k log k)
comparisons; log k=O(Z), so its bit bill fits O(k Z^2). Thus

```
T_indexed=O(K*Z^3).                                    (11)
```

The reference integer operations can be replaced by these elementary
algorithms. This is not a literal CPython-runtime guarantee or a claim
of free random access to native payloads.

### Sequential companion, with library access charged

Keep completed library rows in an append-only sequence with rank tags.
For every child access, scan at most N records, copy the selected row to
arithmetic tapes, and return the library head. Comparisons, copying and
return together cost O(N*Z). The earlier child values remain immutable.

Keep product tables and current-rank contributions in fixed local regions
of total extent O(L_local). Full scans and insertion sorting, including
copies, counter updates and head resets, cost at most O(L_local^2) per
generated record or recurrence operation. Elementary arithmetic uses
O(Z) workspace and O(Z^3) time per operation. Erase and reuse the same
local regions; their historical backing remains charged. These explicit
scan recipes give a fixed-number-of-tapes companion with

```
T_sequential=O(K*(N*Z+L_local^2+Z^3)).                  (12)
```

Python list access is not asserted to be a tape instruction. The four
library values, rank tags and work regions use O((N+J)*Z) historical
cells. Optionally retaining every per-rank source/exit census adds at
most O(K*Z) output bits; their writing fits both time bounds and their
backing is retained. Neither erasure nor streaming makes written output
free. Uniform parsing, validation and bound setup fit the S_bit term and
the explicitly counted arithmetic; alphabet-size dependence is retained.

For each fixed rule, G=O(log N) and all parameters in (9)--(10), apart
from N in K, are fixed powers of log N. Thus the indexed bound is
N*polylog N and the sequential bound is N^2*polylog N. Every output is a
fully evaluated integer of polylogarithmic bit length. Constants and
powers depend on the fixed rule through the displayed formulas. This
is not polynomial in log N: the output contains N library rows.

## 7. Scope and remaining obligations

This quantitatively evaluates the complete formal rank-induction
metadata for the separated default-height least-chronological policy.
It includes every source complement and each original exit divisor,
without enumerating P^G paid paths or W^G unit slots. The new computation
uses the existing width theorem; the normalized count estimate also
bounds expanded leaves/units when no positive rank surplus is assumed.

Actual scalar-word size is not determined by rank counts. It additionally
depends on the native word's instruction/constant encodings and on
whole-job adapter production. Such production bounds must be supplied
before an encoded native word or its physical runtime can be bounded.
An evaluated B_q is not proof of a valid smaller program. No arrays are
routed by this evaluator, and the native/all-column, ownership, precision,
fixed-tape payload, analytic and outer interfaces remain conditional.
No selected astronomical rank library or 1920-fold word is materialized.
There is no new kappa or foundational assumption discharge.

Credit #4507/#5071 for batch recurrences, #4638/#5962 for width envelopes,
Jacob Alan Sussman and zxv for the lockstep/Pascal flow, and the published
source-row/port packages for exact occurrence binding. All original source
notices are retained. Prepared for CubeJerry with substantial OpenAI
assistance; independent human or proof-kernel acceptance is not claimed.
