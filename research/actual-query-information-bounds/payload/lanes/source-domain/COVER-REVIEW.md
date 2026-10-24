# Independent review of the cover trace bound

The bound `rank(J_s-J_0)/|G| >= 2912/183` passes this review. The review
uses the actual 73-dimensional route matrices and the frozen scalar word.
It does not use a phase evaluation of the cover group. The exact receipt is
`COVER-REVIEW.json`; the separate replay of the author's checker is
`COVER-REPLAY.json`.

The checked source is commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The receipt binds the archive,
the scalar matrix, the route recipes, and the reviewed proof and checker by
SHA-256. The optional sixth moment in the cover-algebra note was not reviewed.

## Trace and matrix order

The route at port `q` has local block `q q^T`. Distinct ports therefore have
distinct routes. For an off-diagonal nonzero entry of `A=R^T R`, the two
ports are orthogonal. The local block of their ordered product is
`B_q B_p^T`. Its kernel is `span(p)` and its image is `q`-perp. Thus an
ordered edge product determines both endpoints, for any choice of the
orthonormal complement bases.

The independent checker reads those bases from the pinned data-phase
recipes. It builds all 896 full 73-dimensional routes, checks their squares
and dot products, and verifies the stage transports. It then groups all
nonzero ordered edges by their full 73-dimensional product. There are 5,824
distinct nonidentity products and one identity group with the 112 diagonal
pairs. A separate order control distinguishes `rho_0 rho_1` from
`rho_1 rho_0` and checks the product on all 73 basis vectors.

On the full regular representation, the trace of a nonidentity group element
is zero and the trace of the identity is `|G|`. Thus the identity-coefficient
functional is the ordinary trace divided by `|G|`. This remains true for the
actual group `O(73,2)`. The 17-dimensional block calculation embeds
injectively into that group: each matrix is the identity on the other 56
coordinates. Restriction of the full regular representation to the generated
subgroup gives a direct sum of regular representations. No 17-dimensional
complex payload representation is substituted for the full cover.

The checker sums the identity coefficients from the actual collision groups.
It obtains

\[
\tau(PQ)=4/7,\qquad \tau((PQ)^2)=27/343.
\]

The trace equation in the proof is
`rho_b rho_c = rho_a rho_d`. The nonidentity case is
`b=a, c=d, b!=c`. The draft had a contradictory final inequality in this
case. The author corrected it during review. The calculation already used
the correct condition.

## Rank and the cost comparison

For `M=P-Q`, the projection identities give

\[
\tau(M^2)=104/7,\qquad \tau(M^4)=4758/343.
\]

Cauchy--Schwarz on the nonzero eigenvalues gives

\[
\frac{\operatorname{rank}M}{|G|}
\geq\frac{(104/7)^2}{4758/343}=2912/183.
\]

The polynomial bound for `PQP` also gives the stated common-range bound
`8/183`. Both calculations were repeated with rational arithmetic.

Deleting every centre child leaves rank mass `72W` at ambient rank 73.
For a uniform restriction repeated in every replica, the available average
codimension is less than `896/73`. The excess of the proved rank bound is
`48608/13359`. The resulting optimistic moment is `52704/52487 > 1` at
exponent zero. These figures normalize the complete 16-replica invoice;
they do not assign an isolated hosting bill to each replica.

## Scope controls

* On constant cover functions every route acts as the identity. Then `Q=P`
  and the rank difference is zero. The normalized trace is 8, not `4/7`.
  The theorem needs the full regular cover, or a stated sum of regular orbits.
* Applying one codimension loss to the complete 16-replica stock gives the
  optimistic moment `843264/854027 < 1`. The rank bound alone does not reject
  that different multiplicity.
* A code with extra state, a changed child invoice, a new controller, or a
  changed recursive contract is outside this fixed-stock application.
* This review does not verify a new native circuit, supplier, or kappa value.

Reproduce the independent check from the workspace root:

```sh
python3 -I -B work/centre-encoding-campaign-20261014/lanes/source-domain/review_cover.py --repo worktrees/k5-centre-sharing --campaign work/centre-encoding-campaign-20261014 --out work/centre-encoding-campaign-20261014/lanes/source-domain/COVER-REVIEW.json
```

The result is `PASS_INDEPENDENT_73D_COVER_TRACE_REVIEW`.
This review used OpenAI Codex assistance. No PR or commit was prepared.
