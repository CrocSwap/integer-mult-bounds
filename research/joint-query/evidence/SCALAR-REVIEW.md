# Independent review of the conserved QQ16 scalar pair

The frozen scalar pair passes review. No material error was found.
Both data maps are invertible and preserve all sixteen selected sums.
The complete scalar replays restore every arbitrary helper and clear
the eight owned private outputs. The two data maps were checked with
their own inverses; this is not a claim that the forward and backward
words are mutual inverses.

The scope is the common-chart scalar specialization. Native phases,
legal changing-chart accesses, native child implementations, and the
general ordered operator proof have separate reviews.

## Sources and method

The frozen payload has decompressed SHA256
`6b8d647a8ce2ff86f39b1947d11cbcdfd0f366e90c2816ff6cca09d47c75869c`.
The producer receipt has SHA256
`c9729d71890df17027c75b028c535ad3bd8dc11633812bae856f80c38c52a0a1`.
The producer and note were read without changes. All source pins are
recorded in [REVIEW.json](REVIEW.json).

The [independent checker](verify_conserved_review.py) imports only an
earlier independent rational arithmetic engine. It does not import the
producer, its algebra module, or a native compiler. It rebuilds K and
both selected inverse minors directly from the pinned R. From these it
rebuilds B, C, C^-1, D, and the future logger N, then reconstructs every
literal added scalar event and both typed copy descriptions.

The rebuilt coefficients satisfy

\[
 R_AK_A=R_TK_T=I,\quad R_UK_U=12I,\quad
 BD=12I,\quad N^2=0,\quad CC^{-1}=C^{-1}C=I.
\]

Every nonzero B, C, C^-1, D, or N coefficient is a signed half.
B and N have 52 entries in each of their eight rows. C and C^-1
have four entries in each row, and D has four in each of its 96
nonzero rows. These checks use the actual selected sets and the
actual 8 by 112 matrix, without an assumed root-label symmetry.

The checker also replays each pinned core on all 712 formal inputs
and verifies its clean-J map and scalar bound. It then replays the
new full words on all 712 inputs, including all arbitrary helper and
private values. This replay checks scalar coefficients and chronology;
it does not interpret a chart placeholder as a proved native frame.

## Backward map and inverse

Let u=Ey with E=I+N, let a=R_Tx_T, and let b=Ru. Before the core,
the swap and subtraction give

\[
 X_T=u_T,\quad Y_U=u_U+D x_T,\quad
 Y_T=-B u_{\mathrm{off}T}-11x_T.
\]

The current query is exactly a because BD=12I. Applying the clean
backward core gives the displayed map in the frozen note. The input
A copies must read old y_A before E changes it. Their correction
is exactly what gives X'_A=x_A+y_A-u_A.

The independent replay checks both records directly:

\[
 RY'=a,\qquad \ell_T X'-12RY'=b.
\]

Given arbitrary output data, these records recover u. Subtract K_Ua
on U, add K_Tb+11K_Ta on T, and keep A. Then y=(I-N)u. Recover x_T
as K_Ta, x_U as X'_U+y_U, and x_A as X'_A-y_A+u_A.
Both composition orders were checked on all 224 data columns.

For A, X'_A+Y'_A=x_A+y_A. For T, the b terms cancel and the a
coefficients leave K_Ta=x_T. The checker verifies every selected
sum on all 712 input columns, including possible helper or private
dependence.

## Forward map and inverse

Put f=Rx. The rebuilt forward scalar sequence gives

\[
 X'_U=x_U-K_Uf,\quad X'_A=K_A\ell_Tx,\quad X'_T=K_Tf.
\]

The final A copies read the completed source code. They give
Y'_U=y_U+X'_U and Y'_S=y_S+x_S-X'_S for S=A union T.
All sixteen selected sums therefore hold.

The independent replay checks the two output records

\[
 \ell_T X'=f,\qquad \ell_A X'=\ell_Tx.
\]

These recover x_U and x_T. Subtract their R contributions from f
and apply K_A to recover x_A. The displayed Y equations then recover
y. Both composition orders were checked on all 224 data columns.

For both orientations, all 480 arbitrary helpers have identity output
rows and all eight private output rows are zero. Private values are
owned and discarded. The complete 712-field map is not claimed to be
invertible on those discarded inputs.

## Scalar invoice

The backward added blocks cost, in execution order,
480, 4160, 3840, 208, and 4160 real primitives. Their total is
12,848. The forward added blocks cost 4096, 320, 320, 16, 3840,
and 480, for a total of 9,072. Each retained core costs 202,138.
Thus the complete displayed scalar words cost 214,986 backward and
211,210 forward.

The first forward block has 32 unit coefficients and 384 signed-half
coefficients. Combining each pair of consecutive equal half reads
into one unit read saves 32 times (20 minus 8), which is 384.
X_T is unchanged between those reads, so this combination is valid.

The native-order descriptions call for 24 backward and eight forward
line slots. This review checks the scalar blocks around those slots
and the typed copy descriptions. It does not verify the native lines,
their scalar phases, or their full implementation invoice. Address
maps and any extra scalar phases in the native bundle must be added
before these bounds are used as a full construction cost.

The independent run returned:

```text
PASS_INDEPENDENT_CONSERVED_QQ16_SCALAR_PAIR
words=2 input_columns_each=712 data_inverse_orders_each=2 selected_sums_each=16
B_added=12848 B_complete=214986 F_added=9072 F_complete=211210
```

No complete changing-chart controller, recursive hosting result, or
kappa improvement is claimed. The result is an exact scalar premise
for the separate operator and native construction reviews.

This work uses the selected R, the retained centre-free cores, and
the producer's conserved-sum construction. OpenAI Codex supplied
independent proof and verification work under the user's direction.
