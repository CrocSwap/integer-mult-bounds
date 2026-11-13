# One J8 host cannot supply the three required odd directions

Fix #7481 at its exact emitted word and the exact signed #7113 caller. Event 1423 is `J` stage 8 with Type B host roles 36 and 37 and coefficients \(\alpha=-1\) and \(\beta=1/2\). The old event 1339 is a Type B singleton `IDLE_ODD` on rail 68 with the stage-8 body. The literal role scan finds no other contact to rail 68. The three inputs are arbitrary and independent.

Use port 15, which is a Type B port. The checked native main roles are 17 and 129. The centre mask is 81 and the eight body masks are the axes 65 through 72. The mod-two Gram matrix of these nine masks is the identity. At width two, fix the same parked complement and take all sixteen body Walsh bits zero. Use central Walsh bits `00` and `11`. The body factor is one in both sectors, and the central eigenvalues are \(q=1\) and \(q=-1\), respectively. The retained signed child tensor gives the central phases \(1,i,i,-1\) at width two. The physical phase substitution for this pair gives the two-dimensional host matrix

\[
H(q)=\begin{pmatrix}1 & -q\\ q^{-1}/2 & 1/2\end{pmatrix}.
\]

The required old transformation on this pair and independent odd rail is \(H(q)\oplus[q]\). In particular, \(H(1)-H(-1)=\left(\begin{smallmatrix}0&-2\\1&0\end{smallmatrix}\right)\) has rank two and determinant two. The required direct sum difference is that matrix plus a separate diagonal entry 2. It has rank three and determinant four.

Allow arbitrary linear ingress \(A\), egress \(B\) and bypass \(E\), with the same induced matrices in the two sectors under the fixed coordinate identification. Allow the wrappers and scalar operations without price. Require all remaining access to the original three input and output coordinates to factor through these maps, with no other sector-dependent operation or other-fibre access. A candidate in this class has two sector matrices \(BH(q)A+E\). Their difference is \(B(H(1)-H(-1))A\), of rank at most two. This contradicts the required rank-three difference. The proof covers the specified coframed linear wrappers, including an unrestricted number of intermediate coordinates within those maps. It does not assign a sector property to arbitrary monomial address routes.

Removing all eight Type B copies of the selected singleton could give a paid histogram change of −8 at rank nine. The productive histogram remains fixed in this relaxation. The authenticated #7481 crossing bracket and the directed tariff bound the gross by \(8H_9(C)=8\cdot 9^{1-C}\), between 71 and 72 raw units before any additional charge. One port alone gives at most \(H_9(C)\). This is a ceiling for a hypothetical edit, and the one tested fixed-host correction is impossible even at that generous ceiling.
