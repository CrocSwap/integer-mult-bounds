# Input preparation for the source-code family

The changed-cut construction has a valid native input interface. It can
move the target compensation to the input of the retained backward word.
It needs one rank-one child for each nonzero target row. The sparse
complement section has at most 16 such rows. The full emitted word and
its finite local cost need a separate literal review.

## Exact interface

Use the accepted original-complex clean-J backward word. Its named
physical inputs are

\[
X_p=C_{q_p}x_p,\qquad Y_p=y_p.
\]

The operator is the positive line operator

\[
C_q=\frac{(1+i)I+(1-i)X_q}{2}.
\]

It is not an unspecified representative of the line spanned by \(q\).
The old word first applies 7,401 frame-zero events. Its first source
old_to_new adapter is at event 7,402. The added preparation must occur
before every retained event, while each \(Y_p\) has the input value \(y_p\).

For a row \(a_p\) of a scalar matrix \(A\), do these steps:

1. Clear the existing private field C0.
2. Form \(a_p y\) in C0 from the physical Y inputs.
3. Apply \(C_{q_p}\) to C0.
4. Add C0 to the physical X field \(p\).
5. Clear C0.

The physical addition is

\[
C_{q_p}x_p+C_{q_p}(a_p y)=C_{q_p}(x_p+a_p y).
\]

Thus the logical input changes by \(x\mapsto x+Ay\). No helper input is
assumed to be zero. The first CLEAR removes any old C0 value. The other
private fields retain the original word's private-output-zero contract.
This statement does not supply a seven-carried-field contract.

Choose an invertible binary matrix \(E_p\) whose first column is \(q_p\).
The exact native recipe is

\[
C_{q_p}=P_{E_p}F_1P_{E_p}^{-1}.
\]

It uses one coordinate child and two finite address maps. The identity
has no omitted scalar phase. The independent checker uses an explicit
basis extension to construct \(E_p\). It checks every one of the 512
Gaussian columns for each of the 112 actual ports against the displayed
two-term formula. It also checks all 112 actual source-entry adapters
on all 512 columns. Each adapter sends this positive line operator to
the exact canonical start frame.

The checks reject both an inverse-line substitution and a scalar phase
change. A separate control records basis inputs where the canonical line
frame and the intrinsic \(C_q\) are different. The preparation cannot
replace one by the other without its adapter.

## The changed-cut identity

Let \(\mathcal A\) be the complete retained prefix to the source-code cut,
and let \(\mathcal T\) be its suffix. The exact accepted identities are

\[
\Phi\mathcal A=\operatorname{selector}_Y,\qquad
\mathcal T P=
\begin{bmatrix}-JZ\\ Z\\0\end{bmatrix}.
\]

They hold on all original X, Y, helper, and private input columns. In
particular, the first identity does not depend on X. For arbitrary
dyadic \(B,D\), set

\[
A=JZ(B+D).
\]

First make the input preparation \(x\mapsto x+Ay\). Then run the original
prefix. The same cut read still gives the original \(y\), even though X
has changed. Form all required coordinates of \(By\) before any source
injection, unless the ordered response test permits a serial schedule.
Inject \(PBy\), then run the retained suffix. No late compensation C is
used. The complete logical output is

\[
\begin{aligned}
x'&=x+JZ(B+D)y-Jy-JZBy
   =x-Jy+JZDy,\\
y'&=(I+ZB)y.
\end{aligned}
\]

The helper endpoint responses are unchanged. The same retained native
end frames and helper wrappers therefore give the original complete
physical helper jobs on arbitrary inputs.

There is no recovery read in this schedule. In particular, its execution
does not need \(M^{-1}\), where \(M=I+BZ\). The condition

\[
M\in\operatorname{GL}_8(\mathbb Z[1/2])
\]

is still required when the result is used as an invertible source code
over the dyadic ring. It is equivalent to invertibility of \(I+ZB\).
If it fails, the displayed linear map may still have a literal
implementation with CLEAR, but it is not a reversible encoding of
arbitrary source data. This review does not remove that requirement.

## Sparse section and local cost

For the separately reviewed complement section \(W\),

\[
RW=0,\qquad JW=W.
\]

Its nonzero rows are exactly the 16 ports in its two disjoint selected
minors. Thus \(JW(B+D)\) has support in those 16 rows. For the complement
exchange parameter, the active rows must be checked in the emitted
word; the resulting input-copy upper bound is 16 rank-one children.
This replaces the prior 16 rank-two late copies. It adds no new array.
The unchanged clean-J mass is 5,522, so this upper bound gives mass
5,538 before any further change.

Let \(n\) be the number of nonzero rows of \(JZ(B+D)\), and let \(F\)
denote the existing real-component ADD bound summed over the entries
of a matrix. A direct row construction has input scalar cost

\[
12n+F(JZ(B+D)).
\]

The term \(12n\) pays for two private CLEAR operations and one unit ADD
per active row. A complete eight-coordinate snapshot and source
injection adds

\[
32+F(B\Phi)+F(P).
\]

These are finite local scalar formulas. The exact emitter must check
each coefficient and any removed zero row. The two address maps per
input child remain in the finite native invoice. No global hosting,
precision, or complete supplier cost is inferred here.

## A complete input placement

The same native premise applies if the source update also moves to the
input. First prepare \(x\mapsto x+JZBy\). Then apply
\(y\mapsto (I+ZB)y\) at frame zero, and run the unchanged core. The result
is

\[
x'=x-Jy,\qquad y'=(I+ZB)y.
\]

This order is necessary. The first preparation uses the old source.
It is not a late recovery of that source from its changed value.
The full-source update can use a serial one-buffer schedule when its
ordered response condition holds. A future literal example must check
that condition and its full arbitrary-state map.

## Tensor and exterior factors

Each checked base identity is an equality of complete complex
operators. It therefore tensors to every positive \(\lambda\). The
rank-one child becomes the native coordinate child on \(\lambda\)
coordinates. Its address maps act on each local nine-bit factor.
Scalar coefficients such as the entries of \(B,D\) are applied once;
they are not raised to the \(\lambda\)-th power.

The local maps act as identity on a common spectator factor. Any common
exterior operator on that factor commutes with the input line copy and
with the local adapters. This proves the extension in an already aligned
local interface. Different exterior frames on different roles require
their own alignment proof. The result does not supply new routed query
access between separate global calls.

The independent checker is review_input_compensation_native.py.
Its exact inputs, controls, and coverage are in
INPUT-COMPENSATION-NATIVE-REVIEW.json.
