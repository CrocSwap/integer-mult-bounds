# Certified rational unitary FFT and rounded Toeplitz shear

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

I instantiate Chafik Boukhalfa/PR628's rational unit-phase construction
inside Vlado Vojdanovski/PR1673's retained FFT and Toeplitz-shear schedule.
PR3709 already supplies certified inward dyadic twiddles and rounded FFT
execution. I retain those credits. The result here concerns the unitary
child, its composed approximation and its fixed-grid dirty-data contract.

## 1. Contract and precision allocation

Let \(n=2^d\ge1\), and let \(T\in\mathbb Q(i)^{n\times n}\) be Toeplitz,
with first column \(c\) and first row \(r\). Define
\[
g_0=h_0=c_0/2,\quad
g_j=(c_j+r_{n-j})/2,\quad h_j=(c_j-r_{n-j})/2\quad(1\le j<n).
\]
Write
\[
M_g=\sum_j(|\Re g_j|+|\Im g_j|),\quad
M_h=\sum_j(|\Re h_j|+|\Im h_j|),\quad M=M_g+M_h.
\]
These rational quantities bound the corresponding complex \(\ell^1\) norms.
The desired map on disjoint dirty banks is
\[
S(T)(x,y)=(x,y+Tx).
\]
I assume \(z_0=(x,y)\in2^{-F_0}\mathbb Z[i]^{2n}\),
\(F_0\in\mathbb Z_{\ge0}\), and a supplied rational bound
\(R\ge\max(1,\|z_0\|_2)\), with target \(2^{-t}\), integer \(t\ge1\).
Take \(L=4d+8\) and choose
\[
\begin{aligned}
P&=t+\left\lceil\log_2(16(d+1)(M+1)(R+1))\right\rceil,\\
S&=t+\left\lceil\log_2(8(R+1))\right\rceil,\\
F&=\max\left(F_0,\ t+\left\lceil\log_2(2Ln(M+2))\right\rceil\right).
\end{aligned}
\]
Here \(P\) controls unit phases, \(S\) controls stored spectral multipliers,
and \(F\) controls data rounding. Put
\[
\nu=2^{-P},\quad v=2^{-S},\quad u=2^{-F},\qquad
\delta=4(d+1)M\nu+2v,\qquad H=1+M+2v.
\]

I construct a circuit on the existing \(2n\) logical wires, with at most
\(L\) layers and \((4d+10)n\) one- or two-wire gates. Every unitary
coefficient gate has rational entries and an exact stored adjoint inverse.
I round each active data output component once, after exact evaluation
of its constant-size gate, to the nearest \(F\)-grid value, with ties
toward positive infinity.

The resulting output \(\widehat z\) satisfies
\[
\boxed{\|\widehat z-S(T)z_0\|_2
\le\delta R+LHnu<2^{-t}.}
\]
The source-bank restoration error is at most \(LHnu\). Only the unrounded
rational circuit restores the source exactly. The input matrix \(T\)
and its circulants need not be invertible.

## 2. Certified rational unit phases

I retain the source oracle in `interval_kernel.py` and the stereographic
recipe in `PR628-PROOF.md:212–225` and `check.py:110–128`.
For each requested \(e^{2\pi ik/n}\), reduce the integer description
modulo \(n\) and cancel its gcd. Handle \(1,-1,i,-i\) exactly; the other
requests satisfy the oracle's primitive-root domain.

For phase precision \(P\), create a fresh authenticated oracle namespace
with
\[
B=2(P+32),\qquad \mathrm{SCALE}=2^B.
\]
Set both values before calling the oracle. The cached \(\pi\) and kernel
functions start empty and remain at that one precision.

The source uses Machin's identity and alternating arctangent series.
Writing \(u_B=2^{-B}\), each arctangent endpoint has error below \(2u_B\).
Charging the subsequent hull operations gives angle endpoint error below
\(50u_B\), with absolute angle endpoints below four.

For completeness, the source's Taylor stopping test terminates by
\(N_*=16(B+16)\). With \(j=N_*+1\), the estimate
\(j!\ge(j/3)^j\) gives
\[
128\,4^j/j!\le128(12/j)^j<2^{-B-16}.
\]
The Machin loops likewise take \(O(B)\) terms.

Multiplication by \(i\theta\) keeps one component of each Taylor term
exactly zero. Addition or subtraction with that zero does not add hull
error to an already grid-aligned endpoint. The nonzero recurrence has
one multiplication hull and one division hull. If \(e_\theta\le50u_B\),
the endpoint error \(e_j\) obeys
\[
e_j\le(4/j)e_{j-1}
 +(4^{j-1}/j!)e_\theta+2u_B.
\]
Summing its solution and using \(e^4<128\) gives
\(\sum_{j\le N}e_j<(6400+256N)u_B\). Final remainder widening and its
hull add less than \(2u_B\). Thus each final coordinate endpoint differs
from the true phase coordinate by at most
\[
E_B=2^{16}(N+1)2^{-B}
\le2^{21}(B+17)2^{-B}\le2^{-P-36}.
\]
The last inequality uses \(B+17=2P+81\le2^{P+7}\).

Choose \(C\in\{1,-1,i,-i\}\) so the rotated box has real lower endpoint
at least \(1/2\). A chart exists because one true coordinate has magnitude
at least \(1/\sqrt2>2/3\), while the endpoint error is below \(1/6\).
For the true rotated phase \(v_0\), put
\[
\tau=\Im(v_0)/(1+\Re(v_0)).
\]
The denominator is at least \(3/2\). Compute quotient extrema at the box
corners, round their midpoint to the nearest \((P+4)\)-grid value \(t_0\),
and form
\[
\sigma=C\frac{1-t_0^2+2it_0}{1+t_0^2}.
\]
Then \(|\sigma|=1\) exactly, \(|t_0|<1\), and
\[
|\sigma-e^{2\pi ik/n}|\le4E_B+2^{-P-4}.
\]
This follows from the quotient bound \(2E_B\) and the stereographic
derivative bound \(2/(1+t^2)\le2\).

The executable checks the **maximum endpoint** component-\(\ell^1\)
distance from \(\sigma\) to the entire oracle box. That distance is at
most \(10E_B+2^{-P-3}<\nu\). A minimum distance to the box would not
certify the approximation.

The parameter denominator is at most \(2^{P+4}\). Unit-phase components
therefore have numerator/denominator height at most \(2P+9\), with
slightly larger allowances in the code. The oracle's offline exact
Machin sums, factorials and phase-description arithmetic use polynomial
time and space in \(P\) and the input description length. A long external
phase numerator is an input cost, not a free oracle argument.

## 3. Exactly unitary butterflies and FFT approximation

Use the certified phase \(a+ib\) approximating \(e^{i\pi/4}\), and a
certified twiddle \(w\). Define
\[
B(a,b,w)=
\begin{pmatrix}a&bw\\b&-aw\end{pmatrix}
=
\begin{pmatrix}a&b\\b&-a\end{pmatrix}\operatorname{diag}(1,w).
\]
Since \(a^2+b^2=|w|^2=1\), this matrix is exactly unitary.
Its adjoint is
\(\operatorname{diag}(1,\bar w)\left[\begin{smallmatrix}a&b\\b&-a\end{smallmatrix}\right]\).
It is generally not the same expression with \(w\) merely conjugated.

The splitter difference from the ideal \(1/\sqrt2\) splitter has norm
\(|(a+ib)-e^{i\pi/4}|\). Hence each butterfly differs from its ideal gate
by at most \(2\nu\). Disjoint gates give the same layer bound. I retain
the source's exact bit reversal and its \(d\) butterfly layers, so
\[
\boxed{\|\widetilde F-F\|_2\le2d\nu,\qquad
F=\mathrm{DFT}_{-}/\sqrt n.}
\]
We telescope products of unitary layers, so no amplification factor
appears. Every exact FFT prefix and suffix is unitary. Reverse the layers
and adjoint the stored gates to obtain \(\widetilde F^*\); do not generate
a new approximate inverse phase table.

## 4. Spectral preparation and Toeplitz approximation

For a kernel \(k\), the ideal circulant eigenvalues are the
**unnormalized** DFT
\[
\lambda_\ell=\sum_j k_j e^{-2\pi i\ell j/n}.
\]
I approximate each root independently by a certified rational unit,
sum exactly offline, and round each multiplier component once to the
nearest \(S\)-grid value. If \(\|k\|_1\le M_k\), then
\[
\|\widehat\lambda-\lambda\|_\infty\le M_k\nu+v,\qquad
\|\widehat\lambda\|_\infty\le M_k+v.
\]
The second bound uses exact unit modulus before rounding. It does not
add a spurious phase-error magnitude factor.

I store the rounded multipliers before online use. The exact offline
sum can have a denominator whose size grows with \(n\); carrying that
sum into data gates would violate the stated coefficient-width bound.

The actual circulant child applies
\[
\widetilde C_k=\widetilde F^*\operatorname{diag}(\widehat\lambda)\widetilde F,
\]
so
\[
\|\widetilde C_k-C_k\|_2
\le M_k\nu+v+2M_k\|\widetilde F-F\|_2.
\]
Exact unitarity alone does not make \(\widetilde F\) an exact diagonalizer.

For \(D=\operatorname{diag}(e^{\pi ij/n})\), the source decomposition is
\[
T=C_g+D^*C_{Dh}D.
\]
I generate each diagonal entry of \(\widetilde D\) independently. Thus
\(\|\widetilde D-D\|_2\le\nu\), without a powers' accumulated error or
an \(nP\)-bit phase representation. The actual schedule is the first
circulant shear, the common twist \(\widetilde D\) on both banks, the
circulant shear prepared from \(\widetilde D h\), and the inverse twist.

Twisting preserves \(\|h\|_1\). Charge \(M_h\nu\) for changing the
second kernel and \(2M_h\nu\) for its two exterior twists. Combining
these terms with the two circulant estimates gives
\[
\|\widetilde T-T\|_2
\le(4d+1)M_g\nu+(4d+4)M_h\nu+2v
\le\boxed{\delta}.
\]
In exact rational arithmetic the complete map is
\((x,y)\mapsto(x,y+\widetilde T x)\). The input matrix may be zero
or singular because the pointwise shear gates remain invertible.

## 5. Prefix bounds and rounded execution

Every non-spectral gate stays within one bank and is unitary.
Each of the two spectral layers has orientation
\[
S(A)=\begin{pmatrix}I&0\\A&I\end{pmatrix}.
\]
For a bank unitary \(U=\operatorname{diag}(U_x,U_y)\),
\[
US(A)U^*=S(U_yAU_x^*).
\]
Move the bank unitaries to the ends of any contiguous gate segment.
The remaining shear matrix is a sum of at most two unitarily transformed
spectral matrices. Their norms are at most \(M_g+v\) and \(M_h+v\).
Consequently every segment, inverse segment, prefix and suffix has norm
at most
\[
\boxed{H=1+M_g+M_h+2v.}
\]
Masked partial spectral layers satisfy the same estimate.
I do not multiply a shear bound once per stage.

Nearest component rounding has error at most \(u/2\); a complex output
has error at most \(u/\sqrt2\). A disjoint layer updates at most \(2n\)
complex wires, so its error vector has norm at most \(\sqrt n\,u\).
The source schedule has at most \(L=4d+8\) layers, including empty
bit-reversal layers. Transporting each local residual through its
remaining exact suffix gives
\[
\|\widehat z-\widetilde S z_0\|_2
\le LH\sqrt n\,u\le LHnu.
\]
Every pre-round and rounded state has amplitude at most
\[
A=H(R+Lnu).
\]
The source-bank error receives no coefficient-approximation term,
because the unrounded rational circuit restores that bank exactly.
Fixed-grid execution can still have nonzero source-restoration error;
the verifier includes a small-grid witness.

The precision choices in Section 1 close the requested budget:
\[
4(d+1)M\nu R<2^{-t}/4,\quad 2vR<2^{-t}/4,\quad
LHnu<2^{-t}/2.
\]
Here \(v\le1/32\) and \(H<M+2\). Increasing \(F\) to preserve \(F_0\)
only reduces the arithmetic error. Also \(Lnu\le1/8\), hence
\(A\le H(R+1)\).

## 6. Representations and costs

A unit phase uses \(O(P)\) bits. Products of a splitter and a twiddle
fit \(4P+20\) component bits. Stored spectral components fit
\(S+\lceil\log_2(M+2)\rceil+2\) bits. The implementation uses
\[
C_{\rm bits}=\max(4P+24,\ S+\lceil\log_2(M+2)\rceil+2).
\]
Let \(I=\max(1,\lceil\log_2\max(1,A)\rceil)+2\).
A signed fixed-grid component stores the integer \(2^Fq\) in at most
\(F+I\) bits. Measuring only the numerator of its reduced Fraction
would omit the fixed-grid offset for integer values; the verifier
measures the canonical grid integer and reserves its sign.

A two-wire complex gate evaluates at most four real products per
output component before rounding. With coefficient denominators of
height at most \(C_{\rm bits}\) and data on the \(F\)-grid, their common
denominator has at most \(F+4C_{\rm bits}\) bits. Cross-products,
summation and grid rounding fit the conservative temporary allowance
\[
W_{\rm temp}=2F+8C_{\rm bits}+2I+32.
\]
Thus online operands have
\[
O(F+P+S+\log(1+M)+\log(1+R))
\]
bits. In particular, the caller obtains \(O(p)\)-bit operands when
target precision, incoming fractional precision and logarithmic input
magnitude are \(O(p)\), and \(n,M\) have polynomial size in \(p\).
The incoming precision is an explicit term, not an uncharged assumption.

There are \(O(n\log n)\) logical gates, each requiring a constant number
of bounded-size additions, multiplications and divisions for final
rounding. This identifies the operands for the retained scalar arithmetic
primitives; it is not a measured fixed-tape tariff. Direct spectral
preparation uses \(O(n^2)\) root/coefficient terms and polynomial offline
work in \(n\), precision and the input coefficient/phase description
lengths. Dense checker matrices and their large exact denominators are
verification oracles, not the online representation.

## 7. Source binding and finite evidence

I authenticate the frozen inputs before executing the interval oracle or
parsing the circuit. The adapter retains `diag`, `inverse`, `parallel`,
`fft`, `circ_shear` and `toeplitz_shear`. It changes four coefficient
sites: FFT twiddles, the unitary splitter expression, the unused common
twist generator, and the independent twist vector. Exact array constructors,
charged spectral preparation and rational gate inversion replace the
corresponding NumPy operations. I preserve source assertions under
optimized verifier execution and record the original/adapted AST hashes.

I execute the actual adapted gates, not macro matrix callbacks.
The verifier checks local unitarity and bank ownership, exact FFT
round trips, a direct DFT formula with an independently enclosed
\(1/\sqrt n\), and exact rational Toeplitz references. The direct DFT
formula shares the certified phase oracle; I do not call it an independent
transcendental implementation.
The finite squared-Frobenius checks use \(n\delta^2\) and
\(n(2d\nu)^2\). They check consequences of the written operator-norm
proof; those inequalities alone would only give the looser
\(\sqrt n\)-scaled operator bounds.

The rounded fixtures include arbitrary dirty banks, large incoming
magnitudes, cancellation, an 80-bit incoming grid, zero/singular matrices
and small-grid restoration loss. I report observed completed-component
heights and canonical record widths. I do not instrument every internal
`Fraction` temporary; the general temporary bound relies on Section 6.

Controls alter inverse order, bit reversal, multiplier normalization,
the inverse twist and exact unitarity, and reject insufficient phase/data
precision, a discarded incoming grid, stale lower-precision coefficients,
floating input and changed sources. Passing these checks does not establish
physical tape execution, the full parity recursion, the complete Gaussian
error ledger or the multiplication theorem.
