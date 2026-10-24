# Single crossing for every fixed p16 fragmentation invoice

This proof discharges S1 from [PR #5226](https://github.com/CrocSwap/integer-mult-bounds/pull/5226)
for the fixed p16 positive-partition class below. The retained source checked
S1 on a grid. Here the monotonicity proof covers the whole interval and every
partition in the class. No native word or complete kappa improves.

The caller and current invoice come from Cao Yifan's
[PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610).
SOURCES.json pins the retained ARITHMETIC.json and the S1 statement at canonical
main ff3cc58e370d0f678e529246f8c73e8094e18fcf. This is a theorem about complete
finite invoices, not acceptance of the physical or compiler premises.

## Exact class

Fix p=16, a=7 or8, v=112 and d=8. There are 18 native calls. Each call has
224 main fields of net increment 8 and 408 independent helper fields, with
endpoint census `{4:28,7:7,8:47,9:326}`. It also pays eight rank-8 center jobs.
For each main and helper field, replace its one net increment R by any
positive integer partition of R. The partition can differ between fields
and calls. No extra native jobs are permitted. The complete target inventory
and controller jobs remain those in the source invoice.

These are exactly the numerical hypotheses used in this proof. They cover
nested ascending paths whose transport ranks equal their dimension gains.
They do not cover descents, nonnested costs exceeding the dimension gain,
changed endpoints, extra jobs, sharing, or coded interfaces. Mathematical
partitions are not asserted to have realizable native words.

Let `f(t)=sum_T n_r r^t-sum_P m_r r^t`, with positive ranks and their integer
multiplicities. Put `c_r=n_r-m_r`. The largest rank is 145. Define weighted tails

```text
B_k = sum_(r>=k) r c_r.
```

The comparison invoice uses one unsplit job R per main/helper field. We call
it the unsplit invoice. It is a numerical comparison, not a new construction.
Helper paid jobs cancel their same-rank credits in this invoice. Each call
then has 232 paid rank-8 jobs from mains and centers. The controller adds:

- 224 target jobs of rank 145;
- 1,680 paid rank-1 jobs;
- for j=1,...,7 and separately j=1,...,8, 224 targets of rank `8(j+1)+1`
  and 224 paid jobs of rank `8(j+1)`.

This formula reproduces the source complete invoice when the unsplit native
profile is replaced by the source local paid profile.

## Positive weighted tails survive every partition

For a partition `R=r1+...+rs`, at every integer k the sum of parts at least k
is at most `R [R>=k]`. Substituting the partition for the unsplit paid job
therefore cannot decrease any B_k. This statement uses mass, not concavity
or a comparison at selected exponent values.

For the unsplit invoice and 2<=k<=8, all 15 controller pairs contribute their
rank difference 224. The final target contributes `224*145=32480`. The main
and center cost is `18*232*8=33408`. Thus

```text
B_k = 32480 + 15*224 - 33408 = 2432   (2<=k<=8).
```

For 9<=k<=145, the native rank-8 cost is below the threshold. A controller
pair has nonnegative weighted tail at every threshold: it contributes 224
below its paid rank, only its positive target at the next rank, and zero
after that. The rank-145 targets remain. Hence `B_k>=32480` on this range.
Every fragmented invoice consequently has `B_k>=2432>0` for all 2<=k<=145.
Its total rank mass is unchanged:

```text
f(1) = 2432 - 1680 = 752.
```

The current source invoice has minimum B_k equal to 32480 for k>=2. This
independent numerical certificate gives it the same monotonicity even
without a new native trace replay.

## Interval monotonicity

For 4/5<=t<=1, define `h_t(x)=x^(t-1) ln(x)` on 1<=x<=145. Its derivative is

```text
h_t'(x) = x^(t-2) [1-(1-t) ln(x)] > 0.
```

For a fully rational check of the strict inequality, the exponential series
has positive terms and

```text
exp(5) > sum_(j=0)^12 5^j/j! = 2837864809/19160064 > 145.
```

Thus ln(145)<5 and `(1-t)ln(x)<1`. Summation by parts now gives

```text
f'(t) = sum_(r=1)^145 (r c_r) h_t(r)
      = sum_(k=2)^145 B_k [h_t(k)-h_t(k-1)] > 0.
```

The term at rank 1 vanishes because h_t(1)=0. This proves strict monotonicity
on the entire interval, for every partition in the stated class. It is not
a grid extrapolation. The same argument is a reusable sufficient test for
any finite invoice with nonnegative weighted tails, at least one positive
tail, and a rank bound that keeps h_t increasing.

## An exact endpoint sign gives one crossing

At t=19/20, splitting a positive paid rank cannot reduce its moment:
`(a+b)^t<=a^t+b^t` for a,b>0 and 0<t<1. Thus every fragmented invoice has
f(19/20) no larger than the unsplit invoice.

The checker encloses each r^(19/20) by integer powers. With Q=2^24, it finds
an integer z such that

```text
z^20 <= r^19 Q^20 < (z+1)^20.
```

Then `z/Q <= r^(19/20) < (z+1)/Q`. Signed interval addition gives the exact
unsplit endpoint enclosure

```text
-997308605/262144 <= f_unsplit(19/20) <= -1994616351/524288 < -3804.
```

There is no floating-point logarithm or root in this check. All fragmented
invoices have f(19/20)<0 and f(1)=752>0. Continuity and strict monotonicity
give exactly one zero in (19/20,1), and no other zero in [4/5,1]. Therefore
the raw saving variable C=1-t has exactly one crossing in (0,1/20).

For every bar in (0,1/20], the raw crossing is at least bar if and only if
`f(1-bar)>=0`. For a homogeneous native word used 18 times, PR #5226's
identity `f(t)=18[Lambda_star(t)-Lambda_word(t)]` therefore gives its
p16 necessary-and-sufficient loss test without an extra S1 assumption.
The numerical value of Lambda_star and the all-p controller optimum are
separate source claims; this package does not reprove those. It does not
extend the result to arbitrary p or to native jobs outside the partition
class.

## Evidence, credit and next question

The checker binds the complete source invoice through the local profiles
and an independent controller formula. It checks all 144 weighted tails,
the fixed rank mass, all 96 positive integer partitions of totals 1,...,9,
22 integer-root enclosures, and the rational exponential lower bound.
Controls reject an added high-rank cost, removed helper credit and a wrong
partition total. The written mass and summation proofs cover every assignment
of partitions; those assignments are not enumerated. No native, Lean,
compiler, outer-ledger or selected replay was run.

PR #5226 supplies the fragmentation framework and names S1. Its retained
README attributes the text to Claude Opus 5.5 via Claude Code; no human
identity is inferred from its submission account. Cao Yifan supplies the
PR #4610 invoice. Cinna Davis, zxv and the retained controller/native authors
keep their source credit. The weighted-tail proof, class-wide S1 discharge
and exact checker are new here. Ali Romman with substantial OpenAI Codex
assistance. Apache-2.0; author-checked, not independent acceptance.

A future changed invoice can first test its weighted tails. If extra jobs or
changed endpoints make a tail negative, this sufficient certificate does
not apply; that is not a proof of multiple crossings. Derive an appropriate
interval bound or a new invoice before using a sufficiency claim.
