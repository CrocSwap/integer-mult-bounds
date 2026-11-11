# One changed Type A provider

Use the literal #7113 Type A per-port chronology and keep all factors
fixed except one QUERY and one J. Replace the QUERY by an ordinary ADD
at the same clock. Consider the necessary specialization body \(=1\)
at \(q=1\) and \(q=-1\). The original endpoint is \(I_{36}\) and
\(-I_{36}\), respectively, as checked on all 36 input basis vectors.
The relevant factors are invertible at these two specializations.

For the QUERY destination and source \(d\ne s\), write
\(E=e_d e_s^T\). The old QUERY at \(q=-1\) is \(I-E\) and the
new ADD is \(I+E\). At \(q=1\) their actions agree, so the required
plus block is the original \(J_+\). At \(q=-1\), let \(M\) be the
ordered product of the unchanged factors strictly between the two
clocks. Cancel the shared prefix and suffix. If the QUERY precedes J,
the unique required minus block is
\[
J'_-=J_-M(I-E)(I+E)^{-1}M^{-1}
    =J_- -2(J_-Me_d)(e_s^T M^{-1}).
\]
If J precedes the QUERY, it is
\[
J'_-=M^{-1}(I+E)^{-1}(I-E)MJ_-
    =J_- -2(M^{-1}e_d)(e_s^T MJ_-).
\]
These identities use \(E^2=0\). Both correction vectors are nonzero.
A nonzero coordinate of the correction row or column outside the old
four-role layout is an outside read or write. The exact fixed-role
replay finds such a coordinate for all 68 alternatives.

## Allowing common even adapters

At body \(=1\), the two Type A J shears at active roles \((u,v,x,y)\)
are \(v\gets v+q^{-1}u\) and \(x\gets x+\alpha qy\), with
\(\alpha=-1\). Thus \(J_--J_+\) has exactly the entries \(-2\) at
\((v,u)\) and \(-2\alpha\) at \((x,y)\) and has rank two. The
required difference \(D=J'_--J_+\) adds one outer product to that
matrix, so its rank is at most three.

An invertible q-even left/right pair \(L,R\) uses identical matrices
at both signs. The phase difference of the adapted provider is
\(L(J_--J_+)R\), still rank two. It cannot realize a required
difference of rank three, even if its active images are moved outside
the original four roles. This argument also applies to any replacement
provider satisfying the same rank-two cap at this specialization.

For all 68 cases, whole-row rational elimination verifies
\(\operatorname{rank}(D)=3\) and emits a nonzero exact \(3\times3\)
minor. The independent modular screen emits a nonzero minor modulo
65521 for every case. The package cross-checks the selected rows and
columns of each modular witness by rebuilding its entries over the
rationals and reducing each entry and determinant with invertible
denominators. A control whose nonzero rational determinant is divisible
by 65521 shows why a zero residue would remain inconclusive.

The optimistic invoice before support gives 96 raw units of saving to
one alternative at a time. Every alternative fails a necessary test,
so the compatible saving upper for this family is zero. The proof
covers the given fixed chronology and the one-provider phase-rank-two
relaxation. It leaves higher phase rank, multiple changed providers,
cross-port operations, and full physical and all-width admission open.
