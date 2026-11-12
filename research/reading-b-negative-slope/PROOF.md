# Reading B when the slope is negative

The selected frontier is unchanged. This note proves the two-part existence
test that [PR #7299](https://github.com/CrocSwap/integer-mult-bounds/pull/7299)
left open for a negative rank slope. It does not construct a caller, read an
invoice, or claim a new κ. The selected value remains
\(363005817/100000000000\).

## Hypotheses

Fix an integer rank \(R\ge 2\). Let \(\varphi\) be a real function on
\(\{0,\ldots,R\}\) with \(\varphi(0)=0\), nondecreasing and concave: the first
differences \(\delta(j)=\varphi(j)-\varphi(j-1)\) satisfy

\[
\delta(1)\ge\delta(2)\ge\cdots\ge\delta(R)\ge 0.
\]

The slope \(d\) is real and strictly negative. The flat fee \(c\) is real. The
predecessor contract takes \(c\ge 0\); the comparison proved here does not use
the sign of \(c\).

A positive partition of \(R\) is \(r_1+\cdots+r_k=R\) with each \(r_i\ge 1\).
Reading B charges \(c+d\,\varphi(r_i)\) on \(k-1\) pieces and leaves one piece
free. The free piece maximises the credit. The unsplit target pays no split
fee, so

\[
\Delta_B
  =\varphi(r_*)+(1-d)\sum_{i\neq *}\varphi(r_i)-(k-1)c-\varphi(R),
\]

where \(r_*\) maximises \(d\,\varphi(r_i)\). This is the formula stated in
#7299. Because \(d<0\), that piece has minimum \(\varphi\). A shortest piece
has minimum \(\varphi\), since \(\varphi\) is nondecreasing. If several pieces
share that minimum value, freeing any one of them gives the same
\(\Delta_B\): \(\varphi(r_*)\) is unchanged and the charged pieces keep the
same multiset of \(\varphi\)-values. The argument below frees a shortest piece.

For \(1\le b\le\lfloor R/2\rfloor\) write

\[
\gamma(b)=\varphi(b)+(1-d)\varphi(R-b)-\varphi(R)
\]

for the \(c\)-free credit of the two-part split \((b,R-b)\), freeing \(b\).
Let

\[
G=\max_{1\le b\le\lfloor R/2\rfloor}\gamma(b).
\]

The nonnegative-slope test in #7299 frees the long piece and uses

\[
\lambda(b)=\varphi(R-b)+(1-d)\varphi(b)-\varphi(R).
\]

For \(d<0\),

\[
\gamma(b)-\lambda(b)=-d\bigl(\varphi(R-b)-\varphi(b)\bigr)\ge 0.
\]

The two formulas agree when \(\varphi(b)=\varphi(R-b)\). They differ when the
long piece has strictly larger tariff.

## Theorem

Assume the hypotheses above, including \(d<0\).

1. \(G\ge 0\). For every partition into a shortest piece \(s\) and \(m\ge 1\)
   charged pieces \(e_1,\ldots,e_m\),

\[
\varphi(s)+(1-d)\sum_{q=1}^{m}\varphi(e_q)-\varphi(R)\le mG.
\]

Equivalently, \(\Delta_B\le m(G-c)\).

2. Some partition has \(\Delta_B>0\) if and only if some two-part partition
   has \(\Delta_B>0\), and both are equivalent to \(c<G\). In the improving
   two-part split the free piece is a shortest piece.

The rank \(R=1\) has only the unsplit target. Its credit difference is \(0\),
and it has no two-part split, so both sides of the existence statement are
false.

## Proof

**The threshold is nonnegative.** For \(1\le b\le\lfloor R/2\rfloor\),

\[
\gamma(b)
  =\sum_{j=1}^{b}\delta(j)
   -\sum_{j=R-b+1}^{R}\delta(j)
   -d\,\varphi(R-b).
\]

The tail sum equals \(\sum_{j=1}^{b}\delta(R-b+j)\). Each index satisfies
\(j\le R-b+j\), so \(\delta(j)\ge\delta(R-b+j)\). The term
\(-d\,\varphi(R-b)\) is nonnegative because \(d<0\) and
\(\varphi(R-b)\ge\varphi(0)=0\). Thus every \(\gamma(b)\) is nonnegative, and
\(G\ge 0\).

**One-piece gap.** Let \(p\ge 0\) and \(e\ge 1\) be integers with
\(p+e\le R-1\). Then

\[
(1-d)\bigl(\varphi(p)+\varphi(e)-\varphi(p+e)\bigr)\le G.
\]

The gap is nonnegative: \(\varphi(p+e)-\varphi(p)=\delta(p+1)+\cdots+\delta(p+e)\)
is at most \(\delta(1)+\cdots+\delta(e)=\varphi(e)\). It is nondecreasing in
the prefix, because its forward difference is
\(\delta(p+1)-\delta(p+1+e)\ge 0\).

Suppose first that \(e\le\lfloor R/2\rfloor\). The largest admissible prefix
is \(p_*=R-1-e\), so the gap is at most
\(\varphi(e)+\varphi(R-1-e)-\varphi(R-1)\). Compare that quantity with
\(\gamma(e)\):

\begin{align*}
&\gamma(e)-(1-d)\bigl(\varphi(e)+\varphi(R-1-e)-\varphi(R-1)\bigr)\\
&\quad=\varphi(e)+(1-d)\varphi(R-e)-\varphi(R)
  -(1-d)\varphi(e)-(1-d)\varphi(R-1-e)+(1-d)\varphi(R-1)\\
&\quad=d\,\varphi(e)+(1-d)\delta(R-e)+(1-d)\varphi(R-1)-\varphi(R)\\
&\quad=d\bigl(\varphi(e)-\varphi(R-1)\bigr)+(1-d)\delta(R-e)-\delta(R).
\end{align*}

The index \(R-e\) lies between \(1\) and \(R-1\). Also \(e\le R-1\), so
\(\varphi(e)\le\varphi(R-1)\). Combined with \(d<0\), the first summand is
nonnegative. The coefficient \(1-d\) is strictly greater than \(1\), and
\(\delta(R-e)\ge\delta(R)\), so the remaining expression is nonnegative.
Therefore \((1-d)\) times this gap is at most \(\gamma(e)\le G\).

Suppose instead that \(e\ge\lfloor R/2\rfloor+1\). Then
\(p\le R-1-e\le\lceil R/2\rceil-2\). Whenever such a pair exists,
\(p\le\lfloor R/2\rfloor\). The gap equals
\(\varphi(p)-(\varphi(p+e)-\varphi(e))\le\varphi(p)\), because \(\varphi\) is
nondecreasing. If \(p=0\), the gap is \(0\le G\). If \(p\ge 1\),

\begin{align*}
\gamma(p)-(1-d)\varphi(p)
  &=d\,\varphi(p)+(1-d)\varphi(R-p)-\varphi(R)\\
  &=-d\bigl(\varphi(R-p)-\varphi(p)\bigr)-\bigl(\varphi(R)-\varphi(R-p)\bigr).
\end{align*}

Both summands are nonnegative: \(p\le R-p\), so \(\varphi(R-p)\ge\varphi(p)\)
and \(-d>0\), and \(\varphi\) itself is nondecreasing. Thus
\((1-d)\varphi(p)\le\gamma(p)\le G\). Since the gap is at most \(\varphi(p)\)
and \(1-d>0\), \((1-d)\) times the gap is at most \(G\).

**Chain.** Let \(s\) be a shortest piece and let \(e_1,\ldots,e_m\) be the
charged pieces, \(m\ge 1\), with sum \(L=R-s\). Then \(1\le s\le\lfloor R/2\rfloor\)
and \(L\le R-1\). Set \(L_0=0\) and \(L_q=e_1+\cdots+e_q\). For these values,

\[
\sum_{q=1}^{m}\varphi(e_q)-\varphi(L)
  =\sum_{q=1}^{m}\bigl(\varphi(L_{q-1})+\varphi(e_q)-\varphi(L_q)\bigr).
\]

The \(q=1\) summand is \(\varphi(0)=0\). Each later summand is a one-piece gap
whose prefix and piece add to at most \(L\le R-1\), so the bound above is at
most \(G/(1-d)\). There are \(m-1\) such summands, and \(1-d>0\), hence

\[
(1-d)\Bigl(\sum_{q=1}^{m}\varphi(e_q)-\varphi(L)\Bigr)\le(m-1)G.
\]

The same free piece has two-part value \(\gamma(s)\le G\), and

\begin{align*}
\varphi(s)+(1-d)\sum_{q=1}^{m}\varphi(e_q)-\varphi(R)
  &=\gamma(s)+(1-d)\Bigl(\sum_{q=1}^{m}\varphi(e_q)-\varphi(L)\Bigr)\\
  &\le G+(m-1)G=mG.
\end{align*}

Subtracting \(mc\) gives \(\Delta_B\le m(G-c)\).

**Existence.** If \(c<G\), a maximising two-part split has
\(\Delta_B=\gamma(b)-c>0\). If \(c\ge G\), every partition has
\(\Delta_B\le m(G-c)\le 0\). A strict improvement therefore exists exactly
when \(c<G\).

## The bound does not name the maximiser

The inequality decides the sign of the best credit. It does not say that a
two-part split attains that best credit.

On the harmonic numbers \(H_n\), at \(R=6\), \(d=-1\) and \(c=0\),

\[
\Delta_B(2,2,2)=H_2+2(H_2+H_2)-H_6=101/20,
\]

while the best two-part split is \((4,2)\) at \(G=193/60\). The three-part
credit is strictly larger because \(101/20>193/60\). Its per-piece ratio is
\(101/40\), and \(101/40<193/60\), so every fee that makes the two-part splits
nonpositive also makes this three-part split nonpositive.

The constant in the per-piece bound is attained by a split with more than two
parts. For \(\varphi(n)=\min(n,1)\), \(R=8\) and \(d=-1\), every positive
piece has tariff \(1\), \(G=2\), and \((6,1,1)\) has \(c\)-free credit
\(4=2G\). At \(c=G\) this split and every two-part split have \(\Delta_B=0\).
Strict positivity still starts at the same fee.

For the identity tariff the gaps vanish. If \(\varphi(n)=\alpha n\) with
\(\alpha\ge 0\), the \(c\)-free credit of a partition depends only on its
shortest piece \(s\):

\[
\gamma(s)=-d\,\alpha(R-s),\qquad G=-d\,\alpha(R-1).
\]

Every partition that contains a piece of rank \(1\) ties the two-part split
\((R-1,1)\) at \(c=0\). For \(c>0\), each extra charged piece lowers the
credit by a further \(c\).

## Where the nonnegative argument stops

#7299 proves the existence statement for \(d\ge 0\) by freeing a longest piece.
Two steps of that argument use the longest piece.

Its two-part hypothesis is \(\lambda(b)\le c\), in \(c\)-free form. On the
identity tariff at \(R=6\) and \(d=-1\), \(\lambda(b)=b\) and \(\gamma(b)=6-b\).
The long-free maximum is \(3\) and the short-free maximum is \(5\). At \(c=4\)
every long-free comparison is nonpositive, but \((5,1)\) frees the piece \(1\)
and has \(\Delta_B=1\).

The length step fails for the same reason. That proof bounds every charged
piece by \(\lfloor(R-1)/2\rfloor\), because the free piece is a longest piece
and another positive piece remains. For \(d<0\) the free piece is a shortest
piece, so a charged piece can exceed half the rank. In the partition
\((4,1,1)\) of rank \(6\), the free piece is \(1\) and a charged piece is \(4\),
while \(\lfloor 5/2\rfloor=2\).

The suffix-window lemma is not reused, and this note does not claim that the
lemma is false under its own hypotheses. The one-piece gap bound replaces that
step when \(d<0\).

## Concavity is necessary

Let \(R=5\), \(d=-1\), \(c=0\) and \(\varphi=(0,0,1,1,1,3)\) on
\(\{0,\ldots,5\}\). This tariff is nondecreasing and vanishes at \(0\), but
its differences \((0,1,0,0,2)\) are not nonincreasing. The two-part values are
\(\gamma(1)=-1\) and \(\gamma(2)=0\). The partition \((2,2,1)\) frees the
piece \(1\) and has

\[
\Delta_B=0+2\bigl(\varphi(2)+\varphi(2)\bigr)-\varphi(5)=4-3=1>0.
\]

The nonconcave table \((0,0,1,1,1,1,2)\) from #7299 separates the same
statement at \(R=6\), \(d=-1\) and \(c=1\). Every two-part value is at most
\(1\), so every two-part credit is nonpositive, while \((2,2,2)\) has
\(c\)-free credit \(3\) and \(\Delta_B=1\).

## Scope of the claim

The result is a proof under the stated hypotheses, for every rank and every
real \(d<0\). It is not an unrestricted statement about partitions whose
tariff fails concavity, monotonicity, or \(\varphi(0)=0\). A positive value of
\(\Delta_B\) is an accounting comparison. It is not a claim that a caller
realises the split, and it does not change the selected frontier.
