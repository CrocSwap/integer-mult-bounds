# Sharp precision for a nested triangular border

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and statement

Fix integers d>=1 and P>=1. Both input registers are independent real scalars,
with max norm at most one. Put

```
G = diag(1,-1),  D = diag(epsilon,1),
Q = [[1,epsilon],[0,1]],  epsilon = 2^(-s), s>=1.
W_0 = G,  W_(j+1) = Q D W_j D^(-1).
```

Matrices act on column vectors, so the rightmost instruction executes first.
The two diagonal maps and the shear are exact. Only the innermost invocation
of G is numerical. At its input z the returned value is Gz+e, with

```
||e||_infinity <= eta ||z||_infinity,  eta=2^(-p), p>=0.
```

Every error satisfying that inequality is allowed. A guarantee means that the
returned vector differs from Gx by at most delta=2^(-P), for every input in
the unit square and every allowed error. It is a minimax contract guarantee,
not a lower bound for an implementation that computes G exactly.

**Theorem.** Among all uniform power-of-two parameters epsilon and integer precisions
p, the least precision giving that guarantee is

```
p_min(d,P) = (d+1)P+d.
```

It is attained with s=P+1. This is the only parameter exponent attaining
that minimum. Every exact completed subcall is an involution and has spectral
condition number less than four, uniformly in its nesting height.

This is a synthetic recursive template. It is not the literal controller or
native implementation of PR4623, and asserts no error in that work. It resolves
one contract question raised by that work's requirement to flatten and budget
the entire recursive caller. Classical similarity and error propagation retain
their credit; general literature priority is unclaimed.

## Exact endpoint and the completed-subcall bound

Write

```
a_j = sum_(k=1)^j epsilon^k = epsilon(1-epsilon^j)/(1-epsilon).
```

Direct multiplication, or induction using a_(j+1)=epsilon+epsilon a_j, gives

```
W_j = [[1,-a_j],[0,-1]].
```

Consequently W_j^2=I, ||W_j-G||_infinity=a_j<2epsilon, and
||W_j||_2<=1+a_j. Since 0<a_j<1 and W_j is its own inverse,
cond_2(W_j)<4. These assertions concern completed calls.
Before the innermost call the chronological prefix is D^(-d), with condition
number epsilon^(-d). A bound on completed calls does not bound this prefix.

The displayed recursive word has d shears and 2d scale instructions in its
uncombined expansion, plus the one numerical call. These counts are not an
optimal physical implementation claim. In particular, adjacent input scales
can be combined. No scale, source movement or precision request is free in a
supplier invoice merely because its algebra is exact here.

## Exact worst-case error

The innermost input is z=(epsilon^(-d)x_1,x_2). The suffix after the numerical
call is

```
(QD)^d = [[epsilon^d,a_d],[0,1]].
```

Thus the difference from the desired Gx is

```
(-a_d x_2 + epsilon^d e_1 + a_d e_2, e_2).
```

For ||x||_infinity<=1, the oracle allowance is at most eta epsilon^(-d).
The exact maximum error is therefore

```
E(d,s,p) = max(a_d + eta(1+a_d epsilon^(-d)), eta epsilon^(-d)).  (1)
```

The upper bound is the triangle inequality. It is attained simultaneously
in both displayed components by x=(1,-1) and
e=eta epsilon^(-d)(1,1). These errors even come from the one fixed linear
perturbation Delta=eta [[1,0],[1,0]], whose infinity operator norm is eta.
Sharpness does not require nonlinear, adaptive or independent random errors.

## Necessary precision

If epsilon>=delta, then a_d>=epsilon>=delta, and the first component of (1)
is strictly greater than delta because eta>0. Thus any feasible power-of-two
parameter has s>=P+1. The second component requires

```
2^(ds-p) <= 2^(-P),  hence p>=P+ds>=(d+1)P+d.                (2)
```

If equality holds in the final precision bound, d>0 forces s=P+1.
This proves necessity over every parameter exponent, without a finite search
cutoff. It also separates approximation bias from numerical oracle error.

## Attainment

Take epsilon=delta/2 and eta=delta epsilon^d, equivalently
s=P+1 and p=(d+1)P+d. The second component of (1) equals delta. The first is

```
(1+delta)a_d + delta epsilon^d
  = delta [c+(1-c)epsilon^d],
c=(1+delta)/(2-delta).
```

P>=1 implies delta<=1/2, so c<=1 and this component is at most delta.
This proves sufficiency and the theorem. At this parameter, reducing p by one
makes the second component exactly 2delta, giving an explicit failed guarantee.
The excluded P=0 case is not asserted to follow the same formula.

For example, d=4 and P=2 have s=3 and p_min=14. The completed coupling is
585/4096, below 1/4, and every completed map is an involution with the stated
condition bound. The innermost input gain is 4096. Precision 14 attains worst
error 1/4; precision 13 has error at least 1/2. These are exact values for this
synthetic template, not measurements of a selected provider.

## Consequence and limits

Uniformly small completed leakage and uniformly conditioned completed calls
do not imply a depth-independent oracle precision allowance under nesting.
Here the exact optimal bit request grows as dP. A proposed border compiler
must bound chronological magnitudes and error transfer, or provide stronger
componentwise/exact error semantics. The finite global lemma in PR4623 already
requires global bounds; the theorem does not contradict it or close its
actual recursive implementation obligation.

No native operator, paid target histogram, useful saving, full compiler,
physical scale/ADD circuit, dirty auxiliary protocol, stock, tape, analytic
recovery or integer multiplication theorem is supplied. The initial inputs
are both arbitrary and the desired output retains both. No hidden reset or
discarding is used. Independent human and formal proof-kernel review are
unclaimed. The all-height statement rests on this written proof; finite
verification corroborates the endpoint, sharp error formula and minima.
