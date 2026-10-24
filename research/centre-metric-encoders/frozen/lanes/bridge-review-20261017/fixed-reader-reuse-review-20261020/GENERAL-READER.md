# A reusable query for an arbitrary old reader

This theorem extends the fixed-reader factorization from the
bridge-access lane. It uses ordered operators. It does not assume
that spatial maps commute.

Let X and Z be modules over the coefficient ring. Let J insert a centre
module into X, and let P select it, so \(PJ=I\). Suppose the current
reader and response satisfy

\[
L_tJ=I,\qquad E_t=I+A_tL_t.
\]

Put \(B_t=L_t-P\) and \(C_t=I+JB_t\). Since \(B_tJ=0\), the code is a
unit with \(C_t^{-1}=I-JB_t\). Let \(L_s:X\to Z\) be any old reader.
Define

\[
W=L_sJ,\qquad B_s=L_s-WP,\qquad M=L_sE_tJ.
\]

Then \(B_sJ=0\), and

\[
\boxed{L_sE_tC_t^{-1}=B_s-WB_t+MP.}
\]

To prove the identity, keep the order of all factors:

\[
\begin{aligned}
E_tC_t^{-1}
  &=(I+A_tL_t)(I-JB_t)\\
  &=I-JB_t+A_t(L_t-B_t)\\
  &=I-JB_t+A_tP.
\end{aligned}
\]

Multiplication by \(L_s\), followed by
\(L_s=B_s+WP\) and \(M=W+L_sA_t\), gives the stated identity.

The following six-step query therefore works for arbitrary independent
X and Z inputs:

1. Add \(B_sX\) to Z.
2. Add \(WPX\) to Z.
3. Apply \(C_t\) to X.
4. Subtract the new \(WPX\) from Z.
5. Add \(MPX\) to Z.
6. Apply \(C_t^{-1}\) to X.

The resulting map is

\[
(X,Z)\longmapsto(X,Z+L_sE_tX).
\]

In particular, steps 2 and 4 contribute \(-WB_tX_{\rm initial}\),
and step 5 contributes \(ML_tX_{\rm initial}\). Each X field is
restored. Z keeps its arbitrary baseline. An inverse of E is never
used. Neither invertibility of E nor a zero selected block of E is
required.

The map W is a service obligation. It must act additively on Z, and its
access and implementation must be priced. An in-place application of W
to an existing centre value does not by itself give this additive
service. No inverse of W is required by the theorem.

The theorem is a query identity. It does not by itself make \(L_s\)
a unit encoding of a complete target bank. Such an encoding requires
a unit completion of \(L_s\). If the centre width and the ordinary
coordinates R stay the same, this completion is
\(\left[\begin{smallmatrix}W&B_s\\0&I\end{smallmatrix}\right]\).
It is a unit exactly when W is a unit on the centre space. A completion
with different ordinary coordinates changes the interface and needs
its own implementation. The query identity itself also permits singular W.
In the actual normalized case
\(L_sJ=I\), W is I and \(C_s=I+J(L_s-P)\) gives that completion. The
two W services are then plain same-port copies. Only this case has
the actual 11,168-scalar and 2,064-map invoice in `REVIEW.md`.

The independent checker includes a finite example with two-dimensional
blocks

\[
T=\begin{bmatrix}0&1\\1&0\end{bmatrix},\quad
W=\begin{bmatrix}1&1\\0&1\end{bmatrix},\quad
S=\begin{bmatrix}2&1\\-1&0\end{bmatrix},\quad
A=\begin{bmatrix}-1&0\\0&1\end{bmatrix}.
\]

Take \(L_t=[I,T]\), \(L_s=[W,S]\), and

\[
E_t=\begin{bmatrix}I+A&AT\\0&I\end{bmatrix}.
\]

Here E is singular, its selected block is nonzero, and \(WT\ne TW\).
The six-step query passes all six independent input columns. The word
with plain copies in place of W fails. This example tests the removed
hypotheses. The ordered proof above applies to all modules and maps
with the stated types.

This theorem does not emit a new native response family. It does not
provide a new complete supplier or a change to the selected frontier.
The actual native frame and access conditions remain those in the
separate D25 review.

No publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
