# Independent review of the native involution services

All eight frozen local words pass. The words cover two providers, the
responses \(A\) and \(A^T\), and both shear directions. There is no material
native defect. This review does not establish a complete supplier.

## Frozen inputs and method

The native producer is
`new-core-transfer-20261017/low-displacement-20261020/row-involution-native-20261020/`.
Its `FREEZE.json` has SHA256
`ad8a365247b60ff3621e701bb88d8692cc4f545ae09b3ec8fbe8d69b7f348ea1`.
The decompressed final native payload has SHA256
`aa5356c5cb618984ba3c76c40a255ebd26a66f0a88ac9f57792ab8f6677f9a30`.
This review uses `run-normal-final/`, not the earlier development words.

The matrix source is
`controller-followthrough-20261017/row-involution-20261020/`.
Its main freeze has SHA256
`538ec208e510af7ee29aff4783d304e393c967697a6612e5c42e38fbc0ab9be2`.
Its final matrix payload has SHA256
`a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b`.

The independent checker does not import a producer module. It uses exact
rational arithmetic. It derives the matrices in two ways, reconstructs
each event list from the old native word, and runs a reverse column pass
and a separate forward row pass. Each pass covers all 640 input fields.
The checker binds each native occurrence to the accepted ordered frame
pair and phase recipe. `normal/INPUTS.json` lists every consumed file and
its hash.

## Matrix proof

Write the old response as \(E=I+UV\). Let \(P\) be the ordered set of
sixteen physical pivots and let \(R\) be its complement. The actual
\(V_P\) is invertible. Preserve \(U_R\), and set

\[
 U'_P=V_P^{-1}(-2I-V_RU_R),\qquad A=I+U'V.
\]

Then \(VU'=-2I\), so
\[
 A^2=I+U'(2I+VU')V=I.
\]
The matrix \(A^T\) is also an involution. Over a field with
characteristic different from two, \(U'\) is injective and \(V\) is
surjective. Thus \(\operatorname{rank}(A-I)=16\).
The image of \(U'\) is the minus-one eigenspace; the kernel of \(V\)
is the plus-one eigenspace. Therefore \(\det A=(-1)^{16}=1\).

The checker derives the physical pivot inverse from the actual signed
Gram matrices. It then derives the same \(A\) from the sixteen disjoint
mode blocks. There are eight blocks of size six and eight of size eight.
For a signed block vector \(d\), with pivot \(p\) and \(d_p=1\), the
block is
\[
 A_k=I+\big((k-2)e_p-d\big)d^T.
\]
The inner product of the two update vectors is \(-2\). Hence each
block is an involution with determinant \(-1\). The actual signed
two-port transforms and their inverses convert these blocks to the
physical matrix. The conversion agrees exactly with the first
derivation, including the physical transpose.

The exact checks give
\[
 \operatorname{rank}(A-I)=16,\quad
 \operatorname{rank}(A-E)=16,\quad
 \operatorname{tr}A=80,\quad \det A=1.
\]
Only the selected physical rows change from \(E\).
The general construction proves the first rank statement. It does not
prove the second rank statement for every source. The source's separate
`COMPLETION-LIMITS.md` states this distinction. Its SHA256 is
`91bd564b31766300cc89b87cf808439135d89c27bde655a2fc1842646c304607`;
its freeze is
`775c1b565ec0aa969f2dbecebb04f4b9a82a561e7e7d842c2b1abae7a75509a6`.
This resolves the ambiguous phrase “The change has rank r” in the
original proof. This review does not accept the other results in that
addendum by this reference alone.

## Complete event and phase check

For each family and direction, the checker identifies the old transfer
slots from the actual source metadata. It derives the new coefficients
from the two mode matrices. Exactly 96 source slots change. Their
support and order stay fixed.

The checker then reconstructs the selected-path deletion. Exactly 250
events are removed: 128 rank-one child calls and 122 scalar events.
There is no retained read from a removed selected target. The exact
retained index list agrees with the payload. At the end of this core,
all 112 source fields are in FULL, and the sixteen selected target
fields are still in I. The word then applies sixteen positive FULL
children and the late scalar query.

The late forward query adds the raw selected rows \(M_P X\), where
\(M=A\) or \(A^T\). There is no row precode in these words.
The late backward query is the gatewise inverse transpose of that
forward query in the same chronological order:

- \(t\leftarrow t+c\,s\) becomes \(s\leftarrow s-c\,t\).
- \(t\leftarrow a\,t\) becomes \(t\leftarrow a^{-1}t\).

For a forward product \(F=M_n\cdots M_1\),
\(F^{-T}=M_n^{-T}\cdots M_1^{-T}\). This explains the chronological
order. Both matrix product orders of the isolated query and its inverse
transpose equal identity. The complete backward replay also restores
all 112 target baselines and their temporary scales.

Each frame array, input view, output view, and native phase record is
byte equal to the accepted direct-FULL formation packet. Its independent
review freeze is
`488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532`.
The sixteen FULL calls use that packet's exact identity side maps.
Every scalar event is between fields in its declared common frame.
Every native occurrence has the correct input and output frame. All
recipes are used, and the final frame ledger agrees with the payload.

There are no new phase operators in this change. This review inherits
the pinned complete phase checks; it does not claim a second phase
interpreter run. The coefficient substitutions do not change a native
operator or a boundary map.

## Exact physical contract

Let \(Q\) be the block diagonal input line operator and write \(q_U\)
for its ordinary-port restriction. With physical input
\(X=Qx,\ Y=y\), the forward output is
\[
 X'=F_9x,\qquad
 Y'_P=F_9(y+Mx)_P,\qquad
 Y'_U=F_9q_U(y+Mx)_U.
\]
The backward output is
\[
 X'=F_9(x-M^Ty),\qquad
 Y'_P=F_9y_P,\qquad
 Y'_U=F_9q_Uy_U.
\]

These formulas retain the order of the frame operators. The proof
does not commute \(Q\) through \(M\), and does not identify the two
complete physical words as literal inverse adjoints without their
boundary conversions.

All 640 arbitrary input columns pass in each word. All 416 other
fields remain unchanged for arbitrary values. No field is assumed
zero, and no extra or private field is introduced. Two negative
controls fail as required: omission of the late query and reversal of
the backward query chronology.

## Local invoice and numerical scope

Both providers have the following exact scalar invoices.

| Response | Direction | Retained core | Late query | Total |
|---|---|---:|---:|---:|
| \(A\) | Forward | 6456 | 2960 | 9416 |
| \(A\) | Backward | 6456 | 2960 | 9416 |
| \(A^T\) | Forward | 6952 | 1984 | 8936 |
| \(A^T\) | Backward | 6952 | 1984 | 8936 |

Every word has 1392 H1, 64 H2, 48 H3, and 16 H9 children:
1520 children and native mass 1808. It has 112 input views, 96 output
views, and a native side-map upper bound of 3008. It has no odd scan.
The child profile and map counts remain separate from the old real
scalar tariff.

The maximum exact scalar-content row one-norms are 70 and 22 for the
forward and backward \(A\) words, and 30 and 62 for the corresponding
\(A^T\) words. Each word adds at most one binary denominator level
relative to its input coordinates at scalar operation boundaries.
These checks do not bound primitive internals, recursive child
internals, or roundoff propagation.

The 2960 and 1984 queries are raw selected response rows. They are not
the separate captured-reader query \(WA=-W\). This review does not
certify the source's additional common-frame gauge words, a routed
reader, an endpoint decoder, child hosting, or a complete recursive
precision and supplier cost.

## Reproduction and credit

Run from the workspace root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-involution-native-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-involution-native-review-20261020/normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-involution-native-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-involution-native-review-20261020/optimized
```

Both runs print `PASS_INDEPENDENT_NATIVE_ROW_INVOLUTIONS`.
`REPRODUCTION.json` records the byte comparison and the final source
hash check.

The controller-followthrough lane supplied the row completion.
The new-core-transfer lane supplied the native words and invoices.
This lane supplied the separate matrix derivations, event reconstruction,
reverse replay, and review. The accepted formation and raw phase
reviews supply the unchanged native phase evidence. This work used AI
assistance. No PR, push, commit, or publication was made.
