# The moment threshold and the six-stage grid

This note separates a theorem about the **abstract moment invoice** from an
installation of one particular paired multiplier. The latter retains the
all-size premises listed in the README.

## Definitions and the raw crossing

For the fixed 36-call binary word, let

\[
 T(s)=\sum_{\text{productive }i}r_i^s,\qquad
 P(s)=\sum_{\text{paid }j}r_j^s,\qquad t=1-c,
\]

with every occurrence counted, including repeated ranks. The source has
18,906 productive and 104,904 paid occurrences. Set

\[
 \alpha(c)=P(t)/T(t),\quad
 \gamma(c)=P(t+593/2048)/(12^{593/2048}T(t)),\quad
 \lambda(c)=15^{491/1024}T(t-491/1024)/T(t).
\]

The replay reconstructs these inventories from the source word. Its
outward-rational log/exp series prove that \(D(c)=T(1-c)-P(1-c)\) has
opposite signs at the endpoints of

\[
 0.003890115286594461129996942<c_*<
 0.003890115286594461129996943.
\]

On the containing interval `[0.0038900, 0.00389046]` it also certifies
`-385000 < D'(c) < -383000`; hence this is the unique crossing there.
At that crossing the directed enclosures place \(\gamma\) in
`(0.907225471, 0.907225473)` and \(\lambda\) in
`(0.900009331, 0.900009333)`. By continuity, in a sufficiently small
one-sided neighborhood below \(c_*\), \(0<\alpha,\gamma,\lambda<1\),
and \(1-\alpha(c)=\Theta(c_*-c)\). The last statement follows because
\(D(c)=T(1-c)(1-\alpha(c))\), \(T\) is positive and continuous, and
\(D'\) is bounded away from zero.

For \(\theta\in\{1/64,2\}\), call \(v\) sufficient when

\[
 \alpha(c)^v+\theta\gamma(c)^v+\lambda(c)^v<1.
\]

The second value retains the original, more conservative split-tail
coefficient. If a sufficient power gives surplus \(\epsilon>0\), an
integer floor \(L>2/\epsilon\) makes the usual `2/L` surcharge fit; a
power of two can be chosen. Conversely, at or above the raw crossing in
this interval, \(\alpha\ge1\), so this strict invoice cannot pass.
Thus the supremum of prices for this **specified abstract invoice** is
\(c_*\). This conclusion does not assert a physical construction for
arbitrary \(v,L\), or an upper bound for other invoices or words.

Let \(\delta=c_*-c\). The least sufficient integer power satisfies

\[
 v_{\min}(c)=\Theta(\log(1/\delta))\quad(\delta\downarrow0).
\]

For the lower bound, \(\lambda\) stays above some fixed \(a\in(0,1)\).
Any sufficient \(v\) obeys
\(a^v\le1-\alpha^v\le v(1-\alpha)\le C v\delta\); this excludes
\(v=o(\log(1/\delta))\), and yields a positive constant lower multiple
of \(\log(1/\delta)\). For the upper bound take
\(v=\lceil K\log(1/\delta)\rceil\), with \(K\) large enough that the
uniformly subunit \(\gamma^v\) and \(\lambda^v\) are each at most
\(\delta^2\). Since \(1-\alpha^v=\Omega(v\delta)\) for this choice,
these two tails fit for all sufficiently small \(\delta\). The
constant coefficient \(\theta\) changes constants, not the order.
The floors are chosen after the positive surplus and may grow with
\(c\); this is not a fixed-precision or fixed-resource convergence
claim. `SCALING.json` gives finite directed controls at seven distances
below the lower endpoint of the crossing bracket; it is evidence for the
endpoint calculations and finite examples, while the asymptotic assertion
follows from the argument above.

A sharper expansion follows because the split ratio exceeds the final
productive ratio at the crossing. Put \(\Delta=1-\alpha(c)\),
\(A=\log(1/\Delta)\), and \(a=-\log\gamma(c_*)\). If
\(x_\theta\) is the unique positive real zero of the surplus, then
\[
 a x_\theta=A-\log A+\log(a\theta)+o(1).
\]
Indeed, at the zero the dominant balance is
\(\Delta x_\theta=(1+o(1))\theta e^{-a x_\theta}\); taking logarithms
and substituting \(x_\theta\sim A/a\) gives the formula. The least
integer power is \(\lfloor x_\theta\rfloor+1\). The two continuous
threshold powers therefore differ by \(\log(128)/a\), about 49.83 continuous
factors in the limit; the difference of integer minima has rounding error
strictly less than one. [Expanded proof and finite examples](SCALING.md).

## Literal six-stage upper envelope

The #8035 stage rule pays a positive debit \(d\) at height \(H_i\),
then requires

\[
 b_i<\min\!\left(\eta,\frac{249(c-d/H_i)+b_{i-1}}{250}\right),
 \qquad b_0=0.
\]

The first five rates are rounded by the source to
`(floor(10^18 * limit) - 1) / 10^18`. The sixth is a separately
specified ordinary rate. Omitting the positive debits and the other cap
only increases an upper envelope. Iterating the source's exact first-five
rounding at \(c_*\), the five maximal ticks are

```
3874554825448082  3890053044749874  3890115037627081
3890115285598590  3890115286590476
```

and the final limiting ordinary rate lies in
`[0.003890115286594445189476954232,
  0.003890115286594445189476955228]`. Thus a signed \(\kappa\)
reported on the `10^-18` grid, necessarily below the ordinary rate, is
at most **0.003890115286594445** for this source, six-stage rule and raw
price family. This is an upper bound, not by itself a witness that the
last tick is attainable. The coarser continuous bound
\(c_*(1-250^{-6})\) is valid but slightly less sharp. If the trial is
restricted to the `2^-56` denominator used by #8035, even this coarser
bound limits the report to the 440 tick. None of these statements covers
other operator words, tariffs, stage counts, grids or caller rules.

## Fixed finite installation and model boundary

The included profile receipts evaluate concrete signed margins, both
supplier debits and all six exact rates; their checkers retain rejection
controls for a trial above the crossing, a paid rank-one addition,
vanishing or insufficient stopping margin, and equality at each paid
supplier border. For the last tick, the fixed stop denominator is
\(D=10^{21}\), a 70-bit integer with 29 one-bits. The capped
repeated-square comparison uses at most 69 squarings and 29 multiply/compare
steps, with operands bounded by \(h+1\); a sequential schoolbook
lowering costs \(O(98(1+\log h)^3)\) transitions and
\(O(1+\log h)\) work cells per test before inherited outer accounting.

At the maximum binary log-rank \(H=1{,}024\cdot10^{21}\),
\((5/4)^{13}>2^4\) gives
\(G+1\le\lceil13H/(4\cdot430)\rceil+2\le
7{,}739{,}534{,}883{,}720{,}930{,}232{,}561\). The former
instance-specific \(G<2^{50}\) is false here: the attained rank-15
productive path and rank-12 paid block give
\(G>\lfloor(H-2-8\cdot430)/430\rfloor=
2{,}381{,}395{,}348{,}837{,}209{,}302{,}317\), greater than this host's
`sys.maxsize`. The checked source-slot logarithm is at most 26,038; the dynamic local allowance is 53,044 and
its next-power-of-two allowance is 65,536. The stage quotient guard uses
the actual \(\eta=39/10000\):
\(Q(H)=\lceil10000(2H+64)/9961\rceil<3H<8H\), at every stage.
These checks bound the stated finite profile; they do not prove the
inherited compiler transfer for arbitrary powers. The reference Python
also constructs eager tuples for powered source paths; at least
\(444^{430}>2^{3440}\) retained target paths exist. A finite-tape
lowering must enumerate and charge these paths rather than materialize a
Python tuple. [Fixed-rank lowering and limits](BRIDGE.md).

The source uses finite but astronomical rank and precision constants. Its stated asymptotic implication is **conditional
in the ideal finite-tape model**, retaining #8035's all-column native
action, owned erasure/restoration, compiler transfer, precision/tape
services and analytic recovery. Feasible host tests exercise selected
finite interfaces only; they do not execute the astronomical production
tapes or independently prove those five all-size premises.

Increasing \(v\) indefinitely is a separate physical problem: the fixed
positive height in these finite examples cannot support unbounded native
volume under the retained stripe inequality. The abstract supremum and
logarithmic power theorem therefore do not establish that the full
multiplier approaches \(c_*\). No practical crossover or selected
frontier is claimed.
