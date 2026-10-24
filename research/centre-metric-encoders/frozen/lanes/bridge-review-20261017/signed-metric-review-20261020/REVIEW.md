# Independent review of the signed metric and sixteen-reader code

The actual 112-port response and both scalar codes pass this review.
The signed metric permits a dyadic code with sixteen centre fields.
The new pair suffix also makes the transpose fit the native support
conditions. These are exact local results. This review does not certify
a native service, a routed caller, a recursive host, or a supplier bound.

## Sources and method

The review pins these producer freezes:

| Packet | Freeze SHA256 |
| --- | --- |
| Reciprocal model | `9dbff19fa68567eadea82cef2add71fda3ffe7228944028d06d53880da8b70f7` |
| Original sixteen-reader code | `8739b5dbba6a5422c9b68035683876931fbf8f6599a43375d10e73eee55b2de2` |
| Pair-closed companion | `810508791ea43aecaaf894c3cb50a8170d3e6f1f8e52684e274cda16c2c2db57` |

The source proofs are
[MODEL.md](../../oblique-native-20261017/signed-metric-reciprocal-20261020/MODEL.md),
[SIGNED-SIXTEEN.md](../../new-core-transfer-20261017/low-displacement-20261020/signed-sixteen-20261020/SIGNED-SIXTEEN.md),
and [PAIRED-COMPANION.md](../../new-core-transfer-20261017/low-displacement-20261020/signed-sixteen-20261020/PAIRED-COMPANION.md).

[check_review.py](check_review.py) imports no producer code. It uses
the exact sparse fraction engine from this lane's frozen
[query review](../fixed-reader-reuse-review-20261020/FREEZE.json).
It constructs each response and code from the formulas below, then
compares all matrices with the pinned packets. It reconstructs the
physical pair matrix from the actual pair list. It checks the actual
port labels, all sixteen blocks, and every physical support entry.

The scalar replay starts with 640 independent complex input fields.
Each field is an independent symbolic variable. The check therefore
covers arbitrary data and borrowed fields, not only zero work fields.
The complete code words leave the other 528 fields unchanged. The
two-bank reference words leave the other 416 fields unchanged.

## The reciprocal response

Let \(n=k+4\). In the coordinate order
\((a_0,\ldots,a_{n-3},b,c)\), set

\[
 u=(1^{n-2},k,0)^T,\qquad \ell=(-1^{n-2},1,0),\qquad
 R=I+u\ell,\qquad E=PR,
\]

where \(P\) exchanges \(b,c\). Let

\[
 J=\operatorname{diag}(1^{n-2},-1/k,-1/k),\qquad K=J^{-1}.
\]

Then \(\ell u=-2\), \(Ju=-\ell^T\), and \(u^TJu=2\).
Expansion gives

\[
 R^2=I,\qquad R^TJR=J,\qquad P^TJP=J.
\]

It follows that

\[
 E^{-1}=RP,\qquad E^TJE=J,\qquad E^{-T}=JEK.
\]

The order \(RP\) in the inverse is required. In general \(E^2\ne I\).
The displayed formulas give zero diagonal for both \(E\) and \(E^{-1}\).
Each block has \(\operatorname{rank}(E-P)=1\) and
\(\operatorname{rank}(E-I)=2\).

The actual response has eight six-mode blocks and eight eight-port
blocks. Thus the two ranks are sixteen and thirty-two. The sixteen
readers encode \(E-P\). They do not encode \(E-I\) in sixteen fields.

## The physical chart

Let \(H\) be the 24 actual pair codes on the large 48-port sector.
It is the identity on the small 64-port sector. Each pair satisfies
\(H_{\rm pair}^TH_{\rm pair}=2I\). Physical matrices are
\(H^{-1}AH\), where \(A\) is the mode matrix.

The scale in \(H^TH\) is constant on the whole large sector. All
mode matrices preserve the large and small sectors. The input metric
is constant on each physical pair. These facts, rather than similarity
alone, preserve the transpose metric identity. The physical \(J\) is
diagonal, with 80 entries \(1\), sixteen entries \(-1/2\), and sixteen
entries \(-1/4\).

The check confirms both physical zero diagonals and every orthogonal
port-label support condition. Physical \(P\) is the identity on 80
fields and acts only on the other 32. It has 160 nonzero entries and
is not a field permutation. Its complete common-frame word costs 728
real scalar primitives. This price does not include address views.

## The local code and its inverse

For \(n=6\), use these rows in order:

\[
 \ell,\quad a_2-a_3,\quad a_0-a_1,\quad c,\quad
 a_0+a_1-a_2-a_3,\quad \sum_{j=0}^3a_j-2b.
\]

For \(n=8\), use:

\[
\begin{split}
 \ell,\quad &a_4+a_5-b/2,\quad a_4-a_5,\quad c,\quad
 a_0-a_1,\quad a_2-a_3,\\
 &a_0+a_1-a_2-a_3,\quad
 \sum_{j=0}^3a_j+2a_4+2a_5-2b.
\end{split}
\]

Call the direct sum of these matrices \(C_m\). Direct row products
give the local \(K\)-Grams

\[
 G_6=\operatorname{diag}(2,2,2,-2,4,-4),\qquad
 G_8=\operatorname{diag}(2,1,2,-4,2,2,4,-4).
\]

Both local determinants are \(-8\). Each ordinary row annihilates
\(u\), and its diagonal entry is zero. The centre row is \(\ell\).
Thus \(C_mR=ZC_m\), where \(Z\) negates the sixteen centre positions.
Each displayed Gram entry is a dyadic unit. The identity
\(C_m^{-1}=K C_m^T G_m^{-1}\) proves a dyadic inverse.

For the original physical code, let \(H_{\mathrm{ord}}^{-1}\) undo
the pair codes only on ordinary pairs. Then

\[
 C=H_{\mathrm{ord}}^{-1}C_mH,\qquad
 CKC^T=G,\qquad
 C^{-1}=KC^TG^{-1},\qquad C^{-T}=G^{-1}CK.
\]

The actual ordinary pairs have equal Gram entries. Hence \(G\) is
physical and diagonal. The selected rows are exactly the sixteen
source readers \(L\), in the source order. Their weighted Gram is

\[
 LKL^T=\operatorname{diag}(4I_8,2I_8).
\]

The factor four on the first eight rows comes from the physical
pair transform. The check does not replace it by two.

## The paid pair suffix

Let \(H_{\mathrm{sel}}\) be \(H\) on the four selected large pairs
and the identity elsewhere. The companion code is

\[
 \bar C=H_{\mathrm{sel}}^{-1}C=H^{-1}C_mH.
\]

The supplied suffix implements \(H_{\mathrm{sel}}^{-1}\) in 13
instructions, at a cost of 80 real scalar primitives. It changes
the selected readers by an invertible pair code. It leaves all
ordinary rows unchanged. The individual readers are recovered by
the paid matrix \(H_{\mathrm{sel}}\); recovery is not free.

The complete native charts satisfy

\[
 H\bar C H^{-1}=C_m,\qquad
 H\bar C^T H^{-1}=C_m^T.
\]

For the second identity use that \(H^TH\) commutes with \(C_m^T\).
Both matrices have zero ordinary diagonals and the admitted local
mode support. In contrast, the original \(HC^TH^{-1}\) has 32
ordinary rows outside their mode blocks. The suffix resolves this
specific support defect.

The companion Gram \(\bar G=\bar C K\bar C^T\) is diagonal.
Its sixteen selected entries are all two. The check proves

\[
 \bar C^{-1}=K\bar C^T\bar G^{-1},\qquad
 \bar C^T\bar G^{-1}\bar C=J
\]

and both inverse orders. These conditions permit a separate native
construction to use the transpose code. This review certifies its
scalar word and support; it does not substitute them for a native
phase check.

## Complete scalar prices and bounds

All listed prices include pair changes, signs, scales, and exchanges.
The norms and binary heights are exact maxima at scalar instruction
boundaries. They are not bounds on internal native-child arithmetic.

| Word | Real scalar primitives | Prefix row one-norm | Binary height |
| --- | ---: | ---: | ---: |
| Original \(C\) | 5564 | 24 | 3 |
| Original \(C^{-1}\) | 5564 | 9 | 3 |
| Original literal \(C^{-T}\) | 5564 | 5 | 3 |
| Original diagonal construction of \(C^{-T}\) | 6092 | 32 | 3 |
| Companion \(\bar C\) | 5644 | 24 | 3 |
| Companion \(\bar C^T\) | 5644 | 8 | 3 |
| Companion \(\bar C^{-1}\) | 5644 | 10 | 3 |
| Companion \(\bar C^{-T}\) | 5644 | 6 | 3 |

Each companion word has 752 instructions and uses no extra field.
No prefix uses an odd denominator.

## Arbitrary target baselines in the clean dual

Let \(S\) project onto the selected fields and \(T=I-S\). The complete
clean reference map is

\[
 F_C=\begin{pmatrix}TC&-S\\C&T\end{pmatrix},\qquad
 F_C^{-T}=\begin{pmatrix}TC^{-T}&-I\\SC^{-T}&T\end{pmatrix}.
\]

The exact diagonal conversion is

\[
 \operatorname{diag}(G,G)F_C^{-T}
 \operatorname{diag}(J,G^{-1})
 =
 \begin{pmatrix}TC&-I\\SC&T\end{pmatrix}.
\]

This follows from \(C^{-T}=G^{-1}CK\), and from the fact that
diagonal \(G\) commutes with \(S,T\). The result holds for arbitrary
inputs in both banks. In particular, it retains each ordinary target
baseline with coefficient \(-1\) in the first bank and \(+1\) in the
second bank. Both input banks have a metric factor.

The independent replay forms the literal chronological inverse-
adjoint of the scalar word. It then applies the exact pre and post
scales. It also checks conjugation by the selected-bank exchange.
The complete metric wrappers cost 1264 real primitives before fusion.
Deleting the input metric scales on the target bank makes the map
incorrect. This two-bank price is distinct from the 320-primitives
one-bank conversion in the reciprocal model.

## What changes in the coordinate obstruction

The new raw physical reader has Euclidean Gram

\[
 LL^T=\operatorname{diag}(10I_8,7I_8).
\]

It has row rank sixteen modulo each of 3, 5, and 7. Its Gram rank
is sixteen modulo 3, but eight modulo 5 or 7. Thus the old modulo-3
instance must not be applied to this new reader without change.

The general coordinate obstruction still applies to a Euclidean
unitary code. A subspace of dimension \(r\), with restricted Gram
rank \(s\), in a nondegenerate space of dimension \(m\) must satisfy
\(m\ge 2r-s\). Its radical has dimension \(r-s\), lies in the
orthogonal complement, and that complement has dimension \(m-r\).
Apply this argument modulo 5 or 7. A real dyadic orthogonal code
requires at least 24 output coordinates for this reader.

For a Gaussian dyadic unitary code, use realification. The two real
copies have row rank 32 and Gram rank 16. Thus \(2m\ge64-16\), so
at least 24 complex coordinates are required. This assumes exact
read access through the supported output coordinates, as in the
[coordinate theorem](../../../root/UNITARY-CENTRE-FOOTPRINT-20261020.md).

The sixteen-field code does not satisfy the Euclidean-unitary
hypothesis. It preserves a signed metric between two diagonal
coordinate metrics. Its weighted reader Gram is a dyadic unit.
This is the precise escape from the unitary obstruction.

## Reproduction, limits, and credit

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/signed-metric-review-20261020/check_review.py --output <new-directory>
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/signed-metric-review-20261020/check_review.py --output <another-new-directory>
```

The expected status is
`PASS_INDEPENDENT_SIGNED_METRIC_AND_SIXTEEN_CENTRES`.
Both modes must give the same receipt bytes. The check includes
negative controls for a deleted code ADD, a deleted inverse ADD,
the changed raw reader after the pair suffix, a changed metric sign,
and omitted target metric scales.

The checker also verifies the proposed general one-centre Gram for
seven sizes \(k=1,2,4,8,16,32,64\). These checks are regression data.
The separate all-size proof and word are not part of this freeze.

The root lane supplied the signed reciprocal family. The oblique
lane bound its actual response. The new-core-transfer lane supplied
the sparse local bases, scalar words, and paid pair suffix. This
review independently derives the matrices, checks all scalar
columns, and identifies the modulo-5 and modulo-7 unitary bounds.
AI assistance was used.

Native phases, routed source access, saved-record restoration,
recursive hosting, finite-precision guards, and the complete supplier
cost remain separate obligations. No selected bound changes here.
No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
