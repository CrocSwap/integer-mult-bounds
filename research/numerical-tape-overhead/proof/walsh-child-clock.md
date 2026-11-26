# A numerical allowance for all spatial Walsh children

Let \(a\) be an even active Walsh width and set
\[
 x=\lceil\log_2(a+2)\rceil,\quad v_x=\lceil\log_2(x+2)\rceil,
 \quad y=\lceil(x^2v_x)^{1/3}\rceil,\quad m=2^y-1,
 \quad \Phi(x)=(x^2\log_2(x+2))^{1/3}.
\]
Use the [nonstationary rational template](foundations/nonstationary-rational-walsh.md) with its two one-eighth conversion phases and actual shared endpoint order. For \(x\ge 2^{24}\), its spatial children together consume at most one quarter of the potential
\[
      P(V,a)=V\sqrt a\,2^{48\Phi(x)} .
\]
Here \(V\) is numerical bit volume at a fixed record width. The statement includes every issued spatial call with multiplicity and leaves the local work to its own bill. The inequality still holds on increasing 48.

## Finite invoice and legal sizes

Set \(v=\lceil\log_2(y+2)\rceil\), \(L_F=2\lceil\sqrt{y/v}\rceil\), \(Q=2+\lceil 2y/L_F\rceil\), \(q=2^Q\), \(D_F=1+L_Fq\), and \(A=2(m+D_F-1)\). The optional upper-dimension padding in NW §2 gives this exact arity. Write \(R=10(1+L_Fq)(1+Q)^{L_F}\) for the published local upper invoice for one rational predictor pencil, and \(d=2\lceil2\sqrt m\rceil+1\) for the Newton degree. Then
\[
      y\ge65536,\quad y\le x/32,\quad D_F\le m,\quad q^{L_F}\le m^3,
      \qquad 2m\le A\le4m.
\]

Indeed, \(x^2\ge2^{48}\), and \(v_x\le x/2^{18}\) by the [explicit global guard](walsh-aligned-denominators.md#width-at-the-integer-caller), giving \(y\le x/64+1\). At \(y\ge65536\), \(v\le y/256\), \(L_F\le4\sqrt{y/v}\), \(Q\le3+\sqrt{yv}\), \(\log_2 L_F\le v\) and \(\log_2(1+Q)\le v\). These follow by rounding and \(4+\sqrt{yv}\le y+2\). Consequently
\[
     \log_2 R\le 8+v+5\sqrt{yv}<y-1<\log_2 m.
\]
In particular \(D_F\le m\). Also \(L_F Q\le2y+3L_F\le 3(y-1)\) because \(L_F\le4\sqrt y\), \(y\ge65536\). This proves the label-volume guard. For \(a\ge 2^{x-1}-1\) and \(A\le4\cdot2^y\), the largest even \(f\le a/A\) is positive.

Write \(h=\lceil(\log_2m)/4\rceil=\lceil y/4\rceil\), and \(W_a=(m+1)q^{L_F}8^h\) for the true local batch divisor. The two predictor evaluations cost at most \(2dR\) spatial calls per unit incoming row volume. Each of the two finite subcalls uses one eighth the active rows, and the direct terminal transform costs \(A\) calls per unit remaining row volume. Thus the actual spatial mass, once the exact leading divisibility below is supplied, obeys
\[
 \frac{\sum V_i}{V}=\frac{\sigma}{W_a}
 \le 2dR\sum_{r=0}^{h-1}4^{-r}+A4^{-h}.
\]
This is the spatial invoice in [division repair, §5](foundations/pairwise-newton-division.md) with the [explicit pencil bound](foundations/growing-arity-circuit-candidate.md). Every spatial call has width \(f\), and the order of ordinary work preserves endpoint sharing. Using \(f/a\le1/A\), \(d\le7\sqrt m\), \(A\ge2m\), \(A\le4m\), and \(4^{-h}\le m^{-1/2}\), gives
\[
   \frac{\sum V_i}{V}\sqrt{f/a}
       \le \frac{56}{3\sqrt2} R+2 \le 16R
       \le 2^{10\sqrt{y\log_2(y+2)}} .
\]
For the last inequality, \(12+v\le2\sqrt{yv}\) and \(v\le2\log_2(y+2)\), so \(4+\log_2 R\le7\sqrt{yv}\le10\sqrt{y\log_2(y+2)}\).

The true batch product over any positive width chain satisfies \(\prod_i W_{a_i}\le a_0^4\). Indeed,
\[
 \log_2 W_a=y+L_FQ+3h\le(15/4)y+3L_F+3\le4y,
\]
where \(3L_F+3\le y/4\) for \(y\ge65536\). Since \(A\ge2m\ge2^y\) and \(A_i f_i\le a_i\), multiplying over the width chain proves the claim. If the root has \(2^{k-s}\) complete spectator rows with \(k-s\ge4\lceil\log_2(\max(1,a_0))\rceil\), every batch divisor and their product divide that count, since they are powers of two. Install the direct fallback at \(x<2^{24}\). The stated product estimate covers every other width. This gives a concrete no-padding test for the whole nested Walsh call.

## Loss of potential under rounding

For \(x'=\lceil\log_2(f+2)\rceil\), one has \(f\le a/(2m)\le2^{x-y}\). Thus \(x'\le x-y+1\le x-y/2\). Set \(\lambda=\log_2(x+2)\). On \([x-y/2,x]\) we have \(u\ge x/2\) and \(\log_2(u+2)\ge\lambda/2\). The derivative of \(\Phi\) is at least \((2/3)u^{-1/3}\log_2(u+2)^{1/3}\). Integration gives
\[
 \begin{split}
  \Phi(x)-\Phi(x')&\ge \frac{y}{3\,2^{1/3}} x^{-1/3}\lambda^{1/3}\\
   &\ge \tfrac14\sqrt{y\log_2(y+2)} .
 \end{split}
\]
Indeed \(y\ge x^{2/3}\lambda^{1/3}\), \(y\le x\), and \(3\sqrt[3]2<4\). The normalized spatial mass and this decrement leave at most \(2^{-2\sqrt{y\log_2(y+2)}}\le1/4\) of the parent allowance at coefficient 48. This proves the claim at every width in the displayed range.

## Cubic comparison without differentiating the clock

The [numerical potential proof](../S008/WalshClock.lean) checks the actual base-two definitions of \(\Phi\) and \(\psi(y)=\sqrt{y\log_2(y+2)}\). Let \(q=y/(2x)\). The identity
\[
 (1-2q/3)^3-(1-q)^2=q^2(9-8q)/27\ge0
\]
and monotonicity of the logarithm give \(\Phi(x')\le(1-y/(3x))\Phi(x)\) whenever \(0\le x'\le x-y/2\) and \(0\le y\le x\). Since \(y\ge\Phi(x)\) in the adaptive schedule,
\[
 (y\Phi(x)/x)^2\ge y\log_2(x+2)\ge y\log_2(y+2).
\]
Consequently the actual potential decrease is at least \(\psi(y)/3\). For \(\psi(y)\ge1\), the normalized spatial mass \(2^{10\psi(y)}\) consumes at most one quarter of the parent's allowance already at coefficient 36. The theorem above uses 48, which also permits its smaller absolute constant on the direct range. The formal module also derives the finite mass recurrence from two one-eighth jobs with terminal cost \(A\). It multiplies that complete invoice by the actual \(\sqrt{f/a}\), obtains the bound \(16R\) from the displayed degree, depth and width guards, and composes it with the cubic decrease. The theorem `finite_to_quarter` verifies the resulting quarter allowance for all finite depths and valid real parameters. The pencil profile and the rounding of the published Fourier parameters meet its hypotheses by the arithmetic above.

The numerical child coefficient, common spectator guard and the [scalar application](walsh-aligned-denominators.md) apply to the stated actual suppliers. The [complete Walsh layer](walsh-node.md) attaches its nonrecursive selector, direct base and guarded moves at true word widths. The [integer clock](../CONSTRUCTION.md) accounts for the remaining outer operations.
