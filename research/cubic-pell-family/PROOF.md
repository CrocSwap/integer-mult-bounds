# A Pell family for the fixed cubic repair

## Scope and provenance

This answers Open next question 2 of Nick Petalas's
[PR6653](https://github.com/CrocSwap/integer-mult-bounds/pull/6653): its
certificates at arities 7 and 97 have defect weights `(-r,r/2,r/2)` on
directions `(0,d,e)`; does this pattern extend to an infinite family?
The answer is yes. We also classify **this fixed weight pattern with rational
directions**, not all three-query repairs.

The fixed cubic reader comes from PR6200. The repair interface and cited
three-query lower bound are apoursh's PR6212; PR6215 treats another direction
family. AAAmirinu's PR6246 and CubeJerry's PR6250 supply the earlier
power-of-two and power-of-two-plus-one branches. PR6653 supplies the explicit
question, the two seed certificates and their predecessor attribution. Its
node lemma is consistent with the calculation below, but the proof here uses
direct coefficient comparison. The source manifests identify the exact bytes
consulted. Classical Pell descent and power-sum identities are not claimed as
new mathematics.

This is a polynomial identity and a literal restoration program. Query counts
are local operation counts, not a physical cost or a complete recursive
invoice. There is no new supplier admission or κ claim.

## 1. The defect and fixed weight pattern

Let the integer arity satisfy $r>2$. All $r$ children are retained:

```text
repeat r times:
    y += a^3
    a += b
```

For arbitrary entry values $y=Y,a=A,b=B$, their endpoint is

$$
 a=A+rB,\qquad b=B,\qquad
 y=Y+\sum_{i=0}^{r-1}(A+iB)^3.
$$

The target eager endpoint is $a=A,b=B,y=Y+rA^3$. Thus the defect to remove is

$$
 D_r(A,B)=3S_1A^2B+3S_2AB^2+S_3B^3,
$$

where

$$
 S_1=\frac{r(r-1)}2,\qquad
 S_2=\frac{r(r-1)(2r-1)}6,\qquad
 S_3=\frac{r^2(r-1)^2}4.
$$

For rational directions $d,e$, consider the fixed pattern

$$
 W_{r,d,e}(A,B)
 =-rA^3+\frac r2(A+dB)^3+\frac r2(A+eB)^3.                 \tag{1}
$$

**Theorem 1 (classification of the fixed pattern).** For every integer $r>2$,
the identity $W_{r,d,e}=D_r$ holds with rational $d,e$ if and only if there
is a positive integer $n$ such that

$$
 r^2-3n^2=1,\qquad
 \{d,e\}=\left\{\frac{r-1-n}{2},\frac{r-1+n}{2}\right\}.       \tag{2}
$$

In every such case the directions are integers, and after ordering them they
satisfy $0<d<e<r$. Consequently, allowing noninteger dyadic or arbitrary
rational directions adds no arities within (1).

*Proof.* The $A^3$ coefficient of (1) vanishes. Its $A^2B$ and $AB^2$
coefficients agree with those of $D_r$ exactly when

$$
 d+e=r-1,\qquad d^2+e^2=\frac{(r-1)(2r-1)}3.                \tag{3}
$$

Hence

$$
 de=\frac{(r-1)(r-2)}6,\qquad
 (e-d)^2=\frac{r^2-1}{3}.                                  \tag{4}
$$

If $n=|e-d|=p/q$ in lowest terms with $q>0$, then

$$
 3p^2=(r^2-1)q^2.
$$

Since $p^2$ and $q^2$ are coprime, $q^2\mid3$, forcing $q=1$.
Thus $n$ is an integer and (2) follows. It is positive because $r>2$.

Conversely, suppose (2). Equations (3) and (4) hold. The remaining moment is
also correct:

$$
 \frac r2(d^3+e^3)
 =\frac r2\bigl((d+e)^3-3de(d+e)\bigr)
 =\frac{r^2(r-1)^2}{4}=S_3.
$$

All four coefficients therefore agree.

Modulo 4, $r^2-3n^2=1$ implies that $r$ odd makes $n$ even, and $r$
even makes $n$ odd. Thus $r-1\pm n$ is even and both directions are
integers. Furthermore

$$
 (r-1)^2-n^2=\frac{2(r-1)(r-2)}3>0,
$$

so $n<r-1$ and $d>0$. Positivity of $n$ gives $d<e$, while $n<r+1$
gives $e<r$. This proves all assertions. ∎

There is a useful exact residual before imposing the Pell equation. For
arbitrary $r,n$, set $d=(r-1-n)/2$, $e=(r-1+n)/2$, and

$$
 P=r^2-3n^2-1.
$$

Direct expansion gives

$$
 W_{r,d,e}-D_r
 =-\frac{rP}{8}B^2\bigl(2A+(r-1)B\bigr).                  \tag{5}
$$

Here the displayed formula for $D_r$ is interpreted polynomially if $r$
is not an integer. Formula (5) identifies the failure off the Pell curve;
agreement on a special input such as $B=0$ does not certify the identity.

## 2. Every positive solution and an elementary recurrence

Define integer pairs by

$$
 (r_0,n_0)=(1,0),\qquad
 r_{k+1}=2r_k+3n_k,\quad n_{k+1}=r_k+2n_k.                \tag{6}
$$

Equivalently, $r_k+n_k\sqrt3=(2+\sqrt3)^k$. Equation (6), without any
irrational arithmetic, preserves $r_k^2-3n_k^2=1$. For $k\ge1$, both
coordinates are positive and strictly increase. The first pairs are

$$
 (1,0),\ (2,1),\ (7,4),\ (26,15),\ (97,56),\ (362,209),
 \ (1351,780).
$$

**Theorem 2 (exhaustiveness).** Every positive integer solution of

$$
 r^2-3n^2=1
$$

is exactly one pair $(r_k,n_k)$ with $k\ge1$. The nondegenerate repairs
of Theorem 1 correspond precisely to $k\ge2$.

*Proof.* For any positive solution, $n<r\le2n$. The right equality occurs
only at $(r,n)=(2,1)$, because $r^2=3n^2+1\le4n^2$, with equality only
when $n=1$. Apply the integral inverse of (6):

$$
 r'=2r-3n,\qquad n'=2n-r.                                \tag{7}
$$

We have $r'>0$, since $r>\sqrt3n>3n/2$, and $0\le n'<n$.
The norm remains $r'^2-3n'^2=1$. Thus descent terminates at $n'=0$,
where the positive first coordinate must be 1. Reversing the descent gives
(6), and the deterministic inverse makes the index unique. At $k=1$,
$r=2,d=0,e=1$, so two directions coincide; this excluded boundary does not
contradict the lower-bound statement for $r>2$. ∎

## 3. Infinitely many arities outside the earlier classes

For comparison with the classes listed by PR6653, use the even-index
subsequence

$$
 R_j=r_{2j},\qquad N_j=n_{2j},\qquad j\ge0.
$$

It has the recurrence

$$
 (R_0,N_0)=(1,0),\qquad
 R_{j+1}=7R_j+12N_j,\quad N_{j+1}=4R_j+7N_j.             \tag{8}
$$

All $R_j$ are odd. They also satisfy

$$
 R_{j+2}=14R_{j+1}-R_j,
$$

so modulo 9 their values repeat $1,7,7$. Indeed the first four residues
are $1,7,7,1$, the next is 7, and the two-coordinate recurrence then repeats
its initial state. Therefore

$$
 R_j\equiv7\pmod9\quad\hbox{when }j\equiv1,2\pmod3.    \tag{9}
$$

These arities lie outside the residue classes

$$
 r\bmod9\in\{0,1,2,5,8\}
$$

covered by the cited PR6212/PR6215 constructions. They are at least 7, so
are not the exceptional arities 3 and 4. Being odd and greater than 1, they
are not powers of 2.

To exclude the power-of-two-plus-one branch, square the fundamental solution:

$$
 R_j=r_j^2+3n_j^2=1+6n_j^2.
$$

For every $j\ge1$, $R_j-1=6n_j^2$ is positive and divisible by 3; it
cannot be a power of 2. Hence $R_j\ne2^s+1$ for every nonnegative integer
$s$.

The indices $j\ge1$ with $j\not\equiv0\pmod3$ give infinitely many
strictly increasing arities outside **all the earlier infinite classes
listed by PR6653**. This comparison is with those precise classes, not a
claim to have classified every construction in the literature or every later
contribution. Its first values are

$$
 7,\ 97,\ 18817,\ 262087,\ 50843527,\ 708158977,\ldots.
$$

The first two are Petalas's already established finite certificates. The
uniform family and the complete fixed-pattern classification are the added
result; those seed examples are not claimed anew.

For example, at $r=18817,n=10864$, the directions are $d=3976,e=14840$
and the defect weights are $(-18817,18817/2,18817/2)$.

## 4. Three queries and three shears restore the dirty inputs

For any $k\ge2$, take the ordered integer directions $0<d<e<r$ from
Theorem 1. After the retained children, execute:

```text
a += (e-r)*b       # a = A+eB
y -= (r/2)*a^3
a -= n*b           # a = A+dB, since e-d=n
y -= (r/2)*a^3
a -= d*b           # a = A
y += r*a^3
```

All three shear coefficients are nonzero integers. All three query weights
are nonzero dyadic rationals. The program uses **three appended cube queries
and three source shears**. It writes no auxiliary register and never changes
$b$. Its correction to $y$ is $-W_{r,d,e}=-D_r$, so its exact endpoint is

$$
 (y,a,b)=(Y+rA^3,A,B).
$$

This holds as a polynomial identity, hence for arbitrary incoming $Y,A,B$
over the rationals or reals; neither source nor destination is assumed clean.
There is no deletion, replacement or reordering of the $r$ retained child
queries. Visiting directions in the order $e,d,0$ makes the last query
occur at the restored source, avoiding a separate fourth restoring shear.

The cited PR6212 lower bound excludes one- and two-query dyadic repairs for
$r>2$, including its stated general dyadic-frame model. Combining that
predecessor theorem with this construction makes the dyadic repair query
minimum **exactly three at these arities**, under that same model. The lower
bound is a dependency, not re-proved by the present finite checker.
In particular, query coefficients are fixed independently of input data;
the model has no output feedback into sources, nonlinear source changes,
intermediate observations or access to child interiors. One signed weighted
cube accumulation counts as one query, with source changes additional.

## 5. What this does not settle

The classification concerns the weight shape in (1). Failure of the Pell
equation excludes that shape only; it does not exclude other weights,
directions or dyadic frames, nor prove a four-query minimum at any other
arity. A verified finite prefix corroborates the formulas but is not the
proof of the infinite family; Sections 1–3 supply that proof.

The three-query/three-shear schedule has growing coefficients. Its native
query and shear costs, routing, precision, storage, full caller and recursive
invoice remain unpriced. The formal operation counts do not imply a saving
over eager restoration, a physical realization, or an improvement to the
selected conditional bound. No independent human or formal proof-kernel
acceptance is claimed.

Prepared by **apoursh** with substantial **OpenAI Codex and subagent
assistance**. Retain Nick Petalas, CubeJerry, AAAmirinu and the cited source
lineage above. Apache-2.0.
