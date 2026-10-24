# Exact paired-plane decoder certificate

## Result

Let (q_0,\ldots,q_{111}\in\mathbb F_2^9) be the labels at the selected PR1094
complex ports. Their convention is (UU^T=(J+G)\bmod2), so the selected
pairing matrix is (B_0=UU^T), with (B_0[t,u]=q_t\cdot q_u). Each label has
weight 3 or 7, and distinct labels are joined when (q_i\cdot q_j=0), which
is precisely the odd-Gram edge condition.

The complete graph is 52-regular. A deterministic minimum-remaining-degree
backtracking rule, breaking ties by port index and then neighbor index, returns
the 56 pairs stored in [CERTIFICATE.json](CERTIFICATE.json). Each pair

\[
  k=(i,j),\qquad A_k=[q_i\ q_j]\in\mathbb F_2^{9\times2}
\]

defines one shared plane (E_k=\operatorname{span}(q_i,q_j)) assigned to both
ports. The pair labels are independent and orthogonal, so they form an
orthonormal basis for that plane under the inherited binary form.

## Global factorization

For the 56 planes, solve the exact binary linear system

\[
  \sum_{k=1}^{56} A_k M_k A_k^T=I_9,
  \qquad M_k\in\mathbb F_2^{2\times2}.
\]

The verifier uses highest-index pivots and sets free variables to zero. The
certificate has 40 zero matrices, nine rank-one matrices, and seven rank-two
matrices. For each rank-one matrix choose (M_k=x_ky_k^T). For each
rank-two matrix choose (X_k=I_2,\ Y_k=M_k^T), so in either case
\(M_k=X_kY_k^T\). Concatenating the port columns gives

\[
 D=U[A_1X_1\;\cdots\;A_{56}X_{56}],\qquad
 T=U[A_1Y_1\;\cdots\;A_{56}Y_{56}],
\]

where zero matrices contribute no columns. Therefore
\(DT^T=U I_9 U^T=B_0\) on all 112 by 112 entries. The verifier separately
checks the 9 by 9 identity and the full port matrix.

## Copy-rank invoice

For a scalar outer-product term with supports (R,C\subseteq[112]), the
inherited B14 copy charge is
\(\rho(R,C)=\operatorname{rank}_{\mathbb F_2}B_0[R,C]\). A rank-one plane
matrix contributes its factor supports. A rank-two plane matrix contributes
the union supports of its two columns; since its change of basis is invertible,
both sides have the support of the same plane. Recomputing the restricted
pairing ranks gives:

| Query type | Count | Pairing rank each | Copy charge |
|---|---:|---:|---:|
| Rank-one plane query | 9 | 7 | 63 |
| Rank-two plane query | 7 | 9 | 63 |
| Total active plane queries | 16 |  | **126** |

This exact copy charge uses the separate-term support-pairing convention from
PR717/PR968. The comparison budget (C\le160) in open PR1808 is a planning
threshold for its stated complex-side screen; the 34-unit difference is not a
certificate that all supplier overhead fits in that screen.

## Exact dirty-state endpoint

The inherited operators are

\[
 C_q=((1+i)I+(1-i)X_q)/2,\qquad C_q^2=X_q.
\]

For a matched plane (E=\operatorname{span}(q_i,q_j)), put
\(C_E=C_{q_i}C_{q_j}\). The two commuting translations give
\(C_E^2=X_{q_i+q_j}\). `verify.py` applies the four exact Gaussian-dyadic
operators to every one of the 512 computational basis states for each of the
56 planes. It checks the complete state vector with integer Gaussian
numerators and denominator 16. Since these basis states span the local address
space, the checked equality holds for every dirty superposition on that
space, and tensoring identity on spectator registers preserves it.

The 56 matched planes therefore determine 56 endpoint translation labels
\(q_i+q_j\). Their exact operator identities are checked here, while their
application multiplicity across hosted families is not priced.

This checks the endpoint operator identity. It does not construct the full
selected route that hosts the plane operations, schedules frame changes,
restores every other live register, or charges their precision and interface
costs.

## Changed-law screen and scope

The selected local profile is
\(\{1:2412,2:418,3:432,4:142,5:82,8:8\}\). Replacing the eight rank-8
centre children by the 16 active paired-plane queries gives
\(\{1:2412,2:418,3:432,4:142,5:82,7:9,9:7\}\), with local mass 5,648.
Under the hypothetical two-unpaid-coordinate law, (m=73), (W=896/9),
nine stages, and centre charge 126, the total per-call mass is
\(71(896/9)+126=64750/9\), leaving (13918/9) idle mass. The pinned exact
ceiling routine, with fractional idle mass assigned optimistically at rank 51,
certifies

\[
  a_{hi}=3447203501/10^{12}=0.003447203501,
  \qquad a_{hi}/(1+a_{hi})=3447203501/1003447203501
  \approx0.003435361112.
\]

This is only a favorable complex-side relaxation for the proposed profile. It
does not prove that the changed coverage law is realized by a supplier, that
the 34 remaining copy-rank units cover all other expenses, or that the bit-side
supplier and joint assembly improve. No new \(\kappa\), selected record, or
integrated bound is claimed.

## Controls and reproduction

The verifier rejects a non-edge partner, omission of an active decoder term,
mutation of a plane matrix, and omission of the endpoint correction. It reads
the 112 labels from the exact selected archive entry pinned in `SOURCES.json`;
no predecessor code, solver, or network access is used.

From the repository root:

```sh
python3 -B research/paired-plane-port-matching-seed6c563a/verify.py
python3 scripts/research_package.py --package research/paired-plane-port-matching-seed6c563a --check-only
python3.12 scripts/research_package.py --package research/paired-plane-port-matching-seed6c563a
```

Expected verifier output begins `PASS_PAIRED_PLANE_PORT_MATCHING` and reports
56 pairs, 16 active queries, copy charge 126, and 28,672 exact endpoint basis
checks.
