# Exact prime-power coefficient and root valuations

## Statement and scope

Let \(p\) be prime, \(a\geq1\), \(r=p^a\), and \(u\) a primitive
\(r\)-th root of unity. Work in an algebraic closure of \(\mathbb Q_p\),
with the extension of the additive valuation normalized by
\(v(1-u)=1\). Put

\[
n=r-1,\qquad e_b=\varphi(p^b)=p^{b-1}(p-1)\quad(1\leq b\leq a),
\qquad
f(z)=\sum_{j=0}^{n}a_jz^j,\quad
a_j=\prod_{s=j+1}^{n}(1-u^s).
\]

The empty product is one. Then

\[
v(p)=e_a,\qquad
v(a_j)=\sum_{s=j+1}^{r-1}p^{v_p(s)}.
\tag{1}
\]

Here \(v_p(s)\) is the usual exponent of \(p\) in the integer \(s\).
The lower Newton polygon of \(f\) has vertices

\[
(r-p^b,\;b e_b)\quad(b=a,a-1,\ldots,1),
\qquad (r-1,0).
\tag{2}
\]

Its segment from level \(b\) to level \(b-1\) has horizontal length
\(e_b\) and slope

\[
-\lambda_b,\qquad
\lambda_b=1+\frac{(b-1)(p-1)}p.
\tag{3}
\]

Consequently, counted with algebraic multiplicity, exactly \(e_b\)
roots have valuation \(\lambda_b\), for every \(1\leq b\leq a\).
All root valuations are positive. In the alternative normalization
\(v_p(p)=1\), these valuations are \(\lambda_b/e_a\).

The formula also includes \(r=2\), though the finite checker starts at order 3.
This is an exact
nonarchimedean refinement of the kernel and algebraic-nonunit conclusion
in Ali Romman's PR621 [1]. It does not estimate complex root magnitudes,
change any kappa, or prove an all-size multiplication theorem. No
literature-priority or proof-assistant certification claim is made.
Concurrent PR796 by Hao Yan [3] independently submitted the same formula
before this package's final overlap refresh. The retained proof was developed
independently; its inclusion does not claim priority over that contribution.

## Eisenstein polynomial and root differences

The prime-power cyclotomic polynomial is

\[
\Phi_{p^a}(T)=\sum_{k=0}^{p-1}T^{k p^{a-1}}.
\]

In \(\mathbb F_p[T]\), the geometric-sum identity and Frobenius give

\[
\Phi_{p^a}(T)
=(T^{p^{a-1}}-1)^{p-1}=(T-1)^{e_a}.
\]

Thus \(F_a(X)=\Phi_{p^a}(1-X)\) has leading coefficient
\((-1)^{e_a}\), constant coefficient \(p\), and every other
coefficient divisible by \(p\). Its constant coefficient is not
divisible by \(p^2\). Up to its unit leading sign, \(F_a\) is
Eisenstein at \(p\), so it is irreducible over \(\mathbb Q_p\).

For completeness, its root valuation also follows directly. A root
of unity is a valuation unit. In the residue field of characteristic
\(p\), \(u^{p^a}=1\) implies \((\bar u-1)^{p^a}=0\), hence
\(\bar u=1\). Write \(x=v_p(1-u)>0\), initially using
\(v_p(p)=1\). In \(F_a(1-u)=0\), the constant term has valuation
one, each intermediate term has valuation at least \(1+i x>1\),
and the leading term has valuation \(e_a x\). The least valuation
cannot occur only once, so \(e_a x=1\). Therefore \(v=e_a v_p\)
has \(v(1-u)=1\) and \(v(p)=e_a\).

Take \(1\leq s<r\), and write \(s=p^t m\), with \(p\nmid m\).
The same argument applied to the primitive \(p^{a-t}\)-th root
\(u^{p^t}\) gives

\[
v(1-u^{p^t})=\frac{e_a}{\varphi(p^{a-t})}=p^t.
\]

The factorization

\[
1-u^s=(1-u^{p^t})\sum_{k=0}^{m-1}u^{k p^t}
\]

has a second factor reducing to \(m\neq0\) in the residue field.
It is a valuation unit. Hence

\[
v(1-u^s)=p^{v_p(s)}.
\tag{4}
\]

More generally, for \(i\not\equiv j\pmod r\), choose
\(s\in\{1,\ldots,r-1\}\) congruent to \(i-j\). Since \(u^j\)
is a unit, \(v(u^i-u^j)=p^{v_p(s)}\). Additivity on the nonzero
product defining \(a_j\) proves (1).

## Convex-hull inequality and attaining points

Define

\[
W(k)=\sum_{s=1}^{k}p^{v_p(s)}\quad(0\leq k\leq r-1).
\]

For \(1\leq s<r\), \(v_p(r-s)=v_p(s)\), so (1) gives
\(v(a_j)=W(r-1-j)\). Expanding each summand as
\(p^t=1+(p-1)\sum_{h=1}^{t}p^{h-1}\) yields the exact formula

\[
W(k)=k+(p-1)\sum_{t=1}^{a-1}p^{t-1}
                    \left\lfloor\frac{k}{p^t}\right\rfloor.
\tag{5}
\]

In particular, \(W(0)=0\), and for \(1\leq b\leq a\),

\[
W(p^b-1)
=p^b-1+(p-1)\sum_{t=1}^{b-1}p^{t-1}(p^{b-t}-1)
=b e_b.
\tag{6}
\]

Fix \(1\leq b\leq a\), set \(q=p^{b-1}\), and write
\(k=q-1+h\), where \(0\leq h\leq(p-1)q=e_b\) is an integer.
Terms with \(t\geq b\) in (5) vanish. For \(1\leq t<b\),

\[
\left\lfloor\frac{q-1+h}{p^t}\right\rfloor
=\frac q{p^t}-1+\left\lceil\frac h{p^t}\right\rceil.
\]

Subtracting (5) at \(q-1\) therefore gives

\[
\begin{aligned}
W(q-1+h)-W(q-1)
&=h+(p-1)\sum_{t=1}^{b-1}p^{t-1}
                         \left\lceil\frac h{p^t}\right\rceil\\
&\geq h+(p-1)\sum_{t=1}^{b-1}p^{t-1}\frac h{p^t}
=\lambda_b h.
\end{aligned}
\tag{7}
\]

For \(b\geq2\), equality holds precisely when \(q\mid h\).
For \(b=1\), both sums are empty and equality always holds.
In particular, both endpoints attain equality. Thus every coefficient
point lies on or above the chord between the consecutive points in
(2). The chord lengths are \(e_b\); (6) and (7) give slopes
\(-\lambda_b\), also for the last segment \(b=1\).

As \(j\) increases, \(b\) decreases, so these slopes strictly increase
when there is more than one segment. The resulting broken line is
convex, below every coefficient point, and attained at every listed
vertex. It is therefore exactly the lower convex hull. Indeed any
convex function below the coefficient points is below the chord on
each interval between these attained endpoints. There can be other
collinear coefficient points, but no additional vertices.

## From the polygon to root valuations

Here is a direct form of the Newton-polygon argument. For a nonzero
polynomial \(g(z)=\sum c_jz^j\) and real \(t\), define

\[
M_g(t)=\min_{c_j\neq0}\bigl(v(c_j)+jt\bigr).
\]

One has \(M_{gh}(t)=M_g(t)+M_h(t)\). To see equality despite possible
cancellation, choose the smallest minimizing coefficient indices
\(i_0,j_0\) for \(g,h\). In the coefficient of degree \(i_0+j_0\)
of their product, the term using these two indices is the unique
term with minimum weighted valuation. Any other equally small term
would require two minimizing indices, both at least the chosen ones,
with the same sum, which is impossible.

Since \(f\) is monic and \(a_0\neq0\), factor it over the algebraic
closure as \(f(z)=\prod_{\ell=1}^{n}(z-\alpha_\ell)\). The identity gives

\[
M_f(t)=\sum_{\ell=1}^{n}\min\{t,v(\alpha_\ell)\}.
\tag{8}
\]

By (2)--(3), \(M_f\) has a breakpoint at each \(t=\lambda_b\),
where its slope decreases by \(e_b\): at that value the minimum
passes across the corresponding polygon segment. In (8), each root
of valuation \(t\) causes exactly one such decrease. Thus the root
valuations and multiplicities are precisely (3). The lengths sum to
\(\sum_{b=1}^{a}e_b=p^a-1\), so all roots are accounted for.

For \(r=8\), the vertices are \((0,12),(4,4),(6,1),(7,0)\).
For \(r=27\), they are \((0,54),(18,12),(24,2),(26,0)\), as proposed.

## Exact extraction in the finite replay

The verifier represents each coefficient as an integer polynomial of degree
less than \(e_a\) in \(u\), then substitutes \(u=1-\pi\). If
\(c=\sum_{i=0}^{e_a-1}c_i\pi^i\), the nonzero summands have valuations
\(e_a v_p(c_i)+i\). Distinct indices give distinct residues modulo \(e_a\),
so there is a unique minimum and no cancellation at that valuation. This
justifies the first exact extraction method.

For the second method, write \(F_a(\pi)=p+\sum_{i=1}^{e_a}F_i\pi^i=0\).
Reduction modulo \(\pi\) sends every coefficient to its constant term modulo
\(p\). Thus \(c\) is divisible by \(\pi\) in the integral local ring exactly
when \(p\mid c_0\). In that case put \(m=c_0/p\) and compute

\[
 c/\pi=\sum_{i=1}^{e_a-1}(c_i-mF_i)\pi^{i-1}
             -mF_{e_a}\pi^{e_a-1}.
\]

Repeating this integer operation until the constant residue is nonzero counts
\(v(c)\) exactly. Both methods use the same binomial basis conversion, but
different valuation extraction operations; neither uses the tail-sum formula
as its answer. The finite replay is supporting implementation evidence, not
the proof of the uniform formulas above.

## Sources and attribution

1. Ali Romman, [PR621](https://github.com/CrocSwap/integer-mult-bounds/pull/621),
   "Prove uniform prime-power cyclic inverse bounds (no kappa claim)."
   Merged head: `520774462b19b29af41554b74def31f9d01e997e` (not the merge
   commit). The [pinned proof](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/520774462b19b29af41554b74def31f9d01e997e/research/prime-power-cyclic-inverse/PROOF.md),
   section "Integral polynomial and unit roots," supplies the integral
   tail kernel and algebraic-nonunit conclusion; those are prior work,
   not claims originating here. Locally consulted:
   `research/prime-power-cyclic-inverse/PROOF.md` and `SOURCE.json`.
   The [primary PR metadata](https://api.github.com/repos/CrocSwap/integer-mult-bounds/pulls/621)
   confirms its author, merged status, and exact head.
2. OpenAI, exact-DFT preprint source, commit
   `adc7f1241b42e322a6451854ab7e4b4c146bf78a`,
   [pinned `local.tex`](https://raw.githubusercontent.com/openai/math/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/local.tex),
   labels `loc:newton` and `loc:fourier-factorization`. It defines
   \(H_j=\prod_{s=1}^j(1-u^s)\) and \(h_j=H_j^{-1}\).
   The identity \(H_{r-1}=r\), obtained by evaluating
   \((T^r-1)/(T-1)\) at \(T=1\), turns
    \(r\sum h_jz^j\) into the integral tail kernel above.
3. Hao Yan (@FanPUYen), [PR796](https://github.com/CrocSwap/integer-mult-bounds/pull/796),
   "Research audit: exact prime-power kernel root valuations (no new kappa)."
   Compared head: `22902155c7875139e43e4fdf15723142d6709bdd`. Its
   `research/prime-power-newton-audit/cyclotomic.py` extracts coefficient
   valuations by weighted uniformizer-basis minima. Its exact receipt agrees
   on every shared radix and primitive embedding. The repeated integral
   division method in this package is distinct corroborating evidence.

The valuation and convex-hull calculations are proved here; no external
classification of these roots is assumed. This is a written mathematical
proof, independent of any finite verification script.
