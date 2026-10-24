# Independent three-value verification of the PR5405 fixed-family ceiling

This local check proves the three required strict rational inequalities for the
actual PR5405 profile at `kappa0=0.00302728825`, using a new standard-library
interval implementation. Together with the separately frozen analytic exchange
and discrete-convexity proofs, these inequalities imply positivity of every
equation-(1) invoice at this exponent. The monotonicity argument below extends
that fixed-family conclusion to `kappa0 <= kappa < 1`.

This is a necessary-moment obstruction for the specified invoice family. It is
not a new exponent saving, a physical or global circuit optimum, native execution,
supplier admission, a formal-kernel proof, or a complete multiplication theorem.
The changed/coupled profile of PR5402 is excluded. Equation (1) and its autonomous
local profile are explicit source premises; their derivation from the original
Laurent controller, native circuit and framework assumptions is not replayed here.

The source is Ali Romman's PR5405, head
`314b56a6c0056c2358538f072c6fde9d365be44d`, against retained canonical main
`1ec1119972c9aefe42525172d07b332fcff81cb4`. The frozen source proof has SHA256
`5c82c9f1650b0ffb352f2aa7eaac3aa283754028e41cd85d1ee848af9d18cd37`.
`SOURCE-MANIFEST.json` and `THEORY-MANIFEST.json` identify immutable copies of
the source, guidance and the two independent analytic notes. Root owns upstream
freshness, overlap, publication and any final admission gate. No separate upstream
feed, package publication or public write was performed by this checker.

## Complete invoice and independent coefficient reconstruction

Put `t=1-kappa`, `f(r)=r^t` for positive r and `f(0)=0`. The source profiles are

```
P={1:2193,2:412,3:510,4:127,5:40}
H={4:28,7:7,8:47,9:318}
L(t)=sum_r P[r]f(r)-sum_r H[r]f(r).
```

For p>=1, choose a+b=p-1 and a bit mask x of length 2p+1. A bit one means FULL;
its contribution is P on the paid side and H on the target side. A bit zero
means QUERY; it contributes exactly 112 paid rank-one jobs and no local helpers.
Let n be the number of ones. The complete local net contribution is therefore

```
nL+112(2p+1-n) =112(2p+1)+(L-112)n.
```

There are 224 full-path main targets of rank 1+8n. For retained idle slot j,
1<=j<=p-1, the FULL count on its exterior side is

```
h_j=sum_(s=0)^(2j-1)x_s,        j<=a,
h_j=sum_(s=2j+1)^(2p)x_s,       j>a.
e_j=x_(2j).
```

Its paid terms are 224 jobs of rank 8h_j (omit when h_j=0), plus 224 jobs of
rank eight when e_j=1. Its targets are 224 jobs of rank 1+8(h_j+e_j). Adding
all items, with no helper credit at QUERY stages, gives exactly source equation
(1):

```
E=112(2p+1)+(L-112)n-224f(1+8n)
  +224 sum_(j=1)^(p-1)[f(8h_j)+e_j f(8)-f(1+8(h_j+e_j))].
```

The checker builds paid and target integer histograms from those item lists,
expands equation (1) separately into signed coefficients of the formal symbols
f(r), and compares the coefficient dictionaries exactly. This identity check
uses no floating-point tolerance or interval overlap. It covers every mask and
split for p=1,2,3 (456 cases) as an index control. The invoice formula for arbitrary
p remains the source premise; finite examples are not promoted to its proof.

## Canonical minimum and its two neighboring differences

The frozen exchange note
`inputs/5405-concavity-exchange-reduction.md` proves that every invoice with n
FULL stages has E>=C_n, and that C_n is attained in this family. For n=0,1,2 the
canonical controller has p=1 and no retained side idles, so

```
C_n=336+(L-112)n-224f(1+8n).
```

For n>=3, all two exterior endpoints and the central stage are FULL. Every
remaining side pair, read from outside inward, is 10. There are n-3 such pairs,
split with a=floor((n-3)/2), b=ceil((n-3)/2), hence p=n-2. There are 2p+1=2n-3
stages and n-3 QUERY stages. The j-th side pair has h=j+1 and e=0, so its
net summand is `-delta(8(j+1))`, where delta(z)=f(z+1)-f(z). This independently
reconstructs

```
C_n=nL+112(n-3)-224f(1+8n)
    -224[sum_(k=2)^(a+1)delta(8k)+sum_(k=2)^(b+1)delta(8k)].
```

The two formulas agree at n=3. Symbolic coefficients of this closed expression
are checked exactly against the canonical mask's paid-minus-target histogram
for n=0,...,5 and n=16,...,20. In particular n=18 gives p=16,a=7,b=8, with
18 FULL and 15 QUERY stages. Its first side increment is delta(16), not delta(8).

Let D_n=C_(n+1)-C_n. Adding one FULL count grows the full-path rank from 1+8n
to 9+8n. For n>=3 it also adds one side pair at partial count
k=floor((n+1)/2), on the previously shorter side. The local and QUERY term
increases by L+112, and the added idle difference is -224delta(8k). Thus

```
D_n=L+112-224[f(9+8n)-f(1+8n)+delta(8 floor((n+1)/2))], n>=3.
```

For the two required neighbors k=9 in both cases. Consequently

```
C18=18L+1680-224f(145)
    -224[2 sum_(k=2)^8 delta(8k)+delta(72)],
D17=L+112-224[f(145)-f(137)+delta(72)],
D18=L+112-224[f(153)-f(145)+delta(72)].
```

The checker evaluates the differences both by subtracting independent enclosures
for C values and through these shorter formulas. Interval intersection is an
additional numerical crosscheck; the analytic difference identity is the algebra
above and in the frozen discrete-convexity note.

For completeness, discrete convexity is not a tail extrapolation. Write
`B_n=336+(L-112)n-224f(1+8n)` and `C_n=B_n+224T_n`. Concavity of f gives strict
discrete convexity of B on n>=0. The correction has increments zero for n=0,1,2,
and `1-delta(8 floor((n+1)/2))` for n>=3. They are nondecreasing, including the
jump from zero. Hence C is strictly discretely convex on every nonnegative
integer. This includes the small-count junction. The frozen independent proof
supplies full details. Therefore C18>0, D17<0 and D18>0 make n=18 the unique
minimizing FULL count and prove C_n>=C18>0 for every n>=0, with no DP or n>=96
tail certificate.

## New directed-rational interval implementation

All acceptance arithmetic uses integers on Q=2^256. An interval `(lo,hi)`
represents `[lo/Q,hi/Q]`. Addition, subtraction and integer multiplication take
the appropriate directed endpoints. Products of nonnegative intervals use
integer floor for the lower endpoint and integer ceiling for the upper endpoint.
The only floating values are resource timing fields, which never affect acceptance.

For a positive integer r, write r=2^m y with 1<=y<2. Compute
`log r=m log2+log y`. For z=(y-1)/(y+1), 0<=z<=1/3,

```
log y=2 sum_(j=0)^(N-1) z^(2j+1)/(2j+1)+R,
0<=R<=2 z^(2N+1)/[(2N+1)(1-z^2)].
```

The bound follows by replacing every omitted denominator by its first value
2N+1 and summing a geometric series. The implementation uses N=128, directed
integer recurrence for included terms and exact Fraction arithmetic followed by
upward quantization for the remainder. log2 uses this same formula with y=2.

Use the exact saving `kappa0=12109153/4000000000`; then
`r^t=r*exp(-kappa0 log r)`. For the finitely used r, the outward argument
X=kappa0 log r lies in [0,1], checked before exponentiation. To bound exp(X),
sum its Taylor series through term N=64 with directed nonnegative arithmetic.
For its first omitted term U=X_hi^(N+1)/(N+1)!, all subsequent ratios are at most
X_hi/(N+2)<1. Thus

```
0<=exp(X)-sum_(k=0)^N X^k/k!<=U/[1-X_hi/(N+2)].
```

This upper remainder is computed as an exact rational at X_hi and rounded
upward. Invert the positive exp enclosure with reversed endpoints to bound
exp(-X), and multiply by the exact integer r. For r=0 and r=1 the result is
exact by definition. No author engine, source import, numerical package, solver,
native execution or Lean process is used.

## Rational result and controls

`receipts/arithmetic-v2.json` retains both exact integer endpoints over Q, every
power enclosure used, histogram lists, resource fields and all control outcomes.
The following shorter decimal bounds are exact rational outer bounds with
denominator 10^30; both inequalities are strict:

| Quantity | Lower bound | Upper bound |
|---|---:|---:|
| C17 | 0.271338636819840412923442461615 | 0.271338636819840412923442461616 |
| C18 | 0.000000014914967918767741908079 | 0.000000014914967918767741908080 |
| C19 | 0.022748171405392891630850340572 | 0.022748171405392891630850340573 |
| C18-C17 | -0.271338621904872494155700553537 | -0.271338621904872494155700553536 |
| C19-C18 | 0.022748156490424972863108432493 | 0.022748156490424972863108432494 |

The enclosing interval for C18 has width less than 3e-70; the positive margin
is more than 1.49e-8. The gate is strict on exact rational endpoints, independent
of displayed decimal truncation. The v1 and v2 arithmetic endpoints agree; v2
strengthens the mutation controls without changing the arithmetic implementation.

Five controls have their explicit expected rejection recorded: changed source
bytes fail SHA256 authentication; reversing paid-minus-target fails the gate;
omitting one 112-rank-one QUERY charge fails the exact symbolic invoice identity
and gives a negative value; omitting the 224 full-path targets fails that exact
identity; changing P[4] from 127 to 126 fails comparison with the authenticated
source profile. The omitted-target mutant is deliberately favorable numerically,
so its rejection depends on invoice accounting rather than a bad final sign.

## Independent normalized monotonicity audit

Discrete convexity above is a fixed-t argument. A separate proof is needed for
the interval of savings, and it concerns whole invoices rather than just C18.

First delete side pairs 00. If their preceding FULL count is h, deletion removes
two QUERY stages, reducing paid cost by 224, and removes a retained summand
`-224delta(8h)`. Thus E decreases by `224[1-delta(8h)]>=0`; equality is possible
at h=0. It preserves n and all later partial FULL counts and remains in the
source invoice family after reindexing. Repeat until no 00 pairs remain. This
reduction is valid separately for every 0<t<1 and makes no physical caller claim.

If n=0, all stages are QUERY and direct substitution yields
`E=112(2p+1)-224-224(p-1)=112>0` for every p and every t. Handle that case without
logarithms of zero or a full-path derivative claim.

For n>=1 fix any reduced invoice. Normalize its complete expression by 8^t:

```
E/8^t =112(2p+1-n)8^(-t)+nL(t)/8^t-224(n+1/8)^t
        +224 sum_j [h_j^t+e_j-(h_j+e_j+1/8)^t].
```

The QUERY coefficient is nonnegative, so that term is nonincreasing in t.
The full-path term has strictly negative derivative because n+1/8>1. For each
side summand, if e=0 then reduction forces the other bit to be one, so h>=1.
If h>=1, the derivative is negative because `z^t log z` is strictly increasing
on z>=1: its derivative in z is `z^(t-1)(1+t log z)>0`, and the second base is
larger than h. If h=0, reduction forces e=1 and the summand is
`1-(9/8)^t`, whose derivative is strictly negative. These cases avoid treating
0^t log0 as an ordinary expression.

Finally combining the common rank-four terms gives

```
L/8^t=2193(1/8)^t+412(1/4)^t+510(3/8)^t+99(1/2)^t
      +40(5/8)^t-7(7/8)^t-47-318(9/8)^t.
```

Its only positive derivative term is `7(7/8)^t log(8/7)`, less than
`7 log(1+1/7)<1`. The negative derivative from its first term alone has magnitude
greater than `2193 log8/8>274`, since 0<t<1 and log8>1. All other nonconstant
derivative terms are nonpositive. Thus the local normalized derivative is
strictly negative throughout 0<t<1. All normalized whole-invoice terms are
nonincreasing, so E(t)/8^t is strictly decreasing for every reduced n>=1 invoice.

At t0=1-kappa0, every reduced invoice is positive by the all-n gate. For any
0<t<=t0 its normalized value is at least its positive value at t0. Therefore
the reduced invoice is positive. The unreduced invoice has no lower E at the
same t, so it too is positive. Together with n=0 this proves the source family's
necessary moment test fails for every `kappa0<=kappa<1`.

## Provenance, remaining questions and limits

Credit Ali Romman for PR5405's family, complete invoice, original unbounded ceiling
and DP; Cinna Davis for the paired path/query controller; Cao Yifan for native
source; zxv for predecessor interval arithmetic and invoice preflight; Chris R
for prior independent admission/controller work; Dugongue, Jacob Alan Sussman,
and the retained native/helper/compiler/analytic contributors. Root proposed the
exchange and discrete-convexity conjectures; the sole Astra theory worker supplied
the two independent frozen analytic proofs. This successor check independently
derived the full invoice expansion and canonical arithmetic, implemented the new
log/exp bounds, and audited the normalized extension with substantial OpenAI
Codex assistance. All predecessor source bytes and notices are retained.
New work is Apache-2.0.

Open next questions:

- A human or formal-kernel reviewer can inspect the exchange, small-count
  convexity junction and log/exp remainder derivations. The bounded checks
  do not replace those analytic arguments.
- Connecting source equation (1) to every claimed native/physical construction
  remains a separate source-admission obligation. No such replay was budgeted.
- Improving kappa requires changing a premise such as provider/consumer contract,
  stage rank or idle law; this certificate does not transfer to PR5402.
- A root-controlled publication gate must check the final scoped claim, source
  pins, retained contributor credit and current overlap before any upstream write.
