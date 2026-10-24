# A literal query for a centre reader retained from an earlier stage

This packet expands the bridge worker's fixed-reader construction into
literal scalar and field-map instructions. It checks their composition
with the complete native carrier prefix. It covers the actual D25 stage
pairs \((s,t)=(0,1),(0,2),(1,2)\).

The local carrier prefix and the query use different charts. The prefix
has the exact local native charts. The query starts after the dispatcher
has placed all X fields and the sixteen selected Y fields in the global
FULL chart at level \(t\). The dispatcher is a separate binding. This
packet does not assume that those charts are identical.

## Required update

Let \(P\) be the sixteen selected ports. Let \(J\) insert values at \(P\).
The normalized reader and its unit row code at stage \(s\) are

\[
L_s=J^T+B_s,\qquad B_sJ=0,\qquad C_s=I+JB_s.
\]

All symbols include their actual ordered owner routes. The native
response at stage \(t\) is \(E_t\). The query must add
\(L_sE_tx\) to the selected record. It must restore every X field.

The native prefix accepts arbitrary independent selected records \(z\).
Before the query its contents are

\[
X=x,\qquad Y_P=z,\qquad Y_U=y_U+(E_tx)_U,
\]

with the prefix's stated physical output frames. After the query the
selected content is \(z+L_sE_tx\). If \(z=L_sy\), it is exactly
\(L_s(y+E_tx)\). The ordinary output content is already correct and is
not accessed by the query.

## Literal query order

The source theorem gives

\[
L_sE_tC_t^{-1}
=B_s-B_t+(L_sE_tJ)J^T.
\]

The emitted word executes:

1. Add \(B_sX_U\) to \(Y_P\), through the actual past-stage FULL views.
2. Add \(X_P\) to \(Y_P\).
3. Apply \(C_t\) to X, through the current-stage FULL views.
4. Subtract the current \(X_P\) from \(Y_P\).
5. Add \((L_sE_tJ)X_P\) to \(Y_P\).
6. Apply \(C_t^{-1}\) to X through the same current-stage views.

Steps 2 and 4 account for \(-B_tX_U\). The X fields in step 5 contain
the current reader \(L_tX\). Step 6 restores the original source bank.
No inverse of \(E_t\) and no odd division is used.

Every view is an explicit `map` event. Both the entry map and its inverse
are present. For each term in step 5, the word maps the selected X
source, adds its scalar multiple to the selected Y target, and restores
the X source with the exact inverse map. A scale of a target is also
explicit. No target baseline is assumed to be zero.

## Exact owner paths and phases

The verifier represents a coefficient by a pair consisting of its input
field and a 25-dimensional orthogonal owner matrix. It multiplies the
matrices in chronological operator order. Terms can cancel only when
their complete ordered matrices agree. It does not identify the
responses at stages \(s\) and \(t\).

For each map with matrix \(R\), the packet records a translation
\(\delta_R\), the inverse matrix, and the inverse translation. It
checks orthogonality, both matrix inverse orders, and that every
uncompleted axis is fixed. It verifies the complete Z4 phase identity

\[
F_{9+8t}P_RF_{9+8t}^{-1}=X_{\delta_R}P_R.
\]

This is a polynomial identity, including its quadratic and linear
parts. It holds on the complete spatial domain; it is not a sample of
spatial points. The phase checker is the pinned source implementation.
An independent review of this integration must still check that
dependency and the actual dispatcher.

The actual payload contains 545 distinct FULL maps for each pair with
reader stage zero, and 1616 for pair \((1,2)\). These counts include
distinct inverse and view maps where required. The instruction count
remains 2064 map calls in every pair.

## Verification and price

Both native providers are replayed on all 640 independent local input
columns before the query. The global query is then replayed on all
640 independent formal fields. The result matches the direct expression
\(L_sE_t\), with all 3808 owner-path terms. All 112 X fields are restored.
The 96 ordinary Y fields and all 416 helpers are unchanged by the query.

The serialized payload is read and checked again. Controls that omit
one middle source view or the final source-code restoration fail.
Normal and optimized Python give byte-identical outputs.

| Part | Scalar primitives | Explicit map calls |
| --- | ---: | ---: |
| Past-reader complement query | 1760 | 224 |
| Two selected-field copies | 256 | 0 |
| Current source code and its inverse | 3520 | 448 |
| Middle selected-source query | 5632 | 1392 |
| Query total | 11168 | 2064 |

Adding the native prefix gives 17624 scalar primitives and native
profile

\[
1392H_1+64H_2+48H_3+16H_8,
\]

with mass 1792. The query maps are additional to the prefix's 128 input
views, 96 output views, and native side-map upper bound 3040. The actual
global dispatcher must also be charged. There are no extra owned or
private fields and no new native child in the query.

The exact formal coefficient sweep gives prefix row one-norm 448 and
binary denominator height two for every pair. This is an upper bound
for the actual register norm. Distinct formal owner paths may have
further dependencies in their action on arrays, so it is not a claim
that the induced spatial operator norm is exactly 448. These bounds
apply to the stated independent inputs at the query entrance. A
recursive precision certificate must also account for how those inputs
were formed and for each child implementation.

Reproduce into new directories:

```sh
python3 emit_routed_query.py --out replay-normal
python3 -O emit_routed_query.py --out replay-optimized
```

The result is a concrete query implementation and a checked native
prefix, with the exact intended splice stated. A complete D25 service
requires the separately pinned dispatcher that proves that splice.
Recursive hosting and the complete supplier remain open. The local
same-reader price 9880 is not the price of this past-reader service.

This packet implements the fixed-reader theorem and source-view records
from the bridge-access lane. It uses the reviewed productive row-capture
and line-entry native family. AI agents prepared the code, proof, and
checks.
