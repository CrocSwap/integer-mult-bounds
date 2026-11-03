# Exact consecutive cancellation batches

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract

Use coarse-grid units and half-up rounding

\[
R(t)=\lfloor t+1/2\rfloor,\qquad
F_g(t)=g^{-1}\lfloor gt+1/2\rfloor,\qquad g=2^s,\ s\geq1.
\]

Let \(t_k=c+(a/d)k\), where \(c\in\mathbb Q\), \(a\in\mathbb Z\),
\(d\geq1\), and \(\gcd(a,d)=1\). A source index is safe when
\(R(t_k)=F_g(t_k)\). This is precisely restoration of arbitrary target
dirt by the exact updates \(y\mathrel{+}=R(t_k)\),
\(y\mathrel{-}=F_g(t_k)\), with the source unchanged.

For a physical source \(x=k2^{-p}\), increment \(C+Ax\), and coarse
precision \(w\), substitute \(c=2^w C\) and reduce
\(2^{w-p}A=a/d\). No relation between \(p\) and \(w\) is needed for
this algebraic substitution. Internally rounded source computation and
rounding the target update are outside the contract.

PR1853 supplies the scalar cancellation interface. The new statements below
give its ordered run census, rather than its interval count. We spell out
the rounding cells to make the new argument self-contained.

## The run law

Put

\[
h=1/(2g),\quad m=\lfloor dc\rfloor,\quad \theta=dc-m,\quad
L=\lceil-dh-\theta\rceil,\quad U=\lceil dh-\theta\rceil-1,
\quad B=U-L+1.
\]

Here \(0\leq\theta<1\). For \(d>1\), also put

\[
v=a-d\lfloor a/d+1/2\rfloor,\quad u=|v|,\quad B=qu+r,
\qquad 0\leq r<u.
\]

The integer \(u\) is positive. Consider the bi-infinite sequence of safe
and unsafe indices, with period \(d\), and count a maximal safe run by
its first index modulo \(d\).

**Theorem.** For \(d>1\), the complete positive run-length histogram is

- \(r\) runs of length \(q+1\), if \(r>0\);
- \(u-r\) runs of length \(q\), if \(q>0\).

Thus there are \(\min(B,u)\) runs per period and their sharp maximum
length is \(\lceil B/u\rceil\), with value zero when \(B=0\).
For every positive integer \(\ell\), the exact number of start indices
modulo \(d\) at which \(\ell\) consecutive inputs are all safe is

\[
N_\ell=\max\{0,B-(\ell-1)u\}.
\]

Consequently a uniformly distributed source residue has safe-batch
probability \(N_\ell/d\). This is also the natural frequency along all
integer source indices. It is not a claim about an actual caller's source
distribution.

If \(B>0\), let \(j_*=L\) for \(v>0\) and \(j_*=U\) for
\(v<0\). One explicit start of a longest maximal run is

\[
k_*=(j_*-m)a^{-1}\pmod d.
\]

If \(d=1\), the sequence is constant: every index is safe exactly when
\(B=1\), and otherwise none is safe. In the first case every finite
batch length works and there is no finite longest run. There is no modular
inverse or division by \(u=0\) in this case.

## Proof

Write \(n=R(t)\). Since \(g\) is an integer, equality \(F_g(t)=n\)
holds exactly when

\[
n-h\leq t<n+h.
\]

These cells lie inside the coarse rounding cells. Their lower endpoint is
included and their upper endpoint is excluded. Thus a safe \(t\) has a
unique centered error in \([-h,h)\).

For our orbit, multiplying that centered error by \(d\) gives
\(\theta+j\), where \(j\) is an integer satisfying
\(j\equiv m+ak\pmod d\). Safety is equivalent to \(L\leq j\leq U\).
This integer interval has \(B\geq0\) elements. Its span satisfies
\(B-1<d/g\leq d/2\) whenever it is nonempty. Its elements are distinct
modulo \(d\), and \(\gcd(a,d)=1\) makes every one occur exactly once
in a source period. In particular \(B<d\) for \(d>1\), so every safe
run ends.

If two consecutive source indices are safe, their integer representatives
\(j,j'\in[L,U]\) satisfy \(j'-j\equiv a\pmod d\) and
\(|j'-j|\leq B-1<d/2\). Hence their difference must be the centered
representative \(v\). When \(a/d\) is a half-integer, \(d=2\) and
there is no such pair; this causes no exception to the histogram formula.
Conversely, \(j,j+v\in[L,U]\) identify two consecutive safe source
indices. The safety graph is therefore exactly the integer interval's
chains with step \(v\), with no edge that wraps around its endpoints.

Reverse the interval when \(v<0\). We are left with \(B\) consecutive
integers and step \(u>0\). The chains start at the first
\(\min(B,u)\) integers and have lengths

\[
1+\left\lfloor\frac{B-1-t}{u}\right\rfloor,
\qquad 0\leq t<\min(B,u).
\]

Division \(B=qu+r\) gives exactly the stated histogram. The first chain
has length \(\lceil B/u\rceil\). Solving its first representative's
congruence gives \(k_*\); the preceding and following source indices
are unsafe. Finally, a batch of length \(\ell\) must fit in one chain.
Its first integer representative can occupy exactly
\(\max(0,B-(\ell-1)u)\) positions in the interval. This proves the
batch count and all conclusions. The constant \(d=1\) case follows
directly from the rounding cells. \(\square\)

## Examples and cost

At coefficient \(1/1000\), zero offset and two extra precision bits,
\(L=-125\), \(U=124\), \(B=250\), and \(u=1\). There is one
maximal safe run of length 250 per period, starting at \(k=875\) modulo
1000. No interval of 251 consecutive inputs is safe. This sharp maximum
adds ordered batching information to PR1853's bounded-interval example.

At coefficient \(3/8\), zero offset and one extra bit, \(B=4\) and
\(u=3\). There are two runs of length one and one run of length two.
At coefficient \(1/2\), offset \(1/4\) and two extra bits, \(B=0\);
the entire source orbit is unsafe. Rational offsets cannot be discarded.

For coefficient \(1/(2^{100}+1)\), zero offset and three extra bits,
the sharp maximum is \(2^{97}+1\). The formula never enumerates that
period. Besides a constant number of exact rational/integer operations,
the constructor uses one extended Euclidean inverse modulo \(d\).
Its Euclidean-iteration count is \(O(\log d)\); this is an arithmetic
description, not a physical bit-operation, tape or runtime speedup claim.

## Scope and credit

woklerx's PR1853 supplies bounded mixed-precision counting, following
PR1848's lattice interface. Adam Gall's PR1908 supplies the actual rounded
source boundary and half-open-cell context. Credit Gareth Davidson,
Chafik Boukhalfa, Ali Romman and the retained dirty-leaf lineage.
Nick Petalas's older PR4881 gives a universal affine-box test and PR4878
a period-density bound; neither supplies this ordered run census.
Interval rotations and division into residue chains are classical.
No global literature-priority claim is made.

This is a scoped written proof with finite exact corroboration. The finite
checker does not prove its unbounded quantifiers. There is no native caller,
source reachability proof, physical batch scheduler, complete paid invoice,
compiler admission or new kappa. All five selected framework assumptions
remain. Independent human and formal proof-kernel review are unclaimed.
