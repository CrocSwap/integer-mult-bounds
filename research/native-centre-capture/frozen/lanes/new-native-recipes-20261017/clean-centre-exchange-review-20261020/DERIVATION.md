# A clean record from an arbitrary target baseline

This note gives an independent algebraic derivation. `REVIEW.md`
states the accepted native packet and its exact scope.

Let \(P,R\) partition the data ports. Suppose an admitted native prefix
reaches the exact cut
\[
 X=x,\qquad Y_P=y_P,\qquad Y_R=y_R+E_Rx
\]
in content coordinates. The physical fields \(X\) and \(Y_P\) must have
the same FULL frame. The ordinary \(Y_R\) fields can retain their
declared hole frames.

Let \(L=[I,B]\) in \(P,R\) order, and let
\[
 C=\begin{pmatrix}I&B\\0&I\end{pmatrix}.
\]
Apply \(C\) to the FULL X bank. Each selected pair now has values
\((a,b)=((Lx)_p,y_p)\). Apply the following three scalar ADDs:
\[
 b\leftarrow b+a,\qquad
 a\leftarrow a-b,\qquad
 b\leftarrow b+a.
\]
Their successive pair values are
\[
 (a,b+a),\qquad (-b,b+a),\qquad (-b,a),
\]
where the last two displays use the original \(a,b\).
Thus the final content is
\[
 X_P=-y_P,\quad X_R=x_R,\quad
 Y_P=Lx,\quad Y_R=y_R+E_Rx.
\]
Every selected target baseline is arbitrary. No clean input field is
used. The minus sign is part of the three-ADD rotation and needs no
extra scale.

Under the pinned old scalar tariff, a unit complex ADD costs eight
real scalar units. The rotation costs 24 per selected port. For the
sixteen-port code with cost 1760 and a retained core cost of 6456,
the scalar total is
\[
 6456+1760+16\cdot24=8600.
\]
The independent native replay confirms the cut, exact event order,
frames, retained phase records, and invoice.

Define the next source bank by the same-port role assignment
\[
 Z=(Y_P,X_R),\qquad V=(X_P,Y_R).
\]
Then \(Z=Cx\) has only source input. The complementary bank is
\[
 V_P=-y_P,\qquad V_R=y_R+E_Rx.
\]
This is an invertible map for arbitrary input. Its inverse is
\[
 x=C^{-1}Z,\qquad
 y_P=-V_P,\qquad
 y_R=V_R-E_R C^{-1}Z.
\]
The inverse formula keeps operator order. It does not require any
commutation of \(C\), \(E\), or spatial frame operators.

The role assignment itself does not establish a legal next-stage
entry. That claim needs the actual owner paths and endpoint phases.
With the expected native endpoint, the physical Z fields are all
FULL, while V is FULL on P and a hole on R. The next entry must
therefore admit both resulting types. It must retain the arbitrary
V baseline and the encoded source \(Cx\).

For line-entry reuse, replace the arbitrary selected input \(y_P\)
by a record \(z\) with physical frame \(Q_P\). The accepted H8 prefix
takes this input to FULL \(z\). The same proof gives
\(X_P=-z,\ Y_P=Lx\). Its scalar bill is unchanged; its sixteen
progress children have rank eight instead of rank nine.

## Closure of the source-code family

Let the entries of \(B\) belong to any associative operator ring.
Set \(N_B=e_PB\), where \(B\) has zero columns on P and takes its
input only from R. Then \(N_{B_2}N_{B_1}=0\), even when the entries
of \(B_1\) and \(B_2\) do not commute. Consequently,
\[
 (I+N_{B_2})(I+N_{B_1})=I+N_{B_1+B_2},\qquad
 (I+N_B)^{-1}=I-N_B.
\]
For an invertible block diagonal route
\(T=\operatorname{diag}(T_P,T_R)\),
\[
 T(I+N_B)T^{-1}
 =I+e_P(T_PBT_R^{-1}).
\]
Thus a route that preserves the P/R partition preserves this family.
Repeated clean exchanges can accumulate such source codes without
products of two reader corrections. This is a structural algebraic
statement. It does not price the routed reader, admit the role
dispatcher, or prove that an outer caller performs the required
supplier computation.
