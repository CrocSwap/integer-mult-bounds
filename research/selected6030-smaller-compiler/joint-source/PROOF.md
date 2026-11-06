# Sharp direct coefficient for the net integer splitting tax

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The half-exponent attaining family was also derived separately by the lead
agent. These are author-side AI derivations, not independent human review.

## 1. Statement and exact domain

Fix `0<t<1`. For positive integers `R>J`, write `R=qJ+r`, `q>=1`,
`0<=r<J`, and define

```
S_t(R,J) = q J^t+r^t,
tau_t(R,J) = S_t(R,J)-R^t,
F_q(s) = [q+s^t-(q+s)^t]/(q+s)^sigma,  s=r/J.
```

The least universal coefficient `N(t,sigma)` in

```
tau_t(R,J) <= N(t,sigma) R^sigma J^(t-sigma)                 (1)
```

is finite exactly when `sigma>=1`. At `sigma=1`, it is 1 and is never
attained by a finite split. For `sigma>1`, it is positive, strictly below 1,
and has the following two-neighbor characterization.

Set `a=t^(1/(1-t))`. There is a unique positive real `z` satisfying

```
(sigma-t)[(z+a)^t-a^t] = (sigma-1)z.                        (2)
```

For each real `q>0`, let `s_q` be the unique root in `(0,1)` of

```
H_q(s) = t q s^(t-1)+(t-sigma)s^t-sigma q
                         +(sigma-t)(q+s)^t = 0.            (3)
```

Define the candidate set, with duplicates removed, by

```
Q = {max(1,floor(z)), max(1,ceil(z))}.
N(t,sigma) = max_(q in Q) F_q(s_q).                         (4)
```

There are at most two candidate quotients. A tie between the two is allowed;
no unproved rule about rounding z to its nearest integer is needed. Equality
in (1) occurs precisely for a maximizing candidate q with `r/J=s_q`.
The supremum is sharp over integer jobs even when every maximizing remainder
is irrational. This is an exact all-real characterization, not a finite
enumeration claim.

## 2. Each quotient has one maximizing remainder

Temporarily extend q to a positive real variable. For `0<s<1`, differentiating
F with q fixed gives

```
dF_q/ds = H_q(s)/(q+s)^(sigma+1),
dH_q/ds = -t(1-t)q s^(t-2)
          +t(sigma-t)[(q+s)^(t-1)-s^(t-1)] < 0.             (5)
```

Both terms are strictly negative because `q>0`, `0<t<1`, and `sigma>=1>t`.
The limit of H at zero is positive infinity, whereas

```
H_q(1) = (sigma-t)[(q+1)^t-(q+1)] < 0.
```

Thus (3) has exactly one solution. F increases before it and decreases
after it, making it the unique maximum on the closed interval `[0,1]`.
It lies in the actual remainder domain `[0,1)`. In particular, the excluded
endpoint s=1 creates no missing maximizer. The implicit function theorem
applies because (5) is nonzero, so `q -> s_q` is continuously differentiable.

## 3. The optimized quotient envelope is strictly unimodal

Assume `sigma>1`. Let `g(q)=F_q(s_q)`. The distinction between net and full split charges
matters: g need not decrease starting at q=1. The envelope derivative is

```
g'(q) = [1-t s_q^(t-1)]/(q+s_q)^sigma.                      (6)
```

Indeed, subtracting the s partial derivative of F from its q partial
derivative gives the displayed numerator over the displayed denominator;
the s partial derivative vanishes at s_q. Because the function
`1-t s^(t-1)` strictly increases and vanishes at a, the sign in (6) is
the sign of `s_q-a`. H is strictly decreasing in s, so this is also the sign of

```
D(q) = H_q(a)
     = (sigma-t)[(q+a)^t-a^t]-(sigma-1)q.                   (7)
```

Here `t a^(t-1)=1` was used. Strict concavity of `x^t` shows that

```
[(q+a)^t-a^t]/q
```

is strictly decreasing for q>0. Its limit at zero is 1 and its limit at
infinity is 0. Hence `D(q)/q` strictly decreases from `1-t>0` to
`-(sigma-1)<0`. It has the unique positive root z in (2).

Consequently g strictly increases on `(0,z)` and strictly decreases on
`(z,infinity)`. Restricting q to positive integers proves (4): an integer
below floor(z) is worse than floor(z), and one above ceil(z) is worse than
ceil(z). If z<=1 only q=1 is needed. If z is an integer >=1 it is the
unique best quotient. This is the missing quotient argument for the net tax.

Equation (2) is tractable without an unbounded quotient search. Its left
side divided by z is strictly decreasing. For example, first bracket the
root by doubling positive endpoints and then bisect. The theorem's exact
root and floor/ceiling characterization does not depend on floating point.
For rational parameters, directed rational power enclosures certify signs;
an exact integer turning point may instead be verified algebraically.

## 4. Domain, integer sharpness, and attainment

Write `x=q+s>=1` and `b=s^t-s`. Since `0<=b<1<=x^t`,

```
0 <= q+s^t-x^t = x+b-x^t < x
```

for integer q>=1. The lower bound is subadditivity of the concave power,
applied to q pieces of size one and a possible remainder. Thus for
`sigma>=1`, `F_q(s)<x^(1-sigma)<=1`.

At `sigma=1`, choosing s=0 and integer q tending to infinity gives
`F_q(0)=1-q^(t-1) -> 1`, proving both sharpness and nonattainment.
For `sigma<1`, the same sequence has
`F_q(0)=q^(1-sigma)(1-q^(t-1)) -> infinity`; no finite coefficient exists.

For `sigma>1`, (4) is a maximum at a finite q and interior s, so N<1.
It is positive, for example because `F_1(s)>0` for `0<s<1`.
For any maximizing q, take integer J tending to infinity,
`r=floor(J s_q)`, and `R=qJ+r`. Eventually `0<r<J` and R>J. Continuity
gives `F_q(r/J)->N`. Thus any smaller coefficient fails on integer splits.
The strict single-quotient maxima and strict envelope monotonicity give the
equality characterization in Section 1. A rational maximizing remainder is
attained for all positive integer multiples of its denominator.

## 5. An exactly attaining family with arbitrarily large best quotients

Take `t=1/2` and a positive integer n, and put

```
sigma = 1+1/(2n),   a=1/4,   z=n(n+1).
```

Then `sqrt(z+a)=n+1/2`, and (2) holds exactly:

```
(sigma-1/2)[sqrt(z+1/4)-1/2]
    = ((n+1)/(2n))n = (n+1)/2 = (sigma-1)z.
```

The unique best integer quotient is q=z, and (3) has `s_q=a=1/4`.
The numerator of F is n^2. Therefore

```
N(1/2,1+1/(2n)) = n^2/(n+1/2)^(2+1/n).                    (8)
```

Equality is attained by every `J=4d`, `R=(2n+1)^2 d`, positive integer d.
For n=1, the sharp coefficient is exactly `8/27`, at q=2, s=1/4.
This disproves transferring #6390's q=1 reduction to the net objective.
It also proves that no fixed finite quotient census works uniformly as
sigma decreases to 1. For n>=1 the rational identity

```
N^(2n) = n^(4n)/(n+1/2)^(4n+2)
```

supports exact finite checks without an algebraic-number library.

An independent lead-agent derivation supplies a second proof of this family.
Write `y=sqrt(s)` and `w=sqrt(q+s)`. Completing a square gives

```
q+y-w = (w-1/2)^2-(y-1/2)^2 <= (w-1/2)^2.
```

For `sigma=1+1/(2n)`, the upper envelope is
`(w-1/2)^2/w^(2+1/n)`, with w>=1. Its logarithmic derivative is
`2/(w-1/2)-(2+1/n)/w`; its unique maximum is at `w=n+1/2`.
Equality in the square bound requires y=1/2, which gives q=n(n+1).
Thus this separate calculation proves (8) without the general envelope H.
The separate `independent_family.py` corroborates the n=1 case with rational
radicals and imports neither the primary verifier nor a predecessor program.

For n=1, #4480's coefficient `Q(C,u)` has `C=1/2`, `u=sigma-t=1`,
`A=1/2`, `K=1/2`, hence `Q=1/2`. The sharp coefficient `8/27` is
strictly smaller. This compares coefficients, not complete supplier ranks.

## 6. Complete strictification with the completion tax retained

Retain every chronological product, native, whole-job adapter, same-owner
completion, disjoint splitting, and compiler hypothesis of #4433 and #4480.
Let `C=1-t`, `u>=C`, `sigma=t+u>=1`, positive integer v, integer bases
`1<c<b<m`, cutoff `J=c^v`, and completion threshold `L=b^v`. Let
`P_x,T_x` be raw paid and productive moments, and B the productive count.
The predecessor's native product contract gives moments `P_x^v,T_x^v`.

The exact original-paid splitting tax obeys

```
sum_R tau_t(R,J) <= N(t,t+u) P_(t+u)^v/J^u.                (9)
```

Unsplit R<=J have zero tax. Including their nonnegative higher moments on
the right only weakens the bound; their original t-moment is counted once
in `P_t^v`, rather than charging the entire split again.

For completed productive ranks K<L, preserve #4480's exact gap identity
and its nonnegative completion bound in full. With `h=C t^(t/C)`,

```
E(K) = K^t+S_t(L-K,J)-L^t >= 0,
E(K) <= L J^(-C)+2h J^t-L^t = H(L,J),
H(L,J)/J^t = L/J-(L/J)^t+2h > 0,
T'_t-P'_t = T_t^v-P_t^v-sum_R tau_t(R,J)-sum_(K<L) E(K).
```

There are at most `B^v` completed owners. Define the unchanged ratios

```
alpha=P_t/T_t,             gamma=P_(t+u)/(c^u T_t),
delta=B b/(c^C T_t),       epsilon=B c^t/T_t,
delta0=B b^t/T_t.
```

Substituting (9) and the full H bound yields the complete sufficient test

```
alpha^v + N(t,t+u) gamma^v + delta^v
                  + 2h epsilon^v - delta0^v < 1.           (10)
```

Only the original-paid tax coefficient changes from #4480's Q. Its
completion expression is kept intact, including its negative term and the
positive terms that justify it. For directed interval certification use
upper bounds for all positive terms and a lower bound for `delta0^v`.
The simpler, weaker but still valid #4433 form is

```
alpha^v + N(t,t+u) gamma^v + 2 delta^v < 1.                 (11)
```

The final paid ranks are <=J and productive ranks >=L, so (10) or (11)
gives a strict t-moment gap at a strictly separated interface. In particular,

```
P'_1 <= J^C P'_t < L^C T'_t <= T'_1.
```

The inherited compiler receives the same separated native unit contract.
This is not a proof of the native contract, physical costs, compiler closure,
precision, or the complete multiplication theorem. No new inventory, selected
frontier, kappa, least tensor power, or globally optimal compiler is asserted.
All five framework assumptions in the frozen selected record remain.

## 7. Comparison with the predecessor bound

For `sigma>1` (`u>C`), the sharp N is strictly smaller than #4480's
`Q(C,u)=min(A(C,u),K(C,u))`, not merely no larger. Here

```
A(C,u)=max(C/u,h),
K(C,u)=2^u (C/u)(1-C/u)^((u-C)/C),  u>C.
```

The simplification A=C/u is only valid when u<=C/h; it is not assumed for
the full domain of this theorem. Its A proof has strictly
positive derivative contribution `ht x^(-t-1)` for x>1, so the pointwise
net ratio is strictly below A. Its K proof uses the strict inequality
`ceil(x)<2x` for x>1, and the net tax is positive at the maximizing interior
remainder. Thus the finite-q interior maximizer is strictly below both A and K.
At `sigma=1`, both sharp N and Q equal 1. This comparison retains the exact
domain and all of #4480's native and completion premises.

## 8. Attribution and verification boundary

Nick Petalas's #4832 supplies the sharp linear full-split coefficient;
#6390 at `f9e68f40b0da7236a7fad415f7172218c0666d27` supplies the direct
full-split coefficient and asks the net question answered here. zxv's #4433
supplies higher-moment strictification and #4480 the exact net gap and
completion tax. Cinna Davis's #4412/4414/4416 supplies the chronological
product/completion lineage; Jacob Alan Sussman supplies the finite integer
compiler. Their retained native/helper/controller/outer attribution remains.
Frozen copies identify exact source bytes. Elementary calculus is classical;
no literature-priority claim is made.

The universal statements follow from the written proof. The standard-library
verifier supplies bounded exact corroboration, counterexamples to tempting
wrong reductions, and a literal complete-gap accounting fixture. It does not
formalize this proof in a proof kernel, replay the selected construction, or
establish independent human acceptance.
