# Integer replication and description-size bounds

This is a scoped written proof, not a formalization or native supplier admission. Its flow input is exactly Sections 3–4 of the pinned `FINITE-PRECOMPILATION.md`, with the all-column, disjoint-splitting, whole-job and finite-closure hypotheses retained. Jacob Alan Sussman's Theorem 1G supplies that finite flow; this note supplies the batch-sensitive integer recurrence and its size bounds. The rank inequalities and integer flow also make sense for an algebraic toy with no claimed native operator.

## 1. The fixed batch boundary

At rank N let S_s be the number of source jobs of rank s, S=sum_s S_s>0, U_N the number of unit instances in the unreplicated finite flow, and `(label,e,t)` the ordered exit batches. Labels include paid **positions**, so repeated equal paid ranks remain separate rounds. Every nonzero complement q=N-s and every exit e is strictly between 0 and N. The base programs at 1<=n<m have B_n=1, P_n=n and O_n=0, where O counts fully expanded instances of the mixed unit, not peak live fields or storage bits.

For each source rank s<N, put one complement batch `(q,t)=(N-s,S_s)` in the list R_N. Append every ordered exit batch `(e,t)` separately. Complement grouping is legal because all complementary jobs occur before the flow starts, on the a*S_s distinct original input arrays. Exit grouping across different chronological positions is not supplied by the theorem. Within each existing batch, the inherited arbitrary-input child program and whole-job adapters permit groups of B_q arrays.

For this fixed list of batch boundaries, define

```
a_N = lcm_{(q,t) in R_N} (B_q / gcd(B_q,t)),
B_N = a_N S,
P_N = sum_{(q,t) in R_N} (a_N t/B_q) P_q,
O_N = a_N U_N + sum_{(q,t) in R_N} (a_N t/B_q) O_q.
```

The lcm of an empty list is 1. These expressions are symbolic recurrences over finite integer flow counts and previously compiled widths; they do not expand the scalar word. O_N is the safe no-reuse count of unit instances. If each instance has at most h owned banks under the actual unit contract, h*O_N is a safe bank count, before accounting for each bank's physical extent. Without that contract, O_N alone is not a storage bound. Ordinary base-program work is counted in P; any base-owned auxiliary storage needs its own recurrence.

**Minimality and integrality.** For positive integers B,t,a, write B=gB' and t=gt' with g=gcd(B,t). Since gcd(B',t')=1, B divides at if and only if B' divides a. Hence every batch is integral exactly when a_N divides a. In particular a_N is the least positive replication for these specific batch boundaries and these already-fixed smaller widths. This is not optimality among different flows, chronological reorderings, or jointly redesigned smaller programs. The source's uniform-width choice `lcm_{q in D_N} B_q`, where D_N is the distinct required child-rank set, is a sufficient multiple of a_N and may be strictly larger.

Induction now gives positive integer B_N and nonnegative integer P_N,O_N. There are a_N U_N outer instances; each batch instantiates exactly a_N t/B_q complete child programs, each containing O_q units. Their unit tags are distinct. Adding these disjoint inventories proves the O recurrence. No blank owned field receives productive output credit. Each original input is still assigned to exactly one source, so there are exactly B_N productive arrays.

Dividing the P recurrence by B_N gives the source's exact normalized leaf identity. Thus batch-sensitive clearing changes the finite integer realization without changing its per-array leaf ratio, relative to the same previously fixed ratios. All scalar, routing, coefficient-height, erasure and precision counts are additional obligations; neither P nor O absorbs them.

## 2. Exact flow to which the recurrence binds

Write k_min=min{k:W_k>0}, m=max{k:W_k>0}, W=sum_k W_k and J=number of ordered paid positions. Assume m>=k_min>=2 and 1<=r_j<k_min. For N>=m, let G=floor(log_{k_min}(N/m)), computed by integer multiplication if evaluated. For a paid-position path p of length d, rho_p is the product of its paid ranks. For each multi-index a with |a|=G-d and m*rho_p*c(a)<=N, put

```
c(a) = product_k k^a_k,
u(a) = (|a|! / product_k a_k!) product_k W_k^a_k.
```

There are u(a) units in that class. A target role of rank k*rho_p*c(a) is a source exactly when p is empty or

```
m * (rho_p/r_last) * c(a) * k > N.
```

Otherwise the corresponding parent multi-index a+e_k is present and the Pascal bijection consumes all W_k*u(a) such roles. This is the precise missing-demand condition used by the verifier. Its independent literal construction represents each unit by a word of target **roles**, matches each eligible parent word to `(first role, suffix)` in the next class, and rejects any unconsumed parent demand. Distinct roles retain W_k multiplicity.

At depth G there is just a=0, u(a)=1. Every one of the J^G deepest classes is present because m*r_max^G<=m*k_min^G<=N. Thus each of its J paid rounds is a separate exit batch with t=1. In particular all J^(G+1) labels are retained even if their product ranks agree. In this exact unsplit Section-3 flow, the exit factors in a_N are therefore B_e themselves; the gcd improvement can only arise from source-complement multiplicities. The more general batchwise statement above also applies if a valid upstream flow supplies larger individual exit batches, but does not authorize merging them.

The code implements this source formula and compares it with the independently enumerated role-word construction for N=4,...,25. These fixtures support the implementation; the all-N statements depend on the source hypotheses and the argument above, not extrapolation from the fixture range.

## 3. Bit bounds without materializing the word

Let b_n=ceil(log2 B_n), o_n=ceil(log2(O_n+1)), both zero in the base range. The number of bits in B_n or O_n+1 is at most the corresponding bound plus one. Because a_N divides the uniform lcm and that lcm divides the product over **distinct child ranks**,

```
b_N <= ceil(log2 S_N) + sum_{q in D_N} b_q.
```

Let H_N=sum_{(q,t) in R_N} t. Since B_q>=1 and a_N>=1, the O recurrence gives

```
O_N+1 <= a_N (U_N+H_N+1) max_{q in D_N}(O_q+1),
o_N <= sum_{q in D_N} b_q
       + ceil(log2(U_N+H_N+1)) + max_{q in D_N} o_q.
```

Take the maximum over an empty child set to be zero in the logarithmic formula. These provide direct recursive upper bounds using only the finite flow and smaller bounds, even when exact B_N or O_N are too large to emit.

For a closed bound at an arbitrary finite N, put K=max(W,J) and

```
G_N = floor(log_{k_min}(N/m)),
C_N = ceil(log2 W) + ceil(log2(G_N+1)) + G_N ceil(log2 K),
D_N^* = 1 + ceil(log2(2+W+J)) + ceil(log2(G_N+1))
        + G_N ceil(log2 K).
```

Here D_N^* is a scalar bound, distinct from the child-rank set D_N. At depth d, deleting eligibility constraints bounds the total units by J^d W^(G_N-d), so U_N<=(G_N+1)K^G_N. There are at most W targets per unit and exactly J^(G_N+1) exits. Therefore S_N<=W U_N, H_N<=S_N+J^(G_N+1), and

```
ceil(log2 S_N) <= C_N,
ceil(log2(U_N+H_N+1)) <= D_N^*.
```

Both constants are nondecreasing in N. Since every child rank q<N, strong induction for m<=n<=N yields

```
b_n <= C_N 2^(n-m),
o_n <= C_N 2^(n-m+1) + (n-m+1) D_N^*.
```

For the first inequality, dominate the sum over distinct children by sum_{q=m}^{n-1} C_N 2^(q-m)=C_N(2^(n-m)-1). For the second, use this same sum in the o recurrence and the preceding rank's upper bound for max o_q. Its increase is C_N*2^(n-m)+(D_N^*), which dominates C_N(2^(n-m)-1)+D_N^*. The n=m case follows from o_m<=D_N^*. These bounds are deliberately loose, finite, uniform, and do not require constructing 2^(n-m) or B_n numerically: an expression tree with integer exponent n-m is enough.

For fixed unit data C_N,D_N^*=O(log N), so the bit length is bounded by O(2^N log N). This is an upper bound, not a measured growth rate or a lower bound. It is not a claim that emitting this many bits is practical.

## 4. Operations and bit cost are different

With h target types, the multi-index description contains at most `(G+1)*J^G*binomial(G+h-1,h-1)` class/index records; each checks h target types and performs O(h) integer arithmetic operations. The exact width recurrence adds a gcd per batch, lcm reductions and O(|R_N|) integer products/divisions per rank. Memoization constructs the needed smaller ranks once. These are counts of arithmetic operations, not unit-cost runtime claims: gcd, products, division and output all act on integers whose bit lengths must be charged separately. Exponents and multinomial coefficients also require their ordinary finite arithmetic. The direct role-word oracle is deliberately limited to tiny calibration inputs.

A safe exact evaluator must stop before its bit or record budget and leave the unevaluated recurrence as the answer. This verifier fixes N<=25, checks a 4096-bit output cap, and limits flow instances plus exits to 10,000. Its public helper also rejects N>25 before flow construction. It is not a general untrusted-input compiler; the recorded targets and paid list are small pinned constants. No giant N, compiled word, physical array or native product is materialized.
