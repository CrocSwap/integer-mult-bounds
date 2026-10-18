# Polynomial norm for Gaussian resampling with logarithmic alpha squared

This is an independent verification and explicit statement of the parent investigation's nearest-neighbor factorization. It avoids requiring alpha^2 theta>1. It is a norm lemma, not a complete fast inverse algorithm.

Let s>=5, s<t<5s/4, rho=t/s, theta=rho-1, q_i=floor(rho i+1/2), and beta_i=rho i-q_i. Extend q_(i+s)=q_i+t and beta periodically. Set a=pi alpha^2>=1. The exact periodic normalized Gaussian matrix is

```
N_(i,j mod s) = sum_(k congruent j-i mod s)
  exp[-a*((beta_i+rho*k)^2-beta_(i+k)^2)].
```

Its principal k=0 term is one. Let L be its k=-1 weighted cyclic shift and U its k=+1 shift. Thus

```
L_i = exp[-a*((beta_i-rho)^2-beta_(i-1)^2)],
U_i = exp[-a*((beta_i+rho)^2-beta_(i+1)^2)].
```

All other k terms form R. The aliases k=±s and beyond remain in R; they are not discarded.

For h consecutive lower factors the exponent telescopes to

```
beta_i^2-beta_(i-h)^2 - 2rho sum_(j=0..h-1) beta_(i-j) + h rho^2
 >= h rho theta - 1/4.
```

The upper factors obey the same bound. Therefore both alternating Neumann inverses exist, including over arbitrarily many cyclic wraps, and

```
||(I+L)^-1||, ||(I+U)^-1||
 <= B = exp(a/4)/(1-exp(-a rho theta))
 <= 2 exp(a/4)/theta.
```

The final inequality uses a>=1 and 0<theta<=1. It is intentionally coarse but sufficient.

The nearest reverse products are exact:

```
L_i U_(i-1) = exp[-2a rho*(q_i-q_(i-1))].
```

Every q difference is 1 or 2, including the physical period cut, so `||LU||<=exp(-2a)`. For every omitted integer offset |k|>=2,

```
(beta_i+rho*k)^2-beta_(i+k)^2
 >= (rho*|k|-1/2)^2-1/4
 >= k^2-|k|.
```

Consequently

```
||R|| <= 2 exp(-2a)/(1-exp(-4a)) < 4 exp(-2a).
```

Write `A=(I+L)(I+U)`. Then N=A+(R-LU), and

```
||A^-1(R-LU)|| <= 5 B^2 exp(-2a)
                 <= 20 theta^-2 exp(-3a/2).
```

If `a>=4 ln(16/theta)`, this is bounded above by
`20 theta^4/16^6 < 1/2`. Hence

```
||N^-1|| <= 2 B^2 <= 8 exp(a/2)/theta^2.
```

Choose the integer `alpha=ceil(sqrt(4 ln(16/theta)/pi))`. With
`a0=4 ln(16/theta)`, the elementary ceiling inequality gives
`a<=2a0+2pi`; therefore

```
||N^-1|| <= 8 exp(pi) 16^4 theta^-6.
```

This is an explicit polynomial bound. For theta=Theta(1/d), alpha^2=O(log d) and the total original tensor scale has logarithm O(d log d)=o(p) for every fixed d=p^epsilon, epsilon<1. The period and aliases introduce no exception.

## Exact controls

`check_nearest_neighbor.py` checks 69 admissible finite (s,t) pairs and 93,976 product identities/bounds, including all skip gaps and two complete cyclic wraps. It uses exact rational exponents and no floating point. The exponential conclusions follow from monotonicity and the displayed convergent geometric sums. The output is `NEAREST-NEIGHBOR-CONTROLS.json`.

## Remaining algorithmic obligation

This lemma establishes that logarithmic alpha squared is analytically permitted. The old inverse implementation still incurs too much work at that alpha. A fast stable inverse, such as a fully normalized holes-completion algorithm, must still supply its actual movement, rounding and operation count. Erasing the inverse cost from the outer ledger would not follow from this norm proof alone.
