# A sign criterion for fully crossing helper rank bills

## Scope and provenance

Fix a real exponent $0<t<1$, a terminal $T>0$, and a nonempty
finite list of paths with real endpoints

$$
0\le a_i\le T\le b_i,\qquad 1\le i\le m.
$$

Set $A=\max_i a_i$. For $A\le x\le T$, define

$$
\begin{aligned}
H_{a,b}(x)&=(x-a)^t+(b-x)^t-(b-a)^t,\\
H_0(x)&=H_{0,T}(x)=x^t+(T-x)^t-T^t,\\
G(x)&=H_0(x)-\sum_{i=1}^m H_{a_i,b_i}(x).
\end{aligned}
$$

We use $0^t=0$. Every paid path reaches the helper terminal:
**$b_i\ge T$ is essential to the stated domain.** A path may end exactly
at $T$; proper crossing $b_i>T$ is not required. The endpoints need not
be integers, so the theorem includes the integer-rank instances.

The rank-bill formula and its zero-to-ambient endpoint question come from
unpaidmoon's PR #7283, retaining CubeJerry's helper-split work and
DreamingOfClouds's two-chain word in PR #6902. Nick Petalas's PR #7331,
at `e5383f5c2973c9520918cbe6ebe9c6e6867e5771`, proves the proper-terminal
one-path result and supplies a four-path counterexample to an endpoint
**maximum**. Its first open question asks whether an interior positive bill
can be hidden by nonpositive endpoint bills. We answer that sign question
for every finite number of fully crossing paths. The proof below is
self-contained; it uses classical concavity and tangent-line inequalities.

This is a result about the abstract rank bill. It does not construct a legal
helper split, change a caller, price ordinary work, discharge native,
ownership or restoration obligations, or improve the selected conditional
$\kappa$.

## 1. Ordered-endpoint ratio theorem

**Theorem 1.** Suppose $0\le a<T\le b$. On $a<x<T$,

$$
R_{a,b}(x)=\frac{H_{a,b}(x)}{H_0(x)}
$$

is positive and nondecreasing. It is strictly increasing if $a>0$ or
$b>T$. If $a=0,b=T$, it is identically one.

**Proof.** Strict subadditivity of $z^t$ on positive arguments gives
$H_{a,T}(x)>0$, $H_0(x)>0$, and $H_{a,b}(x)>0$ in this open interval.
Write

$$
\begin{aligned}
H(x)&=H_{a,T}(x),\\
\Delta(x)&=H_{a,b}(x)-H(x)\\
 &=(b-x)^t-(T-x)^t-(b-a)^t+(T-a)^t,\\
E(x)&=H_0(x)-H(x)\\
 &=x^t-(x-a)^t-T^t+(T-a)^t.
\end{aligned}
$$

The function $H$ is strictly concave on $(a,T)$, is continuous on
$[a,T]$, and vanishes at both endpoints. In particular,

$$
H''(x)=t(t-1)\big((x-a)^{t-2}+(T-x)^{t-2}\big)<0.
$$

If $b=T$, then $\Delta=0$. If $b>T$, then

$$
\begin{aligned}
\Delta(a)&=0,\\
\Delta'(x)&=t\big((T-x)^{t-1}-(b-x)^{t-1}\big)>0,\\
\Delta''(x)&=t(1-t)\big((T-x)^{t-2}-(b-x)^{t-2}\big)>0.
\end{aligned}
$$

Thus $\Delta$ is nonnegative and convex, and it is positive and strictly
convex when $b>T$. Tangent-line inequalities at an interior point $x$,
evaluated at $a$, give

$$
\Delta'(x)\ge\frac{\Delta(x)}{x-a},\qquad
H'(x)\le\frac{H(x)}{x-a}.
$$

Consequently

$$
\left(\frac{\Delta}{H}\right)'(x)
=\frac{\Delta'H-\Delta H'}{H^2}\ge0.
$$

For $b>T$, the first tangent inequality is strict, so this derivative is
strictly positive.

If $a=0$, then $E=0$. If $a>0$, then

$$
\begin{aligned}
E(T)&=0,\\
E'(x)&=t\big(x^{t-1}-(x-a)^{t-1}\big)<0,\\
E''(x)&=t(1-t)\big((x-a)^{t-2}-x^{t-2}\big)>0.
\end{aligned}
$$

Thus $E$ is nonnegative and convex, and it is positive and strictly convex
when $a>0$. The tangent-line inequalities evaluated at $T$ give

$$
E'(x)\le-\frac{E(x)}{T-x},\qquad
H'(x)\ge-\frac{H(x)}{T-x}.
$$

It follows that

$$
\left(\frac{E}{H}\right)'(x)
=\frac{E'H-EH'}{H^2}\le0,
$$

strictly when $a>0$. The endpoint derivatives of $H$ need not be finite:
only derivatives at $x\in(a,T)$ and continuity at the endpoints were used.

Finally,

$$
R_{a,b}(x)
=\frac{H(x)+\Delta(x)}{H(x)+E(x)}
=\frac{1+\Delta(x)/H(x)}{1+E(x)/H(x)}.
$$

Its numerator is positive and nondecreasing, and its denominator is positive
and nonincreasing. At least one changes strictly if $a>0$ or $b>T$.
This proves all assertions. $\square$

## 2. No positive bill can hide behind a nonpositive left endpoint

**Theorem 2.** For the nonempty finite path list above,

$$
\big(\exists x\in[A,T]:G(x)>0\big)\quad\Longleftrightarrow\quad G(A)>0.
$$

If $A<T$, positivity at $A$ also implies positivity at some interior
point. In particular, **nonpositive endpoint bills cannot conceal a positive
interior bill**. The upper endpoint is always nonpositive, so only the lower
endpoint needs to be tested for this sign decision.

**Proof.** First, strict subadditivity, with the zero-argument boundary cases,
gives

$$
H_{a_i,b_i}(T)
=(T-a_i)^t+(b_i-T)^t-(b_i-a_i)^t\ge0.
$$

Since $H_0(T)=0$, we have $G(T)\le0$. This also handles the degenerate
case $A=T$, whose domain consists of the single point $T$.

Assume $A<T$. On $A<x<T$, let

$$
S(x)=\sum_{i=1}^m R_{a_i,b_i}(x).
$$

Theorem 1 makes $S$ nondecreasing, and

$$
\frac{G(x)}{H_0(x)}=1-S(x).
$$

If $A>0$, then $H_0(A)>0$. Continuity extends this normalized identity
to $A$, even for paths with $a_i=A$. Thus $G(A)\le0$ implies
$S(A)\ge1$, hence $S(x)\ge1$ and $G(x)\le0$ throughout $(A,T)$.
In fact $S$ is strictly increasing because at least one $a_i=A>0$,
so $G(x)<0$ for every $A<x<T$ in this case.

The remaining endpoint case is $A=0$. Then all $a_i=0$ and $b_i\ge T>0$.
The nonnegative remainder $\Delta$ from Theorem 1, now with $a=0$, gives
$H_{0,b_i}(x)\ge H_0(x)$. Therefore every ratio is at least one and
$S(x)\ge m\ge1$, so again $G(x)\le0$ throughout the interior.
Here $G(A)=G(0)=0$. The unweighted nonempty-list hypothesis is used in
the inequality $m\ge1$.

We have proved that $G(A)\le0$ rules out positive values everywhere.
Conversely, if $G(A)>0$, the lower endpoint itself is a positive value;
continuity gives positive values immediately to its right whenever $A<T$.
$\square$

**Corollary 3 (any permitted closed subinterval).** If

$$
A\le L<U\le T,
$$

then

$$
\big(\exists x\in[L,U]:G(x)>0\big)\quad\Longleftrightarrow\quad G(L)>0.
$$

If $L>0$, this follows by applying the same nondecreasing sum $S$ from
$L$ onward. If $L=0$, then $A=0$ and the special endpoint argument in
Theorem 2 applies. Positive $G(L)$ gives a positive interior neighborhood
by continuity. Thus the criterion applies even when additional constraints
restrict the allowed split dimension to a smaller interval.

**Corollary 4 (sign structure).** On $(A,T)$, the normalized bill
$G/H_0$ is nonincreasing. It is strictly decreasing unless every path is
exactly $[0,T]$. Consequently the positive set, when nonempty, is an
initial interval of the permitted domain. There is at most one interior
zero, except in the constant normalized case. In that exceptional case
$G=(1-m)H_0$, which is nonpositive and vanishes throughout the interior
only when $m=1$.

The monotonicity is for **$G/H_0$**. It does not assert that $G$ itself
is monotone or that $G$ attains its maximum at an endpoint.

## 3. Compatibility with the predecessor's counterexample

PR #7331 gives $t=1/2$, $T=24$, ambient $D=26$, and four paths

$$
(a_i,b_i)\in\{(3,25),(17,26),(0,25),(6,25)\}.
$$

Its rational interior point $x=3819/160$ has a larger bill than both
endpoints $A=17$ and $T=24$, with all three bills negative. Theorem 2
does not contradict that example: it excludes a **positive** interior bill
when $G(17)\le0$, while allowing an interior maximum below zero.
Multiplication by the positive, nonconstant factor $H_0(x)$ need not
preserve monotonicity of the normalized bill.

## 4. Unit path charges matter at the zero endpoint

Theorem 2 does not assert the same endpoint criterion for arbitrary positive
fractional path weights. For example, take $t=1/2$, $T=2$, one path
$(a,b)=(0,3)$, and weight $w=1/2$. Its weighted bill is

$$
G_w(x)=\sqrt{x}+\sqrt{2-x}-\sqrt2
       -\frac12\big(\sqrt{x}+\sqrt{3-x}-\sqrt3\big).
$$

At the endpoints,

$$
G_w(0)=0,\qquad
G_w(2)=-\frac12(\sqrt2+1-\sqrt3)<0.
$$

Nevertheless,

$$
G_w(1)=\frac{3+\sqrt3-3\sqrt2}{2}>0.
$$

The last comparison is exact: both sides of $3+\sqrt3>3\sqrt2$ are
positive, and squaring reduces it to $12+6\sqrt3>18$, or $\sqrt3>1$.
The ratio monotonicity still holds, but at $A=0$ a fractional weighted sum
need not be at least one. The proof's use of the unweighted nonempty list
cannot be dropped.

No theorem here covers a path ending before $T$, fractional or negative
path charges, ordinary implementation costs, or the legality of a proposed
word. A useful next application must first verify the endpoint inequalities
for every charged path in its actual rank bill.

Prepared by apoursh with substantial OpenAI Codex and subagent assistance.
The predecessor research and contributor lineage retain their attribution.
New work is Apache-2.0; no independent human or formal-kernel proof acceptance
is claimed.
