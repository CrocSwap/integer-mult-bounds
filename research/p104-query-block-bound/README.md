# Query-block bound for header query words (no κ)

**No new κ.** This package proves a rank identity for products of rank-one query units and a window bound
`N - r >= w`, and checks them exactly on the literal header word of #6726 and on explicit models.

## Result

1. **Rank identity** (`PROOF.md` Theorem 1, `char != 2`). If `J = (I - x_N y_N^T)...(I - x_1 y_1^T)` is an involution
   with `r = rank(J - I)`, then `rank(2K - Gamma) = N - r`, where `Gamma_ij = y_i^T x_j`, `K = I + Gamma_<`. Reflections
   are allowed. It gives `N >= r + 1` for square-zero units, attained at `r = 2` (three units) and at `r = 8` (the nine
   queries of the #6726 root).
2. **Window bound** (Theorem 2, Lemma 3, Corollary 4). In an algebra `A` with unital subalgebra `B`, a `B`-bimodule
   projection `E : A -> B` and `Q` with `E(Q) = 0`, take units `I + u Q v` with `u, v` over `B` (ordinary controls
   absorbed, no commutation assumed) whose product is `O_1 diag(g) O_2`, `O_i` over `B`, with `r` entries `g_j` in `ker E`
   and the rest `1`. Then `rank rho(I + FG) = (N - r) d` for the strictly lower `F = E(W)`, `G = V U`, and if `w` consecutive
   units pair to zero (`v_i u_j = 0`, diagonal included), then **`N >= r + w`**, in any characteristic and at any position.
3. **Instances.** (a) the parity sector `A = F[q]/(q^4-1)`, `B = F[q^2]`; (b) the 24 uniform single-qubit Clifford cosets
   on `f` columns: `A` the span of the 24 powers `g^{(f)}` (independent exactly for `f >= 5`, rank `4, 10, 20, 23, 24, 24, 24`
   for `f = 1..7`), `B` the 8 monomial cosets (monomial wrappers, `S^{(f)}`, uniform Pauli gates, `q^2`-dependent gates),
   `E` the coordinate projection, `Q = C^{(f)}`.
4. **The #6726 header.** At body variables 1 the retained 606-event caller has `N = 33` square-zero header units
   (18 LOCAL, 15 QUERY), `r = 32` targets in `ker E` and two identities, and `rank(I + FG) = 1 = N - r` in both sectors
   `q^2 = +-1`; `E(M) = O(I + UFV)` agrees with the independent replay. `w` copies with zero pairing between copies
   give `N - r = w` exactly, so the window bound is attained: for a width-`w` window of orthogonal square-zero units
   the `w` per-copy deficits of one unit cannot be shared.

Exact checks (`verify.py`): both retained inputs by blob id and SHA-256; Theorem 1 on the Whitehead word, the #6726
root, conjugated, padded, direct-sum and reflection words; the 24 cosets (subgroup, 1024 bimodule products,
independence); 30 random words in `Q[S_4]` with exact `E(M) = I + UFV` and the Sylvester identity; 6000 window-lemma
instances (equality attained); the header at `q = 1, -1, i, -i`; three-copy replication. Controls: non-involution,
controls outside `B` (12 of 12 break the identity), `f = 4` dependence, non-consecutive and non-orthogonal windows
(Whitehead word; consecutive header units), a header with one query removed.

## Scope

The window bound is for words in the Setting of `PROOF.md` Section 2, with ordinary controls in `B`; the caller
statement uses that identification of a native call with `P` mutually orthogonal square-zero units (Section 4,
not derived here). Not covered: controls that do not commute with the body variables, non-square-zero native central
actions, a recursive query supply, positive characteristic for the Clifford instance, targets outside `1` and `ker E`,
column-split units. No pricing, caller construction or framework assumption is claimed.

## Open next questions

* Does the window bound survive ordinary controls that do not commute with the body variables?
* Is there a native whose per-port central part is not a square-zero unit and that saves contact without losing the window?
* What is the unit count of a recursive query supply (a job whose outputs are query units)?

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/p104-query-block-bound
```
Expected: `PASS_QUERY_BLOCK_BOUND` (normal and `-O`) and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Python 3.12, standard library; about 25 s per run.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
