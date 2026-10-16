# Dev-run search log (chi(Z) >= 4 campaign, 2026-10-16)

Scratch drivers (`%TEMP%\opencode\agent-69\search_chi4.py`,
`search_chi4_b.py`) run against the same engine functions as `verify.py`
(imported from `research/fstar-chi4-zero-digraph-seed73765f29/verify.py`).
These runs are the recorded development evidence behind the README's search
table; the registered, deterministic replay is `verify.py` (which embeds the
smaller declared domain and the 3 x 60000-node Grötzsch probe).

## Round 1: annealing CSP on the Grötzsch incidence system

Target: realize the Grötzsch graph M(C5) (11 vertices, triangle-free,
4-chromatic) as a mutual-zero pattern: variables `p_i, q_i` in `{-3..3}^3`,
hard constraints `p_i . q_i != 0` (diagonal), `p_i . q_j = 0 = p_j . q_i`
(edges), non-edges nonzero in at least one direction. 25 restarts x 4000
simulated-annealing steps.

- best violation counts per improving restart: 15, 14, 12
- no zero-violation configuration found; the run then hit a scratch bug
  (evaluation on an invalid decoder) and was superseded by round 2.

## Round 2: sequential linear construction (exact nullspaces)

Place vertices in degree order; at each step solve `p_i _|_ q_j` (and
`q_i _|_ p_j`) for already placed edge neighbours as an exact linear nullspace
(Fraction arithmetic), sample a generic integer point in the solution
subspace, backtrack on non-edge/diagonal violations. Node budget 200000 per
trial, 12 trials with random restarts.

- 12/12 trials: no solution.
- deepest placements observed: 6-8 of 11 vertices.
- failure mode at the deepest cut: the per-vertex nullspace collapses to rank
  3 (only the zero vector) for a high-degree vertex, or the 24 candidate
  samples all violate a non-edge constraint; the search then backtracks and
  exhausts the node budget.

## Round 2b: direct hill-climbs on exact chi(Z)

Mutations of one integer entry of `P` or `Q`; objective the exact pair
`(chi(Z), chi(G_0))` by subset DP; greedy non-decreasing acceptance;
deterministic seeds.

- `v = 6..9` from random starts (3 restarts x 80 steps, box `{-3..3}`): best
  `chi(Z) = 2`, `chi(G_0) = 2`.
- `v = 6..12` targeted (2-4 restarts x 30-150 steps, box `{-3..3}`): best
  `chi(Z) = 3` only from structured seeds (C5 perpendicularity extensions);
  `chi(Z) >= 4` never observed.
- `v = 5..11` random symmetric/asymmetric/mutual-dense/C5-seeded census (34
  instances, exact `chi`): `chi(Z) >= 4` on 0 instances.

## Interpretation

No `chi(Z) >= 4` instance appears in any route; the obstruction records are
budgeted (node caps, step counts), not unrealizability proofs. The registered
`verify.py` search replays a deterministic slice of these routes and writes the
per-trial obstruction records into `CERTIFICATE.json`
(`search_stats.grz_obstructions`).
