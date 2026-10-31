# Two sessions certify the PR288 sign-gauge obstruction

## Status and attribution

This is a new explicit certificate and independent reconstruction of the
obstruction already reported by eumemic in PR288, §1.4(d). The obstruction
theorem itself is not claimed as new. Braverman and He supplied the graph and
terminal pairs in arXiv:2610.10108v1, §4 and Appendix A. Exact source pins and attribution are recorded in `SOURCES.md`.

The proof below is an elementary written argument. The finite path premises
are checked by `check_certificate.py`. The argument has been examined by a
separate assistant agent in the same AI-assisted workflow; it has not been
formally checked in Lean or independently reviewed by a human.

## 1. Exact statement

Let G be the 182-vertex undirected physical graph defined below. There is no
assignment of fixed additive matrices A_v in M_5(Q), one for each vertex, with:

1. rank(A_v - A_u) <= 1 on every physical edge {u,v};
2. one fixed invertible C_0 in GL_5(Q);
3. for each session (p,l), A_l - A_p = sigma_(p,l) C_0, where each session
   independently chooses sigma_(p,l) in {+1,-1}.

It suffices to impose item 3 on just the two sessions (0,155) and (3,93).
This includes the original sign-gauge model with C_0 invertible lower
triangular. It does not cover independently chosen nonproportional Levi
targets, higher-rank physical edges, or non-additive/nonabelian frames.

For convenience every session is oriented point-to-line. The paper orients
each session from its earlier to its later vertex in pi. Reversing one
session replaces its free sign variable sigma by -sigma, a bijective change
of variables. Thus this orientation choice changes no existence question.
It does not assume any symmetry of the unknown matrices A_v.

## 2. Exact finite instance

Construct F_9 = F_3[t]/(t^2+1). Write eta_r = (r mod 3) + floor(r/3)t for
0 <= r <= 8. The ordered projective representatives are

    v_0 = (0,0,1)
    v_(1+r) = (0,1,eta_r)
    v_(10+9r+s) = (1,eta_r,eta_s).

Vertex i represents point v_i; vertex 91+j represents line v_j. An incidence
edge joins i to 91+j exactly when v_i dot v_j = 0 in F_9. Number the 910
candidate edges lexicographically by (i,j), starting at zero. If the ten
incident line indices for point i are j_(i,0) < ... < j_(i,9), then
e_(10i+r) = {i,91+j_(i,r)}.

Remove the 175 edges R listed in `instance.json`. The remaining 735 edges
are physical. The 157 session indices are B = R minus (C union J), where C
and J are the disjoint nine-element sets in the same file. The complete
lists match the paper and its pinned companion data. PR288's raw JSON has a
176th R entry, the paper page number 13; the original PR checker explicitly
discards it. Our normalized data records the 175 actual edge indices.
The immutable source links and numerical normalization are documented in
`SOURCES.md`; the checker binds the normalized file to its reviewed SHA-256.

F_9 defines only this combinatorial graph. The matrix ranks and traces in
the theorem are over Q. They are not ranks or traces over the bit payload
field F_2.

## 3. A rank-tight path forces unit traces

**Lemma.** Over any field, if m matrices Q_1,...,Q_m of rank at most one sum
to I_m, each Q_j has trace 1. In fact Q_i Q_j = delta_(i,j) Q_i.

**Proof.** Factor Q_j = u_j v_j^T, allowing zero vectors initially. Let U
have columns u_j, and let V have rows v_j^T. Then UV = I_m. Since U and V
are square, they are invertible and VU = I_m. Therefore
v_i^T u_j = delta_(i,j). In particular trace(Q_j) = v_j^T u_j = 1, and
the asserted multiplication identity follows. This also proves that no
Q_j is zero. The term "orthogonal idempotents" here would mean this
algebraic multiplication identity, not orthogonal or Hermitian projections.

Now take any path p=x_0,x_1,...,x_5=l of exactly five physical edges for a
session whose endpoint difference is sigma C_0. Put

    Q_j = sigma C_0^(-1) (A_(x_j) - A_(x_(j-1))).

These five matrices have rank at most one and sum to I_5, since sigma^2=1.
The lemma implies

    trace(C_0^(-1) (A_(x_j) - A_(x_(j-1)))) = sigma.

No shortest-path algorithm is used in this implication. A path of length
five and a rank-five target suffice. Rank subadditivity would itself
prohibit a shorter path under the assumed embedding. Paths need not
follow the coding paper's causal orientation.

Orient each physical edge from point to line and define

    tau_e = trace(C_0^(-1) (A_line - A_point)).

If a chosen session path traverses e in direction epsilon in {+1,-1}
relative to this orientation, then

    tau_e = epsilon sigma, equivalently sigma tau_e = epsilon.

Thus the same fixed edge variable must satisfy every path constraint in
which that edge is used. This is a necessary condition for an embedding;
consistency would not establish sufficiency.

## 4. Three explicit paths

The certificate uses session edge indices 7 and 30 and physical edge
indices 114 and 113:

| Index | Kind | Endpoints in point-to-line order |
| --- | --- | --- |
| 7 | Session | (0,155) |
| 30 | Session | (3,93) |
| 114 | Physical edge | (11,130) |
| 113 | Physical edge | (11,121) |

The three distinct path witnesses are:

| Session | Five-edge path | Candidate edge indices along path |
| --- | --- | --- |
| 7 | 0, 92, 11, 130, 66, 155 | 0, 110, 114, 664, 667 |
| 7 | 0, 92, 11, 121, 68, 155 | 0, 110, 113, 683, 687 |
| 30 | 3, 121, 11, 130, 78, 93 | 33, 113, 114, 784, 780 |

Every listed edge is an incidence edge outside R. Both session indices
belong to B. The independent checker reconstructs these facts directly
from F_9 and the source-bound input. The union uses only eleven physical
edges and eleven vertices.

The session-7 paths traverse edges 114 and 113 in point-to-line direction.
The session-30 path traverses edge 114 in point-to-line direction but
edge 113 in the reverse direction. Hence

    tau_114 = sigma_7,
    tau_114 = sigma_30,
    tau_113 = -sigma_30,
    tau_113 = sigma_7.

The first pair gives sigma_7 = sigma_30; the second pair gives
sigma_7 = -sigma_30. This is impossible over Q for signs in {+1,-1}.
This proves the theorem.

Equivalently, the session/edge cycle

    session 7, edge 114, session 30, edge 113, session 7

has constraint signs +1,+1,-1,+1, whose product is -1. Every sign variable
occurs twice in the product of the four equations, forcing the product to
be +1. The exact certificate stores four incidence records, with the
session-30 path reused for two records.

## 5. Coverage and trusted components

This is a finite contradiction witness, not a search-based exclusion.
The proof universally covers all rational vertex matrices, all invertible
common C_0, and all 2^157 choices of session signs under the stated
premises: any proposed embedding must satisfy these four equations.
There is no need to enumerate the sign assignments, possible matrices,
all paths, or all geodesic incidences.

The discovery producer may be wrong without compromising soundness of an
accepted certificate: the checker imports no producer or upstream code,
rebuilds the graph by a different method, checks the fixed instance hash,
validates every path and selected incidence, recomputes every sign, checks
cycle closure and checks the negative product. Its implementation, the
Python interpreter, the written lemma and the provenance binding remain
part of the trusted argument. No solver status is treated as proof.

## 6. What this does not establish

- No reproduction or closure of PR288's m=3 SAT, MITM or Groebner reports.
- No general obstruction to distinct Levi targets or nonabelian frames.
- No conclusion when paths have more than five edges or edges may have
  rank greater than one; the trace lemma needs exactly m rank-one terms.
- No disproof or re-verification of the Braverman-He network-coding theorem.
- No new multiplication exponent, practical benchmark, or complete formal
  verification of integer multiplication.
- No worldwide novelty claim. The already reported obstruction retains
  its attribution; the explicit certificate, separate checker and tests
  are the contribution prepared here.
