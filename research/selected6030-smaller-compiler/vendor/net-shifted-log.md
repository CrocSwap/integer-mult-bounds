# A normalized logarithmic majorant

This extends the logarithmic majorant in PR4411 and PR4433 without changing
their finite integer compiler, its source complements, or its native
hypotheses. The new parameter normalizes the logarithm by a scale adapted to
the fixed mixed unit. All logarithms in the theorem are base two.

Assume the separated finite compiler has ordinary base `L(n)=n` for
`0<=n<m`, and, for every integer `n>=m`,

```
L(n) = sum_s w_s L(n-s) + sum_e x_e L(e),
sum_s w_s = 1,
n/m < s <= n,
sum_e x_e e^t <= sum_s w_s s^t,
1 <= e <= r_max*(n/m)^theta < n,
theta = log(r_max)/log(k_min) < 1.
```

Here the normalized nonnegative weights arise from whole integer batches;
the moment inequality follows from the strict mixed-unit superpotential.
These are the inherited compiler premises, not a replacement native proof.

Choose `0<t<1`, a positive scale `h`, a positive power `p`, and a rational
`theta_bar=a/b` with `theta<=theta_bar<1`. Suppose

```
2^(h*(b-a))*r_max^b <= m^a,                         (shift)
theta_bar^p < eta := t*m^(t-1),                    (capacity)
m^(1-t) <= (1+log(m)/h)^p.                         (base)
```

Then, with the zero-rank value defined separately,

```
L(n) <= F(n) := n^t*(1+log(n)/h)^p   for n>=1,
F(0) := 0.
```

The scale and power may be real. Integer `h` and `p`, and rational
`theta_bar`, make the shift guard and final-rank checks particularly simple
exact arithmetic. The separate check `r_max^b<=k_min^a` implies the required
`theta<=theta_bar`.

## Base range

Put `x=log(n)` and `M=log(m)`. For positive `x`, the function
`log(1+x/h)/x` decreases: its derivative has the sign of
`x/(h+x)-ln(1+x/h)`, which is nonpositive because
`ln(1+u)>=u/(1+u)` for `u>=0`. Therefore the base guard implies

```
p*log(1+x/h) >= (1-t)*x    for 0<=x<=M.
```

Exponentiation proves `F(n)>=n` throughout the ordinary base range. At
`n=1`, both sides are one. This single endpoint guard covers every integer
base rank; checking a sample of them is unnecessary.

## Exit contraction

Because `n/m>=1` and `theta<=theta_bar`,

```
log(e) <= log(r_max) + theta_bar*(log(n)-log(m)).
```

The shift guard is exactly

```
(1-theta_bar)*h + log(r_max)-theta_bar*log(m) <= 0.
```

Consequently `h+log(e)<=theta_bar*(h+log(n))`. Writing
`A(n)=(1+log(n)/h)^p` gives

```
A(e) <= theta_bar^p*A(n),
sum_e x_e F(e) <= theta_bar^p*A(n)*sum_s w_s s^t.
```

The factor `h` cancels in this ratio. Increasing it is therefore available
up to the explicit shift guard, rather than forcing the original value one.

## Complements and induction

The factor `A` increases on positive ranks. For `y=s/n>1/m`, concavity gives

```
1-(1-y)^t >= t*y >= t*m^(t-1)*y^t = eta*y^t.
```

Treating a zero-rank complement as zero, this implies

```
F(n)-sum_s w_s F(n-s) >= eta*A(n)*sum_s w_s s^t.
```

The strict capacity guard pays the exit bound. All recursive ranks are
smaller than `n`, so strong induction proves the assertion. The argument
uses monotonicity of `A`; it does not require that `A` be concave or that
`p<=1`.

## Specified uniform rank

For a desired exponent `z>t` and `N=2^H`, the sufficient final condition is

```
(1+H/h)^p < 2^((z-t)*H).
```

For positive integers `h,p,H`, and an integer `J=(z-t)*H`, this is exactly

```
(h+H)^p < h^p*2^J.
```

Thus normalized logarithms preserve a finite exact integer final-rank
certificate. This bounds normalized paid rank-one leaves. Actual productive
width, scalar records, owned banks, precision constants, physical costs and
recovery thresholds still come from the newly compiled finite word and the
inherited native and outer arguments.

As a diagnostic using PR4453's unchanged `v=675`, `p=160` and
`theta_bar=15/16`, one may take `h=40*v=27000`: the shift condition reduces
to `2^40*18^16<=153^15`. The endpoint base condition also remains strict.
This changes the final sufficient-rank inequality itself. A standalone
numerical diagnostic is not a new certified rank or an independent native
admission; the package's exact verifier supplies its instantiated values.

Prepared with substantial OpenAI Codex assistance. The finite integer
lockstep compiler is Jacob Alan Sussman's construction, retained through
PR4359; the logarithmic-majorant predecessors are zxv's PR4411 and PR4433.
New material is Apache-2.0.
