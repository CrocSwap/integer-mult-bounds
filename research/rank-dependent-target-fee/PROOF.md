# Rank-dependent fees for one target split

The selected frontier is unchanged. This note proves two readings of the fee
shape left open by the uniform-fee theorem. It does not construct a caller,
read an invoice, or claim a new κ.

## Hypotheses

Fix an integer rank \(R \ge 1\). Let \(\varphi\) be a real function on
\(\{0,\ldots,R\}\) with \(\varphi(0) = 0\), nondecreasing and concave:
the first differences \(\delta(j) = \varphi(j) - \varphi(j-1)\) satisfy
\(\delta(1) \ge \delta(2) \ge \cdots \ge \delta(R) \ge 0\). Concavity and
\(\varphi(0) = 0\) give subadditivity on this range. For \(a,b \ge 0\) with
\(a+b \le R\),

\[
\varphi(a) = \varphi\Bigl(\frac{a}{a+b}(a+b)\Bigr)
  \ge \frac{a}{a+b}\varphi(a+b),
\]

and likewise for \(b\), so \(\varphi(a)+\varphi(b) \ge \varphi(a+b)\). The
same bound extends to every positive integer partition of an integer at most
\(R\).

A positive partition of \(R\) is \(r_1+\cdots+r_k = R\) with each \(r_i \ge 1\).
The flat fee \(c\) is nonnegative. The rank slope \(d\) is rational. Both
readings use the fee expression \(c + d\,\varphi(r_i)\), and they differ only
in which pieces pay it.

## Reading A: every piece pays, including the unsplit target

The split credit is \(\sum_i\bigl(\varphi(r_i) - c - d\,\varphi(r_i)\bigr)\).
The unsplit target pays the same formula at rank \(R\). The difference is

\[
\Delta_A = (1-d)\Bigl(\sum_i \varphi(r_i) - \varphi(R)\Bigr) - (k-1)c.
\]

Write \(\psi = (1-d)\varphi\) and \(S(k)\) for the sum of \(\psi\) on the
balanced \(k\)-partition: if \(R = qk+s\) with \(0 \le s < k\), then
\(S(k) = s\,\psi(q+1) + (k-s)\psi(q)\).

**Theorem A.**

1. If \(d < 1\), then \(\psi\) is nondecreasing and concave with \(\psi(0)=0\).
   For each \(k\), the balanced partition maximises \(\sum \psi(r_i)\). The
   sequence \(S(k)\) is concave for \(1 \le k \le R\). The maximum of
   \(\Delta_A\) equals \(\max_k\bigl(S(k) - \psi(R) - (k-1)c\bigr)\), attained
   at the least \(k\) such that \(S(k+1)-S(k) \le c\), or at \(k=R\) if no
   such \(k\) exists. A split has \(\Delta_A > 0\) if and only if
   \[
   (1-d)\bigl(\varphi(\lfloor R/2\rfloor)+\varphi(\lceil R/2\rceil)-\varphi(R)\bigr) > c.
   \]
2. If \(d \ge 1\), then \(\Delta_A \le 0\) for every partition. Among
   partitions with a fixed \(k \ge 2\), \(\Delta_A\) is maximised by an
   extreme partition \((R-k+1,1,\ldots,1)\) and minimised by a balanced
   partition. The two values differ exactly when those partitions have
   different \(\varphi\)-sums. The global maximum is still the unsplit
   target.

**Proof.** Subadditivity gives \(\sum \varphi(r_i) \ge \varphi(R)\). For
\(d \ge 1\) and \(c \ge 0\) the first term of \(\Delta_A\) is nonpositive and
the fee term is nonpositive, so \(\Delta_A \le 0\).

For a fixed length \(k\), the balanced vector is majorised by every other
positive integer vector of that length and sum, and the extreme vector
majorises every such vector. Karamata's inequality says that a concave
function has the larger sum on the majorised vector. Thus \(\sum \varphi\) is
maximised by the balanced partition and minimised by the extreme partition.
If \(d>1\), the coefficient \(1-d\) is negative, so these directions reverse
for \(\Delta_A\): the extreme partition is best among that \(k\) and the
balanced partition is worst. The inequality is strict precisely when the
\(\varphi\)-sums differ. If \(d=1\), then \(\Delta_A = -(k-1)c\), which
depends only on \(k\).

Now let \(d<1\). Then \(\psi\) inherits the three tariff hypotheses, and
\(\Delta_A = \sum \psi(r_i) - \psi(R) - (k-1)c\). The same majorisation gives
the balanced maximiser. The identity \(S(k) = k\,\psi(R/k)\) holds for the
piecewise-linear interpolant of \(\psi\), because that interpolant agrees with
\(\psi\) on integers and is linear between them. The perspective
\(k \mapsto k\,\psi(R/k)\) of a concave function is concave for \(k>0\), so
its integer samples \(S(k)\) have nonpositive second differences. Subtracting
the linear fee \((k-1)c\) preserves concavity. A concave sequence attains its
maximum at the first position whose forward difference is nonpositive, which
is the stated least \(k\). Strict improvement over \(k=1\) occurs exactly
when the first forward difference is positive, and \(S(2)-S(1)\) is the
displayed halving expression. ∎

The hypothesis \(c \ge 0\) is necessary for the \(d \ge 1\) sign. For
\(\varphi(n)=n\), \(d=2\) and the partition \((1,3)\), \(\Delta_A = 1\) at
\(c=-1\). Under Reading B the same partition has
\(\Delta_B = -(k-1)(d+c)\) on this linear tariff, so \(c=-3\) gives
\(\Delta_B = 1\). Concavity is necessary for the halving test. On
\(\varphi = (0,0,1,1,1,1,2)\) at \(R=6\), with \(d=c=0\), both halves gain
nothing, while \((2,2,2)\) has \(\Delta_A = 1\).

## Reading B: only the extra pieces pay

Number the parts so that one part is free and the other \(k-1\) parts pay
\(c + d\,\varphi(r_i)\). The free part is chosen to maximise the credit.
The difference from the unsplit target, which pays no split fee, is

\[
\Delta_B = (1-d)\sum_i \varphi(r_i) + d\,\varphi(r_\ast) - (k-1)c - \varphi(R),
\]

where \(r_\ast\) maximises \(d\,\varphi(r_i)\). For \(d>0\) this is a part of
maximum \(\varphi\), hence a longest part because \(\varphi\) is
nondecreasing. For \(d=0\) the free part does not appear. For \(d<0\) it is
a part of minimum \(\varphi\).

At \(d=0\), \(\Delta_B\) is exactly \(\Delta_A\), so Theorem A applies and
the balanced partition is optimal.

**Theorem B.** Assume \(d \ge 0\).

1. If \(d \ge 1\), then \(\Delta_B \le 0\) for every partition.
2. A partition with \(\Delta_B > 0\) exists if and only if some two-part
   partition has \(\Delta_B > 0\). Equivalently,
   \[
   \max_{1 \le b \le \lfloor R/2\rfloor}
     \bigl(\varphi(R-b) + (1-d)\varphi(b) - \varphi(R)\bigr) > c.
   \]
   The free part in that two-part split is the longer part \(R-b\).
3. The maximiser need not be balanced when \(d>0\). For \(\varphi(n)=n\),
   \(R=6\), \(k=3\), \(d=1/2\) and \(c=0\), the balanced split \((2,2,2)\)
   has \(\Delta_B = -2\) and the extreme split \((4,1,1)\) has
   \(\Delta_B = -1\).

The two-part test decides existence only. It does not say that a two-part
split is optimal. For the harmonic tariff, \(R=6\), \(d=1/2\) and \(c=0\),
\((4,1,1)\) has \(\Delta_B = 19/30\), while the best two-part split is
\((4,2)\) at \(23/60\) and the balanced split is at \(11/20\).

**Proof of the sign for \(d \ge 1\).** Let \(F\) be a longest part and let
the other parts sum to \(E\). Subadditivity and \(1-d \le 0\) give
\((1-d)\sum \varphi(e_i) \le (1-d)\varphi(E) \le 0\). Since \(\varphi\) is
nondecreasing, \(\varphi(F) \le \varphi(R)\). Hence
\(\Delta_B \le \varphi(F) - \varphi(R) \le 0\). ∎

**Proof of the two-part test.** Sufficiency is immediate: a two-part
partition is a partition, and for \(d \ge 0\) the longer part is a legal
free part. The displayed maximum is exactly the best such \(c\)-free gain.

For necessity, suppose every two-part split has \(\Delta_B \le 0\). Then
for every \(1 \le b \le \lfloor R/2\rfloor\),

\[
\varphi(R-b) + (1-d)\varphi(b) \le \varphi(R) + c. \tag{H}
\]

The case \(k=1\) has \(\Delta_B=0\). Fix \(k \ge 3\), and let \(r_1\) be a
longest part, with charged parts \(e_1,\ldots,e_m\), \(m=k-1 \ge 2\). Each
charged part is at most \(\lfloor(R-1)/2\rfloor\): the longest part is at
least as large as any charged part, and at least one further positive part
remains, so \(R \ge 2e_q+1\). In particular the complement \(R-e_q\) is
strictly longer than \(e_q\), and (H) applies:

\[
(1-d)\varphi(e_q) \le c + \bigl(\varphi(R)-\varphi(R-e_q)\bigr).
\]

Summing over the charged parts,

\[
(1-d)\sum_q \varphi(e_q)
  \le mc + \sum_q\bigl(\varphi(R)-\varphi(R-e_q)\bigr).
\]

It remains to show that the sum of those end windows is at most the tail
after \(r_1\). Let \(L = R-r_1 = \sum e_q\) and
\(t_s = \delta(r_1+s)\) for \(s=1,\ldots,L\). Then
\(t_1 \ge \cdots \ge t_L \ge 0\), and each \(e_q \le L\). The end window of
length \(e_q\) is the suffix \(t_{L-e_q+1}+\cdots+t_L\). The suffix-window
lemma below gives

\[
\sum_q\bigl(\varphi(R)-\varphi(R-e_q)\bigr) \le \varphi(R)-\varphi(r_1).
\]

Therefore

\[
\varphi(r_1) + (1-d)\sum_q \varphi(e_q) - \varphi(R) \le mc,
\]

which is \(\Delta_B + mc \le mc\), so \(\Delta_B \le 0\). ∎

**Suffix-window lemma.** Let \(t_1 \ge \cdots \ge t_L \ge 0\) and let
\(e_1+\cdots+e_m = L\) with each \(e_q \ge 1\). Then

\[
\sum_q\sum_{j=0}^{e_q-1} t_{L-j} \le \sum_{s=1}^L t_s.
\]

**Proof.** The left side is \(\sum_{j=0}^{L-1} m_j t_{L-j}\), where
\(m_j\) is the number of parts strictly larger than \(j\). Thus
\(m_0 \ge m_1 \ge \cdots\) and \(\sum_j m_j = L\). Set \(u_j = t_{L-j}\), so
\(u\) is nondecreasing, and set \(z_j = m_j-1\). Then \(\sum z_j = 0\) and
\(z\) is nonincreasing. If \(z_0 < 0\), every term would be negative and the
sum could not be zero, so \(z_0 \ge 0\). Let \(p\) be the last index with
\(z_p \ge 0\). Then \(z_j \ge 0\) for \(j \le p\) and \(z_j \le 0\) for
\(j > p\). Hence

\[
\sum_j z_j u_j = \sum_j z_j(u_j-u_p) \le 0,
\]

because each summand is nonpositive. Therefore
\(\sum m_j u_j \le \sum u_j\). ∎

## What fails when the free piece is subsidised

For \(d<0\), Reading B still has an explicit balancedness failure, but this
note does not prove the two-part existence test. For \(\varphi(n)=n\),
\(R=6\), \(k=3\), \(d=-1\) and \(c=0\),

\[
\Delta_B = 6 - r_{\min}.
\]

The balanced split scores \(4\) and \((4,1,1)\) scores \(5\). The negative
slope makes the free piece the short one, so the extreme split is better.

The verifier exhausts a finite box for the missing existence statement.
That census is not a proof for every rank and every concave tariff. The box
and its result are stated in the README.
