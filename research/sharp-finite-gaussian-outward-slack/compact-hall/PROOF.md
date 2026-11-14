# Compact two-exclusion Hall proof

## Statement

Write \(H=H_4\) for the Sylvester Hadamard matrix in the parent `PROOF.md`,
\(U=H/2\), and \(\beta=\sqrt{21}-\sqrt{19}\). An edge of the strict graph
joins \(x\in S_5\) to an integer vector \(y\) when

\[
\|y-Ux\|_2\le1,
\qquad
\|y\|_2-\|x\|_2<\beta.
\]

For \(x\) with no zero coordinates, let \(\epsilon(x)=\prod_i
\operatorname{sgn}(x_i)\). Define the full signed-coordinate orbits

\[
\begin{aligned}
O_{0033}&=\{x:\operatorname{sort}(|x_i|)=(0,0,3,3)\},\\
O_{0133}&=\{x:\operatorname{sort}(|x_i|)=(0,1,3,3)\},\\
O_{2223}^{+}&=\{x:\operatorname{sort}(|x_i|)=(2,2,2,3),\ \epsilon(x)=+1\}.
\end{aligned}
\]

Then

\[
T_1=\{x:\|x\|_2^2\le19\}\setminus(O_{0033}\cup O_{0133})
\quad\cup\quad O_{2223}^{+}
\]

has 1,809 inputs. Put

\[
N_1=\{y:\|y\|_2^2\le19\}\setminus(O_{0033}\cup O_{0133}),
\]

which has 1,777 points. The exact lower-bound check proves

\[
N_\beta(T_1)\subseteq N_1,
\]

so \(|T_1|-|N_\beta(T_1)|\ge32\). The full quotient-flow replay
`orbit_cut.py` additionally checks equality and finds the maximum invariant
deficiency 32. This proof does not use the 1,692-point candidate Hall list.

## Signed-permutation action and orbit membership

The paired signed-permutation graph action is

\[
(x,y)\longmapsto(Ax,By),\qquad A,B\in W_4,
\]

and preserves error and both norms when \(BH=HA\). The full quotient replay
checks all 384 signed permutations \(A\); the compatible pairs number 192,
and both projections are exactly

\[
W(D_4)=\{\text{signed permutations with an even number of sign changes}\}.
\]

The compact checker independently verifies that every \(A\in W(D_4)\) has
an output action \(B=HAH^T/4\in W(D_4)\), with \(BH=HA\), and that the
output actions cover \(W(D_4)\).

For a sorted absolute-coordinate pattern with multiplicities \(m_r\), let
\(m_0\) count zero coordinates. If some coordinate is zero, its sign can
absorb the parity of sign changes, so the pattern gives one orbit. If no
coordinate is zero, the two product-sign classes are separate orbits. Their
point counts are

\[
\frac{4!}{\prod_r m_r!}\,2^{4-m_0}
\quad(m_0>0),
\qquad
\frac{4!}{\prod_{r>0}m_r!}\,2^3
\quad(m_0=0,\text{ for each fixed product sign}).
\]

This gives \(|O_{0033}|=24\), \(|O_{0133}|=96\), and
\(|O_{2223}^{+}|=32\). The script generates all 38 required input orbit
representatives from sorted nonnegative patterns with squared norm at most
19, deleting the two excluded patterns, using one representative when a zero
is present and one per product sign otherwise, then adding the special
\((2,2,2,3,+)\) orbit. It does not read an input-list certificate.

## Counts

The count \(|B_{19}|=1,897\) is the sum of coefficients through degree 19
in

\[
(1+2z+2z^4+2z^9+2z^{16})^4.
\]

For one coordinate, these terms count zero and the choices \(\pm1\) through
\(\pm4\); larger absolute coordinates cannot occur in \(B_{19}\). The
checker computes these coefficients by exact integer convolution and also
checks the orbit-size sum. Removing the two
excluded orbits gives \(|N_1|=1,897-24-96=1,777\). Adding the special
positive-product orbit, whose squared norm is 21, gives
\(|T_1|=1,777+32=1,809\). All of \(T_1\) lies in \(S_5\).

## Complete representative neighbor check

Each Hadamard image coordinate has parity \(\sum_i x_i\pmod2\), since every
entry of \(H\) is odd.

- If \(\sum_i x_i\) is even, \(Ux\in\mathbb Z^4\). The only integer
  displacements of Euclidean norm at most one are zero and the eight signed
  coordinate unit vectors: exactly nine candidates.
- If \(\sum_i x_i\) is odd, all four coordinates of \(Ux\) are
  half-integers. Every integer point within Euclidean distance one must
  choose one of the two nearest integers in each coordinate; all 16 such
  choices have squared error exactly one.

The checker enumerates the complete 9 or 16 candidates at each of the 38
orbit representatives. It computes every strict-\(\beta\) comparison by
integer arithmetic, with no floating point, and verifies that each resulting
output satisfies the defining \(N_1\) predicate. Since the paired group
preserves the graph, applying \((A,B)\) transports each representative edge
to an edge from every point in that input orbit, and \(N_1\) is invariant
under the output action. Thus every strict neighbor of every input in
\(T_1\) lies in \(N_1\). This proves the Hall lower bound. It does not
assert that every input is adjacent to every output in the same pair of
orbits.

The compact checker verifies 20 integer-image and 18 half-integer-image
representatives, enumerating 254 strict representative edges in total. The
separate full orbit-flow check verifies the exact union \(N_\beta(T_1)=N_1\).

## Quotient min-cut cross-check

`orbit_cut.py` reconstructs the complete graph on all 3,121 inputs and all
5,697 error-one candidate outputs. It finds 55 input orbits, 87 output
orbits, 236 quotient adjacencies, and 23,137 strict edges. One strict edge
between two orbits implies every input in the source orbit has some strict
neighbor in the target output orbit, and every output in that orbit has a
neighbor from the input orbit: apply the same paired group element to the
edge. Orbit capacities therefore give exact neighborhoods.

The integer min-cut is 3,089, so the maximum invariant deficiency is
3,121-3,089=32. The minimal residual source side is the equivalent witness
\(T_0,N_0\) that separately excludes the negative-product \((2,2,2,2)\)
orbit of size eight from both sides. The maximal residual source side adds
that orbit to both and gives the shorter two-exclusion formula \(T_1,N_1\).
Both cuts and both complete neighborhoods are checked directly.

## Limits

This is a finite Hall obstruction at \(S_5\) and strict threshold \(\beta\).
It proves no global construction at \(\beta\), does not change the upper
injection verification, and makes no new \(\kappa\) or multiplication-frontier
claim. The complete matching and its original verifier remain in the parent
package. This compact lower checker is an addition to the same R5 contribution,
not a separate PR.
