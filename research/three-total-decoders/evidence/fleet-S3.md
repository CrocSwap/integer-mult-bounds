# S3 (adversary): no counterexample to (A) found, v <= 12

Method: S3_search.c (C, 1 process). Lines (p,q) with p,q primitive vectors in {-R..R}^3 (R = 1, 2), p(t).q(t) != 0.
B ranges over F2 matrices with unit diagonal and free entries on exact incidences p(t).q(s) = 0.
Cost = sum_j rank_F2 B[R_j,A_j] (no floor). The outer loop is a hill-climb on the configuration
(objective cost*1000 - #incidences, so it is pushed toward many incidences AND low cost, with occasional uphill moves).
The inner loop is simulated annealing over B, which gives an upper bound on the true minimum, so a refutation would show.

Results (v = 5..12, R = 1,2, several hundred climbs of 3000-6000 mutations each, 4k-60k SA steps per evaluation):
- NO configuration with cost < v. Every climb ends at cost = v exactly (the floor), never below.
- Tight cases (cost/v = 1.000) reach 40-51 incidences at v = 9 (R=1) and 28-42 (R=2), so they are not just the trivial incidence-free case.
- Fano-type structure: P^2(Q) cannot hold the Fano incidence graph (needs char 2), so a whole F7 incidence pattern never
  appears among p(t).q(s)=0 pairs; the search found nothing beating the floor. This is evidence, not proof, that no F7 minor is
  usable inside a rank-3 block.
- Not done: joint Q-liftability of the optima for these random tight configs (no enumeration of all optimal B was run); LC was
  not tested beyond what PROOF.md 12.7 records for tied_min. No LC counterexample found or looked for beyond the cost search.
- Caveat: SA is heuristic. It gives no UNSAT certificate; a cost < v with a hidden narrow basin could be missed.
