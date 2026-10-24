# Native services for a rank-sixteen involution and its transpose

This packet emits eight complete native words. It covers two providers,
two response matrices, and two shear directions. The matrices are the
controller's frozen \(A\) and \(A^T\), with

\[
A^2=(A^T)^2=I,\qquad \operatorname{rank}(A-I)=16,\qquad \det A=1.
\]

Each word has sixteen selected FULL target outputs and 96 ordinary hole
outputs. This change of output contract is part of the construction.

## Exact physical operation

Let \(M\) be \(A\) or \(A^T\). Let \(P\) be the selected set and \(U\) its
complement. Put \(q_p=Q_p^{-1}\). All words accept
\(X_p=Q_px_p\) and \(Y_p=y_p\). All 640 input fields are independent and
arbitrary. The forward word gives

\[
 X_{\rm out}=F_9x,\qquad
 (Y_{\rm out})_P=F_9(y+Mx)_P,\qquad
 (Y_{\rm out})_U=F_9q_U(y+Mx)_U.
\]

The backward word gives

\[
 X_{\rm out}=F_9(x-M^Ty),\qquad
 (Y_{\rm out})_P=F_9y_P,\qquad
 (Y_{\rm out})_U=F_9q_Uy_U.
\]

Every one of the 416 auxiliary fields is unchanged. There is no extra
owned field, private field, zero-input assumption, or odd division.

The selected physical ports, in the pinned order, are

```text
0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23.
```

The first eight ports are four complete physical pair blocks. The pair
code therefore does not mix selected and ordinary fields.

## Actual transfer slots

In each signed mode block of size \(k=6\) or \(8\), the old response is
\(E_k=I-dd^T\). The new response is

\[
A_k=I+\bigl((k-2)e_p-d\bigr)d^T,\qquad d_p=1.
\]

Only the pivot row changes. Its diagonal coefficient is \(k-2\), and its
other coefficients are \((k-3)d_j\). The transpose changes only the pivot
column. For an ordinary row, its old pivot-column coefficient is
multiplied by \(-(k-3)\). Thus the off-diagonal support stays inside the
actual cyclic or clique transfer slots. All new mode coefficients are
integers.

The emitter uses the source transfer record for each slot. It divides the
recorded coefficient by its old mode coefficient to obtain the exact
orientation sign, checks that the sign is \(1\) or \(-1\), and multiplies
that sign by the new mode coefficient. This is done in both native
directions. It does not infer a backward circuit from a matrix transpose.

The source stores the small-clique map separately from the large mode
matrix. The emitter inserts those pinned small physical rows before it
computes the coefficient ratios. The small component has no pair code.

For a forward word, remove every event that writes a selected Y field.
The pair closure makes this removal complete. No retained event reads a
selected Y field. For a backward word, also remove every transfer that
reads a selected Y field. All source-X progress and ordinary-Y progress
remain in place.

After the entire retained sweep, all 112 X fields are FULL, all ordinary
Y fields have completed their hole paths, and every selected Y field is
still in I. Apply sixteen explicit rank-nine FULL children to the
selected Y fields. Then:

- Forward: add \(M[P,*]X\) to \(Y_P\).
- Backward: subtract \(M[P,*]^TY_P\) from X.

All these late operations have the exact common FULL chart. In the
backward word, the ordinary contributions were made during the retained
sweep and the selected contributions are made by the late scatter. Their
sum is exactly \(-M^Ty\).

## The backward scatter

The forward selected-row query is a shear with arbitrary Y baselines.
Take the inverse transpose of each elementary gate in chronological
order. A gate `Y += c X` becomes `X -= c Y`; a scale of a selected Y by
\(a\) becomes a scale of that Y by \(a^{-1}\). The resulting word is the
inverse transpose of the complete forward query. It is precisely the
required negative transpose scatter.

The temporary selected-Y scales are undone. They do not consume a
record or require a zero baseline. This implementation has the same
scalar price as the forward query. A direct grouping by X targets also
passed, but costs 112 more scalar primitives. Its prototype and outputs
are retained separately; the final packet uses the cheaper exact word.

## Complete local invoice

The two providers have the same invoice. Each of the eight words has

\[
1392H_1+64H_2+48H_3+16H_9.
\]

This is 1520 native children and native mass 1808. The sixteen new FULL
children use the previously reviewed rank-nine recipe with identity
left and right wrappers. The remaining native side-map upper bound is
3008. Each word has 112 explicit input monomial views and 96 explicit
output monomial views.

| Response | Direction | Retained scalar cost | Late query | Total scalar cost | Content prefix norm |
| --- | --- | ---: | ---: | ---: | ---: |
| \(A\) | Forward | 6456 | 2960 | 9416 | 70 |
| \(A\) | Backward | 6456 | 2960 | 9416 | 22 |
| \(A^T\) | Forward | 6952 | 1984 | 8936 | 30 |
| \(A^T\) | Backward | 6952 | 1984 | 8936 | 62 |

The content bounds are exact maxima of row one-norms at scalar/native
boundaries in the literal word. The additional binary denominator height
is one. These are not bounds for the internal implementation of a
recursive child.

## Phase and verification

The emitter pins the full native source, the matrix/query packet, the
cyclic flags, the direct-FULL formation packet, and its independent
review. Every used native recipe, ordered frame array, input view, and
output view matches that reviewed formation packet byte-for-byte. No
new spatial operator is introduced. Only the scalar coefficients and
their chronology change. The direct FULL children include their global
phase.

The verifier executes every literal event on all 640 independent input
columns. It checks the entry and exit frame of every native call and the
exact common frame of every scalar read and write. It checks all output
content, all final frames, all helpers, all scalar costs, all native
ranks, and the prefix bounds. It then reads the serialized payload and
repeats the complete checks. In each word, deletion of a retained ADD or
a late-query ADD is rejected.

Normal Python and optimized Python produce byte-identical final
payloads and receipts. Reproduce into new directories:

```sh
python3 emit_involution.py --out replay-normal
python3 -O emit_involution.py --out replay-optimized
```

The first two development runs stopped at source-schema checks before
they emitted a payload. The earlier grouped-scatter normal and optimized
runs passed and are kept as development evidence. The files named in
`FREEZE.json` are the final result.

## What this enables

The native family now contains a dyadic involution with displacement
rank sixteen, together with both actual shear directions for it and its
transpose. The old odd centre eigenvalues are absent. The construction
permits sixteen nonzero diagonal entries by giving those targets a
complete FULL path and a late query. Thus a zero-diagonal restriction of
the old native transfer grammar no longer forces the response family.

For example, the backward word with response \(A^T\) has content update
\(x\mapsto x-Ay\), while the forward word with response \(A\) has content
update \(y\mapsto y+Ax\). Their content responses are reciprocal because
\(A^{-1}=A\). Their physical outputs still have the stated mixed frames.
No interstage Q commutation, free conversion to all-hole outputs, or
complete caller follows from this content identity.

This packet supplies no complete supplier or kappa improvement. A caller
must account for the actual routed responses, selected-field phase
transitions, recursive children, and final output contract.

This work uses the controller's row-completion theorem, the cyclic native
family, and the productive row-capture construction from the coordinated
centre-information campaign. AI agents prepared the proof, code, and
checks. Independent review of this new complete family is separate.
