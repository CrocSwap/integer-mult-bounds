# Independent review of the clean centre exchange

All four frozen local words pass. Each word forms a clean selected
centre record from arbitrary input and keeps the previous selected
baseline on the complementary data field. No clean field is required.
There is no material defect in the local word.

## Pinned packet

The producer directory is
`new-core-transfer-20261017/low-displacement-20261020/clean-late-exchange-20261020/`.
Its freeze has SHA256
`96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc`.
The decompressed payload has SHA256
`b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083`.
The proof has SHA256
`eb8e579b11d3d4ce8e77a2d6003b1a95135d84f79ce60d48ee2370194797569c`.

The packet has separate I-entry and Q-entry words for both providers.
The checker does not import the producer. It uses the earlier
independent exact matrix, column, row, and scalar-tariff tools.
`normal/INPUTS.json` gives every consumed source pin.

## Exact operation

Use the actual sixteen pivots P and let R be the other 96 ports.
Let \(L=V_P^{-1}V=[I,B]\) and
\[
 C=\begin{pmatrix}I&B\\0&I\end{pmatrix}.
\]
The independent checker reconstructs this reader from the pinned
response factors and signed pivot Gram matrix. It checks both
inverse orders of C and its literal 1760-unit scalar code.

The retained native core advances all X paths and the 96 ordinary
Y paths. It removes exactly 250 selected-target events, including
128 H1 calls. There is no retained read of a removed selected target.
The selected target then advances to FULL: by H9 in I-entry formation,
or by the accepted H8 line-to-FULL recipe in Q-entry reuse.

At this common-FULL cut, apply C to X. Apply three unit ADDs on
each selected pair \((a,b)=(X_p,Y_p)\):
\[
 b\leftarrow b+a,\qquad a\leftarrow a-b,\qquad b\leftarrow b+a.
\]
This is the signed exchange \((a,b)\mapsto(-b,a)\). It costs 24
real scalar units per pair. A separate sign scale is not required.
`DERIVATION.md` gives the complete algebra and inverse.

The exact physical input is
\[
 X=Qx,\quad Y_R=y_R,\quad
 Y_P=
 \begin{cases}
 y_P&\text{in I-entry formation},\\
 Q_Pz&\text{in Q-entry reuse}.
 \end{cases}
\]
Write \(b=y_P\) in the first case and \(b=z\) in the second.
The exact physical output is
\[
 X_P=-F_9b,\qquad X_R=F_9x_R,\qquad
 Y_P=F_9Lx,\qquad
 Y_R=F_9q_R(y+Ex)_R.
\]
Only \(y_R\) is used in the last expression. The selected input b is
arbitrary and independent. No commutation of Q with C or E is used.

The checker verifies every one of the 640 input columns by a reverse
pass. A separate forward row pass gives the same complete map.
All 416 outside roles remain unchanged for arbitrary values.
The independent formula for the inverse passes both 224-field
matrix product orders. This inverse is an algebraic identity; this
packet does not emit or price an inverse native service.

## Physical frames and phases

Every event is reconstructed from the exact old native core, the
accepted selected progress children, the scalar source code, and
the three-ADD exchanges. Every scalar source and target has the
declared common frame. Every native occurrence has the accepted
ordered input/output frame pair, rank, and phase record.

The I-entry recipes and endpoint maps are byte equal to the accepted
direct-FULL formation packet. Its independent freeze is
`488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532`.
The Q-entry recipes and endpoint maps are byte equal to the accepted
line-entry packet. Its independent freeze is
`cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c`.

There are zero new phase operators. This review inherits those exact
phase checks and verifies every new occurrence binding. The sixteen
H9 calls have identity side maps. The sixteen H8 calls retain both
accepted side maps; no identity-wrapper assumption is made for H8.

The checker rejects a missing source code, missing exchanges, and a
wrong exchange sign. Each mutation changes the map on arbitrary input.

## Invoice

Both providers have the following scalar bill in either entry variant:

| Part | Real scalar units |
|---|---:|
| Retained core | 6456 |
| C on FULL X | 1760 |
| Sixteen signed exchanges | 384 |
| Total | 8600 |

The native and view bills are:

| Entry | Child profile | Children | Native mass | Input views | Output views | Native side-map upper bound |
|---|---|---:|---:|---:|---:|---:|
| I | 1392 H1 + 64 H2 + 48 H3 + 16 H9 | 1520 | 1808 | 112 | 96 | 3008 |
| Q | 1392 H1 + 64 H2 + 48 H3 + 16 H8 | 1520 | 1792 | 128 | 96 | 3040 |

There is no added field, private field, or odd division.
The maximum scalar-content row one-norm is exactly 22. The scalar
word adds at most one binary denominator level at operation
boundaries. These bounds do not cover primitive internals, recursive
children, or roundoff propagation.

## Role and composition scope

The same-port role partition
\[
 Z=(Y_P,X_R),\qquad V=(X_P,Y_R)
\]
uses all 224 data fields exactly once. The checker verifies this
partition and the clean source \(Z=F_9Cx\). It also verifies the
arbitrary complementary baseline \(V_P=-F_9b\).

This role partition is not by itself an implementation of a routed
dispatcher. The actual owner paths, endpoint phases, field selectors,
and their costs require a separate binding. A physical bank
permutation must be priced if the caller uses one. The local result
does not assume a free global bank conversion.

`DERIVATION.md` also proves the source-code closure over a general
operator ring: products of P-from-R corrections are zero, so these
unit shears compose by addition. Block diagonal routes preserve the
family. The proof permits noncommuting spatial operators. It does
not supply the routed access cost or a complete coupled controller.

Child hosting, the caller's encoded source, a final decoder, recursive
precision, and the complete supplier cost remain open dependencies.

## Reproduction and credit

Run from the workspace root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-centre-exchange-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-centre-exchange-review-20261020/normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-centre-exchange-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-centre-exchange-review-20261020/optimized
```

Both runs print `PASS_INDEPENDENT_CLEAN_CENTRE_EXCHANGE`.
`REPRODUCTION.json` records the byte comparison and final source
hash check.

The root and controller lanes proposed the clean coupled interface.
The new-core-transfer lane emitted both native variants. This lane
gave the independent complete replay, the three-ADD cost reduction,
and the line-entry reuse check. The earlier formation and line-entry
reviews provide the unchanged phase evidence. This work used AI
assistance. No PR, push, commit, or publication was made.
