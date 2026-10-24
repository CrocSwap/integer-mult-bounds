# Independent review of the clean inverse-adjoint pair

All four complete local words pass: two providers, with the
inverse-adjoint and its selected-field conjugate. Both operations
cost 8600 real scalar units and have native mass 1792. No extra
physical swap is required. There is no material local defect.

## Sources and independent method

The producer directory is
`new-core-transfer-20261017/low-displacement-20261020/clean-late-exchange-20261020/`.
The dual freeze has SHA256
`fa8f910fe7f22a696f47513c95e814588723dc8abaaa68061fcba3676c308d43`.
The decompressed dual payload has SHA256
`6c8869b1c1b45632635805e389899b83fa8348c9fe5b84e3c9c7821bcfd0568c`.
The producer proof has SHA256
`1515a8b82ecfcb32d7dc19a4a8bc0fcf0af870ac444bb1628443dfb378360cb9`.

The accepted clean source review has freeze SHA256
`6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d`.
The new checker imports that independent review code and no producer
module. It reconstructs the response blocks, derives the complete
inverse from the clean endpoint, and checks the dual word with a
reverse input-column interpreter and a separate forward row pass.
`normal/INPUTS.json` gives every consumed hash.

## Independent block calculation

Use selected ports P and ordinary ports R. Write the normalized
reader as \(L=[I,B]\), and put \(D=E_{RP}\). The checker verifies
the following identities on the actual source:
\[
 E=E^T,\qquad E_{PP}=0,\qquad E_{PR}=-B,\qquad
 D=-B^T,\qquad E_R=[D,I+DB].
\]
The relation \(D=-B^T\) is thus a checked source identity, not a
premise for an arbitrary reader.

For inputs \((a,u,z,v)=(X_P,X_R,Y_P,Y_R)\), the clean content map is
\[
 M(a,u,z,v)=(-z,\ u,\ a+Bu,\ v+u+D(a+Bu)).
\]
Its inverse at \((A,U,Z,V)\) is
\[
 (Z-BU,\ U,\ -A,\ V-U-DZ).
\]
This gives
\[
 M^{-T}(a,u,z,v)=(-z,\ u+Da-v,\ a+Bv,\ v).
\]
Let S exchange only the selected X and Y coordinates. Then
\[
 S M^{-T} S(a,u,z,v)
 =(z+Bv,\ u+Dz-v,\ -a,\ v).
\]
The checker derives the first dual from the full inverse matrix and
the second by row and column permutation. Separate block formulas
give the same matrices. Both inverse product orders pass for each.
The formulas use no inverse of E and no odd division.

For general operator-valued B and D, the selected conjugate is
\[
 (z-D^*v,\ u-B^*z-v,\ -a,\ v).
\]
The shorter formula with \(+B\) and \(+D\) requires \(D=-B^*\).
This review proves that relation for the local real source. A routed
operator substitution needs its own adjoint and access proof.

## Why the physical inverse-adjoint uses the same native phases

The physical entry and exit operators are
\[
 A_{\rm in}=\operatorname{diag}(Q_X,Q_P,I_R),\qquad
 A_{\rm out}=\operatorname{diag}(F_{9,X},F_{9,P},F_9q_R).
\]
They are unitary. The accepted physical clean map is
\(W=A_{\rm out}M A_{\rm in}^{-1}\). Therefore
\[
 W^{-*}=A_{\rm out}M^{-T}A_{\rm in}^{-1}.
\]
No frame operator is commuted through M in this identity.

For chronological gates \(G_1,\ldots,G_n\), the complete operator is
\(G_n\cdots G_1\), and its inverse-adjoint is
\[
 G_n^{-*}\cdots G_1^{-*}.
\]
Thus the chronological gate order stays fixed. Each exact native
operator and boundary monomial is unitary, so \(U^{-*}=U\), including
its global phase. This follows for the accepted kernels from their
unitary positive line factors and unitary monomial side maps. The
exact previously reviewed phase records are therefore retained.

For a real scalar ADD, the inverse-adjoint transposes source and
target and negates the coefficient. For a real SCALE, it inverts
the coefficient. The checker compares every emitted event with this
rule, at its original chronological position. Each new scalar
source and target is still in the same declared frame.

This is a statement about the exact mathematical child interface.
It does not assert that a rounded numerical implementation is
exactly unitary. Recursive precision and error propagation remain
separate.

## Exact selected-field conjugation

On each selected port, both entry fields have the same intrinsic Q
operator. Both exit fields have the same FULL operator. The checker
verifies the equal input frame, port, rank, and complete left/right
monomial records at each of the 32 selected physical input fields.
It also verifies the FULL/FULL output symmetry. Hence S commutes
with both \(A_{\rm in}\) and \(A_{\rm out}\).

The circuit identity
\[
 S W^{-*}S
 =(S G_n^{-*}S)\cdots(S G_1^{-*}S)
\]
allows every internal pair \(SS\) to cancel. Each remaining
conjugated gate is implemented on the permuted physical field
indices. The checker verifies that explicit permutation for every
native event, scalar target, scalar source, and input adapter.
The actual input adapter operator at each physical field is
unchanged. The 96 ordinary output adapters keep their fields.

The instruction list has the same length as the clean source.
There are no runtime boundary swaps and no unpaid gate. This is
an explicitly emitted circuit, not an assumption that an arbitrary
caller can relabel live banks for free.

The Q-entry physical contract for the selected conjugate is
\[
 \begin{aligned}
 X&=Q(a,u),& Y_P&=Q_Pz,&Y_R&=v,\\
 X'_P&=F_9(z+Bv),&
 X'_R&=F_9(u+Dz-v),&
 Y'_P&=-F_9a,\qquad Y'_R=F_9q_Rv.
 \end{aligned}
\]
For the unpermuted dual, the content is
\((-z,u+Da-v,a+Bv,v)\), with the same physical exit frames.

## Complete verification and invoice

All 640 arbitrary input columns pass in all four words. The
separate forward replay agrees and preserves all 416 outside roles.
The complete native frame ledger and every used recipe agree with
the accepted clean source. There are zero new phase operators;
this review inherits the exact spatial phase sweep rather than
claiming another run of it. Reversing the scalar chronology changes
the map, as the negative control requires.

Every word has:

| Item | Exact count |
|---|---:|
| Retained-core scalar units | 6456 |
| Inverse-transposed source code | 1760 |
| Inverse-transposed exchanges | 384 |
| Total scalar units | 8600 |
| Native profile | 1392 H1 + 64 H2 + 48 H3 + 16 H8 |
| Native children | 1520 |
| Native mass | 1792 |
| Input views | 128 |
| Output views | 96 |
| Native side-map upper bound | 3040 |
| Runtime boundary swaps | 0 |
| New or private fields | 0 |
| Odd scans | 0 |

The H8 side maps stay charged. The exact content row one-norm
maximum is 12, and the maximum additional binary denominator
height is two. These bounds apply at scalar operation boundaries.
They do not cover primitive internals or recursive child errors.

The routed two-call computation, field dispatcher, helper host,
terminal decoder, and full supplier cost are not established here.

## Reproduction and credit

Run from the workspace root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-dual-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-dual-review-20261020/normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-dual-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/clean-dual-review-20261020/optimized
```

Both print `PASS_INDEPENDENT_CLEAN_DUAL_AND_SELECTED_CONJUGATE`.
The reproduction receipt records the output comparison and final
source hash check.

The cover-algebra lane supplied the useful selected-bank form.
The new-core-transfer lane supplied the literal dual circuit. This
lane independently derived the block formula and the field
conjugation rule, and checked the complete native word. The earlier
clean, line-entry, and formation reviews supply the retained phase
evidence. AI assistance was used. No PR, push, commit, or publication
was made.
