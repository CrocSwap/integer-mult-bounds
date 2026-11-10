# Price-null fibres need irreducible cycle exchanges (no κ)

This answers Open next question 1 of DreamingOfClouds'
[PR6345](https://github.com/CrocSwap/integer-mult-bounds/pull/6345)
(`research/p104-frontier-symmetric-ladders`) at the level of that package's own
register-tax model. The question: is the set of optimal frame assignments exactly the union
of its three freedoms? Those are one-step helper re-spans (F1), stop reorders with fixed
endpoints (F2), and a stop move in one register cancelled by a stop move in another (F3).

**Answer in the tax model: no.** Claim type: scoped written proof with exact finite
corroboration. No κ change.

- **Theorem 1.** Two one-stop window chains `(a, s, b)` with different window lengths never
  cancel each other's tax change unless neither changes. So F3 can only pair registers with
  equal windows.
- **Corollary.** In a configuration of one-stop main chains with pairwise distinct windows,
  every configuration reachable by any sequence of F1–F3 keeps each register's step multiset.
- **Theorem 2.** For every `k ≥ 3` there are `k`-register price-null changes in which no
  nonempty proper subset is price-null. Register `i` has window `u_i + u_{i+1} + c` and moves its
  stop from `u_i` to `u_i + c`. Irreducibility holds when the `2k` values `u_j` and `u_j + c` are
  distinct. With `u_j = 2^(j−1)` and `c = 2^k` the windows are also distinct, so the corollary
  shows F1–F3 cannot reach these changes, even through intermediate states.
- **Smallest case.** An exhaustive search finds no three-register cycle with distinct windows
  below largest window 6. At 6: window 4 `{1,3}→{2,2}`, window 5 `{2,3}→{1,4}`, window 6
  `{2,4}→{3,3}`. All dimensions are at most 6, inside the rank range 1..9 that PR6345 reports.

A complete classifier or local search for the fibre therefore needs multi-register cyclic
exchanges, not only pairs. [PROOF.md](PROOF.md) has the proofs and exact scope.

## Scope and limits

This is a statement about the tax model and the freedoms as PR6345 defines them. It does not
show that the PR6167 word admits a legal cycle. Frames must exist at the right dimensions and
events, and the frame table, inventories and replay fields must stay fixed. The tax model
ignores those constraints. PR6167 and PR6345 are cited, not replayed or audited. No supplier,
caller, native, compiler, Lean or Docker obligation is discharged.

## Reproduce

From the repository root, standard library only:

```sh
python3.12 -I -W error -B research/price-null-cycle-exchanges/verify.py
python3.12 -I -W error -O -B research/price-null-cycle-exchanges/verify.py
python3.12 -B scripts/research_package.py --package research/price-null-cycle-exchanges
```

Each verifier run prints `PASS_PRICE_NULL_CYCLE_EXCHANGES` in under a second. It checks:

- Theorem 1 over all 216,062 combinations of two one-stop chain changes (old and new stop each, unchanged included) with distinct windows up to 12;
- Theorem 2 nullity, irreducibility, interior stops and distinct windows for `k = 3..8`;
- the exhaustive smallest three-register cycle and its pinned witness;
- three rejecting controls. Dropping one register breaks nullity. Equal windows do admit a
  pairwise exchange. A non-generic cycle (`u = (1,2,1,2)`, `c = 3`) splits into null pairs.

## Open next questions

1. **Does the PR6167 frame table admit a legal three-register cycle on its actual events?**
   First step: list the actual word's one-stop chains by window, find triples whose step pairs
   admit a cycle, and test each candidate reassignment with the pinned PR6167 replay. Blocker:
   frame dimensions, event positions and fixed inventories.
2. **Is every price-null change a composition of irreducible cycles on multi-stop chains?**
   Multi-stop chains change several steps at once, so Theorem 1's argument does not carry over
   directly.
3. **Can an irreducible cycle enable a stop drop that no single freedom reaches?** Price-null
   moves matter only if they unlock a strict improvement later.

## Credit

The register-tax model, the three freedoms and the question are DreamingOfClouds' (PR6345),
over Ali Romman's PR6167 word and its predecessors. The new theorems, checker and examples
were produced by Nick Petalas. Apache-2.0.
