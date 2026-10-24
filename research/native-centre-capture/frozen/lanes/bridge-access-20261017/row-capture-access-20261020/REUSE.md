# A fixed centre reader can be carried through forward services

The sixteen FULL centre rows need not be converted back to plain target
rows before the next forward service. Their exact next-entry type is
the required intrinsic line. A rank-eight path can carry each row to
the next FULL cut. A dyadic query at that cut updates the same past
reader and restores all source fields.

This result gives a typed forward-service extension. It does not give
a backward companion or a complete caller. The separate local formation
word has been emitted. The complete reuse native word still needs its
own integration and replay.

## The carried reader

Keep the pivot set P and the normalized row readers from `ACCESS.md`.
Let J insert sixteen values at P, and let \(J^{\mathsf T}\) select P.
At stage s, write

\[
L_s=J^{\mathsf T}+B_s,\qquad B_sJ=0,\qquad
C_s=I+JB_s.
\]

Each symbol includes its actual stage routes. In particular, \(B_s\)
and \(B_t\) are different operators when \(s\ne t\).

Suppose the target bank contains \(L_sy\) on its selected FULL rows
and \(y_R\) on its other hole rows. This is a unit encoding of arbitrary
y. Equivalently, its selected and ordinary input values can be chosen
independently.

At a later current entry t, the literal views give local target types
\(Q_p\) on P and I on R. Keep the original ordinary target paths. On
each selected carrier, replace the removed path by

\[
Q_p\longrightarrow F_9.
\]

This is the operator \(F_9q_p\), of native rank eight. The program gives
an exact positive H8 recipe for every selected port. It uses the actual
orthogonal port chart, with its eight complementary axes first, and an
explicit output translation. The full Z4 phase polynomial is checked.

After the retained sweep and these carrier paths, all X fields and
all selected Y fields are FULL. Add \(L_sE_tx\) to the selected target
bank at that cut. The outputs are

\[
X_{\rm out}=F_9x,\qquad
Y_{P,\rm out}=F_9L_s(y+E_tx),\qquad
Y_{R,\rm out}=F_9q_R(y+E_tx)_R.
\]

The same reader \(L_s\) has been retained. No old-stage target read was
used. The input reader was not replaced by \(L_t\).

## A query through sixteen existing source carriers

The actual response has \(E_t[P,P]=0\). It also has

\[
E_t=I+A_tL_t,\qquad
L_t=J^{\mathsf T}+B_t,\qquad C_t=I+JB_t,
\]

where \(A_t=(E_t-I)J\). These are routed operator identities. Since
\(L_sJ=I\), direct multiplication gives

\[
L_sE_tC_t^{-1}
  = B_s-B_t + (L_sE_tJ)J^{\mathsf T}.
\]

No factor at stage s is commuted through a factor at stage t. Put
\(M_{s,t}=L_sE_tJ\). Use this complete order at the FULL cut:

1. Add \(B_sX_R\) to \(Y_P\).
2. Add the current \(X_P\) to \(Y_P\).
3. Apply \(C_t\) to X.
4. Subtract the new \(X_P\) from \(Y_P\).
5. Add \(M_{s,t}X_P\) to \(Y_P\).
6. Apply \(C_t^{-1}\) to X.

Steps 2 and 4 contribute \(-B_tX_R\). The query in step 5 reads the
current centres \(L_tX\) from the existing sixteen X fields. Thus the
complete increment is \(L_sE_tX_{\rm original}\).
Step 6 restores every X field. Every target baseline is retained.
No scratch field or zero input is used.

This factorization avoids an inverse of E. In particular, it needs no
division by five or seven. Both C words are the emitted dyadic shears
from the normalized row-capture packet.

## Actual owner paths and phases

The checker binds the three D25 pairs \((s,t)=(0,1),(0,2),(1,2)\).
For a term with intermediate port j and final source port r, the
complete owner multiplier is

\[
A=\rho_{s,p}\rho_{s,j}\rho_{t,j}\rho_{t,r}.
\]

The coefficient is \(L_{p,j}E_{j,r}\). The full query \(L_sE_t\) has
3,808 such terms. Its selected-source part \(M_{s,t}\) has 696 terms.
Each of the latter reads one of the sixteen selected X fields.
Different owner paths are kept as different terms.

All factors of A act within the completed prefix at level t. They fix
every uncompleted axis. A is orthogonal. Therefore

\[
F_{9+8t}P_AF_{9+8t}^{-1}=X_{\delta_A}P_A.
\]

The program computes the entire Z4 difference polynomial to obtain
\(\delta_A\). It verifies that its odd and quadratic parts vanish.
It also checks the inverse map, whose route is \(A^{-1}\) and whose
translation is \(A^{-1}\delta_A\).

The owner read is \(h\mapsto hA\). The payload map \(P_A\) expresses the
source chart in the target chart. Together with the translation, these
are one field/address map. They are not two independent uses of the
source data.

For each middle-query term, apply that map to its source field, add
the required scalar multiple to the selected Y field, and apply the
inverse map to the source. This restores the full arbitrary source
array before the next term. Right multiplication by A is a cover
bijection, so this procedure is legal on the regular orthogonal cover.

Step 1 uses the literal past-stage FULL views on 96 source fields and
16 target fields. Steps 3 and 6 use the current-stage FULL views on
all 112 source fields. The checker verifies these full phase equations.
Steps 2 and 4 are same-port copies between FULL fields.

The checker also expands both sides of the query identity as exact
sums of owner paths. It compares coefficients only after the complete
route matrices agree. This prevents a false cancellation between
different body owners.

## Invoice and bounds

The conservative query invoice for each checked pair is:

| Part | Real scalar primitives | Monomial map calls |
| --- | ---: | ---: |
| Past-reader complement query | 1,760 | 224 |
| Two same-port copies | 256 | 0 |
| Current C and its inverse | 3,520 | 448 |
| Selected-source middle query | 5,632 | 1,392 |
| Total | 11,168 | 2,064 |

The middle query scales each large target by four, executes its
integer-coefficient additions, then divides that target by four.
The small targets need no such scale. This uses only dyadic units.
The two copies use all sixteen selected ports.

The query uses no native child and no extra field. A conservative
triangle-inequality bound for every scalar prefix is 972, relative to
unit one-norm inputs at the query entrance. The checker derives this
bound from the literal scalar order. It also bounds the new binary
denominator height by three. These are bounds for one query. They are
not a recursive precision certificate.

The retained native word has scalar price 6,456. Replacing its selected
paths by sixteen H8 calls gives the prospective local profile

```text
1392 H1 + 64 H2 + 48 H3 + 16 H8.
```

Its native rank is 1,792, equal to the old rank. The retained word plus
the new query has scalar price 17,624. The 2,064 query maps are additional
to native wrappers and ordinary boundary maps. Their finite cost and
the child hosting must still be included in a complete supplier.

## Reuse scope

The operator proof applies whenever the later FULL cut admits both
stage routes, the pivot normalization \(L_sJ=I\) holds, and the ordinary
target paths do not read a selected target. These are concrete
conditions. They do not require a common response across stages.

This packet verifies those conditions for the actual D25 forward
services and all three possible past/current stage pairs. It does not
assert the same input type for a backward service. That service needs
its own dual code and native proof.

Run `check_reuse.py` normally and with `python3 -O`, with separate output
directories. The two program files and the two receipts must be byte
equal. The immutable formation packet remains unchanged.

No publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
