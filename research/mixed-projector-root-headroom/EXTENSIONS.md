# Two further limits of the mixed root

These results do not add a kappa increment. The first result removes one
possible way to evade the shortest-query model. The second result bounds
the complete price of a specified fifth-stage extension. Neither result
is a global optimum for kappa.

## 1. Outputs without the central transform

Let the central endpoint at S=-1 be J=diag(-I_r,+I_s), where r>=2 is even.
Permit any number s of arbitrary extra inputs. Use exactly r+1 rank-one
square-zero queries. Keep independent forward stage variables and scalar
bases independent of S and those variables. The coefficients commute
with these operators. Require the endpoint
diag(S I_r,I_s) diag(product_i D_i^epsilon_ji), with epsilon_ji in {0,1},
after constant boundary changes independent of S and the D_i. Each stage
acts only at its own full site.
Each stage dimension outside its two-field query plane has a paid whole
idle. No helper output is consumed. Under this contract, the extra outputs
without S cannot improve the signed price over the r active fields alone.

Write U for the query columns, V for the rows, G=VU, and L for its strict
lower part. The chronological expansion gives

```text
U A V = E,     A=(I+2L)^(-1),     E=(I-J)/2=diag(I_r,0_s).
```

Both U and V have rank at least r. They cannot both have rank r+1: an
injective U, invertible A and surjective V would give rank r+1 to their
product. Thus at least one has rank r.

Suppose rank(U)=r. Its image equals im(E), so every query column lies in
the active space. All queries have zero lower blocks. Their active blocks
therefore multiply to -I_r. Let V_a be the restriction of V to that space.
Then U_a A V_a=I_r. The matrix A V_a U_a is an idempotent of rank r on
r+1 coordinates. Consequently

```text
Z=I+2L-V_a U_a
```

has rank one and diagonal entries one. All its off-diagonal factorizations
are nonzero. They give the usual shortest-query Gram normal form. In
particular, no active query disappears. Each active query remains a
nonzero rank-one square-zero operator. If rank(V)=r, apply the same
argument to the reversed transpose word. This covers both possible cases.

At S=1, the first derivative in each independent stage variable identifies
its projector P_i with an output mask. At S=-1 the constant endpoint is J
in the same output basis. Thus every P_i commutes with J and splits into
active and inactive blocks. The active block contains both the query
column and row; it has rank at least two. Compression therefore preserves
a legal active query and all active stage incidences. Compression is valid
here because all queries have the same one-sided block containment. It
would not be valid for unrestricted cross-block queries.

On an inactive output, let the incident child sizes be n_1,...,n_k. Its
productive rank is 8(n_1+...+n_k), without the extra central rank one.
It pays each of the whole idles 8n_j. For H(x)=x^t, 0<t<1,

```text
H(8(n_1+...+n_k)) <= H(8n_1)+...+H(8n_k).
```

This follows from concavity and H(0)=0, by induction on k. An output with
no stage has rank zero and gives no credit. Remove these outputs and
their idle charges. The active signed margin cannot decrease. Omitting
their ordinary costs only makes this price comparison more favorable.

For r=6, an extension with two active extra idles is consequently subject
to the existing minimum-idle ceiling. Extra paid inactive fields do not
evade it. More than r+1 queries, consumed helpers, a different idle
contract, or variable-dependent coefficients remain outside this proof.
In particular, seven queries on four active and two inactive fields
are outside the theorem: r+1 would be five queries in that case.

The replay checks eight exact coupled examples and their reversed
transposes. Their queries do act on the inactive inputs, and their cross
terms cancel only at the final endpoint. These examples check that the
proof did not assume each query commutes with J. The quantified rank and
tariff arguments above supply the proof for arbitrary r and s.

## 2. A fifth full stage with rank four

This price exclusion uses H(x)=x^(1-kappa). The two checked instances
are PR6353 at kappa=0.00328554 and PR6375 at
kappa=0.00328621476572836015146308. The quantifier over all sizes and
shapes is at each of these fixed savings; no claim for every concave
tariff is made.

Retain the four full stages with supports 3,5,11,21 in six coordinates,
where an integer encodes a zero-one mask. They are the two rank-two
endpoints and the two rank-three stages from the main proof. Add one
rank-four stage and replace one of the three thin sites by that stage.
There are now five full stages and two thin queries. Pay four extra whole
idles in total. Each full supplier is a positive-size binary child.

Pairwise intersection, the three-site Gram restriction, and the five-site
union restriction leave exactly these seven possible extra masks:

```text
39, 43, 45, 46, 51, 53, 54.
```

The replay enumerates every four-element subset of six coordinates. These
are necessary masks, not seven constructed words. Proving that their
optimistic complete invoices lose suffices to exclude this extension.
This does not cover a fifth-stage root with only one rank-two projector,
or a different field or query count.

Let a,b,c,d,e be the five child sizes. Put x=a+c, y=b+d and n=x+y+e.
For extra-mask bits b_0,...,b_5, the six output degrees are

```text
x+y+b_0 e, x+b_1 e, y+b_2 e, c+b_3 e, d+b_4 e, e.
```

The native charge is n times the paid-minus-helper bill L per port. Pay
the five binary child bills C(a),...,C(e), the extra idles
H(8c)+H(8d)+2H(8e), and the two thin queries. Credit H(8q+1) for each
of the six displayed output degrees q. All native helper debits remain
in L. This is a full signed invoice, although it omits ordinary costs
and thus favors the candidate.

For each fixed e, maximize the left pair over 1<=c<x and the right pair
over 1<=d<y. The two maximizations are independent. Then enumerate all
x,y>=2 with x+y+e<100. This covers every positive five-child tuple below
100 and every binary shape through the exact binary cost recurrence.
There is no solver relaxation or time limit.

The interval engine gives rational bounds for each H value and L. The
replay rounds lower bounds down and upper bounds up onto a 2^40 integer
grid. It uses lower binary costs, lower paid idles and native charges,
and upper productive terms. Every resulting maximum is an upper bound.
Python integers cannot overflow. The finite maxima are strictly negative.

For n>=100, each binary node costs at least -1, so the five child bills
are at least -(n-5). Put Delta=H(9)-H(8) and
K=H(17)-2H(8)+2Delta. Concavity gives these upper bounds:

```text
mask 39:
H(8n+1)+2H(4n+5)-H(8)+3Delta-n(L-1)-7;

masks 43,45,51,53:
H(8n+1)+2H(4n+1)+K-n(L-1)-7;

masks 46,54:
3H(16n/3+1)+K-n(L-1)-7.
```

For mask 39, apply Jensen to the two pair outputs. The remaining
e-dependent part 2H(4(n+e)+1)-H(8e) decreases for 1<=e<n, so use e=1.
Each increment H(8c+1)-H(8c) is at most Delta.

For the other masks, at most one single output receives e. The sum of
the two single-output differences and the e-output contribution is at
most K: first use c>=1, then note that both
H(8e+9)-H(8e) and H(8e+1)-H(8e) decrease with e. In the middle group,
Jensen bounds the two pair outputs by 2H(4n+1). In the last group, the
first three output degrees sum to 2n, so Jensen gives 3H(16n/3+1).

Each displayed bound is concave in n. The replay checks its value and
derivative are strictly negative at 100. Thus all larger totals lose.
This replaces the seven time-limited numerical searches with a complete
exact price exclusion for their specified support family. Other roots
remain open.

## Open next questions

- Test five-full roots with only one rank-two projector. The seven-mask
  proof does not cover their supports.
- Construct a different child interface with a full native invoice.
- Supply a complete recovery and precision proof for the five-call
  border before applying its favorable formal price.

Ali Romman with substantial OpenAI Codex assistance; no subagents.
The chronological identity and shortest-query normal form retain the
credit in PROOF.md. The interval engine is by zxv and its predecessors.
