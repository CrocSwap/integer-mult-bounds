# How adaptive interchange gives the shrinking excess

Jerry Chen's fork first derived the rate below in its S003 written construction, using the interchange and integer caller of OpenAI's tape paper and the rational Walsh identities of its Fourier paper. Here $T(n)$ is the worst-case number of tape transitions on a pair of $n$-bit inputs. Write $L=1+\log_2 n$, $x=\log_2 L$ and $\Phi(z)=(z^2\log_2(z+2))^{1/3}$. For the earlier construction there are absolute constants $A,C$ such that

$$
T(n)\le A n\sqrt L\,2^{C\Phi(x)},\qquad S(n)\le A n.
$$

The derivation proceeds from address movement to a selected Walsh transform and then to the full product. The constants below may increase between inequalities. Each is independent of input length and recursion depth. [Original extraction, AQ1–AQ9](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/lead/adaptive-extraction.md) · [Sources and independent composite-radix route](../SOURCES.md)

## 1. Cost of moving two address fields

At native field width $e$, choose the largest odd $m\le e^{1/R}$, with a single fixed $R$ large enough that the local compiler's polynomial degree $K$ satisfies $K/R\le1/8$. The compact label construction balances two costs. Writing $u=\log_2 m$, its logarithmic label cost is bounded by $3u/d+O(d^2\log_2(u+2))$. A dyadic degree $d$ of order $(u/\log_2(u+2))^{1/3}$ makes both terms $O(\Phi(u))$. Including the main calls, padding and full-volume reserve calls, the sum of child volumes per input bit is at most $\sqrt m\,2^{C\Phi(u)}$. [Label construction and call counts, AI3–AI7](foundations/adaptive-interchange.md)

Let $P(e)$ bound transitions per incoming bit, uniformly over the untouched address fields. All children have width $f\le e/m$ and $\log_2 f\le\rho\log_2 e$ for a fixed $\rho<1$ above the base case. Set $U(e)=P(e)/\sqrt e$. The factor $\sqrt{mf/e}\le1$ cancels the square-root part of the child cost, giving

$$
U(e)\le C e^{-3/8}+2^{C\Phi(\log_2 e)}U(f).
$$

On the executed width chain, $\Phi(\rho z)\le\rho^{2/3}\Phi(z)$. The sum of the logarithms of the recursive multipliers is therefore $O(\Phi(\log_2 e))$. The additive tolls also have bounded sum because the widths at least halve. Unrolling to the fixed direct base gives an exact swap on $V$ bits in $O(VJ(e))$ transitions, where $J(e)=\sqrt{1+e}\,2^{C\Phi(\log_2(e+2))}$. Contracted children park a geometric sum of payloads. A full-volume reserve takes ownership of the parent's banks. Reusing the marked intervals bounds distinct visited cells by $O(V)$ across the entire swap. [Time and space proof, AI8 onward](foundations/adaptive-interchange.md)

## 2. Cost of a selected Walsh transform

The earlier rational Walsh processor calls that exact swap when it moves data. For active width $a$, put $z=\lceil\log_2(a+2)\rceil$, $v=\lceil\log_2(z+2)\rceil$, $y=\lceil(z^2v)^{1/3}\rceil$ and $m=2^y-1$. This slower arity growth pays for the address work at each numerical node. Its next width $f$ is the largest even integer at most $a/A_m$, with $2m\le A_m\le4m$. Direct butterflies handle the remainder. [Integer schedule, NW8–NW12](foundations/nonstationary-rational-walsh.md)

After division by the square root of the active width, the recursive multiplier is at most $2^{C_B\sqrt{y\log_2(y+2)}}$. For $z_f=\lceil\log_2(f+2)\rceil$ we have $z-z_f\ge y/2$ above the fixed base. Integrating the derivative of $\Phi$ on the last $y/2$ units gives $\Phi(z)-\Phi(z_f)\ge c\sqrt{y\log_2(y+2)}$. Thus a single sufficiently large coefficient of $\Phi$ pays the recursive multiplier. The local toll includes the address work $m^K(1+J(a))(1+\log_2(k+2))$ per bit. Since $y=O(\Phi(z))$, the same induction absorbs its normalized cost after enlarging the coefficient once. For $N=2^k$ records of $O(k)$ bits, the complete selected transform and its adjoint each cost $O(NkJ(k))$, enlarging the constant in $J$ to absorb the fixed logarithmic factor. The proof also accounts for the two outside permutations, precision and reuse of $O(Nk)$ visited cells. [Recurrence, precision and storage, NW12–NW17](foundations/nonstationary-rational-walsh.md)

## 3. Passing from a transform to a product

The tape caller selects shapes with $k=\Theta(L)$ and $Nk=\Theta(n)$. Its short transforms use the selected Walsh processor. Its guarded permutations use exact swaps and restore borrowed coordinates. Three logarithmic factors pay for the controlled permutations and one pays for the outer layer count. Two forward transforms, a pointwise product and the adjoint recover the convolution. The caller fixes the accuracy exponents once, so $O(k)$-bit precision suffices to round each coefficient to its exact integer before carrying and writing the $2n$ product bits. The full time estimate, including polynomial setup of fixed degree $E$, is

$$
C Nk\sqrt k\,2^{C\Phi(\log_2(k+2))}(1+\log_2(k+2))^4 + C(1+k)^E.
$$

The ordinary full-width products also fit this budget. The later arithmetic audit counts $O(N(1+\log_2(k+2)))$ of them and uses $O(k^{\log_3 5})$ steps per product, with $\log_3 5<3/2$. [Original caller, AQ5–AQ7](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/lead/adaptive-extraction.md) · [Short-word arithmetic audit](foundations/review-axes-and-arithmetic.md)

Since $N=2^k$, the additive setup fits in $O(Nk)$. Also $\log_2(k+2)=x+O(1)$ and the four logarithmic factors add only $O(\log_2(x+2))$ to the log overhead. This gives $\log_2(T(n)/(n\sqrt L))\le O(\Phi(x))$. The caller reuses the same intervals between transforms, giving $O(Nk)=O(n)$ distinct visited cells. Its exact schoolbook fallback covers the finitely many small or rejected lengths. Finally, $L=2^x$, so dividing the log overhead by $x$ bounds the excess over exponent $1/2$ by $O((\log_2(x+2)/x)^{1/3})$.

## 4. Where the numerical bound enters

The earlier proof leaves $A,C,R$ and the base thresholds unspecified. The numerical construction fixes the native root degree at $R=240$, implements the selected Walsh layer with aligned modular arithmetic, and gives explicit bounds for the small-input branches. Its native cost contributes $(433/8)\Phi$ and the occupied Walsh column maps add $(33/4)\Phi$, for $(499/8)\Phi$ before the outer costs. The all-input calculation absorbs those costs and rounding to obtain $63\Phi(x)$ for every $n\ge2$. These numbers come from pricing the specified implementation. The physical controller and its correspondence to the Lean cost hypotheses remain written proof obligations. [Native induction](address-native-staircase.md) · [Walsh and outer costs](routing-refined-walsh.md) · [Three-branch calculation](../CONSTRUCTION.md#time-on-the-three-branches) · [Lean proof boundary](../REVIEW.md)
