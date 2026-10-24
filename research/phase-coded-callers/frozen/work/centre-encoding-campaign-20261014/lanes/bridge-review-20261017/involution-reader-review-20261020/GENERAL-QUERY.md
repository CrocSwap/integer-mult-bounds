# Sharing a restored source across target readers

Let X be a source module. Let \(Y_1,\ldots,Y_k\) be distinct target
modules. Let T be a unit on X. Assume that these operations are
admitted at their actual physical views:

1. T and \(T^{-1}\) act in place on X.
2. Reader j adds \(L_jX\) to \(Y_j\). It preserves X and every
   other target.
3. Each operation restores its own borrowed fields.

Then the word

\[
T;\quad
(Y_1\mathrel{+}=L_1X);\quad\cdots\quad
(Y_k\mathrel{+}=L_kX);\quad
T^{-1}
\]

has the exact endpoint

\[
(x,y_1,\ldots,y_k)
\longmapsto
(x,y_1+L_1Tx,\ldots,y_k+L_kTx).
\]

The proof follows the actual order. After the first word the
source is Tx. Each reader leaves that source unchanged and
retains the independent baseline of its own target. The final
word restores x. Thus the source transformations are paid once.
No zero target, inverse reader, or commutation hypothesis is
required.

The price is

\[
a(T)+a(T^{-1})+\sum_{j=1}^k c(L_j),
\]

before any sharing of physical views. A reader that alters a
source during its literal word is permitted only if that word
restores the source before the next reader. The endpoint
identity does not remove the cost of target storage or access.

## Actual D25 schedule for one retained reader

Use the reviewed current involution \(T=A_t\). Assume k distinct
target banks are already available in the completed FULL frame,
with the same retained reader \(L_s=P+B_s\). This is an explicit
availability premise. It is not a new native host construction.

Use this schedule:

1. Apply the actual current A word to X, with its current views.
2. Put the 96 ordinary X fields in the old s FULL views.
3. For each target bank, add the sixteen selected X fields to
   its selected target fields while those targets remain in
   global FULL. Enter its sixteen old s target views, run the
   1,760-scalar complement reader, and restore its target views.
4. Restore the 96 old source views.
5. Apply the actual current A word to X again.

The selected X fields remain in global FULL throughout step 3.
The complement reader does not need those selected X fields.
Each target therefore receives both the selected copy and
\(B_sA_tx\). Their sum is \(L_sA_tx\), with the full operator
order retained.

The two current A words cost 6,552 scalar primitives and
448 maps. The k readers cost \(1888k\) scalar primitives.
Their shared ordinary source views cost 192 maps. Their
target views cost \(32k\) maps. Thus the complete query
schedule has

\[
\boxed{6552+1888k\text{ scalar primitives},\qquad
640+32k\text{ monomial calls}.}
\]

For k=1, these are the reviewed literal counts 8,440 and 672.
For k=2, they are 10,328 and 704. The two-target schedule
has not been joined to a native host or supplier in this
packet. No extra fields are treated as free.

If readers use g different old stages, the same source pair
can still be shared. Group the targets by their old stage,
and enter and restore the 96 ordinary source views for
each group. The scalar count remains \(6552+1888k\); the
map count becomes \(448+192g+32k\). This formula assumes
that each stated old-stage view is admitted at the common
completed cut.

This theorem isolates a reusable source operation. It does
not make a product \(C_sA_t\) reciprocal or stage independent.
It does not construct a backward caller, a complete recursive
host, or a terminal decoder.

The bridge-access producer checked the actual one-reader
view schedule and its multi-target count independently.
Its response is recorded in `PEER-REVIEW.md`.

No publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
